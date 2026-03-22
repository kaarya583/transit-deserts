# Core Project Structure

## Research Question

**"Which census tracts in LA County experience systematically low job accessibility via public transit, after controlling for population and income, and what structural factors best explain this?"**

## Core Notebooks (Run Sequentially)

### Stage 1: Data & Network Construction
1. **`00_setup.ipynb`** - Environment verification and folder setup
2. **`01_data_ingestion.ipynb`** - Load GTFS, Census, LEHD, OSM data
3. **`02_network_and_travel_times.ipynb`** - Build multimodal network, compute travel times

### Stage 2: Accessibility Measurement
4. **`03_accessibility.ipynb`** - Calculate accessibility metrics, identify transit deserts

### Stage 3: Spatial Structure Analysis (CORE)
5. **`04_spatial_analysis.ipynb`** - Global/Local Moran's I, LISA clusters, spatial regression

### Stage 4: Structural Factor Analysis
6. **`05_ml_analysis.ipynb`** - Random Forest feature importance (diagnostic tool)

### Stage 5: Synthesis
7. **`09_research_summary.ipynb`** - Synthesize findings, display required figures

## Required Outputs

Each notebook produces outputs saved to `outputs/`:

- **Notebook 01**: `la_tracts_with_acs_jobs.geojson`, `metro_stops_all.geojson`
- **Notebook 02**: `travel_times_sample.parquet`, `origins_tract_centroids.geojson`
- **Notebook 03**: `accessibility_metrics.csv`, `tracts_with_accessibility.geojson`, `map_transit_deserts.png`
- **Notebook 04**: `spatial_autocorrelation_results.csv`, `spatial_regression_results.csv`, `map_lisa_clusters.png`
- **Notebook 05**: `ml_feature_importance.csv`, `ml_feature_importance.png`
- **Notebook 09**: `accessibility_distribution.png` (if not already created)

## Required Figures (5 Total)

1. Map of transit deserts (`map_transit_deserts.png` - Notebook 03)
2. Map of LISA Low-Low clusters (`map_lisa_clusters.png` - Notebook 04)
3. Accessibility distribution histogram (`accessibility_distribution.png` - Notebook 09)
4. Spatial regression coefficient table (`spatial_regression_results.csv` - Notebook 04)
5. ML feature importance bar chart (`ml_feature_importance.png` - Notebook 05)

## Verification Checklist

Before considering the project complete, verify:

- [ ] All 7 core notebooks run without errors
- [ ] All required outputs are generated
- [ ] All 5 required figures are created
- [ ] Research summary notebook synthesizes findings correctly
- [ ] README accurately describes the project

## Archived Notebooks

Non-core notebooks have been moved to `notebooks/archive/`:
- Advanced ML with ensembles/clustering/PCA
- Intervention simulations
- Additional visualizations
- Extensive EDA

These can be referenced but are not part of the core research pipeline.

