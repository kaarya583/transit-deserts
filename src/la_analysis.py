"""
LA County: tract accessibility, deserts, metro graph, corridors via Laplacian effective resistance.
"""

from __future__ import annotations

import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

warnings.filterwarnings("ignore", category=UserWarning)

import config
import transport_graph
import viz_la


def _load_tracts() -> gpd.GeoDataFrame:
    shp = list(config.DATA_RAW.glob("tl_*.shp"))
    if not shp:
        raise FileNotFoundError("Add Census tract shapefile (tl_*.shp) to data_raw/")
    tracts = gpd.read_file(shp[0])
    if "COUNTYFP" in tracts.columns:
        tracts = tracts[tracts["COUNTYFP"] == "037"].copy()
    elif "GEOID" in tracts.columns:
        tracts = tracts[tracts["GEOID"].astype(str).str[:5] == config.COUNTY_GEOID_PREFIX].copy()
    tracts["GEOID"] = tracts["GEOID"].astype(str).str.zfill(11)
    return tracts


def _load_jobs() -> pd.DataFrame:
    paths = list(config.DATA_RAW.glob("*wac*.csv.gz")) + list(config.DATA_RAW.glob("*wac*.csv"))
    if not paths:
        return pd.DataFrame(columns=["GEOID", "jobs_total"])
    raw = pd.read_csv(paths[0], compression="gzip" if paths[0].suffix == ".gz" else None)
    if "w_geocode" not in raw.columns or "C000" not in raw.columns:
        return pd.DataFrame(columns=["GEOID", "jobs_total"])
    raw["GEOID"] = raw["w_geocode"].astype(str).str.zfill(15).str[:11]
    raw = raw[raw["GEOID"].str.startswith("06037")]
    jobs = raw.groupby("GEOID", as_index=False)["C000"].sum()
    jobs.rename(columns={"C000": "jobs_total"}, inplace=True)
    jobs["GEOID"] = jobs["GEOID"].astype(str).str.zfill(11)
    return jobs


def _load_acs() -> pd.DataFrame:
    paths = list(config.DATA_RAW.glob("*acs*.csv"))
    if not paths:
        return pd.DataFrame(columns=["GEOID", "pop_total", "median_income"])
    acs = pd.read_csv(paths[0])
    if all(c in acs.columns for c in ["state", "county", "tract"]):
        acs["GEOID"] = (
            acs["state"].astype(str).str.zfill(2)
            + acs["county"].astype(str).str.zfill(3)
            + acs["tract"].astype(str).str.zfill(6)
        )
    if "B01003_001E" in acs.columns:
        acs["pop_total"] = pd.to_numeric(acs["B01003_001E"], errors="coerce")
    if "B19013_001E" in acs.columns:
        acs["median_income"] = pd.to_numeric(acs["B19013_001E"], errors="coerce").replace(
            -666666666, np.nan
        )
    acs["GEOID"] = acs["GEOID"].astype(str).str.zfill(11)
    return acs[["GEOID", "pop_total", "median_income"]].drop_duplicates("GEOID")


def haversine_m(lon1, lat1, lon2, lat2):
    r = 6371000.0
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return r * (2 * np.arcsin(np.sqrt(np.clip(a, 0, 1))))


