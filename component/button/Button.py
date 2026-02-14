from typing import Callable
from component.geometry.Rect import Rect

import pyxel


class Button:
    def __init__(self, rect: Rect, text: str, base_col: int, hover_col: int, on_click: Callable[[], None]):
        self.rect = rect
        self.text = text
        self.base_col = base_col
        self.hover_col = hover_col
        self.on_click = on_click
        self.hover = False
        self._text_pad_x = 6
        self._text_pad_y = 5

    def update(self, mx: int, my: int, click: bool) -> None:
        self.hover = self.rect.contains(mx, my)
        if click and self.hover:
            self.on_click()

    def draw(self) -> None:
        self._draw_background()
        self._draw_border()
        self._draw_label()

    def _draw_background(self) -> None:
        col = self.hover_col if self.hover else self.base_col
        self.rect.fill(col)

    def _draw_border(self) -> None:
        self.rect.border(7)

    def _draw_label(self) -> None:
        tx = self.rect.x + self._text_pad_x
        ty = self.rect.y + self._text_pad_y
        pyxel.text(tx, ty, self.text, 7)
