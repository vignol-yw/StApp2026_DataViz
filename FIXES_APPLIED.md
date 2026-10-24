# Fixes Applied to Cardiovascular Dashboard

## Date: 2024-10-24

## Issue Summary
The application was failing when navigating to the "Territory Analysis" page with the following error:
```
AttributeError: module 'plotly.graph_objects' has no attribute 'Choroplethmapbox'
```

## Root Cause
Plotly 7.x changed the API for choropleth maps:
- **Removed**: `go.Choroplethmapbox` (doesn't exist in Plotly 7.1.0)
- **Available alternatives**:
  - `px.choropleth_map()` - High-level plotly.express function
  - `go.Choroplethmap()` - Low-level graph_objects for subplots

## Changes Made

### 1. Fixed `carte_indice_comparatif()` function (line ~369 in utils/plots.py)

**Before:**
```python
fig = go.Figure(go.Choroplethmapbox(...))
```

**After:**
```python
fig = px.choropleth_map(
    df_map,
    geojson=geojson,
    locations="dept",
    color="indice_norm",
    map_style="carto-positron",  # Note: changed from mapbox_style to map_style
    ...
)
```

**Key parameter changes:**
- `go.Choroplethmapbox` → `px.choropleth_map`
- `mapbox_style` → `map_style`
- `colorscale` → `color_continuous_scale`
- `z` → `color`
- Layout uses `coloraxis_colorbar` instead of individual trace colorbar

### 2. Fixed `trois_cartes_cote_a_cote()` function (line ~716 in utils/plots.py)

**Before:**
```python
specs=[[{"type": "choroplethmapbox"}] * 3]
...
fig.add_trace(go.Choroplethmapbox(...))
...
fig.update_layout(
    mapbox=dict(style=..., center=..., zoom=...),
    mapbox2=dict(...),
    mapbox3=dict(...),
)
```

**After:**
```python
specs=[[{"type": "choroplethmap"}] * 3]
...
fig.add_trace(go.Choroplethmap(...))
...
fig.update_layout(
    map=dict(style=..., center=..., zoom=...),
    map2=dict(...),
    map3=dict(...),
)
```

**Key parameter changes:**
- Subplot spec type: `"choroplethmapbox"` → `"choroplethmap"`
- Trace type: `go.Choroplethmapbox` → `go.Choroplethmap`
- Layout: `mapbox`/`mapbox2`/`mapbox3` → `map`/`map2`/`map3`

### 3. Translation Updates
Both functions also received English translations:
- Docstrings translated to English
- Chart titles and annotations translated
- Hover text labels translated

## Testing Performed

✓ **Test 1**: Direct function test of `carte_indice_comparatif()`
```
[OK] Map created: Comparative Index by Department: Maladies cardioneurovasculaires (2024)
```

✓ **Test 2**: Direct function test of `trois_cartes_cote_a_cote()`
```
[OK] Map created: Territorial Comparison of Cardiovascular Sub-pathologies (2024)
```

✓ **Test 3**: All pages import without errors
```
[OK] pages.01_poids
[OK] pages.02_age
[OK] pages.03_sexe
[OK] pages.04_territoire  ← Previously failing, now works
[OK] pages.05_evolution
[OK] pages.06_acp
[OK] pages.07_conclusion
[OK] pages.08_sources
```

✓ **Test 4**: Streamlit app runs successfully on http://localhost:8501
```
HTTP Status: 200
App is running and accessible!
```

## Migration Guide for Plotly 7.x

If you encounter similar issues with other Plotly code:

### For single maps (full figure):
```python
# Old (Plotly 4.x/5.x)
import plotly.graph_objects as go
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson,
    mapbox_style="carto-positron",
    ...
))

# New (Plotly 7.x)
import plotly.express as px
fig = px.choropleth_map(
    df,
    geojson=geojson,
    map_style="carto-positron",  # renamed parameter
    ...
)
```

### For subplots/multiple maps:
```python
# Old
from plotly.subplots import make_subplots
fig = make_subplots(specs=[[{"type": "choroplethmapbox"}]])
fig.add_trace(go.Choroplethmapbox(...))
fig.update_layout(mapbox=dict(...))

# New
from plotly.subplots import make_subplots
fig = make_subplots(specs=[[{"type": "choroplethmap"}]])
fig.add_trace(go.Choroplethmap(...))
fig.update_layout(map=dict(...))
```

## Files Modified
- `utils/plots.py` - Fixed two map visualization functions

## Status
✅ **RESOLVED** - All issues fixed, app fully functional in English
