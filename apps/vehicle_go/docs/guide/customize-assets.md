---
title: "カスタマイズガイド - のりものビュンビュン"
category: guide
tags: [vehicle, customize, assets, images, sounds]
related:
  - ../README.md
  - how-to-play.md
---

# のりものビュンビュン カスタマイズガイド

## 概要

デフォルトでは Pygame プリミティブで乗り物を描画し、手続き的に音声を生成しています。
カスタム画像や音声ファイルを追加することで、見た目や音をカスタマイズできます。

## ディレクトリ構造

```
apps/vehicle_go/
├── assets/
│   ├── images/     # カスタム画像
│   │   ├── car.png
│   │   ├── bus.png
│   │   └── ...
│   └── sounds/     # カスタム音声
│       ├── car.wav
│       ├── bus.wav
│       └── ...
└── game.py
```

## 画像のカスタマイズ

### 対応フォーマット

- **PNG** (推奨、透過対応)
- **JPG**
- **BMP**

### 推奨サイズ

| 乗り物タイプ | 推奨サイズ | 備考 |
|-------------|-----------|------|
| 地上車両 | 150x80 px | 車、バス、消防車等 |
| 電車 | 300x60 px | 3両編成を想定 |
| 飛行機 | 120x100 px | 翼を含む |
| 船 | 150x80 px | 船体 |

### ファイル名規則

```
{vehicle_key}.png
```

| 乗り物 | ファイル名 |
|--------|-----------|
| くるま | `car.png` |
| バス | `bus.png` |
| でんしゃ | `train.png` |
| しょうぼうしゃ | `firetruck.png` |
| ひこうき | `airplane.png` |
| きゅうきゅうしゃ | `ambulance.png` |
| バイク | `motorcycle.png` |
| ふね | `ship.png` |

### 画像作成のコツ

1. **背景は透過**にする（PNG形式）
2. **左向き**で作成（走行時に右向きに反転）
3. **明るい色**を使用（幼児が認識しやすい）
4. **シンプルな形状**を心がける

## 音声のカスタマイズ

### 対応フォーマット

- **WAV** (推奨)
- **OGG**
- **MP3**

### 推奨仕様

| 項目 | 推奨値 |
|------|--------|
| サンプルレート | 44100 Hz |
| ビット深度 | 16-bit |
| チャンネル | モノラル or ステレオ |
| 長さ | 1〜3秒 |

### ファイル名規則

```
{vehicle_key}.wav
```

| 乗り物 | ファイル名 | デフォルトの音 |
|--------|-----------|---------------|
| くるま | `car.wav` | エンジン音（中音） |
| バス | `bus.wav` | エンジン音（低音） |
| でんしゃ | `train.wav` | ガタンゴトン |
| しょうぼうしゃ | `firetruck.wav` | サイレン |
| ひこうき | `airplane.wav` | ジェット音 |
| きゅうきゅうしゃ | `ambulance.wav` | サイレン |
| バイク | `motorcycle.wav` | エンジン音（高音） |
| ふね | `ship.wav` | 汽笛 |

### 音声作成のコツ

1. **ループ可能**な音声が理想的
2. **急な音量変化**を避ける
3. **子供が怖がらない**音を選ぶ
4. **フェードイン/アウト**を追加

## コード側の対応

現在の実装では、カスタムアセットの読み込みは自動では行われません。
カスタムアセットを使用する場合は、`game.py` を以下のように修正します。

### 画像読み込みの追加

```python
def _load_custom_image(self, key: str) -> pygame.Surface | None:
    """カスタム画像を読み込む"""
    for ext in ['png', 'jpg', 'bmp']:
        path = Path(__file__).parent / f"assets/images/{key}.{ext}"
        if path.exists():
            return pygame.image.load(str(path)).convert_alpha()
    return None
```

### 音声読み込みの追加

```python
def _load_custom_sound(self, key: str) -> pygame.mixer.Sound | None:
    """カスタム音声を読み込む"""
    for ext in ['wav', 'ogg', 'mp3']:
        path = Path(__file__).parent / f"assets/sounds/{key}.{ext}"
        if path.exists():
            return pygame.mixer.Sound(str(path))
    return None
```

## フリー素材リソース

### 画像素材

- [いらすとや](https://www.irasutoya.com/) - 日本語フリー素材
- [OpenGameArt](https://opengameart.org/) - ゲーム用素材
- [Kenney](https://kenney.nl/) - ゲームアセット

### 音声素材

- [効果音ラボ](https://soundeffect-lab.info/) - 日本語フリー素材
- [Freesound](https://freesound.org/) - クリエイティブ・コモンズ
- [DOVA-SYNDROME](https://dova-s.jp/) - フリー BGM・効果音

## 注意事項

1. **ライセンスを確認**してから素材を使用してください
2. **商用利用**の可否を確認してください
3. **クレジット表記**が必要な素材もあります
4. **ファイルサイズ**は適度に抑えてください（画像は 500KB 以下推奨）
