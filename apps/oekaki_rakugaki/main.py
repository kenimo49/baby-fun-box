"""
Oekaki Rakugaki - 単体実行用エントリーポイント

開発・デバッグ時に使用:
    python apps/oekaki_rakugaki/main.py
"""

import pygame

from apps.oekaki_rakugaki.game import OekakiRakugakiGame
from shared.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH


def main() -> None:
    """ゲームを単体で起動"""
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    pygame.display.set_caption("おえかきらくがき")

    game = OekakiRakugakiGame(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
