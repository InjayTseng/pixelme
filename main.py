import math
import numpy as np
from PIL import Image


# --- Color Palettes ---

PALETTES = {
    'original': None,  # 不做色彩轉換
    'gameboy': [
        (15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15),
    ],
    'nes': [
        (0, 0, 0), (252, 252, 252), (188, 188, 188), (124, 124, 124),
        (168, 0, 32), (228, 0, 88), (248, 56, 0), (228, 92, 16),
        (172, 124, 0), (0, 184, 0), (0, 168, 0), (0, 168, 68),
        (0, 136, 136), (0, 120, 248), (104, 68, 252), (216, 0, 204),
        (248, 120, 88), (252, 160, 68), (248, 184, 0), (184, 248, 24),
        (88, 216, 84), (0, 232, 216), (120, 120, 120), (60, 188, 252),
        (148, 120, 248), (248, 88, 152), (248, 168, 160), (248, 184, 112),
        (252, 224, 168), (216, 248, 120), (184, 248, 184), (184, 248, 216),
        (0, 252, 252), (164, 228, 252), (184, 184, 248), (216, 168, 248),
    ],
    'sepia': [
        (44, 33, 21), (66, 49, 32), (88, 66, 43), (110, 82, 54),
        (143, 107, 70), (176, 133, 87), (198, 156, 109), (220, 180, 132),
        (237, 204, 163), (245, 222, 179), (250, 235, 200), (255, 245, 220),
    ],
}


def _find_nearest(pixel, pal):
    """找到調色盤中最接近的顏色，回傳 (nearest_color, error)"""
    dists = np.sum((pal - pixel) ** 2, axis=1)
    idx = np.argmin(dists)
    return pal[idx], pixel - pal[idx]


def apply_palette(img, palette, dither=False):
    """將圖片的每個像素映射到最近的調色盤顏色"""
    if palette is None:
        return img
    img = img.convert('RGB')
    pal = np.array(palette, dtype=np.float32)

    if dither:
        # Floyd-Steinberg dithering
        arr = np.array(img, dtype=np.float32)
        h, w = arr.shape[:2]
        for y in range(h):
            for x in range(w):
                old = arr[y, x].copy()
                nearest, error = _find_nearest(old, pal)
                arr[y, x] = nearest
                # 擴散誤差到鄰近像素
                if x + 1 < w:
                    arr[y, x + 1] += error * 7 / 16
                if y + 1 < h:
                    if x - 1 >= 0:
                        arr[y + 1, x - 1] += error * 3 / 16
                    arr[y + 1, x] += error * 5 / 16
                    if x + 1 < w:
                        arr[y + 1, x + 1] += error * 1 / 16
        result = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(result)

    # 無 dithering：向量化最近色
    arr = np.array(img, dtype=np.float32)
    flat = arr.reshape(-1, 3)
    dists = np.sum((flat[:, None, :] - pal[None, :, :]) ** 2, axis=2)
    indices = np.argmin(dists, axis=1)
    result = pal[indices].reshape(arr.shape).astype(np.uint8)
    return Image.fromarray(result)


def pixelate(img, grid_size, cell_w, cell_h, palette=None, dither=False):
    """將圖片像素化，可選套用調色盤與 dithering"""
    base = max(cell_w, cell_h)
    if grid_size >= base:
        out = img.resize((cell_w, cell_h), resample=Image.Resampling.LANCZOS)
        return apply_palette(out, palette, dither) if palette else out

    small = img.resize((grid_size, grid_size), resample=Image.Resampling.LANCZOS)
    if palette:
        small = apply_palette(small, palette, dither)
    big = small.resize((cell_w, cell_h), resample=Image.Resampling.NEAREST)
    return big


# 各平台設定：(名稱, 寬, 高, 列數, 行數)
PLATFORMS = [
    ('twitter',   1500, 500,  6, 2),   # 3:1
    ('facebook',  820,  312,  5, 2),   # ~2.6:1
    ('substack',  1500, 300,  10, 2),  # 5:1
]


