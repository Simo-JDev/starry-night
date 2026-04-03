import json
import numpy as np
from skyfield.api import Loader, Star, wgs84

_DATA_DIR = "./data"


def load_constellation_lines():
    with open(f"{_DATA_DIR}/constellations.lines.json") as f:
        geojson = json.load(f)

    segments = []
    label_points = {}
    for feature in geojson["features"]:
        constellation_id = feature.get("id")
        points = []
        for line in feature["geometry"]["coordinates"]:
            points.extend((p[0], p[1]) for p in line)
            for i in range(len(line) - 1):
                segments.append([(line[i][0], line[i][1]), (line[i + 1][0], line[i + 1][1])])
        if constellation_id and points:
            label_points[constellation_id] = points
    return segments, label_points


def project_constellations(
    segments,
    lat,
    lon,
    year,
    month,
    day,
    hour,
    minute,
    earth=None,
    t=None,
    show_names=False,
    label_points=None,
):
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

    labels_projected = []
    if show_names and label_points:
        ids = []
        counts = []
        label_ra = []
        label_dec = []
        for constellation_id, points in label_points.items():
            ids.append(constellation_id)
            counts.append(len(points))
            label_ra.extend(p[0] / 15.0 for p in points)
            label_dec.extend(p[1] for p in points)

        stars_labels = Star(ra_hours=np.asarray(label_ra), dec_degrees=np.asarray(label_dec))
        alt_l, az_l, _ = earth.at(t).observe(stars_labels).apparent().altaz()
        alt_l = np.asarray(alt_l.degrees)
        az_l = np.asarray(az_l.degrees)

        start = 0
        for constellation_id, count in zip(ids, counts):
            end = start + count
            alt_slice = alt_l[start:end]
            az_slice = az_l[start:end]
            start = end

            visible = alt_slice > 0
            if not np.any(visible):
                continue

            alt_vis = alt_slice[visible]
            az_vis = az_slice[visible]
            az_rad = np.radians(az_vis)
            mean_az = np.degrees(np.arctan2(np.mean(np.sin(az_rad)), np.mean(np.cos(az_rad)))) % 360.0
            mean_alt = float(np.mean(alt_vis))
            labels_projected.append(
                {"id": constellation_id, "altitude_deg": mean_alt, "azimuth_deg": mean_az}
            )

    return result, labels_projected
