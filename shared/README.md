---
title: "Shared Library API"
category: api
tags: [api, shared, base-game, constants, fonts, components, button]
related:
  - ../docs/design/game-architecture.md
  - ../docs/design/toddler-friendly.md
  - ../docs/knowledge/pygame-basics.md
---

# Shared Library API

## 概要

Baby Fun Box の共有ライブラリです。全てのゲームで使用する基底クラス、定数、ユーティリティを提供します。

---

## クイックスタート

```python
from shared.base_game import BaseGame
from shared.constants import BABY_COLORS, MIN_TOUCH_SIZE, FPS
from shared.fonts import get_font
from shared.components import Button, BackButton, IconButton
```

---

## ディレクトリ構造

```
shared/
├── __init__.py          # エクスポート
├── base_game.py         # 基底クラス
├── constants.py         # 定数定義
├── fonts.py             # フォント管理
└── components/
    ├── __init__.py
    └── button.py        # ボタンコンポーネント
```

---

## base_game.py

### BaseGame クラス

全てのゲームが継承する抽象基底クラス。

```python
from shared.base_game import BaseGame

class MyGame(BaseGame):
    name = "My Game"
    description = "ゲームの説明"

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """イベント処理（必須）"""
        pass

    def update(self, dt: float) -> None:
        """状態更新（必須）"""
        pass

    def draw(self) -> None:
        """描画（必須）"""
        pass
```

### クラス属性

| 属性 | 型 | 説明 |
|------|-----|------|
| `name` | `str` | ゲーム名（ランチャー表示用） |
| `description` | `str` | ゲームの説明 |
| `icon_path` | `str \| None` | アイコン画像のパス |

### インスタンス属性

| 属性 | 型 | 説明 |
|------|-----|------|
| `screen` | `pygame.Surface` | 描画サーフェス |
| `width` | `int` | 画面幅 |
| `height` | `int` | 画面高さ |
| `running` | `bool` | ゲーム実行中フラグ |
| `return_to_launcher` | `bool` | ランチャーに戻るフラグ |
| `clock` | `pygame.time.Clock` | FPS 制御用クロック |

### 抽象メソッド（実装必須）

```python
@abstractmethod
def handle_events(self, events: list[pygame.event.Event]) -> None:
    """イベント処理"""
    pass

@abstractmethod
def update(self, dt: float) -> None:
    """状態更新（dt: 秒単位のデルタタイム）"""
    pass

@abstractmethod
def draw(self) -> None:
    """描画処理"""
    pass
```

### オーバーライド可能なメソッド

```python
def on_enter(self) -> None:
    """ゲーム開始時（リソース読み込み等）"""
    pass

def on_exit(self) -> None:
    """ゲーム終了時（クリーンアップ等）"""
    pass
```

### ユーティリティメソッド

```python
def request_return_to_launcher(self) -> None:
    """ランチャーに戻ることをリクエスト"""

def run(self) -> None:
    """ゲームループを実行（ランチャーから呼ばれる）"""

@classmethod
def get_icon(cls) -> pygame.Surface | None:
    """アイコン画像を取得"""
```

---

## constants.py

### 画面設定

```python
DEFAULT_WIDTH: int = 1024   # デフォルト画面幅
DEFAULT_HEIGHT: int = 768   # デフォルト画面高さ
FPS: int = 60               # フレームレート
```

### 基本色

```python
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
GRAY: tuple[int, int, int] = (128, 128, 128)
LIGHT_GRAY: tuple[int, int, int] = (200, 200, 200)
```

### 背景色

```python
BACKGROUND_LIGHT: tuple[int, int, int] = (240, 248, 255)  # アリスブルー
BACKGROUND_CREAM: tuple[int, int, int] = (255, 253, 245)  # クリーム
```

### 幼児向け色パレット

```python
BABY_RED: tuple[int, int, int] = (255, 89, 94)
BABY_YELLOW: tuple[int, int, int] = (255, 202, 58)
BABY_GREEN: tuple[int, int, int] = (138, 201, 38)
BABY_BLUE: tuple[int, int, int] = (25, 130, 196)
BABY_PURPLE: tuple[int, int, int] = (106, 76, 147)
BABY_ORANGE: tuple[int, int, int] = (255, 146, 76)
BABY_PINK: tuple[int, int, int] = (255, 119, 168)

# リスト形式（ランダム選択用）
BABY_COLORS: list[tuple[int, int, int]] = [...]
```

### タッチ・UI 設定

```python
MIN_TOUCH_SIZE: int = 80     # 最小タッチサイズ（幼児向け）
BUTTON_WIDTH: int = 200      # ボタンの幅
BUTTON_HEIGHT: int = 80      # ボタンの高さ
BUTTON_RADIUS: int = 15      # 角丸の半径
BACK_BUTTON_SIZE: int = 60   # 戻るボタンのサイズ
ICON_SIZE: int = 150         # アイコンサイズ
```

---

## fonts.py

### get_font

```python
def get_font(size: int) -> pygame.font.Font:
    """日本語対応フォントを取得"""
```

**使用例**:

```python
from shared.fonts import get_font

font = get_font(48)
text = font.render("こんにちは", True, BLACK)
```

### 対応フォント

Linux: Noto Sans CJK, TakaoGothic, VL Gothic
macOS: ヒラギノ角ゴシック
Windows: MS Gothic, メイリオ

---

## components/button.py

### Button

```python
from shared.components import Button

button = Button(
    x=100, y=200,
    width=200, height=80,
    text="スタート",
    on_click=lambda: print("Clicked!")
)

# イベント処理
button.handle_event(event)

# 描画
button.draw(screen)
```

### IconButton

```python
from shared.components import IconButton

icon_button = IconButton(
    x=100, y=100,
    size=150,
    icon=image,
    label="ゲーム名"
)
```

### BackButton

```python
from shared.components import BackButton

back_button = BackButton(
    x=20, y=20,
    on_click=self.request_return_to_launcher
)
```

---

## 関連ドキュメント

- [ゲームアーキテクチャ設計](../docs/design/game-architecture.md)
- [幼児向け UX 設計](../docs/design/toddler-friendly.md)
- [Pygame 基礎](../docs/knowledge/pygame-basics.md)
