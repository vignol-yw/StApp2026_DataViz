import streamlit as st
from utils.plots import pyramide_ages, heatmap_ratio_sexe
from utils.stats import ratio_hommes_femmes


def main():
    st.title("Who is Affected? Sex")
    
    st.markdown("""
    Sex influences the prevalence of many pathologies, both for biological 
    and behavioral reasons. This page presents the differences between 
    men and women in the treatment of pathologies.
    """)
    
    # Récupérer les données
    data = st.session_state.get("data")
    if data is None:
        st.error("Data not loaded.")
        return
    
    df = data["df"]
    year = st.session_state.get("selected_year", df["annee"].max())
    depts = st.session_state.get("depts_filter")
    patho = st.session_state.get("selected_patho_niv1")
    
    df_year = df[(df["annee"] == year) & (df["dept"].isin(depts))]
    
    # Age Pyramid
    st.subheader(f"Age Pyramid : {patho}")
    
    # Calculer ratio global pour cette pathologie
    df_patho = df_year[df_year["patho_niv1"] == patho]
    ratio_global = ratio_hommes_femmes(df_patho)
    
    if not ratio_global.empty and "ratio_h_f" in ratio_global.columns:
        ratio_val = ratio_global["ratio_h_f"].values[0]
        if ratio_val > 1:
            st.info(
                f"**Interpretation** : Pour cette pathologie, the male/female ratio est de "
                f"**{ratio_val:.2f}** : men are **{(ratio_val-1)*100:.0f}%** plus "
                f"nombreux que les femmes parmi patients treated."
            )
        elif ratio_val < 1:
            st.info(
                f"**Interpretation** : Pour cette pathologie, the male/female ratio est de "
                f"**{ratio_val:.2f}** : women are **{(1/ratio_val-1)*100:.0f}%** plus "
                f"nombreuses que les hommes parmi patients treated."
            )
        else:
            st.info("**Interpretation** : La répartition hommes/femmes est équilibrée.")
    
    fig_pyramide = pyramide_ages(df_year, patho)
    st.plotly_chart(fig_pyramide, use_container_width=True)
    
    st.caption(
        "The pyramid allows de visualiser la distribution par âge séparément "
        "pour les hommes (à gauche) et les femmes (à droite)."
    )
    
    st.divider()
    
    # Heatmap ratio H/F par pathologie et âge
    st.subheader("Male/Female Ratio par pathologie et classe d'âge")
    
    st.info(
        "**Interpretation** : Cette heatmap montre le ratio de prévalence hommes/femmes "
        "pour chaque combinaison pathologie × classe d'âge. Un ratio **supérieur à 1** "
        "(rouge) indique une male overrepresentation, un ratio **inférieur à 1** "
        "(bleu) une female overrepresentation."
    )
    
    fig_ratio = heatmap_ratio_sexe(df_year)
    st.plotly_chart(fig_ratio, use_container_width=True)
    
    st.divider()
    
    # Tableau récapitulatif par pathologie
    st.subheader("Summary par pathologie")
    
    df_ratio_patho = ratio_hommes_femmes(df_year, ["patho_niv1"])
    df_ratio_patho = df_ratio_patho.sort_values("ratio_h_f", ascending=False)
    
    # Identifier les extrêmes
    if not df_ratio_patho.empty:
        patho_h = df_ratio_patho.iloc[0]
        patho_f = df_ratio_patho.iloc[-1]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Most masculine",
                patho_h["patho_niv1"][:35] + "...",
                f"Ratio H/F = {patho_h['ratio_h_f']:.2f}"
            )
        with col2:
            st.metric(
                "Most feminine",
                patho_f["patho_niv1"][:35] + "...",
                f"Ratio H/F = {patho_f['ratio_h_f']:.2f}"
            )
    
    with st.expander("📋 See table des ratios par pathologie"):
        import pandas as pd
        df_display = df_ratio_patho[["patho_niv1", "prev_hommes", "prev_femmes", "ratio_h_f"]].copy()
        df_display.columns = ["Pathology", "Male Prevalence", "Female Prevalence", "Ratio H/F"]
        
        st.dataframe(
            df_display.style.format({
                "Male Prevalence": "{:.2%}",
                "Female Prevalence": "{:.2%}",
                "Ratio H/F": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )


if __name__ == "__main__":
    main()
else:
    main()
