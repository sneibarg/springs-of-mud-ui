from dataclasses import dataclass
from typing import Optional

import pyxel


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    def contains(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h

    def fill(self, color: int) -> None:
        pyxel.rect(self.x, self.y, self.w, self.h, color)

    def border(self, color: int) -> None:
        pyxel.rectb(self.x, self.y, self.w, self.h, color)

    def draw(self, fill: Optional[int] = None, border: Optional[int] = None) -> None:
        if fill is not None:
            self.fill(fill)
        if border is not None:
            self.border(border)

    def clip_begin(self) -> None:
        pyxel.clip(self.x, self.y, self.w, self.h)

    @staticmethod
    def clip_end() -> None:
        pyxel.clip()
