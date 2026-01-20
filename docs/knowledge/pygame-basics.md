---
title: "Pygame 基礎"
category: knowledge
tags: [pygame, basics, game-loop, initialization, surface]
related:
  - ./pygame-rendering.md
  - ./pygame-input.md
  - ../design/game-architecture.md
---

# Pygame 基礎

## 概要

Pygame を使ったゲーム開発の基礎知識をまとめたドキュメントです。Baby Fun Box プロジェクトで使用しているパターンと、一般的なベストプラクティスを解説します。

---

## 前提知識

- Python 3.10 以上
- 基本的な Python 構文（クラス、関数、型ヒント）

---

## Pygame 初期化

### 基本的な初期化パターン

```python
import pygame

# Pygame 全体を初期化
pygame.init()

# 画面を作成
screen = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("Baby Fun Box")

# ゲームループ
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0  # 60FPS、秒単位のデルタタイム

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新処理
    # 描画処理

    pygame.display.flip()

pygame.quit()
```

### モジュール別初期化

特定のモジュールのみ使用する場合：

```python
# 音声のみ使用する場合
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# フォントのみ使用する場合
pygame.font.init()
```

### 初期化の確認

```python
# 各モジュールが初期化されているか確認
print(pygame.get_init())          # pygame全体
print(pygame.mixer.get_init())    # mixer
print(pygame.font.get_init())     # font
```

---

## ゲームループ

### 標準パターン

Baby Fun Box では以下のパターンを採用しています：

```python
class BaseGame:
    def run(self) -> None:
        self.on_enter()  # 開始時の処理

        while self.running and not self.return_to_launcher:
            # 1. デルタタイムの取得（60FPS制限）
            dt = self.clock.tick(60) / 1000.0

            # 2. イベント取得
            events = pygame.event.get()

            # 3. 共通イベント処理
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return

            # 4. ゲーム固有のイベント処理
            self.handle_events(events)

            # 5. 状態更新
            self.update(dt)

            # 6. 描画
            self.draw()

            # 7. 画面更新
            pygame.display.flip()

        self.on_exit()  # 終了時の処理
```

### デルタタイムの重要性

フレームレートに依存しないアニメーションのために、デルタタイム（前フレームからの経過時間）を使用します：

```python
# 悪い例: フレームレート依存
self.x += 5  # 60FPSなら秒速300px、30FPSなら秒速150px

# 良い例: デルタタイム使用
self.x += 300 * dt  # 常に秒速300px
```

---

## 座標系とサーフェス

### 座標系

Pygame の座標系は **左上が原点 (0, 0)** です：

```
(0, 0) ─────────────────→ X
   │
   │    画面領域
   │
   │
   ↓
   Y
```

### Surface（サーフェス）

`Surface` は画像やピクセルデータを保持するオブジェクトです：

```python
# 画面サーフェス（特別な Surface）
screen = pygame.display.set_mode((1024, 768))

# 通常のサーフェス（オフスクリーン描画用）
surface = pygame.Surface((200, 200))

# 透明度をサポートするサーフェス
surface_alpha = pygame.Surface((200, 200), pygame.SRCALPHA)
```

### Rect（矩形）

`Rect` は位置とサイズを管理する便利なクラスです：

```python
rect = pygame.Rect(100, 50, 200, 100)  # x, y, width, height

# 位置の取得
rect.x, rect.y          # 左上
rect.center             # 中心
rect.topleft            # 左上（タプル）
rect.bottomright        # 右下（タプル）

# 当たり判定
rect.collidepoint((150, 75))   # 点が矩形内にあるか
rect.colliderect(other_rect)   # 矩形同士の衝突
```

---

## ベストプラクティス

### 推奨パターン

#### 1. FPS 制限を必ず設定する

```python
clock = pygame.time.Clock()
dt = clock.tick(60) / 1000.0  # 60FPS 制限
```

#### 2. 責務を分離する

```python
class Game:
    def handle_events(self, events):
        """イベント処理のみ"""
        pass

    def update(self, dt):
        """状態更新のみ"""
        pass

    def draw(self):
        """描画のみ"""
        pass
```

#### 3. 定数を一箇所で管理する

```python
# shared/constants.py
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 768
FPS = 60
MIN_TOUCH_SIZE = 80  # 幼児向け最小タッチサイズ
```

#### 4. 型ヒントを使用する

```python
def handle_events(self, events: list[pygame.event.Event]) -> None:
    pass

def update(self, dt: float) -> None:
    pass
```

### アンチパターン

#### 1. `pygame.init()` の複数回呼び出し

```python
# 悪い例
def start_game():
    pygame.init()  # 毎回初期化
    # ...

# 良い例
# アプリケーション起動時に1回だけ初期化
```

#### 2. `pygame.quit()` なしの終了

```python
# 悪い例
if should_quit:
    sys.exit()  # リソースリーク

# 良い例
if should_quit:
    pygame.quit()
    sys.exit()
```

#### 3. イベントループでの `pygame.event.get()` 複数回呼び出し

```python
# 悪い例
for event in pygame.event.get():  # 1回目
    # ...
for event in pygame.event.get():  # 2回目: 空になっている

# 良い例
events = pygame.event.get()
for event in events:
    # ...
# 後で events を再利用可能
```

---

## トラブルシューティング

### 問題: 画面が真っ白/真っ黒のまま

**原因**: `pygame.display.flip()` を呼び忘れている

**解決策**:
```python
while running:
    # 描画処理
    screen.fill(WHITE)
    # ...
    pygame.display.flip()  # これを忘れずに
```

### 問題: `pygame.error: display Surface quit`

**原因**: `pygame.quit()` 後に描画しようとしている

**解決策**: ゲームループを正しく終了させる
```python
while running:
    # ...
    if should_quit:
        running = False  # ループを抜けてから quit

pygame.quit()  # ループ外で呼ぶ
```

### 問題: フレームレートが安定しない

**原因**: `clock.tick()` を使っていない

**解決策**:
```python
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000.0  # FPS制限
```

### 問題: 日本語が表示されない

**原因**: フォントが日本語をサポートしていない

**解決策**: `shared/fonts.py` を使用
```python
from shared.fonts import get_font

font = get_font(48)  # 日本語対応フォントを自動選択
text = font.render("こんにちは", True, BLACK)
```

---

## 関連ドキュメント

- [Pygame 描画処理](./pygame-rendering.md) - 描画の詳細
- [Pygame 入力処理](./pygame-input.md) - イベント処理の詳細
- [ゲームアーキテクチャ設計](../design/game-architecture.md) - BaseGame パターン
