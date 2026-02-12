from dataclasses import dataclass


@dataclass
class Layout:
    game_w: int = 256
    game_h: int = 192
    ui_w: int = 160
    h: int = 192
    gutter: int = 1  # separator line thickness

    @property
    def w(self) -> int:
        return self.game_w + self.gutter + self.ui_w

    @property
    def game_x(self) -> int:
        return 0

    @property
    def ui_x(self) -> int:
        return self.game_w + self.gutter