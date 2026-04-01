import os
import tempfile
import pytest
import numpy as np
from PIL import Image

from main import (apply_palette, pick_grid_sizes, pixelate, create_banner, main,
                   PALETTES, PLATFORMS, PLATFORM_NAMES, DEFAULT_PLATFORMS)


# --- pick_grid_sizes ---

def test_pick_grid_sizes_returns_correct_count():
    for count in [1, 5, 10, 20]:
        result = pick_grid_sizes(count, 100)
        assert len(result) == count, f"Expected {count}, got {len(result)}"


def test_pick_grid_sizes_monotonic():
    result = pick_grid_sizes(10, 200)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1], f"Not monotonic at index {i}"


def test_pick_grid_sizes_starts_at_one():
    result = pick_grid_sizes(5, 100)
    assert result[0] == 1


def test_pick_grid_sizes_small_cell():
    """Even with very small cell_size, should return correct count."""
    result = pick_grid_sizes(20, 5)
    assert len(result) == 20


# --- apply_palette ---

def test_apply_palette_none_returns_original():
    img = Image.new('RGB', (4, 4), color=(128, 64, 32))
    result = apply_palette(img, None)
    assert result is img


def test_apply_palette_nearest_color():
    img = Image.new('RGB', (1, 1), color=(200, 50, 50))
    palette = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    result = apply_palette(img, palette)
    pixel = result.getpixel((0, 0))
    assert pixel == (255, 0, 0), f"Expected red, got {pixel}"


def test_apply_palette_rgba_input():
    """RGBA images should be converted to RGB without crashing."""
    img = Image.new('RGBA', (4, 4), color=(128, 64, 32, 255))
    palette = [(0, 0, 0), (255, 255, 255)]
    result = apply_palette(img, palette)
    assert result.mode == 'RGB'


def test_apply_palette_dither():
    """Dithering should produce different output than no-dither."""
    img = Image.new('RGB', (8, 8))
    # Gradient image
    for x in range(8):
        for y in range(8):
            img.putpixel((x, y), (x * 32, y * 32, 128))
    palette = [(0, 0, 0), (255, 255, 255)]
    no_dither = np.array(apply_palette(img, palette, dither=False))
    with_dither = np.array(apply_palette(img, palette, dither=True))
    # Both should have same shape, but different pixel values
    assert no_dither.shape == with_dither.shape
    assert not np.array_equal(no_dither, with_dither)


def test_apply_palette_preserves_dimensions():
    img = Image.new('RGB', (16, 8))
    palette = [(0, 0, 0), (255, 255, 255)]
    result = apply_palette(img, palette)
    assert result.size == (16, 8)


# --- pixelate ---

def test_pixelate_output_dimensions():
    img = Image.new('RGB', (100, 100), color=(50, 100, 150))
    result = pixelate(img, 4, 200, 100)
    assert result.size == (200, 100)


def test_pixelate_with_palette():
    img = Image.new('RGB', (100, 100), color=(200, 50, 50))
    palette = [(255, 0, 0), (0, 0, 255)]
    result = pixelate(img, 4, 50, 50, palette)
    assert result.size == (50, 50)
    # Should be mapped to red
    pixel = result.getpixel((0, 0))
    assert pixel == (255, 0, 0)


def test_pixelate_large_grid_returns_resized():
    """When grid_size >= base, should return a clean resize, not pixelated."""
    img = Image.new('RGB', (100, 100), color=(50, 100, 150))
    result = pixelate(img, 500, 50, 50)
    assert result.size == (50, 50)


# --- create_banner ---

def test_create_banner_outputs_png_and_gif():
    img = Image.new('RGB', (100, 100), color=(50, 100, 150))
    with tempfile.TemporaryDirectory() as tmpdir:
        create_banner(img, 'test', 300, 100, 3, 1, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'banner_test.png'))
        assert os.path.exists(os.path.join(tmpdir, 'banner_test.gif'))


def test_create_banner_png_dimensions():
    img = Image.new('RGB', (100, 100), color=(50, 100, 150))
    with tempfile.TemporaryDirectory() as tmpdir:
        create_banner(img, 'dim', 600, 200, 3, 2, tmpdir)
        banner = Image.open(os.path.join(tmpdir, 'banner_dim.png'))
        assert banner.size == (600, 200)


