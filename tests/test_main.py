import os
import tempfile
import pytest
import numpy as np
from PIL import Image

from main import apply_palette, pick_grid_sizes, pixelate, create_banner, main, PALETTES


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
