"""
Figures: tract access and deserts, income, metro network, corridor maps, metrics, report table.
"""

from __future__ import annotations

import geopandas as gpd
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import config


def setup_style():
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans", "Helvetica"],
            "axes.facecolor": "#fafafa",
            "figure.facecolor": "white",
            "axes.edgecolor": "#333333",
            "axes.linewidth": 0.8,
            "axes.titlesize": 13,
            "axes.titleweight": "600",
            "axes.labelsize": 10.5,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.frameon": True,
            "legend.framealpha": 0.95,
            "legend.edgecolor": "#cccccc",
        }
    )


def _extent(ax):
    b = config.LA_BBOX
    ax.set_xlim(b["min_lon"], b["max_lon"])
    ax.set_ylim(b["min_lat"], b["max_lat"])
    ax.set_aspect("equal")


def figure_accessibility_deserts(gdf: gpd.GeoDataFrame, path):
    setup_style()
    g = gdf.to_crs(config.GEO_CRS)
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 7.2), gridspec_kw={"wspace": 0.22})

    acc = g["accessibility_jobs"].astype(float)
    vmin, vmax = 0.0, float(np.nanpercentile(acc, 97))
    g.plot(
        ax=axes[0],
        column="accessibility_jobs",
        cmap="YlGnBu",
        edgecolor="white",
        linewidth=0.25,
        legend=True,
        vmin=vmin,
        vmax=vmax,
        legend_kwds={"shrink": 0.65, "label": "Jobs reachable (30 min)", "aspect": 24},
    )
    axes[0].set_title("Job access by transit (30 min)")
    axes[0].axis("off")
    _extent(axes[0])

    g.plot(
        ax=axes[1],
        column="transit_desert",
        cmap="RdYlBu_r",
        edgecolor="white",
        linewidth=0.25,
        legend=True,
        legend_kwds={"title": "Transit desert"},
    )
    axes[1].set_title(f"Transit deserts (bottom {config.DESERT_PERCENTILE}%)")
    axes[1].axis("off")
    _extent(axes[1])

    fig.suptitle("Los Angeles County — transit and jobs", fontsize=15, fontweight="600", y=1.02)
    plt.savefig(path, facecolor="white")
    plt.close()


def figure_income_access(gdf: gpd.GeoDataFrame, path):
    setup_style()
    sub = gdf.dropna(subset=["median_income", "accessibility_jobs"]).copy()
    if len(sub) < 20:
        return
    fig, ax = plt.subplots(figsize=(9.2, 6.2))
    inc_k = sub["median_income"].astype(float) / 1000.0
    acc_k = sub["accessibility_jobs"].astype(float) / 1000.0
    desert = sub["transit_desert"].values
    ax.scatter(
        inc_k,
        acc_k,
        c=np.where(desert, "#e11d48", "#0ea5e9"),
        s=24,
        alpha=0.5,
        edgecolors="white",
        linewidths=0.25,
    )
    ax.set_xlabel("Median household income ($1,000s)")
    ax.set_ylabel("Jobs reachable in 30 min (thousands)")
    ax.set_title("Income vs. job access by tract")
    leg = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#0ea5e9", markersize=8, label="Other", linestyle=""),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#e11d48", markersize=8, label="Transit desert", linestyle=""),
    ]
    ax.legend(handles=leg, loc="lower right", frameon=True)
    ax.grid(True, alpha=0.35, linestyle="--", linewidth=0.6)
    plt.tight_layout()
    plt.savefig(path, facecolor="white")
    plt.close()


