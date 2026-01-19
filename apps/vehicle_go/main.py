"""
Vehicle Go - 単体実行用エントリーポイント

開発・デバッグ時に使用:
    python apps/vehicle_go/main.py
"""

import pygame

from apps.vehicle_go.game import VehicleGoGame
from shared.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH


def main() -> None:
    """ゲームを単体で起動"""
    pygame.init()

    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    pygame.display.set_caption("Vehicle Go - のりものビュンビュン")

    game = VehicleGoGame(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
