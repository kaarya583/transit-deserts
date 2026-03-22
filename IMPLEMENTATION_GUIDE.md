# Implementation Guide: Transit Corridor Optimization

This document provides clear instructions for implementing each phase of the project.

## Phase 0: Project Scoping & Guardrails ✅ COMPLETE

**Status**: Documentation created, folder structure established

**Files Created**:
- `docs/project_scope.md` - Research question, non-goals, assumptions
- `docs/methods_outline.md` - Detailed methodology
- `src/config.py` - All constants and parameters (FROZEN)
- Folder structure established

**Next**: Proceed to Phase 1

---

## Phase 1: Data Ingestion & Baseline

### 1.1 Ingest GTFS (Bus + Rail)

**Module**: `src/ingest/gtfs.py` ✅ CREATED

**Tasks**:
- [ ] Load GTFS feeds from `data_raw/`
- [ ] Extract stops
- [ ] CRS normalization (EPSG:4326)
- [ ] Filter to LA County extent
- [ ] Save as GeoJSON

**Checkpoint**: Can plot stops on map and they look reasonable

**Notebook**: `01_baseline_accessibility.ipynb` (Cell 1.1)

**Output**: `data_processed/stops_all.geojson`

**Sanity Check**:
```python
# After ingestion, verify:
assert len(stops) > 0
assert stops.crs == config.GEOGRAPHIC_CRS
assert 'mode' in stops.columns
# Visual check: stops.plot()
```

### 1.2 Ingest Job Data

**Module**: `src/ingest/jobs.py` (TO CREATE)

**Tasks**:
- [ ] Load LEHD/LODES WAC file
- [ ] Aggregate to census tract
- [ ] Clean missing/zero tracts
- [ ] Merge with tract geometries

**Checkpoint**: Table exists: `tract_id | jobs_total`

**Notebook**: `01_baseline_accessibility.ipynb` (Cell 1.2)

**Output**: `data_processed/jobs_by_tract.geojson`

**Sanity Check**:
```python
# Verify:
assert jobs['jobs_total'].sum() > 0
assert jobs['jobs_total'].min() >= 0
assert len(jobs) == len(tracts)  # or close
# Histogram: jobs['jobs_total'].hist()
```

### 1.3 Ingest Population & Need Indicators

**Module**: `src/ingest/demographics.py` (TO CREATE)

**Tasks**:
- [ ] Load Census ACS data
- [ ] Extract: population, income, car ownership
- [ ] Create weight vector w_i
- [ ] Normalize weights

**Checkpoint**: Histogram of weights, sanity check extremes

**Notebook**: `01_baseline_accessibility.ipynb` (Cell 1.3)

**Output**: `data_processed/tracts_with_demographics.geojson`

**Sanity Check**:
```python
# Verify:
assert 'pop_total' in tracts.columns
assert 'median_income' in tracts.columns
assert 'weight' in tracts.columns
assert tracts['weight'].sum() > 0
# Histogram: tracts['weight'].hist()
```

---

## Phase 2: Baseline Accessibility (Descriptive)

### 2.1 Define Accessibility Metric (FROZEN)

**Documentation**: Already in `docs/methods_outline.md`

**Formula**: 
\[
A_i = \sum_j J_j \cdot \mathbf{1}(T_{ij} \leq \tau)
\]

**Parameters**:
- τ = 30 minutes (from `config.TIME_THRESHOLD`)
- Binary cutoff (no decay)

**Notebook**: `01_baseline_accessibility.ipynb` (Cell 2.1 - markdown only)

**Action**: Document the formula, do NOT change it later

### 2.2 Compute Baseline Accessibility

**Module**: `src/accessibility/compute.py` (TO CREATE)

**Tasks**:
- [ ] Load travel time matrix (or compute if needed)
- [ ] For each tract i:
  - Count jobs j where T_ij <= τ
  - Compute A_i
- [ ] Normalize by population: A_i / P_i × 1000
- [ ] Save results

**Checkpoint**: 
- Choropleth map of accessibility
- Distribution plot
- Summary statistics

**Notebook**: `01_baseline_accessibility.ipynb` (Cell 2.2)

**Output**: `data_processed/baseline_accessibility.geojson`

**Sanity Check**:
```python
# Verify:
assert accessibility['access_30min_per1k'].min() >= 0
assert accessibility['access_30min_per1k'].max() < 1e6  # reasonable upper bound
# Map: accessibility.plot(column='access_30min_per1k', legend=True)
# Histogram: accessibility['access_30min_per1k'].hist(bins=50)
```

