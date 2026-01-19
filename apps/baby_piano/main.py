"""
Baby Piano - 単体実行用エントリーポイント

開発・デバッグ時に使用:
    python apps/baby_piano/main.py
"""

import pygame

from apps.baby_piano.game import BabyPianoGame
from shared.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH


def main() -> None:
    """ゲームを単体で起動"""
    pygame.init()

    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    pygame.display.set_caption("Baby Piano")

    game = BabyPianoGame(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
