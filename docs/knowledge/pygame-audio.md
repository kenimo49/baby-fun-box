---
title: "Pygame 音声処理"
category: knowledge
tags: [pygame, audio, sound, music, mixer, procedural]
related:
  - ./pygame-basics.md
  - ./pygame-rendering.md
  - ../design/toddler-friendly.md
---

# Pygame 音声処理

## 概要

Pygame での音声処理（効果音、BGM）のパターンを解説します。Baby Fun Box では、外部音声ファイルを使わずにプロシージャル（コードによる）音声生成を多用しています。

---

## ミキサー初期化

### 基本的な初期化

```python
import pygame

# デフォルト設定で初期化
pygame.mixer.init()

# カスタム設定で初期化
pygame.mixer.init(
    frequency=44100,  # サンプリングレート（Hz）
    size=-16,         # サンプルサイズ（16bit signed）
    channels=2,       # ステレオ
    buffer=512        # バッファサイズ（低いほど遅延少）
)
```

### 初期化タイミング

```python
# pygame.init() より前に mixer を初期化
pygame.mixer.init()
pygame.init()

# または pygame.init() 後に再初期化
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=44100)
```

---

## 効果音 (Sound)

### ファイルからの読み込み

```python
# OGG / WAV / MP3 に対応
pop_sound = pygame.mixer.Sound("assets/sounds/pop.wav")

# 再生
pop_sound.play()

# 音量設定 (0.0 ~ 1.0)
pop_sound.set_volume(0.5)
```

### プロシージャル音声生成

Baby Fun Box で使用している、コードで音声を生成するパターン：

```python
import array
import math
import pygame

def create_pop_sound() -> pygame.mixer.Sound:
    """「ポン」という効果音を生成"""
    sample_rate = 44100
    duration = 0.15  # 秒

    # サンプル数
    num_samples = int(sample_rate * duration)

    # 16bit signed の配列
    sound_array = array.array("h")

    for i in range(num_samples):
        t = i / sample_rate

        # 減衰エンベロープ
        envelope = math.exp(-t * 20)

        # 複数の周波数を合成（より自然な音に）
        freq1 = 400  # 基本周波数
        freq2 = 600  # 倍音

        wave = (
            math.sin(2 * math.pi * freq1 * t) * 0.7 +
            math.sin(2 * math.pi * freq2 * t) * 0.3
        )

        # 振幅を適用（32767 は 16bit の最大値）
        amplitude = int(32767 * envelope * wave * 0.5)
        sound_array.append(amplitude)

    # ステレオ化（左右同じ）
    stereo_array = array.array("h")
    for sample in sound_array:
        stereo_array.append(sample)  # Left
        stereo_array.append(sample)  # Right

    return pygame.mixer.Sound(buffer=stereo_array)
```

### 音色のバリエーション

```python
def create_tone(frequency: float, duration: float = 0.2) -> pygame.mixer.Sound:
    """指定周波数のトーンを生成"""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)

    sound_array = array.array("h")

    for i in range(num_samples):
        t = i / sample_rate

        # ADSR エンベロープ（簡易版）
        if t < 0.01:  # Attack
            envelope = t / 0.01
        elif t < duration - 0.05:  # Sustain
            envelope = 1.0
        else:  # Release
            envelope = (duration - t) / 0.05

        wave = math.sin(2 * math.pi * frequency * t)
        amplitude = int(32767 * envelope * wave * 0.3)

        # ステレオ
        sound_array.append(amplitude)
        sound_array.append(amplitude)

    return pygame.mixer.Sound(buffer=sound_array)


# ドレミファソラシドの周波数
NOTES = {
    'C4': 261.63,
    'D4': 293.66,
    'E4': 329.63,
    'F4': 349.23,
    'G4': 392.00,
    'A4': 440.00,
    'B4': 493.88,
    'C5': 523.25,
}

# 音階の Sound を事前生成
piano_sounds = {note: create_tone(freq) for note, freq in NOTES.items()}
```

---

## BGM (Music)

### ストリーミング再生

大きな音声ファイルはストリーミングで再生：

