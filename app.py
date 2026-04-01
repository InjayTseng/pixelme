"""PixelMe — Streamlit Web UI"""
import io
import tempfile
import os
import streamlit as st
from PIL import Image
from main import (create_banner, apply_palette, PALETTES, PLATFORMS,
                  PLATFORM_NAMES, DEFAULT_PLATFORMS)

st.set_page_config(page_title="PixelMe", page_icon="🟩", layout="wide")
st.title("PixelMe")
st.caption("Turn any profile photo into a pixel-art progression banner.")

# --- Sidebar controls ---
with st.sidebar:
    st.header("Settings")
    uploaded = st.file_uploader("Upload a photo", type=["png", "jpg", "jpeg", "webp"])
    platform = st.selectbox("Platform", PLATFORM_NAMES, index=0)
    palette_name = st.selectbox("Palette", list(PALETTES.keys()), index=0)
    dither = st.checkbox("Floyd-Steinberg dithering")
    labels = st.checkbox("Resolution labels")
    generate = st.button("Generate", type="primary", use_container_width=True)

# --- Main area ---
if uploaded and generate:
    img = Image.open(uploaded).convert("RGB")
    palette = PALETTES[palette_name]
    suffix = f"_{palette_name}" if palette_name != "original" else ""

    # Find platform config
    plat = next(p for p in PLATFORMS if p[0] == platform)
    name, w, h, cols, rows = plat

    with tempfile.TemporaryDirectory() as tmpdir:
        banner_name = f"{name}{suffix}"
        create_banner(img, banner_name, w, h, cols, rows, tmpdir, palette, dither, labels, no_gif=False)

        png_path = os.path.join(tmpdir, f"banner_{banner_name}.png")
        gif_path = os.path.join(tmpdir, f"banner_{banner_name}.gif")

        st.subheader("Static Banner")
        st.image(png_path, use_container_width=True)

        # Download PNG
        with open(png_path, "rb") as f:
            st.download_button("Download PNG", f.read(),
                               file_name=f"pixelme_{banner_name}.png",
                               mime="image/png")

        st.subheader("Animated GIF")
        st.image(gif_path, use_container_width=True)

        # Download GIF
        with open(gif_path, "rb") as f:
            st.download_button("Download GIF", f.read(),
                               file_name=f"pixelme_{banner_name}.gif",
                               mime="image/gif")

elif not uploaded:
    st.info("Upload a photo in the sidebar to get started.")
