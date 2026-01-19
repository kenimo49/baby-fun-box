"""
Balloon Pop - 単体実行用エントリーポイント

開発・デバッグ時に単体でゲームを実行するためのスクリプト。
統合アプリからはランチャー経由で game.py の BalloonPopGame が呼ばれる。
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
    pygame.display.set_caption("Balloon Pop - バルーンポップ")

    # ここでインポート（パス設定後）
    from apps.balloon_pop.game import BalloonPopGame

    game = BalloonPopGame(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
