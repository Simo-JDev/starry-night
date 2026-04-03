from skyfield.api import Loader, wgs84

from constellations import load_constellation_lines, project_constellations
from milkyway import load_milky_way, project_milky_way
from stars import load_stars, compute_star_positions

_DATA_DIR = "./data"


def build_skymap_data(lat, lon, year, month, day, hour, minute, mag=6.5, ring_only=False, show_names=False):
    stars_df = None
    mw_projected = None
    segments_projected = None
    constellation_labels = None

    if ring_only:
        return stars_df, mw_projected, segments_projected, constellation_labels

    load = Loader(_DATA_DIR)
    planets = load("de421.bsp")
    ts = load.timescale()
    observer = wgs84.latlon(lat, lon)
    t_skyfield = ts.utc(year, month, day, hour, minute)
    earth = planets["earth"] + observer

    df = load_stars(magnitude_limit=mag)
    stars_df = compute_star_positions(df, lat, lon, year, month, day, hour, minute, earth=earth, t=t_skyfield)

    mw_polygons = load_milky_way()
    mw_projected = project_milky_way(
        mw_polygons, lat, lon, year, month, day, hour, minute, earth=earth, t=t_skyfield
    )

    segments, label_points = load_constellation_lines()
    segments_projected, constellation_labels = project_constellations(
        segments,
        lat,
        lon,
        year,
        month,
        day,
        hour,
        minute,
        earth=earth,
        t=t_skyfield,
        show_names=show_names,
        label_points=label_points,
    )

    return stars_df, mw_projected, segments_projected, constellation_labels
