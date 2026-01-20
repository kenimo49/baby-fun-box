---
title: "トラブルシューティング"
category: guide
tags: [troubleshooting, debug, pygame, audio, rendering, input]
related:
  - ./knowledge/pygame-basics.md
  - ./knowledge/pygame-rendering.md
  - ./knowledge/pygame-input.md
  - ./knowledge/pygame-audio.md
---

# トラブルシューティング

Baby Fun Box 開発で遭遇する可能性のある問題と解決策をまとめています。

---

## 目次

1. [起動・初期化](#起動初期化)
2. [描画関連](#描画関連)
3. [入力関連](#入力関連)
4. [音声関連](#音声関連)
5. [パフォーマンス](#パフォーマンス)
6. [パッケージング・デプロイ](#パッケージングデプロイ)

---

## 起動・初期化

### pygame.error: No available video device

**症状**: Pygame の初期化時にエラー

**原因**: ディスプレイ環境が設定されていない（SSH 接続、ヘッドレス環境）

**解決策**:
```bash
# ダミーディスプレイを使用
export SDL_VIDEODRIVER=dummy
python main.py
```

または X11 フォワーディングを使用：
```bash
ssh -X user@host
```

---

### ModuleNotFoundError: No module named 'pygame'

**症状**: pygame モジュールが見つからない

**解決策**:
```bash
pip install pygame
# または
pip install -r requirements.txt
```

---

### pygame.error: display Surface quit

**症状**: ゲーム終了後に描画しようとした

**原因**: `pygame.quit()` 後に描画関数を呼んでいる

**解決策**:
```python
# 良い例: running フラグで制御
while self.running:
    self.draw()
    pygame.display.flip()

# pygame.quit() はループ外で
pygame.quit()
```

---

## 描画関連

### 画面が真っ黒

**原因1**: `pygame.display.flip()` を呼んでいない

**解決策**:
```python
def draw(self):
    self.screen.fill(WHITE)
    # 描画処理
    pygame.display.flip()  # これを忘れない！
```

**原因2**: 座標が画面外

**解決策**:
```python
# 座標をログ出力して確認
print(f"Drawing at ({x}, {y})")
```

---

### 画像が表示されない

**原因1**: パスが間違っている

**解決策**:
```python
from pathlib import Path

# 相対パスではなく、ファイルからの相対パスを使用
ASSETS_DIR = Path(__file__).parent / "assets"
image_path = ASSETS_DIR / "images" / "sprite.png"

if image_path.exists():
    image = pygame.image.load(str(image_path))
else:
    print(f"Image not found: {image_path}")
```

**原因2**: `convert()` / `convert_alpha()` を忘れている

**解決策**:
```python
# PNG（透過あり）の場合
image = pygame.image.load("sprite.png").convert_alpha()

# JPG（透過なし）の場合
image = pygame.image.load("photo.jpg").convert()
```

---

### 描画がちらつく

**原因**: ダブルバッファリングを使っていない

**解決策**:
```python
# ダブルバッファを有効化
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
```

---

### 透明な部分が黒くなる

**原因**: `convert_alpha()` ではなく `convert()` を使っている

**解決策**:
```python
# 透過画像は convert_alpha() を使用
image = pygame.image.load("sprite.png").convert_alpha()
```

---

## 入力関連

### クリック/タッチが反応しない

**原因1**: 当たり判定が小さすぎる

**解決策**:
```python
from shared.constants import MIN_TOUCH_SIZE

# 最小 80px を保証
button_width = max(button_width, MIN_TOUCH_SIZE)
```

**原因2**: イベントを 2 回取得している

**解決策**:
```python
# 悪い例
for event in pygame.event.get():
    pass
for event in pygame.event.get():  # 空になっている！
    pass

# 良い例
events = pygame.event.get()
for event in events:
    pass
```

**原因3**: 状態チェックが漏れている

**解決策**:
```python
def _handle_tap(self, x, y):
    # 状態をチェック
    if self.game_state != GameState.PLAYING:
        return
    # タップ処理
```

---

### ダブルクリックになる

**原因**: BUTTONDOWN と BUTTONUP の両方で処理している

**解決策**:
```python
# どちらか一方のみで処理
if event.type == pygame.MOUSEBUTTONDOWN:
    self._handle_click(event.pos)
# BUTTONUP では処理しない
```

---

### タッチが反応しない（タッチスクリーン）

**原因**: タッチイベントがマウスイベントに変換されていない

**解決策**:
```python
# main.py の先頭で設定
import os
os.environ['SDL_MOUSE_TOUCH_EVENTS'] = '1'
```

---

## 音声関連

### 音が出ない

**原因1**: ミキサーが初期化されていない

**解決策**:
```python
# pygame.init() の前に確認
if not pygame.mixer.get_init():
    pygame.mixer.init()
```

**原因2**: 音量が 0

**解決策**:
```python
sound.set_volume(0.5)  # 0.0 ~ 1.0
```

**原因3**: Linux でオーディオデバイスの問題

**解決策**:
```bash
# PulseAudio を確認
pulseaudio --check
pulseaudio --start

# ALSA デバイスを確認
aplay -l
```

---

### pygame.error: mixer not initialized

**原因**: ミキサー初期化前に Sound を作成

**解決策**:
```python
# 初期化順序を確認
pygame.mixer.init()  # 先に初期化
sound = pygame.mixer.Sound("sound.wav")  # その後に作成
```

---

### 音が途切れる

**原因**: バッファサイズが小さすぎる

**解決策**:
```python
# バッファサイズを大きく
pygame.mixer.init(buffer=1024)  # デフォルト 512
```

---

### 音の遅延が大きい

**原因**: バッファサイズが大きすぎる

**解決策**:
```python
# バッファサイズを小さく（ただし途切れに注意）
pygame.mixer.init(buffer=256)
```

---

### プロシージャル音声がノイズだらけ

**原因**: 振幅がオーバーフローしている

**解決策**:
```python
# 振幅を制限（16bit signed の範囲）
amplitude = max(-32767, min(32767, int(value)))
```

---

## パフォーマンス

### FPS が低い

**原因1**: 毎フレーム画像を読み込んでいる

**解決策**:
```python
# 起動時に一度だけ読み込む
def __init__(self):
    self.image = pygame.image.load("sprite.png").convert_alpha()

def draw(self):
    self.screen.blit(self.image, (x, y))  # キャッシュを使用
```

**原因2**: フォントを毎フレーム作成している

**解決策**:
```python
# 起動時にフォントをキャッシュ
def __init__(self):
    self.font = get_font(48)

def draw(self):
    text = self.font.render("Hello", True, BLACK)
```

**原因3**: 不要な描画をしている

**解決策**:
```python
# 変更があった部分のみ更新
if self.needs_redraw:
    self._draw_background()
    self.needs_redraw = False
```

---

## パッケージング・デプロイ

### GLIBC version not found

**症状**: Ubuntu 22.04 で実行時にエラー

**原因**: PyInstaller パッケージが新しい GLIBC を必要としている

**解決策**: ターゲットマシンでビルドする
```bash
# ターゲットマシンで実行
git clone <repo>
cd baby-fun-box
pip install -r requirements.txt
pip install pyinstaller
./scripts/build.sh
```

→ 詳細: [deploy-to-device.md](./guide/deploy-to-device.md)

---

### アイコンが表示されない（デスクトップショートカット）

**原因**: .desktop ファイルのパスが間違っている

**解決策**:
```ini
[Desktop Entry]
# 絶対パスを使用
Icon=/home/user/baby-fun-box/icon.png
Exec=/home/user/baby-fun-box/baby-fun-box
```

---

### 実行権限がない

**解決策**:
```bash
chmod +x /path/to/baby-fun-box
chmod +x /path/to/baby-fun-box.desktop
```

---

## 問題が解決しない場合

1. **ログを確認**: `print()` でデバッグ出力を追加
2. **最小再現コード**: 問題を再現する最小限のコードを作成
3. **Issue を作成**: [GitHub Issues](https://github.com/kenimo49/baby-fun-box/issues)

---

## 関連ドキュメント

- [Pygame 基礎](./knowledge/pygame-basics.md) - 初期化とゲームループ
- [Pygame 描画処理](./knowledge/pygame-rendering.md) - 描画の詳細
- [Pygame 入力処理](./knowledge/pygame-input.md) - 入力の詳細
- [Pygame 音声処理](./knowledge/pygame-audio.md) - 音声の詳細