### 2.3 Identify Transit Deserts (Optional)

**Tasks**:
- [ ] Define threshold (bottom 20% from config)
- [ ] Label tracts as desert/non-desert
- [ ] Create map

**Checkpoint**: Map with deserts highlighted

**Notebook**: `01_baseline_accessibility.ipynb` (Cell 2.3)

**Output**: `outputs/figures/baseline_accessibility_map.png`

---

## Phase 3: Candidate Corridor Generation

### 3.1 Define What a "Corridor" Is

**Module**: `src/corridors/corridor.py` (TO CREATE)

**Class Definition**:
```python
class Corridor:
    geometry: LineString  # polyline
    stop_spacing: float  # meters
    speed: float  # km/h
    headway: float  # minutes (for docs)
    corridor_id: str
```

**Notebook**: `02_candidate_corridors.ipynb` (Cell 3.1)

**Action**: Create Corridor class, document structure

### 3.2 Generate Candidate Corridors

**Module**: `src/corridors/generate.py` (TO CREATE)

**Strategies**:
1. Desert → job center (connect transit deserts to high-job areas)
2. High-pop → high-job (connect dense residential to employment)
3. Existing arterial alignment (follow major roads)

**Tasks**:
- [ ] Generate 20-50 candidate corridors
- [ ] Create Corridor objects
- [ ] Save as GeoDataFrame

**Checkpoint**: Map showing all candidates

**Notebook**: `02_candidate_corridors.ipynb` (Cell 3.2)

**Output**: `data_processed/candidate_corridors.geojson`

**Sanity Check**:
```python
# Verify:
assert len(corridors) >= config.MIN_CANDIDATE_CORRIDORS
assert len(corridors) <= config.MAX_CANDIDATE_CORRIDORS
assert all(corridors['geometry'].type == 'LineString')
# Map: corridors.plot(color='red', linewidth=2)
```

---

## Phase 4: Counterfactual Accessibility

### 4.1 Synthetic Network Augmentation

**Module**: `src/accessibility/counterfactual.py` (TO CREATE)

**Tasks**:
- [ ] For each corridor:
  - Generate synthetic stops along polyline
  - Connect stops to walking network
  - Update travel time matrix
