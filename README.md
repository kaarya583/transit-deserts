# LA Public Transit & Job Accessibility

Pipeline for **Los Angeles County**: tract **job accessibility** (30 min), **transit deserts**, **metro graph** with **demand** at stations, and **candidate corridors** scored as **demand × R_eff** (effective resistance from the Laplacian).

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Data in `data_raw/`: tract shapefile `tl_*.shp`, LEHD WAC, ACS, GTFS zips.

```bash
python scripts/run_la_analysis.py
```

## Figures

| File | Description |
|------|-------------|
| `01_accessibility_and_deserts.png` | Job access + desert tracts |
| `02_income_vs_accessibility.png` | Income vs access |
| `03_metro_network_demand.png` | Rail graph, demand-scaled nodes |
| `04_corridor_candidates_map.png` | Dark basemap, numbered top corridors |
| `05_corridor_impact_metrics.png` | Demand / R_eff / impact (normalized) |
| `06_corridors_on_deserts.png` | Top 5 corridors over transit deserts (hatch) |
| `07_corridor_results_table.png` | Report table: stop names, km, demand, R_eff, impact |
| `08_dline_extension_network_impact.png` | Baseline vs extension graph with headline network impacts |
| `09_dline_extension_top_pair_gains.png` | OD pairs with largest effective resistance reduction |
| `10_dline_extension_reach_gain_report.png` | Composite map + bars of reach gain to new D Line stations |
| `11_dline_accessibility_impact.png` | Before/after tract accessibility impact near D Line extension |

**Tables:** `summary.csv`, `graph_summary.csv`, `corridor_priorities.csv`, `dline_extension_pair_impacts.csv`, `dline_extension_top_gains.csv`, `dline_extension_reach_gain.csv`, `dline_accessibility_impact.csv`

See `docs/METHODS.md`.

## Layout

```
src/config.py  src/la_analysis.py  src/transport_graph.py  src/viz_la.py
scripts/run_la_analysis.py  notebooks/01_la_transit_accessibility.ipynb
```

Planning-oriented, not a ridership model.
