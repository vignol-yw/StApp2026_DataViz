import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional

from .constants import DEPT_NAMES, REGION_NAMES, DEPT_TO_REGION, CATEGORIES_TRAITEMENT


# Palette accessible (ColorBrewer)
COLORS = {
    "primary": "#2171b5",      # Bleu principal
    "secondary": "#6baed6",    # Bleu secondaire
    "highlight": "#d7301f",    # Rouge pour mise en évidence
    "neutral": "#969696",      # Gris
    "positive": "#238b45",     # Vert
    "negative": "#d7301f",     # Rouge
    "divergent_low": "#2166ac",   # Bleu (bas)
    "divergent_mid": "#f7f7f7",   # Blanc (milieu)
    "divergent_high": "#b2182b",  # Rouge (haut)
}

# Échelle divergente pour les indices comparatifs
DIVERGENT_SCALE = [
    [0.0, "#2166ac"],
    [0.25, "#67a9cf"],
    [0.5, "#f7f7f7"],
    [0.75, "#ef8a62"],
    [1.0, "#b2182b"]
]

SOURCE_TEXT = "Source: National Health Insurance (Cnam), Pathology Mapping"


def format_prevalence(val: float, per_mille: bool = True) -> str:
    """Formate une prévalence pour affichage."""
    if pd.isna(val):
        return "N/A"
    if per_mille:
        return f"{val * 1000:.1f}‰"
    return f"{val * 100:.2f}%"


