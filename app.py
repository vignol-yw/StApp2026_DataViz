import streamlit as st

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="Cardiovascular Diseases in France",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.prepare import check_data_ready
from utils.data_loader import (
    load_pathologies, load_ref_age_sexe, load_national_rates, load_geojson,
    get_available_years, get_pathologies_niv1, get_pathologies_niv2
)
from utils.constants import PATHO_CARDIO, DEPTS_METRO, DEPTS_OUTREMER


def main():
    # Check that data is prepared
    if not check_data_ready():
        st.error(
            "Prepared data is missing.\n\n"
            "Run the following command to prepare the data:\n"
            "```\npython -m utils.prepare\n```"
        )
        st.stop()
    
    # Load data (with cache)
    @st.cache_data(show_spinner="Loading data...")
    def load_all_data():
        return {
            "df": load_pathologies(),
            "df_ref": load_ref_age_sexe(),
            "df_national": load_national_rates(),
            "geojson": load_geojson()
        }
    
    try:
        data = load_all_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    df = data["df"]
    
    # Navigation with st.navigation
    pages = {
        "Introduction": [
            st.Page("pages/01_poids.py", title="Disease Burden"),
        ],
        "Who is Affected?": [
            st.Page("pages/02_age.py", title="Age"),
            st.Page("pages/03_sexe.py", title="Sex"),
        ],
        "Where?": [
            st.Page("pages/04_territoire.py", title="Territory"),
        ],
        "When?": [
            st.Page("pages/05_evolution.py", title="Temporal Evolution"),
        ],
        "Advanced Analysis": [
            st.Page("pages/06_acp.py", title="What Goes Together (PCA)"),
        ],
        "Conclusion": [
            st.Page("pages/07_conclusion.py", title="Summary"),
            st.Page("pages/08_sources.py", title="Sources and Limitations"),
        ],
    }
    
    pg = st.navigation(pages)
    
    # Sidebar: global filters
    with st.sidebar:
        st.header("Global Filters")
        
        # Year
        years = get_available_years(df)
        selected_year = st.selectbox(
            "Year",
            options=years,
            index=len(years) - 1,  # Last year by default
            key="global_year"
        )
        
        # Pathology level 1
        pathos_niv1 = get_pathologies_niv1(df)
        default_idx = pathos_niv1.index(PATHO_CARDIO) if PATHO_CARDIO in pathos_niv1 else 0
        selected_patho_niv1 = st.selectbox(
            "Pathology Category",
            options=pathos_niv1,
            index=default_idx,
            key="global_patho_niv1"
        )
        
        # Pathology level 2 (optional)
        pathos_niv2 = get_pathologies_niv2(df, selected_patho_niv1)
        if pathos_niv2:
            selected_patho_niv2 = st.selectbox(
                "Sub-pathology (optional)",
                options=["All"] + pathos_niv2,
                index=0,
                key="global_patho_niv2"
            )
        else:
            selected_patho_niv2 = "All"
        
        # Territory
        territoire_options = ["Metropolitan France", "Entire France (with overseas)"]
        selected_territoire = st.radio(
            "Territory",
            options=territoire_options,
            index=0,
            key="global_territoire"
        )
        
        st.divider()
        st.caption("Data: National Health Insurance (Cnam)")
        st.caption("Pathology Mapping 2015-2024")
    
    # Store filters in session_state for pages
    st.session_state["data"] = data
    st.session_state["selected_year"] = selected_year
    st.session_state["selected_patho_niv1"] = selected_patho_niv1
    st.session_state["selected_patho_niv2"] = selected_patho_niv2 if selected_patho_niv2 != "All" else None
    st.session_state["include_outremer"] = selected_territoire == "Entire France (with overseas)"
    st.session_state["depts_filter"] = (
        DEPTS_METRO + DEPTS_OUTREMER if st.session_state["include_outremer"] else DEPTS_METRO
    )
    
    # Run the selected page
    pg.run()


if __name__ == "__main__":
    main()