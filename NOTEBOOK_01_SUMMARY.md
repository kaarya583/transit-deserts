# Notebook 01: Data Ingestion - Complete Summary

## 🎯 High-Level Overview

**What We Did**: Collected, cleaned, and merged all the foundational data needed to analyze transit accessibility in Los Angeles County.

**Why It Matters**: Without clean, properly formatted data, we can't compute travel times, measure accessibility, or identify transit deserts. This notebook is the foundation for everything that follows.

---

## 📊 What We Have Now (Outputs)

### 1. **Tracts File** (`la_tracts_with_acs_jobs.geojson`)
- **What**: 2,498 census tracts in LA County with boundaries (polygons)
- **Data Included**:
  - Population (from ACS)
  - Median household income
  - Vehicle ownership
  - Commute patterns
  - Job counts (from LEHD)
- **Format**: GeoJSON (can also load from Parquet for speed)
- **Key Column**: `GEOID` (11-digit code: 06037XXXXXX)

### 2. **Jobs File** (`jobs_by_tract_la.csv`)
- **What**: Total number of jobs per census tract
- **Source**: LEHD LODES workplace data (2021)
- **Coverage**: 2,494 tracts with job data
- **Total Jobs**: ~4.5 million jobs in LA County
- **Key Column**: `tract_geoid` (matches `GEOID` in tracts file)

### 3. **Stops File** (`metro_stops_all.geojson`)
- **What**: All LA Metro transit stops (bus + rail)
- **Count**: 12,278 stops total
  - 11,838 bus stops
  - 440 rail stops
- **Format**: Point geometries with lat/lon
- **Use**: These are the transit access points we'll use to build the network

---

## 🔧 Low-Level Technical Details

### Data Sources & Processing

#### **Census Tracts (TIGER/Line)**
- **Source**: `tl_2025_06_tract.shp` (2025 TIGER shapefile for California)
- **Processing**:
  1. Loaded all 9,129 California tracts
  2. Filtered to county FIPS code `037` (Los Angeles County)
  3. Result: 2,498 tracts
- **Why**: We need tract boundaries to:
  - Map accessibility scores
  - Aggregate population/demographics
  - Define "neighborhoods" for analysis

#### **ACS Data (American Community Survey)**
- **Source**: Census API (2018-2022 5-year estimates)
- **Variables Downloaded**:
  - `B01003_001E`: Total population
  - `B19013_001E`: Median household income
  - `B25046_001E`: Aggregate vehicles available
  - `B08126_001E`: Transit commuters by poverty status
  - `B08301_001E`: Total commuters
- **Processing**:
  1. Downloaded via API (2,498 tracts)
  2. Renamed columns to readable names
  3. Created `tract_geoid` by zero-padding: `state(2) + county(3) + tract(6) = 11 digits`
  4. Filtered to LA County (county code "37")
- **Why**: We need demographics to:
  - Identify which tracts have high need (low income, no cars)
  - Measure equity (who has access vs. who needs it)

#### **LEHD Jobs Data (LODES)**
- **Source**: `ca_wac_S000_JT00_2021.csv.gz` (Workplace Area Characteristics)
- **Format**: 15-digit `w_geocode` = state(2) + county(3) + tract(6) + block(4)
- **Processing** (THE TRICKY PART):
  1. Read in 50k-row chunks (252k total rows)
  2. Filter to LA County while reading (positions 2-5 = "037")
  3. Extract tract GEOID: zero-pad to 15 digits, then slice first 11 digits
  4. Aggregate jobs by tract (sum `C000` column)
  5. Result: 2,494 tracts with job counts
- **Why**: We need jobs to:
  - Compute accessibility (jobs reachable within X minutes)
  - Measure opportunity (how many jobs can people access?)

#### **GTFS Data (Transit Stops)**
- **Source**: `metro_bus_gtfs.zip` and `metro_rail_gtfs.zip`
- **Processing**:
  1. Used `gtfs_kit` to parse GTFS feeds
  2. Extracted `stops.txt` table
  3. Created point geometries from lat/lon
  4. Combined bus + rail stops
- **Why**: We need stops to:
  - Build the transit network
  - Compute walking distances to transit
  - Measure transit coverage

### Key Technical Challenges Solved

1. **GEOID Format Mismatch**:
   - Problem: Different data sources use different formats (with/without leading zeros)
   - Solution: Always zero-pad to correct length, then slice
   - Example: `60371011101` → zero-pad to 15 → `060371011101000` → slice 11 → `06037101110`

2. **Large File Processing**:
   - Problem: LEHD file has 252k rows, too big to load at once
   - Solution: Chunked reading with immediate filtering (only keep LA County)
   - Result: Process ~63k LA County rows instead of 252k statewide

3. **Data Type Consistency**:
   - Problem: GEOIDs stored as integers vs strings
   - Solution: Always convert to string before merging
   - Result: Successful merges between all datasets

---

## 🚀 How This Sets Up the Project

### For Notebook 02 (Network & Travel Times)

**What We'll Do**:
- Build a multimodal network (walking + transit)
- Compute travel times from each tract to each job location
- Create travel time matrices

**What We Need (Now Have)**:
- ✅ Tract centroids (from tracts file) → origins
- ✅ Job locations (from jobs file) → destinations  
- ✅ Transit stops (from stops file) → network nodes
- ✅ Walking network (will download in notebook 02)

### For Notebook 03 (Accessibility)

**What We'll Do**:
- Calculate jobs reachable within 30/45 minutes
- Compute 2SFCA accessibility scores
- Normalize by population

**What We Need (Now Have)**:
- ✅ Travel time matrices (from notebook 02)
- ✅ Job counts per tract (from jobs file)
- ✅ Population per tract (from tracts file)

### For Notebook 04 (Spatial Analysis)

**What We'll Do**:
- Map accessibility scores
- Find spatial clusters (transit deserts)
- Run spatial regressions

**What We Need (Now Have)**:
- ✅ Accessibility scores (from notebook 03)
- ✅ Demographics (income, cars) for regression
- ✅ Tract boundaries for mapping

### For Notebook 05 (Interventions)

**What We'll Do**:
- Simulate adding stops or increasing frequency
- Measure impact on accessibility
- Optimize interventions

**What We Need (Now Have)**:
- ✅ Baseline accessibility (from notebook 03)
- ✅ Current stop locations (from stops file)
- ✅ Network structure (from notebook 02)

---

## ✅ Quality Checks

- [x] All 2,498 tracts have population data
- [x] 2,494 tracts have job data (99.8% coverage)
- [x] GEOIDs match between files (can merge successfully)
- [x] All stops loaded (12,278 total)
- [x] Data types consistent (strings for GEOIDs)
- [x] Files saved in multiple formats (GeoJSON + Parquet)

---

## 📝 Next Steps

**Ready for Notebook 02**: All data is clean, formatted correctly, and ready to use. We can now:
1. Build the multimodal network
2. Compute travel times
3. Start measuring accessibility

The foundation is solid! 🎉

