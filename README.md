# Transit Deserts: Minimal Notebook Workflow

This project measures transit accessibility inequities in Los Angeles using GTFS, census, and jobs data. The workflow is intentionally simple: everything happens inside a small set of Jupyter notebooks.

## Folder Layout
```
transit-deserts/
├── data_raw/        # Downloaded input files (GTFS, census, jobs)
├── notebooks/       # Ordered notebooks (00–07)
├── outputs/         # Figures, tables, exported data
├── requirements.txt # Python dependencies
└── README.md
```

Only three folders matter:
- `data_raw/` – you place all source data here; it stays out of git.
- `notebooks/` – every analysis step lives in a numbered notebook.
- `outputs/` – anything you want to share (plots, tables) goes here.

## Setup
1. Create/activate a Python 3.11 environment (Anaconda “base” works).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Register the kernel once (from the same environment):
   ```bash
   python -m ipykernel install --user --name transit-deserts --display-name "Python 3.11 (transit-deserts)"
   ```
4. Open the notebooks and select the `Python 3.11 (transit-deserts)` kernel.

## Notebook Roadmap
1. `00_setup.ipynb` – confirm environment, check folders, verify GTFS files.
2. `01_data_ingestion.ipynb` – download/inspect GTFS, census, LEHD, and OSM data.
3. `02_network_and_travel_times.ipynb` – build walking+transit network, compute travel times.
4. `03_accessibility.ipynb` – calculate accessibility indices (30/45 min jobs, 2SFCA).
5. `04_spatial_analysis.ipynb` – exploratory maps, clustering, Moran’s I, regressions.
6. `05_interventions.ipynb` – simulate added stops/frequency and measure equity impact.
7. `06_visualization.ipynb` – create final charts/maps (optional lightweight dashboard).
8. `07_reporting.ipynb` – assemble policy brief tables and narrative.

Work notebook-by-notebook; each saves interim results to `outputs/` (CSVs, Parquet, PNGs). There is no separate `src/` code folder—keep helper functions inside the notebooks for clarity.

## Data You Need
- GTFS: LA Metro bus & rail zips.
- Census: tract shapefile plus ACS 5-year tables (income, cars, population, commute).
- Jobs: LEHD LODES workplace area characteristics.

Place every downloaded file inside `data_raw/`. Large files stay out of git thanks to `.gitignore`.

## Tips
- Keep markdown notes in each notebook describing assumptions.
- Use `outputs/` for intermediate exports (e.g., `outputs/accessibility_tracts.parquet`).
- When Overpass (OSM) times out, rerun with a smaller bounding box or try later.

That’s it—one folder, a handful of notebooks, and clear linear steps. Reach out if you need help filling in any notebook.