# --- main (end-to-end) ---

def test_main_end_to_end():
    # Create a synthetic test image
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img = Image.new('RGB', (64, 64), color=(100, 150, 200))
        input_path = os.path.join(tmpdir, 'test.png')
        test_img.save(input_path)

        out_dir = os.path.join(tmpdir, 'output')
        result = main(input_path, out_dir, 'original')
        assert result == 0

        # Check all platforms generated
        for platform in ['twitter', 'facebook', 'substack']:
            assert os.path.exists(os.path.join(out_dir, f'banner_{platform}.png'))
            assert os.path.exists(os.path.join(out_dir, f'banner_{platform}.gif'))


def test_main_missing_file():
    result = main('/nonexistent/path.png', '/tmp/out')
    assert result == 1


def test_main_invalid_palette():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img = Image.new('RGB', (10, 10))
        input_path = os.path.join(tmpdir, 'test.png')
        test_img.save(input_path)
        result = main(input_path, tmpdir, 'nonexistent_palette')
        assert result == 1


# --- --platform ---

def test_main_single_platform():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img = Image.new('RGB', (64, 64), color=(100, 150, 200))
        input_path = os.path.join(tmpdir, 'test.png')
        test_img.save(input_path)
        out_dir = os.path.join(tmpdir, 'output')
        result = main(input_path, out_dir, platform='linkedin', no_gif=True)
        assert result == 0
        assert os.path.exists(os.path.join(out_dir, 'banner_linkedin.png'))
        assert not os.path.exists(os.path.join(out_dir, 'banner_twitter.png'))


def test_main_invalid_platform():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img = Image.new('RGB', (10, 10))
        input_path = os.path.join(tmpdir, 'test.png')
        test_img.save(input_path)
        result = main(input_path, tmpdir, platform='tiktok')
        assert result == 1


# --- --size ---

def test_main_custom_size():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img = Image.new('RGB', (64, 64))
        input_path = os.path.join(tmpdir, 'test.png')
        test_img.save(input_path)
        out_dir = os.path.join(tmpdir, 'output')
        result = main(input_path, out_dir, custom_size=(800, 200), no_gif=True)
        assert result == 0
        banner = Image.open(os.path.join(out_dir, 'banner_custom.png'))
        assert banner.size == (800, 200)


# --- --no-gif ---

def test_create_banner_no_gif():
    img = Image.new('RGB', (100, 100))
    with tempfile.TemporaryDirectory() as tmpdir:
        create_banner(img, 'nogif', 300, 100, 3, 1, tmpdir, no_gif=True)
        assert os.path.exists(os.path.join(tmpdir, 'banner_nogif.png'))
        assert not os.path.exists(os.path.join(tmpdir, 'banner_nogif.gif'))


# --- --labels ---

def test_create_banner_labels_differ():
    img = Image.new('RGB', (100, 100), color=(50, 100, 150))
    with tempfile.TemporaryDirectory() as tmpdir:
        create_banner(img, 'nolbl', 300, 100, 3, 1, tmpdir, no_gif=True)
        create_banner(img, 'lbl', 300, 100, 3, 1, tmpdir, labels=True, no_gif=True)
        a = np.array(Image.open(os.path.join(tmpdir, 'banner_nolbl.png')))
        b = np.array(Image.open(os.path.join(tmpdir, 'banner_lbl.png')))
        assert not np.array_equal(a, b)


# --- all palettes ---

def test_main_all_palettes():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img = Image.new('RGB', (32, 32))
        input_path = os.path.join(tmpdir, 'test.png')
        test_img.save(input_path)
        out_dir = os.path.join(tmpdir, 'output')
        for pal in PALETTES:
            main(input_path, out_dir, pal, no_gif=True)
        for pal in ['gameboy', 'nes', 'sepia']:
            assert os.path.exists(os.path.join(out_dir, f'banner_twitter_{pal}.png'))


# --- platform constants ---

def test_platform_names_consistent():
    assert set(PLATFORM_NAMES) == {p[0] for p in PLATFORMS}
    for d in DEFAULT_PLATFORMS:
        assert d in PLATFORM_NAMES
