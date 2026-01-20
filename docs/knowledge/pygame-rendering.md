---
title: "Pygame 描画処理"
category: knowledge
tags: [pygame, rendering, drawing, animation, surface, alpha]
related:
  - ./pygame-basics.md
  - ./pygame-audio.md
  - ../design/game-architecture.md
---

# Pygame 描画処理

## 概要

Pygame での描画処理のベストプラクティスを解説します。Baby Fun Box では、外部画像ファイルを使わずにプロシージャル（コードによる）描画を多用しています。

---

## 描画の基本原則

### 描画順序

毎フレーム、以下の順序で描画を行います：

```python
def draw(self) -> None:
    # 1. 背景クリア（必須）
    self.screen.fill(BACKGROUND_LIGHT)

    # 2. 背景オブジェクト（奥）
    self._draw_background()

    # 3. ゲームオブジェクト（中間）
    for obj in self.objects:
        obj.draw(self.screen)

    # 4. エフェクト（パーティクル等）
    for particle in self.particles:
        particle.draw(self.screen)

    # 5. UI（手前）
    self.back_button.draw(self.screen)
    self._draw_score()

    # 注: pygame.display.flip() は BaseGame.run() で呼ばれる
```

### ダブルバッファリング

Pygame はデフォルトでダブルバッファリングを使用します：

1. バックバッファに描画
2. `pygame.display.flip()` でフロントバッファと交換
3. 画面に表示

これにより、描画途中の状態が表示されることを防ぎます。

---

## 基本描画関数

### 矩形

```python
import pygame

# 塗りつぶし矩形
pygame.draw.rect(screen, RED, (x, y, width, height))

# 枠線のみ
pygame.draw.rect(screen, RED, (x, y, width, height), width=2)

# 角丸矩形
pygame.draw.rect(screen, RED, (x, y, width, height), border_radius=15)
```

### 円

```python
# 塗りつぶし円
pygame.draw.circle(screen, BLUE, (center_x, center_y), radius)

# 枠線のみ
pygame.draw.circle(screen, BLUE, (center_x, center_y), radius, width=2)
```

### 多角形

```python
# 三角形
points = [(100, 200), (150, 100), (200, 200)]
pygame.draw.polygon(screen, GREEN, points)

# 枠線のみ
pygame.draw.polygon(screen, GREEN, points, width=2)
```

### 線

```python
# 直線
pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), width=2)

# 連続線
points = [(10, 10), (50, 30), (90, 10)]
pygame.draw.lines(screen, BLACK, closed=False, points=points, width=2)
```

---

## 画像の扱い

### 読み込みと最適化

```python
# 基本的な読み込み
image = pygame.image.load("path/to/image.png")

# 描画高速化のための変換
image = image.convert()        # 透明度なし
image = image.convert_alpha()  # 透明度あり

# サイズ変更
image = pygame.transform.scale(image, (new_width, new_height))

# スムーズなサイズ変更（低速だが高品質）
image = pygame.transform.smoothscale(image, (new_width, new_height))
```

### 描画

```python
# 左上を基準に描画
screen.blit(image, (x, y))

# 中心を基準に描画
rect = image.get_rect(center=(center_x, center_y))
screen.blit(image, rect)
```

---

## アルファブレンディング

### 透明なサーフェス

```python
# SRCALPHA フラグで透明度をサポート
surface = pygame.Surface((200, 200), pygame.SRCALPHA)

# 半透明の円を描画
color_with_alpha = (255, 0, 0, 128)  # RGBA (Aが透明度)
pygame.draw.circle(surface, color_with_alpha, (100, 100), 50)

# メインスクリーンに描画
screen.blit(surface, (x, y))
```

### パーティクルエフェクト

Baby Fun Box のバルーンポップで使用しているパターン：

