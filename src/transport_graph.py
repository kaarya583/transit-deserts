"""
GTFS rail graph, Laplacian-based effective resistance, station demand buffers, corridor impact = demand × R_eff.
"""

from __future__ import annotations

import zipfile
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import LineString

import config


def _haversine_m(lon1, lat1, lon2, lat2):
    r = 6371000.0
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return r * (2 * np.arcsin(np.sqrt(np.clip(a, 0, 1))))


def _read_stops_from_zip(zip_path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as z:
        df = pd.read_csv(z.open("stops.txt"), dtype=str, low_memory=False)
    for col in ("stop_lon", "stop_lat"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_gtfs_stops_fast() -> gpd.GeoDataFrame:
    parts = []
    for z in sorted(config.DATA_RAW.glob("*gtfs*.zip")):
        stops = _read_stops_from_zip(z)
        if stops.empty:
            continue
        parts.append(stops)
    if not parts:
        raise FileNotFoundError("Add *gtfs*.zip feeds under data_raw/")
    stops = pd.concat(parts, ignore_index=True)
    gdf = gpd.GeoDataFrame(
        stops,
        geometry=gpd.points_from_xy(stops["stop_lon"], stops["stop_lat"], crs=config.GEO_CRS),
    )
    b = config.LA_BBOX
    return gdf.cx[b["min_lon"] : b["max_lon"], b["min_lat"] : b["max_lat"]]


def _load_stop_times_chunked(z: zipfile.ZipFile, trip_ids: set[str], chunksize: int = 400_000) -> pd.DataFrame:
    if not trip_ids:
        return pd.DataFrame()
    parts = []
    with z.open("stop_times.txt") as fp:
        for chunk in pd.read_csv(
            fp,
            chunksize=chunksize,
            dtype=str,
            usecols=["trip_id", "stop_sequence", "stop_id"],
            low_memory=False,
        ):
            chunk["stop_sequence"] = pd.to_numeric(chunk["stop_sequence"], errors="coerce")
            sub = chunk[chunk["trip_id"].isin(trip_ids)]
            if len(sub):
                parts.append(sub)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def _read_feed_tables_for_graph(zip_path: Path, route_types: set[int]) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    with zipfile.ZipFile(zip_path) as z:
        try:
            routes = pd.read_csv(z.open("routes.txt"), dtype=str, low_memory=False)
            trips = pd.read_csv(z.open("trips.txt"), dtype=str, low_memory=False)
            stops = pd.read_csv(z.open("stops.txt"), dtype=str, low_memory=False)
        except KeyError:
            return None
        if "route_type" not in routes.columns or "route_id" not in trips.columns:
            return None
        routes["route_type"] = pd.to_numeric(routes["route_type"], errors="coerce").fillna(-1).astype(int)
        r_ok = routes[routes["route_type"].isin(route_types)]
        if r_ok.empty:
            return None
        rid_set = set(r_ok["route_id"].astype(str))
        trips_f = trips[trips["route_id"].astype(str).isin(rid_set)]
        if trips_f.empty:
            return None
        trip_ids = set(trips_f["trip_id"].astype(str))
        st = _load_stop_times_chunked(z, trip_ids)
        if st.empty:
            return None

    st = st.merge(trips_f[["trip_id", "route_id"]], on="trip_id", how="left")
    st = st.merge(routes[["route_id", "route_type"]], on="route_id", how="left")
    st = st[st["route_type"].isin(route_types)]

    for col in ("stop_lon", "stop_lat"):
        stops[col] = pd.to_numeric(stops[col], errors="coerce")
    b = config.LA_BBOX
    stops_tbl = stops[
        (stops["stop_lon"] >= b["min_lon"])
        & (stops["stop_lon"] <= b["max_lon"])
        & (stops["stop_lat"] >= b["min_lat"])
        & (stops["stop_lat"] <= b["max_lat"])
    ].copy()
    if stops_tbl.empty:
        return None
    return st, stops_tbl


def _apply_transfers_from_zip(
    G: nx.Graph,
    zip_path: Path,
    stops_tbl: pd.DataFrame,
    sid_map: dict,
) -> None:
    ok = set(stops_tbl["stop_id"].astype(str))
    try:
        with zipfile.ZipFile(zip_path) as z:
            if "transfers.txt" not in z.namelist():
                return
            tr = pd.read_csv(z.open("transfers.txt"), dtype=str, low_memory=False)
    except (OSError, KeyError):
        return
    if "from_stop_id" not in tr.columns or "to_stop_id" not in tr.columns:
        return
    base_w = float(getattr(config, "TRANSFER_EDGE_M", 150.0))
    for _, row in tr.iterrows():
        a, b = str(row["from_stop_id"]), str(row["to_stop_id"])
        if a not in ok or b not in ok or a == b:
            continue
        na, nb = sid_map.get(a), sid_map.get(b)
        if na is None or nb is None:
            continue
        w = base_w
        if "min_transfer_time" in tr.columns:
            mt = pd.to_numeric(row.get("min_transfer_time"), errors="coerce")
            if pd.notna(mt) and float(mt) > 0:
                w = max(w, min(float(mt) / 60.0 * config.WALK_M_PER_MIN, 2000.0))
        if G.has_edge(na, nb):
            G[na][nb]["weight"] = min(G[na][nb]["weight"], w)
        else:
            G.add_edge(na, nb, weight=float(w))


def load_feeds():
    from types import SimpleNamespace

    out = []
    for z in sorted(config.DATA_RAW.glob("*gtfs*.zip")):
        out.append((z.stem, SimpleNamespace(path=z)))
    return out


def build_line_graph(
    feeds: list,
    route_types: set[int] | None = None,
) -> tuple[nx.Graph, pd.DataFrame]:
    if route_types is None:
        route_types = {0, 1, 2}
    G = nx.Graph()
    stop_rows = []

    for feed_name, feed in feeds:
        zip_path = getattr(feed, "path", None)
        if zip_path is None:
            continue
        zip_path = Path(zip_path)
        if not zip_path.is_file():
            continue
        parsed = _read_feed_tables_for_graph(zip_path, set(route_types))
        if parsed is None:
            continue
        st, stops_tbl = parsed
        stops_tbl["node_id"] = feed_name + "::" + stops_tbl["stop_id"].astype(str)
        sid_map = {str(r["stop_id"]): r["node_id"] for _, r in stops_tbl.iterrows()}
        coord_map = {
            str(r["stop_id"]): (float(r["stop_lon"]), float(r["stop_lat"])) for _, r in stops_tbl.iterrows()
        }

        for _, grp in st.groupby("trip_id"):
            grp = grp.sort_values("stop_sequence")
            seq = grp["stop_id"].astype(str).tolist()
            for a, b in zip(seq[:-1], seq[1:]):
                na, nb = sid_map.get(a), sid_map.get(b)
                if na is None or nb is None:
                    continue
                ca, cb = coord_map.get(a), coord_map.get(b)
                if ca is None or cb is None:
                    continue
                w = _haversine_m(ca[0], ca[1], cb[0], cb[1])
                if G.has_edge(na, nb):
                    G[na][nb]["weight"] = min(G[na][nb]["weight"], w)
                else:
                    G.add_edge(na, nb, weight=float(w))

        _apply_transfers_from_zip(G, zip_path, stops_tbl, sid_map)

        for _, r in stops_tbl.iterrows():
            stop_rows.append(
                {
                    "node_id": r["node_id"],
                    "stop_name": str(r.get("stop_name", "")),
                    "lon": float(r["stop_lon"]),
                    "lat": float(r["stop_lat"]),
                    "feed": feed_name,
                }
            )

    nodes = pd.DataFrame(stop_rows).drop_duplicates("node_id")
    if G.number_of_nodes() > 0:
        largest = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest).copy()
    return G, nodes


def station_buffer_weights(
    tracts: gpd.GeoDataFrame,
    station_points: pd.DataFrame,
    buffer_m: float = 800.0,
) -> pd.DataFrame:
    tg = tracts.to_crs(config.PROJ_CRS)
    cen = tg.geometry.centroid
    tx = cen.x.values
    ty = cen.y.values
    pop = tg["pop_total"].fillna(0).values
    job = tg["jobs_total"].fillna(0).values
    acc = tg["accessibility_jobs"].astype(float).values
    tree = cKDTree(np.column_stack([tx, ty]))

    st = station_points.copy()
    stp = gpd.GeoDataFrame(
        st,
        geometry=gpd.points_from_xy(st["lon"], st["lat"], crs=config.GEO_CRS),
    ).to_crs(config.PROJ_CRS)
    sx = stp.geometry.x.values
    sy = stp.geometry.y.values

    pop_near = []
    job_near = []
    acc_mean = []
    for i in range(len(st)):
        idx = tree.query_ball_point([sx[i], sy[i]], r=buffer_m)
        if len(idx):
            pop_near.append(float(pop[idx].sum()))
            job_near.append(float(job[idx].sum()))
            acc_mean.append(float(np.nanmean(acc[idx])))
        else:
            pop_near.append(0.0)
            job_near.append(0.0)
            acc_mean.append(np.nan)

    out = station_points.copy()
    out["pop_near"] = pop_near
    out["jobs_near"] = job_near
    out["mean_tract_accessibility"] = acc_mean
    out["weight"] = np.sqrt(np.maximum(out["pop_near"], 1.0) * np.maximum(out["jobs_near"], 1.0))
    return out


def _corridor_buffer_stats(
    gdf: gpd.GeoDataFrame,
    lon1: float,
    lat1: float,
    lon2: float,
    lat2: float,
    buffer_m: float,
) -> dict:
    line = LineString([(lon1, lat1), (lon2, lat2)])
    gl = gpd.GeoDataFrame(geometry=[line], crs=config.GEO_CRS).to_crs(config.PROJ_CRS)
    buf = gl.buffer(buffer_m).iloc[0]
    gt = gdf.to_crs(config.PROJ_CRS)
    hit = gt.geometry.intersects(buf)
    sub = gdf.loc[hit].copy()
    if len(sub) == 0:
        return {"n_tracts": 0, "mean_accessibility": np.nan, "pct_desert": np.nan}
    acc = sub["accessibility_jobs"].astype(float)
    des = sub["transit_desert"].astype(bool)
    return {
        "n_tracts": int(len(sub)),
        "mean_accessibility": float(np.nanmean(acc)),
        "pct_desert": float(des.mean() * 100.0),
    }


def corridor_graph_impact_scores(
    G: nx.Graph,
    gdf: gpd.GeoDataFrame,
    stations: pd.DataFrame,
    top_k: int = 50,
    max_pairs: int = 50,
    max_eucl_m: float = 22000.0,
    buffer_m: float | None = None,
) -> pd.DataFrame:
    stations = stations[stations["node_id"].isin(G.nodes)].copy()
    if len(stations) < 5 or G.number_of_nodes() < 3:
        return pd.DataFrame()
    buffer_m = buffer_m or getattr(config, "CORRIDOR_BUFFER_M", 800.0)
    acc_all = gdf["accessibility_jobs"].astype(float)
    acc_ref = float(np.nanpercentile(acc_all, 92))
    if acc_ref <= 0:
        acc_ref = float(np.nanmax(acc_all)) or 1.0

    _, ix, _, Lp = laplacian_pinv_conductance(G)

    s = stations.nlargest(min(top_k, len(stations)), "weight").copy()
    ids = s["node_id"].tolist()
    pos = stations.set_index("node_id")[["lon", "lat"]]
    wmap = stations.set_index("node_id")["weight"]

    rng = np.random.default_rng(42)
    pairs = []
    for _ in range(max_pairs * 25):
        i, j = rng.choice(len(ids), 2, replace=False)
        a, b = ids[i], ids[j]
        if a >= b:
            a, b = b, a
        if a not in ix or b not in ix:
            continue
        eucl = _haversine_m(pos.loc[a, "lon"], pos.loc[a, "lat"], pos.loc[b, "lon"], pos.loc[b, "lat"])
        if eucl > max_eucl_m:
            continue
        pairs.append((a, b))
        if len(pairs) >= max_pairs:
            break
    pairs = list(dict.fromkeys(pairs))

    rows = []
    for a, b in pairs:
        lon1, lat1 = float(pos.loc[a, "lon"]), float(pos.loc[a, "lat"])
        lon2, lat2 = float(pos.loc[b, "lon"]), float(pos.loc[b, "lat"])
        eucl = _haversine_m(lon1, lat1, lon2, lat2)
        demand = float(wmap.get(a, 0.0) * wmap.get(b, 0.0))
        R_eff = effective_resistance(ix, Lp, a, b)
        stt = _corridor_buffer_stats(gdf, lon1, lat1, lon2, lat2, buffer_m)
        mean_acc = stt["mean_accessibility"]
        if not np.isfinite(mean_acc) or stt["n_tracts"] == 0:
            unmet = np.nan
        else:
            unmet = max(0.0, 1.0 - min(mean_acc / acc_ref, 1.0))
        impact = demand * R_eff
        rows.append(
            {
                "station_a": a,
                "station_b": b,
                "lon_a": lon1,
                "lat_a": lat1,
                "lon_b": lon2,
                "lat_b": lat2,
                "euclidean_m": eucl,
                "euclidean_km": eucl / 1000.0,
                "demand_proxy": demand,
                "effective_resistance": R_eff,
                "n_tracts_buffer": stt["n_tracts"],
                "mean_accessibility_buffer": mean_acc,
                "pct_desert_tracts_buffer": stt["pct_desert"],
                "unmet_need": unmet,
                "impact_score": impact,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("impact_score", ascending=False).reset_index(drop=True)


def laplacian_pinv_conductance(G: nx.Graph):
    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return nodes, {}, np.zeros((0, 0)), np.zeros((0, 0))
    ix = {u: i for i, u in enumerate(nodes)}
    A = np.zeros((n, n))
    for u, v, d in G.edges(data=True):
        dist = float(d.get("weight", 1.0))
        c = 1.0 / (dist + 1.0)
        i, j = ix[u], ix[v]
        A[i, j] = c
        A[j, i] = c
    deg = A.sum(axis=1)
    L = np.diag(deg) - A
    Lp = np.linalg.pinv(L)
    return nodes, ix, L, Lp


def effective_resistance(ix: dict, Lp: np.ndarray, a, b) -> float:
    i, j = ix[a], ix[b]
    return float(Lp[i, i] + Lp[j, j] - 2.0 * Lp[i, j])


def accessibility_roughness(L: np.ndarray, f: np.ndarray) -> float:
    if L.size == 0 or len(f) != L.shape[0]:
        return float("nan")
    return float(f @ L @ f)


def summarize_graph(G: nx.Graph) -> dict:
    if G.number_of_nodes() == 0:
        return {"nodes": 0, "edges": 0, "density": 0.0}
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": float(nx.density(G)),
    }


def load_dline_extension_stops(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame(columns=["node_id", "stop_id", "stop_name", "lon", "lat"])
    df = pd.read_csv(p)
    req = {"stop_id", "stop_name", "stop_lat", "stop_lon"}
    if not req.issubset(set(df.columns)):
        return pd.DataFrame(columns=["node_id", "stop_id", "stop_name", "lon", "lat"])
    out = df.copy()
    out["lon"] = pd.to_numeric(out["stop_lon"], errors="coerce")
    out["lat"] = pd.to_numeric(out["stop_lat"], errors="coerce")
    out = out.dropna(subset=["lon", "lat"]).copy()
    b = config.LA_BBOX
    out = out[
        (out["lon"] >= b["min_lon"])
        & (out["lon"] <= b["max_lon"])
        & (out["lat"] >= b["min_lat"])
        & (out["lat"] <= b["max_lat"])
    ].copy()
    out["stop_id"] = out["stop_id"].astype(str)
    out["stop_name"] = out["stop_name"].astype(str)
    out["node_id"] = "dline_ext::" + out["stop_id"]
    return out[["node_id", "stop_id", "stop_name", "lon", "lat"]].reset_index(drop=True)


def add_dline_extension_to_graph(
    G: nx.Graph,
    station_nodes: pd.DataFrame,
    ext_stops: pd.DataFrame,
    connect_max_m: float = 3500.0,
) -> tuple[nx.Graph, pd.DataFrame, pd.DataFrame]:
    if ext_stops is None or len(ext_stops) < 2:
        return G.copy(), station_nodes.copy(), pd.DataFrame()
    Gx = G.copy()
    ext = ext_stops.reset_index(drop=True).copy()
    for _, r in ext.iterrows():
        Gx.add_node(r["node_id"])
    edge_rows = []
    for i in range(len(ext) - 1):
        a = ext.iloc[i]
        b = ext.iloc[i + 1]
        w = float(_haversine_m(float(a["lon"]), float(a["lat"]), float(b["lon"]), float(b["lat"])))
        Gx.add_edge(a["node_id"], b["node_id"], weight=w)
        edge_rows.append(
            {
                "u": a["node_id"],
                "v": b["node_id"],
                "lon_u": float(a["lon"]),
                "lat_u": float(a["lat"]),
                "lon_v": float(b["lon"]),
                "lat_v": float(b["lat"]),
                "kind": "extension",
            }
        )
    base = station_nodes[station_nodes["node_id"].isin(G.nodes)].copy()
    if len(base) > 0:
        terminals = [ext.iloc[0], ext.iloc[-1]]
        used_anchors = set()
        for t in terminals:
            d = _haversine_m(base["lon"].values, base["lat"].values, float(t["lon"]), float(t["lat"]))
            ix = int(np.argmin(d))
            best_d = float(d[ix])
            anchor = base.iloc[ix]
            if best_d <= float(connect_max_m) and anchor["node_id"] not in used_anchors:
                Gx.add_edge(str(t["node_id"]), str(anchor["node_id"]), weight=best_d)
                used_anchors.add(anchor["node_id"])
                edge_rows.append(
                    {
                        "u": str(t["node_id"]),
                        "v": str(anchor["node_id"]),
                        "lon_u": float(t["lon"]),
                        "lat_u": float(t["lat"]),
                        "lon_v": float(anchor["lon"]),
                        "lat_v": float(anchor["lat"]),
                        "kind": "anchor",
                    }
                )
    ext_nodes = ext.rename(columns={"lon": "stop_lon", "lat": "stop_lat"})[
        ["node_id", "stop_name", "stop_lon", "stop_lat"]
    ].copy()
    ext_nodes.rename(columns={"stop_lon": "lon", "stop_lat": "lat"}, inplace=True)
    ext_nodes["feed"] = "project28_dline_extension"
    nodes_out = pd.concat([station_nodes.copy(), ext_nodes], ignore_index=True).drop_duplicates("node_id")
    edges_out = pd.DataFrame(edge_rows)
    return Gx, nodes_out, edges_out


def compare_effective_resistance(
    G_before: nx.Graph,
    G_after: nx.Graph,
    focus_nodes: list[str],
    max_pairs: int = 250,
    seed: int = 42,
) -> tuple[dict, pd.DataFrame]:
    shared = [n for n in focus_nodes if n in G_before.nodes and n in G_after.nodes]
    if len(shared) < 3:
        return {}, pd.DataFrame()
    all_pairs = list(combinations(shared, 2))
    if len(all_pairs) > max_pairs:
        rng = np.random.default_rng(seed)
        take = rng.choice(len(all_pairs), size=max_pairs, replace=False)
        pairs = [all_pairs[i] for i in take]
    else:
        pairs = all_pairs
    _, ix0, _, Lp0 = laplacian_pinv_conductance(G_before)
    _, ix1, _, Lp1 = laplacian_pinv_conductance(G_after)
    rows = []
    for a, b in pairs:
        if a not in ix0 or b not in ix0 or a not in ix1 or b not in ix1:
            continue
        r0 = effective_resistance(ix0, Lp0, a, b)
        r1 = effective_resistance(ix1, Lp1, a, b)
        s0 = float(nx.shortest_path_length(G_before, source=a, target=b, weight="weight"))
        s1 = float(nx.shortest_path_length(G_after, source=a, target=b, weight="weight"))
        rows.append(
            {
                "station_a": a,
                "station_b": b,
                "r_eff_before": r0,
                "r_eff_after": r1,
                "r_eff_delta": r1 - r0,
                "r_eff_pct_change": ((r1 - r0) / r0 * 100.0) if r0 > 0 else np.nan,
                "sp_m_before": s0,
                "sp_m_after": s1,
                "sp_m_delta": s1 - s0,
                "sp_m_pct_change": ((s1 - s0) / s0 * 100.0) if s0 > 0 else np.nan,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return {}, df
    summary = {
        "pair_count": int(len(df)),
        "mean_r_eff_before": float(df["r_eff_before"].mean()),
        "mean_r_eff_after": float(df["r_eff_after"].mean()),
        "mean_r_eff_pct_change": float(df["r_eff_pct_change"].mean()),
        "median_r_eff_pct_change": float(df["r_eff_pct_change"].median()),
        "mean_sp_km_before": float(df["sp_m_before"].mean() / 1000.0),
        "mean_sp_km_after": float(df["sp_m_after"].mean() / 1000.0),
        "mean_sp_pct_change": float(df["sp_m_pct_change"].mean()),
    }
    return summary, df.sort_values("r_eff_pct_change", ascending=True).reset_index(drop=True)


def compare_extension_reach_gain(
    G_base: nx.Graph,
    G_after: nx.Graph,
    station_nodes_base: pd.DataFrame,
    ext_stops: pd.DataFrame,
    focus_nodes: list[str],
    baseline_offnetwork_penalty_m: float = 8000.0,
) -> tuple[dict, pd.DataFrame]:
    if ext_stops is None or len(ext_stops) == 0:
        return {}, pd.DataFrame()
    base_nodes = station_nodes_base[station_nodes_base["node_id"].isin(G_base.nodes)].copy()
    if len(base_nodes) == 0:
        return {}, pd.DataFrame()
    ext = ext_stops.copy()
    ext_ids = ext["node_id"].astype(str).tolist()
    G_virtual = G_base.copy()
    for _, e in ext.iterrows():
        e_id = str(e["node_id"])
        d = _haversine_m(base_nodes["lon"].values, base_nodes["lat"].values, float(e["lon"]), float(e["lat"]))
        ix = int(np.argmin(d))
        anchor = str(base_nodes.iloc[ix]["node_id"])
        G_virtual.add_node(e_id)
        G_virtual.add_edge(e_id, anchor, weight=float(d[ix]) + float(baseline_offnetwork_penalty_m))
    rows = []
    for n in focus_nodes:
        if n not in G_base.nodes or n not in G_after.nodes:
            continue
        b_vals = []
        a_vals = []
        for e_id in ext_ids:
            if e_id not in G_virtual.nodes or e_id not in G_after.nodes:
                continue
            b_vals.append(float(nx.shortest_path_length(G_virtual, source=n, target=e_id, weight="weight")))
            a_vals.append(float(nx.shortest_path_length(G_after, source=n, target=e_id, weight="weight")))
        if not b_vals or not a_vals:
            continue
        b_mean = float(np.mean(b_vals))
        a_mean = float(np.mean(a_vals))
        rows.append(
            {
                "node_id": str(n),
                "mean_sp_to_ext_km_before": b_mean / 1000.0,
                "mean_sp_to_ext_km_after": a_mean / 1000.0,
                "delta_km": (a_mean - b_mean) / 1000.0,
                "pct_change": ((a_mean - b_mean) / b_mean * 100.0) if b_mean > 0 else np.nan,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return {}, df
    summary = {
        "station_count": int(len(df)),
        "mean_reach_delta_km": float(df["delta_km"].mean()),
        "median_reach_delta_km": float(df["delta_km"].median()),
        "mean_reach_pct_change": float(df["pct_change"].mean()),
    }
    return summary, df.sort_values("delta_km", ascending=True).reset_index(drop=True)
