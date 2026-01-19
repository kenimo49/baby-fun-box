"""
タッチ対応ボタンコンポーネント

1〜2歳児向けに大きなタッチターゲットを持つボタン
"""

from dataclasses import dataclass
from typing import Callable

import pygame

from shared.constants import (
    BUTTON_COLOR,
    BUTTON_HEIGHT,
    BUTTON_HOVER_COLOR,
    BUTTON_RADIUS,
    BUTTON_TEXT_COLOR,
    BUTTON_WIDTH,
    BACK_BUTTON_SIZE,
    WHITE,
)
from shared.fonts import get_font


@dataclass
class Button:
    """タッチ対応の角丸ボタン"""

    x: int
    y: int
    width: int = BUTTON_WIDTH
    height: int = BUTTON_HEIGHT
    text: str = ""
    color: tuple[int, int, int] = BUTTON_COLOR
    hover_color: tuple[int, int, int] = BUTTON_HOVER_COLOR
    text_color: tuple[int, int, int] = BUTTON_TEXT_COLOR
    radius: int = BUTTON_RADIUS
    font_size: int = 36
    on_click: Callable[[], None] | None = None

    _is_hovered: bool = False
    _is_pressed: bool = False
    _font: pygame.font.Font | None = None

    def __post_init__(self) -> None:
        """フォントの初期化"""
        self._font = get_font(self.font_size)

    @property
    def rect(self) -> pygame.Rect:
        """ボタンの矩形を取得"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def center(self) -> tuple[int, int]:
        """ボタンの中心座標を取得"""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def contains_point(self, x: int, y: int) -> bool:
        """指定した点がボタン内にあるか判定"""
        return self.rect.collidepoint(x, y)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        イベントを処理する

        Returns:
            クリックされた場合 True
        """
        if event.type == pygame.MOUSEMOTION:
            self._is_hovered = self.contains_point(*event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(*event.pos):
                self._is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self._is_pressed:
                self._is_pressed = False
                if self.contains_point(*event.pos):
                    if self.on_click:
                        self.on_click()
                    return True

        return False

    def draw(self, screen: pygame.Surface) -> None:
        """ボタンを描画"""
        # 状態に応じた色を選択
        if self._is_pressed:
            current_color = self.hover_color
        elif self._is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color

        # 角丸矩形を描画
        pygame.draw.rect(
            screen,
            current_color,
            self.rect,
            border_radius=self.radius,
        )

        # テキストを描画
        if self.text and self._font:
            text_surface = self._font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.center)
            screen.blit(text_surface, text_rect)


