# Baby Fun Box

1〜2歳の幼児向けのゲームアプリを収録した Ubuntu アプリケーションです。

Pygame を使用したシンプルで安全なゲーム体験を提供します。

---

## ⚡ クイックスタート

### 必要環境

- Python 3.10 以上
- Ubuntu 22.04 以上（推奨）

### インストール & 実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# アプリケーション起動（ランチャー）
python main.py

# 特定のゲームを単体で実行
python apps/{game-name}/main.py
```

---

## 🎮 収録ゲーム

| ゲーム名 | 説明 | 対象年齢 |
|---------|------|---------|
| balloon_pop | 風船をタップして弾けさせるゲーム | 1〜2歳 |
| animal_touch | 動物をタップして鳴き声を聞くゲーム | 1〜2歳 |
| baby_piano | シンプルなピアノゲーム | 1〜2歳 |
| mogura_tataki | もぐらたたきゲーム | 1〜2歳 |
| oekaki_rakugaki | お絵かき・らくがきゲーム | 1〜2歳 |
| vehicle_go | 乗り物を動かすゲーム | 1〜2歳 |

---

## 📂 プロジェクト構造

```
baby-fun-box/
├── README.md              # このファイル
├── CLAUDE.md              # AI アシスタント向けガイドライン
├── main.py                # アプリケーションエントリーポイント
├── apps/                  # ゲームアプリケーション
│   ├── launcher/          # ゲーム選択画面
│   └── {game-name}/       # 各ゲームのディレクトリ
├── docs/                  # ドキュメント
│   ├── knowledge/         # 実践的知識（HOW）
│   ├── design/            # 設計思想（WHY）
│   └── guide/             # ガイドライン
├── scripts/               # ビルド・配布スクリプト
└── shared/                # 共有ライブラリ
```

---

## 📚 ドキュメント

### 目的別ナビゲーション

| 目的 | 参照先 |
|------|--------|
| 新規ゲーム追加 | [docs/guide/new-game.md](./docs/guide/new-game.md) |
| 配布パッケージ作成 | [docs/guide/create-package.md](./docs/guide/create-package.md) |
| Ubuntu インストール | [docs/guide/ubuntu-installation.md](./docs/guide/ubuntu-installation.md) |
| 実機への導入 | [docs/guide/deploy-to-device.md](./docs/guide/deploy-to-device.md) |
| Pygame 基礎学習 | [docs/knowledge/](./docs/knowledge/) |
| 設計思想の理解 | [docs/design/](./docs/design/) |
| ドキュメント全体 | [docs/README.md](./docs/README.md) |

### AI アシスタント向け

Claude や他の AI アシスタントを使用する場合は、**[CLAUDE.md](./CLAUDE.md)** を参照してください。

---

## 🛠️ 開発

### テスト実行

```bash
pytest
```

### コードスタイル

- フォーマッター: Black
- 型チェック: mypy
- docstring: Google スタイル

---

## 📦 配布

### Ubuntu パッケージ作成

```bash
./scripts/build.sh
```

### インストール

```bash
./scripts/install.sh
```

詳細は [配布ガイド](./docs/guide/create-package.md) を参照してください。

---

## 🤝 貢献

新しいゲームの追加やバグ修正の貢献を歓迎します。

1. Issue を作成して変更内容を議論
2. フォークしてブランチを作成
3. 変更を実装してテストを追加
4. Pull Request を作成

### PR タイトル形式

```
{fix or feat}: {簡潔な説明}
```

---

## 📄 ライセンス

MIT License
