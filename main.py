"""
Baby Fun Box - 幼児向けゲームコレクション

統合アプリのエントリーポイント。
ランチャーを起動し、登録されたゲームを選択できる。
"""

import pygame

from apps.animal_touch.game import AnimalTouchGame
from apps.baby_piano.game import BabyPianoGame
from apps.balloon_pop.game import BalloonPopGame
from apps.launcher import Launcher
from shared.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH


def main() -> None:
    """メインエントリーポイント"""
    # Pygame初期化
    pygame.init()
    pygame.mixer.init()

    # 画面設定
    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    pygame.display.set_caption("Baby Fun Box")

    # ランチャーを作成
    launcher = Launcher(screen)

    # ゲームを登録
    launcher.register_game(BalloonPopGame)
    launcher.register_game(AnimalTouchGame)
    launcher.register_game(BabyPianoGame)

    # ランチャーを実行
    launcher.run()

    # 終了処理
    pygame.quit()


if __name__ == "__main__":
    main()
