---
title: "ビルドとデプロイ"
category: guide
tags: [build, deploy, pyinstaller, ubuntu]
related:
  - ../../scripts/build.sh
  - ../../scripts/install.sh
---

# ビルドとデプロイガイド

Baby Fun Box を Ubuntu PC 向けにビルド・配布する手順です。

## 概要

PyInstaller を使って、Python 環境不要の実行ファイルを生成します。

```
開発PC (Ubuntu)          →  配布パッケージ  →  対象PC (Ubuntu)
                                  │
ソースコード                      │          アプリ一覧に表示
   ↓                              ↓              ↓
build.sh                   baby-fun-box-package/  install.sh
   ↓                         ├── baby-fun-box    → ~/.local/share/baby-fun-box/
PyInstaller                  ├── baby-fun-box.png
   ↓                         ├── baby-fun-box.desktop
dist/baby-fun-box-package/   └── install.sh
```

---

## ビルド手順（開発PC）

### 前提条件

```bash
# Ubuntu 22.04
# Python 3.10+
# Git
```

### 1. リポジトリをクローン

```bash
git clone https://github.com/kenimo49/baby-fun-box.git
cd baby-fun-box
```

### 2. ビルドスクリプトを実行

```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

### 3. 配布パッケージを確認

```bash
ls -la dist/baby-fun-box-package/
```

出力例:
```
baby-fun-box           # 実行ファイル
baby-fun-box.png       # アイコン
baby-fun-box.desktop   # デスクトップエントリ
install.sh             # インストーラー
_internal/             # 依存ライブラリ
```

---

## インストール手順（対象PC）

### 1. パッケージをコピー

USB メモリやネットワーク経由で `baby-fun-box-package/` フォルダをコピー。

### 2. インストーラーを実行

```bash
cd baby-fun-box-package
chmod +x install.sh
./install.sh
```

### 3. 起動

- **アプリケーションメニュー** から「Baby Fun Box」を選択
- または: `~/.local/share/baby-fun-box/baby-fun-box`

---

## ビルドスクリプトの詳細

### build.sh の処理内容

1. **依存パッケージの確認**: Python3 の存在確認
2. **仮想環境のセットアップ**: venv 作成、pip install
3. **アイコンの準備**: SVG → PNG 変換（ImageMagick/Inkscape）
4. **PyInstaller でビルド**: --onedir モードで実行ファイル生成
5. **配布パッケージの作成**: 必要ファイルを dist/ にまとめる

### PyInstaller オプション

| オプション | 説明 |
|-----------|------|
| `--onedir` | 1つのディレクトリにまとめる（起動が速い） |
| `--windowed` | コンソールウィンドウを表示しない |
| `--add-data` | apps/ と shared/ を含める |
| `--hidden-import` | pygame のモジュールを明示的に含める |

---

## トラブルシューティング

### ビルドエラー: pygame が見つからない

```bash
# 仮想環境が有効か確認
source venv/bin/activate
pip install pygame
```

### ビルドエラー: SDL2 関連

```bash
sudo apt install libsdl2-dev libsdl2-mixer-dev
```

### 実行時エラー: 日本語が表示されない

対象PCで日本語フォントをインストール:

```bash
sudo apt install fonts-noto-cjk
```

### 実行時エラー: 音が出ない

```bash
# PulseAudio を確認
pulseaudio --start

# ALSA デバイスを確認
aplay -l
```

### アイコンが表示されない

```bash
# アイコンキャッシュを更新
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
```

---

## アンインストール

```bash
rm -rf ~/.local/share/baby-fun-box
rm -f ~/.local/share/applications/baby-fun-box.desktop
rm -f ~/.local/share/icons/hicolor/256x256/apps/baby-fun-box.png
```

---

## 配布パッケージの内容

| ファイル | 説明 |
|---------|------|
| `baby-fun-box` | メイン実行ファイル |
| `_internal/` | Python ランタイムと依存ライブラリ |
| `baby-fun-box.png` | アプリケーションアイコン (256x256) |
| `baby-fun-box.desktop` | デスクトップエントリ定義 |
| `install.sh` | インストーラースクリプト |

---

## 開発者向け情報

### 手動ビルド

```bash
# 仮想環境を有効化
source venv/bin/activate

# PyInstaller を直接実行
pyinstaller --name="baby-fun-box" --onedir --windowed \
  --add-data="apps:apps" --add-data="shared:shared" \
  main.py
```

### クリーンビルド

```bash
rm -rf build/ dist/ *.spec
./scripts/build.sh
```
