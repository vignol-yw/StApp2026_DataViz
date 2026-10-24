from __future__ import annotations

from typing import Iterable

import pandas as pd


def normalize_dept_code(code) -> str | None:
    """Normalise un code departement au format INSEE (01, 2A, 2B, 971, etc.)."""
    if pd.isna(code):
        return None
    value = str(code).strip()
    if value == "" or value.lower() == "nan":
        return None
    if value in {"2A", "2B"}:
        return value
    if value.isdigit():
        if len(value) == 1:
            return f"0{value}"
        return value
    if len(value) == 3 and value.startswith("0"):
        return value
    return value.upper()


def normalize_region_code(code) -> str | None:
    """Normalise un code region."""
    if pd.isna(code):
        return None
    value = str(code).strip()
    if value == "":
        return None
    if value.isdigit():
        return value.zfill(2)
    return value


def remove_total_lines(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les lignes de total et les lignes fictives (tous sexes, tous ages, France)."""
    out = df.copy()
    out = out[out["dept"].map(normalize_dept_code).ne("999")] if "dept" in out.columns else out
    out = out[out["sexe"].ne("9")] if "sexe" in out.columns else out
    out = out[out["classe_age"].ne("tsage")] if "classe_age" in out.columns else out
    return out


def coerce_numeric(series: pd.Series) -> pd.Series:
    """Convertit une serie en numerique en traitant les donnees manquantes."""
    s = series.copy()
    s = s.replace({"": pd.NA, "NS": pd.NA, "na": pd.NA, "NaN": pd.NA})
    return pd.to_numeric(s, errors="coerce")
