import streamlit as st
import pandas as pd
from utils.plots import carte_indice_comparatif, slope_chart_classement
from utils.stats import prevalence_brute, prevalence_standardisee_directe, indice_comparatif
from utils.constants import DEPTS_METRO, DEPTS_OUTREMER, DEPT_NAMES


def main():
    st.title("🗺️ Where? Territorial Analysis")
    
    st.markdown("""
    Pathology prevalence varies by territory. Cette page utilise 
    l'**comparative index** (standardisation indirecte) pour compare departments 
    en neutralizing the effects de la structure par âge et sexe de la population.
    
    An index of **1** corresponds to the national average. Un indice supérieur signifie 
    que le département a more patients que ce que sa structure démographique laisserait attendre.
    """)
    
    # Récupérer les données
    data = st.session_state.get("data")
    if data is None:
        st.error("Data not loaded.")
        return
    
    df = data["df"]
    df_national = data["df_national"]
    df_ref = data["df_ref"]
    geojson = data["geojson"]
    
    year = st.session_state.get("selected_year", df["annee"].max())
    patho = st.session_state.get("selected_patho_niv1")
    patho_niv2 = st.session_state.get("selected_patho_niv2")
    include_outremer = st.session_state.get("include_outremer", False)
    
    # Filtrer les données
    depts = DEPTS_METRO + DEPTS_OUTREMER if include_outremer else DEPTS_METRO
    df_filtered = df[
        (df["annee"] == year) & 
        (df["patho_niv1"] == patho) &
        (df["dept"].isin(depts))
    ]
    
    if patho_niv2:
        df_filtered = df_filtered[df_filtered["patho_niv2"] == patho_niv2]
    
    df_national_filtered = df_national[
        (df_national["annee"] == year) & 
        (df_national["patho_niv1"] == patho)
    ]
    if patho_niv2:
        df_national_filtered = df_national_filtered[df_national_filtered["patho_niv2"] == patho_niv2]
    
    # Calculer l'comparative index par département
    df_indices = indice_comparatif(df_filtered, df_national_filtered, ["dept"])
    df_indices = df_indices[df_indices["dept"].isin(DEPTS_METRO)]  # Carte métropole uniquement
    
    if df_indices.empty:
        st.warning("No datas suffisantes pour calculer l'comparative index.")
        return
    
    # Statistiques globales
    indice_mean = df_indices["indice_comparatif"].mean()
    indice_min = df_indices["indice_comparatif"].min()
    indice_max = df_indices["indice_comparatif"].max()
    
    dept_min = df_indices.loc[df_indices["indice_comparatif"].idxmin(), "dept"]
    dept_max = df_indices.loc[df_indices["indice_comparatif"].idxmax(), "dept"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lowest Index", f"{DEPT_NAMES.get(dept_min, dept_min)}", f"{indice_min:.2f}")
    with col2:
        st.metric("Average", "Metropolitan France", f"{indice_mean:.2f}")
    with col3:
        st.metric("Highest Index", f"{DEPT_NAMES.get(dept_max, dept_max)}", f"{indice_max:.2f}")
    
    st.divider()
    
    # Carte choroplèthe
    st.subheader("Carte de l'comparative index")
    
    patho_label = f"{patho}" + (f" - {patho_niv2}" if patho_niv2 else "")
    
    st.info(
        f"**Interpretation** : L'écart entre le département le plus bas ({indice_min:.2f}) "
        f"et le plus haut ({indice_max:.2f}) est de **{(indice_max/indice_min - 1)*100:.0f}%**. "
        f"Les départements en rouge ont une prévalence supérieure à ce que leur structure "
        f"démographique laisserait attendre ; ceux en bleu ont une prévalence inférieure."
    )
    
    fig_carte = carte_indice_comparatif(df_indices, geojson, patho_label, year)
    st.plotly_chart(fig_carte, use_container_width=True)
    
    # Outre-mer (si sélectionné)
    if include_outremer:
        st.subheader("Overseas Departments")
        
        df_indices_om = indice_comparatif(
            df_filtered[df_filtered["dept"].isin(DEPTS_OUTREMER)], 
            df_national_filtered, 
            ["dept"]
        )
        
        if not df_indices_om.empty:
            df_indices_om["Department"] = df_indices_om["dept"].map(DEPT_NAMES)
            df_indices_om = df_indices_om[["Department", "observe", "attendu", "indice_comparatif"]]
            df_indices_om.columns = ["Department", "Observed", "Expected", "Comparative Index"]
            
            st.dataframe(
                df_indices_om.style.format({
                    "Observed": "{:,.0f}",
                    "Expected": "{:,.0f}",
                    "Comparative Index": "{:.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Insufficient data pour les DOM-TOM.")
    
    st.divider()
    
    # Slope chart : classement brut vs standardisé
    st.subheader("Raw vs Standardized Prevalence : what ranking change ?")
    
    st.markdown("""
    Standardization allows de compare departments indépendamment de leur 
    structure par âge. Certains départements changent fortement de position selon 
    qu'on regarde la prévalence brute ou standardisée.
    """)
    
    # Calculer prévalence brute et standardisée
    df_brute = prevalence_brute(df_filtered, ["dept"])
    df_std = prevalence_standardisee_directe(df_filtered, df_ref, ["dept"])
    
    df_compare = df_brute.merge(df_std, on="dept", how="inner")
    df_compare = df_compare[df_compare["dept"].isin(DEPTS_METRO)]
    
    if not df_compare.empty:
        fig_slope = slope_chart_classement(df_compare)
        st.plotly_chart(fig_slope, use_container_width=True)
    
    st.divider()
    
    # Classement détaillé
    st.subheader("Department Rankings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔴 Highest Indexs**")
        df_top = df_indices.nlargest(10, "indice_comparatif").copy()
        df_top["Department"] = df_top["dept"].map(DEPT_NAMES)
        df_top = df_top[["Department", "dept", "indice_comparatif"]]
        df_top.columns = ["Department", "Code", "Index"]
        st.dataframe(
            df_top.style.format({"Index": "{:.2f}"}),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("**🔵 Lowest Indexs**")
        df_bottom = df_indices.nsmallest(10, "indice_comparatif").copy()
        df_bottom["Department"] = df_bottom["dept"].map(DEPT_NAMES)
        df_bottom = df_bottom[["Department", "dept", "indice_comparatif"]]
        df_bottom.columns = ["Department", "Code", "Index"]
        st.dataframe(
            df_bottom.style.format({"Index": "{:.2f}"}),
            use_container_width=True,
            hide_index=True
        )


if __name__ == "__main__":
    main()
else:
    main()
