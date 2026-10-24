import streamlit as st
from utils.plots import bar_pathologies, treemap_cardio
from utils.constants import PATHO_CARDIO


def main():
    st.title("Disease Burden")
    
    st.markdown("""
    This first visualization presents the **number of patients** treated 
    for each major pathology category in France. Cardiovascular diseases 
    are among the most frequent pathologies. The treemap below details 
    the subcategories of this disease family.
    """)
    
    # Get data and filters
    data = st.session_state.get("data")
    if data is None:
        st.error("Data not loaded. Return to home page.")
        return
    
    df = data["df"]
    year = st.session_state.get("selected_year", df["annee"].max())
    depts = st.session_state.get("depts_filter", df["dept"].unique())
    
    # Filter data
    df_year = df[(df["annee"] == year) & (df["dept"].isin(depts))]
    
    # Horizontal bars for pathologies
    st.subheader("Patient Numbers by Pathology Category")
    
    # Calculate total cardio for context
    total_all = df_year["ntop"].sum()
    df_cardio = df_year[df_year["patho_niv1"] == PATHO_CARDIO]
    total_cardio = df_cardio["ntop"].sum()
    
    if total_all > 0:
        pct_cardio = total_cardio / total_all * 100
        st.info(
            f"**Interpretation**: In {year}, cardiovascular diseases represent "
            f"**{total_cardio/1e6:.1f} million** patients treated, "
            f"approximately **{pct_cardio:.0f}%** of all identified pathologies."
        )
    
    fig_bar = bar_pathologies(df_year, year, highlight_patho=PATHO_CARDIO)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.caption(
        "Note: The same person can be counted in multiple categories "
        "if they have multiple pathologies. 'Treatments' are not "
        "pathologies but prescriptions in the absence of identified pathology."
    )
    
    st.divider()
    
    # Treemap for cardio sub-pathologies
    st.subheader("Details of Cardiovascular Diseases")
    
    # Find the most frequent sub-pathology
    df_cardio_niv2 = df_cardio.groupby("patho_niv2", as_index=False)["ntop"].sum()
    df_cardio_niv2 = df_cardio_niv2[df_cardio_niv2["patho_niv2"].notna()]
    
    if not df_cardio_niv2.empty:
        top_patho = df_cardio_niv2.loc[df_cardio_niv2["ntop"].idxmax()]
        st.info(
            f"**Interpretation**: Among cardiovascular diseases, "
            f"the most frequent subcategory is '{top_patho['patho_niv2']}' "
            f"with **{top_patho['ntop']/1e6:.1f} million** patients."
        )
    
    fig_treemap = treemap_cardio(df_year, year)
    st.plotly_chart(fig_treemap, use_container_width=True)


if __name__ == "__main__":
    main()
else:
    main()
