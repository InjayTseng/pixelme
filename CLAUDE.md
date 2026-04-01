# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PixelMe generates pixel-art progression banners from profile photos for social media. Each banner shows an avatar evolving through pixelation stages. Inspired by Travis LeRoy Southworth's *I'm a Square* NFT series.

## Running

```bash
pip install Pillow numpy
python main.py photo.png -o out/ -p gameboy --dither --labels
python main.py --help
```

## Testing

```bash
python -m pytest tests/ -v
```

24 tests covering: `pick_grid_sizes`, `apply_palette`, `pixelate`, `create_banner`, `main()`, platform selection, custom size, no-gif, labels, all palettes.

## Architecture

Single file `main.py` (~300 lines) with `cli()` entry point using argparse.

Core functions:
- `pixelate(img, grid_size, cell_w, cell_h, palette, dither)` — downscale → palette → upscale NEAREST
- `apply_palette(img, palette, dither)` — vectorized nearest-color or Floyd-Steinberg dithering
- `pick_grid_sizes(count, cell_size, end_fraction=0.15)` — log-distributed pixelation levels
- `create_banner(img, name, w, h, cols, rows, out_dir, palette, dither, labels, no_gif)` — grid + optional GIF
- `main(input_path, out_dir, palette_name, dither, labels, platform, custom_size, no_gif)` — orchestrator
- `draw_label()` — resolution text overlay with cross-platform font cache

## Platforms

`PLATFORMS` list, `DEFAULT_PLATFORMS` = twitter/facebook/substack:

| Platform | Size | Grid |
|----------|------|------|
| twitter | 1500x500 | 6x2 |
| facebook | 820x312 | 5x2 |
| substack | 1500x300 | 10x2 |
| linkedin | 1584x396 | 8x2 |
| youtube | 2560x1440 | 8x2 |
| discord | 960x540 | 6x2 |

## CLI Flags

`-p/--palette`, `--all-palettes`, `-d/--dither`, `-l/--labels`, `--platform`, `--size WxH`, `--no-gif`, `--list-palettes`, `--list-platforms`

Legacy positional args (`main.py <input> <outdir> <palette>`) still supported via `parse_known_args`.

## Notes

- `end_fraction=0.15` caps max pixelation at ~1/6 of cell resolution
- Font cache in `_font_cache` dict, probes macOS/Linux/Windows paths once per size
- GIF frames quantized to 128 colors for size optimization
- Self-evolve pipeline state in `.self-evolve/`
