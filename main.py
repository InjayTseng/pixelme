import math
from PIL import Image


def pixelate(img, grid_size, cell_w, cell_h):
    """將圖片像素化，保持原始色調"""
    base = max(cell_w, cell_h)
    if grid_size >= base:
        return img.resize((cell_w, cell_h), resample=Image.Resampling.LANCZOS)

    small = img.resize((grid_size, grid_size), resample=Image.Resampling.LANCZOS)
    big = small.resize((cell_w, cell_h), resample=Image.Resampling.NEAREST)
    return big


# 各平台設定：(名稱, 寬, 高, 列數, 行數)
PLATFORMS = [
    ('twitter',   1500, 500,  6, 2),   # 3:1
    ('facebook',  820,  312,  5, 2),   # ~2.6:1
    ('substack',  1500, 300,  10, 2),  # 5:1
]


def pick_grid_sizes(count, cell_size, end_fraction=0.15):
    """從 1 到 cell_size * end_fraction 之間均勻挑選 count 個像素化階段（log 等距）
    end_fraction=0.15 → 最清楚的一格大約是 1/6 解析度，明顯保持像素感"""
    end_size = max(2, int(cell_size * end_fraction))
    if count <= 1:
        return [end_size]
    sizes = set()
    for i in range(count):
        t = i / (count - 1)
        val = int(round(2 ** (t * math.log2(end_size))))
        sizes.add(max(1, val))
    result = sorted(sizes)
    # 如果去重後不夠，補中間值
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
    return result[:count]


def create_banner(img, name, width, height, cols, rows, out_dir='.'):
    cell_w = width // cols
    cell_h = height // rows
    count = cols * rows
    cell_size = min(cell_w, cell_h)
    grid_sizes = pick_grid_sizes(count, cell_size)

    banner = Image.new('RGB', (width, height))
    for index, size in enumerate(grid_sizes):
        r = index // cols
        c = index % cols
        cell = pixelate(img, size, cell_w, cell_h)
        banner.paste(cell, (c * cell_w, r * cell_h))

    output = f'{out_dir}/banner_{name}.png'
    banner.save(output)
    print(f"[{name}] {width}x{height} ({cols}x{rows}) → {output}")

    # 生成 GIF 動畫：逐格從低解析度到高解析度
    frames = []
    for size in grid_sizes:
        frame = img.resize((size, size), resample=Image.Resampling.LANCZOS)
        frame = frame.resize((width, height), resample=Image.Resampling.NEAREST)
        frames.append(frame)
    # 最後一幀停留久一點
    gif_path = f'{out_dir}/banner_{name}.gif'
    durations = [300] * (len(frames) - 1) + [1500]
    frames[0].save(gif_path, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0)
    print(f"[{name}] GIF animation → {gif_path}")


def main(input_path='avatar.png', out_dir='.'):
    import os
    os.makedirs(out_dir, exist_ok=True)

    try:
        img = Image.open(input_path).convert('RGB')
    except FileNotFoundError:
        print("找不到圖片，請確認檔名與路徑。")
        return

    for name, w, h, cols, rows in PLATFORMS:
        create_banner(img, name, w, h, cols, rows, out_dir)


if __name__ == '__main__':
    import sys
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'avatar.png'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    main(input_path, out_dir)
