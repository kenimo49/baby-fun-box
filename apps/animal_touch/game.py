"""
AnimalTouchGame - 動物をタップすると鳴き声が聞こえるゲーム

1〜2歳児向けに設計:
- 大きな動物イラスト（タップしやすい）
- タップで鳴き声 + アニメーション
- カラフルで親しみやすいデザイン
"""

import array
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pygame

from shared.base_game import BaseGame
from shared.components import BackButton
from shared.constants import BACKGROUND_CREAM, BABY_COLORS
from shared.fonts import get_font

# アセットディレクトリのパス
ASSETS_DIR = Path(__file__).parent / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# 対応する画像フォーマット
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]


@dataclass
class Animal:
    """動物のデータクラス"""

    name: str  # 日本語名
    sound_text: str  # 鳴き声テキスト
    image_key: str  # 画像/音声ファイルのキー（dog, cat, etc.）
    color: tuple[int, int, int]  # メインカラー（フォールバック描画用）
    secondary_color: tuple[int, int, int]  # サブカラー
    draw_func: Callable[[pygame.Surface, int, int, int, float], None]  # フォールバック描画関数
    sound_freq: float  # フォールバック鳴き声の周波数


class AnimalTouchGame(BaseGame):
    """動物をタップして鳴き声を聞くゲーム"""

    name = "Animal Touch"
    description = "動物をタップして鳴き声を聞こう！"
    icon_path = "assets/icon.png"

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        # 動物リスト
        self.animals: list[Animal] = []
        self._setup_animals()

        # 画像キャッシュ
        self.animal_images: dict[str, pygame.Surface] = {}
        self._load_animal_images()

        # 音声キャッシュ
        self.animal_sounds: dict[str, pygame.mixer.Sound] = {}

        # 現在の動物
        self.current_animal_index = 0

        # アニメーション状態
        self.is_animating = False
        self.animation_time = 0.0
        self.animation_duration = 0.8

        # 鳴き声表示
        self.show_sound_text = False
        self.sound_text_time = 0.0
        self.sound_text_duration = 1.5

        # 自動切り替えタイマー
        self.auto_switch_timer = 0.0
        self.auto_switch_interval = 8.0  # 8秒で自動切り替え

        # 効果音
        self.current_sound: pygame.mixer.Sound | None = None

        # UI
        self.back_button = BackButton(x=20, y=20, on_click=self.request_return_to_launcher)

        # フォント（日本語対応）
        self.name_font = get_font(72)
        self.sound_font = get_font(96)
        self.hint_font = get_font(36)

        # 矢印ボタンの領域
        self.left_arrow_rect = pygame.Rect(20, self.height // 2 - 40, 60, 80)
        self.right_arrow_rect = pygame.Rect(self.width - 80, self.height // 2 - 40, 60, 80)

    def _setup_animals(self) -> None:
        """動物のデータをセットアップ"""
        self.animals = [
            Animal(
                name="いぬ",
                sound_text="ワンワン！",
                image_key="dog",
                color=(139, 90, 43),
                secondary_color=(101, 67, 33),
                draw_func=self._draw_dog,
                sound_freq=300,
            ),
            Animal(
                name="ねこ",
                sound_text="ニャー！",
                image_key="cat",
                color=(255, 165, 0),
                secondary_color=(255, 200, 100),
                draw_func=self._draw_cat,
                sound_freq=500,
            ),
            Animal(
                name="うし",
                sound_text="モー！",
                image_key="cow",
                color=(40, 40, 40),
                secondary_color=(255, 255, 255),
                draw_func=self._draw_cow,
                sound_freq=150,
            ),
            Animal(
                name="ぶた",
                sound_text="ブーブー！",
                image_key="pig",
                color=(255, 182, 193),
                secondary_color=(255, 150, 170),
                draw_func=self._draw_pig,
                sound_freq=200,
            ),
            Animal(
                name="ひつじ",
                sound_text="メェー！",
                image_key="sheep",
                color=(245, 245, 245),
                secondary_color=(200, 200, 200),
                draw_func=self._draw_sheep,
                sound_freq=400,
            ),
            Animal(
                name="にわとり",
                sound_text="コケコッコー！",
                image_key="chicken",
                color=(255, 100, 50),
                secondary_color=(255, 220, 100),
                draw_func=self._draw_chicken,
                sound_freq=600,
            ),
            Animal(
                name="カエル",
                sound_text="ケロケロ！",
                image_key="frog",
                color=(50, 205, 50),
                secondary_color=(144, 238, 144),
                draw_func=self._draw_frog,
                sound_freq=350,
            ),
            Animal(
                name="ライオン",
                sound_text="ガオー！",
                image_key="lion",
                color=(255, 180, 50),
                secondary_color=(200, 120, 20),
                draw_func=self._draw_lion,
                sound_freq=120,
            ),
        ]

    def _load_animal_images(self) -> None:
        """動物の画像を読み込む（存在する場合のみ）"""
        if not IMAGES_DIR.exists():
            return

        for animal in self.animals:
            image_path = self._find_image_file(animal.image_key)
            if image_path:
                try:
                    image = pygame.image.load(str(image_path))
                    # アルファチャンネルがある場合は変換
                    if image.get_alpha():
                        image = image.convert_alpha()
                    else:
                        image = image.convert()
                    self.animal_images[animal.image_key] = image
                except pygame.error:
                    # 読み込みに失敗した場合はフォールバック描画を使用
                    pass

    def _find_image_file(self, image_key: str) -> Path | None:
        """画像ファイルを探す（複数フォーマット対応）"""
        for ext in SUPPORTED_IMAGE_FORMATS:
            path = IMAGES_DIR / f"{image_key}{ext}"
            if path.exists():
                return path
        return None

    def _load_animal_sounds(self) -> None:
        """動物の鳴き声音声を読み込む（存在する場合のみ）"""
        if not SOUNDS_DIR.exists():
            return

        for animal in self.animals:
            sound_path = self._find_sound_file(animal.image_key)
            if sound_path:
                try:
                    sound = pygame.mixer.Sound(str(sound_path))
                    sound.set_volume(0.5)
                    self.animal_sounds[animal.image_key] = sound
                except pygame.error:
                    pass

    def _find_sound_file(self, sound_key: str) -> Path | None:
        """音声ファイルを探す"""
        for ext in [".ogg", ".wav", ".mp3"]:
            path = SOUNDS_DIR / f"{sound_key}{ext}"
            if path.exists():
                return path
        return None

    def _create_animal_sound(self, freq: float) -> pygame.mixer.Sound:
        """動物の鳴き声を生成（フォールバック）"""
        sample_rate = 22050
        duration = 0.3
        samples = int(sample_rate * duration)

        sound_array = array.array("h")
        for i in range(samples):
            t = i / sample_rate
            freq_mod = freq * (1 + 0.1 * math.sin(2 * math.pi * 5 * t))
            amplitude = int(20000 * math.exp(-t * 3) * math.sin(2 * math.pi * freq_mod * t))
            sound_array.append(amplitude)

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.4)
        return sound

    def _draw_animal_image(
        self, screen: pygame.Surface, image: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """画像ファイルから動物を描画"""
        y_offset = int(bounce * 20)
        cy -= y_offset

        # アスペクト比を維持してリサイズ
        img_width, img_height = image.get_size()
        aspect = img_width / img_height

        if aspect > 1:
            # 横長
            new_width = size
            new_height = int(size / aspect)
        else:
            # 縦長または正方形
            new_height = size
            new_width = int(size * aspect)

        scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))

        # 中央に配置
        x = cx - new_width // 2
        y = cy - new_height // 2

        screen.blit(scaled_image, (x, y))

    # ========== 動物の描画関数（フォールバック） ==========

    def _draw_dog(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """犬を描画"""
        y_offset = int(bounce * 20)
        cy -= y_offset

        body_rect = pygame.Rect(cx - size // 2, cy - size // 4, size, size // 2)
        pygame.draw.ellipse(screen, (139, 90, 43), body_rect)

        head_size = size // 2
        head_pos = (cx - size // 4, cy - size // 3)
        pygame.draw.circle(screen, (139, 90, 43), head_pos, head_size // 2)

        pygame.draw.ellipse(
            screen, (101, 67, 33), (head_pos[0] - head_size // 3, head_pos[1] - head_size // 2, head_size // 3, head_size // 2)
        )
        pygame.draw.ellipse(
            screen, (101, 67, 33), (head_pos[0] + head_size // 6, head_pos[1] - head_size // 2, head_size // 3, head_size // 2)
        )

        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0] - head_size // 6, head_pos[1] - head_size // 8), head_size // 10)
        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0] + head_size // 6, head_pos[1] - head_size // 8), head_size // 10)

        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0], head_pos[1] + head_size // 6), head_size // 8)

        tail_points = [
            (cx + size // 2, cy),
            (cx + size // 2 + size // 4, cy - size // 4),
            (cx + size // 2 + size // 3, cy - size // 3),
        ]
        pygame.draw.lines(screen, (101, 67, 33), False, tail_points, 8)

    def _draw_cat(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """猫を描画"""
        y_offset = int(bounce * 15)
        cy -= y_offset

        color = (255, 165, 0)

        body_rect = pygame.Rect(cx - size // 3, cy - size // 6, size * 2 // 3, size // 3)
        pygame.draw.ellipse(screen, color, body_rect)

        head_size = size // 2
        head_pos = (cx - size // 4, cy - size // 4)
        pygame.draw.circle(screen, color, head_pos, head_size // 2)

        ear_size = head_size // 3
        pygame.draw.polygon(
            screen,
            color,
            [
                (head_pos[0] - head_size // 3, head_pos[1] - head_size // 4),
                (head_pos[0] - head_size // 2, head_pos[1] - head_size // 2 - ear_size),
                (head_pos[0] - head_size // 6, head_pos[1] - head_size // 3),
            ],
        )
        pygame.draw.polygon(
            screen,
            color,
            [
                (head_pos[0] + head_size // 6, head_pos[1] - head_size // 3),
                (head_pos[0] + head_size // 3, head_pos[1] - head_size // 2 - ear_size),
                (head_pos[0] + head_size // 2, head_pos[1] - head_size // 4),
            ],
        )

        pygame.draw.ellipse(
            screen, (0, 200, 0), (head_pos[0] - head_size // 4, head_pos[1] - head_size // 6, head_size // 5, head_size // 4)
        )
        pygame.draw.ellipse(
            screen, (0, 200, 0), (head_pos[0] + head_size // 10, head_pos[1] - head_size // 6, head_size // 5, head_size // 4)
        )

        pygame.draw.polygon(
            screen,
            (255, 150, 150),
            [
                (head_pos[0], head_pos[1] + head_size // 8),
                (head_pos[0] - head_size // 10, head_pos[1] + head_size // 5),
                (head_pos[0] + head_size // 10, head_pos[1] + head_size // 5),
            ],
        )

        whisker_y = head_pos[1] + head_size // 6
        pygame.draw.line(screen, (100, 100, 100), (head_pos[0] - head_size // 2, whisker_y - 5), (head_pos[0] - head_size // 6, whisker_y), 2)
        pygame.draw.line(screen, (100, 100, 100), (head_pos[0] - head_size // 2, whisker_y + 5), (head_pos[0] - head_size // 6, whisker_y), 2)
        pygame.draw.line(screen, (100, 100, 100), (head_pos[0] + head_size // 6, whisker_y), (head_pos[0] + head_size // 2, whisker_y - 5), 2)
        pygame.draw.line(screen, (100, 100, 100), (head_pos[0] + head_size // 6, whisker_y), (head_pos[0] + head_size // 2, whisker_y + 5), 2)

    def _draw_cow(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """牛を描画"""
        y_offset = int(bounce * 10)
        cy -= y_offset

        body_rect = pygame.Rect(cx - size // 2, cy - size // 4, size, size // 2)
        pygame.draw.ellipse(screen, (255, 255, 255), body_rect)

        spots = [(cx - size // 4, cy - size // 8), (cx + size // 6, cy), (cx, cy + size // 8)]
        for spot in spots:
            pygame.draw.circle(screen, (40, 40, 40), spot, size // 8)

        head_pos = (cx - size // 3, cy - size // 4)
        pygame.draw.circle(screen, (255, 255, 255), head_pos, size // 4)

        pygame.draw.ellipse(screen, (200, 180, 150), (head_pos[0] - size // 4, head_pos[1] - size // 3, size // 8, size // 4))
        pygame.draw.ellipse(screen, (200, 180, 150), (head_pos[0] + size // 8, head_pos[1] - size // 3, size // 8, size // 4))

        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0] - size // 10, head_pos[1] - size // 12), size // 16)
        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0] + size // 10, head_pos[1] - size // 12), size // 16)

        pygame.draw.ellipse(screen, (255, 200, 200), (head_pos[0] - size // 8, head_pos[1] + size // 12, size // 4, size // 6))

    def _draw_pig(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """豚を描画"""
        y_offset = int(bounce * 12)
        cy -= y_offset

        color = (255, 182, 193)

        pygame.draw.circle(screen, color, (cx, cy), size // 3)

        head_pos = (cx - size // 4, cy - size // 6)
        pygame.draw.circle(screen, color, head_pos, size // 4)

        pygame.draw.ellipse(screen, (255, 150, 170), (head_pos[0] - size // 4, head_pos[1] - size // 4, size // 5, size // 4))
        pygame.draw.ellipse(screen, (255, 150, 170), (head_pos[0] + size // 8, head_pos[1] - size // 4, size // 5, size // 4))

        nose_rect = pygame.Rect(head_pos[0] - size // 8, head_pos[1] + size // 16, size // 4, size // 6)
        pygame.draw.ellipse(screen, (255, 150, 170), nose_rect)
        pygame.draw.circle(screen, (200, 100, 120), (head_pos[0] - size // 20, head_pos[1] + size // 8), size // 24)
        pygame.draw.circle(screen, (200, 100, 120), (head_pos[0] + size // 20, head_pos[1] + size // 8), size // 24)

        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0] - size // 10, head_pos[1] - size // 16), size // 20)
        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0] + size // 10, head_pos[1] - size // 16), size // 20)

    def _draw_sheep(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """羊を描画"""
        y_offset = int(bounce * 12)
        cy -= y_offset

        wool_color = (245, 245, 245)
        for dx, dy in [(-size // 4, 0), (size // 4, 0), (0, -size // 6), (0, size // 6), (-size // 6, -size // 8), (size // 6, -size // 8)]:
            pygame.draw.circle(screen, wool_color, (cx + dx, cy + dy), size // 4)

        head_pos = (cx - size // 3, cy)
        pygame.draw.ellipse(screen, (60, 60, 60), (head_pos[0] - size // 6, head_pos[1] - size // 8, size // 3, size // 4))

        pygame.draw.circle(screen, (255, 255, 255), (head_pos[0] - size // 16, head_pos[1] - size // 20), size // 20)
        pygame.draw.circle(screen, (255, 255, 255), (head_pos[0] + size // 8, head_pos[1] - size // 20), size // 20)

        pygame.draw.ellipse(screen, (60, 60, 60), (head_pos[0] - size // 4, head_pos[1] - size // 12, size // 8, size // 10))
        pygame.draw.ellipse(screen, (60, 60, 60), (head_pos[0] + size // 6, head_pos[1] - size // 12, size // 8, size // 10))

    def _draw_chicken(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """鶏を描画"""
        y_offset = int(bounce * 18)
        cy -= y_offset

        body_color = (255, 220, 100)
        pygame.draw.ellipse(screen, body_color, (cx - size // 3, cy - size // 6, size * 2 // 3, size // 2))

        head_pos = (cx - size // 4, cy - size // 3)
        pygame.draw.circle(screen, body_color, head_pos, size // 5)

        comb_color = (255, 50, 50)
        pygame.draw.circle(screen, comb_color, (head_pos[0], head_pos[1] - size // 5), size // 10)
        pygame.draw.circle(screen, comb_color, (head_pos[0] - size // 12, head_pos[1] - size // 6), size // 12)
        pygame.draw.circle(screen, comb_color, (head_pos[0] + size // 12, head_pos[1] - size // 6), size // 12)

        beak_color = (255, 150, 50)
        pygame.draw.polygon(
            screen,
            beak_color,
            [
                (head_pos[0] - size // 5, head_pos[1]),
                (head_pos[0] - size // 3, head_pos[1] + size // 20),
                (head_pos[0] - size // 5, head_pos[1] + size // 10),
            ],
        )

        pygame.draw.circle(screen, (0, 0, 0), (head_pos[0] - size // 16, head_pos[1] - size // 20), size // 24)

        pygame.draw.ellipse(screen, (255, 200, 80), (cx - size // 6, cy - size // 8, size // 3, size // 4))

    def _draw_frog(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """カエルを描画"""
        y_offset = int(bounce * 25)
        cy -= y_offset

        color = (50, 205, 50)
        light_color = (144, 238, 144)

        pygame.draw.ellipse(screen, color, (cx - size // 3, cy - size // 6, size * 2 // 3, size // 2))

        eye_size = size // 5
        pygame.draw.circle(screen, color, (cx - size // 5, cy - size // 4), eye_size)
        pygame.draw.circle(screen, color, (cx + size // 5, cy - size // 4), eye_size)
        pygame.draw.circle(screen, (255, 255, 255), (cx - size // 5, cy - size // 4), eye_size - 5)
        pygame.draw.circle(screen, (255, 255, 255), (cx + size // 5, cy - size // 4), eye_size - 5)
        pygame.draw.circle(screen, (0, 0, 0), (cx - size // 5, cy - size // 4), eye_size // 3)
        pygame.draw.circle(screen, (0, 0, 0), (cx + size // 5, cy - size // 4), eye_size // 3)

        pygame.draw.arc(screen, (0, 100, 0), (cx - size // 4, cy - size // 8, size // 2, size // 4), 3.14, 0, 3)

        pygame.draw.ellipse(screen, light_color, (cx - size // 5, cy, size * 2 // 5, size // 4))

    def _draw_lion(
        self, screen: pygame.Surface, cx: int, cy: int, size: int, bounce: float
    ) -> None:
        """ライオンを描画"""
        y_offset = int(bounce * 15)
        cy -= y_offset

        mane_color = (200, 120, 20)
        body_color = (255, 180, 50)

        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            mx = cx - size // 6 + int(math.cos(rad) * size // 3)
            my = cy - size // 6 + int(math.sin(rad) * size // 3)
            pygame.draw.circle(screen, mane_color, (mx, my), size // 6)

        pygame.draw.circle(screen, body_color, (cx - size // 6, cy - size // 6), size // 4)

        pygame.draw.ellipse(screen, body_color, (cx - size // 6, cy, size // 2, size // 3))

        pygame.draw.circle(screen, (0, 0, 0), (cx - size // 4, cy - size // 5), size // 20)
        pygame.draw.circle(screen, (0, 0, 0), (cx - size // 12, cy - size // 5), size // 20)

        pygame.draw.polygon(
            screen,
            (150, 100, 50),
            [
                (cx - size // 6, cy - size // 12),
                (cx - size // 5, cy),
                (cx - size // 8, cy),
            ],
        )

        pygame.draw.arc(screen, (100, 50, 20), (cx - size // 4, cy - size // 12, size // 6, size // 8), 3.14, 0, 2)

    # ========== ゲームロジック ==========

    def on_enter(self) -> None:
        """ゲーム開始時の初期化"""
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        # 音声ファイルを読み込み
        self._load_animal_sounds()
        self.current_animal_index = random.randint(0, len(self.animals) - 1)

    def _trigger_animation(self) -> None:
        """動物のアニメーションをトリガー"""
        self.is_animating = True
        self.animation_time = 0.0
        self.show_sound_text = True
        self.sound_text_time = 0.0
        self.auto_switch_timer = 0.0

        # 鳴き声を再生
        animal = self.animals[self.current_animal_index]

        # 音声ファイルがあればそれを使用、なければ生成
        if animal.image_key in self.animal_sounds:
            self.current_sound = self.animal_sounds[animal.image_key]
        else:
            self.current_sound = self._create_animal_sound(animal.sound_freq)

        self.current_sound.play()

    def _next_animal(self) -> None:
        """次の動物に切り替え"""
        self.current_animal_index = (self.current_animal_index + 1) % len(self.animals)
        self.auto_switch_timer = 0.0

    def _prev_animal(self) -> None:
        """前の動物に切り替え"""
        self.current_animal_index = (self.current_animal_index - 1) % len(self.animals)
        self.auto_switch_timer = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """イベント処理"""
        for event in events:
            if self.back_button.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.request_return_to_launcher()
                elif event.key == pygame.K_LEFT:
                    self._prev_animal()
                elif event.key == pygame.K_RIGHT:
                    self._next_animal()
                elif event.key == pygame.K_SPACE:
                    self._trigger_animation()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if self.left_arrow_rect.collidepoint(x, y):
                    self._prev_animal()
                elif self.right_arrow_rect.collidepoint(x, y):
                    self._next_animal()
                else:
                    animal_area = pygame.Rect(
                        self.width // 4,
                        self.height // 4,
                        self.width // 2,
                        self.height // 2,
                    )
                    if animal_area.collidepoint(x, y):
                        self._trigger_animation()

    def update(self, dt: float) -> None:
        """更新処理"""
        if self.is_animating:
            self.animation_time += dt
            if self.animation_time >= self.animation_duration:
                self.is_animating = False

        if self.show_sound_text:
            self.sound_text_time += dt
            if self.sound_text_time >= self.sound_text_duration:
                self.show_sound_text = False

        self.auto_switch_timer += dt
        if self.auto_switch_timer >= self.auto_switch_interval:
            self._next_animal()

    def draw(self) -> None:
        """描画処理"""
        self.screen.fill(BACKGROUND_CREAM)

        animal = self.animals[self.current_animal_index]

        # 動物名を表示
        name_text = self.name_font.render(animal.name, True, (80, 80, 80))
        name_rect = name_text.get_rect(centerx=self.width // 2, top=80)
        self.screen.blit(name_text, name_rect)

        # バウンスアニメーションの計算
        bounce = 0.0
        if self.is_animating:
            progress = self.animation_time / self.animation_duration
            bounce = math.sin(progress * math.pi * 3) * (1 - progress)

        # 動物を描画
        animal_cx = self.width // 2
        animal_cy = self.height // 2 + 20
        animal_size = min(self.width, self.height) // 2

        # 画像があれば画像を表示、なければフォールバック描画
        if animal.image_key in self.animal_images:
            self._draw_animal_image(
                self.screen,
                self.animal_images[animal.image_key],
                animal_cx,
                animal_cy,
                animal_size,
                bounce,
            )
        else:
            animal.draw_func(self.screen, animal_cx, animal_cy, animal_size, bounce)

        # 鳴き声テキストを表示（吹き出し風）
        if self.show_sound_text:
            text_surface = self.sound_font.render(animal.sound_text, True, (50, 50, 50))
            text_rect = text_surface.get_rect(centerx=self.width // 2, top=self.height - 150)

            bubble_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, (255, 255, 255), bubble_rect, border_radius=15)
            pygame.draw.rect(self.screen, (100, 100, 100), bubble_rect, 3, border_radius=15)

            self.screen.blit(text_surface, text_rect)

        # 矢印ボタンを描画
        self._draw_arrow_button(self.left_arrow_rect, "left")
        self._draw_arrow_button(self.right_arrow_rect, "right")

        # ヒントテキスト
        hint_text = self.hint_font.render("Touch the animal!", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(centerx=self.width // 2, bottom=self.height - 20)
        self.screen.blit(hint_text, hint_rect)

        # 戻るボタン
        self.back_button.draw(self.screen)

    def _draw_arrow_button(self, rect: pygame.Rect, direction: str) -> None:
        """矢印ボタンを描画"""
        pygame.draw.rect(self.screen, (200, 200, 200), rect, border_radius=10)

        cx, cy = rect.center
        arrow_size = 20

        if direction == "left":
            points = [
                (cx + arrow_size // 2, cy - arrow_size),
                (cx - arrow_size // 2, cy),
                (cx + arrow_size // 2, cy + arrow_size),
            ]
        else:
            points = [
                (cx - arrow_size // 2, cy - arrow_size),
                (cx + arrow_size // 2, cy),
                (cx - arrow_size // 2, cy + arrow_size),
            ]

        pygame.draw.polygon(self.screen, (100, 100, 100), points)