- [ ] Keep baseline intact (don't modify original network)

**Checkpoint**: One corridor works end-to-end

**Notebook**: `03_counterfactual_accessibility.ipynb` (Cell 4.1)

**Output**: Updated travel time matrices (one per corridor, or combined)

**Sanity Check**:
```python
# Verify synthetic stops:
assert len(synthetic_stops) > 0
assert synthetic_stops.crs == config.ANALYSIS_CRS
# Visual: plot corridor + synthetic stops
```

### 4.2 Compute Δ Accessibility

**Module**: `src/accessibility/counterfactual.py` (extend)

**Tasks**:
- [ ] For each corridor ℓ:
  - Compute counterfactual accessibility A_i^cf(ℓ)
  - Compute gain: ΔA_i(ℓ) = A_i^cf(ℓ) - A_i^baseline
- [ ] Store in matrix: tract_id × corridor_id

**Checkpoint**: Table exists, no negative surprises (or explainable)

**Notebook**: `03_counterfactual_accessibility.ipynb` (Cell 4.2)

**Output**: `data_processed/counterfactual_accessibility_gains.parquet`

**Sanity Check**:
```python
# Verify:
assert gains.shape[0] == len(tracts)
assert gains.shape[1] == len(corridors)
assert gains.min().min() >= -1000  # small negative OK (routing changes)
# Distribution: gains.values.flatten().hist()
```

---

## Phase 5: Optimization (CORE CONTRIBUTION)

### 5.1 Define Objective Function

**Formula**:
\[
\text{Score}(\ell) = \sum_i w_i \cdot \Delta A_i(\ell)
\]

**Module**: `src/optimization/objective.py` (TO CREATE)

**Tasks**:
- [ ] Implement score calculation
- [ ] Handle different weight definitions
- [ ] No ML, no tuning, transparent

**Notebook**: `04_optimization_results.ipynb` (Cell 5.1)

**Action**: Document formula, implement function

### 5.2 Rank Corridors

**Module**: `src/optimization/rank.py` (TO CREATE)

**Tasks**:
- [ ] Compute scores for all corridors
- [ ] Rank top-k
- [ ] Compare weighted vs unweighted
- [ ] Create visualizations

**Checkpoint**: 
- Table + bar plot
- Map of top 3 corridors

**Notebook**: `04_optimization_results.ipynb` (Cell 5.2)

**Output**: 
- `outputs/tables/corridor_rankings.csv`
- `outputs/figures/top_corridors_map.png`

**Sanity Check**:
```python
# Verify:
assert len(rankings) == len(corridors)
assert rankings['score'].is_monotonic_decreasing  # or close
# Bar plot: rankings.head(10).plot.barh(x='corridor_id', y='score')
```

---

## Phase 6: Upper-Bound Demand Estimation

### 6.1 Define Demand Proxy

**Formula**:
\[
D_i(\ell) = P_i \cdot \frac{\Delta A_i(\ell)}{A_i^{baseline} + \epsilon}
\]

**Module**: `src/demand/estimate.py` (TO CREATE)

**Tasks**:
- [ ] Implement demand calculation
- [ ] Label as upper bound explicitly
- [ ] Document limitations

**Notebook**: `05_demand_analysis.ipynb` (Cell 6.1)

**Action**: Document formula, implement function

### 6.2 Aggregate Demand

**Module**: `src/demand/estimate.py` (extend)

**Tasks**:
- [ ] Aggregate: D(ℓ) = Σ D_i(ℓ)
- [ ] Rank by demand
- [ ] Compare vs accessibility ranking

**Checkpoint**: Ranking by demand, comparison table

**Notebook**: `05_demand_analysis.ipynb` (Cell 6.2)

**Output**: `outputs/tables/demand_estimates.csv`

**Sanity Check**:
```python
# Verify:
assert demand['demand'].min() >= 0
assert demand['demand'].max() < 1e6  # reasonable upper bound
# Compare rankings: demand vs accessibility
```

---

## Phase 7: Equity & Sensitivity Analysis

### 7.1 Distributional Effects

**Tasks**:
- [ ] Gains by income decile
- [ ] Gains by desert vs non-desert
- [ ] Lorenz-style plots or boxplots

**Checkpoint**: Visualizations show distribution

**Notebook**: `05_demand_analysis.ipynb` (Cell 7.1)

**Output**: `outputs/figures/equity_analysis.png`

### 7.2 Sensitivity Analysis

**Parameters to Vary**:
- τ: 30 vs 45 minutes
- Stop spacing: 200m vs 400m vs 800m
- Weight definition: different need indicators

**Tasks**:
- [ ] Re-run optimization with different parameters
- [ ] Check ranking stability
- [ ] Document sensitivity

**Checkpoint**: Rankings stable? Scores vary?

**Notebook**: `05_demand_analysis.ipynb` (Cell 7.2)

**Output**: `outputs/tables/sensitivity_analysis.csv`

---

## Phase 8: Research Presentation Layer

### 8.1 Methods Outline

**Status**: ✅ Already created in `docs/methods_outline.md`

**Action**: Review and update if needed

### 8.2 Figures (Minimal, High Quality)

**Required Figures**:
1. Baseline accessibility map ✅ (Phase 2)
2. Candidate corridors map ✅ (Phase 3)
3. Top corridors map ✅ (Phase 5)
4. Accessibility gain distribution ✅ (Phase 4)
5. Demand ranking ✅ (Phase 6)

**Action**: Ensure all figures are publication-quality

---

## Implementation Order

**Sequential Execution**:
1. Phase 0 ✅ (Complete)
2. Phase 1 → Notebook 01
3. Phase 2 → Notebook 01 (continued)
4. Phase 3 → Notebook 02
5. Phase 4 → Notebook 03
6. Phase 5 → Notebook 04
7. Phase 6 → Notebook 05
8. Phase 7 → Notebook 05 (continued)
9. Phase 8 → Review all outputs

**Do NOT skip ahead**. Each phase builds on previous.

---

## Testing Strategy

**After Each Phase**:
1. Run sanity checks (see above)
2. Verify outputs exist
3. Check visualizations look reasonable
4. Document any issues

**Before Moving to Next Phase**:
- All checkpoints passed
- Outputs saved
- No obvious errors

---

## Common Pitfalls to Avoid

1. **Don't change assumptions mid-stream** - They're frozen in config.py
2. **Don't skip checkpoints** - They catch errors early
3. **Don't optimize prematurely** - Follow the plan exactly
4. **Don't add features** - Stick to the scope
5. **Don't forget visualizations** - They're sanity checks

---

## Next Steps

**Immediate**: Implement Phase 1.1 (GTFS ingestion)

**Instruction for Cursor**: 
> "Implement Phase 1.1 exactly as written in IMPLEMENTATION_GUIDE.md. Create the notebook cell and use the gtfs.py module. Include sanity checks."

