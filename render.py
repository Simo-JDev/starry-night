import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath
from matplotlib.patches import Polygon as MplPolygon

BV_COLOURS = [
    (float("-inf"), 0.0,  "#aabfff"),
    (0.0,           0.5,  "#ffffff"),
    (0.5,           1.0,  "#ffe9c4"),
    (1.0,           float("inf"), "#ffcc6f"),
]


def _bv_colour(bv):
    if bv != bv:  # NaN
        return "#ffffff"
    for lo, hi, colour in BV_COLOURS:
        if lo <= bv < hi:
            return colour
    return "#ffcc6f"


def _to_polar(alt_deg, az_deg):
    r = 1.0 - alt_deg / 90.0
    theta = np.radians(az_deg)
    return theta, r


MW_ALPHA = {1: 0.03, 2: 0.06, 3: 0.09, 4: 0.13, 5: 0.18}


def render_map(stars_df, milky_way, constellation_segments, output_file="skymap.png"):
    fig = plt.figure(figsize=(10, 10), dpi=300, facecolor="#05071a")
    ax = fig.add_axes([0, 0, 1, 1], projection="polar", facecolor="#05071a")

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Clip path — unit circle in data coordinates
    clip_circle = mpatches.Circle(
        (0.5, 0.5), 0.5,
        transform=ax.transAxes,
        facecolor="none",
        edgecolor="none",
    )
    ax.add_patch(clip_circle)

    # --- Milky Way ---
    for polygon in milky_way:
        verts_above = [(alt, az) for alt, az in polygon["vertices"] if alt > 0]
        if len(verts_above) < 3:
            continue
        polar_verts = [_to_polar(alt, az) for alt, az in verts_above]
        # Convert polar (theta, r) to cartesian for Polygon artist on polar axes
        xs = [r * np.cos(theta) for theta, r in polar_verts]
        ys = [r * np.sin(theta) for theta, r in polar_verts]
        # Polar axes use theta/r directly via fill
        thetas = [t for t, _ in polar_verts]
        rs = [r for _, r in polar_verts]
        patch = ax.fill(thetas, rs,
                        color="#ccd9ff",
                        alpha=MW_ALPHA.get(polygon["level"], 0.06),
                        linewidth=0)[0]
        patch.set_clip_path(clip_circle)

    # --- Constellation lines ---
    for (alt1, az1), (alt2, az2) in constellation_segments:
        if alt1 <= 0 or alt2 <= 0:
            continue
        t1, r1 = _to_polar(alt1, az1)
        t2, r2 = _to_polar(alt2, az2)
        line, = ax.plot([t1, t2], [r1, r2],
                        color="#444466", linewidth=0.4, alpha=0.4,
                        solid_capstyle="round")
        line.set_clip_path(clip_circle)

    # --- Stars ---
    above = stars_df[stars_df["altitude_deg"] > 0]
    thetas = np.radians(above["azimuth_deg"].values)
    rs = 1.0 - above["altitude_deg"].values / 90.0
    sizes = np.clip((6.5 - above["magnitude"].values) ** 2 * 1.5, 0.5, None)
    colours = [_bv_colour(bv) for bv in above["bv"].values]

    sc = ax.scatter(thetas, rs, s=sizes, c=colours, linewidths=0, zorder=3)
    sc.set_clip_path(clip_circle)

    # --- Border ring ---
    ring_theta = np.linspace(0, 2 * np.pi, 360)
    ring_r = np.ones(360)
    border, = ax.plot(ring_theta, ring_r, color="#334", linewidth=1.5, zorder=4)
    border.set_clip_path(clip_circle)

    fig.savefig(output_file, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
