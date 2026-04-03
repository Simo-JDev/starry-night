import json
from skyfield.api import Loader, Star, wgs84

_DATA_DIR = "./data"


def load_constellation_lines():
    with open(f"{_DATA_DIR}/constellations.lines.json") as f:
        geojson = json.load(f)

    segments = []
    for feature in geojson["features"]:
        for line in feature["geometry"]["coordinates"]:
            for i in range(len(line) - 1):
                segments.append([(line[i][0], line[i][1]), (line[i + 1][0], line[i + 1][1])])
    return segments


def project_constellations(segments, lat, lon, year, month, day, hour, minute, earth=None, t=None):
    if earth is None or t is None:
        load = Loader(_DATA_DIR)
        planets = load("de421.bsp")
        ts = load.timescale()
        observer = wgs84.latlon(lat, lon)
        t = ts.utc(year, month, day, hour, minute)
        earth = planets["earth"] + observer

    # Collect all endpoints (2 per segment) into one vectorised call
    all_ra = [pt[0] / 15.0 for seg in segments for pt in seg]
    all_dec = [pt[1] for seg in segments for pt in seg]

    stars = Star(ra_hours=all_ra, dec_degrees=all_dec)
    alt, az, _ = earth.at(t).observe(stars).apparent().altaz()
    alt_d = alt.degrees.tolist()
    az_d = az.degrees.tolist()

    total = len(segments)
    result = []
    for i in range(total):
        a, b = i * 2, i * 2 + 1
        if alt_d[a] > 0 or alt_d[b] > 0:
            result.append([(alt_d[a], az_d[a]), (alt_d[b], az_d[b])])
    return result
