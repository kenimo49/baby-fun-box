"""
BaseGame - 全ゲーム共通の基底クラス

全てのミニゲームはこのクラスを継承して実装する。
ランチャーからの統一的なゲーム起動・終了を可能にする。
"""

from abc import ABC, abstractmethod
from pathlib import Path

import pygame


class BaseGame(ABC):
    """全ゲーム共通の基底クラス"""

    # サブクラスで定義するゲーム情報
    name: str = "Game Name"
    description: str = "Game description"
    icon_path: str | None = None  # アイコン画像のパス（assets/icon.pngなど）

    def __init__(self, screen: pygame.Surface) -> None:
        """
        ゲームを初期化する

        Args:
            screen: pygameの描画サーフェス（ランチャーから渡される）
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.running = True
        self.return_to_launcher = False
        self.clock = pygame.time.Clock()

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        イベント処理

        Args:
            events: pygameイベントのリスト
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        ゲーム状態の更新

        Args:
            dt: 前フレームからの経過時間（秒）
        """
        pass

    @abstractmethod
    def draw(self) -> None:
        """描画処理"""
        pass

    def on_enter(self) -> None:
        """
        ゲーム開始時に呼ばれる（オーバーライド可能）

        リソースの読み込みや初期化処理をここで行う
        """
        pass

    def on_exit(self) -> None:
        """
        ゲーム終了時に呼ばれる（オーバーライド可能）

        リソースの解放などをここで行う
        """
        pass

    def request_return_to_launcher(self) -> None:
        """ランチャーに戻ることをリクエストする"""
        self.return_to_launcher = True

    def run(self) -> None:
        """
        ゲームループを実行する

        このメソッドはランチャーから呼ばれる。
        return_to_launcher が True になるとループを抜ける。
        """
        self.on_enter()

        while self.running and not self.return_to_launcher:
            dt = self.clock.tick(60) / 1000.0  # 60FPS、秒単位のデルタタイム
            events = pygame.event.get()

            # 共通のイベント処理
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return

            # ゲーム固有のイベント処理
            self.handle_events(events)

            # 更新と描画
            self.update(dt)
            self.draw()
            pygame.display.flip()

        self.on_exit()

    @classmethod
    def get_icon(cls) -> pygame.Surface | None:
        """
        ゲームのアイコン画像を取得する

        Returns:
            アイコンのSurface、または None
        """
        if cls.icon_path is None:
            return None

        try:
            # クラスが定義されているファイルからの相対パスとして解決
            import inspect

            class_file = inspect.getfile(cls)
            class_dir = Path(class_file).parent
            icon_full_path = class_dir / cls.icon_path

            if icon_full_path.exists():
                return pygame.image.load(str(icon_full_path))
        except Exception:
            pass

        return None
