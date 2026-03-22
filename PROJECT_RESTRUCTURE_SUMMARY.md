# Project Restructure Summary

## ✅ What Has Been Completed

### Phase 0: Project Scoping & Guardrails ✅

**Documentation Created**:
- `docs/project_scope.md` - Research question, non-goals, assumptions (FROZEN)
- `docs/methods_outline.md` - Detailed methodology for all phases
- `src/config.py` - All constants and parameters (FROZEN - do not change)

**Folder Structure Created**:
```
transit-deserts/
├── data_raw/              (existing)
├── data_processed/        (NEW)
├── data_intermediate/     (NEW)
├── src/                   (NEW)
│   ├── config.py          ✅
│   ├── ingest/            ✅ (gtfs.py created)
│   ├── accessibility/     (to create)
│   ├── corridors/         (to create)
│   ├── optimization/      (to create)
│   └── demand/            (to create)
├── notebooks/
│   ├── 00_exploration.ipynb  ✅ (NEW)
│   ├── 01_baseline_accessibility.ipynb  (to create)
│   ├── 02_candidate_corridors.ipynb     (to create)
│   ├── 03_counterfactual_accessibility.ipynb  (to create)
│   ├── 04_optimization_results.ipynb    (to create)
│   └── 05_demand_analysis.ipynb         (to create)
├── outputs/
│   ├── figures/           (NEW)
│   └── tables/            (NEW)
└── docs/                  (NEW)
    ├── project_scope.md   ✅
    └── methods_outline.md ✅
```

**Modules Created**:
- `src/ingest/gtfs.py` - GTFS data loading (ready to use)

**Guides Created**:
- `IMPLEMENTATION_GUIDE.md` - Step-by-step instructions for each phase

### Phase 1: Data Ingestion (PARTIAL)

**Completed**:
- ✅ GTFS ingestion module (`src/ingest/gtfs.py`)
- ✅ Exploration notebook (`00_exploration.ipynb`)

**Remaining**:
- ⏳ Job data ingestion module (`src/ingest/jobs.py`)
- ⏳ Demographics ingestion module (`src/ingest/demographics.py`)
- ⏳ Notebook 01 (Baseline Accessibility) - Phase 1 cells

---

## 📋 Next Steps (In Order)

### Immediate: Complete Phase 1

1. **Create `src/ingest/jobs.py`**
   - Load LEHD/LODES WAC file
   - Aggregate to census tract
   - Follow pattern from `gtfs.py`

2. **Create `src/ingest/demographics.py`**
   - Load Census ACS data
   - Extract population, income, car ownership
   - Create weight vector

3. **Create Notebook 01: Baseline Accessibility**
   - Cell 1.1: Ingest GTFS (use `src/ingest/gtfs.py`)
   - Cell 1.2: Ingest jobs (use `src/ingest/jobs.py`)
   - Cell 1.3: Ingest demographics (use `src/ingest/demographics.py`)
   - Cell 2.1: Define accessibility metric (markdown)
   - Cell 2.2: Compute baseline accessibility
   - Cell 2.3: Identify transit deserts

### Then: Phase 2-8

Follow `IMPLEMENTATION_GUIDE.md` sequentially.

---

## 🎯 Key Changes from Old Project

### Old Project Focus
- **Question**: "Where are transit deserts?"
- **Method**: Identification, spatial analysis, ML prediction
- **Output**: Maps of deserts, feature importance

### New Project Focus
- **Question**: "Where should new transit corridors be placed to maximize accessibility?"
- **Method**: Counterfactual analysis, optimization, demand estimation
- **Output**: Ranked corridors, accessibility gains, demand estimates

### Structural Changes
1. **New folder structure**: `src/` modules instead of notebook-only
2. **New workflow**: Descriptive → Counterfactual → Optimization → Demand
3. **New focus**: Optimization and policy recommendations, not just identification
4. **Frozen assumptions**: All parameters in `config.py` (do not change)

---

## 📖 How to Use This Project

### For Implementation

1. **Read `IMPLEMENTATION_GUIDE.md`** - Detailed instructions for each phase
2. **Follow phases sequentially** - Do not skip ahead
3. **Check checkpoints** - Verify each phase before moving on
4. **Use sanity checks** - Visualizations and assertions at each step

### For Understanding

1. **Read `docs/project_scope.md`** - Understand research question and boundaries
2. **Read `docs/methods_outline.md`** - Understand methodology
3. **Check `src/config.py`** - See all parameters (they're frozen)

### For Cursor/LLM Assistance

**Always say**:
> "Implement Phase X.Y exactly as written in IMPLEMENTATION_GUIDE.md. Do not move ahead."

This prevents:
- Feature creep
- Assumption drift
- Premature optimization

---

## ⚠️ Important Notes

### Frozen Parameters
- **DO NOT CHANGE** values in `src/config.py` without documenting why
- **DO NOT CHANGE** accessibility metric definition once Phase 2 starts
- **DO NOT CHANGE** objective function once Phase 5 starts

### Scope Boundaries
- **NO** full ridership prediction (upper bound only)
- **NO** operational scheduling
- **NO** land-use feedback
- **NO** political feasibility

### Testing Strategy
- Run sanity checks after each phase
- Verify outputs exist before moving on
- Check visualizations look reasonable
- Document any issues

---

## 📊 Expected Outputs

### Phase 1-2 (Baseline)
- `data_processed/stops_all.geojson`
- `data_processed/jobs_by_tract.geojson`
- `data_processed/tracts_with_demographics.geojson`
- `data_processed/baseline_accessibility.geojson`
- `outputs/figures/baseline_accessibility_map.png`

### Phase 3 (Corridors)
- `data_processed/candidate_corridors.geojson`
- `outputs/figures/candidate_corridors_map.png`

### Phase 4 (Counterfactual)
- `data_processed/counterfactual_accessibility_gains.parquet`

### Phase 5 (Optimization)
- `outputs/tables/corridor_rankings.csv`
- `outputs/figures/top_corridors_map.png`

### Phase 6 (Demand)
- `outputs/tables/demand_estimates.csv`
- `outputs/figures/demand_ranking.png`

---

## 🚀 Getting Started

1. **Run Notebook 00** (`00_exploration.ipynb`)
   - Verifies folder structure
   - Checks data availability
   - No analysis yet

2. **Implement Phase 1.1** (GTFS ingestion)
   - Use `src/ingest/gtfs.py`
   - Create Notebook 01, Cell 1.1
   - Include sanity checks

3. **Continue sequentially** following `IMPLEMENTATION_GUIDE.md`

---

## 📝 Project Status

**Current Phase**: Phase 0 ✅ Complete, Phase 1 ⏳ In Progress

**Completion**:
- Phase 0: ✅ 100%
- Phase 1: ⏳ 30% (GTFS module done, jobs/demographics pending)
- Phase 2-8: ⏳ 0%

**Next Milestone**: Complete Phase 1 (all data ingestion)

---

## ❓ Questions?

- **Methodology**: See `docs/methods_outline.md`
- **Implementation**: See `IMPLEMENTATION_GUIDE.md`
- **Scope**: See `docs/project_scope.md`
- **Parameters**: See `src/config.py`

