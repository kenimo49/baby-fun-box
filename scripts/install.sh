#!/bin/bash
#
# Baby Fun Box - インストールスクリプト
# Ubuntu でアプリケーションをインストールします。
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="baby-fun-box"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

echo "=========================================="
echo "Baby Fun Box - インストーラー"
echo "=========================================="
echo ""

# 1. インストールディレクトリの作成
echo "[1/4] インストールディレクトリを作成中..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# 2. ファイルのコピー
echo "[2/4] ファイルをコピー中..."

# 実行ファイルと関連ファイルをコピー
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
rm -f "$INSTALL_DIR/install.sh"  # インストーラー自体は除外
rm -f "$INSTALL_DIR/$APP_NAME.desktop"  # デスクトップファイルは別処理

# 実行権限を付与
chmod +x "$INSTALL_DIR/$APP_NAME"

echo "  -> $INSTALL_DIR にインストールしました"

# 3. アイコンのインストール
echo "[3/4] アイコンをインストール中..."

if [ -f "$INSTALL_DIR/$APP_NAME.png" ]; then
    cp "$INSTALL_DIR/$APP_NAME.png" "$ICON_DIR/"
    echo "  -> アイコンをインストールしました"
elif [ -f "$INSTALL_DIR/$APP_NAME.svg" ]; then
    # SVG を PNG に変換（可能な場合）
    SVG_ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
    mkdir -p "$SVG_ICON_DIR"
    cp "$INSTALL_DIR/$APP_NAME.svg" "$SVG_ICON_DIR/"
    echo "  -> SVG アイコンをインストールしました"
fi

# 4. デスクトップエントリの作成
echo "[4/4] デスクトップエントリを作成中..."

# パスを置換してデスクトップファイルを作成
sed "s|INSTALL_PATH|$INSTALL_DIR|g" "$SCRIPT_DIR/$APP_NAME.desktop" > "$DESKTOP_DIR/$APP_NAME.desktop"
chmod +x "$DESKTOP_DIR/$APP_NAME.desktop"

echo "  -> デスクトップエントリを作成しました"

# アイコンキャッシュを更新
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

# デスクトップデータベースを更新
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "インストール完了!"
echo "=========================================="
echo ""
echo "起動方法:"
echo "  1. アプリケーションメニューから \"Baby Fun Box\" を選択"
echo "  2. または: $INSTALL_DIR/$APP_NAME"
echo ""
echo "アンインストール:"
echo "  rm -rf $INSTALL_DIR"
echo "  rm -f $DESKTOP_DIR/$APP_NAME.desktop"
echo "  rm -f $ICON_DIR/$APP_NAME.png"
echo ""

# 起動するか確認
read -p "今すぐ起動しますか? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "起動中..."
    "$INSTALL_DIR/$APP_NAME" &
fi
