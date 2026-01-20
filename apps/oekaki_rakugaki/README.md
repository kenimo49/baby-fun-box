---
title: "Oekaki Rakugaki - おえかきらくがき"
category: game
tags: [pygame, game, toddler, 1-2years, drawing, creative]
related:
  - ../../docs/knowledge/pygame-basics.md
  - ../../docs/knowledge/pygame-input.md
  - ../../docs/design/toddler-friendly.md
  - ../../shared/README.md
---

# Oekaki Rakugaki - おえかきらくがき

## 概要

画面をなぞってカラフルな線を描いたり、スタンプを押したりする、1〜2歳児向けのお絵かきアプリです。7色パレット、3段階のペンサイズ、3種類のスタンプを搭載しています。

## 対象年齢

**1〜2歳**

### この年齢に適している理由

- **シンプルな操作**: 画面をなぞるだけで線が描ける
- **カラフルな色パレット**: 7色の大きなボタンで選びやすい
- **スタンプ機能**: 押すだけでかわいい図形（星・ハート・花）
- **即座のフィードバック**: 描くたびに「ポン」「キラキラ」音
- **失敗のない設計**: 好きなように描ける自由な空間

## 遊び方

1. 画面中央のキャンバスを指でなぞる
2. なぞった軌跡が線として描かれる
3. 下部の色ボタンで色を変更
4. サイズボタンで太さを変更
5. スタンプボタンでスタンプモードに切り替え
6. キャンバスをタップしてスタンプを押す
7. 「クリア」ボタンで白紙に戻す

## 操作方法

| 操作 | アクション |
|------|----------|
| キャンバスをドラッグ | 線を描く |
| キャンバスをタップ（スタンプモード） | スタンプを押す |
| 色ボタン | 色を選択 |
| サイズボタン | ペンサイズを変更 |
| スタンプボタン | スタンプモードに切り替え |
| クリアボタン | キャンバスを白紙に |
| 戻るボタン（左上） | ランチャーに戻る |
| ESC キー | ランチャーに戻る |

## ツール一覧

### 色パレット（7色）

| 色 | RGB |
|----|-----|
| 赤 | (255, 89, 94) |
| オレンジ | (255, 146, 76) |
| 黄 | (255, 202, 58) |
| 緑 | (138, 201, 38) |
| 青 | (25, 130, 196) |
| 紫 | (106, 76, 147) |
| ピンク | (255, 119, 168) |

### ペンサイズ（3段階）

| サイズ | ピクセル |
|--------|----------|
| 小 | 8px |
| 中 | 16px |
| 大 | 24px |

### スタンプ（3種類）

| スタンプ | 画像キー | 形状 |
|---------|---------|------|
| ほし | star | 五芒星 |
| ハート | heart | ハート形 |
| はな | flower | 5枚の花びら |

## 実行方法

### 統合アプリ経由

```bash
# プロジェクトルートから
python main.py
# ランチャーでOekakiを選択
```

### 単体実行（開発用）

```bash
# プロジェクトルートから
python apps/oekaki_rakugaki/main.py
```

## ファイル構成

```
oekaki_rakugaki/
├── __init__.py      # モジュール初期化
├── main.py          # 単体実行用エントリーポイント
├── game.py          # OekakiRakugakiGame クラス（BaseGame継承）
├── README.md        # このファイル
└── assets/          # リソース
    ├── images/      # スタンプ画像（star.png など）
    └── sounds/      # 効果音（pop.wav, sparkle.wav など）
```

## 技術的な詳細

### クラス構成

```
OekakiRakugakiGame (BaseGame)  - ゲーム全体の管理
├── Stamp                      - スタンプデータ（名前、画像キー、描画関数）
└── canvas (pygame.Surface)    - 描画用キャンバス
```

### レイアウト定数

```python
HEADER_HEIGHT = 70      # ヘッダー（タイトル、クリアボタン）
TOOLBAR_HEIGHT = 110    # ツールバー（色、サイズ、スタンプ）
CANVAS_MARGIN = 10      # キャンバスの余白
```

### 特徴

- **BaseGame 継承**: ランチャーからの統一的な呼び出しに対応
- **専用キャンバス**: ツールバーとは別のサーフェスに描画
- **滑らかな線**: 連続したドラッグを線で接続 + 端を丸く処理
- **プロシージャル効果音**: ポップ音、キラキラ音を生成
- **カスタムアセット対応**: `assets/` にスタンプ画像を配置すれば優先使用

### 描画処理

```python
# ドラッグ中の線描画
pygame.draw.line(
    self.canvas,
    self.current_color,
    self.last_pos,
    canvas_pos,
    self.current_size,
)
# 端を丸くする
pygame.draw.circle(
    self.canvas, self.current_color, canvas_pos, self.current_size // 2
)
```

### スタンプのプリミティブ描画

カスタム画像がない場合、コードで図形を描画：

```python
# 星の描画例
def _draw_star(self, surface, x, y, size, color):
    points = []
    for i in range(5):
        # 外側の点
        angle = math.radians(i * 72 - 90)
        points.append((x + math.cos(angle) * size, y + math.sin(angle) * size))
        # 内側の点
        angle = math.radians(i * 72 - 90 + 36)
        points.append((x + math.cos(angle) * size * 0.4, y + math.sin(angle) * size * 0.4))
    pygame.draw.polygon(surface, color, points)
```

## 今後の拡張案

- [ ] タッチスクリーン対応の最適化
- [ ] 消しゴムツール
- [ ] スタンプの種類追加（動物、乗り物など）
- [ ] 背景色の変更
- [ ] 作品の保存機能
- [ ] アンドゥ/リドゥ機能
- [ ] アイコン画像の追加

## 関連ドキュメント

- [Pygame 基礎](../../docs/knowledge/pygame-basics.md) - サーフェスの操作
- [Pygame 入力処理](../../docs/knowledge/pygame-input.md) - ドラッグ検出
- [幼児向け UX 設計](../../docs/design/toddler-friendly.md) - フィードバック設計
- [Shared Library API](../../shared/README.md) - BackButton コンポーネント
