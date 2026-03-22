# Project Scope: Optimizing Transit Corridor Investments

## Primary Research Question

**Where should new transit corridors be placed to maximize marginal job accessibility, and what is the implied upper bound on additional transit demand?**

## Research Objectives

1. **Descriptive**: Establish baseline accessibility status quo
2. **Counterfactual**: Measure accessibility impact of candidate transit corridors
3. **Optimization**: Rank corridors using principled objective function
4. **Demand Estimation**: Translate accessibility gains into upper-bound demand estimates

## Explicit Non-Goals

- ❌ **No full ridership prediction** - We estimate upper-bound demand only
- ❌ **No operational scheduling** - We abstract corridors as synthetic lines
- ❌ **No land-use feedback** - Job locations and population are fixed
- ❌ **No political feasibility modeling** - We focus on technical optimization

## Core Assumptions (Frozen)

These assumptions anchor the analysis and will not change:

1. **Fixed travel times**: Baseline network travel times are fixed
2. **Fixed job locations**: Jobs are located at tract centroids (from LEHD)
3. **Uniform adoption within tracts**: All residents in a tract have same accessibility
4. **Synthetic lines abstracted from GTFS**: New corridors are idealized, not constrained by existing GTFS routes
5. **Binary accessibility**: Job is either reachable (within threshold) or not (no distance decay)
6. **Single time threshold**: τ = 30 or 45 minutes (chosen once, documented)

## Scope Boundaries

- **Geographic**: Los Angeles County census tracts
- **Temporal**: Single time point (8 AM weekday, representative)
- **Modal**: Public transit + walking only (no private vehicles)
- **Corridor definition**: Polylines with stop spacing, speed, headway parameters

## Success Criteria

1. ✅ Baseline accessibility computed and visualized
2. ✅ 20-50 candidate corridors generated and mapped
3. ✅ Counterfactual accessibility computed for each corridor
4. ✅ Corridors ranked by weighted accessibility gain
5. ✅ Upper-bound demand estimated for top corridors
6. ✅ Equity analysis (distributional effects)
7. ✅ Sensitivity analysis (robustness checks)

## Deliverables

- **Code**: Reproducible pipeline (notebooks + src modules)
- **Figures**: Baseline map, top corridors map, gain distributions, demand rankings
- **Tables**: Corridor rankings, accessibility gains, demand estimates
- **Documentation**: Methods outline, assumptions, limitations

