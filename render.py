import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath
from matplotlib.font_manager import FontProperties
from pathlib import Path

# --- Figure / layout constants ---
FIG_SIZE = (10, 10)
FIG_DPI = 600
BASE_BG_COLOR = "#191f39"
FIG_BG_COLOR = BASE_BG_COLOR
MAP_BG_COLOR = BASE_BG_COLOR
MAP_POS = [0.2187, 0.2187, 0.5626, 0.5626]
RING_LIMIT = 1.5
MAP_RADIUS = 1.0

# --- Colors ---
WHITE = "white"

# --- Ring geometry / style ---
RING_HORIZON_RADIUS = 1.0
RING_HORIZON_LINEWIDTH = 5
RING_GUIDE_RADIUS = 1.21
RING_GUIDE_LINEWIDTH = 0.6
RING_TICK_RADIUS_MINOR = 1.05
RING_TICK_RADIUS_MEDIUM = 1.05
RING_TICK_RADIUS_MAJOR = 1.08
RING_TICK_LINEWIDTH_MINOR = 0.4
RING_TICK_LINEWIDTH_MEDIUM = 0.6
RING_TICK_LINEWIDTH_MAJOR = 0.9
RING_MID_TICK_RADIUS = 1.032

# --- Ring labels ---
DEGREE_LABEL_STEP = 15
DEGREE_LABEL_RADIUS = 1.11
DEGREE_LABEL_FONT_SIZE = 9
DEGREE_LABEL_FLIP_FROM = 195
CARDINAL_LABEL_RADIUS = 1.21
CARDINAL_FONT_SIZE = 10
INTERCARDINAL_FONT_SIZE = 10
CARDINAL_LABEL_BBOX_PAD = 0.25
CARDINAL_LABEL_BBOX_COLOR = FIG_BG_COLOR
CARDINAL_LETTER_SPACING = "\u200A"  # hair space for subtle tracking
CARDINALS = {0: "North", 90: "East", 180: "South", 270: "West"}
INTERCARDINALS = {45: "NE", 135: "SE", 225: "SW", 315: "NW"}
UPSIDE_DOWN_CARDINAL_AZ = {225, 270, 315}

# --- Sky rendering ---
ALTITUDE_MAX_DEG = 90.0
HORIZON_ALTITUDE_DEG = 0
MAP_CONTENT_MAX_RADIUS = 0.98
MW_MIN_VISIBLE_RATIO = 0.30
MW_FILL_COLOR = "#ffffff"
CONSTELLATION_LINEWIDTH = 0.5
CONSTELLATION_ALPHA = 0.9
CONSTELLATION_LABEL_FONT_SIZE = 6
CONSTELLATION_LABEL_ALPHA = 0.8
STAR_SIZE_MAG_REF = 7.5
STAR_SIZE_SCALE = 0.2
STAR_SIZE_MIN = 0.01

# --- Border / text ---
FIG_BORDER_POS = (0.03, 0.03)
FIG_BORDER_SIZE = (0.94, 0.94)
FIG_BORDER_LINEWIDTH = 5
TITLE_POS = (0.5, 0.92)
TITLE_FONT_SIZE = 20
NORMAL_FONT_PATH = Path(__file__).resolve().parent / "assets" / "fonts" / "Lato-Regular.ttf"
TITLE_FONT_PATH = Path(__file__).resolve().parent / "assets" / "fonts" / "Lato-Bold.ttf"
SUBTITLE_POS = (0.5, 0.079)
SUBTITLE_FONT_SIZE = 9
SAVE_BBOX_PAD_INCHES = 0.45

NORMAL_FONT_PROPS = FontProperties(fname=str(NORMAL_FONT_PATH)) if NORMAL_FONT_PATH.exists() else None
TITLE_FONT_PROPS = FontProperties(fname=str(TITLE_FONT_PATH)) if TITLE_FONT_PATH.exists() else None


def _to_polar(alt_deg, az_deg):
    r = MAP_CONTENT_MAX_RADIUS * (1.0 - alt_deg / ALTITUDE_MAX_DEG)
    theta = np.radians(az_deg)
    return theta, r


MW_ALPHA = {1: 0.08, 2: 0.12, 3: 0.16, 4: 0.22, 5: 0.30}


