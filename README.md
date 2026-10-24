# Diseases Dashboard - France

An interactive data visualization dashboard exploring cardiovascular diseases in France from 2015 to 2024, built with **Streamlit** and **Plotly**.

> **Data Source**: National Health Insurance (Cnam) - *Pathologies dataset*  
> **Live Demo**:  or http://localhost:8501 (when running locally) 
> **Github link**: 

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Dashboard Pages](#dashboard-pages)
- [Technical Stack](#technical-stack)
- [Data Methodology](#data-methodology)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

This dashboard tells the story of cardiovascular diseases in France through interactive visualizations, combining:

- **Disease Burden**: Understanding the weight of different pathologies
- **Demographics**: Age and sex distribution patterns
- **Geographic Analysis**: Territorial differences across French departments
- **Temporal Trends**: Evolution from 2015 to 2024
- **Multivariate Analysis**: PCA to identify patterns and correlations

The project transforms raw healthcare data into actionable insights through clean, honest, and well-documented visualizations.

---

## Features

- **Interactive Filters**: Filter data by year, pathology, department, age group, and sex
- **8 Comprehensive Pages**: From disease burden to PCA analysis
- **Geographic Maps**: Choropleth maps showing regional variations
- **Responsive Charts**: Bar charts, treemaps, pyramids, scatter plots, and more
- **English Interface**: Fully translated from French for international accessibility
- **Optimized Performance**: Uses Parquet files and DuckDB for fast data processing

---

## Project Structure

```
final_project/
├── app.py                      # Main entry point & navigation
├── data/
│   ├── amelie_pathology.csv    # Raw data (source)
│   ├── departements.geojson    # Geographic boundaries
│   └── processed/              # Generated Parquet files
│       ├── pathologies.parquet
│       ├── national_rates.parquet
│       └── ref_age_sexe.parquet
├── pages/                      # Dashboard sections
│   ├── 01_poids.py            # Disease burden
│   ├── 02_age.py              # Age analysis
│   ├── 03_sexe.py             # Sex analysis
│   ├── 04_territoire.py       # Geographic analysis
│   ├── 05_evolution.py        # Temporal trends
│   ├── 06_acp.py              # PCA analysis
│   ├── 07_conclusion.py       # Summary comparison
│   └── 08_sources.py          # Data sources & methodology
├── utils/
│   ├── constants.py           # Department codes, pathology lists
│   ├── data_loader.py         # Data loading functions
│   ├── prepare.py             # Data preprocessing script
│   ├── stats.py               # Statistical calculations
│   └── plots.py               # Visualization functions
├── tests/                     # Automated tests
├── requirements.txt           # Python dependencies
├── FIXES_APPLIED.md          # Plotly 7.x migration notes
└── README.md                 # This file
```

---

## Installation

### Prerequisites

- Python 3.10 or higher (tested on Python 3.14)
- Windows, macOS, or Linux

### Step 1: Clone or Download the Project

```bash
cd "c:\Users\vigno\Documents\cours\S07\data viz\final_project"
```

### Step 2: Create a Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Key dependencies:**
- `streamlit==1.66.1` - Dashboard framework
- `plotly==7.1.0` - Interactive visualizations
- `pandas==3.1.0` - Data manipulation
- `duckdb==1.2.0` - Fast data processing
- `scikit-learn` - PCA analysis

---

## Usage

### 1. Data Preparation

Ensure the raw data file exists:
```
data/amelie_pathology.csv
```
If the file don't exist download using this link https://www.data.gouv.fr/api/1/datasets/r/5f71ba43-afc8-43a0-b306-dafe29940f9c  and place in data folder

Generate the processed Parquet files:
```bash
python -m utils.prepare
```

This creates optimized files in `data/processed/`:
- `pathologies.parquet` (~1.6M rows)
- `national_rates.parquet`
- `ref_age_sexe.parquet`

### 2. Run the Dashboard

```bash
streamlit run app.py
```

The application will open automatically in your browser at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://[your-ip]:8501

### 3. Navigate the Dashboard

Use the sidebar to:
- Select year (2015-2024)
- Choose pathology category
- Filter by department, age group, or sex
- Navigate between the 8 analysis pages

---

## Dashboard Pages

| Page | Title | Description |
|------|-------|-------------|
| 01 | **Disease Burden** | Overview of pathology weights and prevalence |
| 02 | **Who is Affected? Age** | Age distribution and risk groups |
| 03 | **Who is Affected? Sex** | Sex-specific patterns and disparities |
| 04 | **Territory Analysis** | Geographic variations across France |
| 05 | **Temporal Evolution** | Trends from 2015 to 2024 |
| 06 | **What Goes Together (PCA)** | Multivariate patterns and correlations |
| 07 | **Summary** | Side-by-side comparison maps |
| 08 | **Sources and Limitations** | Data methodology and notes |

---

## Technical Stack

### Core Technologies
- **Frontend**: Streamlit 1.66.1
- **Visualization**: Plotly 7.1.0 (Express & Graph Objects)
- **Data Processing**: Pandas 3.1.0, DuckDB 1.2.0
- **Statistical Analysis**: NumPy, Scikit-learn
- **Geographic Data**: GeoJSON for French departments

### Key Features
- **Plotly 7.x Compatible**: Updated from deprecated `Choroplethmapbox` to `choropleth_map`
- **Responsive Design**: Charts adapt to container width
- **Color Schemes**: Divergent scales for comparative indices
- **Performance**: Parquet files for 10x faster loading than CSV

---

## Data Methodology

### Data Cleaning
- **Exclusions**: Total aggregation rows (department 999, all ages, all sexes)
- **Missing Values**: NS (Not Specified) values treated as missing data
- **Normalization**: Comparative indices calculated relative to national average

### Statistical Methods
- **Prevalence Rates**: Per 1,000 inhabitants
- **Comparative Index**: Department rate / National rate (1.0 = national average)
- **Age Standardization**: Reference population from 2015-2024 baseline
- **PCA**: Principal Component Analysis on multi-pathology correlations

### Geographic Scope
- **Metropolitan France**: 96 departments
- **Overseas Territories**: 5 departments (DOM)
- **Excluded**: COM (overseas collectivities) due to data limitations

---

## Troubleshooting

### Issue: Plotly AttributeError

**Error:**
```
AttributeError: module 'plotly.graph_objects' has no attribute 'Choroplethmapbox'
```

**Solution:**
This was fixed in the latest version. See [FIXES_APPLIED.md](FIXES_APPLIED.md) for migration details.

### Issue: Missing Parquet Files

**Error:**
```
File not found: data/processed/pathologies.parquet
```

**Solution:**
Run the data preparation script:
```bash
python -m utils.prepare
```

### Issue: Port Already in Use

**Error:**
```
Address already in use
```

**Solution (Windows):**
```powershell
Get-NetTCPConnection -LocalPort 8501 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

Then restart the app.

### Issue: Import Errors

**Solution:**
Ensure virtual environment is activated and dependencies are installed:
```bash
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 🧪 Testing

Run automated tests:
```bash
pytest -q
```

Run with coverage:
```bash
pytest --cov=utils --cov=pages
```

---

## 📝 Recent Updates

### 2024-10-24
- ✅ Fixed Plotly 7.x compatibility (`Choroplethmapbox` → `choropleth_map`)
- ✅ Complete English translation (previously in French)
- ✅ Updated all chart titles and annotations
- ✅ Verified all 8 pages load without errors

See [FIXES_APPLIED.md](FIXES_APPLIED.md) for detailed migration notes.

---

## 📄 License

This project is developed for educational purposes as part of a data visualization course.

**Data Source**: National Health Insurance (Cnam) - Public health data  
**Attribution**: Charts include source attribution as per data usage requirements

---

## 👥 Contributing

This is an academic project. For suggestions or bug reports, please create an issue.

---

## 🙏 Acknowledgments

- **Cnam** for providing comprehensive healthcare data
- **Streamlit** team for the excellent dashboard framework
- **Plotly** for powerful interactive visualizations

---

**Built with ❤️ for better health data understanding**
