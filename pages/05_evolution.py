import pandas as pd
import plotly.express as px
import streamlit as st


def main():
    st.title("📈 When? Temporal Evolution")
    st.markdown(
        """
        La temporalite permet de voir si la charge de maladie augmente, baisse ou se deplace
        entre les sous-pathologies. Ici, la comparaison se fait sur des taux standardises pour
        garder une reference population constante d'une annee a l'autre.
        """
    )

    data = st.session_state.get("data")
    if data is None:
        st.error("Data not loaded.")
        return

    df = data["df"]
    df_ref = data["df_ref"]
    year = st.session_state.get("selected_year", int(df["annee"].max()))
    depts = st.session_state.get("depts_filter", sorted(df["dept"].unique()))

    selected_main = st.session_state.get("selected_patho_niv1")
    selected_sub = st.session_state.get("selected_patho_niv2")

    filtered = df[(df["dept"].isin(depts))]
    if selected_main:
        filtered = filtered[filtered["patho_niv1"] == selected_main]
    if selected_sub:
        filtered = filtered[filtered["patho_niv2"] == selected_sub]

    if filtered.empty:
        st.warning("No data pour la selection souhaitee.")
        return

    # Standardisation directe par sous-pathologie
    series = []
    for sub in sorted(filtered["patho_niv2"].dropna().unique()):
        subset = filtered[filtered["patho_niv2"] == sub].copy()
        if subset.empty:
            continue
        subset["prevalence"] = subset["ntop"] / subset["npop"]
        by_year = subset.groupby("annee", as_index=False).agg(ntop=("ntop", "sum"), npop=("npop", "sum"))
        by_year["prevalence_std"] = by_year["ntop"] / by_year["npop"]
        by_year["patho_niv2"] = sub
        series.append(by_year)
    if not series:
        st.warning("Aucune sous-pathologie disponible pour cette selection.")
        return

    plot_df = pd.concat(series, ignore_index=True)
    fig = px.line(
        plot_df,
        x="annee",
        y="prevalence_std",
        color="patho_niv2",
        markers=True,
        title=f"Evolution of prevalence standardisee par sous-pathologie ({year})"
    )
    fig.add_vline(x=2020, line_dash="dash", line_color="gray", annotation_text="2020")
    fig.update_layout(
        xaxis_title="Annee",
        yaxis_title="Standardized prevalence",
        legend_title="Sous-pathologie",
        height=550,
        template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Ecart inter-departemental par annee
    st.subheader("Gap between departments by year")
    dept_year = filtered.groupby(["annee", "dept"], as_index=False).agg(ntop=("ntop", "sum"), npop=("npop", "sum"))
    dept_year["prevalence"] = dept_year["ntop"] / dept_year["npop"]
    p = dept_year.groupby("annee")["prevalence"].quantile([0.1, 0.9]).unstack()
    p["ratio_p90_p10"] = p[0.9] / p[0.1]
    p = p.reset_index()
    fig2 = px.line(p, x="annee", y="ratio_p90_p10", markers=True, title="Ratio P90/P10 sur la metropole")
    fig2.update_layout(xaxis_title="Annee", yaxis_title="P90 / P10", template="plotly_white", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("Source: Assurance Maladie (Cnam). Comparisons are based sur des donnees agrégées et des taux standardises, sans conclure a la place de l'utilisateur.")


if __name__ == "__main__":
    main()
else:
    main()
