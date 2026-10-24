import streamlit as st
import pandas as pd
from utils.plots import heatmap_age_pathologie, bar_pathologies
from utils.stats import prevalence_brute
from utils.constants import ORDRE_AGE


def main():
    st.title("👶 Who is Affected? Age")
    
    st.markdown("""
    Age is a determining factor in the prevalence of chronic pathologies. 
    This page explores the age distribution of different pathologies 
    and highlights the proportion of patients under 65 years old.
    """)
    
    # Get data
    data = st.session_state.get("data")
    if data is None:
        st.error("Data not loaded.")
        return
    
    df = data["df"]
    year = st.session_state.get("selected_year", df["annee"].max())
    depts = st.session_state.get("depts_filter")
    
    df_year = df[(df["annee"] == year) & (df["dept"].isin(depts))]
    
    # Heatmap pathology × age
    st.subheader("Prevalence by Pathology and Age Group")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        log_scale = st.checkbox("Logarithmic scale", value=True, key="heatmap_log")
    
    st.info(
        "**Interpretation**: Each cell represents the prevalence (proportion of patients) "
        "for a pathology and an age range. The logarithmic scale allows "
        "better visualization of differences between low and high values."
    )
    
    fig_heatmap = heatmap_age_pathologie(df_year, log_scale=log_scale)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.divider()
    
    # Proportion under 65
    st.subheader("Proportion of Patients Under 65 Years Old")
    
    age_order_map = {age: idx for idx, age in enumerate(ORDRE_AGE)}
    classes_moins_65 = [age for age in ORDRE_AGE if age_order_map.get(age, 99) < age_order_map.get("65-69", 99)]

    df_moins65 = df_year[df_year["classe_age"].isin(classes_moins_65)]
    df_plus65 = df_year[~df_year["classe_age"].isin(classes_moins_65)]
    
    eff_moins65 = df_moins65.groupby("patho_niv1")["ntop"].sum()
    eff_plus65 = df_plus65.groupby("patho_niv1")["ntop"].sum()
    eff_total = df_year.groupby("patho_niv1")["ntop"].sum()
    
    df_age_summary = pd.DataFrame({
        "Pathologie": eff_total.index,
        "Total": eff_total.values,
        "Moins de 65 ans": eff_moins65.reindex(eff_total.index, fill_value=0).values,
        "65 ans et plus": eff_plus65.reindex(eff_total.index, fill_value=0).values
    })
    df_age_summary["Part < 65 ans (%)"] = (
        df_age_summary["Moins de 65 ans"] / df_age_summary["Total"] * 100
    ).round(1)
    df_age_summary = df_age_summary.sort_values("Part < 65 ans (%)", ascending=False)
    
    # Find extremes
    patho_plus_jeune = df_age_summary.iloc[0]
    patho_plus_agee = df_age_summary.iloc[-1]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Youngest pathology",
            patho_plus_jeune["Pathologie"][:40] + "...",
            f"{patho_plus_jeune['Part < 65 ans (%)']:.0f}% under 65"
        )
    with col2:
        st.metric(
            "Oldest pathology",
            patho_plus_agee["Pathologie"][:40] + "...",
            f"{patho_plus_agee['Part < 65 ans (%)']:.0f}% under 65"
        )
    
    st.info(
        f"**Interpretation**: The proportion of patients under 65 varies greatly "
        f"by pathology: from **{patho_plus_agee['Part < 65 ans (%)']:.0f}%** "
        f"for pathologies mainly affecting elderly people, "
        f"to **{patho_plus_jeune['Part < 65 ans (%)']:.0f}%** for those also affecting "
        f"younger individuals."
    )
    
    # Summary table
    with st.expander("📋 See detailed table"):
        st.dataframe(
            df_age_summary.style.format({
                "Total": "{:,.0f}",
                "Moins de 65 ans": "{:,.0f}",
                "65 ans et plus": "{:,.0f}",
                "Part < 65 ans (%)": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    # Distribution by age for selected pathology
    st.subheader("Age Distribution of Selected Pathology")
    
    patho = st.session_state.get("selected_patho_niv1")
    df_patho = df_year[df_year["patho_niv1"] == patho]
    
    if df_patho.empty:
        st.warning("No data for this pathology.")
        return
    
    # Aggregate by age group
    df_age = df_patho.groupby("classe_age", as_index=False).agg({
        "ntop": "sum",
        "npop": "sum"
    })
    df_age["prevalence"] = df_age["ntop"] / df_age["npop"]
    
    # Sort
    df_age["ordre"] = df_age["classe_age"].apply(lambda x: ORDRE_AGE.index(x) if x in ORDRE_AGE else 99)
    df_age = df_age.sort_values("ordre")
    
    # Calculate proportion < 65 for this pathology
    patho_row = df_age_summary[df_age_summary["Pathologie"] == patho]
    if not patho_row.empty:
        part_moins65 = patho_row["Part < 65 ans (%)"].values[0]
        st.info(
            f"**{patho}**: **{part_moins65:.0f}%** of patients are under 65 years old."
        )
    
    import plotly.express as px
    fig = px.bar(
        df_age,
        x="classe_age",
        y="ntop",
        title=f"Patient Numbers by Age Group: {patho} ({year})",
        labels={"classe_age": "Age Group", "ntop": "Number of Patients"}
    )
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
else:
    main()
