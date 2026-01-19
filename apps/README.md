# Apps - Pygame ゲームアプリケーション

このディレクトリには、Baby Fun Box の各ゲームが格納されています。

## ディレクトリ構造

```
apps/
├── launcher/             # ゲーム選択画面
│   ├── __init__.py
│   └── launcher.py
└── {game_name}/          # 各ゲームのディレクトリ
    ├── __init__.py       # モジュール初期化
    ├── main.py           # 単体実行用エントリーポイント
    ├── game.py           # ゲームクラス（BaseGame継承）
    ├── assets/           # 画像・音声リソース
    │   ├── images/
    │   └── sounds/
    └── README.md         # ゲーム固有のドキュメント
```

## ゲーム一覧

| ゲーム名 | 説明 | 対象年齢 |
|---------|------|---------|
| balloon_pop | 風船をタップして弾けさせるゲーム | 1〜2歳 |
| animal_touch | 動物をタップして鳴き声を聞くゲーム | 1〜2歳 |

## 実行方法

### 統合アプリ（ランチャー経由）

```bash
# プロジェクトルートから
python main.py
```

### 単体実行（開発・デバッグ用）

```bash
# 特定のゲームを単体で実行
python apps/balloon_pop/main.py
```

## 新しいゲームを追加する

1. このディレクトリに新しいフォルダを作成（名前はアンダースコア区切り）
2. `game.py` で `BaseGame` を継承したゲームクラスを作成
3. `main.py` で単体実行用のエントリーポイントを作成
4. `__init__.py` でゲームクラスをエクスポート
5. `README.md` でゲームの概要を記述
6. ルートの `main.py` でゲームを登録

詳細は [../docs/guide/new-game.md](../docs/guide/new-game.md) を参照してください。