def compute_accessibility(tracts: gpd.GeoDataFrame, stops: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    tp = tracts.to_crs(config.PROJ_CRS)
    cen = tp.geometry.centroid
    tgc = gpd.GeoDataFrame(geometry=cen, crs=config.PROJ_CRS).to_crs(config.GEO_CRS)
    tg = tracts.copy()
    tg["centroid_lon"] = tgc.geometry.x.values
    tg["centroid_lat"] = tgc.geometry.y.values

    tg["jobs_total"] = tg["jobs_total"].fillna(0)
    tg["pop_total"] = tg["pop_total"].fillna(0).clip(lower=0)
    dest = tg[tg["jobs_total"] > 0].copy()

    sg = stops.to_crs(config.GEO_CRS)
    sc = np.array([[p.x, p.y] for p in sg.geometry])

    oc = np.column_stack([tg["centroid_lon"], tg["centroid_lat"]])
    dc = np.column_stack([dest["centroid_lon"], dest["centroid_lat"]])

    od = cdist(oc, sc, metric="euclidean")
    dd = cdist(dc, sc, metric="euclidean")
    oi = np.argmin(od, axis=1)
    di = np.argmin(dd, axis=1)
    osl, osta = sc[oi, 0], sc[oi, 1]
    dsl, dsta = sc[di, 0], sc[di, 1]
    om = od[np.arange(len(tg)), oi] * 111000.0
    dm = dd[np.arange(len(dest)), di] * 111000.0

    tw_o = om[:, np.newaxis] / config.WALK_M_PER_MIN
    tw_d = dm[np.newaxis, :] / config.WALK_M_PER_MIN
    dtr = haversine_m(osl[:, np.newaxis], osta[:, np.newaxis], dsl[np.newaxis, :], dsta[np.newaxis, :])
    tt = dtr / config.TRANSIT_M_PER_MIN
    tmat = tw_o + tt + config.WAIT_MIN + tw_d

    jobs = dest["jobs_total"].values
    reach = (tmat <= config.TIME_THRESHOLD_MIN).astype(np.float64)
    acc = reach @ jobs

    out = tg.copy()
    out["accessibility_jobs"] = acc
    safe_pop = out["pop_total"].replace(0, np.nan)
    out["accessibility_per_1k"] = (out["accessibility_jobs"] / safe_pop) * 1000.0
    out["accessibility_per_1k"] = out["accessibility_per_1k"].replace([np.inf, -np.inf], np.nan)

    thr = np.nanpercentile(out["accessibility_jobs"], config.DESERT_PERCENTILE)
    out["transit_desert"] = out["accessibility_jobs"] <= thr
    return out


def run_pipeline():
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    config.FIGURES.mkdir(parents=True, exist_ok=True)
    config.TABLES.mkdir(parents=True, exist_ok=True)

    viz_la.setup_style()

    tracts = _load_tracts()
    jobs = _load_jobs()
    acs = _load_acs()
    tracts = tracts.merge(jobs, on="GEOID", how="left")
    tracts = tracts.merge(acs, on="GEOID", how="left")
    tracts["jobs_total"] = tracts["jobs_total"].fillna(0)

    stops = transport_graph.load_gtfs_stops_fast()
    gdf = compute_accessibility(tracts, stops)

    out_geo = config.DATA_PROCESSED / "la_tract_accessibility.geojson"
    gdf.to_file(out_geo, driver="GeoJSON")
    gdf.to_parquet(config.DATA_PROCESSED / "la_tract_accessibility.parquet")

    summary = {
        "tracts": len(gdf),
        "stops_used": len(stops),
        "total_jobs_in_model": float(gdf["jobs_total"].sum()),
        "mean_accessibility_jobs": float(gdf["accessibility_jobs"].mean()),
        "median_accessibility_jobs": float(np.median(gdf["accessibility_jobs"])),
        "desert_tracts_pct": float(gdf["transit_desert"].mean() * 100),
        "time_threshold_min": config.TIME_THRESHOLD_MIN,
    }

    viz_la.figure_accessibility_deserts(gdf, config.FIGURES / "01_accessibility_and_deserts.png")
    viz_la.figure_income_access(gdf, config.FIGURES / "02_income_vs_accessibility.png")

    feeds = transport_graph.load_feeds()
    G, station_nodes = transport_graph.build_line_graph(feeds, route_types=set(config.GRAPH_ROUTE_TYPES))
    station_nodes = station_nodes[station_nodes["node_id"].isin(G.nodes)].copy()

    gstats = transport_graph.summarize_graph(G)
    summary["graph_nodes"] = gstats["nodes"]
    summary["graph_edges"] = gstats["edges"]

    nodes, _, L, _ = transport_graph.laplacian_pinv_conductance(G)
    stations_w = transport_graph.station_buffer_weights(gdf, station_nodes, buffer_m=config.STATION_BUFFER_M)
    stations_w = stations_w[stations_w["node_id"].isin(G.nodes)].copy()
    st_ix = stations_w.set_index("node_id")
    f = np.array([float(st_ix["mean_tract_accessibility"].get(n, np.nan)) for n in nodes])
    med = float(np.nanmedian(f[np.isfinite(f)])) if np.any(np.isfinite(f)) else 0.0
    f = np.where(np.isfinite(f), f, med)
    summary["accessibility_roughness_fLf"] = transport_graph.accessibility_roughness(L, f)

    pd.DataFrame([gstats]).to_csv(config.TABLES / "graph_summary.csv", index=False)

    viz_la.figure_metro_network(G, stations_w, config.FIGURES / "03_metro_network_demand.png")

    cors = transport_graph.corridor_graph_impact_scores(
        G,
        gdf,
        stations_w,
        top_k=config.CORRIDOR_TOP_STATIONS,
        max_pairs=config.CORRIDOR_RANDOM_PAIRS,
        max_eucl_m=float(config.CORRIDOR_MAX_EUCL_KM) * 1000.0,
        buffer_m=config.CORRIDOR_BUFFER_M,
    )
    if len(cors) > 0:
        cors.to_csv(config.TABLES / "corridor_priorities.csv", index=False)
        summary["top_impact_score"] = float(cors.iloc[0]["impact_score"])
        summary["top_corridor_km"] = float(cors.iloc[0]["euclidean_km"])
        summary["top_effective_resistance"] = float(cors.iloc[0]["effective_resistance"])
        viz_la.figure_corridor_map(gdf, G, stations_w, cors, config.FIGURES / "04_corridor_candidates_map.png")
        viz_la.figure_corridor_metrics(cors, config.FIGURES / "05_corridor_impact_metrics.png")
        viz_la.figure_corridors_on_deserts(gdf, cors, config.FIGURES / "06_corridors_on_deserts.png")
        viz_la.figure_corridor_results_table(cors, station_nodes, config.FIGURES / "07_corridor_results_table.png")

    pd.DataFrame([summary]).to_csv(config.TABLES / "summary.csv", index=False)

    return gdf, summary


if __name__ == "__main__":
    run_pipeline()
