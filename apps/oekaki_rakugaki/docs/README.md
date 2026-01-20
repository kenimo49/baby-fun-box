---
title: "Oekaki Rakugaki - おえかきらくがき"
category: game
tags: [drawing, creative, toddler, pygame]
related:
  - ../game.py
  - guide/how-to-play.md
  - guide/customize-assets.md
  - knowledge/drawing-system.md
  - design/toddler-ux.md
---

# Oekaki Rakugaki - おえかきらくがき

画面を指でなぞってカラフルな線を描くお絵かきアプリ。1〜2歳児向けに、指先の発達と色の認識を促します。

## 概要

- **対象年齢**: 1〜2歳
- **目的**: 指先の発達・色の認識・創造性
- **操作**: タッチ/ドラッグ

## 機能一覧

| 機能 | 説明 |
|------|------|
| フリードロー | 指でなぞると線が描ける |
| 7色パレット | カラフルな色から選択 |
| 3段階サイズ | 細・中・太のペンサイズ |
| スタンプ | 星・ハート・花をタップで配置 |
| クリア | キャンバスをリセット |

## ドキュメント

### ガイド (guide/)

| ドキュメント | 内容 |
|--------------|------|
| [遊び方](guide/how-to-play.md) | 基本的な遊び方 |
| [カスタマイズ](guide/customize-assets.md) | スタンプ画像・音声の変更方法 |

### 技術詳細 (knowledge/)

| ドキュメント | 内容 |
|--------------|------|
| [描画システム](knowledge/drawing-system.md) | キャンバス・ストローク処理の仕組み |

### 設計思想 (design/)

| ドキュメント | 内容 |
|--------------|------|
| [幼児UX設計](design/toddler-ux.md) | 1〜2歳児向けUI設計の考え方 |

## 単体実行

```bash
python apps/oekaki_rakugaki/main.py
```

## 技術仕様

- 描画: pygame.Surface をキャンバスとして使用
- 入力: MOUSEMOTION/MOUSEBUTTONDOWN/UP
- 音声: 手続き的生成（ポップ音・キラキラ音）
- スタンプ: Pygame プリミティブ描画（カスタム画像対応）