```python
# BGM を読み込み（メモリに全て読み込まない）
pygame.mixer.music.load("assets/music/background.ogg")

# 再生（-1 でループ）
pygame.mixer.music.play(loops=-1)

# 停止
pygame.mixer.music.stop()

# フェードアウト（ミリ秒）
pygame.mixer.music.fadeout(1000)

# 音量設定
pygame.mixer.music.set_volume(0.3)
```

### 再生状態の確認

```python
if pygame.mixer.music.get_busy():
    print("BGM 再生中")
```

---

## 音量管理

### 個別音量

```python
# Sound 個別に設定
pop_sound.set_volume(0.5)
click_sound.set_volume(0.7)
```

### マスター音量

```python
class AudioManager:
    def __init__(self):
        self.master_volume = 1.0
        self.sounds: dict[str, pygame.mixer.Sound] = {}

    def add_sound(self, name: str, sound: pygame.mixer.Sound) -> None:
        self.sounds[name] = sound

    def play(self, name: str) -> None:
        if name in self.sounds:
            self.sounds[name].play()

    def set_master_volume(self, volume: float) -> None:
        self.master_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.master_volume)
```

---

## 幼児向け音声設計

### ポジティブな音

```python
# 明るい周波数帯（高め）
def create_success_sound() -> pygame.mixer.Sound:
    """成功音（明るい上昇音）"""
    frequencies = [523, 659, 784]  # C5, E5, G5（メジャーコード）

    sample_rate = 44100
    duration = 0.3
    num_samples = int(sample_rate * duration)

    sound_array = array.array("h")

    for i in range(num_samples):
        t = i / sample_rate
        envelope = math.exp(-t * 5)

        # 時間経過で周波数を上げる
        freq_index = min(int(t / duration * len(frequencies)), len(frequencies) - 1)
        freq = frequencies[freq_index]

        wave = math.sin(2 * math.pi * freq * t)
        amplitude = int(32767 * envelope * wave * 0.3)

        sound_array.append(amplitude)
        sound_array.append(amplitude)

    return pygame.mixer.Sound(buffer=sound_array)
```

### 即座のフィードバック

```python
def _handle_touch(self, pos: tuple[int, int]) -> None:
    for obj in self.objects:
        if obj.is_hit(pos):
            # 遅延なしで再生
            self.touch_sound.play()
            break
```

### 音量のバランス

```python
# 効果音は控えめに
EFFECT_VOLUME = 0.3

# BGM はさらに控えめに
BGM_VOLUME = 0.15
```

---

## トラブルシューティング

### 問題: 音が出ない

**原因1**: ミキサーが初期化されていない

**解決策**:
```python
# pygame.init() の前に確認
if not pygame.mixer.get_init():
    pygame.mixer.init()
```

**原因2**: システムの音声デバイス問題

**解決策** (Linux):
```bash
# PulseAudio を確認
pulseaudio --check
pulseaudio --start

# ALSA デバイスを確認
aplay -l
```

### 問題: 音が途切れる

**原因**: バッファサイズが小さすぎる

**解決策**:
```python
# バッファサイズを大きく
pygame.mixer.init(buffer=1024)  # デフォルト 512
```

### 問題: 音の遅延が大きい

**原因**: バッファサイズが大きすぎる

**解決策**:
```python
# バッファサイズを小さく（ただし途切れに注意）
pygame.mixer.init(buffer=256)
```

### 問題: `pygame.error: mixer not initialized`

**原因**: ミキサー初期化前に Sound を作成

**解決策**:
```python
# 初期化順序を確認
pygame.mixer.init()  # 先に初期化
sound = pygame.mixer.Sound("sound.wav")  # その後に作成
```

### 問題: プロシージャル音声がノイズだらけ

**原因**: 振幅がオーバーフローしている

**解決策**:
```python
# 振幅を制限
amplitude = max(-32767, min(32767, int(value)))
```

---

## 関連ドキュメント

- [Pygame 基礎](./pygame-basics.md) - 初期化の順序
- [Pygame 描画処理](./pygame-rendering.md) - 視覚フィードバックとの連携
- [幼児向け UX 設計](../design/toddler-friendly.md) - フィードバック設計
