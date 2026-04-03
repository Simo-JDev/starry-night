import pandas as pd
from skyfield.api import Loader, Star, wgs84
from skyfield.data import hipparcos

_DATA_DIR = "./data"


def load_stars(magnitude_limit=6.5):
    with open(f"{_DATA_DIR}/hipparcos.dat", "rb") as f:
        df = hipparcos.load_dataframe(f)
    # Drop rows missing required astrometric fields to avoid NaN propagation in Skyfield.
    required = ["ra_degrees", "dec_degrees", "parallax_mas"]
    mask = (df["magnitude"] <= magnitude_limit) & df[required].notna().all(axis=1)
    return df[mask].copy()


def compute_star_positions(df, lat, lon, year, month, day, hour, minute, earth=None, t=None):
    if earth is None or t is None:
        load = Loader(_DATA_DIR)
        planets = load("de421.bsp")
        ts = load.timescale()
        observer = wgs84.latlon(lat, lon)
        t = ts.utc(year, month, day, hour, minute)
        earth = planets["earth"] + observer

    astrometric = earth.at(t).observe(Star.from_dataframe(df))
    alt, az, _ = astrometric.apparent().altaz()

    result = pd.DataFrame(
        {
            "magnitude": df["magnitude"].values,
            "altitude_deg": alt.degrees,
            "azimuth_deg": az.degrees,
            "bv": df["BV"].values if "BV" in df.columns else float("nan"),
        },
        index=df.index,
    )
    return result[result["altitude_deg"] > 0]