def draw_ring(ax_ring):
    def _ring_rad(az_deg):
        # Counterclockwise from North: N at top, E at left.
        return np.radians(-az_deg)

    def _tracked(text):
        return CARDINAL_LETTER_SPACING.join(list(text))

    # Thick horizon circle
    ax_ring.add_patch(
        mpatches.Circle(
            (0, 0),
            RING_HORIZON_RADIUS,
            fill=False,
            edgecolor=WHITE,
            linewidth=RING_HORIZON_LINEWIDTH,
            zorder=5,
        )
    )

    # Thin guide ring just before the horizon.
    ax_ring.add_patch(
        mpatches.Circle(
            (0, 0),
            0.985,
            fill=False,
            edgecolor=HORIZON_GAP_COLOR,
            linewidth=4,
            zorder=20,
        )
    )

    # Thin guide ring just outside the horizon (drawn under ticks and labels).
    ax_ring.add_patch(
        mpatches.Circle(
            (0, 0),
            RING_MID_TICK_RADIUS,
            fill=False,
            edgecolor=WHITE,
            linewidth=RING_GUIDE_LINEWIDTH,
            zorder=6,
        )
    )

    # Thin guide ring through cardinal/intercardinal label radius (drawn under text).
    ax_ring.add_patch(
        mpatches.Circle(
            (0, 0),
            RING_GUIDE_RADIUS,
            fill=False,
            edgecolor=WHITE,
            linewidth=RING_GUIDE_LINEWIDTH,
            zorder=6,
        )
    )

    # Ticks for every degree
    for az in range(360):
        rad = _ring_rad(az)
        if az % 15 == 0:
            r_out, lw = RING_TICK_RADIUS_MAJOR, RING_TICK_LINEWIDTH_MAJOR
        elif az % 5 == 0:
            r_out, lw = RING_TICK_RADIUS_MEDIUM, RING_TICK_LINEWIDTH_MEDIUM
        else:
            r_out, lw = RING_TICK_RADIUS_MINOR, RING_TICK_LINEWIDTH_MINOR
        x1, y1 = np.sin(rad), np.cos(rad)
        x2, y2 = r_out * np.sin(rad), r_out * np.cos(rad)
        ax_ring.plot([x1, x2], [y1, y2], color=WHITE, linewidth=lw, zorder=6)

    # Degree labels at fixed step.
    for az in range(0, 360, DEGREE_LABEL_STEP):
        rad = _ring_rad(az)
        x = DEGREE_LABEL_RADIUS * np.sin(rad)
        y = DEGREE_LABEL_RADIUS * np.cos(rad)
        rotation = az if az <= 180 else az - 180
        if az >= DEGREE_LABEL_FLIP_FROM:
            rotation = (rotation + 180) % 360
        label = "360" if az == 0 else str(az)
        ax_ring.text(x, y, label, fontsize=DEGREE_LABEL_FONT_SIZE, color=WHITE,
                     ha="center", va="center", rotation=rotation, zorder=7)

    # Cardinal and intercardinal labels.
    for az, label in {**CARDINALS, **INTERCARDINALS}.items():
        rad = _ring_rad(az)
        x = CARDINAL_LABEL_RADIUS * np.sin(rad)
        y = CARDINAL_LABEL_RADIUS * np.cos(rad)
        rotation = az if az <= 180 else az - 180
        if az in UPSIDE_DOWN_CARDINAL_AZ:
            rotation = (rotation + 180) % 360
        fontsize = CARDINAL_FONT_SIZE if az in CARDINALS else INTERCARDINAL_FONT_SIZE
        display_label = _tracked(label) if az in CARDINALS else label
        # Knock out the guide ring behind labels so it doesn't run through text.
        ax_ring.text(x, y, display_label, fontsize=fontsize, color=WHITE,
                     ha="center", va="center", rotation=rotation, zorder=7,
                     bbox=dict(
                         boxstyle=f"round,pad={CARDINAL_LABEL_BBOX_PAD}",
                         facecolor=CARDINAL_LABEL_BBOX_COLOR,
                         edgecolor="none",
                     ))


