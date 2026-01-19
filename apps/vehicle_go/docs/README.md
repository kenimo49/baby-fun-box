---
title: "Vehicle Go - のりものビュンビュン"
category: game
tags: [vehicle, animation, toddler, pygame]
related:
  - ../game.py
  - guide/how-to-play.md
  - guide/customize-assets.md
---

# Vehicle Go - のりものビュンビュン

乗り物をタップすると画面を走り抜けるゲーム。1〜2歳児向けに、乗り物への興味を育みます。

## 概要

- **対象年齢**: 1〜2歳
- **目的**: 乗り物への興味・認識力の発達
- **操作**: タップのみ

## 乗り物一覧

| 乗り物 | 日本語名 | 動きのタイプ |
|--------|----------|--------------|
| Car | くるま | 水平走行 |
| Bus | バス | 水平走行 |
| Train | でんしゃ | 水平走行 |
| Fire Truck | しょうぼうしゃ | 水平走行 |
| Airplane | ひこうき | 斜め上飛行 |
| Ambulance | きゅうきゅうしゃ | 水平走行 |
| Motorcycle | バイク | 水平走行 |
| Ship | ふね | 波形移動 |

## ドキュメント

| ドキュメント | 内容 |
|--------------|------|
| [遊び方](guide/how-to-play.md) | 基本的な遊び方 |
| [カスタマイズ](guide/customize-assets.md) | 画像・音声の変更方法 |

## 単体実行

```bash
python apps/vehicle_go/main.py
```

## 技術仕様

- 描画: Pygame プリミティブによるベクター描画
- 音声: 手続き的生成（ノイズ + 周波数変調）
- アニメーション: フレームベース（60 FPS）
- パーティクル: 排気ガス、水しぶき、雲
