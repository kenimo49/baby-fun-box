"""
Launcher - ゲーム選択画面

登録されたゲームをアイコンで表示し、タップで起動できるランチャー。
1〜2歳児向けに大きなタッチターゲットを採用。
"""

from typing import Type

import pygame

from shared.base_game import BaseGame
from shared.components import IconButton
from shared.constants import (
    BABY_BLUE,
    BABY_GREEN,
    BABY_ORANGE,
    BABY_PINK,
    BABY_PURPLE,
    BABY_RED,
    BABY_YELLOW,
    BACKGROUND_CREAM,
    ICON_SIZE,
    WHITE,
)
from shared.fonts import get_font


# ゲームアイコンに使う色のリスト
ICON_COLORS = [
    BABY_RED,
    BABY_YELLOW,
    BABY_GREEN,
    BABY_BLUE,
    BABY_PURPLE,
    BABY_ORANGE,
    BABY_PINK,
]


class Launcher:
    """ゲーム選択画面"""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.clock = pygame.time.Clock()
        self.running = True

        # 登録されたゲームクラスのリスト
        self.games: list[Type[BaseGame]] = []
        self.game_buttons: list[IconButton] = []

        # 現在実行中のゲーム
        self.current_game: BaseGame | None = None

        # フォント（日本語対応）
        self.title_font = get_font(72)
        self.subtitle_font = get_font(36)

    def register_game(self, game_class: Type[BaseGame]) -> None:
        """ゲームを登録する"""
        self.games.append(game_class)
        self._update_buttons()

    def _update_buttons(self) -> None:
        """ボタンの配置を更新する"""
        self.game_buttons.clear()

        num_games = len(self.games)
        if num_games == 0:
            return

        # グリッドレイアウトの計算
        cols = min(num_games, 4)  # 最大4列
        rows = (num_games + cols - 1) // cols

        # ボタン間のスペース
        spacing = 40
        button_size = ICON_SIZE
        label_height = 30

        # グリッド全体のサイズ
        grid_width = cols * button_size + (cols - 1) * spacing
        grid_height = rows * (button_size + label_height) + (rows - 1) * spacing

        # グリッドの開始位置（中央揃え、少し下にオフセット）
        start_x = (self.width - grid_width) // 2
        start_y = (self.height - grid_height) // 2 + 50

        for i, game_class in enumerate(self.games):
            row = i // cols
            col = i % cols

            x = start_x + col * (button_size + spacing)
            y = start_y + row * (button_size + label_height + spacing)

            # ゲームのアイコンを取得（なければ色で代用）
            icon = game_class.get_icon()
            color = ICON_COLORS[i % len(ICON_COLORS)]

            # クロージャで正しいインデックスをキャプチャ
            def make_callback(game_cls: Type[BaseGame]) -> callable:
                return lambda: self._launch_game(game_cls)

            button = IconButton(
                x=x,
                y=y,
                size=button_size,
                icon=icon,
                label=game_class.name,
                color=color,
                hover_color=tuple(max(c - 30, 0) for c in color),  # type: ignore
                on_click=make_callback(game_class),
            )
            self.game_buttons.append(button)

    def _launch_game(self, game_class: Type[BaseGame]) -> None:
        """ゲームを起動する"""
        self.current_game = game_class(self.screen)

    def handle_events(self) -> None:
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

            # ボタンのイベント処理
            for button in self.game_buttons:
                button.handle_event(event)

    def update(self) -> None:
        """更新処理"""
        pass  # 現在は特に更新処理なし

    def draw(self) -> None:
        """描画処理"""
        self.screen.fill(BACKGROUND_CREAM)

        # タイトル
        title_text = self.title_font.render("Baby Fun Box", True, (80, 80, 80))
        title_rect = title_text.get_rect(centerx=self.width // 2, top=30)
        self.screen.blit(title_text, title_rect)

        # サブタイトル
        subtitle_text = self.subtitle_font.render(
            "Choose a game!", True, (120, 120, 120)
        )
        subtitle_rect = subtitle_text.get_rect(centerx=self.width // 2, top=100)
        self.screen.blit(subtitle_text, subtitle_rect)

        # ゲームボタンを描画
        for button in self.game_buttons:
            button.draw(self.screen)

        # ゲームがない場合のメッセージ
        if len(self.games) == 0:
            no_games_text = self.subtitle_font.render(
                "No games available", True, (150, 150, 150)
            )
            no_games_rect = no_games_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(no_games_text, no_games_rect)

        pygame.display.flip()

    def run(self) -> None:
        """メインループ"""
        while self.running:
            # ゲームが起動されていたら実行
            if self.current_game is not None:
                self.current_game.run()

                # ゲームが終了したらランチャーに戻る
                if self.current_game.return_to_launcher:
                    self.current_game = None
                elif not self.current_game.running:
                    # ゲームが完全に終了した場合はランチャーも終了
                    self.running = False
                    break
                else:
                    self.current_game = None

                continue

            # ランチャーの処理
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
