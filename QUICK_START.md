# Quick Start Guide

## ✅ What's Been Set Up

### 1. Project Structure ✅
- New folder structure with `src/` modules
- `data_processed/`, `data_intermediate/`, `outputs/figures/`, `outputs/tables/`
- All folders created and ready

### 2. Documentation ✅
- `docs/project_scope.md` - Research question, assumptions, non-goals
- `docs/methods_outline.md` - Detailed methodology
- `IMPLEMENTATION_GUIDE.md` - Step-by-step instructions
- `PROJECT_RESTRUCTURE_SUMMARY.md` - Status and next steps

### 3. Configuration ✅
- `src/config.py` - All parameters frozen (DO NOT CHANGE)
- Time threshold: 30 minutes
- Corridor parameters: stop spacing, speed, headway
- File paths and output names

### 4. Modules Created ✅
- `src/ingest/gtfs.py` - GTFS data loading (ready to use)

### 5. Notebooks Created ✅
- `00_exploration.ipynb` - Data exploration and sanity checks

---

## 🚀 Next Steps (In Order)

### Step 1: Run Exploration Notebook

```bash
# Open and run:
notebooks/00_exploration.ipynb
```

**What it does**:
- Verifies folder structure
- Checks data availability
- No analysis yet, just validation

**Checkpoint**: All folders exist, data files are present

---

### Step 2: Implement Phase 1.1 - GTFS Ingestion

**Create**: `notebooks/01_baseline_accessibility.ipynb`

**Cell 1.1**: GTFS Ingestion
```python
# Use the module:
from src.ingest import gtfs

# Ingest GTFS
stops = gtfs.ingest_gtfs(save=True)

# Sanity check
assert len(stops) > 0
assert stops.crs == config.GEOGRAPHIC_CRS
stops.plot()  # Visual check
```

**Checkpoint**: Can plot stops on map, they look reasonable

**Output**: `data_processed/stops_all.geojson`

---

### Step 3: Implement Phase 1.2 - Job Data Ingestion

**Create**: `src/ingest/jobs.py`

**Tasks**:
- Load LEHD/LODES WAC file
- Aggregate to census tract
- Merge with tract geometries
- Save as GeoJSON

**Cell 1.2** in Notebook 01:
```python
from src.ingest import jobs

jobs_gdf = jobs.ingest_jobs(save=True)

# Sanity check
assert jobs_gdf['jobs_total'].sum() > 0
jobs_gdf['jobs_total'].hist()  # Visual check
```

**Checkpoint**: Table exists: `tract_id | jobs_total`

**Output**: `data_processed/jobs_by_tract.geojson`

---

### Step 4: Implement Phase 1.3 - Demographics Ingestion

**Create**: `src/ingest/demographics.py`

**Tasks**:
- Load Census ACS data
- Extract: population, income, car ownership
- Create weight vector w_i
- Save as GeoJSON

**Cell 1.3** in Notebook 01:
```python
from src.ingest import demographics

tracts = demographics.ingest_demographics(save=True)

# Sanity check
assert 'weight' in tracts.columns
tracts['weight'].hist()  # Visual check
```

**Checkpoint**: Histogram of weights, sanity check extremes

**Output**: `data_processed/tracts_with_demographics.geojson`

---

### Step 5: Implement Phase 2 - Baseline Accessibility

**Cell 2.1**: Define Accessibility Metric (markdown only)
- Document the formula (already in `docs/methods_outline.md`)
- Do NOT change it later

**Cell 2.2**: Compute Baseline Accessibility
- Create `src/accessibility/compute.py`
- Implement accessibility calculation
- Create choropleth map
- Distribution plot

**Cell 2.3**: Identify Transit Deserts
- Define threshold (bottom 20%)
- Create map

**Output**: `data_processed/baseline_accessibility.geojson`

---

### Step 6-8: Continue Following IMPLEMENTATION_GUIDE.md

Follow phases sequentially:
- Phase 3: Candidate Corridors
- Phase 4: Counterfactual Accessibility
- Phase 5: Optimization
- Phase 6: Demand Estimation
- Phase 7: Equity & Sensitivity
- Phase 8: Presentation

---

## 📋 Implementation Checklist

### Phase 0 ✅
- [x] Project scope defined
- [x] Methods outlined
- [x] Config file created
- [x] Folder structure created

### Phase 1 ⏳
- [x] GTFS ingestion module
- [ ] Job data ingestion module
- [ ] Demographics ingestion module
- [ ] Notebook 01 created

### Phase 2 ⏳
- [ ] Accessibility computation module
- [ ] Baseline accessibility computed
- [ ] Transit deserts identified

### Phase 3-8 ⏳
- [ ] To be implemented following guide

---

## 🎯 Key Principles

1. **Follow phases sequentially** - Don't skip ahead
2. **Check checkpoints** - Verify each phase before moving on
3. **Use sanity checks** - Visualizations and assertions
4. **Don't change assumptions** - They're frozen in config.py
5. **Document issues** - Note any problems encountered

---

## 📖 Reference Documents

- **Implementation**: `IMPLEMENTATION_GUIDE.md` - Detailed step-by-step
- **Methodology**: `docs/methods_outline.md` - How everything works
- **Scope**: `docs/project_scope.md` - What's in/out of scope
- **Status**: `PROJECT_RESTRUCTURE_SUMMARY.md` - What's done, what's next

---

## ⚠️ Important Reminders

1. **Parameters are FROZEN** - Don't change `config.py` without documenting why
2. **Follow the guide** - Use `IMPLEMENTATION_GUIDE.md` exactly
3. **Test as you go** - Run sanity checks after each phase
4. **Visualize everything** - Maps and plots catch errors early

---

## 🆘 If You Get Stuck

1. **Check the guide**: `IMPLEMENTATION_GUIDE.md` has detailed instructions
2. **Check checkpoints**: Each phase has specific checkpoints
3. **Check sanity checks**: Visualizations should look reasonable
4. **Document issues**: Note problems for later review

---

## 🎓 For Cursor/LLM Assistance

**Always say**:
> "Implement Phase X.Y exactly as written in IMPLEMENTATION_GUIDE.md. Include sanity checks and visualizations. Do not move ahead."

This ensures:
- ✅ Correct implementation
- ✅ Proper testing
- ✅ No feature creep
- ✅ No assumption drift

---

**Ready to start? Begin with Step 1: Run `00_exploration.ipynb`**

