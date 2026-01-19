"""
Animal Touch - 単体実行用エントリーポイント

開発・デバッグ時に単体でゲームを実行するためのスクリプト。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加（単体実行時用）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pygame

from shared.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH


def main() -> None:
    """単体実行用エントリーポイント"""
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    pygame.display.set_caption("Animal Touch - どうぶつタッチ")

    from apps.animal_touch.game import AnimalTouchGame

    game = AnimalTouchGame(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
