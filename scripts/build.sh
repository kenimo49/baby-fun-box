#!/bin/bash
#
# Baby Fun Box - ビルドスクリプト
# Ubuntu 22.04 で PyInstaller を使って実行ファイルを生成します。
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build"

echo "=========================================="
echo "Baby Fun Box - Build Script"
echo "=========================================="

cd "$PROJECT_DIR"

# 1. 依存パッケージの確認
echo ""
echo "[1/5] 依存パッケージを確認中..."

if ! command -v python3 &> /dev/null; then
    echo "エラー: python3 がインストールされていません"
    exit 1
fi

# 2. 仮想環境のセットアップ
echo ""
echo "[2/5] Python 仮想環境をセットアップ中..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

# 3. SVG を PNG に変換（アイコン用）
echo ""
echo "[3/5] アイコンを準備中..."

if [ -f "baby-fun-box.svg" ] && ! [ -f "baby-fun-box.png" ]; then
    # ImageMagick または Inkscape で変換
    if command -v convert &> /dev/null; then
        convert -background none -density 256 baby-fun-box.svg baby-fun-box.png
        echo "  -> SVG を PNG に変換しました (ImageMagick)"
    elif command -v inkscape &> /dev/null; then
        inkscape baby-fun-box.svg -o baby-fun-box.png -w 256 -h 256
        echo "  -> SVG を PNG に変換しました (Inkscape)"
    else
        echo "  -> 警告: ImageMagick/Inkscape がないため PNG 変換をスキップ"
        echo "     sudo apt install imagemagick または inkscape をインストールしてください"
    fi
fi

# 4. PyInstaller でビルド
echo ""
echo "[4/5] PyInstaller でビルド中..."

# クリーンアップ
rm -rf "$BUILD_DIR" "$DIST_DIR"

# PyInstaller 実行
pyinstaller \
    --name="baby-fun-box" \
    --onedir \
    --windowed \
    --add-data="apps:apps" \
    --add-data="shared:shared" \
    --hidden-import=pygame \
    --hidden-import=pygame.mixer \
    --hidden-import=pygame.font \
    --hidden-import=pygame.image \
    --hidden-import=pygame.transform \
    --hidden-import=pygame.draw \
    --hidden-import=pygame.display \
    --hidden-import=pygame.event \
    --hidden-import=pygame.time \
    --hidden-import=pygame.mouse \
    --hidden-import=pygame.surface \
    --hidden-import=pygame.rect \
    --clean \
    --noconfirm \
    main.py

echo "  -> ビルド完了"

# 5. 配布パッケージの作成
echo ""
echo "[5/5] 配布パッケージを作成中..."

PACKAGE_DIR="$DIST_DIR/baby-fun-box-package"
mkdir -p "$PACKAGE_DIR"

# ファイルをコピー
cp -r "$DIST_DIR/baby-fun-box/"* "$PACKAGE_DIR/"

# アイコンとデスクトップエントリをコピー
if [ -f "baby-fun-box.png" ]; then
    cp baby-fun-box.png "$PACKAGE_DIR/"
fi
if [ -f "baby-fun-box.svg" ]; then
    cp baby-fun-box.svg "$PACKAGE_DIR/"
fi
cp scripts/install.sh "$PACKAGE_DIR/"
cp scripts/baby-fun-box.desktop "$PACKAGE_DIR/"

# 実行権限を付与
chmod +x "$PACKAGE_DIR/baby-fun-box"
chmod +x "$PACKAGE_DIR/install.sh"

echo ""
echo "=========================================="
echo "ビルド完了!"
echo "=========================================="
echo ""
echo "配布パッケージ: $PACKAGE_DIR"
echo ""
echo "含まれるファイル:"
ls -la "$PACKAGE_DIR"
echo ""
echo "インストール方法:"
echo "  1. baby-fun-box-package フォルダを対象PCにコピー"
echo "  2. cd baby-fun-box-package && ./install.sh"
echo ""
