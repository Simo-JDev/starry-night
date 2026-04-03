import json
import numpy as np
from skyfield.api import Loader, Star, wgs84

_DATA_DIR = "./data"


def load_milky_way():
    with open(f"{_DATA_DIR}/mw.json") as f:
        geojson = json.load(f)

    polygons = []
    for feature in geojson["features"]:
        level = int(feature["properties"]["id"].lstrip("abcdefghijklmnopqrstuvwxyz"))
        for poly in feature["geometry"]["coordinates"]:
            coords = poly[0]  # outer ring of each polygon
            vertices = [(c[0], c[1]) for c in coords]
            polygons.append({"level": level, "vertices": vertices})
    return polygons


def project_milky_way(polygons, lat, lon, year, month, day, hour, minute, earth=None, t=None):
    if earth is None or t is None:
        load = Loader(_DATA_DIR)
        planets = load("de421.bsp")
        ts = load.timescale()
        observer = wgs84.latlon(lat, lon)
        t = ts.utc(year, month, day, hour, minute)
        earth = planets["earth"] + observer

    counts = [len(poly["vertices"]) for poly in polygons]
    if not counts:
        return []

    all_vertices = [vertex for poly in polygons for vertex in poly["vertices"]]
    ra_hours = np.array([ra for ra, _ in all_vertices], dtype=float) / 15.0
    dec_degrees = np.array([dec for _, dec in all_vertices], dtype=float)

    stars = Star(ra_hours=ra_hours, dec_degrees=dec_degrees)
    alt, az, _ = earth.at(t).observe(stars).apparent().altaz()
    alt_d = np.asarray(alt.degrees)
    az_d = np.asarray(az.degrees)

    result = []
    start = 0
    for poly, count in zip(polygons, counts):
        end = start + count
        projected = list(zip(alt_d[start:end].tolist(), az_d[start:end].tolist()))
        result.append({"level": poly["level"], "vertices": projected})
        start = end

    return result
