# Transit Deserts: Analyzing Accessibility Inequities in Los Angeles

## Quick Description

A data science project that identifies and analyzes transit accessibility inequities in Los Angeles County using spatial analysis and machine learning. Combines GTFS transit data, census demographics, and employment statistics to identify transit deserts, understand spatial patterns, and provide evidence-based insights for equitable transit planning.

## What It Does

This project answers three key questions:
1. **Where are transit deserts?** (Spatial clustering analysis)
2. **What drives accessibility?** (Feature importance, regression models)
3. **How can we improve equity?** (Intervention simulation, policy recommendations)

## Key Methods

- **Spatial Analysis**: Moran's I, LISA clusters, spatial regression
- **Machine Learning**: Random Forest, Gradient Boosting, clustering, PCA
- **Accessibility Metrics**: Jobs reachable within time thresholds
- **Equity Analysis**: Links accessibility to demographics

## Technologies

- Python (GeoPandas, scikit-learn, libpysal)
- Jupyter Notebooks
- GTFS, Census ACS, LEHD LODES data
- OpenStreetMap

## Outputs

- Interactive maps of transit deserts
- Feature importance rankings
- Spatial cluster classifications
- Model performance comparisons
- Policy-ready visualizations

## Repository Structure

```
transit-deserts/
├── notebooks/          # 11 sequential analysis notebooks
├── data_raw/          # Input data (GTFS, census, jobs)
├── outputs/           # Generated maps, tables, visualizations
└── requirements.txt   # Python dependencies
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run notebooks sequentially (00 → 07)
3. Each notebook saves outputs for the next step

## Key Findings

- Transit deserts form **spatially contiguous regions** (not random)
- **Distance to downtown** and **population density** are top predictors
- **Spatial spillover effects** matter (neighbors' accessibility affects yours)
- ML models outperform spatial regression for prediction (R² ~0.85 vs ~0.04)
- **Cluster-specific interventions** needed (not one-size-fits-all)

## Use Cases

- Transit planning agencies
- Equity research
- Urban policy analysis
- Academic research (spatial analysis, accessibility)
- Data science portfolio (geospatial ML)

## License

Open source - feel free to use and adapt for your own analysis.

