# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PixelMe is a Python script that generates a pixel-art progression banner from an avatar image. It creates a horizontal strip showing 8 stages of pixelation (from 1x1 to full resolution), producing a "reveal" effect.

## Running

```bash
python main.py
```

Requires Pillow (`pip install Pillow`). Input: `avatar.png` in the project root. Output: `im_a_square_banner.jpg`.

## Architecture

Single file (`main.py`) with one function `create_pixel_progression_banner(input_path, output_path)`. It resizes the input to 512x512, generates 8 pixelation levels (grid sizes: 1, 2, 4, 8, 16, 32, 64, 512), and composites them side-by-side into a banner (4096x512).

## Notes

- Comments are in Traditional Chinese (zh-TW).
- Input images are force-resized to square (512x512) regardless of original aspect ratio.
- Uses NEAREST resampling for sharp pixel edges when upscaling.
