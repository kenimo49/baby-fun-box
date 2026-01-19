"""
BalloonPopGame - 風船をタップして弾けさせる幼児向けゲーム

BaseGameを継承し、ランチャーから呼び出せる形式で実装。
"""

import array
import math
import random
from dataclasses import dataclass, field

import pygame

from shared.base_game import BaseGame
from shared.components import BackButton
from shared.constants import BABY_COLORS, BACKGROUND_LIGHT


@dataclass
class Particle:
    """弾けたときに飛び散るパーティクル"""

    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    radius: float
    life: float = 1.0
    decay: float = 0.02

    def update(self) -> bool:
        """パーティクルを更新。生存中ならTrue、消滅ならFalse"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # 重力
        self.life -= self.decay
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        """パーティクルを描画"""
        alpha = int(255 * self.life)
        radius = int(self.radius * self.life)
        if radius > 0:
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surface,
                (*self.color, alpha),
                (radius, radius),
                radius,
            )
            screen.blit(surface, (int(self.x - radius), int(self.y - radius)))


@dataclass
class Balloon:
    """風船オブジェクト"""

    x: float
    y: float
    radius: float
    color: tuple[int, int, int]
    speed: float = 1.0
    wobble_offset: float = field(default_factory=lambda: random.uniform(0, math.pi * 2))
    wobble_speed: float = field(default_factory=lambda: random.uniform(0.02, 0.05))
    time: float = 0.0

    def update(self, screen_height: int) -> bool:
        """風船を更新。画面内ならTrue、画面外ならFalse"""
        self.y -= self.speed
        self.time += self.wobble_speed
        self.x += math.sin(self.time + self.wobble_offset) * 0.5
        return self.y + self.radius > -50

    def draw(self, screen: pygame.Surface) -> None:
        """風船を描画"""
        x, y = int(self.x), int(self.y)
        r = int(self.radius)

        pygame.draw.circle(screen, self.color, (x, y), r)

        highlight_color = tuple(min(c + 60, 255) for c in self.color)
        highlight_pos = (x - r // 3, y - r // 3)
        pygame.draw.circle(screen, highlight_color, highlight_pos, r // 4)  # type: ignore

        string_start = (x, y + r)
        string_end = (x + math.sin(self.time) * 5, y + r + 30)
        pygame.draw.line(screen, (150, 150, 150), string_start, string_end, 2)  # type: ignore

    def contains_point(self, px: int, py: int) -> bool:
        """指定した点が風船内にあるか判定"""
        distance = math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)
        return distance <= self.radius


class BalloonPopGame(BaseGame):
    """風船をタップして弾けさせるゲーム"""

    # ゲーム情報
    name = "Balloon Pop"
    description = "風船をタップして弾けさせよう！"
    icon_path = "assets/icon.png"

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        self.balloons: list[Balloon] = []
        self.particles: list[Particle] = []

        self.spawn_timer = 0.0
        self.spawn_interval = 1.5

        self.pop_sound: pygame.mixer.Sound | None = None

        # 戻るボタン
        self.back_button = BackButton(
            x=20,
            y=20,
            on_click=self.request_return_to_launcher,
        )

    def on_enter(self) -> None:
        """ゲーム開始時の初期化"""
        # ミキサーの初期化（まだの場合）
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 効果音を生成
        self.pop_sound = self._create_pop_sound()

        # 初期風船を生成
        self.balloons.clear()
        self.particles.clear()
        for _ in range(3):
            self._spawn_balloon()

    def on_exit(self) -> None:
        """ゲーム終了時のクリーンアップ"""
        self.balloons.clear()
        self.particles.clear()

    def _create_pop_sound(self) -> pygame.mixer.Sound:
        """ポップ音を生成"""
        sample_rate = 22050
        duration = 0.1
        samples = int(sample_rate * duration)

        sound_array = array.array("h")
        for i in range(samples):
            t = i / sample_rate
            amplitude = int(32767 * math.exp(-t * 30) * math.sin(2 * math.pi * 400 * t))
            sound_array.append(amplitude)

        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(0.3)
        return sound

    def _spawn_balloon(self) -> None:
        """新しい風船を生成"""
        radius = random.uniform(60, 100)
        x = random.uniform(radius, self.width - radius)
        y = self.height + radius
        color = random.choice(BABY_COLORS)
        speed = random.uniform(0.8, 1.5)

        self.balloons.append(Balloon(x=x, y=y, radius=radius, color=color, speed=speed))

    def _pop_balloon(self, balloon: Balloon) -> None:
        """風船を弾けさせる"""
        if self.pop_sound:
            self.pop_sound.play()

        num_particles = random.randint(15, 25)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            particle = Particle(
                x=balloon.x,
                y=balloon.y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,
                color=balloon.color,
                radius=random.uniform(5, 15),
                decay=random.uniform(0.015, 0.03),
            )
            self.particles.append(particle)

        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self.particles.append(
                Particle(
                    x=balloon.x,
                    y=balloon.y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed - 3,
                    color=(255, 255, 100),
                    radius=random.uniform(8, 12),
                    decay=random.uniform(0.02, 0.04),
                )
            )

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """イベント処理"""
        for event in events:
            # 戻るボタンの処理
            if self.back_button.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.request_return_to_launcher()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for balloon in self.balloons[:]:
                    if balloon.contains_point(mouse_x, mouse_y):
                        self._pop_balloon(balloon)
                        self.balloons.remove(balloon)
                        break

    def update(self, dt: float) -> None:
        """ゲーム状態の更新"""
        self.balloons = [b for b in self.balloons if b.update(self.height)]
        self.particles = [p for p in self.particles if p.update()]

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_balloon()

        if len(self.balloons) < 2:
            self._spawn_balloon()

    def draw(self) -> None:
        """描画処理"""
        self.screen.fill(BACKGROUND_LIGHT)

        for balloon in self.balloons:
            balloon.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        # 戻るボタンを描画
        self.back_button.draw(self.screen)
