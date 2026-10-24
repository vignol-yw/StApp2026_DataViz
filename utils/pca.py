import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Optional

from .stats import prevalence_standardisee_directe
from .constants import DEPTS_METRO, DEPTS_OUTREMER


def prepare_pca_data(
    df: pd.DataFrame,
    df_ref: pd.DataFrame,
    annee: int,
    include_outremer: bool = False,
    min_completeness: float = 0.8
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """
    Prépare les données pour l'ACP : matrice départements × pathologies.
    
    Args:
        df: DataFrame des pathologies
        df_ref: DataFrame de référence âge × sexe
        annee: Année d'analyse
        include_outremer: Inclure les DOM-TOM
        min_completeness: Seuil minimal de complétude (défaut 80%)
    
    Returns:
        Tuple (DataFrame pivotée, liste depts exclus, liste pathos exclues)
    """
    # Filtrer année et départements
    depts = DEPTS_METRO.copy()
    if include_outremer:
        depts.extend(DEPTS_OUTREMER)
    
    df_year = df[(df["annee"] == annee) & (df["dept"].isin(depts))]
    
    # Calculer prévalence standardisée par département et pathologie
    df_prev = prevalence_standardisee_directe(
        df_year, df_ref, 
        group_cols=["dept", "patho_niv1"]
    )
    
    # Pivoter : lignes = départements, colonnes = pathologies
    df_pivot = df_prev.pivot(index="dept", columns="patho_niv1", values="prevalence_std")
    
    # Identifier les colonnes et lignes trop incomplètes
    col_completeness = df_pivot.notna().mean()
    row_completeness = df_pivot.notna().mean(axis=1)
    
    pathos_exclues = col_completeness[col_completeness < min_completeness].index.tolist()
    depts_exclus = row_completeness[row_completeness < min_completeness].index.tolist()
    
    # Filtrer
    df_pivot = df_pivot.drop(columns=pathos_exclues, errors="ignore")
    df_pivot = df_pivot.drop(index=depts_exclus, errors="ignore")
    
    # Imputer les valeurs manquantes restantes par la médiane
    df_pivot = df_pivot.fillna(df_pivot.median())
    
    return df_pivot, depts_exclus, pathos_exclues


def run_pca(
    df_pivot: pd.DataFrame,
    n_components: Optional[int] = None
) -> dict:
    """
    Exécute l'ACP sur la matrice départements × pathologies.
    
    Args:
        df_pivot: DataFrame pivotée (index=dept, colonnes=pathologies)
        n_components: Nombre de composantes (défaut: min(n_obs, n_var))
    
    Returns:
        Dictionnaire avec :
        - pca: objet PCA fitted
        - scaler: StandardScaler fitted
        - coords: coordonnées des individus (départements)
        - loadings: corrélations variables-axes
        - variance_ratio: variance expliquée par axe
        - contributions: contributions des individus aux axes
    """
    if n_components is None:
        n_components = min(df_pivot.shape)
    
    # Centrer-réduire
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_pivot.values)
    
    # ACP
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(X_scaled)
    
    # Coordonnées des individus
    coord_cols = [f"PC{i+1}" for i in range(n_components)]
    df_coords = pd.DataFrame(coords, index=df_pivot.index, columns=coord_cols)
    
    # Loadings (corrélations variables-axes)
    # loadings = composantes × sqrt(variance expliquée)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    df_loadings = pd.DataFrame(
        loadings, 
        index=df_pivot.columns, 
        columns=coord_cols
    )
    
    # Contributions des individus aux axes (en %)
    # contrib_ik = coord_ik² / sum_i(coord_ik²) × 100
    contrib = (coords ** 2) / (coords ** 2).sum(axis=0) * 100
    df_contrib = pd.DataFrame(contrib, index=df_pivot.index, columns=coord_cols)
    
    return {
        "pca": pca,
        "scaler": scaler,
        "coords": df_coords,
        "loadings": df_loadings,
        "variance_ratio": pca.explained_variance_ratio_,
        "contributions": df_contrib,
        "variables": list(df_pivot.columns),
        "individus": list(df_pivot.index),
    }


def interpret_axis(loadings: pd.Series, threshold: float = 0.5) -> str:
    """
    Génère une interprétation textuelle d'un axe à partir des loadings.
    
    Args:
        loadings: Série des corrélations variable-axe
        threshold: Seuil de corrélation significative
    
    Returns:
        Texte d'interprétation
    """
    positive = loadings[loadings > threshold].sort_values(ascending=False)
    negative = loadings[loadings < -threshold].sort_values()
    
    parts = []
    
    if len(positive) > 0:
        pos_vars = ", ".join(positive.index[:3])
        parts.append(f"Corrélé positivement avec : {pos_vars}")
    
    if len(negative) > 0:
        neg_vars = ", ".join(negative.index[:3])
        parts.append(f"Corrélé négativement avec : {neg_vars}")
    
    if len(parts) == 0:
        return "Axe peu différenciant (aucune corrélation forte)."
    
    return " | ".join(parts)


def get_correlation_matrix(df_pivot: pd.DataFrame) -> pd.DataFrame:
    """Calcule la matrice de corrélation entre pathologies."""
    return df_pivot.corr()
