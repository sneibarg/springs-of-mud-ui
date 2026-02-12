from typing import Callable
from component.Rect import Rect

import pyxel


class Button:
    def __init__(self, rect: Rect, text: str, base_col: int, hover_col: int, on_click: Callable[[], None]):
        self.rect = rect
        self.text = text
        self.base_col = base_col
        self.hover_col = hover_col
        self.on_click = on_click
        self.hover = False

    def update(self, mx: int, my: int, click: bool) -> None:
        self.hover = self.rect.contains(mx, my)
        if click and self.hover:
            self.on_click()

    def draw(self) -> None:
        col = self.hover_col if self.hover else self.base_col
        pyxel.rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h, col)
        pyxel.rectb(self.rect.x, self.rect.y, self.rect.w, self.rect.h, 7)
        # crude centering
        tx = self.rect.x + 6
        ty = self.rect.y + 5
        pyxel.text(tx, ty, self.text, 7)