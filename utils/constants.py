from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
CSV_PATH = DATA_DIR / "amelie_pathology.csv"
GEOJSON_PATH = DATA_DIR / "departements.geojson"

# Année de référence pour la standardisation
ANNEE_REFERENCE = 2024

# Codes spéciaux à exclure des agrégations
SEXE_TOUS = "9"
AGE_TOUS = "tsage"
DEPT_FRANCE = "999"
REGION_FRANCE = "99"

# Départements métropolitains (pour filtrage)
DEPTS_METRO = [
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "21",
    "22", "23", "24", "25", "26", "27", "28", "29", "2A", "2B",
    "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
    "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
    "60", "61", "62", "63", "64", "65", "66", "67", "68", "69",
    "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
    "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
    "90", "91", "92", "93", "94", "95"
]

# Départements d'outre-mer
DEPTS_OUTREMER = ["971", "972", "973", "974", "976"]

# Référentiel département → région (régions actuelles 2016)
DEPT_TO_REGION = {
    # Auvergne-Rhône-Alpes (84)
    "01": "84", "03": "84", "07": "84", "15": "84", "26": "84",
    "38": "84", "42": "84", "43": "84", "63": "84", "69": "84",
    "73": "84", "74": "84",
    # Bourgogne-Franche-Comté (27)
    "21": "27", "25": "27", "39": "27", "58": "27", "70": "27",
    "71": "27", "89": "27", "90": "27",
    # Bretagne (53)
    "22": "53", "29": "53", "35": "53", "56": "53",
    # Centre-Val de Loire (24)
    "18": "24", "28": "24", "36": "24", "37": "24", "41": "24", "45": "24",
    # Corse (94)
    "2A": "94", "2B": "94",
    # Grand Est (44)
    "08": "44", "10": "44", "51": "44", "52": "44", "54": "44",
    "55": "44", "57": "44", "67": "44", "68": "44", "88": "44",
    # Hauts-de-France (32)
    "02": "32", "59": "32", "60": "32", "62": "32", "80": "32",
    # Île-de-France (11)
    "75": "11", "77": "11", "78": "11", "91": "11", "92": "11",
    "93": "11", "94": "11", "95": "11",
    # Normandie (28)
    "14": "28", "27": "28", "50": "28", "61": "28", "76": "28",
    # Nouvelle-Aquitaine (75)
    "16": "75", "17": "75", "19": "75", "23": "75", "24": "75",
    "33": "75", "40": "75", "47": "75", "64": "75", "79": "75",
    "86": "75", "87": "75",
    # Occitanie (76)
    "09": "76", "11": "76", "12": "76", "30": "76", "31": "76",
    "32": "76", "34": "76", "46": "76", "48": "76", "65": "76",
    "66": "76", "81": "76", "82": "76",
    # Pays de la Loire (52)
    "44": "52", "49": "52", "53": "52", "72": "52", "85": "52",
    # Provence-Alpes-Côte d'Azur (93)
    "04": "93", "05": "93", "06": "93", "13": "93", "83": "93", "84": "93",
    # Outre-mer
    "971": "01",  # Guadeloupe
    "972": "02",  # Martinique
    "973": "03",  # Guyane
    "974": "04",  # La Réunion
    "976": "06",  # Mayotte
}

# Noms des régions
REGION_NAMES = {
    "01": "Guadeloupe",
    "02": "Martinique",
    "03": "Guyane",
    "04": "La Réunion",
    "06": "Mayotte",
    "11": "Île-de-France",
    "24": "Centre-Val de Loire",
    "27": "Bourgogne-Franche-Comté",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d'Azur",
    "94": "Corse",
}

# Noms des départements
DEPT_NAMES = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes", "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes",
    "09": "Ariège", "10": "Aube", "11": "Aude", "12": "Aveyron",
    "13": "Bouches-du-Rhône", "14": "Calvados", "15": "Cantal", "16": "Charente",
    "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "21": "Côte-d'Or",
    "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne", "25": "Doubs",
    "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "2A": "Corse-du-Sud", "2B": "Haute-Corse", "30": "Gard", "31": "Haute-Garonne",
    "32": "Gers", "33": "Gironde", "34": "Hérault", "35": "Ille-et-Vilaine",
    "36": "Indre", "37": "Indre-et-Loire", "38": "Isère", "39": "Jura",
    "40": "Landes", "41": "Loir-et-Cher", "42": "Loire", "43": "Haute-Loire",
    "44": "Loire-Atlantique", "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne",
    "48": "Lozère", "49": "Maine-et-Loire", "50": "Manche", "51": "Marne",
    "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle", "55": "Meuse",
    "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord",
    "60": "Oise", "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques", "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales",
    "67": "Bas-Rhin", "68": "Haut-Rhin", "69": "Rhône", "70": "Haute-Saône",
    "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie",
    "75": "Paris", "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines",
    "79": "Deux-Sèvres", "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne",
    "83": "Var", "84": "Vaucluse", "85": "Vendée", "86": "Vienne",
    "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne", "90": "Territoire de Belfort",
    "91": "Essonne", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne", "95": "Val-d'Oise",
    "971": "Guadeloupe", "972": "Martinique", "973": "Guyane",
    "974": "La Réunion", "976": "Mayotte",
}

# Pathologies cardio-neuro-vasculaires (niveau 1)
PATHO_CARDIO = "Maladies cardioneurovasculaires"

# Catégories de traitement (pas des maladies)
CATEGORIES_TRAITEMENT = [
    "Traitements du risque vasculaire (hors pathologies)",
    "Traitements psychotropes (hors pathologies)",
    "Traitements antalgiques ou anti-inflammatoires (hors pathologies, traitements, maternité ou hospitalisations)",
]

# Catégories spéciales (à exclure des analyses de pathologies)
CATEGORIES_SPECIALES = [
    "Total consommants tous régimes",
    "Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire",
]

# Ordre des classes d'âge pour tri
ORDRE_AGE = [
    "00-04", "05-09", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79",
    "80-84", "85-89", "90-94", "95et+"
]
