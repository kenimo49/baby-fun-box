"""
共通定数 - Baby Fun Box全体で使用する定数

色、サイズ、その他の共通設定を定義
"""

# =============================================================================
# 画面設定
# =============================================================================

# デフォルトの画面サイズ
DEFAULT_WIDTH: int = 1024
DEFAULT_HEIGHT: int = 768

# フレームレート
FPS: int = 60


# =============================================================================
# 色定義（RGB）
# =============================================================================

# 基本色
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
GRAY: tuple[int, int, int] = (128, 128, 128)
LIGHT_GRAY: tuple[int, int, int] = (200, 200, 200)

# 背景色
BACKGROUND_LIGHT: tuple[int, int, int] = (240, 248, 255)  # アリスブルー
BACKGROUND_CREAM: tuple[int, int, int] = (255, 253, 245)  # クリーム

# 幼児向けの鮮やかな色パレット
BABY_RED: tuple[int, int, int] = (255, 89, 94)
BABY_YELLOW: tuple[int, int, int] = (255, 202, 58)
BABY_GREEN: tuple[int, int, int] = (138, 201, 38)
BABY_BLUE: tuple[int, int, int] = (25, 130, 196)
BABY_PURPLE: tuple[int, int, int] = (106, 76, 147)
BABY_ORANGE: tuple[int, int, int] = (255, 146, 76)
BABY_PINK: tuple[int, int, int] = (255, 119, 168)

# 幼児向け色のリスト（ランダム選択用）
BABY_COLORS: list[tuple[int, int, int]] = [
    BABY_RED,
    BABY_YELLOW,
    BABY_GREEN,
    BABY_BLUE,
    BABY_PURPLE,
    BABY_ORANGE,
    BABY_PINK,
]

# UI色
BUTTON_COLOR: tuple[int, int, int] = (100, 149, 237)  # コーンフラワーブルー
BUTTON_HOVER_COLOR: tuple[int, int, int] = (65, 105, 225)  # ロイヤルブルー
BUTTON_TEXT_COLOR: tuple[int, int, int] = WHITE


# =============================================================================
# タッチ・UI設定
# =============================================================================

# タッチ対象の最小サイズ（1〜2歳児の指に適したサイズ）
MIN_TOUCH_SIZE: int = 80  # ピクセル

# ボタンのデフォルトサイズ
BUTTON_WIDTH: int = 200
BUTTON_HEIGHT: int = 80
BUTTON_RADIUS: int = 15  # 角丸の半径

# 戻るボタンのサイズ
BACK_BUTTON_SIZE: int = 60

# アイコンサイズ（ランチャー用）
ICON_SIZE: int = 150


# =============================================================================
# アニメーション設定
# =============================================================================

# フェードイン/アウトの時間（秒）
FADE_DURATION: float = 0.3

# ボタンのアニメーション
BUTTON_SCALE_PRESSED: float = 0.95
