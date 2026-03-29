import json
from skyfield.api import Loader, Star, wgs84
from skyfield.positionlib import position_of_radec

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


def project_milky_way(polygons, lat, lon, year, month, day, hour, minute):
    load = Loader(_DATA_DIR)
    planets = load("de421.bsp")
    ts = load.timescale()

    observer = wgs84.latlon(lat, lon)
    t = ts.utc(year, month, day, hour, minute)
    earth = planets["earth"] + observer

    result = []
    for polygon in polygons:
        projected = []
        for ra, dec in polygon["vertices"]:
            star = Star(ra_hours=ra / 15.0, dec_degrees=dec)
            alt, az, _ = earth.at(t).observe(star).apparent().altaz()
            projected.append((alt.degrees, az.degrees))
        result.append({"level": polygon["level"], "vertices": projected})
    drawn = 0
    skipped = 0
    for polygon in result:
        total = len(polygon["vertices"])
        above = sum(1 for alt, _ in polygon["vertices"] if alt > 0)
        will_draw = above / total >= 0.30
        status = "DRAW" if will_draw else "SKIP"
        if will_draw:
            drawn += 1
        else:
            skipped += 1
        print(f"  level={polygon['level']}  verts={total}  above_horizon={above}  {status}")
    print(f"Total: {drawn} drawn, {skipped} skipped")

    return result
