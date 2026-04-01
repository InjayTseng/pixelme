# Self-Evolve Task List
Generated: 2026-04-01

## Backlog

### [P0] Fix `apply_palette` crash on RGBA / non-RGB images
- **Why**: `apply_palette` hardcodes `reshape(-1, 3)` — any RGBA input will crash.
- **Acceptance**: `python -c "from main import apply_palette; from PIL import Image; apply_palette(Image.new('RGBA', (4,4)), [(0,0,0),(255,255,255)])"` must not raise.
- **Files**: `main.py` (`apply_palette`)
- **Status**: DONE

### [P0] Fix `pick_grid_sizes` silently returning fewer values than `count`
- **Why**: Gap-filling loop can break early, `result[:count]` truncates — leaves banner cells black.
- **Acceptance**: `python -c "from main import pick_grid_sizes; r = pick_grid_sizes(20, 10); assert len(r) == 20, f'got {len(r)}'"` must pass.
- **Files**: `main.py` (`pick_grid_sizes`, `create_banner`)
- **Status**: DONE

### [P0] Update stale CLAUDE.md to reflect current architecture
- **Why**: CLAUDE.md describes removed single-function architecture — entirely wrong.
- **Acceptance**: CLAUDE.md accurately describes current functions, CLI args, and platform outputs.
- **Files**: `CLAUDE.md`
- **Status**: DONE

### [P1] Add `requirements.txt` with pinned dependencies
- **Why**: No version pins; `Image.Resampling` requires Pillow >= 9.1.
- **Acceptance**: `pip install -r requirements.txt` works; pins `Pillow>=9.1.0` and `numpy>=1.21.0`.
- **Files**: `requirements.txt` (new)
- **Status**: DONE

### [P1] Add test suite covering core functions
- **Why**: Zero tests; edge cases in `pick_grid_sizes`, `apply_palette`, `pixelate` are invisible.
- **Acceptance**: `python -m pytest tests/ -v` passes with 10+ test cases.
- **Files**: `tests/test_main.py` (new)
- **Status**: DONE (16 tests)

### [P1] Add `argparse` CLI with `--help`, `--palette`, `--list-palettes`
- **Why**: Positional-only sys.argv gives no help, no validation, no discoverability.
- **Acceptance**: `python main.py --help` prints usage; `python main.py --list-palettes` works.
- **Files**: `main.py`
- **Status**: DONE

### [P2] Add Floyd-Steinberg dithering option
- **Why**: Nearest-color produces harsh banding; dithering makes gameboy/sepia look dramatically better.
- **Acceptance**: `python main.py avatar.png out/ --palette gameboy --dither` produces visibly smoother output.
- **Files**: `main.py`
- **Status**: DONE

### [P2] Optimize GIF file size with per-frame palette quantization
- **Why**: Substack GIF can exceed Twitter's 5MB limit; frames saved as full RGB without quantization.
- **Acceptance**: `banner_twitter.gif` < 2MB, `banner_substack.gif` < 3MB.
- **Files**: `main.py` (`create_banner`)
- **Status**: DONE

### [P2] Add optional cell-label overlay showing resolution
- **Why**: Labels like "1px", "4px" make the progression self-explanatory to viewers.
- **Acceptance**: `python main.py avatar.png out/ --labels` adds text labels to each cell.
- **Files**: `main.py`
- **Status**: TODO

### [P2] Clean up stale artifacts from repo
- **Why**: Old bw files and results.jpg are committed but feature was removed.
- **Acceptance**: `git ls-files | grep -E 'banner_.*bw|results\.jpg'` returns empty.
- **Files**: `.gitignore`, git rm
- **Status**: TODO
