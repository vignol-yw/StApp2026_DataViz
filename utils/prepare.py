import sys
from pathlib import Path

import duckdb

from .constants import (
    AGE_TOUS,
    ANNEE_REFERENCE,
    CSV_PATH,
    DEPT_FRANCE,
    DEPTS_METRO,
    DEPTS_OUTREMER,
    PROCESSED_DIR,
    SEXE_TOUS,
)


def _as_sql_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def prepare_data(force: bool = False) -> dict[str, Path]:
    """Lit le CSV source, nettoie les donnees et exporte les Parquet utiles."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_files = {
        "main": PROCESSED_DIR / "pathologies.parquet",
        "ref_age_sexe": PROCESSED_DIR / "ref_age_sexe.parquet",
        "national_rates": PROCESSED_DIR / "national_rates.parquet",
    }

    if not force and all(path.exists() for path in output_files.values()):
        print("OK: fichiers Parquet deja presents. Utilisez --force pour recalculer.")
        return output_files

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Fichier source introuvable: {CSV_PATH}\n"
            "Placez le CSV dans data/amelie_pathology.csv avant de lancer la preparation."
        )

    csv_sql = _as_sql_path(CSV_PATH)
    print(f"Lecture du CSV source: {CSV_PATH}")
    print("Preparation des donnees...")

    con = duckdb.connect()

    con.execute(
        f"""
        CREATE VIEW raw_data AS
        SELECT
            CAST(annee AS INTEGER) AS annee,
            patho_niv1,
            patho_niv2,
            patho_niv3,
            top,
            cla_age_5 AS classe_age,
            sexe,
            region,
            dept,
            CASE
                WHEN Ntop IS NULL OR TRIM(Ntop) = '' THEN NULL
                ELSE CAST(Ntop AS INTEGER)
            END AS ntop,
            CASE
                WHEN Npop IS NULL OR TRIM(Npop) = '' THEN NULL
                ELSE CAST(Npop AS INTEGER)
            END AS npop,
            CASE
                WHEN prev IS NULL OR TRIM(prev) = '' THEN NULL
                ELSE CAST(REPLACE(prev, ',', '.') AS DOUBLE)
            END AS prev,
            "Niveau prioritaire" AS niveau_prioritaire,
            libelle_classe_age,
            libelle_sexe
        FROM read_csv(
            '{csv_sql}',
            delim=';',
            header=true,
            ignore_errors=true,
            encoding='utf-8',
            all_varchar=true,
            null_padding=true
        )
        """
    )

    # 1) Donnees principales nettoyees : pas de lignes de total, pas de departement fictif 999
    main_path = _as_sql_path(output_files["main"])
    con.execute(
        f"""
        COPY (
            SELECT
                annee,
                patho_niv1,
                patho_niv2,
                patho_niv3,
                classe_age,
                sexe,
                region,
                dept,
                ntop,
                npop
            FROM raw_data
            WHERE sexe <> '{SEXE_TOUS}'
              AND classe_age <> '{AGE_TOUS}'
              AND dept <> '{DEPT_FRANCE}'
              AND dept IS NOT NULL
              AND patho_niv1 NOT IN (
                  'Total consommants tous regimes',
                  'Total consommants tous régimes',
                  'Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire'
              )
        ) TO '{main_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    # 2) Population de reference par age et sexe (France entiere, annee de reference)
    ref_path = _as_sql_path(output_files["ref_age_sexe"])
    con.execute(
        f"""
        COPY (
            SELECT
                classe_age,
                sexe,
                SUM(npop) AS pop_ref
            FROM raw_data
            WHERE annee = {ANNEE_REFERENCE}
              AND sexe <> '{SEXE_TOUS}'
              AND classe_age <> '{AGE_TOUS}'
              AND dept <> '{DEPT_FRANCE}'
              AND npop IS NOT NULL
            GROUP BY classe_age, sexe
            ORDER BY classe_age, sexe
        ) TO '{ref_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    # 3) Taux nationaux par case pour la standardisation indirecte
    national_path = _as_sql_path(output_files["national_rates"])
    con.execute(
        f"""
        COPY (
            SELECT
                annee,
                patho_niv1,
                patho_niv2,
                patho_niv3,
                classe_age,
                sexe,
                SUM(ntop) AS ntop_national,
                SUM(npop) AS npop_national,
                CASE
                    WHEN SUM(npop) > 0 THEN CAST(SUM(ntop) AS DOUBLE) / SUM(npop)
                    ELSE NULL
                END AS taux_national
            FROM raw_data
            WHERE sexe <> '{SEXE_TOUS}'
              AND classe_age <> '{AGE_TOUS}'
              AND dept <> '{DEPT_FRANCE}'
              AND npop IS NOT NULL
              AND patho_niv1 NOT IN (
                  'Total consommants tous regimes',
                  'Total consommants tous régimes',
                  'Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire'
              )
            GROUP BY annee, patho_niv1, patho_niv2, patho_niv3, classe_age, sexe
            ORDER BY annee, patho_niv1, classe_age, sexe
        ) TO '{national_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )

    con.close()

    for name, path in output_files.items():
        if path.exists():
            row_count = duckdb.connect().execute(f"SELECT COUNT(*) FROM read_parquet('{_as_sql_path(path)}')").fetchone()[0]
            print(f"OK: {name} -> {path.name} ({row_count:,} lignes)")
        else:
            print(f"ERROR: {name} not created: {path}")

    return output_files


def check_data_ready() -> bool:
    """Vérifie si les Parquet requis existent."""
    required = [
        PROCESSED_DIR / "pathologies.parquet",
        PROCESSED_DIR / "ref_age_sexe.parquet",
        PROCESSED_DIR / "national_rates.parquet",
    ]
    return all(path.exists() for path in required)


if __name__ == "__main__":
    force = "--force" in sys.argv
    try:
        prepare_data(force=force)
        print("\nOK: preparation terminee.")
    except Exception as exc:  # pragma: no cover
        print(f"\nERROR: {exc}")
        raise SystemExit(1)
