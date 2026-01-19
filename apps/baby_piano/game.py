"""
BabyPianoGame - カラフルなピアノで音を鳴らすゲーム

1〜2歳児向けに設計:
- 大きくてカラフルな鍵盤（タップしやすい）
- タップで音が鳴る + 視覚的フィードバック
- 虹色の楽しいデザイン
- 音ゲーモード：曲に合わせて鍵盤を弾く
"""

import array
import math
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import pygame

from shared.base_game import BaseGame
from shared.components import BackButton, Button
from shared.constants import (
    BABY_BLUE,
    BABY_GREEN,
    BABY_ORANGE,
    BABY_PINK,
    BABY_PURPLE,
    BABY_RED,
    BABY_YELLOW,
    BACKGROUND_CREAM,
    WHITE,
)
from shared.fonts import get_font

# アセットディレクトリのパス
ASSETS_DIR = Path(__file__).parent / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# ピアノの音階（C4からC5の1オクターブ）
# インデックス: 0=ド, 1=レ, 2=ミ, 3=ファ, 4=ソ, 5=ラ, 6=シ, 7=ド(高)
NOTES = [
    {"name": "ド", "freq": 261.63, "key": "c4"},
    {"name": "レ", "freq": 293.66, "key": "d4"},
    {"name": "ミ", "freq": 329.63, "key": "e4"},
    {"name": "ファ", "freq": 349.23, "key": "f4"},
    {"name": "ソ", "freq": 392.00, "key": "g4"},
    {"name": "ラ", "freq": 440.00, "key": "a4"},
    {"name": "シ", "freq": 493.88, "key": "b4"},
    {"name": "ド", "freq": 523.25, "key": "c5"},
]

# 鍵盤の色（虹色 + ピンク）
KEY_COLORS = [
    BABY_RED,
    BABY_ORANGE,
    BABY_YELLOW,
    BABY_GREEN,
    (100, 200, 255),  # 水色
    BABY_BLUE,
    BABY_PURPLE,
    BABY_PINK,
]


class GameMode(Enum):
    """ゲームモード"""
    FREE_PLAY = "free"
    SONG_MODE = "song"
    SONG_SELECT = "select"


@dataclass
class Song:
    """曲のデータ"""
    title: str
    notes: list[int]  # 鍵盤のインデックス（0-7）、-1は休符
    tempo: float = 0.6  # 各音の間隔（秒）


# 曲データ
SONGS = [
    Song(
        title="きらきら星",
        notes=[
            0, 0, 4, 4, 5, 5, 4, -1,  # きらきらひかる
            3, 3, 2, 2, 1, 1, 0, -1,  # おそらのほしよ
            4, 4, 3, 3, 2, 2, 1, -1,  # まばたきしては
            4, 4, 3, 3, 2, 2, 1, -1,  # みんなをみてる
            0, 0, 4, 4, 5, 5, 4, -1,  # きらきらひかる
            3, 3, 2, 2, 1, 1, 0,      # おそらのほしよ
        ],
        tempo=0.5,
    ),
    Song(
        title="かえるのうた",
        notes=[
            0, 1, 2, 3, 2, 1, 0, -1,  # かえるのうたが
            2, 3, 4, 5, 4, 3, 2, -1,  # きこえてくるよ
            0, -1, 0, -1, 0, -1, 0, -1,  # ゲロゲロゲロゲロ
            0, 1, 2, 3, 2, 1, 0,      # グワッグワッグワッ
        ],
        tempo=0.4,
    ),
    Song(
        title="ちょうちょう",
        notes=[
            4, 2, 2, -1, 3, 1, 1, -1,  # ちょうちょう ちょうちょう
            0, 1, 2, 3, 4, 4, 4, -1,  # なのはにとまれ
            4, 2, 2, 2, 3, 1, 1, 1,   # なのはにあいたら
            0, 2, 4, 4, 2, 2, 2,      # さくらにとまれ
        ],
        tempo=0.5,
    ),
    Song(
        title="メリーさんのひつじ",
        notes=[
            2, 1, 0, 1, 2, 2, 2, -1,  # メリーさんのひつじ
            1, 1, 1, -1, 2, 4, 4, -1,  # ひつじ ひつじ
            2, 1, 0, 1, 2, 2, 2, 2,   # メリーさんのひつじ
            1, 1, 2, 1, 0,            # かわいいな
        ],
        tempo=0.45,
    ),
]


