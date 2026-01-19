---
title: "ベビーピアノ - ドキュメント"
category: index
tags: [baby-piano, documentation, music]
related:
  - ../game.py
  - ../../../docs/README.md
---

# ベビーピアノ - ドキュメント

「ベビーピアノ」ゲームに関するドキュメントです。

## クイックナビゲーション

| 目的 | 参照先 |
|------|--------|
| 遊び方を知りたい | [guide/how-to-play.md](./guide/how-to-play.md) |
| 新しい曲を追加したい | [guide/add-songs.md](./guide/add-songs.md) |
| 音声ファイルを差し替えたい | [guide/customize-sounds.md](./guide/customize-sounds.md) |
| ゲームの実装を理解したい | [../game.py](../game.py) |

## ディレクトリ構成

```
apps/baby_piano/
├── docs/
│   ├── README.md                 # このファイル
│   └── guide/
│       ├── how-to-play.md        # 遊び方ガイド
│       ├── add-songs.md          # 曲の追加方法
│       └── customize-sounds.md   # 音声カスタマイズ
├── assets/
│   └── sounds/                   # カスタム音声ファイル
├── game.py                       # ゲーム本体
├── main.py                       # 単体実行用
└── __init__.py
```

## ゲーム概要

| 項目 | 内容 |
|------|------|
| **対象年齢** | 1〜2歳 |
| **目的** | 音感と色の認識を育む |
| **モード** | じゆうモード / おんがくモード |
| **収録曲** | きらきら星、かえるのうた、ちょうちょう、メリーさんのひつじ |

## 関連リンク

- [Baby Fun Box 全体ドキュメント](../../../docs/README.md)
- [新しいゲームの追加方法](../../../docs/guide/new-game.md)
