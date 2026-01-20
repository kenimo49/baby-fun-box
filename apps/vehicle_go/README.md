---
title: "Vehicle Go - のりものビュンビュン"
category: game
tags: [pygame, game, toddler, 1-2years, vehicles, animation]
related:
  - ../../docs/knowledge/pygame-basics.md
  - ../../docs/knowledge/pygame-audio.md
  - ../../docs/design/toddler-friendly.md
  - ../../shared/README.md
---

# Vehicle Go - のりものビュンビュン

## 概要

カラフルな乗り物アイコンをタップすると、エンジン音やサイレンと共に画面を横切って走り出す、1〜2歳児向けの乗り物ゲームです。8種類の乗り物が登場します。

## 対象年齢

**1〜2歳**

### この年齢に適している理由

- **大きなアイコン**: 140px の大きなボタンで押しやすい
- **カラフルなデザイン**: 各乗り物が異なる鮮やかな色
- **即座のフィードバック**: タップと同時に音 + アニメーション開始
- **乗り物の多様性**: 車、バス、電車、飛行機、船など馴染みのある乗り物
- **繰り返しの楽しさ**: 何度でもタップして走らせられる

## 遊び方

1. 画面上部の乗り物アイコンから好きなものをタップ
2. 選んだ乗り物が画面下部を走り出す
3. エンジン音やサイレンが鳴る
4. 乗り物が画面右端に消えるまでアニメーション
5. 別の乗り物をタップして繰り返し

## 操作方法

| 操作 | アクション |
|------|----------|
| 乗り物アイコンをタップ | 乗り物を走らせる |
| 戻るボタン（左上） | ランチャーに戻る |
| ESC キー | ランチャーに戻る |

## 乗り物一覧（8種類）

| 乗り物 | 色 | 特徴 | 移動タイプ |
|--------|-----|------|-----------|
| くるま | 赤 | エンジン音、車輪回転 | 水平 |
| バス | 黄 | 低いエンジン音、ゆっくり | 水平 |
| でんしゃ | 緑 | 3両編成、線路音 | 水平 |
| しょうぼうしゃ | 赤 | サイレン、警告灯点滅 | 水平 |
| ひこうき | 白/青 | 高いエンジン音、斜め上昇 | 斜め上 |
| きゅうきゅうしゃ | 白/赤 | サイレン、赤十字マーク | 水平 |
| バイク | 紫 | 高めのエンジン音、高速 | 水平 |
| ふね | 青 | 汽笛、波に揺れる | 波状 |

## 実行方法

### 統合アプリ経由

```bash
# プロジェクトルートから
python main.py
# ランチャーでVehicle Goを選択
```

### 単体実行（開発用）

```bash
# プロジェクトルートから
python apps/vehicle_go/main.py
```

## ファイル構成

```
vehicle_go/
├── __init__.py      # モジュール初期化
├── main.py          # 単体実行用エントリーポイント
├── game.py          # VehicleGoGame クラス（BaseGame継承）
├── README.md        # このファイル
└── assets/          # リソース
    ├── images/      # 乗り物画像（car.png など）
    └── sounds/      # 効果音（car.wav など）
```

## 技術的な詳細

### クラス構成

```
VehicleGoGame (BaseGame)  - ゲーム全体の管理
├── Vehicle               - 乗り物データ（名前、色、速度、描画関数など）
└── Particle              - パーティクルエフェクト（排気煙、水しぶきなど）
```

### 乗り物データ構造

```python
@dataclass
class Vehicle:
    name: str                    # 日本語名
    image_key: str               # 画像/音声ファイルのキー
    color: tuple[int, int, int]  # メインカラー
    secondary_color: tuple       # サブカラー
    sound_freq: float            # エンジン音の周波数
    speed: float                 # 移動速度（px/s）
    movement_type: str           # "horizontal" / "diagonal_up" / "wave"
    draw_func: Callable          # 描画関数
    y_offset: float = 0          # Y座標オフセット
```

### 移動タイプ

| タイプ | 動作 | 使用乗り物 |
|--------|------|-----------|
| horizontal | 水平に移動 | 車、バス、電車、消防車、救急車、バイク |
| diagonal_up | 斜め上に上昇 | 飛行機 |
| wave | 波状に揺れながら移動 | 船 |

### パーティクルエフェクト

| タイプ | 色 | 使用場面 |
|--------|-----|---------|
| exhaust | 灰色 | 車両の排気煙 |
| water | 水色 | 船の水しぶき |
| cloud | 白 | 飛行機の飛行機雲 |

### 特徴

- **BaseGame 継承**: ランチャーからの統一的な呼び出しに対応
- **プロシージャル効果音**: エンジン音、サイレン音、汽笛を生成
- **車輪回転アニメーション**: 回転するスポークを描画
- **警告灯点滅**: 消防車・救急車の赤/青ライト
- **波のアニメーション**: 船が揺れながら進む
- **カスタムアセット対応**: `assets/` に画像/音声を配置すれば優先使用

### 音声生成

```python
# エンジン音の生成
def _create_engine_sound(self, freq: float, duration: float = 1.5):
    # 複数の周波数を組み合わせ
    value = math.sin(2 * math.pi * freq * t)
    value += 0.5 * math.sin(2 * math.pi * freq * 1.5 * t)
    value += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
    # 振動感を追加
    value *= 1 + 0.2 * math.sin(2 * math.pi * 8 * t)

# サイレン音の生成（消防車・救急車用）
def _create_siren_sound(self, freq1: float, freq2: float):
    # 周波数を交互に切り替え
    cycle = (t * 2) % 1.0
    freq = freq1 if cycle < 0.5 else freq2
```

### レイアウト

```python
# グリッドレイアウト（2行 x 4列）
cols = 4
rows = 2
button_size = 140
spacing = 20

# アニメーション領域
animation_area_y = self.height - 200
```

## 今後の拡張案

- [ ] タッチスクリーン対応の最適化
- [ ] 乗り物の種類追加（ヘリコプター、ロケットなど）
- [ ] 背景のバリエーション（街、海、空など）
- [ ] 同時に複数の乗り物を走らせる
- [ ] 乗り物の音声カスタマイズ
- [ ] アイコン画像の追加

## 関連ドキュメント

- [Pygame 基礎](../../docs/knowledge/pygame-basics.md) - アニメーション
- [Pygame 音声処理](../../docs/knowledge/pygame-audio.md) - プロシージャル音声生成
- [幼児向け UX 設計](../../docs/design/toddler-friendly.md) - フィードバック設計
- [Shared Library API](../../shared/README.md) - BackButton コンポーネント