def bar_pathologies(
    df: pd.DataFrame,
    annee: int,
    highlight_patho: Optional[str] = None,
    title: Optional[str] = None
) -> go.Figure:
    """
    Barres horizontales des pathologies triées par effectif.
    
    Args:
        df: DataFrame avec colonnes patho_niv1, ntop
        annee: Année affichée (pour le titre)
        highlight_patho: Pathologie à mettre en évidence
        title: Titre personnalisé
    """
    # Agréger par pathologie
    df_agg = df.groupby("patho_niv1", as_index=False)["ntop"].sum()
    df_agg = df_agg.sort_values("ntop", ascending=True)
    
    # Couleurs
    colors = [
        COLORS["highlight"] if p == highlight_patho else COLORS["primary"]
        for p in df_agg["patho_niv1"]
    ]
    
    # Marquer les traitements
    df_agg["type"] = df_agg["patho_niv1"].apply(
        lambda x: "Traitement" if x in CATEGORIES_TRAITEMENT else "Pathologie"
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_agg["ntop"],
        y=df_agg["patho_niv1"],
        orientation="h",
        marker_color=colors,
        text=df_agg["ntop"].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}k"),
        textposition="outside",
        hovertemplate="%{y}<br>%{x:,.0f} patients<extra></extra>"
    ))
    
    if title is None:
        title = f"Patient Numbers by Pathology Category ({annee})"
    
    fig.update_layout(
        title=title,
        xaxis_title="Number of Patients",
        yaxis_title="",
        showlegend=False,
        height=600,
        margin=dict(l=300, r=50, t=60, b=80),
        annotations=[dict(
            text=SOURCE_TEXT,
            xref="paper", yref="paper",
            x=0, y=-0.12,
            showarrow=False,
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig


def treemap_cardio(
    df: pd.DataFrame,
    annee: int,
    title: Optional[str] = None
) -> go.Figure:
    """
    Treemap for cardiovascular sub-pathologies.
    """
    df_cardio = df[df["patho_niv1"] == "Maladies cardioneurovasculaires"].copy()
    
    # Aggregate by level 2
    df_agg = df_cardio.groupby("patho_niv2", as_index=False)["ntop"].sum()
    df_agg = df_agg[df_agg["patho_niv2"].notna()]
    
    if title is None:
        title = f"Cardiovascular Sub-Pathologies ({annee})"
    
    fig = px.treemap(
        df_agg,
        path=["patho_niv2"],
        values="ntop",
        color="ntop",
        color_continuous_scale="Blues",
        title=title
    )
    
    fig.update_traces(
        texttemplate="%{label}<br>%{value:,.0f}",
        hovertemplate="%{label}<br>%{value:,.0f} patients<extra></extra>"
    )
    
    fig.update_layout(
        height=500,
        margin=dict(t=60, b=40),
        coloraxis_showscale=False
    )
    
    return fig


def heatmap_age_pathologie(
    df: pd.DataFrame,
    log_scale: bool = True,
    title: Optional[str] = None
) -> go.Figure:
    """
    Heatmap pathologie × classe d'âge (prévalence).
    """
    from .constants import ORDRE_AGE
    
    # Calculer prévalence par patho × âge
    df_agg = df.groupby(["patho_niv1", "classe_age"], as_index=False).agg({
        "ntop": "sum",
        "npop": "sum"
    })
    df_agg["prevalence"] = df_agg["ntop"] / df_agg["npop"]
    
    # Pivoter
    df_pivot = df_agg.pivot(index="patho_niv1", columns="classe_age", values="prevalence")
    
    # Ordonner les colonnes
    age_order = [a for a in ORDRE_AGE if a in df_pivot.columns]
    df_pivot = df_pivot[age_order]
    
    # Log scale si demandé
    values = df_pivot.values
    if log_scale:
        values = np.log10(values + 1e-6)
    
    if title is None:
        title = "Prévalence par pathologie et classe d'âge"
        if log_scale:
            title += " (échelle log)"
    
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=df_pivot.columns.tolist(),
        y=df_pivot.index.tolist(),
        colorscale="Blues",
        hovertemplate="Pathologie: %{y}<br>Âge: %{x}<br>Prévalence: %{customdata:.2%}<extra></extra>",
        customdata=df_pivot.values
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Classe d'âge",
        yaxis_title="",
        height=600,
        margin=dict(l=300, t=60, b=80),
        annotations=[dict(
            text=SOURCE_TEXT,
            xref="paper", yref="paper",
            x=0, y=-0.15,
            showarrow=False,
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig


def pyramide_ages(
    df: pd.DataFrame,
    patho: str,
    title: Optional[str] = None
) -> go.Figure:
    """
    Pyramide des âges pour une pathologie donnée.
    """
    from .constants import ORDRE_AGE
    
    df_patho = df[df["patho_niv1"] == patho].copy()
    
    # Agréger par âge et sexe
    df_agg = df_patho.groupby(["classe_age", "sexe"], as_index=False)["ntop"].sum()
    
    # Séparer hommes et femmes
    df_h = df_agg[df_agg["sexe"] == "1"].set_index("classe_age")["ntop"]
    df_f = df_agg[df_agg["sexe"] == "2"].set_index("classe_age")["ntop"]
    
    # Ordonner
    ages = [a for a in ORDRE_AGE if a in df_h.index or a in df_f.index]
    
    hommes = [df_h.get(a, 0) for a in ages]
    femmes = [df_f.get(a, 0) for a in ages]
    
    if title is None:
        title = f"Pyramide des âges : {patho}"
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=ages,
        x=[-v for v in hommes],
        orientation="h",
        name="Hommes",
        marker_color="#4393c3",
        hovertemplate="Hommes %{y}: %{customdata:,.0f}<extra></extra>",
        customdata=hommes
    ))
    
    fig.add_trace(go.Bar(
        y=ages,
        x=femmes,
        orientation="h",
        name="Femmes",
        marker_color="#d6604d",
        hovertemplate="Femmes %{y}: %{x:,.0f}<extra></extra>"
    ))
    
    max_val = max(max(hommes), max(femmes))
    
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Nombre de patients",
            tickvals=[-max_val, -max_val/2, 0, max_val/2, max_val],
            ticktext=[f"{max_val/1e3:.0f}k", f"{max_val/2e3:.0f}k", "0", 
                     f"{max_val/2e3:.0f}k", f"{max_val/1e3:.0f}k"]
        ),
        yaxis_title="Classe d'âge",
        barmode="overlay",
        bargap=0.1,
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        annotations=[dict(
            text=SOURCE_TEXT,
            xref="paper", yref="paper",
            x=0, y=-0.12,
            showarrow=False,
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig


def heatmap_ratio_sexe(
    df: pd.DataFrame,
    title: Optional[str] = None
) -> go.Figure:
    """
    Heatmap du ratio hommes/femmes par pathologie et classe d'âge.
    Échelle divergente centrée sur 1.
    """
    from .constants import ORDRE_AGE
    from .stats import ratio_hommes_femmes
    
    # Calculer ratio par patho × âge
    df_ratio = ratio_hommes_femmes(df, ["patho_niv1", "classe_age"])
    
    # Pivoter
    df_pivot = df_ratio.pivot(index="patho_niv1", columns="classe_age", values="ratio_h_f")
    
    # Ordonner les colonnes
    age_order = [a for a in ORDRE_AGE if a in df_pivot.columns]
    df_pivot = df_pivot[age_order]
    
    if title is None:
        title = "Ratio hommes/femmes par pathologie et âge"
    
    # Normaliser les valeurs pour l'échelle divergente (0.5 à 2 → 0 à 1)
    values_norm = (df_pivot.values - 0.5) / 1.5  # 0.5→0, 1→0.33, 2→1
    values_norm = np.clip(values_norm, 0, 1)
    
    fig = go.Figure(data=go.Heatmap(
        z=values_norm,
        x=df_pivot.columns.tolist(),
        y=df_pivot.index.tolist(),
        colorscale=DIVERGENT_SCALE,
        zmin=0,
        zmax=1,
        hovertemplate="Pathologie: %{y}<br>Âge: %{x}<br>Ratio H/F: %{customdata:.2f}<extra></extra>",
        customdata=df_pivot.values,
        colorbar=dict(
            title="Ratio H/F",
            tickvals=[0, 0.33, 0.67, 1],
            ticktext=["0.5", "1", "1.5", "2+"]
        )
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Classe d'âge",
        yaxis_title="",
        height=600,
        margin=dict(l=300, t=60, b=80),
        annotations=[dict(
            text=f"{SOURCE_TEXT} | Ratio > 1 : plus d'hommes ; < 1 : plus de femmes",
            xref="paper", yref="paper",
            x=0, y=-0.15,
            showarrow=False,
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig


def carte_indice_comparatif(
    df_indices: pd.DataFrame,
    geojson: dict,
    patho: str,
    annee: int,
    title: Optional[str] = None
) -> go.Figure:
    """
    Choropleth map of comparative index by department.
    """
    if title is None:
        title = f"Comparative Index by Department: {patho} ({annee})"
    
    # Add department names
    df_map = df_indices.copy()
    df_map["dept_nom"] = df_map["dept"].map(DEPT_NAMES)
    
    # Normalize index for scale (0.7 to 1.3 → 0 to 1)
    df_map["indice_norm"] = (df_map["indice_comparatif"] - 0.7) / 0.6
    df_map["indice_norm"] = df_map["indice_norm"].clip(0, 1)
    
    # Use px.choropleth_map (Plotly 7.x)
    fig = px.choropleth_map(
        df_map,
        geojson=geojson,
        locations="dept",
        color="indice_norm",
        featureidkey="properties.code",
        color_continuous_scale=DIVERGENT_SCALE,
        range_color=[0, 1],
        hover_name="dept_nom",
        hover_data={
            "dept": True,
            "indice_comparatif": ":.2f",
            "indice_norm": False
        },
        map_style="carto-positron",
        center={"lat": 46.5, "lon": 2.5},
        zoom=4.5,
        opacity=0.8,
        title=title
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=50),
        coloraxis_colorbar=dict(
            title="Index",
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=["0.7", "0.85", "1.0", "1.15", "1.3"]
        ),
        annotations=[dict(
            text=f"{SOURCE_TEXT} | Index = 1: national average",
            xref="paper", yref="paper",
            x=0, y=-0.05,
            showarrow=False,
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig


def slope_chart_classement(
    df: pd.DataFrame,
    title: Optional[str] = None
) -> go.Figure:
    """
    Graphique en pentes : classement prévalence brute vs standardisée.
    """
    if title is None:
        title = "Classement des départements : prévalence brute vs standardisée"
    
    # Calculer les rangs
    df_ranked = df.copy()
    df_ranked["rang_brute"] = df_ranked["prevalence"].rank(ascending=False)
    df_ranked["rang_std"] = df_ranked["prevalence_std"].rank(ascending=False)
    df_ranked["dept_nom"] = df_ranked["dept"].map(DEPT_NAMES)
    
    fig = go.Figure()
    
    for _, row in df_ranked.iterrows():
        color = COLORS["highlight"] if abs(row["rang_brute"] - row["rang_std"]) > 10 else COLORS["neutral"]
        
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[row["rang_brute"], row["rang_std"]],
            mode="lines+markers",
            line=dict(color=color, width=1),
            marker=dict(size=6),
            name=row["dept_nom"],
            hovertemplate=(
                f"<b>{row['dept_nom']}</b><br>"
                f"Rang brut: {int(row['rang_brute'])}<br>"
                f"Rang standardisé: {int(row['rang_std'])}<extra></extra>"
            ),
            showlegend=False
        ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(
            tickvals=[0, 1],
            ticktext=["Prévalence brute", "Prévalence standardisée"],
            range=[-0.1, 1.1]
        ),
        yaxis=dict(
            title="Classement (1 = plus élevé)",
            autorange="reversed"
        ),
        height=600,
        annotations=[dict(
            text=f"{SOURCE_TEXT} | En rouge : départements dont le rang change de plus de 10 places",
            xref="paper", yref="paper",
            x=0, y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig


def courbes_evolution(
    df: pd.DataFrame,
    col_valeur: str = "prevalence_std",
    col_groupe: str = "patho_niv2",
    title: Optional[str] = None
) -> go.Figure:
    """
    Courbes d'évolution temporelle par groupe.
    """
    if title is None:
        title = "Évolution de la prévalence standardisée"
    
    fig = px.line(
        df,
        x="annee",
        y=col_valeur,
        color=col_groupe,
        markers=True,
        title=title
    )
    
    # Ajouter repère 2020
    fig.add_vline(
        x=2020, 
        line_dash="dash", 
        line_color="gray",
        annotation_text="2020",
        annotation_position="top"
    )
    
    fig.update_layout(
        xaxis_title="Année",
        yaxis_title="Prévalence standardisée",
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=150),
        annotations=[dict(
            text=SOURCE_TEXT,
            xref="paper", yref="paper",
            x=0, y=-0.35,
            showarrow=False,
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig


def scree_plot(variance_ratio: list, title: Optional[str] = None) -> go.Figure:
    """
    Éboulis des valeurs propres (ACP).
    """
    if title is None:
        title = "Variance expliquée par axe"
    
    n = len(variance_ratio)
    cumsum = np.cumsum(variance_ratio)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(go.Bar(
        x=[f"PC{i+1}" for i in range(n)],
        y=variance_ratio,
        name="Variance par axe",
        marker_color=COLORS["primary"]
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=[f"PC{i+1}" for i in range(n)],
        y=cumsum,
        mode="lines+markers",
        name="Variance cumulée",
        line=dict(color=COLORS["highlight"])
    ), secondary_y=True)
    
    fig.update_layout(
        title=title,
        xaxis_title="Composante",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    fig.update_yaxes(title_text="Variance expliquée", secondary_y=False)
    fig.update_yaxes(title_text="Variance cumulée", secondary_y=True, range=[0, 1])
    
    return fig


def cercle_correlations(
    loadings: pd.DataFrame,
    ax1: int = 0,
    ax2: int = 1,
    title: Optional[str] = None
) -> go.Figure:
    """
    Cercle des corrélations (ACP).
    """
    col1 = f"PC{ax1+1}"
    col2 = f"PC{ax2+1}"
    
    if title is None:
        title = f"Cercle des corrélations ({col1} vs {col2})"
    
    fig = go.Figure()
    
    # Cercle unité
    theta = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(
        x=np.cos(theta),
        y=np.sin(theta),
        mode="lines",
        line=dict(color="gray", dash="dash"),
        showlegend=False
    ))
    
    # Flèches des variables
    for var in loadings.index:
        x = loadings.loc[var, col1]
        y = loadings.loc[var, col2]
        
        fig.add_annotation(
            x=x, y=y,
            ax=0, ay=0,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=COLORS["primary"]
        )
        
        fig.add_trace(go.Scatter(
            x=[x*1.1],
            y=[y*1.1],
            mode="text",
            text=[var[:20] + "..." if len(var) > 20 else var],
            textposition="middle center",
            textfont=dict(size=9),
            showlegend=False,
            hoverinfo="text",
            hovertext=var
        ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(title=col1, range=[-1.2, 1.2], zeroline=True),
        yaxis=dict(title=col2, range=[-1.2, 1.2], zeroline=True, scaleanchor="x"),
        height=600,
        width=600
    )
    
    return fig


def projection_individus(
    coords: pd.DataFrame,
    ax1: int = 0,
    ax2: int = 1,
    color_by_region: bool = True,
    title: Optional[str] = None
) -> go.Figure:
    """
    Projection des individus (départements) dans le plan factoriel.
    """
    col1 = f"PC{ax1+1}"
    col2 = f"PC{ax2+1}"
    
    if title is None:
        title = f"Projection des départements ({col1} vs {col2})"
    
    df_plot = coords[[col1, col2]].copy()
    df_plot["dept"] = df_plot.index
    df_plot["dept_nom"] = df_plot["dept"].map(DEPT_NAMES)
    
    if color_by_region:
        df_plot["region"] = df_plot["dept"].map(DEPT_TO_REGION)
        df_plot["region_nom"] = df_plot["region"].map(REGION_NAMES)
        
        fig = px.scatter(
            df_plot,
            x=col1,
            y=col2,
            color="region_nom",
            hover_name="dept_nom",
            text="dept",
            title=title
        )
    else:
        fig = px.scatter(
            df_plot,
            x=col1,
            y=col2,
            hover_name="dept_nom",
            text="dept",
            title=title
        )
    
    fig.update_traces(textposition="top center", textfont_size=8)
    
    fig.update_layout(
        xaxis_title=col1,
        yaxis_title=col2,
        height=600,
        legend=dict(
            title="Région",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig


def trois_cartes_cote_a_cote(
    dfs: list[pd.DataFrame],
    geojson: dict,
    pathos: list[str],
    annee: int
) -> go.Figure:
    """
    Three side-by-side maps for the conclusion.
    """
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=pathos,
        specs=[[{"type": "choroplethmap"}] * 3],
        horizontal_spacing=0.02
    )
    
    for i, (df, patho) in enumerate(zip(dfs, pathos)):
        df_map = df.copy()
        df_map["dept_nom"] = df_map["dept"].map(DEPT_NAMES)
        df_map["indice_norm"] = (df_map["indice_comparatif"] - 0.7) / 0.6
        df_map["indice_norm"] = df_map["indice_norm"].clip(0, 1)
        
        fig.add_trace(go.Choroplethmap(
            geojson=geojson,
            locations=df_map["dept"],
            z=df_map["indice_norm"],
            featureidkey="properties.code",
            colorscale=DIVERGENT_SCALE,
            zmin=0,
            zmax=1,
            marker_opacity=0.8,
            marker_line_width=0.5,
            showscale=(i == 2),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Index: %{customdata[1]:.2f}<extra></extra>"
            ),
            customdata=df_map[["dept_nom", "indice_comparatif"]].values,
            colorbar=dict(
                title="Index",
                tickvals=[0, 0.5, 1],
                ticktext=["0.7", "1.0", "1.3"],
                x=1.02
            ) if i == 2 else None
        ), row=1, col=i+1)
    
    fig.update_layout(
        title=f"Territorial Comparison of Cardiovascular Sub-pathologies ({annee})",
        map=dict(style="carto-positron", center=dict(lat=46.5, lon=2.5), zoom=4),
        map2=dict(style="carto-positron", center=dict(lat=46.5, lon=2.5), zoom=4),
        map3=dict(style="carto-positron", center=dict(lat=46.5, lon=2.5), zoom=4),
        height=400,
        margin=dict(l=0, r=0, t=60, b=40)
    )
    
    return fig