def figure_metro_network(G: nx.Graph, stations_w: pd.DataFrame, path, max_edges: int = 2500):
    setup_style()
    stations_w = stations_w[stations_w["node_id"].isin(G.nodes)].copy()
    pos = {r["node_id"]: (r["lon"], r["lat"]) for _, r in stations_w.iterrows()}
    w = stations_w.set_index("node_id")["weight"].astype(float)
    wvals = np.array([w.get(n, 1.0) for n in pos])
    s_node = 14 + 58 * (np.log1p(wvals) - np.log1p(wvals.min())) / max(np.ptp(np.log1p(wvals)), 1e-9)

    fig, ax = plt.subplots(figsize=(11.5, 10))
    b = config.LA_BBOX
    ax.set_facecolor("#f1f5f9")

    drawn = 0
    for u, v in G.edges():
        if drawn >= max_edges:
            break
        if u in pos and v in pos:
            ax.plot(
                [pos[u][0], pos[v][0]],
                [pos[u][1], pos[v][1]],
                color="#94a3b8",
                alpha=0.45,
                linewidth=0.9,
                zorder=1,
            )
            drawn += 1

    sc = ax.scatter(
        [pos[n][0] for n in pos],
        [pos[n][1] for n in pos],
        s=s_node,
        c=np.log1p(wvals),
        cmap="viridis",
        alpha=0.9,
        edgecolors="#0f172a",
        linewidths=0.4,
        zorder=2,
    )
    cb = plt.colorbar(sc, ax=ax, shrink=0.7, pad=0.02)
    cb.set_label("log(1 + demand near station)")

    ax.set_xlim(b["min_lon"], b["max_lon"])
    ax.set_ylim(b["min_lat"], b["max_lat"])
    ax.set_aspect("equal")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Metro rail network — node size ∝ local demand (pop × jobs, 800 m)", fontweight="600")
    plt.tight_layout()
    plt.savefig(path, facecolor="white")
    plt.close()


def figure_corridor_map(
    gdf: gpd.GeoDataFrame,
    G: nx.Graph,
    stations_w: pd.DataFrame,
    cors: pd.DataFrame,
    path,
):
    n_show = getattr(config, "CORRIDOR_VIZ_TOP_N", 8)
    if cors is None or len(cors) == 0:
        return
    top = cors.head(n_show).reset_index(drop=True)
    g = gdf.to_crs(config.GEO_CRS)
    stations_w = stations_w[stations_w["node_id"].isin(G.nodes)].copy()
    pos = {r["node_id"]: (r["lon"], r["lat"]) for _, r in stations_w.iterrows()}

    fig, ax = plt.subplots(figsize=(14, 12))
    ax.set_facecolor("#0b1220")

    acc = g["accessibility_jobs"].astype(float)
    vmax = float(np.nanpercentile(acc, 95))
    g.plot(
        ax=ax,
        column="accessibility_jobs",
        cmap="cividis",
        edgecolor="#1e293b",
        linewidth=0.15,
        alpha=0.85,
        vmin=0,
        vmax=vmax,
        legend=False,
    )

    for u, v in list(G.edges())[:3000]:
        if u in pos and v in pos:
            ax.plot(
                [pos[u][0], pos[v][0]],
                [pos[u][1], pos[v][1]],
                color="#334155",
                alpha=0.25,
                linewidth=0.6,
                zorder=2,
            )

    scores = top["impact_score"].values.astype(float)
    smin, smax = float(np.nanmin(scores)), float(np.nanmax(scores))
    if smax <= smin:
        smax = smin + 1.0
    norm = Normalize(vmin=smin, vmax=smax)
    cmap = plt.cm.plasma

    for i, (_, r) in enumerate(top.iterrows()):
        c = cmap(norm(float(r["impact_score"])))
        x1, y1 = float(r["lon_a"]), float(r["lat_a"])
        x2, y2 = float(r["lon_b"]), float(r["lat_b"])
        line, = ax.plot(
            [x1, x2],
            [y1, y2],
            color=c,
            linewidth=5.5,
            solid_capstyle="round",
            zorder=5,
            alpha=0.95,
        )
        line.set_path_effects([pe.Stroke(linewidth=9, foreground="#0f172a", alpha=0.85), pe.Normal()])
        ax.scatter([x1, x2], [y1, y2], s=120, c=[c, c], zorder=6, edgecolors="white", linewidths=1.2)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.annotate(
            str(i + 1),
            (mx, my),
            fontsize=11,
            fontweight="700",
            color="white",
            ha="center",
            va="center",
            zorder=7,
            path_effects=[pe.withStroke(linewidth=3, foreground="#0f172a")],
        )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.55, pad=0.02, aspect=28)
    cbar.set_label("Impact = demand × effective resistance", color="white", fontsize=10)
    cbar.ax.tick_params(colors="white")
    cbar.outline.set_edgecolor("white")
    ax.tick_params(colors="white", labelsize=9)
    ax.set_xlabel("Longitude", color="white")
    ax.set_ylabel("Latitude", color="white")
    ax.set_title(
        "Top candidate corridors (ranked)\n"
        "Score = endpoint demand × R_eff (how weakly the network connects these stations today)",
        color="white",
        fontsize=12,
        fontweight="600",
        pad=12,
    )
    _extent(ax)
    plt.tight_layout()
    plt.savefig(path, facecolor="#0b1220")
    plt.close()


