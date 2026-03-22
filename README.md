# Optimizing Transit Corridor Investments to Maximize Accessibility and Potential Demand in Los Angeles

## Research Question

**Where should new transit corridors be placed to maximize marginal job accessibility, and what is the implied upper bound on additional transit demand?**

## Problem Statement

Public transit accessibility varies dramatically across Los Angeles County. While identifying transit deserts is important, this project goes further: it optimizes where new transit corridors should be placed to maximize accessibility gains, particularly for high-need communities. Using counterfactual analysis and principled optimization, we rank candidate corridors and estimate upper-bound demand.

## Project Structure

```
transit-deserts/
├── docs/
│   ├── project_scope.md          # Research question, assumptions, non-goals
│   └── methods_outline.md         # Detailed methodology
├── src/
│   ├── config.py                  # Frozen parameters (DO NOT CHANGE)
│   ├── ingest/                    # Data ingestion modules
│   ├── accessibility/             # Accessibility computation modules
│   ├── corridors/                 # Corridor generation modules
│   ├── optimization/              # Optimization modules
│   └── demand/                    # Demand estimation modules
├── notebooks/
│   ├── 00_exploration.ipynb       # Data exploration & sanity checks
│   ├── 01_baseline_accessibility.ipynb    # Baseline accessibility
│   ├── 02_candidate_corridors.ipynb       # Corridor generation
│   ├── 03_counterfactual_accessibility.ipynb  # Counterfactual analysis
│   ├── 04_optimization_results.ipynb          # Optimization & ranking
│   └── 05_demand_analysis.ipynb               # Demand estimation & equity
├── data_raw/                      # Source data (gitignored)
├── data_processed/                # Clean, processed data
├── data_intermediate/             # Intermediate computations
└── outputs/
    ├── figures/                   # Publication-quality figures
    └── tables/                    # Results tables
```

## Methodology Overview

### Phase 1: Data Ingestion & Baseline
- Load GTFS (bus + rail), jobs (LEHD), demographics (Census)
- Compute baseline accessibility using cumulative opportunity measure
- Identify transit deserts

### Phase 2: Candidate Corridor Generation
- Generate 20-50 candidate corridors using multiple strategies:
  - Desert → job center connections
  - High-pop → high-job connections
  - Existing arterial alignments

### Phase 3: Counterfactual Accessibility
- For each corridor, compute accessibility impact
- Measure ΔA_i(ℓ) = A_i^cf(ℓ) - A_i^baseline
- Store results as tract × corridor matrix

### Phase 4: Optimization
- Rank corridors using objective function:
  Score(ℓ) = Σ w_i · ΔA_i(ℓ)
- Where w_i = population × need indicator
- Compare weighted vs unweighted rankings

### Phase 5: Upper-Bound Demand Estimation
- Estimate demand: D_i(ℓ) = P_i · ΔA_i(ℓ) / (A_i^baseline + ε)
- Aggregate: D(ℓ) = Σ D_i(ℓ)
- Label explicitly as upper bound

### Phase 6: Equity & Sensitivity Analysis
- Distributional effects (by income, desert status)
- Sensitivity to parameters (time threshold, stop spacing, weights)

## Key Features

- **Counterfactual Design**: Measures impact of each corridor individually
- **Principled Optimization**: Transparent objective function, no ML black boxes
- **Upper-Bound Demand**: Honest estimation with clear limitations
- **Equity Focus**: Weighted optimization prioritizes high-need areas
- **Sensitivity Analysis**: Robustness checks for key parameters

## Data Sources

- **GTFS**: LA Metro bus and rail schedules
- **LEHD/LODES**: Workplace Area Characteristics (jobs by tract)
- **Census ACS**: Population, income, demographics by tract
- **OSM**: OpenStreetMap walking network

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Place data in `data_raw/`**:
   - GTFS files: `metro_bus_gtfs.zip`, `metro_rail_gtfs.zip`
   - Census tract shapefile
   - LEHD WAC file: `ca_wac_S000_JT00_YYYY.csv.gz`
   - ACS data (or download via API)

   Large files stay out of git thanks to `.gitignore`.

3. **Run notebooks sequentially**:
   - `00_exploration.ipynb` — Verify data
   - `01_baseline_accessibility.ipynb` — Baseline
   - `02_candidate_corridors.ipynb` — Generate corridors
   - `03_counterfactual_accessibility.ipynb` — Counterfactuals
   - `04_optimization_results.ipynb` — Optimization
   - `05_demand_analysis.ipynb` — Demand & equity

## Key Assumptions (Frozen)

These assumptions anchor the analysis and are documented in `docs/project_scope.md`:

1. Fixed travel times (baseline network is fixed)
2. Fixed job locations (tract centroids)
3. Uniform adoption within tracts
4. Synthetic corridors (abstracted from GTFS)
5. Binary accessibility (within threshold = reachable)
6. Single time threshold (τ = 30 or 45 minutes)

## Explicit Non-Goals

- ❌ Full ridership prediction (upper bound only)
- ❌ Operational scheduling
- ❌ Land-use feedback
- ❌ Political feasibility modeling

## Outputs

### Required Figures
1. Baseline accessibility map
2. Candidate corridors map
3. Top corridors map (optimization results)
4. Accessibility gain distribution
5. Demand ranking

### Required Tables
1. Corridor rankings (optimization scores)
2. Demand estimates (upper bounds)
3. Equity analysis (distributional effects)
4. Sensitivity analysis (robustness checks)

## Documentation

- **`docs/project_scope.md`**: Research question, assumptions, non-goals
- **`docs/methods_outline.md`**: Detailed methodology for all phases
- **`IMPLEMENTATION_GUIDE.md`**: Step-by-step implementation instructions
- **`PROJECT_RESTRUCTURE_SUMMARY.md`**: What's been done, what's next

## Implementation Status

- ✅ Phase 0: Project scoping & guardrails
- ⏳ Phase 1: Data ingestion (GTFS module complete, jobs/demographics pending)
- ⏳ Phase 2-8: To be implemented

See `IMPLEMENTATION_GUIDE.md` for detailed instructions.

## Citation

If using this work, please cite appropriately and acknowledge data sources (Census Bureau, LA Metro, LEHD, OpenStreetMap).
