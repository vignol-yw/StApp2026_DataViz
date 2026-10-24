import streamlit as st
import pandas as pd

from utils.plots import carte_indice_comparatif
from utils.stats import indice_comparatif


def main():
    st.title("📝 Conclusion")
    st.markdown(
        """
        This summary compares three cardiac sub-pathologies major. Elle permet de lire,
        a cote, leur territorial distribution et d'identify gaps by department.
        """
    )

    data = st.session_state.get("data")
    if data is None:
        st.error("Data not loaded.")
        return

    df = data["df"]
    df_national = data["df_national"]
    geojson = data["geojson"]
    year = st.session_state.get("selected_year", int(df["annee"].max()))
    selected_patho = st.session_state.get("selected_patho_niv1") or "Maladies cardioneurovasculaires"
    in_outremer = st.session_state.get("include_outremer", False)

    pathos = [
        "Coronary disease",
        "Stroke",
        "Heart failure",
    ]

    cols = st.columns(3)
    for i, patho in enumerate(pathos):
        with cols[i]:
            df_patho = df[(df["annee"] == year) & (df["patho_niv2"] == patho)]
            if df_patho.empty:
                st.warning(f"No data pour {patho}.")
                continue
            df_nat_patho = df_national[(df_national["annee"] == year) & (df_national["patho_niv2"] == patho)]
            if df_nat_patho.empty:
                st.warning(f"No national rate pour {patho}.")
                continue
            idx = indice_comparatif(df_patho, df_nat_patho, ["dept"])
            fig = carte_indice_comparatif(idx, geojson, patho, year)
            st.plotly_chart(fig, use_container_width=True)

    st.caption("Each map compares the department to the national average for the given sub-pathology. The scale is centered on 1. ")


if __name__ == "__main__":
    main()
else:
    main()
