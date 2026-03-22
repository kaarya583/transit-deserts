"""
LA County transit accessibility: GTFS stops, LEHD jobs, ACS population/income.
Cumulative opportunity within a fixed travel-time budget; Moran’s I on tract accessibility.
"""

from __future__ import annotations

import warnings
import geopandas as gpd
import gtfs_kit as gk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.spatial.distance import cdist

warnings.filterwarnings("ignore", category=UserWarning)

import config  # noqa: E402


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


def load_gtfs_stops() -> gpd.GeoDataFrame:
    feeds = []
    for z in sorted(config.DATA_RAW.glob("*gtfs*.zip")):
        feeds.append(gk.read_feed(z, dist_units="km"))
    if not feeds:
        raise FileNotFoundError("Add metro_bus_gtfs.zip and metro_rail_gtfs.zip to data_raw/")
    parts = []
    for f in feeds:
        if f.stops is not None and len(f.stops) > 0:
            parts.append(f.stops)
    stops = pd.concat([p for p in parts if p is not None and len(p) > 0], ignore_index=True)
    gdf = gpd.GeoDataFrame(
        stops,
        geometry=gpd.points_from_xy(stops["stop_lon"], stops["stop_lat"], crs=config.GEO_CRS),
    )
    b = config.LA_BBOX
    return gdf.cx[b["min_lon"] : b["max_lon"], b["min_lat"] : b["max_lat"]]


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


def morans_i(gdf: gpd.GeoDataFrame, col: str = "accessibility_jobs"):
    try:
        from esda.moran import Moran
        from libpysal.weights import Queen
    except ImportError:
        return None

    gdf = gdf.copy()
    gdf.geometry = gdf.geometry.buffer(0)
    y = gdf[col].astype(float).values
    if np.any(~np.isfinite(y)):
        y = np.where(np.isfinite(y), y, np.nanmedian(y))

    w = Queen.from_dataframe(gdf, use_index=False)
    if w.n == 0:
        return None
    mi = Moran(y, w, permutations=99)
    return {"I": float(mi.I), "p_sim": float(mi.p_sim), "z_score": float(mi.z_norm)}


def run_pipeline():
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    config.FIGURES.mkdir(parents=True, exist_ok=True)
    config.TABLES.mkdir(parents=True, exist_ok=True)

    tracts = _load_tracts()
    jobs = _load_jobs()
    acs = _load_acs()
    tracts = tracts.merge(jobs, on="GEOID", how="left")
    tracts = tracts.merge(acs, on="GEOID", how="left")
    tracts["jobs_total"] = tracts["jobs_total"].fillna(0)

    stops = load_gtfs_stops()
    gdf = compute_accessibility(tracts, stops)

    moran = morans_i(gdf)

    out_geo = config.DATA_PROCESSED / "la_tract_accessibility.geojson"
    gdf.to_file(out_geo, driver="GeoJSON")
    pq = config.DATA_PROCESSED / "la_tract_accessibility.parquet"
    gdf.to_parquet(pq)

    summary = {
        "tracts": len(gdf),
        "stops_used": len(stops),
        "total_jobs_in_model": float(gdf["jobs_total"].sum()),
        "mean_accessibility_jobs": float(gdf["accessibility_jobs"].mean()),
        "median_accessibility_jobs": float(np.median(gdf["accessibility_jobs"])),
        "desert_tracts_pct": float(gdf["transit_desert"].mean() * 100),
        "time_threshold_min": config.TIME_THRESHOLD_MIN,
    }
    if moran:
        summary["moran_I"] = moran["I"]
        summary["moran_p"] = moran["p_sim"]
    pd.DataFrame([summary]).to_csv(config.TABLES / "summary.csv", index=False)

    _plot_maps(gdf)
    _plot_distribution(gdf)
    _plot_income(gdf)
    if moran:
        with open(config.TABLES / "moran.txt", "w") as f:
            f.write(f"Moran's I = {moran['I']:.4f}\np-value (sim) = {moran['p_sim']:.4f}\n")

    return gdf, moran, summary


def _la_extent(ax):
    b = config.LA_BBOX
    ax.set_xlim(b["min_lon"], b["max_lon"])
    ax.set_ylim(b["min_lat"], b["max_lat"])


def _plot_maps(gdf: gpd.GeoDataFrame):
    g = gdf.to_crs(config.GEO_CRS)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    vmin, vmax = 0, np.nanpercentile(g["accessibility_jobs"], 98)
    g.plot(
        column="accessibility_jobs",
        ax=axes[0],
        legend=True,
        cmap="viridis",
        vmin=vmin,
        vmax=vmax,
        legend_kwds={"label": "Jobs reachable (30 min)"},
    )
    axes[0].set_title("Job accessibility via transit (30 min)")
    axes[0].axis("off")
    _la_extent(axes[0])

    g.plot(
        column="transit_desert",
        ax=axes[1],
        categorical=True,
        cmap="OrRd",
        legend=True,
        legend_kwds={"title": "Transit desert"},
    )
    axes[1].set_title(f"Transit desert (bottom {config.DESERT_PERCENTILE}%)")
    axes[1].axis("off")
    _la_extent(axes[1])

    plt.tight_layout()
    plt.savefig(config.FIGURES / "01_accessibility_and_deserts.png", dpi=200, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 6))
    g.plot(column="accessibility_jobs", ax=ax, legend=True, cmap="magma", vmin=vmin, vmax=vmax)
    ax.set_title("Jobs reachable within 30 minutes (tract level)")
    ax.axis("off")
    _la_extent(ax)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "02_accessibility_choropleth.png", dpi=200, bbox_inches="tight")
    plt.close()


def _plot_distribution(gdf: gpd.GeoDataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    x = gdf["accessibility_jobs"].replace([np.inf, -np.inf], np.nan).dropna()
    sns.histplot(x / 1000.0, bins=50, kde=True, ax=ax, color="steelblue")
    ax.set_xlabel("Jobs reachable within 30 min (thousands)")
    ax.set_ylabel("Number of tracts")
    ax.set_title("Distribution of tract job accessibility")
    plt.tight_layout()
    plt.savefig(config.FIGURES / "03_accessibility_distribution.png", dpi=200, bbox_inches="tight")
    plt.close()


def _plot_income(gdf: gpd.GeoDataFrame):
    sub = gdf.dropna(subset=["median_income", "accessibility_jobs"]).copy()
    if len(sub) < 10:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(
        sub["median_income"] / 1000.0,
        sub["accessibility_jobs"] / 1000.0,
        alpha=0.35,
        s=12,
        c="darkslateblue",
    )
    ax.set_xlabel("Median household income ($1000s)")
    ax.set_ylabel("Jobs reachable in 30 min (thousands)")
    ax.set_title("Income vs transit accessibility to jobs")
    plt.tight_layout()
    plt.savefig(config.FIGURES / "04_income_vs_accessibility.png", dpi=200, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    run_pipeline()
