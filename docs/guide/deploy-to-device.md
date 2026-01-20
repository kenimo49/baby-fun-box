---
title: "実機への導入ガイド"
category: guide
tags: [deploy, ubuntu, device, ssh]
related:
  - ./create-package.md
  - ./ubuntu-installation.md
  - ./build-and-deploy.md
---

# 実機への導入ガイド

開発環境から実際の Ubuntu PC に Baby Fun Box を導入する手順です。

---

## 重要: GLIBC 互換性について

PyInstaller でビルドしたパッケージは **ビルド環境の GLIBC バージョン** に依存します。

| ビルド環境 | 対象環境 | 結果 |
|-----------|---------|------|
| Ubuntu 24.04 (GLIBC 2.39) | Ubuntu 22.04 (GLIBC 2.35) | ❌ 動作しない |
| Ubuntu 22.04 (GLIBC 2.35) | Ubuntu 22.04 (GLIBC 2.35) | ✅ 動作する |

**対策**: 対象マシンと同じ OS バージョンでビルドする必要があります。

---

## 導入方法

### 方法 A: 対象マシンで直接ビルド（推奨）

対象マシンに SSH 接続してビルドする方法です。

### 方法 B: 同一バージョンの VM/Docker でビルド

開発マシン上で Ubuntu 22.04 の環境を用意してビルドする方法です。

---

## 方法 A: 対象マシンで直接ビルド

### 前提条件

| 項目 | 要件 |
|------|------|
| 対象マシン | Ubuntu 22.04 LTS |
| ネットワーク | SSH 接続可能 |
| ツール | sshpass（開発マシン側） |

### Step 1: ソースコードをアーカイブ

```bash
cd /path/to/baby-fun-box

# venv, dist, build を除外してアーカイブ
tar --exclude='venv' --exclude='dist' --exclude='build' \
    --exclude='*.spec' --exclude='.git' --exclude='__pycache__' \
    -czf /tmp/baby-fun-box-src.tar.gz .
```

### Step 2: 対象マシンに転送

```bash
# sshpass を使う場合
sshpass -p 'PASSWORD' scp /tmp/baby-fun-box-src.tar.gz \
    USER@TARGET_IP:~/

# 通常の scp の場合
scp /tmp/baby-fun-box-src.tar.gz USER@TARGET_IP:~/
```

### Step 3: 対象マシンで依存パッケージをインストール

```bash
sshpass -p 'PASSWORD' ssh USER@TARGET_IP \
    "echo 'PASSWORD' | sudo -S apt-get update && \
     echo 'PASSWORD' | sudo -S apt-get install -y \
     python3-venv python3-pip libsdl2-dev libsdl2-mixer-dev"
```

### Step 4: 対象マシンで展開・ビルド

```bash
sshpass -p 'PASSWORD' ssh USER@TARGET_IP \
    "mkdir -p ~/baby-fun-box-build && \
     cd ~/baby-fun-box-build && \
     tar -xzf ~/baby-fun-box-src.tar.gz && \
     chmod +x scripts/build.sh && \
     ./scripts/build.sh"
```

ビルドには 5〜10 分かかります。

### Step 5: インストール

```bash
sshpass -p 'PASSWORD' ssh USER@TARGET_IP \
    "cd ~/baby-fun-box-build/dist/baby-fun-box-package && \
     ./install.sh <<< 'n'"
```

### Step 6: デスクトップショートカットを作成

```bash
sshpass -p 'PASSWORD' ssh USER@TARGET_IP \
    "cp ~/.local/share/applications/baby-fun-box.desktop ~/デスクトップ/ && \
     chmod +x ~/デスクトップ/baby-fun-box.desktop"
```

### Step 7: 動作確認

```bash
# リモートで起動
sshpass -p 'PASSWORD' ssh USER@TARGET_IP \
    "export DISPLAY=:0 && \
     ~/.local/share/baby-fun-box/baby-fun-box &"

# プロセス確認
sshpass -p 'PASSWORD' ssh USER@TARGET_IP \
    "ps aux | grep baby-fun-box | grep -v grep"
```

---

## ワンライナー（全自動導入）

以下のスクリプトで Step 1〜6 を一括実行できます。

