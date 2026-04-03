from datetime import datetime

import requests
import streamlit as st

from render import BASE_BG_COLOR, FIG_DPI, render_map, render_map_bytes
from skymap import build_skymap_data

PREVIEW_DPI = 120
GEOCODER_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_LIMIT = 5


@st.cache_data(show_spinner=False)
def get_skymap_data(lat, lon, year, month, day, hour, minute, mag, ring_only, show_names):
    return build_skymap_data(
        lat,
        lon,
        year,
        month,
        day,
        hour,
        minute,
        mag=mag,
        ring_only=ring_only,
        show_names=show_names,
    )


@st.cache_data(show_spinner=False)
def get_preview_image(
    lat,
    lon,
    year,
    month,
    day,
    hour,
    minute,
    mag,
    show_names,
    title,
    subtitle,
    background_color,
):
    stars_df, milky_way, constellation_segments, constellation_labels = get_skymap_data(
        lat, lon, year, month, day, hour, minute, mag, False, show_names
    )
    return render_map_bytes(
        stars_df,
        milky_way,
        constellation_segments,
        title=title,
        subtitle=subtitle,
        ring_only=False,
        show_names=show_names,
        constellation_labels=constellation_labels,
        background_color=background_color,
        figure_dpi=PREVIEW_DPI,
    )


@st.cache_data(show_spinner=False)
def geocode_location_options(query):
    response = requests.get(
        GEOCODER_URL,
        params={"q": query, "format": "jsonv2", "limit": GEOCODER_LIMIT},
        headers={"User-Agent": "starry-night-streamlit-app/1.0"},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()
    if not results:
        return []
    return [
        {
            "label": match.get("display_name", query),
            "lat": float(match["lat"]),
            "lon": float(match["lon"]),
        }
        for match in results
    ]


st.set_page_config(page_title="Starry Night", layout="wide")
st.title("Starry Night Generator")
st.caption("Adjust the inputs to refresh the low-resolution preview. Use Generate to save the full-resolution PNG.")

controls, preview = st.columns([1, 1.3], gap="large")
valid_datetime = True
location_result = None
location_error = None
location_options = []

with controls:
    st.subheader("Inputs")
    location_query = st.text_input("Location", value="London, United Kingdom", help="Type a town, city, or place name.")

    if location_query.strip():
        try:
            location_options = geocode_location_options(location_query.strip())
            if not location_options:
                location_error = f'No location found for "{location_query}".'
        except requests.RequestException as exc:
            location_error = f"Location lookup failed: {exc}"
    else:
        location_error = "Enter a location to generate the sky map."

    if location_options:
        selected_label = st.selectbox(
            "Matching Places",
            options=[item["label"] for item in location_options],
            help="Choose the exact place to use for the sky map.",
        )
        location_result = next(item for item in location_options if item["label"] == selected_label)
    if location_result:
        st.caption(location_result["label"])
        st.caption(f'Latitude: {location_result["lat"]:.4f}, Longitude: {location_result["lon"]:.4f}')
    elif location_error:
        st.warning(location_error)

    date_cols = st.columns(3)
    year = date_cols[0].number_input("Year", min_value=1, max_value=9999, value=2026, step=1)
    month = date_cols[1].number_input("Month", min_value=1, max_value=12, value=4, step=1)
    day = date_cols[2].number_input("Day", min_value=1, max_value=31, value=3, step=1)

    time_cols = st.columns(2)
    hour = time_cols[0].number_input("Hour", min_value=0, max_value=23, value=22, step=1)
    minute = time_cols[1].number_input("Minute", min_value=0, max_value=59, value=0, step=1)

    mag = st.number_input("Magnitude Limit", min_value=-5.0, max_value=20.0, value=6.5, step=0.1, format="%.1f")
    output = st.text_input("Output File", value="skymap.png")
    title = st.text_input("Title", value="")
    subtitle = st.text_area("Subtitle", value="", height=100)
    show_names = st.checkbox("Show Constellation Names", value=False)
    background_color = st.color_picker("Background Color", value=BASE_BG_COLOR)

try:
    datetime(int(year), int(month), int(day), int(hour), int(minute))
except ValueError as exc:
    valid_datetime = False
    with preview:
        st.subheader("Preview")
        st.error(f"Invalid date or time: {exc}")

valid_inputs = valid_datetime and location_result is not None

if valid_inputs:
    with preview:
        st.subheader("Preview")
        preview_bytes = get_preview_image(
            float(location_result["lat"]),
            float(location_result["lon"]),
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            float(mag),
            bool(show_names),
            title,
            subtitle,
            background_color,
        )
        st.image(preview_bytes, caption="Live preview", use_container_width=True)
elif location_error and valid_datetime:
    with preview:
        st.subheader("Preview")
        st.info("Enter a valid location to see the preview.")

if st.button("Generate", type="primary", disabled=not valid_inputs):
    with st.spinner("Rendering full-resolution PNG..."):
        stars_df, milky_way, constellation_segments, constellation_labels = get_skymap_data(
            float(location_result["lat"]),
            float(location_result["lon"]),
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            float(mag),
            False,
            bool(show_names),
        )
        render_map(
            stars_df,
            milky_way,
            constellation_segments,
            output_file=output,
            title=title,
            subtitle=subtitle,
            ring_only=False,
            show_names=bool(show_names),
            constellation_labels=constellation_labels,
            background_color=background_color,
            figure_dpi=FIG_DPI,
        )
    st.success(f"Saved full-resolution image to {output}")
