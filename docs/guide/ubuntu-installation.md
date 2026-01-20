---
title: "インストールガイド"
category: guide
tags: [install, ubuntu, deploy]
related:
  - ./build-and-deploy.md
---

# Baby Fun Box インストールガイド

Ubuntu PC に Baby Fun Box をインストールする手順です。

---

## 動作環境

| 項目 | 要件 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| 画面 | タッチスクリーン推奨 |
| 音声 | スピーカー内蔵または外付け |

---

## インストール手順

### 1. パッケージを入手

`baby-fun-box-ubuntu22.04.tar.gz` を USB メモリ等で対象 PC にコピーします。

### 2. パッケージを展開

```bash
# ホームディレクトリで作業
cd ~

# パッケージを展開
tar -xzf baby-fun-box-ubuntu22.04.tar.gz
```

### 3. インストーラーを実行

```bash
cd baby-fun-box-package
./install.sh
```

インストーラーが以下を行います：

- アプリケーションを `~/.local/share/baby-fun-box/` にコピー
- アプリケーションメニューに登録
- アイコンをインストール

### 4. インストール完了

```
==========================================
インストール完了!
==========================================

起動方法:
  1. アプリケーションメニューから "Baby Fun Box" を選択
  2. または: ~/.local/share/baby-fun-box/baby-fun-box
```

---

## 起動方法

### アプリケーションメニューから

1. 画面左下の **アクティビティ** をクリック
2. 検索バーに「**Baby Fun Box**」と入力
3. 表示されたアイコンをクリック

### コマンドラインから

```bash
~/.local/share/baby-fun-box/baby-fun-box
```

---

## 使い方

### ランチャー画面

起動すると 6 つのゲームが表示されます：

| アイコン | ゲーム名 | 内容 |
|---------|---------|------|
| 🎈 | ふうせんパチン | 風船をタッチして割る |
| 🐻 | どうぶつタッチ | 動物をタッチして鳴き声を聞く |
| 🎹 | ベビーピアノ | 鍵盤をタッチして音を鳴らす |
| 🚗 | のりものゴー | 乗り物をタッチして走らせる |
| 🎨 | おえかきらくがき | 画面をタッチして絵を描く |
| 🐹 | モグラたたき | 出てくるモグラをタッチ |

### 操作方法

- **ゲーム選択**: ゲームアイコンをタッチ
- **ランチャーに戻る**: 画面左上の [←] ボタンをタッチ
- **アプリ終了**: キーボードの ESC キー

---

## トラブルシューティング

### 音が出ない

```bash
# PulseAudio を起動
pulseaudio --start

# 音量を確認
alsamixer
```

### 日本語が表示されない

```bash
# 日本語フォントをインストール
sudo apt install fonts-noto-cjk
```

### タッチが反応しない

```bash
# 入力デバイスを確認
xinput list
```

タッチスクリーンがリストに表示されていれば正常です。

### アプリがメニューに表示されない

```bash
# デスクトップデータベースを更新
update-desktop-database ~/.local/share/applications
```

### 起動時にエラーが出る

```bash
# ライブラリの不足を確認
ldd ~/.local/share/baby-fun-box/baby-fun-box | grep "not found"
```

不足している場合は以下をインストール：

```bash
sudo apt install libsdl2-2.0-0 libsdl2-mixer-2.0-0
```

---

## アンインストール

以下のコマンドで完全に削除できます：

```bash
rm -rf ~/.local/share/baby-fun-box
rm -f ~/.local/share/applications/baby-fun-box.desktop
rm -f ~/.local/share/icons/hicolor/256x256/apps/baby-fun-box.png
```

---

## サポート

問題が解決しない場合は、以下の情報を添えてお問い合わせください：

- Ubuntu のバージョン（`lsb_release -a`）
- エラーメッセージのスクリーンショット
- 実行した手順