```python
class Particle:
    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.radius = 5
        self.lifetime = 1.0  # 秒

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / 1.0))
        self.y -= 50 * dt  # 上昇

    def draw(self, screen: pygame.Surface) -> None:
        if self.alpha <= 0:
            return
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        color = (*self.color, self.alpha)
        pygame.draw.circle(surface, color, (self.radius, self.radius), self.radius)
        screen.blit(surface, (self.x - self.radius, self.y - self.radius))

    @property
    def is_alive(self) -> bool:
        return self.lifetime > 0
```

---

## アニメーションパターン

### 時間ベースアニメーション

```python
class Balloon:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.wobble_time = 0.0
        self.wobble_amplitude = 5.0
        self.wobble_speed = 3.0

    def update(self, dt: float) -> None:
        # ゆらゆら動き
        self.wobble_time += dt * self.wobble_speed
        self.offset_x = math.sin(self.wobble_time) * self.wobble_amplitude

        # 上昇
        self.y -= 50 * dt

    def draw(self, screen: pygame.Surface) -> None:
        draw_x = self.x + self.offset_x
        pygame.draw.circle(screen, self.color, (int(draw_x), int(self.y)), self.radius)
```

### イージング関数

滑らかなアニメーションのためのイージング：

```python
import math

def ease_out_quad(t: float) -> float:
    """減速するイージング (0.0 ~ 1.0)"""
    return 1 - (1 - t) ** 2

def ease_out_bounce(t: float) -> float:
    """バウンスするイージング"""
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375

# 使用例
class PopAnimation:
    def __init__(self):
        self.progress = 0.0  # 0.0 ~ 1.0
        self.duration = 0.3  # 秒

    def update(self, dt: float) -> None:
        self.progress = min(1.0, self.progress + dt / self.duration)

    def get_scale(self) -> float:
        return 1.0 + ease_out_bounce(self.progress) * 0.3
```

---

## パフォーマンス最適化

### `convert()` / `convert_alpha()` を使う

```python
# 悪い例（毎フレーム変換が発生）
image = pygame.image.load("image.png")

# 良い例（読み込み時に一度だけ変換）
image = pygame.image.load("image.png").convert_alpha()
```

### 静的な要素はサーフェスにキャッシュ

```python
class Background:
    def __init__(self, width: int, height: int):
        # 一度だけ生成
        self.surface = pygame.Surface((width, height))
        self._draw_static_elements()

    def _draw_static_elements(self) -> None:
        self.surface.fill(BACKGROUND_LIGHT)
        # 複雑な背景描画...

    def draw(self, screen: pygame.Surface) -> None:
        # 毎フレームは blit のみ
        screen.blit(self.surface, (0, 0))
```

### Rect を活用した当たり判定

```python
# 毎フレーム Rect を作らない
class GameObject:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)

    def move(self, dx: int, dy: int) -> None:
        self.rect.move_ip(dx, dy)  # in-place 移動

    def collides_with(self, point: tuple[int, int]) -> bool:
        return self.rect.collidepoint(point)
```

---

## トラブルシューティング

### 問題: 描画が反映されない

**原因**: `pygame.display.flip()` を呼んでいない、または `fill()` で前フレームを消していない

**解決策**:
```python
def draw(self) -> None:
    self.screen.fill(WHITE)  # 必ずクリア
    # 描画処理
    # flip() は BaseGame で呼ばれる
```

### 問題: アルファ（透明度）が効かない

**原因**: `SRCALPHA` フラグを指定していない

**解決策**:
```python
# 悪い例
surface = pygame.Surface((100, 100))

# 良い例
surface = pygame.Surface((100, 100), pygame.SRCALPHA)
```

### 問題: 画像が荒い/ぼやける

**原因**: `scale()` で拡大している

**解決策**:
```python
# 高品質なスケーリング（ただし低速）
image = pygame.transform.smoothscale(image, (width, height))

# または、元から大きい画像を用意して縮小する
```

---

## 関連ドキュメント

- [Pygame 基礎](./pygame-basics.md) - 初期化とゲームループ
- [Pygame 音声処理](./pygame-audio.md) - 効果音との連携
- [ゲームアーキテクチャ設計](../design/game-architecture.md) - draw() の責務
