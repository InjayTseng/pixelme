# Codebase Knowledge Base

## Patterns & Conventions
- Single-file Python project (`main.py`), Pillow + numpy for image processing
- CLI interface: `python main.py <input> <output_dir> <palette>`
- Platforms defined as tuples in `PLATFORMS` list: (name, width, height, cols, rows)
- Pixel grid sizes are log-distributed via `pick_grid_sizes()`
- Palette mapping uses numpy vectorized nearest-color matching

## Architecture
- `pixelate()` — core pixel art function: downscale → optional palette → upscale with NEAREST
- `apply_palette()` — maps every pixel to closest color in a palette array
- `create_banner()` — composes grid of pixelated cells + generates GIF animation
- `pick_grid_sizes()` — generates log-spaced pixelation levels, capped at `end_fraction` of cell size
- Output: PNG (static grid banner) + GIF (animated progression) per platform

## Testing
- No test framework yet
- Manual testing: `python main.py samples/sample1.jpg previews/sample1`
- Verify: check output files exist and are valid images

## Gotchas
- Pillow `quantize()` fails when colors > actual unique pixels in image (caused bugs with 1x1, 2x2 grids)
- `end_fraction` must be relative to cell size, not source image size, or high-res stages look like originals
- GIF frames use full banner dimensions — can get large for substack (1500x300)
- `.gitignore` uses `/banner_*.png` (root only) to avoid ignoring previews/ subdirectories

## Discoveries (2026-04-01)
- Unsplash direct URLs work for sample images (free license, no auth needed)
- 4 palettes implemented: original, gameboy (4 colors), nes (36 colors), sepia (12 colors)
- Influencer seeding identified as top growth strategy
- GIF animation is the #1 viral hook — auto-plays on Twitter/X
