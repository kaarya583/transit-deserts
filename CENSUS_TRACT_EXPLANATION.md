# Understanding Census Tract Polygons: How They're Chosen

## 🎯 High-Level: What Are Census Tracts?

**Census tracts** are small statistical areas created by the US Census Bureau to organize demographic data. Think of them as "neighborhood-sized" units that:
- Have roughly **4,000 people each** (range: 1,200-8,000)
- Follow **visible boundaries** (roads, rivers, railroads) when possible
- Stay **relatively stable** over time (updated every 10 years)
- Are used by **all Census data** (ACS, decennial census, LEHD)

**For LA County**: We have **2,498 tracts** - these are the "neighborhoods" we're analyzing.

---

## 🔧 Low-Level: How Tracts Are Actually Created

### Who Creates Them?
- **US Census Bureau** (not us, not the city)
- Created through the **Participant Statistical Areas Program (PSAP)**
- Local governments can suggest boundaries, but Census has final say

### Design Principles:

1. **Population Size**:
   - Target: ~4,000 people per tract
   - Range: 1,200-8,000 (can vary for geographic constraints)
   - Why: Large enough for stable statistics, small enough for neighborhood detail

2. **Boundary Rules**:
   - Follow **visible features** when possible:
     - Major roads/highways
     - Rivers/waterways
     - Railroad tracks
     - City boundaries
   - Avoid splitting:
     - Neighborhoods
     - School districts
     - Voting precincts (when possible)

3. **Stability**:
   - Boundaries change only every 10 years (with Census)
   - Small changes allowed mid-decade if population shifts dramatically
   - Goal: Allow comparison over time

4. **Homogeneity** (when possible):
   - Try to keep similar land use together
   - Residential areas together
   - Commercial areas together
   - But this is secondary to population size

### The Process:

1. **Census Bureau** starts with previous decade's tracts
2. **Local governments** review and suggest changes
3. **Census** evaluates based on:
   - Population targets
   - Boundary visibility
   - Geographic constraints
4. **Final boundaries** published in TIGER/Line files
5. **All Census data** (ACS, decennial, LEHD) uses these same boundaries

---

## 📊 Why We Use Tracts (Not Other Units)

### Tracts vs. Other Options:

| Unit | Size | Pros | Cons | Our Choice? |
|------|------|------|------|-------------|
| **Census Tracts** | ~4,000 people | Standard, stable, all data available | Might miss sub-neighborhood variation | ✅ **YES** |
| Block Groups | ~1,200 people | More granular | Less stable, smaller sample sizes | ❌ Too small |
| ZIP Codes | Variable | Familiar to public | Not designed for demographics, boundaries change | ❌ Not standardized |
| Neighborhoods | Variable | Intuitive | Not standardized, boundaries vary | ❌ Not consistent |
| City Boundaries | Large | Administrative | Too large, miss internal variation | ❌ Too large |

### Why Tracts Win:

1. **Data Availability**: All our sources (ACS, LEHD, TIGER) use tracts
2. **Right Size**: Small enough to see neighborhood differences, large enough for stable stats
3. **Policy Relevance**: Planners and policymakers think in tracts
4. **Stability**: Can compare over time
5. **Standardization**: Same boundaries across all data sources

---

## 🗺️ How LA County Tracts Look

**Structure**:
- **2,498 tracts** covering all of LA County
- Each tract has unique **11-digit GEOID**: `06037XXXXXX`
  - `06` = California (state FIPS code)
  - `037` = Los Angeles County (county FIPS code)
  - `XXXXXX` = Tract number (6 digits, e.g., `432300`)

**Examples**:
- `06037432300` = Tract 4323.00 in LA County, CA
- `06037101110` = Tract 1011.10 in LA County, CA

**Boundaries**:
- Follow major roads (e.g., Wilshire Blvd, Sunset Blvd)
- Follow natural features (e.g., LA River, Santa Monica Mountains)
- Generally rectangular/irregular polygons
- Vary in size (dense urban = smaller, suburban = larger)

---

## 🎯 For Our Project: What This Means

### Origins (Where People Live):
- **2,498 tract centroids** = where people live
- Each centroid = geometric center of tract polygon
- We assume people are distributed throughout the tract
- **Population** from ACS tells us how many people live in each tract

### Destinations (Where People Work):
- **~2,494 tract centroids with jobs** = where people work
- **Job counts** from LEHD tell us how many jobs are in each tract
- Some tracts are residential-only (no jobs)
- Some tracts are employment centers (many jobs)

### Accessibility Calculation:
- We compute travel time from **each origin tract** to **each destination tract**
- Weight by **jobs at destination** (more jobs = more opportunity)
- Sum up: "How many jobs can I reach from my tract within 30 minutes?"

---

## 📝 Key Takeaways

1. **We didn't choose the tracts** - Census Bureau did (based on population, boundaries, stability)

2. **Tracts are the right unit** because:
   - All our data is already at tract level
   - They represent meaningful neighborhoods
   - They're stable over time
   - They're policy-relevant

3. **For this analysis**:
   - Origins = tract centroids (where people live)
   - Destinations = tract centroids with jobs (where people work)
   - We measure accessibility between these points

4. **Limitations to be aware of**:
   - Geometric centroids ≠ actual population centers
   - Tract-level aggregation might miss within-tract variation
   - But this is standard practice and appropriate for this scale of analysis

---

**Bottom Line**: Census tracts are the standard unit for neighborhood-level demographic analysis. We're using them because they're the right size, have all the data we need, and are what policymakers use. The polygons themselves were designed by the Census Bureau to balance population size, visible boundaries, and statistical stability.

