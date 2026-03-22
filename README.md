# LA Public Transit & Job Accessibility

End-to-end analysis of **how many jobs are reachable within 30 minutes by transit + walking** across **Los Angeles County** census tracts, using **Metro GTFS** stops, **LEHD** jobs, and **ACS** population and income.

**Outputs:** choropleth maps of accessibility and “transit deserts,” income vs. accessibility, a tract-level distribution, **Moran’s I** (spatial clustering of accessibility), and CSV summaries in `outputs/tables/`.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Place in `data_raw/` (not committed):

- Census tract shapefile `tl_*.shp` (and sidecars)
- LEHD WAC file `*wac*.csv` or `.csv.gz`
- ACS tract file `*acs*.csv`
- GTFS: `metro_bus_gtfs.zip`, `metro_rail_gtfs.zip`

Run:

```bash
python scripts/run_la_analysis.py
```

Figures are written to `outputs/figures/` (`01_`–`04_` prefixes). See `docs/METHODS.md` for assumptions.

## Repository layout

```
src/config.py          # Paths and parameters
src/la_analysis.py     # Load data, accessibility, Moran’s I, plots
scripts/run_la_analysis.py
notebooks/01_la_transit_accessibility.ipynb
docs/METHODS.md
outputs/figures/       # Key PNGs (tracked)
outputs/tables/        # summary.csv, moran.txt (tracked)
```

This is a **planning sketch**, not a ridership forecast.