```bash
#!/bin/bash
# deploy-to-device.sh

TARGET_IP="192.168.0.11"
TARGET_USER="timeleap"
TARGET_PASS="timeleap"
PROJECT_DIR="/path/to/baby-fun-box"

# 1. ソースをアーカイブ
cd "$PROJECT_DIR"
tar --exclude='venv' --exclude='dist' --exclude='build' \
    --exclude='*.spec' --exclude='.git' --exclude='__pycache__' \
    -czf /tmp/baby-fun-box-src.tar.gz .

# 2. 転送
sshpass -p "$TARGET_PASS" scp /tmp/baby-fun-box-src.tar.gz \
    "$TARGET_USER@$TARGET_IP":~/

# 3. 依存パッケージ
sshpass -p "$TARGET_PASS" ssh "$TARGET_USER@$TARGET_IP" \
    "echo '$TARGET_PASS' | sudo -S apt-get update && \
     echo '$TARGET_PASS' | sudo -S apt-get install -y \
     python3-venv python3-pip libsdl2-dev libsdl2-mixer-dev"

# 4. ビルド
sshpass -p "$TARGET_PASS" ssh "$TARGET_USER@$TARGET_IP" \
    "rm -rf ~/baby-fun-box-build && \
     mkdir -p ~/baby-fun-box-build && \
     cd ~/baby-fun-box-build && \
     tar -xzf ~/baby-fun-box-src.tar.gz && \
     chmod +x scripts/build.sh && \
     ./scripts/build.sh"

# 5. インストール
sshpass -p "$TARGET_PASS" ssh "$TARGET_USER@$TARGET_IP" \
    "cd ~/baby-fun-box-build/dist/baby-fun-box-package && \
     ./install.sh <<< 'n'"

# 6. デスクトップショートカット
sshpass -p "$TARGET_PASS" ssh "$TARGET_USER@$TARGET_IP" \
    "cp ~/.local/share/applications/baby-fun-box.desktop ~/デスクトップ/ && \
     chmod +x ~/デスクトップ/baby-fun-box.desktop"

echo "導入完了！"
```

---

## 起動方法（対象マシン）

| 方法 | 操作 |
|------|------|
| デスクトップ | アイコンをダブルクリック |
| アプリメニュー | アクティビティ → 「Baby Fun Box」で検索 |
| ターミナル | `~/.local/share/baby-fun-box/baby-fun-box` |

### 初回起動時の注意

デスクトップアイコンをダブルクリックすると「信頼されていないアプリケーション」と表示される場合があります：

1. アイコンを**右クリック**
2. 「**起動を許可**」を選択
3. 以降はダブルクリックで起動可能

---

## トラブルシューティング

### GLIBC エラー

```
version `GLIBC_2.38' not found
```

**原因**: ビルド環境と対象環境の GLIBC バージョンが異なる

**対策**: 対象マシンで直接ビルドする（方法 A）

### ビルド時に pygame が見つからない

```bash
# 対象マシンで実行
cd ~/baby-fun-box-build
rm -rf venv
./scripts/build.sh
```

### SSH 接続できない

```bash
# sshpass がインストールされているか確認
which sshpass

# なければインストール
sudo apt install sshpass
```

### デスクトップにアイコンが表示されない

```bash
# デスクトップフォルダ名を確認（日本語/英語）
ls ~/

# 日本語の場合
cp ~/.local/share/applications/baby-fun-box.desktop ~/デスクトップ/

# 英語の場合
cp ~/.local/share/applications/baby-fun-box.desktop ~/Desktop/
```

---

## クリーンアップ

導入後、不要なファイルを削除する場合：

```bash
sshpass -p 'PASSWORD' ssh USER@TARGET_IP \
    "rm -rf ~/baby-fun-box-build ~/baby-fun-box-src.tar.gz"
```

---

## 関連ドキュメント

- [配布パッケージ作成ガイド](./create-package.md) - ローカルでのビルド手順
- [Ubuntu インストールガイド](./ubuntu-installation.md) - エンドユーザー向けインストール手順
- [ビルドとデプロイ詳細](./build-and-deploy.md) - 技術的な詳細情報