def pick_grid_sizes(count, cell_size, end_fraction=0.15):
    """從 1 到 cell_size * end_fraction 之間均勻挑選 count 個像素化階段（log 等距）"""
    end_size = max(2, int(cell_size * end_fraction))
    if count <= 1:
        return [end_size]
    sizes = set()
    for i in range(count):
        t = i / (count - 1)
        val = int(round(2 ** (t * math.log2(end_size))))
        sizes.add(max(1, val))
    result = sorted(sizes)
    # 補中間值直到數量足夠
    while len(result) < count:
        gaps = []
        for j in range(len(result) - 1):
            mid = (result[j] + result[j + 1]) // 2
            if mid != result[j] and mid != result[j + 1]:
                gaps.append((result[j + 1] - result[j], mid))
        if not gaps:
            break
        gaps.sort(reverse=True)
        result.append(gaps[0][1])
        result = sorted(set(result))
    # 如果仍不夠（range 太小），重複最後一個值填滿
    while len(result) < count:
        result.append(result[-1])
    return result[:count]


def create_banner(img, name, width, height, cols, rows, out_dir='.', palette=None, dither=False):
    cell_w = width // cols
    cell_h = height // rows
    count = cols * rows
    cell_size = min(cell_w, cell_h)
    grid_sizes = pick_grid_sizes(count, cell_size)

    banner = Image.new('RGB', (width, height))
    for index, size in enumerate(grid_sizes):
        r = index // cols
        c = index % cols
        cell = pixelate(img, size, cell_w, cell_h, palette, dither)
        banner.paste(cell, (c * cell_w, r * cell_h))

    output = f'{out_dir}/banner_{name}.png'
    banner.save(output)
    print(f"[{name}] {width}x{height} ({cols}x{rows}) → {output}")

    # GIF 動畫（每幀量化到 128 色以減小檔案大小）
    frames = []
    for size in grid_sizes:
        frame = img.resize((size, size), resample=Image.Resampling.LANCZOS)
        if palette:
            frame = apply_palette(frame, palette, dither)
        frame = frame.resize((width, height), resample=Image.Resampling.NEAREST)
        frame = frame.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        frames.append(frame)
    gif_path = f'{out_dir}/banner_{name}.gif'
    durations = [300] * (len(frames) - 1) + [1500]
    frames[0].save(gif_path, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print(f"[{name}] GIF → {gif_path}")


def main(input_path='avatar.png', out_dir='.', palette_name='original', dither=False):
    import os
    os.makedirs(out_dir, exist_ok=True)

    try:
        img = Image.open(input_path).convert('RGB')
    except FileNotFoundError:
        print(f"找不到圖片: {input_path}")
        return 1

    if palette_name not in PALETTES:
        print(f"未知調色盤 '{palette_name}'，可用: {', '.join(PALETTES.keys())}")
        return 1

    palette = PALETTES[palette_name]
    suffix = f'_{palette_name}' if palette_name != 'original' else ''

    for name, w, h, cols, rows in PLATFORMS:
        create_banner(img, f'{name}{suffix}', w, h, cols, rows, out_dir, palette, dither)
    return 0


def cli():
    import argparse
    parser = argparse.ArgumentParser(
        prog='pixelme',
        description='Generate pixel-art progression banners for social media.',
    )
    parser.add_argument('input', nargs='?', default='avatar.png',
                        help='Input image path (default: avatar.png)')
    parser.add_argument('-o', '--output', default='.',
                        help='Output directory (default: current dir)')
    parser.add_argument('-p', '--palette', default='original',
                        choices=list(PALETTES.keys()),
                        help='Color palette (default: original)')
    parser.add_argument('-d', '--dither', action='store_true',
                        help='Apply Floyd-Steinberg dithering (with palette)')
    parser.add_argument('--list-palettes', action='store_true',
                        help='List available palettes and exit')

    # Support legacy positional args: main.py <input> <outdir> <palette>
    args, unknown = parser.parse_known_args()

    if args.list_palettes:
        for name, pal in PALETTES.items():
            colors = len(pal) if pal else 'full'
            print(f"  {name:12s} ({colors} colors)")
        return 0

    # Legacy compat: if unknown positional args, treat as outdir / palette
    if unknown:
        if args.output == '.':
            args.output = unknown[0]
        if len(unknown) > 1 and args.palette == 'original':
            args.palette = unknown[1]

    return main(args.input, args.output, args.palette, args.dither)


if __name__ == '__main__':
    import sys
    sys.exit(cli() or 0)
