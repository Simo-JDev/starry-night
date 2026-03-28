import json
from skyfield.api import Loader, Star, wgs84
from skyfield.positionlib import position_of_radec

_DATA_DIR = "./data"


def load_milky_way():
    with open(f"{_DATA_DIR}/mw.json") as f:
        geojson = json.load(f)

    polygons = []
    for feature in geojson["features"]:
        level = int(feature["id"].lstrip("abcdefghijklmnopqrstuvwxyz"))
        coords = feature["geometry"]["coordinates"][0]
        vertices = [(c[0], c[1]) for c in coords]
        polygons.append({"level": level, "vertices": vertices})
    return polygons


def project_milky_way(polygons, lat, lon, year, month, day, hour, minute):
    load = Loader(_DATA_DIR)
    planets = load("de421.bsp")
    ts = load.timescale()

    observer = wgs84.latlon(lat, lon)
    t = ts.utc(year, month, day, hour, minute)
    earth = planets["earth"] + observer

    result = []
    for polygon in polygons:
        verts = polygon["vertices"]
        # Build a vectorised Star from all vertices at once
        ra_hours = [ra / 15.0 for ra, _ in verts]
        dec_degs = [dec for _, dec in verts]
        stars = Star(ra_hours=ra_hours, dec_degrees=dec_degs)
        alt, az, _ = earth.at(t).observe(stars).apparent().altaz()
        projected = list(zip(alt.degrees.tolist(), az.degrees.tolist()))
        result.append({"level": polygon["level"], "vertices": projected})
    return result
