# Research Restructure Plan: From Exploratory to Directed Research

## Primary Research Question

**"Which census tracts in LA County experience systematically low job accessibility via public transit, after controlling for population and income, and what structural factors best explain this?"**

This question:
- Uses statistics + spatial modeling
- Makes ML supporting, not dominant
- Directly aligns with policy & planning
- Avoids "ML-for-ML's-sake"

---

## Notebook Reclassification

### Tier 1: CORE PIPELINE (Keep & Polish)
- `00_setup.ipynb` - Environment setup
- `01_data_ingestion.ipynb` - Data loading
- `02_network_and_travel_times.ipynb` - Network construction
- `03_accessibility.ipynb` - Accessibility metrics
- `04_spatial_analysis.ipynb` - Spatial analysis (CORE)

**These form the causal chain**: Infrastructure → Travel times → Accessibility → Spatial inequity

### Tier 2: SUPPORTING ANALYSIS (Trim Aggressively)
- `05_ml_advanced_analysis.ipynb` - Simplify to ONE RF model, feature importance only
- `08_eda_feature_analysis.ipynb` - Keep only correlations/well-vs-poorly comparison

**Demote**: Remove ensembles, clustering, PCA as main results

### Tier 3: EXPLORATORY / APPENDIX ONLY
- Clustering analysis → Appendix figure
- PCA → Appendix figure  
- Multiple ML models → Remove
- Ensemble methods → Remove

---

## Final 4-Stage Structure

### Stage 1: Data & Network Construction
**Notebooks**: `00_setup`, `01_data_ingestion`, `02_network_and_travel_times`

**Outputs**:
- Travel-time matrix
- Stops + walking network
- Clean tract/job data

**Focus**: Engineering skill, clear assumptions

### Stage 2: Accessibility Definition & Measurement  
**Notebook**: `03_accessibility`

**Outputs**:
- Single accessibility score per tract (30-min threshold)
- Binary "transit desert" flag
- Clear definition

**Focus**: Statistical clarity, conceptual contribution

### Stage 3: Spatial Structure & Inequality (CORE)
**Notebook**: `04_spatial_analysis`

**Outputs**:
- Map of Low-Low LISA clusters
- Table of spatial regression coefficients
- Global Moran's I results

**Focus**: This is the research core - lean into it

### Stage 4: Explanation & Policy Interpretation
**Notebook**: Simplified `05_ml_analysis` (rename from `05_ml_advanced_analysis`)

**Outputs**:
- ONE Random Forest model
- Feature importance ranking
- Interpretation of structural drivers

**Focus**: ML supports inference, doesn't replace it

---

## Required Figures (5 Total)

1. **Map of transit deserts** (from Stage 2)
2. **Map of LISA Low-Low clusters** (from Stage 3)
3. **Accessibility distribution histogram** (from Stage 2)
4. **Spatial regression coefficient table** (from Stage 3)
5. **ML feature importance bar chart** (from Stage 4)

All other figures → Appendix or remove

---

## ML Simplification Checklist

### Remove:
- ❌ Ensemble models
- ❌ Multiple boosting frameworks (XGBoost, LightGBM)
- ❌ K-means clustering (move to appendix)
- ❌ PCA as main result (move to appendix)
- ❌ Coordinate features as major drivers (red flag)
- ❌ Hierarchical clustering
- ❌ Elbow method (keep simple)

### Keep:
- ✅ ONE Random Forest model
- ✅ Clean feature set (no log transforms, focused)
- ✅ Feature importance ranking
- ✅ Clear interpretation

### Reframe Language:
- "Machine learning was used as a diagnostic tool to identify non-linear relationships and confirm the relative importance of explanatory variables."
- NOT: "We used ML to predict accessibility"

---

## Next Steps

1. Create simplified `05_ml_analysis.ipynb` (remove ensembles, clustering, PCA)
2. Update `08_eda_feature_analysis.ipynb` (keep only essential comparisons)
3. Create `09_research_summary.ipynb` (synthesizes Stages 1-4)
4. Rewrite README.md (research-lab-oriented)
5. Create appendix notebook for exploratory analyses

