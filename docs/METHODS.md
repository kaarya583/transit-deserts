# Methods (short)

**Area:** Los Angeles County census tracts.

**Transit:** Metro bus + rail stops from GTFS (`data_raw/*.zip`).

**Jobs:** LEHD Workplace Area Characteristics (`C000`) aggregated to tracts.

**People / income:** ACS tract tables (population, median household income).

**Accessibility:** For each tract home location, nearest stop is found; travel time to each tract with jobs uses walk–transit–walk legs with fixed speeds and a 5-minute wait. Jobs reachable in **≤ 30 minutes** are summed (cumulative opportunity).

**Transit deserts:** Tracts in the **bottom 20%** of job accessibility.

**Spatial clustering:** **Moran’s I** (Queen contiguity) on tract accessibility — tests whether high- or low-accessibility tracts cluster in space.

This is a planning-oriented sketch, not a ridership model.
