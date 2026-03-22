# Transit Deserts

This project measures transit accessibility inequities in Los Angeles using GTFS, census, and jobs data.
## Folder Layout
```
transit-deserts/
├── data_raw/        # Downloaded input files (GTFS, census, jobs)
├── notebooks/       # Ordered notebooks (00–07)
├── outputs/         # Figures, tables, exported data
├── requirements.txt # Python dependencies
└── README.md
```

3 Important Folders
- `data_raw/` – all source data here
- `notebooks/` – every analysis step lives in a numbered notebook.
- `outputs/` – anything to share (plots, tables)

## Notebook Roadmap
1. `00_setup.ipynb` – confirm environment, check folders, verify GTFS files.
2. `01_data_ingestion.ipynb` – download/inspect GTFS, census, LEHD, and OSM data.
3. `02_network_and_travel_times.ipynb` – build walking+transit network, compute travel times.
4. `03_accessibility.ipynb` – calculate accessibility indices (30/45 min jobs, 2SFCA).
5. `04_spatial_analysis.ipynb` – exploratory maps, clustering, Moran’s I, regressions.
6. `05_interventions.ipynb` – simulate added stops/frequency and measure equity impact.
7. `06_visualization.ipynb` – create final charts/maps (optional lightweight dashboard).
8. `07_reporting.ipynb` – assemble policy brief tables and narrative.

## Data
- GTFS: LA Metro bus & rail zips.
- Census: tract shapefile plus ACS 5-year tables (income, cars, population, commute).
- Jobs: LEHD LODES workplace area characteristics.

Place every downloaded file inside `data_raw/`. Large files stay out of git thanks to `.gitignore`.
