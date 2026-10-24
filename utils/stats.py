import pandas as pd
import numpy as np
from typing import Optional


def prevalence_brute(
    df: pd.DataFrame,
    group_cols: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Calcule la prévalence brute par groupe.
    
    Args:
        df: DataFrame avec colonnes ntop, npop
        group_cols: Colonnes de regroupement (ex: ['annee', 'dept'])
    
    Returns:
        DataFrame avec colonnes de groupe + ntop, npop, prevalence
    """
    if group_cols is None:
        group_cols = []
    
    # Exclure les lignes avec ntop NULL
    df_valid = df[df["ntop"].notna()].copy()
    
    if len(group_cols) == 0:
        total_ntop = df_valid["ntop"].sum()
        total_npop = df_valid["npop"].sum()
        return pd.DataFrame({
            "ntop": [total_ntop],
            "npop": [total_npop],
            "prevalence": [total_ntop / total_npop if total_npop > 0 else np.nan]
        })
    
    result = df_valid.groupby(group_cols, as_index=False).agg({
        "ntop": "sum",
        "npop": "sum"
    })
    result["prevalence"] = result["ntop"] / result["npop"]
    result.loc[result["npop"] == 0, "prevalence"] = np.nan
    
    return result


def prevalence_standardisee_directe(
    df: pd.DataFrame,
    df_ref: pd.DataFrame,
    group_cols: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Calcule la prévalence standardisée par méthode directe.
    
    La prévalence de chaque case âge × sexe est pondérée par la structure
    de la population de référence.
    
    Args:
        df: DataFrame avec colonnes classe_age, sexe, ntop, npop
        df_ref: DataFrame de référence avec colonnes classe_age, sexe, pop_ref
        group_cols: Colonnes de regroupement supplémentaires
    
    Returns:
        DataFrame avec colonnes de groupe + prevalence_std
    """
    if group_cols is None:
        group_cols = []
    
    # Calcul de la prévalence par case
    case_cols = group_cols + ["classe_age", "sexe"]
    df_case = prevalence_brute(df, case_cols)
    
    # Joindre avec la structure de référence
    df_case = df_case.merge(df_ref[["classe_age", "sexe", "pop_ref"]], 
                            on=["classe_age", "sexe"], how="left")
    
    # Pondération
    df_case["prev_ponderee"] = df_case["prevalence"] * df_case["pop_ref"]
    
    # Agrégation
    if len(group_cols) == 0:
        total_poids = df_case["pop_ref"].sum()
        total_pond = df_case["prev_ponderee"].sum()
        return pd.DataFrame({
            "prevalence_std": [total_pond / total_poids if total_poids > 0 else np.nan]
        })
    
    result = df_case.groupby(group_cols, as_index=False).agg({
        "prev_ponderee": "sum",
        "pop_ref": "sum"
    })
    result["prevalence_std"] = result["prev_ponderee"] / result["pop_ref"]
    result = result.drop(columns=["prev_ponderee", "pop_ref"])
    
    return result


def indice_comparatif(
    df: pd.DataFrame,
    df_taux_nationaux: pd.DataFrame,
    group_cols: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Calcule l'indice comparatif (standardisation indirecte).
    
    Indice = Observé / Attendu
    où Attendu = somme(npop_local × taux_national_case)
    
    Les cases où ntop ou taux_national sont NULL sont exclues de façon cohérente
    de l'observé ET de l'attendu.
    
    Args:
        df: DataFrame avec colonnes annee, patho_niv1/2/3, classe_age, sexe, ntop, npop
        df_taux_nationaux: DataFrame avec colonnes correspondantes + taux_national
        group_cols: Colonnes de regroupement (ex: ['dept'])
    
    Returns:
        DataFrame avec colonnes de groupe + observe, attendu, indice_comparatif
    """
    if group_cols is None:
        group_cols = []
    
    # Colonnes de jointure pour les taux nationaux
    join_cols = ["annee", "patho_niv1", "patho_niv2", "patho_niv3", "classe_age", "sexe"]
    
    # Joindre avec les taux nationaux
    df_joined = df.merge(
        df_taux_nationaux[join_cols + ["taux_national"]],
        on=join_cols,
        how="left"
    )
    
    # Exclure les cases où ntop OU taux_national sont NULL (cohérence)
    df_valid = df_joined[
        df_joined["ntop"].notna() & 
        df_joined["taux_national"].notna()
    ].copy()
    
    # Calcul de l'attendu par case
    df_valid["attendu_case"] = df_valid["npop"] * df_valid["taux_national"]
    
    # Agrégation
    if len(group_cols) == 0:
        observe = df_valid["ntop"].sum()
        attendu = df_valid["attendu_case"].sum()
        return pd.DataFrame({
            "observe": [observe],
            "attendu": [attendu],
            "indice_comparatif": [observe / attendu if attendu > 0 else np.nan]
        })
    
    result = df_valid.groupby(group_cols, as_index=False).agg({
        "ntop": "sum",
        "attendu_case": "sum"
    }).rename(columns={"ntop": "observe", "attendu_case": "attendu"})
    
    result["indice_comparatif"] = result["observe"] / result["attendu"]
    result.loc[result["attendu"] == 0, "indice_comparatif"] = np.nan
    
    return result


def ratio_hommes_femmes(
    df: pd.DataFrame,
    group_cols: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Calcule le ratio de prévalence hommes/femmes.
    
    Args:
        df: DataFrame avec colonnes sexe (1=hommes, 2=femmes), ntop, npop
        group_cols: Colonnes de regroupement
    
    Returns:
        DataFrame avec colonnes de groupe + prev_hommes, prev_femmes, ratio_h_f
    """
    if group_cols is None:
        group_cols = []
    
    # Séparer hommes et femmes
    df_h = df[df["sexe"] == "1"].copy()
    df_f = df[df["sexe"] == "2"].copy()
    
    # Prévalence par groupe
    prev_h = prevalence_brute(df_h, group_cols)
    prev_f = prevalence_brute(df_f, group_cols)
    
    prev_h = prev_h.rename(columns={"prevalence": "prev_hommes", "ntop": "ntop_h", "npop": "npop_h"})
    prev_f = prev_f.rename(columns={"prevalence": "prev_femmes", "ntop": "ntop_f", "npop": "npop_f"})
    
    if len(group_cols) == 0:
        return pd.DataFrame({
            "prev_hommes": prev_h["prev_hommes"].values,
            "prev_femmes": prev_f["prev_femmes"].values,
            "ratio_h_f": prev_h["prev_hommes"].values / prev_f["prev_femmes"].values
        })
    
    result = prev_h.merge(prev_f, on=group_cols, how="outer")
    result["ratio_h_f"] = result["prev_hommes"] / result["prev_femmes"]
    result = result[group_cols + ["prev_hommes", "prev_femmes", "ratio_h_f"]]
    
    return result


def ecart_interdepartemental(
    df: pd.DataFrame,
    group_cols: Optional[list[str]] = None,
    depts_metro: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Calcule l'écart interdépartemental (ratio P90/P10) de la prévalence.
    
    Args:
        df: DataFrame avec colonnes dept, ntop, npop
        group_cols: Colonnes de regroupement (ex: ['annee'])
        depts_metro: Liste des départements à inclure (défaut: métropole)
    
    Returns:
        DataFrame avec colonnes de groupe + p10, p90, ratio_p90_p10
    """
    from .constants import DEPTS_METRO
    
    if depts_metro is None:
        depts_metro = DEPTS_METRO
    
    if group_cols is None:
        group_cols = []
    
    # Filtrer sur les départements métropolitains
    df_metro = df[df["dept"].isin(depts_metro)]
    
    # Prévalence par département et groupe
    prev_dept = prevalence_brute(df_metro, group_cols + ["dept"])
    
    # Calculer P10 et P90 par groupe
    def calc_quantiles(grp):
        return pd.Series({
            "p10": grp["prevalence"].quantile(0.1),
            "p90": grp["prevalence"].quantile(0.9),
        })
    
    if len(group_cols) == 0:
        p10 = prev_dept["prevalence"].quantile(0.1)
        p90 = prev_dept["prevalence"].quantile(0.9)
        return pd.DataFrame({
            "p10": [p10],
            "p90": [p90],
            "ratio_p90_p10": [p90 / p10 if p10 > 0 else np.nan]
        })
    
    result = prev_dept.groupby(group_cols).apply(calc_quantiles, include_groups=False).reset_index()
    result["ratio_p90_p10"] = result["p90"] / result["p10"]
    
    return result
