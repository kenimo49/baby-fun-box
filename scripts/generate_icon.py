#!/usr/bin/env python3
"""
Baby Fun Box アイコン生成スクリプト

カラフルな4分割グリッドのアイコンを生成します。
"""

import math
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow が必要です: pip install Pillow")
    exit(1)


# Baby Fun Box のカラーパレット
BABY_COLORS = [
    (255, 89, 94),    # 赤
    (255, 202, 58),   # 黄
    (138, 201, 38),   # 緑
    (25, 130, 196),   # 青
    (255, 119, 168),  # ピンク
    (255, 146, 76),   # オレンジ
]


def create_icon(size: int = 256) -> Image.Image:
    """カラフルなアイコンを生成"""
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 背景（角丸四角形）
    padding = size // 16
    corner_radius = size // 8

    # 背景を白で塗りつぶし（角丸）
    draw.rounded_rectangle(
        [padding, padding, size - padding, size - padding],
        radius=corner_radius,
        fill=(255, 255, 255, 255),
        outline=(200, 200, 200, 255),
        width=2
    )

    # 4分割グリッド
    grid_padding = size // 8
    grid_size = (size - grid_padding * 2) // 2
    gap = size // 32

    positions = [
        (grid_padding, grid_padding),                          # 左上
        (grid_padding + grid_size + gap, grid_padding),        # 右上
        (grid_padding, grid_padding + grid_size + gap),        # 左下
        (grid_padding + grid_size + gap, grid_padding + grid_size + gap),  # 右下
    ]

    # 各セルを描画
    for i, (x, y) in enumerate(positions):
        color = BABY_COLORS[i]
        cell_radius = size // 16

        draw.rounded_rectangle(
            [x, y, x + grid_size - gap, y + grid_size - gap],
            radius=cell_radius,
            fill=color
        )

        # 各セルにシンプルな図形を描画
        cx = x + (grid_size - gap) // 2
        cy = y + (grid_size - gap) // 2
        shape_size = grid_size // 4

        if i == 0:  # 左上: 星
            draw_star(draw, cx, cy, shape_size, (255, 255, 255, 200))
        elif i == 1:  # 右上: ハート
            draw_heart(draw, cx, cy, shape_size, (255, 255, 255, 200))
        elif i == 2:  # 左下: 円
            draw.ellipse(
                [cx - shape_size, cy - shape_size, cx + shape_size, cy + shape_size],
                fill=(255, 255, 255, 200)
            )
        elif i == 3:  # 右下: 三角形
            draw_triangle(draw, cx, cy, shape_size, (255, 255, 255, 200))

    return img


def draw_star(draw: ImageDraw.Draw, cx: int, cy: int, size: int, color: tuple) -> None:
    """星を描画"""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 0.4
        x = cx + r * math.cos(angle)
        y = cy - r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=color)


def draw_heart(draw: ImageDraw.Draw, cx: int, cy: int, size: int, color: tuple) -> None:
    """ハートを描画"""
    # 簡易的なハート（2つの円 + 三角形）
    r = size * 0.5
    offset = size * 0.3

    # 左上の円
    draw.ellipse([cx - offset - r, cy - offset - r, cx - offset + r, cy - offset + r], fill=color)
    # 右上の円
    draw.ellipse([cx + offset - r, cy - offset - r, cx + offset + r, cy - offset + r], fill=color)
    # 下の三角形
    draw.polygon([
        (cx - size, cy - offset * 0.5),
        (cx + size, cy - offset * 0.5),
        (cx, cy + size)
    ], fill=color)


def draw_triangle(draw: ImageDraw.Draw, cx: int, cy: int, size: int, color: tuple) -> None:
    """三角形を描画"""
    points = [
        (cx, cy - size),
        (cx - size, cy + size * 0.7),
        (cx + size, cy + size * 0.7),
    ]
    draw.polygon(points, fill=color)


def main() -> None:
    """メイン処理"""
    output_dir = Path(__file__).parent.parent

    # 複数サイズを生成
    sizes = [256, 128, 64, 48, 32]

    for size in sizes:
        icon = create_icon(size)

        if size == 256:
            # メインアイコン
            output_path = output_dir / "baby-fun-box.png"
            icon.save(output_path, "PNG")
            print(f"Created: {output_path}")

        # サイズ別アイコン
        output_path = output_dir / f"baby-fun-box-{size}.png"
        icon.save(output_path, "PNG")
        print(f"Created: {output_path}")

    print("\nIcon generation complete!")


if __name__ == "__main__":
    main()
