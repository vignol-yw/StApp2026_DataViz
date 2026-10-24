import streamlit as st
import pandas as pd

from utils.pca import prepare_pca_data, run_pca, interpret_axis
from utils.plots import scree_plot, cercle_correlations, projection_individus


def main():
    st.title("🔬 What Goes Together (ACP)")
    st.markdown(
        """
        Principal component analysis allows distinguishing departments that are similar
        sur les pathologies et those that are more different, en reduisant la complexite du jeu de donnees.
        """
    )

    data = st.session_state.get("data")
    if data is None:
        st.error("Data not loaded.")
        return

    df = data["df"]
    df_ref = data["df_ref"]
    geojson = data["geojson"]
    year = st.session_state.get("selected_year", int(df["annee"].max()))
    include_outremer = st.session_state.get("include_outremer", False)

    if df.empty:
        st.warning("No data disponible pour l'ACP.")
        return

    df_for_pca = df[df["annee"] == year].copy()
    df_for_pca = df_for_pca[df_for_pca["dept"].notna()]

    if df_for_pca.empty:
        st.warning("Pas de donnee pour l'annee choisie.")
        return

    pca_df, depts_exclus, pathos_exclues = prepare_pca_data(
        df_for_pca,
        df_ref,
        year,
        include_outremer=include_outremer,
        min_completeness=0.7,
    )

    if pca_df.empty or pca_df.shape[1] < 2:
        st.warning("Trop peu de variables ou de departements disponibles pour lancer l'ACP.")
        return

    if depts_exclus:
        st.info(f"Excluded departments pour incompletude : {', '.join(depts_exclus[:10])}")
    if pathos_exclues:
        st.info(f"Excluded variables pour incompletude : {', '.join(pathos_exclues[:10])}")

    result = run_pca(pca_df, n_components=min(4, min(pca_df.shape)))
    variance = result["variance_ratio"]

    st.subheader("Scree plot")
    st.plotly_chart(scree_plot(variance.tolist()), use_container_width=True)

    ax1 = st.selectbox("Horizontal axis", list(range(1, min(4, len(variance)) + 1)), index=0)
    ax2 = st.selectbox("Vertical axis", list(range(1, min(4, len(variance)) + 1)), index=1)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Correlation circle")
        fig_circle = cercle_correlations(result["loadings"], ax1 - 1, ax2 - 1)
        st.plotly_chart(fig_circle, use_container_width=True)
    with col2:
        st.subheader("Department projection")
        fig_proj = projection_individus(result["coords"], ax1 - 1, ax2 - 1)
        st.plotly_chart(fig_proj, use_container_width=True)

    st.subheader("Correlation matrix")
    corr = pca_df.corr()
    st.dataframe(corr.round(3), use_container_width=True)

    st.subheader("Department contributions")
    contrib = result["contributions"].round(2)
    st.dataframe(contrib, use_container_width=True)

    st.subheader("Axis interpretation")
    axis_text = []
    for idx in range(min(2, result["loadings"].shape[1])):
        axis_label = f"PC{idx + 1}"
        vals = result["loadings"][axis_label]
        axis_text.append(f"**{axis_label}** : {interpret_axis(vals)}")
    st.markdown("\n\n".join(axis_text))

    st.caption("Reading the axes se fait a partir des correlations entre variables et dimensions ; elle ne constitue pas une preuve causale.")


if __name__ == "__main__":
    main()
else:
    main()