def figure_corridor_metrics(cors: pd.DataFrame, path, n: int | None = None):
    n = n or getattr(config, "CORRIDOR_VIZ_TOP_N", 8)
    if cors is None or len(cors) == 0:
        return
    top = cors.head(n).reset_index(drop=True)
    setup_style()

    def nz(x):
        m = float(np.nanmax(x)) or 1.0
        return np.asarray(x, dtype=float) / m

    d = nz(top["demand_proxy"].values)
    r = nz(top["effective_resistance"].values)
    im = nz(top["impact_score"].values)

    fig, ax = plt.subplots(figsize=(11, max(5.0, 0.55 * len(top))))
    y = np.arange(len(top))[::-1]
    h = 0.22
    ax.barh(y - h, d, height=h * 0.9, color="#3b82f6", label="Demand (norm.)", alpha=0.92, edgecolor="white", linewidth=0.5)
    ax.barh(y, r, height=h * 0.9, color="#a855f7", label="R_eff (norm.)", alpha=0.92, edgecolor="white", linewidth=0.5)
    ax.barh(y + h, im, height=h * 0.9, color="#f43f5e", label="Demand×R_eff (norm.)", alpha=0.92, edgecolor="white", linewidth=0.5)

    labs = []
    for _, row in top.iterrows():
        a = str(row["station_a"]).split("::")[-1][:8]
        b = str(row["station_b"]).split("::")[-1][:8]
        labs.append(f"{a}–{b}")

    ax.set_yticks(y)
    ax.set_yticklabels(labs, fontsize=9)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Normalized (each column scaled to its own max)")
    ax.set_title("Same candidates — demand, R_eff, and their product (each scaled 0–1 within column)", fontweight="600", fontsize=12)
    ax.legend(loc="lower right", ncol=3, fontsize=9)
    ax.grid(True, axis="x", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(path, facecolor="white")
    plt.close()


def _stop_display_name(node_id: str, name_by_id: dict, max_len: int = 38) -> str:
    raw = name_by_id.get(node_id)
    if raw is None or (isinstance(raw, float) and np.isnan(raw)) or str(raw).strip() == "":
        return str(node_id).split("::")[-1][:max_len]
    s = str(raw).strip().replace("\n", " ")
    return (s[: max_len - 1] + "…") if len(s) > max_len else s


def figure_corridors_on_deserts(
    gdf: gpd.GeoDataFrame,
    cors: pd.DataFrame,
    path,
):
    n = getattr(config, "CORRIDOR_REPORT_TOP_N", 5)
    if cors is None or len(cors) == 0:
        return
    top = cors.head(n).reset_index(drop=True)
    setup_style()
    g = gdf.to_crs(config.GEO_CRS)
    fig, ax = plt.subplots(figsize=(12.5, 10))
    ax.set_facecolor("#f1f5f9")

    g_other = g[~g["transit_desert"]]
    g_other.plot(ax=ax, color="#e2e8f0", edgecolor="white", linewidth=0.2, zorder=1)
    g_des = g[g["transit_desert"]]
    g_des.plot(
        ax=ax,
        color="#fecdd3",
        edgecolor="#e11d48",
        linewidth=0.35,
        hatch="///",
        alpha=0.75,
        zorder=2,
    )

    scores = top["impact_score"].values.astype(float)
    smin, smax = float(np.nanmin(scores)), float(np.nanmax(scores))
    if smax <= smin:
        smax = smin + 1.0
    norm = Normalize(vmin=smin, vmax=smax)
    cmap = plt.cm.plasma

    for i, (_, r) in enumerate(top.iterrows()):
        c = cmap(norm(float(r["impact_score"])))
        x1, y1 = float(r["lon_a"]), float(r["lat_a"])
        x2, y2 = float(r["lon_b"]), float(r["lat_b"])
        line, = ax.plot(
            [x1, x2],
            [y1, y2],
            color=c,
            linewidth=5.0,
            solid_capstyle="round",
            zorder=5,
            alpha=0.95,
        )
        line.set_path_effects([pe.Stroke(linewidth=8, foreground="#1e293b", alpha=0.7), pe.Normal()])
        ax.scatter([x1, x2], [y1, y2], s=95, c=[c, c], zorder=6, edgecolors="white", linewidths=1.0)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.annotate(
            str(i + 1),
            (mx, my),
            fontsize=11,
            fontweight="700",
            color="white",
            ha="center",
            va="center",
            zorder=7,
            path_effects=[pe.withStroke(linewidth=2.5, foreground="#0f172a")],
        )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.72, pad=0.02)
    cbar.set_label("Impact (demand × R_eff)")

    leg = [
        Patch(facecolor="#e2e8f0", edgecolor="white", linewidth=0.5, label="Other tracts"),
        Patch(
            facecolor="#fecdd3",
            edgecolor="#e11d48",
            linewidth=0.5,
            hatch="///",
            label=f"Transit desert (bottom {config.DESERT_PERCENTILE}%)",
        ),
    ]
    ax.legend(handles=leg, loc="lower left", framealpha=0.95, fontsize=9)
    ax.set_title(
        f"Top {n} corridor candidates on transit deserts\n"
        "Deserts hatched; corridor colors by impact (same ranking as main analysis)",
        fontweight="600",
        fontsize=12,
    )
    ax.axis("off")
    _extent(ax)
    plt.tight_layout()
    plt.savefig(path, facecolor="white")
    plt.close()


