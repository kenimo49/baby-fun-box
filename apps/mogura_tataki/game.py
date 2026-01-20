"""
MoguraTatakiGame - もぐらたたき

1〜2歳児向けに設計:
- かわいい動物が穴から顔を出す
- タップすると楽しいリアクション
- ゆっくりペースで焦らず遊べる
- スコアやタイムリミットなし
"""

import array
import math
import random
from dataclasses import dataclass
from pathlib import Path

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
class Hole:
    """穴のデータ"""

    x: int
    y: int
    rect: pygame.Rect
    is_active: bool = False  # キャラクターが出ているか
    character_index: int = 0  # どのキャラクター
    pop_progress: float = 0.0  # 出現アニメーション (0.0-1.0)
    show_timer: float = 0.0  # 表示残り時間
    was_tapped: bool = False  # タップされたか
    tap_animation: float = 0.0  # タップアニメーション


@dataclass
class Character:
    """キャラクターのデータ"""

    name: str
    color: tuple[int, int, int]
    image_key: str


class MoguraTatakiGame(BaseGame):
    """もぐらたたきゲーム"""

    name = "Mogura"
    description = "出てきた動物をタッチしよう！"
    icon_path = "assets/icon.png"

    # グリッド設定
    GRID_COLS = 3
    GRID_ROWS = 2
    HOLE_SIZE = 140

    # タイミング設定
    MIN_SHOW_TIME = 2.0  # 最小表示時間
    MAX_SHOW_TIME = 4.0  # 最大表示時間
    POP_SPEED = 3.0  # 出現速度
    SPAWN_INTERVAL = 1.5  # 出現間隔

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        # キャラクター
        self.characters = [
            Character(name="うさぎ", color=BABY_PINK, image_key="rabbit"),
            Character(name="くま", color=BABY_ORANGE, image_key="bear"),
            Character(name="ねこ", color=BABY_YELLOW, image_key="cat"),
            Character(name="いぬ", color=BABY_BLUE, image_key="dog"),
            Character(name="ひよこ", color=BABY_YELLOW, image_key="chick"),
            Character(name="かえる", color=BABY_GREEN, image_key="frog"),
        ]

        # 穴のセットアップ
        self.holes: list[Hole] = []
        self._setup_holes()

        # ゲーム状態
        self.spawn_timer = 1.0  # 最初の出現までの時間
        self.active_count = 0  # 現在出ているキャラクター数

        # エフェクト
        self.particles: list[dict] = []

        # サウンド
        self.custom_sounds: dict[str, pygame.mixer.Sound] = {}
        self.pop_sound: pygame.mixer.Sound | None = None
        self.tap_sound: pygame.mixer.Sound | None = None
        self.miss_sound: pygame.mixer.Sound | None = None

        # カスタム画像
        self.custom_images: dict[str, pygame.Surface] = {}
        self._load_custom_assets()

        # UI
        self.back_button = BackButton(x=20, y=20, on_click=self.request_return_to_launcher)

        # フォント
        self.title_font = get_font(42)
        self.hint_font = get_font(28)

    def _setup_holes(self) -> None:
        """穴をセットアップ"""
        self.holes.clear()

        # グリッドのサイズを計算
        spacing_x = 180
        spacing_y = 200
        grid_width = (self.GRID_COLS - 1) * spacing_x
        grid_height = (self.GRID_ROWS - 1) * spacing_y

        start_x = (self.width - grid_width) // 2
        start_y = 200

        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y

                hole = Hole(
                    x=x,
                    y=y,
                    rect=pygame.Rect(
                        x - self.HOLE_SIZE // 2,
                        y - self.HOLE_SIZE // 2,
                        self.HOLE_SIZE,
                        self.HOLE_SIZE,
                    ),
                )
                self.holes.append(hole)

    def _load_custom_assets(self) -> None:
        """カスタムアセットを読み込む"""
        # キャラクター画像
        for char in self.characters:
            for ext in ["png", "jpg", "bmp"]:
                image_path = IMAGES_DIR / f"{char.image_key}.{ext}"
                if image_path.exists():
                    try:
                        image = pygame.image.load(str(image_path)).convert_alpha()
                        self.custom_images[char.image_key] = image
                        break
                    except pygame.error:
                        pass

        # サウンド
        for sound_name in ["pop", "tap", "miss"]:
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
        """ポップアップ音を生成"""
        sample_rate = 22050
        duration = 0.1
        samples = int(sample_rate * duration)
        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            # 上昇するピッチ
            freq = 400 + (800 * t / duration)
            envelope = 1.0 - (t / duration) ** 2
            value = math.sin(2 * math.pi * freq * t)
            amplitude = int(12000 * envelope * value)
            sound_array.append(max(-32767, min(32767, amplitude)))

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.3)
        return sound

    def _create_tap_sound(self) -> pygame.mixer.Sound:
        """タップ成功音を生成"""
        sample_rate = 22050
        duration = 0.15
        samples = int(sample_rate * duration)
        sound_array = array.array("h")

        for i in range(samples):
            t = i / sample_rate
            envelope = 1.0 - (t / duration)

            # 明るい和音
            value = 0.0
            for freq in [523, 659, 784]:  # C, E, G
                value += math.sin(2 * math.pi * freq * t) / 3

            amplitude = int(15000 * envelope * value)
            sound_array.append(max(-32767, min(32767, amplitude)))

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.35)
        return sound

    def _play_pop_sound(self) -> None:
        """ポップ音を再生"""
        if "pop" in self.custom_sounds:
            self.custom_sounds["pop"].play()
        elif self.pop_sound:
            self.pop_sound.play()

    def _play_tap_sound(self) -> None:
        """タップ音を再生"""
        if "tap" in self.custom_sounds:
            self.custom_sounds["tap"].play()
        elif self.tap_sound:
            self.tap_sound.play()

    def _spawn_character(self) -> None:
        """キャラクターを出現させる"""
        # 空いている穴を探す
        available_holes = [h for h in self.holes if not h.is_active]
        if not available_holes:
            return

        hole = random.choice(available_holes)
        hole.is_active = True
        hole.character_index = random.randint(0, len(self.characters) - 1)
        hole.pop_progress = 0.0
        hole.show_timer = random.uniform(self.MIN_SHOW_TIME, self.MAX_SHOW_TIME)
        hole.was_tapped = False
        hole.tap_animation = 0.0

        self.active_count += 1
        self._play_pop_sound()

    def _spawn_particles(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        """パーティクルを生成"""
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 200)
            self.particles.append({
                "x": float(x),
                "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 0.5,
                "color": color,
                "size": random.uniform(8, 15),
            })

    # ========== キャラクター描画 ==========

    def _draw_character(
        self, screen: pygame.Surface, char: Character, x: int, y: int, size: int, progress: float
    ) -> None:
        """キャラクターを描画"""
        # 出現アニメーション（下から上へ）
        visible_height = int(size * min(progress, 1.0))
        if visible_height <= 0:
            return

        # カスタム画像があれば使用
        if char.image_key in self.custom_images:
            image = self.custom_images[char.image_key]
            scaled = pygame.transform.scale(image, (size, size))

            # クリップして表示
            clip_rect = pygame.Rect(0, size - visible_height, size, visible_height)
            clipped = scaled.subsurface(clip_rect)
            screen.blit(clipped, (x - size // 2, y - visible_height + size // 4))
        else:
            # プリミティブ描画
            self._draw_character_primitive(screen, char, x, y, size, visible_height)

    def _draw_character_primitive(
        self,
        screen: pygame.Surface,
        char: Character,
        x: int,
        y: int,
        size: int,
        visible_height: int,
    ) -> None:
        """キャラクターをプリミティブで描画"""
        # 顔（円）
        face_size = size * 0.8
        face_y = y - visible_height // 2 + size // 4

        if visible_height > size * 0.3:
            pygame.draw.circle(screen, char.color, (x, int(face_y)), int(face_size // 2))

            # 目
            eye_offset = face_size * 0.2
            eye_y = face_y - face_size * 0.1
            pygame.draw.circle(screen, (50, 50, 50), (int(x - eye_offset), int(eye_y)), 6)
            pygame.draw.circle(screen, (50, 50, 50), (int(x + eye_offset), int(eye_y)), 6)
            pygame.draw.circle(screen, WHITE, (int(x - eye_offset - 2), int(eye_y - 2)), 2)
            pygame.draw.circle(screen, WHITE, (int(x + eye_offset - 2), int(eye_y - 2)), 2)

            # 口（笑顔）
            mouth_y = face_y + face_size * 0.15
            pygame.draw.arc(
                screen,
                (50, 50, 50),
                (int(x - face_size * 0.2), int(mouth_y - face_size * 0.1),
                 int(face_size * 0.4), int(face_size * 0.2)),
                math.pi, 0, 2
            )

            # 耳（キャラクターによって異なる）
            if char.image_key in ["rabbit", "cat"]:
                # 尖った耳
                ear_size = face_size * 0.3
                pygame.draw.polygon(
                    screen, char.color,
                    [(x - face_size * 0.3, face_y - face_size * 0.3),
                     (x - face_size * 0.4, face_y - face_size * 0.7),
                     (x - face_size * 0.15, face_y - face_size * 0.4)]
                )
                pygame.draw.polygon(
                    screen, char.color,
                    [(x + face_size * 0.3, face_y - face_size * 0.3),
                     (x + face_size * 0.4, face_y - face_size * 0.7),
                     (x + face_size * 0.15, face_y - face_size * 0.4)]
                )
            elif char.image_key in ["bear", "dog"]:
                # 丸い耳
                ear_radius = face_size * 0.15
                pygame.draw.circle(screen, char.color, (int(x - face_size * 0.35), int(face_y - face_size * 0.35)), int(ear_radius))
                pygame.draw.circle(screen, char.color, (int(x + face_size * 0.35), int(face_y - face_size * 0.35)), int(ear_radius))

            # 頬（ピンク）
            cheek_y = face_y + face_size * 0.05
            pygame.draw.circle(screen, (255, 180, 180), (int(x - face_size * 0.3), int(cheek_y)), 5)
            pygame.draw.circle(screen, (255, 180, 180), (int(x + face_size * 0.3), int(cheek_y)), 5)

    def _draw_hole(self, screen: pygame.Surface, hole: Hole) -> None:
        """穴を描画"""
        x, y = hole.x, hole.y

        # 穴の背景（茶色の楕円）
        hole_width = self.HOLE_SIZE
        hole_height = self.HOLE_SIZE // 3

        # 穴の影
        pygame.draw.ellipse(
            screen,
            (80, 60, 40),
            (x - hole_width // 2 - 5, y + 20, hole_width + 10, hole_height + 10)
        )

        # 穴
        pygame.draw.ellipse(
            screen,
            (50, 35, 20),
            (x - hole_width // 2, y + 25, hole_width, hole_height)
        )

        # キャラクター
        if hole.is_active:
            char = self.characters[hole.character_index]

            # タップされた時のアニメーション
            char_y = y
            if hole.was_tapped and hole.tap_animation > 0:
                # 上に跳ねる
                bounce = math.sin(hole.tap_animation * math.pi) * 30
                char_y -= bounce

            self._draw_character(screen, char, x, int(char_y), 100, hole.pop_progress)

        # 穴の縁（前面）
        pygame.draw.ellipse(
            screen,
            (100, 80, 50),
            (x - hole_width // 2, y + 25, hole_width, hole_height),
            4
        )

    # ========== ゲームロジック ==========

    def on_enter(self) -> None:
        """ゲーム開始時の初期化"""
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.pop_sound = self._create_pop_sound()
        self.tap_sound = self._create_tap_sound()

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

                    # 穴のクリック判定
                    for hole in self.holes:
                        if hole.is_active and not hole.was_tapped:
                            # 顔の領域で判定（穴の上部）
                            face_rect = pygame.Rect(
                                hole.x - 50,
                                hole.y - 80,
                                100,
                                100
                            )
                            if face_rect.collidepoint(x, y) and hole.pop_progress > 0.5:
                                hole.was_tapped = True
                                hole.tap_animation = 1.0
                                char = self.characters[hole.character_index]
                                self._spawn_particles(hole.x, hole.y - 40, char.color)
                                self._play_tap_sound()
                                break

    def update(self, dt: float) -> None:
        """更新処理"""
        # 出現タイマー
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and self.active_count < 3:
            self._spawn_character()
            self.spawn_timer = self.SPAWN_INTERVAL

        # 各穴の更新
        for hole in self.holes:
            if hole.is_active:
                # 出現アニメーション
                if hole.pop_progress < 1.0:
                    hole.pop_progress += self.POP_SPEED * dt
                    hole.pop_progress = min(hole.pop_progress, 1.0)

                # タップアニメーション
                if hole.was_tapped:
                    hole.tap_animation -= dt * 3
                    if hole.tap_animation <= 0:
                        # 引っ込む
                        hole.is_active = False
                        self.active_count -= 1
                else:
                    # 表示タイマー
                    hole.show_timer -= dt
                    if hole.show_timer <= 0:
                        # 時間切れで引っ込む
                        hole.pop_progress -= self.POP_SPEED * 0.5 * dt
                        if hole.pop_progress <= 0:
                            hole.is_active = False
                            self.active_count -= 1

        # パーティクル更新
        for particle in self.particles[:]:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vy"] += 300 * dt  # 重力
            particle["life"] -= dt
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def draw(self) -> None:
        """描画処理"""
        # 背景（草原）
        self.screen.fill((150, 200, 100))

        # 背景のグラデーション効果
        for i in range(0, self.height, 20):
            alpha = 50 - (i / self.height) * 50
            color = (int(130 + alpha), int(180 + alpha), int(80 + alpha))
            pygame.draw.rect(self.screen, color, (0, i, self.width, 20))

        # タイトル
        title_text = self.title_font.render("もぐらたたき", True, (60, 80, 40))
        title_rect = title_text.get_rect(centerx=self.width // 2, top=20)

        # タイトル背景
        bg_rect = title_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (255, 255, 255, 180), bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 150, 80), bg_rect, 3, border_radius=15)
        self.screen.blit(title_text, title_rect)

        # 穴とキャラクター
        for hole in self.holes:
            self._draw_hole(self.screen, hole)

        # パーティクル
        for particle in self.particles:
            alpha = int(255 * (particle["life"] / 0.5))
            size = int(particle["size"] * (particle["life"] / 0.5))
            if size > 0:
                pygame.draw.circle(
                    self.screen,
                    particle["color"],
                    (int(particle["x"]), int(particle["y"])),
                    size
                )

        # ヒント
        hint_text = self.hint_font.render("どうぶつをタッチしよう！", True, (80, 100, 60))
        hint_rect = hint_text.get_rect(centerx=self.width // 2, bottom=self.height - 30)
        self.screen.blit(hint_text, hint_rect)

        # 戻るボタン
        self.back_button.draw(self.screen)
