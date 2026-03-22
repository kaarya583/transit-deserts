# Notebook 00: Exploration & Sanity Checks - Implementation Guide

## Purpose (WHY)

This notebook exists **only** for:
- ✅ Sanity-check raw data
- ✅ Build intuition about LA's spatial structure  
- ✅ Catch errors early (CRS, missing tracts, weird geometries)
- ✅ Validate spatial alignment

**This is reconnaissance, not analysis.** Research labs expect this phase even if it's not in the final paper.

## What MUST be Included

### 1. Data Loading (Read-Only)
- ✅ Census tracts geometry
- ✅ Job counts by tract (LEHD/LODES)
- ✅ Population / need variables (Census ACS)
- ✅ Transit stops (bus + rail from GTFS)

### 2. Basic Checks
- ✅ Number of tracts
- ✅ Missing job/population tracts
- ✅ CRS consistency
- ✅ Bounding box sanity
- ✅ Geometry validity

### 3. Simple Maps
- ✅ Tracts (base map)
- ✅ Jobs (choropleth)
- ✅ Transit stops overlay

## What MUST NOT be Included ❌

- ❌ **No accessibility calculations**
- ❌ **No travel time logic**
- ❌ **No optimization**
- ❌ **No corridor ideas**
- ❌ **No metrics or analysis**

**If Cursor starts adding "metrics" here, it's wrong.**

## Checkpoint Artifact

After running this notebook, you should be able to say:

> **"Yes, the data makes sense spatially, and nothing looks broken."**

If not, **stop the project here** and fix ingestion.

## Structure

The notebook follows this structure:

1. **Part 1**: Load Census Tract Geometry
2. **Part 2**: Load Job Data (LEHD/LODES)
3. **Part 3**: Load Population & Demographics (Census ACS)
4. **Part 4**: Load Transit Stops (GTFS)
5. **Part 5**: Merge Data & Check Completeness
6. **Part 6**: Simple Maps for Spatial Intuition
7. **Part 7**: Sanity Checks Summary

## Outputs

**Maps** (saved to `outputs/figures/`):
- `00_tracts_base_map.png` - Base map of census tracts
- `00_jobs_choropleth.png` - Jobs distribution choropleth
- `00_transit_stops_overlay.png` - Transit stops overlaid on tracts

**No processed data files** - This notebook is read-only.

## Sanity Checks

The notebook performs these checks:

1. ✅ Census tracts loaded
2. ✅ Tract CRS consistent
3. ✅ Tract geometries valid
4. ✅ Tract bounding box reasonable (LA County extent)
5. ✅ Job data loaded
6. ✅ Jobs are positive
7. ✅ Population data available
8. ✅ Transit stops loaded
9. ✅ Stops CRS consistent
10. ✅ Spatial alignment (stops overlap with tracts)

**All checks must pass** before proceeding to Notebook 01.

## Common Issues & Fixes

### Issue: GEOID column not found
**Fix**: Check column names, may need to create from components (STATEFP + COUNTYFP + TRACTCE)

### Issue: CRS mismatch
**Fix**: This is OK - we'll normalize in processing. Just document it.

### Issue: Missing data
**Fix**: Document which tracts are missing what, decide if acceptable

### Issue: Invalid geometries
**Fix**: Remove invalid geometries or fix them

## Next Steps

**If all checks pass**: Proceed to Notebook 01 (Baseline Accessibility)

**If checks fail**: Fix data ingestion issues before continuing

---

**Remember**: This notebook is **read-only exploration**. No analysis, no metrics, no optimization. Just validation and intuition.