@dataclass
class IconButton:
    """アイコン付きの大きなボタン（ランチャー用）"""

    x: int
    y: int
    size: int = 150
    icon: pygame.Surface | None = None
    label: str = ""
    color: tuple[int, int, int] = BUTTON_COLOR
    hover_color: tuple[int, int, int] = BUTTON_HOVER_COLOR
    on_click: Callable[[], None] | None = None

    _is_hovered: bool = False
    _is_pressed: bool = False
    _font: pygame.font.Font | None = None

    def __post_init__(self) -> None:
        """フォントの初期化"""
        self._font = get_font(28)

    @property
    def rect(self) -> pygame.Rect:
        """ボタンの矩形を取得（ラベル分の高さを含む）"""
        label_height = 30 if self.label else 0
        return pygame.Rect(self.x, self.y, self.size, self.size + label_height)

    @property
    def icon_rect(self) -> pygame.Rect:
        """アイコン部分の矩形"""
        return pygame.Rect(self.x, self.y, self.size, self.size)

    @property
    def center(self) -> tuple[int, int]:
        """アイコン部分の中心座標"""
        return (self.x + self.size // 2, self.y + self.size // 2)

    def contains_point(self, x: int, y: int) -> bool:
        """指定した点がボタン内にあるか判定"""
        return self.rect.collidepoint(x, y)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベントを処理する"""
        if event.type == pygame.MOUSEMOTION:
            self._is_hovered = self.contains_point(*event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(*event.pos):
                self._is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self._is_pressed:
                self._is_pressed = False
                if self.contains_point(*event.pos):
                    if self.on_click:
                        self.on_click()
                    return True

        return False

    def draw(self, screen: pygame.Surface) -> None:
        """ボタンを描画"""
        # 状態に応じた色を選択
        if self._is_pressed:
            current_color = self.hover_color
        elif self._is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color

        # 角丸の正方形を描画
        pygame.draw.rect(
            screen,
            current_color,
            self.icon_rect,
            border_radius=20,
        )

        # アイコンまたはプレースホルダーを描画
        if self.icon:
            # アイコンをリサイズして中央に配置
            icon_size = int(self.size * 0.6)
            scaled_icon = pygame.transform.scale(self.icon, (icon_size, icon_size))
            icon_pos = (
                self.x + (self.size - icon_size) // 2,
                self.y + (self.size - icon_size) // 2,
            )
            screen.blit(scaled_icon, icon_pos)
        else:
            # アイコンがない場合はラベルの頭文字を大きく表示
            if self.label and self._font:
                big_font = get_font(72)
                initial = self.label[0].upper()
                text_surface = big_font.render(initial, True, WHITE)
                text_rect = text_surface.get_rect(center=self.center)
                screen.blit(text_surface, text_rect)

        # ラベルを描画
        if self.label and self._font:
            text_surface = self._font.render(self.label, True, (50, 50, 50))
            text_rect = text_surface.get_rect(
                centerx=self.x + self.size // 2,
                top=self.y + self.size + 5,
            )
            screen.blit(text_surface, text_rect)


@dataclass
class BackButton:
    """戻るボタン（ホームアイコン）"""

    x: int = 20
    y: int = 20
    size: int = BACK_BUTTON_SIZE
    color: tuple[int, int, int] = (100, 100, 100)
    hover_color: tuple[int, int, int] = (70, 70, 70)
    on_click: Callable[[], None] | None = None

    _is_hovered: bool = False
    _is_pressed: bool = False

    @property
    def rect(self) -> pygame.Rect:
        """ボタンの矩形"""
        return pygame.Rect(self.x, self.y, self.size, self.size)

    @property
    def center(self) -> tuple[int, int]:
        """中心座標"""
        return (self.x + self.size // 2, self.y + self.size // 2)

    def contains_point(self, x: int, y: int) -> bool:
        """指定した点がボタン内にあるか判定"""
        return self.rect.collidepoint(x, y)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベントを処理する"""
        if event.type == pygame.MOUSEMOTION:
            self._is_hovered = self.contains_point(*event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(*event.pos):
                self._is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self._is_pressed:
                self._is_pressed = False
                if self.contains_point(*event.pos):
                    if self.on_click:
                        self.on_click()
                    return True

        return False

    def draw(self, screen: pygame.Surface) -> None:
        """戻るボタン（家のアイコン）を描画"""
        # 状態に応じた色を選択
        if self._is_pressed or self._is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color

        cx, cy = self.center
        s = self.size

        # 家の形を描画（シンプルなアイコン）
        # 屋根（三角形）
        roof_points = [
            (cx, cy - s // 3),  # 頂点
            (cx - s // 3, cy),  # 左下
            (cx + s // 3, cy),  # 右下
        ]
        pygame.draw.polygon(screen, current_color, roof_points)

        # 本体（四角形）
        body_rect = pygame.Rect(
            cx - s // 4,
            cy,
            s // 2,
            s // 3,
        )
        pygame.draw.rect(screen, current_color, body_rect)

        # ドア（小さな四角形）
        door_rect = pygame.Rect(
            cx - s // 10,
            cy + s // 8,
            s // 5,
            s // 4,
        )
        pygame.draw.rect(screen, WHITE, door_rect)
