"""
VehicleGoGame - 乗り物をタップして走らせるゲーム

1〜2歳児向けに設計:
- カラフルな乗り物アイコン
- タップでエンジン音と共に走り出す
- 楽しいアニメーションとエフェクト
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

# アセットディレクトリ
ASSETS_DIR = Path(__file__).parent / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
IMAGES_DIR = ASSETS_DIR / "images"


@dataclass
class Particle:
    """パーティクルエフェクト"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: tuple[int, int, int]
    size: float


@dataclass
class Vehicle:
    """乗り物のデータ"""
    name: str  # 日本語名
    image_key: str  # 画像/音声ファイルのキー
    color: tuple[int, int, int]  # メインカラー
    secondary_color: tuple[int, int, int]  # サブカラー
    sound_freq: float  # エンジン音の周波数
    speed: float  # 移動速度（px/s）
    movement_type: str  # "horizontal", "diagonal_up", "wave"
    draw_func: Callable  # 描画関数
    y_offset: float = 0  # Y座標オフセット


class VehicleGoGame(BaseGame):
    """乗り物を走らせるゲーム"""

    name = "Vehicle Go"
    description = "乗り物をタップして走らせよう！"
    icon_path = "assets/icon.png"

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        # 乗り物データ
        self.vehicles: list[Vehicle] = []
        self._setup_vehicles()

        # 乗り物ボタンの領域
        self.vehicle_rects: list[pygame.Rect] = []
        self._setup_vehicle_rects()

        # アニメーション状態
        self.running_vehicle: Vehicle | None = None
        self.vehicle_x: float = -200
        self.vehicle_y: float = 0
        self.is_running: bool = False
        self.wheel_rotation: float = 0

        # パーティクル
        self.particles: list[Particle] = []

        # サウンド
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.current_sound: pygame.mixer.Sound | None = None

        # UI
        self.back_button = BackButton(x=20, y=20, on_click=self.request_return_to_launcher)

        # カスタムアセット
        self.custom_images: dict[str, pygame.Surface] = {}
        self.custom_sounds: dict[str, pygame.mixer.Sound] = {}
        self._load_custom_assets()

        # フォント
        self.title_font = get_font(48)
        self.name_font = get_font(24)
        self.hint_font = get_font(28)

        # アニメーション領域
        self.animation_area_y = self.height - 200

    def _setup_vehicles(self) -> None:
        """乗り物データをセットアップ"""
        self.vehicles = [
            Vehicle(
                name="くるま",
                image_key="car",
                color=BABY_RED,
                secondary_color=(200, 50, 50),
                sound_freq=150,
                speed=400,
                movement_type="horizontal",
                draw_func=self._draw_car,
            ),
            Vehicle(
                name="バス",
                image_key="bus",
                color=BABY_YELLOW,
                secondary_color=(200, 180, 50),
                sound_freq=100,
                speed=300,
                movement_type="horizontal",
                draw_func=self._draw_bus,
            ),
            Vehicle(
                name="でんしゃ",
                image_key="train",
                color=BABY_GREEN,
                secondary_color=(50, 180, 50),
                sound_freq=80,
                speed=350,
                movement_type="horizontal",
                draw_func=self._draw_train,
            ),
            Vehicle(
                name="しょうぼうしゃ",
                image_key="firetruck",
                color=(220, 50, 50),
                secondary_color=(180, 180, 180),
                sound_freq=400,
                speed=450,
                movement_type="horizontal",
                draw_func=self._draw_firetruck,
            ),
            Vehicle(
                name="ひこうき",
                image_key="airplane",
                color=WHITE,
                secondary_color=BABY_BLUE,
                sound_freq=200,
                speed=500,
                movement_type="diagonal_up",
                draw_func=self._draw_airplane,
                y_offset=-50,
            ),
            Vehicle(
                name="きゅうきゅうしゃ",
                image_key="ambulance",
                color=WHITE,
                secondary_color=BABY_RED,
                sound_freq=450,
                speed=500,
                movement_type="horizontal",
                draw_func=self._draw_ambulance,
            ),
            Vehicle(
                name="バイク",
                image_key="motorcycle",
                color=BABY_PURPLE,
                secondary_color=(100, 100, 100),
                sound_freq=250,
                speed=550,
                movement_type="horizontal",
                draw_func=self._draw_motorcycle,
            ),
            Vehicle(
                name="ふね",
                image_key="ship",
                color=BABY_BLUE,
                secondary_color=(200, 150, 100),
                sound_freq=60,
                speed=200,
                movement_type="wave",
                draw_func=self._draw_ship,
                y_offset=30,
            ),
        ]

    def _setup_vehicle_rects(self) -> None:
        """乗り物選択ボタンの領域をセットアップ"""
        self.vehicle_rects.clear()

        # グリッドレイアウト（2行 x 4列）
        cols = 4
        rows = 2
        button_size = 140
        spacing = 20

        grid_width = cols * button_size + (cols - 1) * spacing
        grid_height = rows * button_size + (rows - 1) * spacing

        start_x = (self.width - grid_width) // 2
        start_y = 120

        for i in range(len(self.vehicles)):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_size + spacing)
            y = start_y + row * (button_size + spacing)
            self.vehicle_rects.append(pygame.Rect(x, y, button_size, button_size))

    def _load_custom_assets(self) -> None:
        """カスタム画像・音声を読み込む（存在する場合のみ）"""
        for vehicle in self.vehicles:
            key = vehicle.image_key

            # カスタム画像の読み込み
            for ext in ["png", "jpg", "bmp"]:
                image_path = IMAGES_DIR / f"{key}.{ext}"
                if image_path.exists():
                    try:
                        image = pygame.image.load(str(image_path)).convert_alpha()
                        self.custom_images[key] = image
                        break
                    except pygame.error:
                        pass

            # カスタム音声の読み込み
            for ext in ["wav", "ogg", "mp3"]:
                sound_path = SOUNDS_DIR / f"{key}.{ext}"
                if sound_path.exists():
                    try:
                        sound = pygame.mixer.Sound(str(sound_path))
                        sound.set_volume(0.5)
                        self.custom_sounds[key] = sound
                        break
                    except pygame.error:
                        pass

    def _create_engine_sound(self, freq: float, duration: float = 1.5) -> pygame.mixer.Sound:
        """エンジン音を生成"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            # エンベロープ
            if t < 0.1:
                envelope = t / 0.1
            elif t < duration - 0.3:
                envelope = 1.0
            else:
                envelope = (duration - t) / 0.3

            # エンジン音（複数の周波数を組み合わせ）
            value = math.sin(2 * math.pi * freq * t)
            value += 0.5 * math.sin(2 * math.pi * freq * 1.5 * t)
            value += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            # 振動感を追加
            value *= 1 + 0.2 * math.sin(2 * math.pi * 8 * t)

            amplitude = int(15000 * envelope * value / 1.8)
            sound_array.append(max(-32767, min(32767, amplitude)))

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.4)
        return sound

    def _create_siren_sound(self, freq1: float, freq2: float) -> pygame.mixer.Sound:
        """サイレン音を生成（消防車・救急車用）"""
        sample_rate = 22050
        duration = 2.0
        samples = int(sample_rate * duration)
        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            # サイレンの周波数を切り替え
            cycle = (t * 2) % 1.0
            freq = freq1 if cycle < 0.5 else freq2

            envelope = 1.0 if t < duration - 0.2 else (duration - t) / 0.2
            value = math.sin(2 * math.pi * freq * t)
            amplitude = int(18000 * envelope * value)
            sound_array.append(max(-32767, min(32767, amplitude)))

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.35)
        return sound

    def _create_horn_sound(self, freq: float) -> pygame.mixer.Sound:
        """警笛音を生成（船用）"""
        sample_rate = 22050
        duration = 1.5
        samples = int(sample_rate * duration)
        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            if t < 0.2:
                envelope = t / 0.2
            elif t < duration - 0.5:
                envelope = 1.0
            else:
                envelope = (duration - t) / 0.5

            value = math.sin(2 * math.pi * freq * t)
            value += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            amplitude = int(20000 * envelope * value / 1.3)
            sound_array.append(max(-32767, min(32767, amplitude)))

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.4)
        return sound

    def _start_vehicle(self, vehicle: Vehicle) -> None:
        """乗り物を走らせる"""
        if self.is_running:
            return

        self.running_vehicle = vehicle
        self.vehicle_x = -200
        self.vehicle_y = self.animation_area_y + vehicle.y_offset
        self.is_running = True
        self.wheel_rotation = 0
        self.particles.clear()

        # サウンド再生（カスタム音声があれば使用）
        if vehicle.image_key in self.custom_sounds:
            self.current_sound = self.custom_sounds[vehicle.image_key]
        elif vehicle.image_key in ["firetruck", "ambulance"]:
            self.current_sound = self._create_siren_sound(400, 500)
        elif vehicle.image_key == "ship":
            self.current_sound = self._create_horn_sound(vehicle.sound_freq)
        else:
            self.current_sound = self._create_engine_sound(vehicle.sound_freq)
        self.current_sound.play()

    def _spawn_particle(self, x: float, y: float, particle_type: str) -> None:
        """パーティクルを生成"""
        if particle_type == "exhaust":
            particle = Particle(
                x=x,
                y=y,
                vx=random.uniform(-30, -10),
                vy=random.uniform(-20, 20),
                life=0.8,
                max_life=0.8,
                color=(150, 150, 150),
                size=random.uniform(5, 15),
            )
        elif particle_type == "water":
            particle = Particle(
                x=x,
                y=y,
                vx=random.uniform(-50, -20),
                vy=random.uniform(-30, 10),
                life=0.6,
                max_life=0.6,
                color=(150, 200, 255),
                size=random.uniform(3, 8),
            )
        elif particle_type == "cloud":
            particle = Particle(
                x=x,
                y=y,
                vx=random.uniform(-20, 0),
                vy=random.uniform(-10, 10),
                life=1.0,
                max_life=1.0,
                color=(255, 255, 255),
                size=random.uniform(10, 20),
            )
        else:
            return
        self.particles.append(particle)

    # ========== 乗り物の描画関数 ==========

    def _draw_car(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """車を描画"""
        # ボディ
        body_rect = pygame.Rect(x - size // 2, y - size // 4, size, size // 2)
        pygame.draw.rect(screen, vehicle.color, body_rect, border_radius=10)

        # 屋根
        roof_points = [
            (x - size // 4, y - size // 4),
            (x - size // 6, y - size // 2),
            (x + size // 4, y - size // 2),
            (x + size // 3, y - size // 4),
        ]
        pygame.draw.polygon(screen, vehicle.secondary_color, roof_points)

        # 窓
        window_rect = pygame.Rect(x - size // 6, y - size // 2 + 5, size // 3, size // 5)
        pygame.draw.rect(screen, (200, 230, 255), window_rect)

        # 車輪
        wheel_radius = size // 6
        wheel1_x = x - size // 3
        wheel2_x = x + size // 4
        wheel_y = y + size // 4

        pygame.draw.circle(screen, (50, 50, 50), (int(wheel1_x), int(wheel_y)), wheel_radius)
        pygame.draw.circle(screen, (50, 50, 50), (int(wheel2_x), int(wheel_y)), wheel_radius)

        # 車輪のスポーク
        for wheel_x in [wheel1_x, wheel2_x]:
            spoke_len = wheel_radius - 3
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle + self.wheel_rotation)
                sx = wheel_x + math.cos(rad) * spoke_len
                sy = wheel_y + math.sin(rad) * spoke_len
                pygame.draw.line(screen, (150, 150, 150), (int(wheel_x), int(wheel_y)), (int(sx), int(sy)), 2)

    def _draw_bus(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """バスを描画"""
        # ボディ（長方形）
        body_rect = pygame.Rect(x - size * 0.6, y - size // 3, size * 1.2, size * 0.6)
        pygame.draw.rect(screen, vehicle.color, body_rect, border_radius=8)

        # 窓（複数）
        window_width = size // 5
        for i in range(4):
            wx = x - size * 0.5 + i * (window_width + 8) + 10
            window_rect = pygame.Rect(wx, y - size // 4, window_width, size // 4)
            pygame.draw.rect(screen, (200, 230, 255), window_rect)

        # 車輪
        wheel_radius = size // 7
        pygame.draw.circle(screen, (50, 50, 50), (int(x - size * 0.4), int(y + size // 4)), wheel_radius)
        pygame.draw.circle(screen, (50, 50, 50), (int(x + size * 0.4), int(y + size // 4)), wheel_radius)

    def _draw_train(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """電車を描画"""
        car_width = size * 0.5
        car_height = size * 0.4

        # 3両編成
        for i in range(3):
            cx = x - size * 0.6 + i * (car_width + 5)

            # 車体
            body_rect = pygame.Rect(cx, y - car_height // 2, car_width, car_height)
            pygame.draw.rect(screen, vehicle.color, body_rect, border_radius=5)

            # 窓
            window_rect = pygame.Rect(cx + 5, y - car_height // 3, car_width - 10, car_height // 3)
            pygame.draw.rect(screen, (200, 230, 255), window_rect)

            # ライン
            line_rect = pygame.Rect(cx, y + car_height // 6, car_width, 5)
            pygame.draw.rect(screen, vehicle.secondary_color, line_rect)

            # 車輪
            pygame.draw.circle(screen, (50, 50, 50), (int(cx + car_width // 4), int(y + car_height // 2)), size // 12)
            pygame.draw.circle(screen, (50, 50, 50), (int(cx + car_width * 3 // 4), int(y + car_height // 2)), size // 12)

    def _draw_firetruck(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """消防車を描画"""
        # ボディ
        body_rect = pygame.Rect(x - size // 2, y - size // 4, size, size // 2)
        pygame.draw.rect(screen, vehicle.color, body_rect, border_radius=5)

        # 運転席
        cab_rect = pygame.Rect(x + size // 4, y - size // 2, size // 4, size // 4)
        pygame.draw.rect(screen, vehicle.color, cab_rect)

        # 窓
        window_rect = pygame.Rect(x + size // 4 + 3, y - size // 2 + 3, size // 4 - 6, size // 5)
        pygame.draw.rect(screen, (200, 230, 255), window_rect)

        # はしご
        pygame.draw.rect(screen, vehicle.secondary_color, (x - size * 0.4, y - size // 3, size * 0.6, size // 10))

        # 警告灯
        light_color = (255, 100, 100) if (pygame.time.get_ticks() // 200) % 2 == 0 else (255, 200, 200)
        pygame.draw.circle(screen, light_color, (int(x + size // 3), int(y - size // 2 - 10)), 8)

        # 車輪
        pygame.draw.circle(screen, (50, 50, 50), (int(x - size // 3), int(y + size // 4)), size // 7)
        pygame.draw.circle(screen, (50, 50, 50), (int(x + size // 4), int(y + size // 4)), size // 7)

    def _draw_airplane(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """飛行機を描画"""
        # 機体
        body_points = [
            (x + size // 2, y),
            (x + size // 4, y - size // 10),
            (x - size // 2, y - size // 10),
            (x - size // 2, y + size // 10),
            (x + size // 4, y + size // 10),
        ]
        pygame.draw.polygon(screen, vehicle.color, body_points)

        # 翼
        wing_points = [
            (x - size // 6, y - size // 10),
            (x - size // 4, y - size // 2),
            (x + size // 6, y - size // 2),
            (x + size // 6, y - size // 10),
        ]
        pygame.draw.polygon(screen, vehicle.secondary_color, wing_points)

        wing_points2 = [
            (x - size // 6, y + size // 10),
            (x - size // 4, y + size // 2),
            (x + size // 6, y + size // 2),
            (x + size // 6, y + size // 10),
        ]
        pygame.draw.polygon(screen, vehicle.secondary_color, wing_points2)

        # 尾翼
        tail_points = [
            (x - size // 2, y - size // 10),
            (x - size * 0.6, y - size // 3),
            (x - size * 0.4, y - size // 10),
        ]
        pygame.draw.polygon(screen, vehicle.secondary_color, tail_points)

        # 窓
        for i in range(3):
            wx = x + size // 4 - i * (size // 6)
            pygame.draw.circle(screen, (200, 230, 255), (int(wx), int(y)), 5)

    def _draw_ambulance(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """救急車を描画"""
        # ボディ
        body_rect = pygame.Rect(x - size // 2, y - size // 4, size, size // 2)
        pygame.draw.rect(screen, vehicle.color, body_rect, border_radius=5)

        # 赤いライン
        line_rect = pygame.Rect(x - size // 2, y - size // 8, size, size // 8)
        pygame.draw.rect(screen, vehicle.secondary_color, line_rect)

        # 赤十字
        cross_size = size // 6
        pygame.draw.rect(screen, vehicle.secondary_color, (x - cross_size // 2, y - size // 6 - cross_size, cross_size, cross_size * 2))
        pygame.draw.rect(screen, vehicle.secondary_color, (x - cross_size, y - size // 6 - cross_size // 2, cross_size * 2, cross_size))

        # 警告灯
        light_color = (255, 50, 50) if (pygame.time.get_ticks() // 150) % 2 == 0 else (50, 50, 255)
        pygame.draw.circle(screen, light_color, (int(x), int(y - size // 4 - 10)), 8)

        # 車輪
        pygame.draw.circle(screen, (50, 50, 50), (int(x - size // 3), int(y + size // 4)), size // 7)
        pygame.draw.circle(screen, (50, 50, 50), (int(x + size // 3), int(y + size // 4)), size // 7)

    def _draw_motorcycle(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """バイクを描画"""
        # フレーム
        frame_points = [
            (x - size // 3, y),
            (x, y - size // 4),
            (x + size // 4, y),
        ]
        pygame.draw.lines(screen, vehicle.color, False, frame_points, 5)

        # タンク
        tank_rect = pygame.Rect(x - size // 6, y - size // 4, size // 3, size // 6)
        pygame.draw.ellipse(screen, vehicle.color, tank_rect)

        # シート
        pygame.draw.ellipse(screen, (50, 50, 50), (x - size // 8, y - size // 5, size // 4, size // 8))

        # ハンドル
        pygame.draw.line(screen, vehicle.secondary_color, (x + size // 6, y - size // 4), (x + size // 4, y - size // 3), 4)

        # 車輪
        wheel_radius = size // 5
        pygame.draw.circle(screen, (50, 50, 50), (int(x - size // 3), int(y + size // 6)), wheel_radius)
        pygame.draw.circle(screen, (50, 50, 50), (int(x + size // 4), int(y + size // 6)), wheel_radius)

        # スポーク
        for wheel_x in [x - size // 3, x + size // 4]:
            for angle in range(0, 360, 45):
                rad = math.radians(angle + self.wheel_rotation)
                sx = wheel_x + math.cos(rad) * (wheel_radius - 3)
                sy = y + size // 6 + math.sin(rad) * (wheel_radius - 3)
                pygame.draw.line(screen, (150, 150, 150), (int(wheel_x), int(y + size // 6)), (int(sx), int(sy)), 2)

    def _draw_ship(self, screen: pygame.Surface, x: float, y: float, size: float, vehicle: Vehicle) -> None:
        """船を描画"""
        # 波のアニメーション
        wave_offset = math.sin(pygame.time.get_ticks() / 200) * 5
        y += wave_offset

        # 船体
        hull_points = [
            (x - size // 2, y),
            (x - size * 0.4, y + size // 3),
            (x + size * 0.4, y + size // 3),
            (x + size // 2, y),
        ]
        pygame.draw.polygon(screen, vehicle.secondary_color, hull_points)

        # 甲板
        deck_rect = pygame.Rect(x - size * 0.4, y - size // 6, size * 0.8, size // 4)
        pygame.draw.rect(screen, vehicle.color, deck_rect)

        # 煙突
        pygame.draw.rect(screen, (100, 100, 100), (x - size // 10, y - size // 3, size // 5, size // 4))

        # 窓
        for i in range(3):
            wx = x - size // 4 + i * (size // 4)
            pygame.draw.circle(screen, (200, 230, 255), (int(wx), int(y)), 6)

        # 波（水面）
        wave_y = y + size // 3 + 10
        for i in range(-2, 3):
            wave_x = x + i * 30 + (pygame.time.get_ticks() // 50) % 30
            pygame.draw.arc(screen, (100, 180, 255),
                          (wave_x - 15, wave_y - 5, 30, 20), 0, math.pi, 3)

    # ========== アイコン描画（選択画面用） ==========

    def _draw_vehicle_icon(self, screen: pygame.Surface, vehicle: Vehicle, rect: pygame.Rect) -> None:
        """乗り物アイコンを描画"""
        # 背景
        pygame.draw.rect(screen, vehicle.color, rect, border_radius=15)
        pygame.draw.rect(screen, (50, 50, 50), rect, 3, border_radius=15)

        cx = rect.centerx
        cy = rect.centery - 10
        icon_size = rect.width * 0.6

        # カスタム画像があれば使用、なければプリミティブ描画
        if vehicle.image_key in self.custom_images:
            image = self.custom_images[vehicle.image_key]
            # アイコンサイズにスケール
            scaled = pygame.transform.scale(image, (int(icon_size), int(icon_size * 0.7)))
            image_rect = scaled.get_rect(center=(cx, cy))
            screen.blit(scaled, image_rect)
        else:
            vehicle.draw_func(screen, cx, cy, icon_size, vehicle)

        # 名前
        name_surface = self.name_font.render(vehicle.name, True, WHITE)
        name_rect = name_surface.get_rect(centerx=rect.centerx, bottom=rect.bottom - 5)
        screen.blit(name_surface, name_rect)

    # ========== ゲームロジック ==========

    def on_enter(self) -> None:
        """ゲーム開始時の初期化"""
        if not pygame.mixer.get_init():
            pygame.mixer.init()

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
                    for i, rect in enumerate(self.vehicle_rects):
                        if rect.collidepoint(x, y):
                            self._start_vehicle(self.vehicles[i])
                            break

    def update(self, dt: float) -> None:
        """更新処理"""
        if self.is_running and self.running_vehicle:
            vehicle = self.running_vehicle

            # 位置更新
            self.vehicle_x += vehicle.speed * dt

            # 移動タイプ別の処理
            if vehicle.movement_type == "diagonal_up":
                self.vehicle_y -= vehicle.speed * 0.3 * dt
            elif vehicle.movement_type == "wave":
                self.vehicle_y = self.animation_area_y + vehicle.y_offset + math.sin(self.vehicle_x / 50) * 15

            # 車輪回転
            self.wheel_rotation += vehicle.speed * dt * 0.5

            # パーティクル生成
            if random.random() < 0.3:
                if vehicle.movement_type == "wave":
                    self._spawn_particle(self.vehicle_x - 50, self.vehicle_y + 40, "water")
                elif vehicle.image_key == "airplane":
                    self._spawn_particle(self.vehicle_x - 80, self.vehicle_y, "cloud")
                else:
                    self._spawn_particle(self.vehicle_x - 60, self.vehicle_y + 20, "exhaust")

            # 画面外判定
            if self.vehicle_x > self.width + 200:
                self.is_running = False
                self.running_vehicle = None

        # パーティクル更新
        for particle in self.particles[:]:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.life -= dt
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw(self) -> None:
        """描画処理"""
        self.screen.fill(BACKGROUND_CREAM)

        # タイトル
        title_text = self.title_font.render("のりものビュンビュン", True, (80, 80, 80))
        title_rect = title_text.get_rect(centerx=self.width // 2, top=20)
        self.screen.blit(title_text, title_rect)

        # 乗り物選択グリッド
        for i, vehicle in enumerate(self.vehicles):
            self._draw_vehicle_icon(self.screen, vehicle, self.vehicle_rects[i])

        # アニメーション領域の背景
        animation_rect = pygame.Rect(0, self.animation_area_y - 50, self.width, 200)
        pygame.draw.rect(self.screen, (230, 240, 250), animation_rect)

        # 地面/水面
        ground_y = self.animation_area_y + 80
        pygame.draw.rect(self.screen, (200, 200, 200), (0, ground_y, self.width, 5))

        # パーティクル描画
        for particle in self.particles:
            alpha = int(255 * (particle.life / particle.max_life))
            size = int(particle.size * (particle.life / particle.max_life))
            if size > 0:
                pygame.draw.circle(self.screen, particle.color,
                                 (int(particle.x), int(particle.y)), size)

        # 走行中の乗り物
        if self.is_running and self.running_vehicle:
            vehicle = self.running_vehicle
            if vehicle.image_key in self.custom_images:
                # カスタム画像を使用
                image = self.custom_images[vehicle.image_key]
                scaled = pygame.transform.scale(image, (150, 100))
                image_rect = scaled.get_rect(center=(int(self.vehicle_x), int(self.vehicle_y)))
                self.screen.blit(scaled, image_rect)
            else:
                # プリミティブ描画
                vehicle.draw_func(
                    self.screen,
                    self.vehicle_x,
                    self.vehicle_y,
                    120,
                    vehicle
                )

        # ヒント
        if not self.is_running:
            hint_text = self.hint_font.render("のりものをタップしよう！", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(centerx=self.width // 2, bottom=self.height - 20)
            self.screen.blit(hint_text, hint_rect)

        # 戻るボタン
        self.back_button.draw(self.screen)
