"""
フォント管理 - 日本語対応フォントの読み込み

pygameのデフォルトフォントは日本語をサポートしないため、
システムの日本語フォントを使用する。
"""

from pathlib import Path

import pygame

# 日本語フォントの候補（優先順位順）
JAPANESE_FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf",
    "/usr/share/fonts/truetype/vlgothic/VL-Gothic-Regular.ttf",
    # macOS
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    # Windows
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
]

# キャッシュされたフォントパス
_cached_font_path: str | None = None


def get_japanese_font_path() -> str | None:
    """
    利用可能な日本語フォントのパスを取得する

    Returns:
        フォントのパス、見つからない場合はNone
    """
    global _cached_font_path

    if _cached_font_path is not None:
        return _cached_font_path

    for font_path in JAPANESE_FONT_PATHS:
        if Path(font_path).exists():
            _cached_font_path = font_path
            return font_path

    return None


def get_font(size: int) -> pygame.font.Font:
    """
    指定サイズの日本語対応フォントを取得する

    Args:
        size: フォントサイズ

    Returns:
        pygame.font.Font オブジェクト
    """
    if not pygame.font.get_init():
        pygame.font.init()

    font_path = get_japanese_font_path()

    if font_path:
        try:
            return pygame.font.Font(font_path, size)
        except Exception:
            pass

    # フォールバック: デフォルトフォント
    return pygame.font.Font(None, size)
