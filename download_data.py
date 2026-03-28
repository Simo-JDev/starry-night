import os
import urllib.request
from skyfield.api import Loader
from skyfield.data import hipparcos

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

load = Loader(DATA_DIR)

# Hipparcos star catalog
hipparcos_path = os.path.join(DATA_DIR, "hipparcos.dat")
if os.path.exists(hipparcos_path):
    print("hipparcos.dat already exists")
else:
    print("Downloading hipparcos.dat...")
    urllib.request.urlretrieve(hipparcos.URL, hipparcos_path)

# DE421 ephemeris
de421_path = os.path.join(DATA_DIR, "de421.bsp")
if os.path.exists(de421_path):
    print("de421.bsp already exists")
else:
    print("Downloading de421.bsp...")
    load("de421.bsp")

# Milky Way polygons
mw_path = os.path.join(DATA_DIR, "mw.json")
if os.path.exists(mw_path):
    print("mw.json already exists")
else:
    print("Downloading mw.json...")
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/mw.json",
        mw_path,
    )

# Constellation lines
const_path = os.path.join(DATA_DIR, "constellations.lines.json")
if os.path.exists(const_path):
    print("constellations.lines.json already exists")
else:
    print("Downloading constellations.lines.json...")
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/constellations.lines.json",
        const_path,
    )
