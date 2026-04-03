# starry-night

Generate a stylized sky map for a specific place and time, either from the command line or through a local Streamlit app.

## What It Does

This project renders a circular night-sky poster showing:

- visible stars
- Milky Way shading
- constellation lines
- optional constellation abbreviations
- a compass-style outer ring

The renderer supports custom title, subtitle, and background color. The Streamlit app adds a live low-resolution preview and a location lookup flow.

## Project Layout

- [main.py](/Users/simo/Documents/GitHub/starry-night/main.py): CLI entrypoint
- [streamlit_app.py](/Users/simo/Documents/GitHub/starry-night/streamlit_app.py): Streamlit app
- [skymap.py](/Users/simo/Documents/GitHub/starry-night/skymap.py): shared sky-data pipeline used by both CLI and app
- [render.py](/Users/simo/Documents/GitHub/starry-night/render.py): Matplotlib renderer
- [download_data.py](/Users/simo/Documents/GitHub/starry-night/download_data.py): downloads required astronomy data files into `./data`

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Download the required data files.

Example:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 download_data.py
```

The download step fetches:

- `hipparcos.dat`
- `de421.bsp`
- `mw.json`
- `constellations.lines.json`

## Run The CLI

The CLI takes explicit latitude, longitude, date, and time values.

Example:

```bash
python3 main.py \
  --lat 51.5074 \
  --lon -0.1278 \
  --year 2026 \
  --month 4 \
  --day 3 \
  --hour 22 \
  --minute 0 \
  --mag 6.5 \
  --output skymap.png \
  --title "London Sky" \
  --subtitle "03 April 2026\n22:00"
```

Useful flags:

- `--show-names`: show constellation abbreviations
- `--ring-only`: debug-only mode that renders just the outer ring

## Run The Streamlit App

Start the app locally with:

```bash
streamlit run streamlit_app.py
```

The app currently includes:

- place lookup by typing a town, city, or location name
- a confirmed place selection from matching results
- resolved latitude and longitude display
- date and time inputs
- magnitude limit input
- title and subtitle inputs
- background color picker
- optional constellation abbreviations
- live low-resolution preview
- full-resolution PNG generation only when `Generate` is pressed

By default, the preview updates as inputs change, but the final image is only saved when you click `Generate`.

## Notes

- The Streamlit app uses online geocoding via OpenStreetMap Nominatim to resolve place names into coordinates, so local internet access is required for location lookup.
- The CLI still supports `--ring-only` for debugging, but that option is intentionally not exposed in the Streamlit app.
- Output is saved to the path provided in the app or CLI, relative to the project root unless you specify an absolute path.
