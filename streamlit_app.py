from datetime import datetime
import re

import streamlit as st

from render import BASE_BG_COLOR, FIG_DPI, render_map, render_map_bytes
from skymap import build_skymap_data

PREVIEW_DPI = 120
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def normalize_hex_color(raw_value):
    value = raw_value.strip()
    if not value.startswith("#"):
        value = f"#{value}"
    if HEX_COLOR_RE.fullmatch(value):
        return value.lower(), None
    return BASE_BG_COLOR, "Background color must be a 6-digit hex value like #191f39."


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
    ring_only,
    show_names,
    title,
    subtitle,
    background_color,
):
    stars_df, milky_way, constellation_segments, constellation_labels = get_skymap_data(
        lat, lon, year, month, day, hour, minute, mag, ring_only, show_names
    )
    return render_map_bytes(
        stars_df,
        milky_way,
        constellation_segments,
        title=title,
        subtitle=subtitle,
        ring_only=ring_only,
        show_names=show_names,
        constellation_labels=constellation_labels,
        background_color=background_color,
        figure_dpi=PREVIEW_DPI,
    )


st.set_page_config(page_title="Starry Night", layout="wide")
st.title("Starry Night Generator")
st.caption("Adjust the inputs to refresh the low-resolution preview. Use Generate to save the full-resolution PNG.")

controls, preview = st.columns([1, 1.3], gap="large")

with controls:
    st.subheader("Inputs")
    lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=51.5074, step=0.0001, format="%.4f")
    lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-0.1278, step=0.0001, format="%.4f")

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
    ring_only = st.checkbox("Ring Only", value=False)
    show_names = st.checkbox("Show Constellation Names", value=False, disabled=ring_only)
    background_input = st.text_input("Background Color", value=BASE_BG_COLOR, help="Paste a hex value like #191f39.")

    background_color, color_error = normalize_hex_color(background_input)
    if color_error:
        st.warning(color_error)
    st.markdown(
        f"<div style='width:100%;height:2.25rem;border-radius:0.5rem;border:1px solid #d0d7de;background:{background_color};'></div>",
        unsafe_allow_html=True,
    )

valid_datetime = True
try:
    datetime(int(year), int(month), int(day), int(hour), int(minute))
except ValueError as exc:
    valid_datetime = False
    with preview:
        st.subheader("Preview")
        st.error(f"Invalid date or time: {exc}")

if valid_datetime:
    with preview:
        st.subheader("Preview")
        preview_bytes = get_preview_image(
            float(lat),
            float(lon),
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            float(mag),
            bool(ring_only),
            bool(show_names and not ring_only),
            title,
            subtitle,
            background_color,
        )
        st.image(preview_bytes, caption="Live preview", use_container_width=True)

if st.button("Generate", type="primary", disabled=not valid_datetime):
    with st.spinner("Rendering full-resolution PNG..."):
        stars_df, milky_way, constellation_segments, constellation_labels = get_skymap_data(
            float(lat),
            float(lon),
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            float(mag),
            bool(ring_only),
            bool(show_names and not ring_only),
        )
        render_map(
            stars_df,
            milky_way,
            constellation_segments,
            output_file=output,
            title=title,
            subtitle=subtitle,
            ring_only=bool(ring_only),
            show_names=bool(show_names and not ring_only),
            constellation_labels=constellation_labels,
            background_color=background_color,
            figure_dpi=FIG_DPI,
        )
    st.success(f"Saved full-resolution image to {output}")