@dataclass
class PianoKey:
    """ピアノの鍵盤"""

    index: int
    rect: pygame.Rect
    color: tuple[int, int, int]
    pressed_color: tuple[int, int, int]
    note_name: str
    frequency: float
    sound_key: str
    is_pressed: bool = False
    press_time: float = 0.0
    is_highlighted: bool = False  # 音ゲーモードでのハイライト


class BabyPianoGame(BaseGame):
    """カラフルなピアノで遊ぶゲーム"""

    name = "Baby Piano"
    description = "カラフルな鍵盤をタップして音を鳴らそう！"
    icon_path = "assets/icon.png"

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        # ゲームモード
        self.mode = GameMode.FREE_PLAY

        # 鍵盤の設定
        self.keys: list[PianoKey] = []
        self._setup_keys()

        # 音声キャッシュ
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.generated_sounds: dict[float, pygame.mixer.Sound] = {}

        # UI
        self.back_button = BackButton(x=20, y=20, on_click=self._handle_back)

        # モード切替ボタン
        self.mode_button = Button(
            x=self.width - 180,
            y=20,
            width=160,
            height=50,
            text="おんがくモード",
            color=BABY_PURPLE,
            hover_color=(150, 100, 180),
            font_size=20,
            on_click=self._toggle_mode,
        )

        # フォント
        self.title_font = get_font(48)
        self.note_font = get_font(72)
        self.hint_font = get_font(28)
        self.song_font = get_font(36)

        # アニメーション
        self.press_duration = 0.2

        # 最後に押された音の表示
        self.last_note: str | None = None
        self.last_note_time: float = 0.0
        self.note_display_duration: float = 1.0

        # 音ゲーモード用の状態
        self.current_song: Song | None = None
        self.song_position: int = 0  # 現在の音の位置
        self.song_completed: bool = False
        self.correct_count: int = 0
        self.total_notes: int = 0

        # ハイライトアニメーション
        self.highlight_pulse: float = 0.0

        # 曲選択ボタン
        self.song_buttons: list[Button] = []
        self._setup_song_buttons()

    def _setup_keys(self) -> None:
        """鍵盤をセットアップ"""
        num_keys = len(NOTES)

        padding = 20
        available_width = self.width - padding * 2
        key_width = available_width // num_keys
        key_height = self.height - 280

        start_x = padding
        start_y = 170

        for i, note in enumerate(NOTES):
            color = KEY_COLORS[i]
            pressed_color = tuple(max(c - 50, 0) for c in color)

            rect = pygame.Rect(
                start_x + i * key_width,
                start_y,
                key_width - 4,
                key_height,
            )

            key = PianoKey(
                index=i,
                rect=rect,
                color=color,
                pressed_color=pressed_color,  # type: ignore
                note_name=note["name"],
                frequency=note["freq"],
                sound_key=note["key"],
            )
            self.keys.append(key)

    def _setup_song_buttons(self) -> None:
        """曲選択ボタンをセットアップ"""
        self.song_buttons.clear()

        button_width = 280
        button_height = 80
        spacing = 20
        start_y = 200

        # ボタンを中央に配置
        start_x = (self.width - button_width) // 2

        for i, song in enumerate(SONGS):
            color = KEY_COLORS[i % len(KEY_COLORS)]
            hover_color = tuple(max(c - 30, 0) for c in color)

            def make_callback(song_index: int):
                return lambda: self._select_song(song_index)

            button = Button(
                x=start_x,
                y=start_y + i * (button_height + spacing),
                width=button_width,
                height=button_height,
                text=song.title,
                color=color,
                hover_color=hover_color,  # type: ignore
                font_size=28,
                on_click=make_callback(i),
            )
            self.song_buttons.append(button)

    def _handle_back(self) -> None:
        """戻るボタンの処理"""
        if self.mode == GameMode.SONG_MODE:
            # 曲プレイ中は曲選択に戻る
            self.mode = GameMode.SONG_SELECT
            self._reset_song_state()
        elif self.mode == GameMode.SONG_SELECT:
            # 曲選択中はフリープレイに戻る
            self.mode = GameMode.FREE_PLAY
        else:
            # フリープレイ中はランチャーに戻る
            self.request_return_to_launcher()

    def _toggle_mode(self) -> None:
        """モード切替"""
        if self.mode == GameMode.FREE_PLAY:
            self.mode = GameMode.SONG_SELECT
        else:
            self.mode = GameMode.FREE_PLAY
            self._reset_song_state()

    def _select_song(self, song_index: int) -> None:
        """曲を選択"""
        self.current_song = SONGS[song_index]
        self.mode = GameMode.SONG_MODE
        self._reset_song_state()
        self._update_highlight()

    def _reset_song_state(self) -> None:
        """曲の状態をリセット"""
        self.song_position = 0
        self.song_completed = False
        self.correct_count = 0
        self.total_notes = 0
        for key in self.keys:
            key.is_highlighted = False

    def _update_highlight(self) -> None:
        """次に押すべき鍵盤をハイライト"""
        for key in self.keys:
            key.is_highlighted = False

        if self.current_song and not self.song_completed:
            # 休符をスキップ
            while (self.song_position < len(self.current_song.notes) and
                   self.current_song.notes[self.song_position] == -1):
                self.song_position += 1

            if self.song_position < len(self.current_song.notes):
                note_index = self.current_song.notes[self.song_position]
                if 0 <= note_index < len(self.keys):
                    self.keys[note_index].is_highlighted = True

    def _load_sounds(self) -> None:
        """音声ファイルを読み込む"""
        if not SOUNDS_DIR.exists():
            return

        for note in NOTES:
            sound_key = note["key"]
            for ext in [".ogg", ".wav", ".mp3"]:
                path = SOUNDS_DIR / f"{sound_key}{ext}"
                if path.exists():
                    try:
                        sound = pygame.mixer.Sound(str(path))
                        sound.set_volume(0.6)
                        self.sounds[sound_key] = sound
                        break
                    except pygame.error:
                        pass

    def _create_note_sound(self, frequency: float) -> pygame.mixer.Sound:
        """音階の音を生成"""
        # キャッシュを確認
        if frequency in self.generated_sounds:
            return self.generated_sounds[frequency]

        sample_rate = 22050
        duration = 0.5
        samples = int(sample_rate * duration)

        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            if t < 0.05:
                envelope = t / 0.05
            elif t < 0.15:
                envelope = 1.0 - 0.3 * (t - 0.05) / 0.1
            elif t < 0.4:
                envelope = 0.7
            else:
                envelope = 0.7 * (1.0 - (t - 0.4) / 0.1)
                envelope = max(0, envelope)

            value = math.sin(2 * math.pi * frequency * t)
            value += 0.3 * math.sin(2 * math.pi * frequency * 2 * t)
            value += 0.1 * math.sin(2 * math.pi * frequency * 3 * t)

            amplitude = int(20000 * envelope * value / 1.4)
            sound_array.append(amplitude)

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.6)
        self.generated_sounds[frequency] = sound
        return sound

    def _play_key(self, key: PianoKey) -> None:
        """鍵盤を押したときの処理"""
        key.is_pressed = True
        key.press_time = 0.0

        self.last_note = key.note_name
        self.last_note_time = 0.0

        # 音声を再生
        if key.sound_key in self.sounds:
            self.sounds[key.sound_key].play()
        else:
            sound = self._create_note_sound(key.frequency)
            sound.play()

        # 音ゲーモードでの判定
        if self.mode == GameMode.SONG_MODE and self.current_song and not self.song_completed:
            self._check_song_note(key.index)

    def _check_song_note(self, pressed_index: int) -> None:
        """音ゲーモードでの音判定"""
        if not self.current_song:
            return

        # 休符をスキップ
        while (self.song_position < len(self.current_song.notes) and
               self.current_song.notes[self.song_position] == -1):
            self.song_position += 1

        if self.song_position >= len(self.current_song.notes):
            self.song_completed = True
            return

        expected_index = self.current_song.notes[self.song_position]

        self.total_notes += 1
        if pressed_index == expected_index:
            self.correct_count += 1
            self.song_position += 1

            # 次のハイライトを更新
            self._update_highlight()

            # 曲が終わったかチェック
            # 残りが全て休符かチェック
            remaining = self.current_song.notes[self.song_position:]
            if all(n == -1 for n in remaining) or self.song_position >= len(self.current_song.notes):
                self.song_completed = True
                for key in self.keys:
                    key.is_highlighted = False

    def on_enter(self) -> None:
        """ゲーム開始時の初期化"""
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self._load_sounds()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """イベント処理"""
        for event in events:
            if self.back_button.handle_event(event):
                continue

            if self.mode != GameMode.SONG_SELECT:
                if self.mode_button.handle_event(event):
                    continue

            # 曲選択モードのボタン処理
            if self.mode == GameMode.SONG_SELECT:
                for button in self.song_buttons:
                    if button.handle_event(event):
                        break
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._handle_back()
                elif event.key == pygame.K_1:
                    self._play_key(self.keys[0])
                elif event.key == pygame.K_2:
                    self._play_key(self.keys[1])
                elif event.key == pygame.K_3:
                    self._play_key(self.keys[2])
                elif event.key == pygame.K_4:
                    self._play_key(self.keys[3])
                elif event.key == pygame.K_5:
                    self._play_key(self.keys[4])
                elif event.key == pygame.K_6:
                    self._play_key(self.keys[5])
                elif event.key == pygame.K_7:
                    self._play_key(self.keys[6])
                elif event.key == pygame.K_8:
                    self._play_key(self.keys[7])
                # 曲完了後にスペースで再プレイ
                elif event.key == pygame.K_SPACE and self.song_completed:
                    self._reset_song_state()
                    self._update_highlight()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos

                    # 曲完了後のクリックで再プレイ
                    if self.song_completed:
                        self._reset_song_state()
                        self._update_highlight()
                        continue

                    for key in self.keys:
                        if key.rect.collidepoint(x, y):
                            self._play_key(key)
                            break

    def update(self, dt: float) -> None:
        """更新処理"""
        # キー押下アニメーション
        for key in self.keys:
            if key.is_pressed:
                key.press_time += dt
                if key.press_time >= self.press_duration:
                    key.is_pressed = False

        # 音の名前表示
        if self.last_note:
            self.last_note_time += dt
            if self.last_note_time >= self.note_display_duration:
                self.last_note = None

        # ハイライトのパルスアニメーション
        self.highlight_pulse += dt * 4
        if self.highlight_pulse > math.pi * 2:
            self.highlight_pulse -= math.pi * 2

    def draw(self) -> None:
        """描画処理"""
        self.screen.fill(BACKGROUND_CREAM)

        if self.mode == GameMode.SONG_SELECT:
            self._draw_song_select()
        else:
            self._draw_piano()

        # 戻るボタン
        self.back_button.draw(self.screen)

    def _draw_song_select(self) -> None:
        """曲選択画面の描画"""
        # タイトル
        title_text = self.title_font.render("きょくをえらんでね！", True, (80, 80, 80))
        title_rect = title_text.get_rect(centerx=self.width // 2, top=80)
        self.screen.blit(title_text, title_rect)

        # 曲ボタン
        for button in self.song_buttons:
            button.draw(self.screen)

        # ヒント
        hint_text = self.hint_font.render("Touch a song to start!", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(centerx=self.width // 2, bottom=self.height - 20)
        self.screen.blit(hint_text, hint_rect)

    def _draw_piano(self) -> None:
        """ピアノ画面の描画"""
        # タイトル
        if self.mode == GameMode.SONG_MODE and self.current_song:
            title = self.current_song.title
        else:
            title = "Baby Piano"
        title_text = self.title_font.render(title, True, (80, 80, 80))
        title_rect = title_text.get_rect(centerx=self.width // 2, top=20)
        self.screen.blit(title_text, title_rect)

        # 音ゲーモード: 進捗表示
        if self.mode == GameMode.SONG_MODE and self.current_song:
            if self.song_completed:
                # 完了メッセージ
                complete_text = self.note_font.render("できたね！", True, BABY_PINK)
                complete_rect = complete_text.get_rect(centerx=self.width // 2, top=70)
                self.screen.blit(complete_text, complete_rect)

                # もう一度プレイのヒント
                retry_text = self.hint_font.render("タップでもういちど", True, (100, 100, 100))
                retry_rect = retry_text.get_rect(centerx=self.width // 2, top=130)
                self.screen.blit(retry_text, retry_rect)
            else:
                # 進捗バー
                total_real_notes = sum(1 for n in self.current_song.notes if n != -1)
                current_real_pos = sum(1 for n in self.current_song.notes[:self.song_position] if n != -1)
                progress = current_real_pos / total_real_notes if total_real_notes > 0 else 0

                bar_width = 300
                bar_height = 20
                bar_x = (self.width - bar_width) // 2
                bar_y = 85

                # 背景
                pygame.draw.rect(self.screen, (200, 200, 200),
                               (bar_x, bar_y, bar_width, bar_height), border_radius=10)
                # 進捗
                if progress > 0:
                    pygame.draw.rect(self.screen, BABY_GREEN,
                                   (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=10)
                # 枠
                pygame.draw.rect(self.screen, (100, 100, 100),
                               (bar_x, bar_y, bar_width, bar_height), 2, border_radius=10)

        # 最後に押された音の表示（フリープレイモード）
        elif self.last_note and self.mode == GameMode.FREE_PLAY:
            alpha = 1.0 - (self.last_note_time / self.note_display_duration)
            alpha = max(0, min(1, alpha))
            note_color = (int(80 * alpha), int(80 * alpha), int(80 * alpha))
            note_text = self.note_font.render(self.last_note, True, note_color)
            note_rect = note_text.get_rect(centerx=self.width // 2, top=70)
            self.screen.blit(note_text, note_rect)

        # 鍵盤を描画
        for key in self.keys:
            self._draw_key(key)

        # モード切替ボタン
        if self.mode == GameMode.FREE_PLAY:
            self.mode_button.text = "おんがくモード"
        else:
            self.mode_button.text = "じゆうモード"
        self.mode_button.draw(self.screen)

        # ヒント
        if self.mode == GameMode.FREE_PLAY:
            hint = "Touch the keys to play!"
        elif self.song_completed:
            hint = ""
        else:
            hint = "ひかっているキーをタップしよう！"
        if hint:
            hint_text = self.hint_font.render(hint, True, (150, 150, 150))
            hint_rect = hint_text.get_rect(centerx=self.width // 2, bottom=self.height - 20)
            self.screen.blit(hint_text, hint_rect)

    def _draw_key(self, key: PianoKey) -> None:
        """鍵盤を描画"""
        rect = key.rect

        # 押下時のアニメーション
        if key.is_pressed:
            progress = key.press_time / self.press_duration
            offset = int(10 * (1 - progress))
            draw_rect = pygame.Rect(
                rect.x,
                rect.y + offset,
                rect.width,
                rect.height - offset,
            )
            color = key.pressed_color
        else:
            draw_rect = rect
            color = key.color

        # 鍵盤の影
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 5
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            shadow_rect,
            border_radius=15,
        )

        # 鍵盤本体
        pygame.draw.rect(
            self.screen,
            color,
            draw_rect,
            border_radius=15,
        )

        # ハイライト表示（音ゲーモード）
        if key.is_highlighted and self.mode == GameMode.SONG_MODE:
            # パルスアニメーション
            pulse = (math.sin(self.highlight_pulse) + 1) / 2  # 0-1
            highlight_alpha = int(100 + 80 * pulse)

            # 光る枠線
            pygame.draw.rect(
                self.screen,
                (255, 255, 100),  # 黄色のハイライト
                draw_rect.inflate(8, 8),
                width=6,
                border_radius=18,
            )

            # 内側のグロー効果
            glow_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
            glow_surface.fill((255, 255, 200, highlight_alpha))
            self.screen.blit(glow_surface, draw_rect.topleft)

            # 星マークを表示
            star_y = draw_rect.top + 30
            star_text = get_font(48).render("★", True, (255, 220, 50))
            star_rect = star_text.get_rect(centerx=draw_rect.centerx, centery=star_y)
            self.screen.blit(star_text, star_rect)

        # 鍵盤の枠線
        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            draw_rect,
            width=3,
            border_radius=15,
        )

        # 音階名を鍵盤の下部に表示
        font = get_font(36)
        text_surface = font.render(key.note_name, True, WHITE)
        text_rect = text_surface.get_rect(
            centerx=draw_rect.centerx,
            bottom=draw_rect.bottom - 20,
        )
        self.screen.blit(text_surface, text_rect)

        # 押下時のエフェクト
        if key.is_pressed:
            overlay = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
            alpha = int(100 * (1 - key.press_time / self.press_duration))
            overlay.fill((255, 255, 255, alpha))
            self.screen.blit(overlay, draw_rect.topleft)
