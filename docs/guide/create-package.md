---
title: "配布パッケージ作成ガイド"
category: guide
tags: [build, package, pyinstaller]
related:
  - ./build-and-deploy.md
  - ./ubuntu-installation.md
  - ../../scripts/build.sh
---

# 配布パッケージ作成ガイド

Baby Fun Box の配布用パッケージを作成する手順です。

---

## 概要

PyInstaller を使って、Python 環境不要の実行ファイルを生成します。

```
ソースコード → build.sh → dist/baby-fun-box-package/ → tar.gz
```

---

## 前提条件

| 項目 | 要件 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| Python | 3.10 以上 |
| ディスク容量 | 500MB 以上の空き |

---

## クイックスタート

### 3 ステップでパッケージ作成

```bash
# 1. リポジトリをクローン（初回のみ）
git clone https://github.com/kenimo49/baby-fun-box.git
cd baby-fun-box

# 2. ビルドスクリプトを実行
chmod +x scripts/build.sh
./scripts/build.sh

# 3. tar.gz を作成
cd dist
tar -czf baby-fun-box-ubuntu22.04.tar.gz baby-fun-box-package/
```

### 出力ファイル

```
dist/
├── baby-fun-box-package/        # 配布フォルダ
│   ├── baby-fun-box             # 実行ファイル
│   ├── baby-fun-box.png         # アイコン
│   ├── baby-fun-box.desktop     # デスクトップエントリ
│   ├── install.sh               # インストーラー
│   └── _internal/               # 依存ライブラリ
└── baby-fun-box-ubuntu22.04.tar.gz  # 配布用アーカイブ
```

---

## 詳細手順

### 1. 依存パッケージのインストール

```bash
# 必須パッケージ
sudo apt install python3-venv python3-pip

# アイコン生成用（オプション）
sudo apt install imagemagick
# または
sudo apt install inkscape
```

### 2. ビルドスクリプトの実行

```bash
cd baby-fun-box
./scripts/build.sh
```

スクリプトが自動的に以下を行います：

1. Python 仮想環境を作成
2. 依存パッケージをインストール
3. SVG アイコンを PNG に変換
4. PyInstaller でビルド
5. 配布パッケージを作成

### 3. ビルド結果の確認

```bash
ls -la dist/baby-fun-box-package/
```

期待される出力：
```
-rwxr-xr-x  baby-fun-box
-rw-r--r--  baby-fun-box.png
-rw-r--r--  baby-fun-box.desktop
-rwxr-xr-x  install.sh
drwxr-xr-x  _internal/
```

### 4. 配布用アーカイブの作成

```bash
cd dist
tar -czf baby-fun-box-ubuntu22.04.tar.gz baby-fun-box-package/
```

---

## 配布方法

### USB メモリで配布

```bash
# USB をマウント（例: /media/usb）
cp dist/baby-fun-box-ubuntu22.04.tar.gz /media/usb/
```

### ネットワーク経由

```bash
# SCP で転送
scp dist/baby-fun-box-ubuntu22.04.tar.gz user@target-pc:~/
```

---

## トラブルシューティング

### ビルドエラー: pygame が見つからない

```bash
# 仮想環境を再作成
rm -rf venv
./scripts/build.sh
```

### ビルドエラー: SDL2 関連

```bash
sudo apt install libsdl2-dev libsdl2-mixer-dev
```

### アイコンが PNG に変換されない

```bash
# Pillow で手動生成
source venv/bin/activate
python scripts/generate_icon.py
```

### ビルドが遅い / メモリ不足

PyInstaller は初回ビルドに時間がかかります（5〜10分）。
メモリ 4GB 以上を推奨します。

---

## クリーンビルド

キャッシュを削除して最初からビルドする場合：

```bash
rm -rf build/ dist/ venv/ *.spec
./scripts/build.sh
```

---

## 関連ドキュメント

- [インストールガイド](./ubuntu-installation.md) - 対象 PC でのインストール手順
- [ビルドとデプロイ詳細](./build-and-deploy.md) - 技術的な詳細情報
