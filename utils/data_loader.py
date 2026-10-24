import pandas as pd
from pathlib import Path
from typing import Optional

from .constants import PROCESSED_DIR, GEOJSON_PATH, DEPT_NAMES, REGION_NAMES, DEPT_TO_REGION


def load_pathologies() -> pd.DataFrame:
    """Charge les données principales des pathologies."""
    path = PROCESSED_DIR / "pathologies.parquet"
    if not path.exists():
        raise FileNotFoundError(
            "Les données préparées sont manquantes.\n"
            "Exécutez : python -m utils.prepare"
        )
    return pd.read_parquet(path)


def load_ref_age_sexe() -> pd.DataFrame:
    """Charge la structure de référence âge × sexe."""
    path = PROCESSED_DIR / "ref_age_sexe.parquet"
    if not path.exists():
        raise FileNotFoundError(
            "Les données préparées sont manquantes.\n"
            "Exécutez : python -m utils.prepare"
        )
    return pd.read_parquet(path)


def load_national_rates() -> pd.DataFrame:
    """Charge les taux nationaux par case."""
    path = PROCESSED_DIR / "national_rates.parquet"
    if not path.exists():
        raise FileNotFoundError(
            "Les données préparées sont manquantes.\n"
            "Exécutez : python -m utils.prepare"
        )
    return pd.read_parquet(path)


def load_geojson() -> dict:
    """Charge le GeoJSON des départements."""
    import json
    if not GEOJSON_PATH.exists():
        raise FileNotFoundError(
            f"GeoJSON manquant : {GEOJSON_PATH}\n"
            "Téléchargez-le depuis github.com/gregoiredavid/france-geojson"
        )
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_dept_name(code: str) -> str:
    """Retourne le nom d'un département."""
    return DEPT_NAMES.get(code, code)


def get_region_name(code: str) -> str:
    """Retourne le nom d'une région."""
    return REGION_NAMES.get(code, code)


def get_region_for_dept(dept_code: str) -> Optional[str]:
    """Retourne le code région pour un département."""
    return DEPT_TO_REGION.get(dept_code)


def get_available_years(df: pd.DataFrame) -> list[int]:
    """Retourne les années disponibles triées."""
    return sorted(df["annee"].unique())


def get_pathologies_niv1(df: pd.DataFrame) -> list[str]:
    """Retourne les pathologies de niveau 1."""
    return sorted(df["patho_niv1"].dropna().unique())


def get_pathologies_niv2(df: pd.DataFrame, patho_niv1: Optional[str] = None) -> list[str]:
    """Retourne les pathologies de niveau 2, éventuellement filtrées."""
    if patho_niv1:
        subset = df[df["patho_niv1"] == patho_niv1]
    else:
        subset = df
    return sorted(subset["patho_niv2"].dropna().unique())


def get_departments(df: pd.DataFrame) -> list[str]:
    """Retourne les codes département."""
    return sorted(df["dept"].unique())
