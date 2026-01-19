---
title: "新しいゲームの追加方法"
category: guide
tags: [pygame, game, tutorial]
related:
  - ../knowledge/pygame-basics.md
  - ../_templates/game.md
---

# 新しいゲームの追加方法

## 概要

Baby Fun Box に新しいゲームを追加する手順を説明します。

## 手順

### 1. ディレクトリを作成

```bash
mkdir -p apps/{game-name}/assets/{images,sounds}
```

### 2. main.py を作成

```python
"""
{ゲーム名} - {簡単な説明}
"""
import pygame
from pygame.locals import *


def main() -> None:
    """ゲームのエントリーポイント"""
    pygame.init()

    # 画面設定
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("{ゲーム名}")
    clock = pygame.time.Clock()

    running = True
    while running:
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # 更新処理
        # ...

        # 描画処理
        screen.fill((0, 0, 0))
        # ...

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
```

### 3. README.md を作成

テンプレート（[../_templates/game.md](../_templates/game.md)）を参考に作成してください。

### 4. テストを追加（推奨）

```python
# apps/{game-name}/tests/test_main.py
import pytest


def test_game_initialization():
    """ゲームが正常に初期化できることを確認"""
    # テストコード
    pass
```

## チェックリスト

- [ ] `apps/{game-name}/main.py` が存在する
- [ ] `apps/{game-name}/README.md` が存在する
- [ ] `python apps/{game-name}/main.py` で起動できる
- [ ] ESC キーまたは閉じるボタンで終了できる

## 関連ドキュメント

- [Pygame 基礎](../knowledge/pygame-basics.md)
- [ゲームテンプレート](../_templates/game.md)