def figure_corridor_results_table(
    cors: pd.DataFrame,
    station_nodes: pd.DataFrame,
    path,
):
    n = getattr(config, "CORRIDOR_REPORT_TOP_N", 5)
    if cors is None or len(cors) == 0:
        return
    top = cors.head(n).reset_index(drop=True)
    setup_style()
    name_by = station_nodes.set_index("node_id")["stop_name"].to_dict()

    headers = ["Rank", "Station A", "Station B", "Length (km)", "Demand", "R_eff", "Impact"]
    cell_text = []
    for i, r in top.iterrows():
        cell_text.append(
            [
                str(i + 1),
                _stop_display_name(str(r["station_a"]), name_by),
                _stop_display_name(str(r["station_b"]), name_by),
                f"{float(r['euclidean_km']):.2f}",
                f"{float(r['demand_proxy']):.3e}",
                f"{float(r['effective_resistance']):.1f}",
                f"{float(r['impact_score']):.3e}",
            ]
        )

    fig_w = 16.0
    fig_h = 1.0 + 0.55 * len(top)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    table = ax.table(
        cellText=cell_text,
        colLabels=headers,
        loc="center",
        cellLoc="left",
        colLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.05, 1.35)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#cbd5e1")
        cell.set_facecolor("#f8fafc" if row == 0 else "white")
        if row == 0:
            cell.set_text_props(fontweight="600", fontsize=10)
            cell.set_facecolor("#e2e8f0")
    fig.suptitle("Top corridor candidates (report summary)", fontsize=13, fontweight="600", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(path, facecolor="white")
    plt.close()


def figure_dline_network_impact(
    G_before: nx.Graph,
    G_after: nx.Graph,
    station_nodes_before: pd.DataFrame,
    station_nodes_after: pd.DataFrame,
    ext_edges: pd.DataFrame,
    impact_summary: dict,
    path,
):
    setup_style()
    pos_b = station_nodes_before.set_index("node_id")[["lon", "lat"]].to_dict("index")
    pos_a = station_nodes_after.set_index("node_id")[["lon", "lat"]].to_dict("index")
    fig, axes = plt.subplots(1, 2, figsize=(15.8, 7.8), gridspec_kw={"wspace": 0.08})
    for ax in axes:
        ax.set_facecolor("#f8fafc")
        ax.axis("off")
        _extent(ax)
    for u, v in list(G_before.edges()):
        if u in pos_b and v in pos_b:
            axes[0].plot(
                [pos_b[u]["lon"], pos_b[v]["lon"]],
                [pos_b[u]["lat"], pos_b[v]["lat"]],
                color="#94a3b8",
                linewidth=1.0,
                alpha=0.55,
                zorder=1,
            )
    for u, v in list(G_after.edges()):
        if u in pos_a and v in pos_a:
            axes[1].plot(
                [pos_a[u]["lon"], pos_a[v]["lon"]],
                [pos_a[u]["lat"], pos_a[v]["lat"]],
                color="#94a3b8",
                linewidth=1.0,
                alpha=0.4,
                zorder=1,
            )
    if ext_edges is not None and len(ext_edges) > 0:
        for _, r in ext_edges.iterrows():
            c = "#be123c" if str(r.get("kind", "")) == "extension" else "#f97316"
            lw = 4.2 if str(r.get("kind", "")) == "extension" else 2.2
            axes[1].plot(
                [float(r["lon_u"]), float(r["lon_v"])],
                [float(r["lat_u"]), float(r["lat_v"])],
                color=c,
                linewidth=lw,
                alpha=0.95,
                zorder=3,
                solid_capstyle="round",
            )
    axes[0].set_title("Baseline rail graph", fontsize=12, fontweight="600")
    axes[1].set_title("With D Line extension scenario", fontsize=12, fontweight="600")
    if impact_summary:
        txt = (
            f"Compared pairs: {impact_summary.get('pair_count', 0)}\n"
            f"Mean R_eff change: {impact_summary.get('mean_r_eff_pct_change', np.nan):.2f}%\n"
            f"Median R_eff change: {impact_summary.get('median_r_eff_pct_change', np.nan):.2f}%\n"
            f"Mean shortest-path change: {impact_summary.get('mean_sp_pct_change', np.nan):.2f}%"
        )
        axes[1].text(
            0.02,
            0.03,
            txt,
            transform=axes[1].transAxes,
            fontsize=9.5,
            ha="left",
            va="bottom",
            bbox=dict(facecolor="white", edgecolor="#cbd5e1", alpha=0.97, boxstyle="round,pad=0.45"),
        )
    fig.suptitle("Project 28 D Line extension: network-level impact", fontsize=14, fontweight="700", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(path, facecolor="white")
    plt.close()


def figure_dline_top_pair_gains(pair_df: pd.DataFrame, station_nodes: pd.DataFrame, path, top_n: int = 10):
    if pair_df is None or len(pair_df) == 0:
        return
    setup_style()
    name_by = station_nodes.set_index("node_id")["stop_name"].to_dict()
    best = pair_df.nsmallest(top_n, "r_eff_pct_change").copy().reset_index(drop=True)
    labels = []
    for _, r in best.iterrows():
        a = _stop_display_name(str(r["station_a"]), name_by, max_len=20)
        b = _stop_display_name(str(r["station_b"]), name_by, max_len=20)
        labels.append(f"{a} -> {b}")
    y = np.arange(len(best))[::-1]
    vals = best["r_eff_pct_change"].values.astype(float)
    fig, ax = plt.subplots(figsize=(12.2, max(5.2, 0.48 * len(best) + 2.0)))
    ax.barh(y, vals, color="#be123c", alpha=0.9, edgecolor="white", linewidth=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.axvline(0, color="#334155", linewidth=1.0)
    ax.set_xlabel("Effective resistance % change after extension (negative = improvement)")
    ax.set_title("OD pairs with largest connectivity gains from D Line extension", fontsize=12, fontweight="600")
    ax.grid(True, axis="x", alpha=0.3, linestyle="--", linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(path, facecolor="white")
    plt.close()


def figure_dline_reach_gain_report(
    reach_df: pd.DataFrame,
    station_nodes: pd.DataFrame,
    ext_edges: pd.DataFrame,
    reach_summary: dict,
    path,
    top_n: int = 12,
):
    if reach_df is None or len(reach_df) == 0:
        return
    setup_style()
    nodes = station_nodes.copy()
    nodes = nodes[nodes["node_id"].isin(reach_df["node_id"])].copy()
    merged = nodes.merge(reach_df, on="node_id", how="inner")
    fig, axes = plt.subplots(1, 2, figsize=(16.2, 8.0), gridspec_kw={"width_ratios": [1.15, 1.0], "wspace": 0.12})
    axm, axb = axes
    axm.set_facecolor("#f8fafc")
    _extent(axm)
    axm.axis("off")
    pos = nodes.set_index("node_id")[["lon", "lat"]].to_dict("index")
    for _, r in ext_edges.iterrows():
        c = "#be123c" if str(r.get("kind", "")) == "extension" else "#f97316"
        lw = 4.0 if str(r.get("kind", "")) == "extension" else 2.1
        axm.plot(
            [float(r["lon_u"]), float(r["lon_v"])],
            [float(r["lat_u"]), float(r["lat_v"])],
            color=c,
            linewidth=lw,
            alpha=0.95,
            zorder=4,
            solid_capstyle="round",
        )
    gain = -merged["delta_km"].values.astype(float)
    gain_span = float(np.nanmax(gain) - np.nanmin(gain)) if len(gain) else 0.0
    size = 26 + 320 * (gain - np.nanmin(gain)) / max(gain_span, 1e-9)
    sc = axm.scatter(
        merged["lon"].values,
        merged["lat"].values,
        s=size,
        c=gain,
        cmap="YlOrRd",
        edgecolors="#334155",
        linewidths=0.45,
        alpha=0.9,
        zorder=5,
    )
    cb = plt.colorbar(sc, ax=axm, shrink=0.72, pad=0.015)
    cb.set_label("Mean network reach gain to D Line stations (km)")
    axm.set_title("Spatial footprint of D Line reach gains", fontsize=12, fontweight="600")
    top = reach_df.nsmallest(top_n, "delta_km").copy().reset_index(drop=True)
    name_by = station_nodes.set_index("node_id")["stop_name"].to_dict()
    labels = [_stop_display_name(str(n), name_by, max_len=24) for n in top["node_id"]]
    y = np.arange(len(top))[::-1]
    vals = -top["delta_km"].values.astype(float)
    axb.barh(y, vals, color="#be123c", edgecolor="white", linewidth=0.7, alpha=0.92)
    axb.set_yticks(y)
    axb.set_yticklabels(labels, fontsize=9)
    axb.set_xlabel("Reduction in mean shortest-path distance to extension stations (km)")
    axb.set_title(f"Top {top_n} stations with largest gains", fontsize=12, fontweight="600")
    axb.grid(True, axis="x", alpha=0.3, linestyle="--", linewidth=0.6)
    axb.spines["top"].set_visible(False)
    axb.spines["right"].set_visible(False)
    if reach_summary:
        txt = (
            f"Stations compared: {reach_summary.get('station_count', 0)}\n"
            f"Mean gain: {-reach_summary.get('mean_reach_delta_km', np.nan):.2f} km\n"
            f"Median gain: {-reach_summary.get('median_reach_delta_km', np.nan):.2f} km\n"
            f"Mean % change: {-reach_summary.get('mean_reach_pct_change', np.nan):.1f}%"
        )
        axb.text(
            0.98,
            0.03,
            txt,
            transform=axb.transAxes,
            ha="right",
            va="bottom",
            fontsize=9.5,
            bbox=dict(facecolor="white", edgecolor="#cbd5e1", alpha=0.98, boxstyle="round,pad=0.45"),
        )
    fig.suptitle("Project 28 D Line extension impact: network reach improvement", fontsize=14, fontweight="700", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(path, facecolor="white")
    plt.close()
