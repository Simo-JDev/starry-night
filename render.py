import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath


def _to_polar(alt_deg, az_deg):
    r = 1.0 - alt_deg / 90.0
    theta = np.radians(az_deg)
    return theta, r


MW_ALPHA = {1: 0.08, 2: 0.14, 3: 0.20, 4: 0.28, 5: 0.40}


def render_map(stars_df, milky_way, constellation_segments, output_file="skymap.png", title="", subtitle=""):
    fig = plt.figure(figsize=(10, 10), dpi=300, facecolor="#3d4460")
    ax = fig.add_axes([0.20, 0.10, 0.60, 0.60], projection="polar", facecolor="#2e3552")

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(1)
    ax.axis("off")

    # --- Milky Way ---
    for polygon in milky_way:
        thetas = [np.radians(az) for _, az in polygon["vertices"]]
        rs = [1.0 - (alt / 90.0) for alt, _ in polygon["vertices"]]
        ax.fill(thetas, rs, color="#ffffff",
                alpha=MW_ALPHA.get(polygon["level"], 0.06),
                linewidth=0, zorder=1)

    ax.set_ylim(0, 1.0)

    # --- Constellation lines ---
    for (alt1, az1), (alt2, az2) in constellation_segments:
        t1, r1 = _to_polar(alt1, az1)
        t2, r2 = _to_polar(alt2, az2)
        ax.plot([t1, t2], [r1, r2],
                color="white", linewidth=1.2, alpha=0.9,
                solid_capstyle="round")

    # --- Stars ---
    above = stars_df[stars_df["altitude_deg"] > 0]
    thetas = np.radians(above["azimuth_deg"].values)
    rs = 1.0 - above["altitude_deg"].values / 90.0
    sizes = np.clip((6.5 - above["magnitude"].values) ** 2 * 1.5, 0.5, None)

    ax.scatter(thetas, rs, s=sizes, color="white", linewidths=0, zorder=3)

    # --- Tick ring: filled annulus between horizon (r=1.0) and outer edge (r=1.18) ---
    ring_theta = np.linspace(0, 2 * np.pi, 720)
    ax.fill_between(ring_theta, 1.0, 1.18, color="#4a5070", zorder=3)

    # Inner horizon circle
    ax.plot(ring_theta, np.ones(720), color="white", linewidth=1.5, zorder=4)

    # Ticks inside the band
    for az in range(360):
        theta = np.radians(az)
        if az % 15 == 0:
            ax.plot([theta, theta], [1.0, 1.10], color="white", linewidth=0.8, zorder=5)
        elif az % 5 == 0:
            ax.plot([theta, theta], [1.0, 1.07], color="white", linewidth=0.6, zorder=5)
        else:
            ax.plot([theta, theta], [1.0, 1.04], color="white", linewidth=0.4, zorder=5)

    # Degree labels at every 15°, inside the band at r=1.13
    for az in range(0, 360, 15):
        theta = np.radians(az)
        rotation = az - 90 if az <= 180 else az + 90
        ax.text(theta, 1.13, f"{az}°",
                ha="center", va="center",
                fontsize=6, color="white",
                rotation=rotation, rotation_mode="anchor",
                zorder=6)

    # Outer boundary circle at r=1.18
    ax.plot(ring_theta, np.full(720, 1.18), color="white", linewidth=1, zorder=4)

    # Cardinal and intercardinal labels just outside r=1.18
    cardinals = {0: "North", 90: "East", 180: "South", 270: "West"}
    intercardinals = {45: "NE", 135: "SE", 225: "SW", 315: "NW"}
    for az, label in cardinals.items():
        theta = np.radians(az)
        rotation = az - 90 if az <= 180 else az + 90
        ax.text(theta, 1.26, label,
                ha="center", va="center",
                fontsize=8, color="white",
                rotation=rotation, rotation_mode="anchor",
                zorder=6)
    for az, label in intercardinals.items():
        theta = np.radians(az)
        rotation = az - 90 if az <= 180 else az + 90
        ax.text(theta, 1.26, label,
                ha="center", va="center",
                fontsize=7, color="white",
                rotation=rotation, rotation_mode="anchor",
                zorder=6)

    # --- Figure border ---
    fig.patches.append(mpatches.Rectangle(
        (0.02, 0.02), 0.96, 0.96,
        transform=fig.transFigure,
        fill=False, edgecolor="white", linewidth=1, zorder=10,
    ))

    # --- Title and subtitle ---
    if title:
        fig.text(0.5, 0.88, title,
                 ha="center", va="top",
                 fontsize=28, color="white", fontweight="bold")
    if subtitle:
        subtitle = subtitle.replace('\\n', '\n')
        fig.text(0.5, 0.03, subtitle,
                 ha="center", va="bottom",
                 fontsize=10, color="white", multialignment="center")

    fig.savefig(output_file, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
