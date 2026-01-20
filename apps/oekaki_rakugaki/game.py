"""
OekakiRakugakiGame - お絵かきらくがきアプリ

1〜2歳児向けに設計:
- 画面をなぞってカラフルな線を描く
- 7色パレットから色を選択
- 3段階のペンサイズ
- スタンプ機能（星・ハート・花）
- 楽しい音のフィードバック
"""

import array
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pygame

from shared.base_game import BaseGame
from shared.components import BackButton
from shared.constants import (
    BABY_BLUE,
    BABY_COLORS,
    BABY_GREEN,
    BABY_ORANGE,
    BABY_PINK,
    BABY_PURPLE,
    BABY_RED,
    BABY_YELLOW,
    WHITE,
)
from shared.fonts import get_font

# アセットディレクトリ
ASSETS_DIR = Path(__file__).parent / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
IMAGES_DIR = ASSETS_DIR / "images"


@dataclass
class Stamp:
    """スタンプデータ"""

    name: str
    image_key: str
    draw_func: Callable


class OekakiRakugakiGame(BaseGame):
    """お絵かきらくがきゲーム"""

    name = "Oekaki"
    description = "自由にお絵かきしよう！"
    icon_path = "assets/icon.png"

    # レイアウト定数
    HEADER_HEIGHT = 70
    TOOLBAR_HEIGHT = 110
    CANVAS_MARGIN = 10

    # ペンサイズ
    PEN_SIZES = [8, 16, 24]

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        # キャンバス設定
        self.canvas_rect = pygame.Rect(
            self.CANVAS_MARGIN,
            self.HEADER_HEIGHT,
            self.width - self.CANVAS_MARGIN * 2,
            self.height - self.HEADER_HEIGHT - self.TOOLBAR_HEIGHT,
        )
        self.canvas = pygame.Surface(
            (self.canvas_rect.width, self.canvas_rect.height)
        )
        self.canvas.fill(WHITE)

        # 描画状態
        self.is_drawing = False
        self.last_pos: tuple[int, int] | None = None
        self.current_color = BABY_RED
        self.current_size = self.PEN_SIZES[1]  # 中サイズ

        # スタンプ
        self.stamps = self._setup_stamps()
        self.is_stamp_mode = False
        self.selected_stamp_index = 0

        # UI要素の領域
        self.color_rects: list[pygame.Rect] = []
        self.size_rects: list[pygame.Rect] = []
        self.stamp_rects: list[pygame.Rect] = []
        self.clear_rect = pygame.Rect(0, 0, 0, 0)
        self._setup_ui_rects()

        # 戻るボタン
        self.back_button = BackButton(x=20, y=15, on_click=self.request_return_to_launcher)

        # フォント
        self.title_font = get_font(36)
        self.button_font = get_font(20)

        # サウンド
        self.custom_sounds: dict[str, pygame.mixer.Sound] = {}
        self.pop_sound: pygame.mixer.Sound | None = None
        self.sparkle_sound: pygame.mixer.Sound | None = None

        # カスタムアセット
        self.custom_images: dict[str, pygame.Surface] = {}
        self._load_custom_assets()

    def _setup_stamps(self) -> list[Stamp]:
        """スタンプをセットアップ"""
        return [
            Stamp(name="ほし", image_key="star", draw_func=self._draw_star),
            Stamp(name="ハート", image_key="heart", draw_func=self._draw_heart),
            Stamp(name="はな", image_key="flower", draw_func=self._draw_flower),
        ]

    def _setup_ui_rects(self) -> None:
        """UI要素の領域をセットアップ"""
        toolbar_y = self.height - self.TOOLBAR_HEIGHT + 10

        # 色パレット（7色）
        color_size = 50
        color_spacing = 8
        colors_width = len(BABY_COLORS) * color_size + (len(BABY_COLORS) - 1) * color_spacing
        color_start_x = 30

        self.color_rects = []
        for i in range(len(BABY_COLORS)):
            x = color_start_x + i * (color_size + color_spacing)
            self.color_rects.append(pygame.Rect(x, toolbar_y + 5, color_size, color_size))

        # サイズボタン（3サイズ）
        size_button_size = 50
        size_spacing = 8
        size_start_x = color_start_x + colors_width + 40

        self.size_rects = []
        for i in range(3):
            x = size_start_x + i * (size_button_size + size_spacing)
            self.size_rects.append(pygame.Rect(x, toolbar_y + 5, size_button_size, size_button_size))

        # スタンプボタン（3つ）
        stamp_button_size = 50
        stamp_spacing = 8
        stamp_start_x = size_start_x + 3 * (size_button_size + size_spacing) + 30

        self.stamp_rects = []
        for i in range(len(self.stamps)):
            x = stamp_start_x + i * (stamp_button_size + stamp_spacing)
            self.stamp_rects.append(pygame.Rect(x, toolbar_y + 5, stamp_button_size, stamp_button_size))

        # クリアボタン
        self.clear_rect = pygame.Rect(self.width - 120, 15, 100, 40)

    def _load_custom_assets(self) -> None:
        """カスタム画像・音声を読み込む"""
        # スタンプ画像
        for stamp in self.stamps:
            for ext in ["png", "jpg", "bmp"]:
                image_path = IMAGES_DIR / f"{stamp.image_key}.{ext}"
                if image_path.exists():
                    try:
                        image = pygame.image.load(str(image_path)).convert_alpha()
                        self.custom_images[stamp.image_key] = image
                        break
                    except pygame.error:
                        pass

        # 音声
        for sound_name in ["pop", "sparkle"]:
            for ext in ["wav", "ogg", "mp3"]:
                sound_path = SOUNDS_DIR / f"{sound_name}.{ext}"
                if sound_path.exists():
                    try:
                        sound = pygame.mixer.Sound(str(sound_path))
                        sound.set_volume(0.5)
                        self.custom_sounds[sound_name] = sound
                        break
                    except pygame.error:
                        pass

    def _create_pop_sound(self) -> pygame.mixer.Sound:
        """ポップ音を生成"""
        sample_rate = 22050
        duration = 0.05
        samples = int(sample_rate * duration)
        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            envelope = 1.0 - (t / duration)  # 減衰
            freq = 800 + random.uniform(-50, 50)
            value = math.sin(2 * math.pi * freq * t)
            amplitude = int(8000 * envelope * value)
            sound_array.append(max(-32767, min(32767, amplitude)))

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.3)
        return sound

    def _create_sparkle_sound(self) -> pygame.mixer.Sound:
        """キラキラ音を生成"""
        sample_rate = 22050
        duration = 0.15
        samples = int(sample_rate * duration)
        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            envelope = 1.0 - (t / duration) ** 0.5

            # 複数の高周波を組み合わせ
            value = 0.0
            for freq in [1200, 1500, 1800, 2100]:
                value += math.sin(2 * math.pi * freq * t) * (1.0 / 4)

            amplitude = int(10000 * envelope * value)
            sound_array.append(max(-32767, min(32767, amplitude)))

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.25)
        return sound

    def _play_pop_sound(self) -> None:
        """ポップ音を再生"""
        if "pop" in self.custom_sounds:
            self.custom_sounds["pop"].play()
        elif self.pop_sound:
            self.pop_sound.play()

    def _play_sparkle_sound(self) -> None:
        """キラキラ音を再生"""
        if "sparkle" in self.custom_sounds:
            self.custom_sounds["sparkle"].play()
        elif self.sparkle_sound:
            self.sparkle_sound.play()

    # ========== スタンプ描画関数 ==========

    def _draw_star(
        self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple[int, int, int]
    ) -> None:
        """星を描画"""
        points = []
        for i in range(5):
            # 外側の点
            angle = math.radians(i * 72 - 90)
            px = x + math.cos(angle) * size
            py = y + math.sin(angle) * size
            points.append((px, py))

            # 内側の点
            angle = math.radians(i * 72 - 90 + 36)
            px = x + math.cos(angle) * (size * 0.4)
            py = y + math.sin(angle) * (size * 0.4)
            points.append((px, py))

        pygame.draw.polygon(surface, color, points)

    def _draw_heart(
        self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple[int, int, int]
    ) -> None:
        """ハートを描画"""
        # 上部の2つの円
        radius = size * 0.5
        pygame.draw.circle(surface, color, (int(x - radius * 0.5), int(y - radius * 0.3)), int(radius))
        pygame.draw.circle(surface, color, (int(x + radius * 0.5), int(y - radius * 0.3)), int(radius))

        # 下部の三角形
        points = [
            (x - size, y),
            (x + size, y),
            (x, y + size * 1.2),
        ]
        pygame.draw.polygon(surface, color, points)

    def _draw_flower(
        self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple[int, int, int]
    ) -> None:
        """花を描画"""
        petal_radius = size * 0.5
        center_radius = size * 0.3

        # 5枚の花びら
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            px = x + math.cos(angle) * petal_radius
            py = y + math.sin(angle) * petal_radius
            pygame.draw.circle(surface, color, (int(px), int(py)), int(petal_radius))

        # 中心
        center_color = BABY_YELLOW if color != BABY_YELLOW else BABY_ORANGE
        pygame.draw.circle(surface, center_color, (x, y), int(center_radius))

    def _draw_stamp_on_canvas(self, x: int, y: int) -> None:
        """キャンバスにスタンプを描画"""
        stamp = self.stamps[self.selected_stamp_index]
        stamp_size = 40

        # カスタム画像があれば使用
        if stamp.image_key in self.custom_images:
            image = self.custom_images[stamp.image_key]
            scaled = pygame.transform.scale(image, (stamp_size * 2, stamp_size * 2))
            rect = scaled.get_rect(center=(x, y))
            self.canvas.blit(scaled, rect)
        else:
            # プリミティブ描画
            stamp.draw_func(self.canvas, x, y, stamp_size, self.current_color)

        self._play_sparkle_sound()

    # ========== ゲームロジック ==========

    def on_enter(self) -> None:
        """ゲーム開始時の初期化"""
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # サウンド生成
        self.pop_sound = self._create_pop_sound()
        self.sparkle_sound = self._create_sparkle_sound()

    def _clear_canvas(self) -> None:
        """キャンバスをクリア"""
        self.canvas.fill(WHITE)
        self._play_sparkle_sound()

    def _get_canvas_pos(self, screen_pos: tuple[int, int]) -> tuple[int, int] | None:
        """スクリーン座標をキャンバス座標に変換"""
        x, y = screen_pos
        if self.canvas_rect.collidepoint(x, y):
            return (x - self.canvas_rect.x, y - self.canvas_rect.y)
        return None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """イベント処理"""
        for event in events:
            if self.back_button.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.request_return_to_launcher()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos

                    # クリアボタン
                    if self.clear_rect.collidepoint(x, y):
                        self._clear_canvas()
                        continue

                    # 色パレット
                    for i, rect in enumerate(self.color_rects):
                        if rect.collidepoint(x, y):
                            self.current_color = BABY_COLORS[i]
                            self.is_stamp_mode = False
                            self._play_pop_sound()
                            continue

                    # サイズボタン
                    for i, rect in enumerate(self.size_rects):
                        if rect.collidepoint(x, y):
                            self.current_size = self.PEN_SIZES[i]
                            self.is_stamp_mode = False
                            self._play_pop_sound()
                            continue

                    # スタンプボタン
                    for i, rect in enumerate(self.stamp_rects):
                        if rect.collidepoint(x, y):
                            self.is_stamp_mode = True
                            self.selected_stamp_index = i
                            self._play_pop_sound()
                            continue

                    # キャンバス
                    canvas_pos = self._get_canvas_pos((x, y))
                    if canvas_pos:
                        if self.is_stamp_mode:
                            self._draw_stamp_on_canvas(canvas_pos[0], canvas_pos[1])
                        else:
                            self.is_drawing = True
                            self.last_pos = canvas_pos
                            # 点を描画
                            pygame.draw.circle(
                                self.canvas, self.current_color, canvas_pos, self.current_size // 2
                            )
                            self._play_pop_sound()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_drawing = False
                    self.last_pos = None

            elif event.type == pygame.MOUSEMOTION:
                if self.is_drawing and not self.is_stamp_mode:
                    canvas_pos = self._get_canvas_pos(event.pos)
                    if canvas_pos and self.last_pos:
                        # 線を描画
                        pygame.draw.line(
                            self.canvas,
                            self.current_color,
                            self.last_pos,
                            canvas_pos,
                            self.current_size,
                        )
                        # 端を丸くするため円も描画
                        pygame.draw.circle(
                            self.canvas, self.current_color, canvas_pos, self.current_size // 2
                        )
                        self.last_pos = canvas_pos

    def update(self, dt: float) -> None:
        """更新処理（特になし）"""
        pass

    def draw(self) -> None:
        """描画処理"""
        # 背景
        self.screen.fill((245, 245, 250))

        # ヘッダー背景
        pygame.draw.rect(self.screen, (230, 230, 240), (0, 0, self.width, self.HEADER_HEIGHT))

        # タイトル
        title_text = self.title_font.render("おえかきらくがき", True, (80, 80, 80))
        title_rect = title_text.get_rect(centery=self.HEADER_HEIGHT // 2, left=100)
        self.screen.blit(title_text, title_rect)

        # クリアボタン
        pygame.draw.rect(self.screen, (220, 100, 100), self.clear_rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 80, 80), self.clear_rect, 2, border_radius=8)
        clear_text = self.button_font.render("クリア", True, WHITE)
        clear_text_rect = clear_text.get_rect(center=self.clear_rect.center)
        self.screen.blit(clear_text, clear_text_rect)

        # キャンバス（枠線付き）
        pygame.draw.rect(self.screen, (200, 200, 200), self.canvas_rect.inflate(4, 4), border_radius=5)
        self.screen.blit(self.canvas, self.canvas_rect)

        # ツールバー背景
        toolbar_rect = pygame.Rect(0, self.height - self.TOOLBAR_HEIGHT, self.width, self.TOOLBAR_HEIGHT)
        pygame.draw.rect(self.screen, (230, 230, 240), toolbar_rect)

        # 色パレット
        for i, rect in enumerate(self.color_rects):
            color = BABY_COLORS[i]
            pygame.draw.rect(self.screen, color, rect, border_radius=8)

            # 選択中の色は枠線を太く
            if color == self.current_color and not self.is_stamp_mode:
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 4, border_radius=8)
            else:
                pygame.draw.rect(self.screen, (150, 150, 150), rect, 2, border_radius=8)

        # サイズボタン
        for i, rect in enumerate(self.size_rects):
            # 背景
            bg_color = (200, 200, 210) if self.current_size == self.PEN_SIZES[i] and not self.is_stamp_mode else (240, 240, 245)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)

            # 枠線
            border_color = (50, 50, 50) if self.current_size == self.PEN_SIZES[i] and not self.is_stamp_mode else (150, 150, 150)
            border_width = 3 if self.current_size == self.PEN_SIZES[i] and not self.is_stamp_mode else 2
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)

            # サイズ表示（円）
            pygame.draw.circle(
                self.screen, (80, 80, 80), rect.center, self.PEN_SIZES[i] // 2
            )

        # スタンプボタン
        for i, rect in enumerate(self.stamp_rects):
            # 背景
            bg_color = (200, 200, 210) if self.is_stamp_mode and self.selected_stamp_index == i else (240, 240, 245)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)

            # 枠線
            border_color = (50, 50, 50) if self.is_stamp_mode and self.selected_stamp_index == i else (150, 150, 150)
            border_width = 3 if self.is_stamp_mode and self.selected_stamp_index == i else 2
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)

            # スタンプアイコン
            stamp = self.stamps[i]
            if stamp.image_key in self.custom_images:
                image = self.custom_images[stamp.image_key]
                scaled = pygame.transform.scale(image, (30, 30))
                img_rect = scaled.get_rect(center=rect.center)
                self.screen.blit(scaled, img_rect)
            else:
                stamp.draw_func(self.screen, rect.centerx, rect.centery, 15, BABY_COLORS[i % len(BABY_COLORS)])

        # 戻るボタン
        self.back_button.draw(self.screen)
