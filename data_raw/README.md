# Data (local only)

Place these files here (not committed):

| File pattern | Source |
|--------------|--------|
| `tl_*.shp` + sidecars | U.S. Census TIGER/Line tracts |
| `*wac*.csv` or `.csv.gz` | LEHD LODES WAC (workplace jobs) |
| `*acs*.csv` | ACS 5-year tract tables (pop, median income) |
| `metro_bus_gtfs.zip`, `metro_rail_gtfs.zip` | LA Metro GTFS |

Then run `python scripts/run_la_analysis.py`.
