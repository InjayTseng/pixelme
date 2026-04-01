"""PixelMe — Streamlit Web UI"""
import tempfile
import os
import streamlit as st
from PIL import Image
from main import (create_banner, PALETTES, PLATFORMS, PLATFORM_NAMES)

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

# --- Demo with sample if no upload ---
use_sample = False
if not uploaded and generate:
    sample_path = "samples/sample1.jpg"
    if os.path.exists(sample_path):
        uploaded = sample_path
        use_sample = True
        st.info("No photo uploaded — using sample image for demo.")

if uploaded and generate:
    if use_sample:
        img = Image.open(uploaded).convert("RGB")
    else:
        img = Image.open(uploaded).convert("RGB")

    palette = PALETTES[palette_name]
    suffix = f"_{palette_name}" if palette_name != "original" else ""
    plat = next(p for p in PLATFORMS if p[0] == platform)
    name, w, h, cols, rows = plat

    with st.spinner("Generating..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            banner_name = f"{name}{suffix}"
            create_banner(img, banner_name, w, h, cols, rows, tmpdir,
                          palette, dither, labels, no_gif=False)

            png_path = os.path.join(tmpdir, f"banner_{banner_name}.png")
            gif_path = os.path.join(tmpdir, f"banner_{banner_name}.gif")

            # Read files into memory before tmpdir cleanup
            with open(png_path, "rb") as f:
                png_bytes = f.read()
            with open(gif_path, "rb") as f:
                gif_bytes = f.read()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Static Banner")
        st.image(png_bytes, use_container_width=True)
        st.download_button("Download PNG", png_bytes,
                           file_name=f"pixelme_{banner_name}.png",
                           mime="image/png")
    with col2:
        st.subheader("Animated GIF")
        st.image(gif_bytes, use_container_width=True)
        st.download_button("Download GIF", gif_bytes,
                           file_name=f"pixelme_{banner_name}.gif",
                           mime="image/gif")

elif not generate:
    st.markdown("""
    ### How it works
    1. **Upload** a profile photo (or click Generate for a demo)
    2. **Pick** a platform and palette
    3. **Generate** and download your pixel-art banner

    Works with Twitter/X, Facebook, Substack, LinkedIn, YouTube, and Discord.
    """)