def render_map(
    stars_df,
    milky_way,
    constellation_segments,
    output_file="skymap.png",
    title="",
    subtitle="",
    ring_only=False,
    show_names=False,
    constellation_labels=None,
):
    fig = plt.figure(figsize=FIG_SIZE, dpi=FIG_DPI, facecolor=FIG_BG_COLOR)
    ring_limit = RING_LIMIT
    map_radius = MAP_RADIUS
    ring_scale = ring_limit / map_radius

    # Keep map and ring centered, but give the ring a larger axes box so it wraps the map.
    map_pos = MAP_POS
    cx = map_pos[0] + map_pos[2] / 2
    cy = map_pos[1] + map_pos[3] / 2
    ring_size = map_pos[2] * ring_scale
    ring_pos = [cx - ring_size / 2, cy - ring_size / 2, ring_size, ring_size]

    if not ring_only:
        ax = fig.add_axes(map_pos, projection="polar", facecolor=MAP_BG_COLOR)

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(1)
        ax.axis("off")

        # --- Milky Way ---
        for polygon in milky_way:
            verts = polygon["vertices"]
            above = [(alt, az) for alt, az in verts if alt > HORIZON_ALTITUDE_DEG]
            if len(above) / len(verts) < MW_MIN_VISIBLE_RATIO:
                continue
            thetas = [np.radians(az) for _, az in above]
            rs = [MAP_CONTENT_MAX_RADIUS * (1.0 - (alt / ALTITUDE_MAX_DEG)) for alt, _ in above]
            ax.fill(thetas, rs, color=MW_FILL_COLOR,
                    alpha=MW_ALPHA.get(polygon["level"], 0.06),
                    linewidth=0, zorder=1)

        ax.set_ylim(0, 1.0)

        # --- Constellation lines ---
        for (alt1, az1), (alt2, az2) in constellation_segments:
            t1, r1 = _to_polar(alt1, az1)
            t2, r2 = _to_polar(alt2, az2)
            ax.plot([t1, t2], [r1, r2],
                    color=WHITE, linewidth=CONSTELLATION_LINEWIDTH, alpha=CONSTELLATION_ALPHA,
                    solid_capstyle="round")

        # --- Constellation abbreviations ---
        if show_names and constellation_labels:
            for item in constellation_labels:
                t_lab, r_lab = _to_polar(item["altitude_deg"], item["azimuth_deg"])
                ax.text(
                    t_lab,
                    r_lab,
                    item["id"],
                    color=WHITE,
                    fontsize=CONSTELLATION_LABEL_FONT_SIZE,
                    alpha=CONSTELLATION_LABEL_ALPHA,
                    ha="center",
                    va="center",
                    zorder=2,
                )

        # --- Stars ---
        above = stars_df[stars_df["altitude_deg"] > 0]
        thetas = np.radians(above["azimuth_deg"].values)
        rs = MAP_CONTENT_MAX_RADIUS * (1.0 - above["altitude_deg"].values / ALTITUDE_MAX_DEG)
        # Keep star size monotonic with magnitude: dimmer stars should not become larger.
        brightness = np.clip(STAR_SIZE_MAG_REF - above["magnitude"].values, 0, None)
        sizes = np.clip((brightness ** 2) * STAR_SIZE_SCALE, STAR_SIZE_MIN, None)

        ax.scatter(thetas, rs, s=sizes, color=WHITE, linewidths=0, zorder=3)

    # --- Compass ring (drawn last so it stays above map layers) ---
    ax_ring = fig.add_axes(ring_pos, frameon=False)
    ax_ring.set_zorder(20)
    ax_ring.set_xlim(-ring_limit, ring_limit)
    ax_ring.set_ylim(-ring_limit, ring_limit)
    ax_ring.set_aspect("equal")
    ax_ring.axis("off")
    ax_ring.patch.set_visible(False)
    draw_ring(ax_ring)

    # --- Figure border ---
    fig.patches.append(mpatches.Rectangle(
        FIG_BORDER_POS, *FIG_BORDER_SIZE,
        transform=fig.transFigure,
        fill=False, edgecolor=WHITE, linewidth=FIG_BORDER_LINEWIDTH, zorder=10,
    ))

    # --- Title and subtitle ---
    if title:
        title_text_kwargs = {}
        if TITLE_FONT_PROPS is not None:
            title_text_kwargs["fontproperties"] = TITLE_FONT_PROPS
        else:
            title_text_kwargs["fontweight"] = "bold"
        fig.text(*TITLE_POS, title,
                 ha="center", va="top",
                 fontsize=TITLE_FONT_SIZE, color=WHITE,
                 **title_text_kwargs)
    if subtitle:
        subtitle_text_kwargs = {}
        if NORMAL_FONT_PROPS is not None:
            subtitle_text_kwargs["fontproperties"] = NORMAL_FONT_PROPS
        subtitle = subtitle.replace('\\n', '\n')
        fig.text(*SUBTITLE_POS, subtitle,
                 ha="center", va="bottom",
                 fontsize=SUBTITLE_FONT_SIZE, color=WHITE, multialignment="center",
                 **subtitle_text_kwargs)

    fig.savefig(
        output_file,
        dpi=FIG_DPI,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=SAVE_BBOX_PAD_INCHES,
    )
    plt.close(fig)
HORIZON_GAP_COLOR = BASE_BG_COLOR
