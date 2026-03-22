# Notebook 02: Network and Travel Times - Ready to Run

## ✅ What's Fixed

1. **Notebook 01 GEOID Issue**: Fixed LEHD reading to preserve leading zeros
   - Now reads `w_geocode` as string (not integer)
   - Properly zero-pads to 15 digits before slicing
   - Jobs file now has correct 11-digit GEOIDs starting with `06037`
   - **2,494 tracts now have jobs data** (was 0 before)

2. **Tracts File Updated**: Re-merged jobs data into tracts file
   - All 2,498 tracts have population data
   - 2,494 tracts have jobs data (99.8% coverage)

3. **Notebook 02 Enhanced**: Added explanation of census tract polygons

---

## 📚 Understanding Census Tract Polygons

### High-Level Explanation

**What are census tracts?**
- Small statistical areas created by the US Census Bureau
- Designed to have ~4,000 people each
- Boundaries follow visible features (roads, rivers)
- Updated every 10 years with the Census

**Why we use them:**
- All our data (ACS, LEHD) is already at tract level
- They represent meaningful "neighborhoods" for policy
- Standard unit used by planners and policymakers
- Stable boundaries allow comparison over time

**How they're chosen:**
- **We don't choose them** - the Census Bureau does
- Created through the Participant Statistical Areas Program (PSAP)
- Based on:
  1. Population targets (~4,000 per tract)
  2. Visible boundaries (roads, rivers, railroads)
  3. Geographic constraints
  4. Stability over time

**LA County specifics:**
- 2,498 tracts total
- Each has unique 11-digit GEOID: `06037XXXXXX`
  - `06` = California
  - `037` = Los Angeles County
  - `XXXXXX` = Tract number

### Low-Level Technical Details

**Boundary creation process:**
1. Census Bureau starts with previous decade's tracts
2. Local governments suggest changes
3. Census evaluates based on population, boundaries, geography
4. Final boundaries published in TIGER/Line files
5. All Census data uses these same boundaries

**For our analysis:**
- **Origins** = tract centroids (geometric center of polygon)
  - Represent where people LIVE
  - 2,498 origin points
- **Destinations** = tract centroids with jobs
  - Represent where people WORK
  - ~2,494 destination points (tracts with jobs > 0)

**Limitations:**
- Geometric centroids ≠ actual population centers
- Could use population-weighted centroids for more accuracy
- But geometric centroids are standard and appropriate for this scale

---

## 🚀 Notebook 02: What It Does

### Step-by-Step Process

1. **Load Data** (from Notebook 01)
   - Tracts with demographics and jobs
   - Transit stops
   - Jobs by tract

2. **Create Origin/Destination Points**
   - Compute tract centroids (geometric centers)
   - Origins = all tracts (where people live)
   - Destinations = tracts with jobs (where people work)

3. **Build Walking Network**
   - Download OSM walking network for LA County
   - May take 5-10 minutes
   - Projects to UTM for accurate distances

4. **Compute Travel Times** (Simplified)
   - Find nearest transit stop to each origin
   - Find nearest transit stop to each destination
   - Compute straight-line distances
   - Convert to travel times using:
     - Walking speed: 80 m/min (~5 km/h)
     - Transit speed: 500 m/min (~30 km/h average)
     - Wait time: 5 minutes average

5. **Save Outputs**
   - Travel time matrix (origins × destinations)
   - Origin/destination point files
   - Walking network (if downloaded)

### Important Notes

**Simplified Approach:**
- Uses straight-line distances (not actual network paths)
- Assumes direct transit connections
- This is a **pragmatic approximation** for this project
- For production, use full multimodal routing (R5, OpenTripPlanner)

**Why This Works:**
- Still produces meaningful accessibility measures
- Captures relative differences between tracts
- Fast enough to run on a laptop
- Can be refined later with full routing

---

## ✅ Current Status

### Data Ready:
- ✅ 2,498 tracts with population data
- ✅ 2,494 tracts with jobs data (99.8% coverage)
- ✅ 12,278 transit stops
- ✅ All GEOIDs properly formatted and matching

### Notebook 02 Ready:
- ✅ All cells created and documented
- ✅ Error handling in place
- ✅ Clear explanations of methods
- ✅ Outputs defined

### Next Steps:
1. **Run Notebook 02** to build network and compute travel times
2. **Review outputs** to ensure travel times are reasonable
3. **Move to Notebook 03** to calculate accessibility scores

---

## 📝 Key Files Created

- `CENSUS_TRACT_EXPLANATION.md` - Detailed explanation of how tracts are chosen
- `NOTEBOOK_02_READY.md` - This file (status and instructions)
- `NOTEBOOK_01_SUMMARY.md` - Summary of Notebook 01
- `PROJECT_STATUS_COMPLETE.md` - Overall project status

---

**You're all set to run Notebook 02!** 🚀

The data is clean, the code is ready, and everything should work smoothly. The notebook will guide you through each step with clear explanations.

