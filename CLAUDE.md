# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PixelMe generates pixel-art progression banners from profile photos for social media. Each banner shows an avatar evolving through pixelation stages. Inspired by Travis LeRoy Southworth's *I'm a Square* NFT series.

## Running

```bash
pip install Pillow numpy

# Default (reads avatar.png, outputs to current dir)
python main.py

# Custom input, output dir, and palette
python main.py path/to/photo.png output_dir/ gameboy
```

## Architecture

Single file `main.py` with these core functions:

- `pixelate(img, grid_size, cell_w, cell_h, palette)` — downscale to grid_size, optional palette mapping, upscale with NEAREST
- `apply_palette(img, palette)` — numpy vectorized nearest-color mapping to a palette array
- `pick_grid_sizes(count, cell_size, end_fraction)` — log-distributed pixelation levels, capped at fraction of cell size
- `create_banner(img, name, w, h, cols, rows, out_dir, palette)` — composes grid + generates GIF animation
- `main(input_path, out_dir, palette_name)` — entry point, iterates over platforms

## Platforms

Defined in `PLATFORMS` list as `(name, width, height, cols, rows)`:

| Platform | Size | Grid |
|----------|------|------|
| Twitter/X | 1500x500 | 6x2 |
| Facebook | 820x312 | 5x2 |
| Substack | 1500x300 | 10x2 |

## Palettes

`PALETTES` dict: `original` (no mapping), `gameboy` (4 colors), `nes` (36 colors), `sepia` (12 colors).

## Output

Each platform generates:
- `banner_{name}.png` — static grid banner
- `banner_{name}.gif` — animated progression (300ms/frame, last frame 1500ms)

## Notes

- Uses NEAREST resampling for sharp pixel block edges
- `end_fraction=0.15` caps max pixelation at ~1/6 of cell resolution to maintain pixel-art feel
- Sample images in `samples/` from Unsplash (free license)
- Self-evolve pipeline state in `.self-evolve/`
