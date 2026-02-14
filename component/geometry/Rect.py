from __future__ import annotations
from dataclasses import dataclass

import pyxel


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def contains(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h

    def inset(self, dx: int, dy: int) -> Rect:
        return Rect(self.x + dx, self.y + dy, max(0, self.w - 2 * dx), max(0, self.h - 2 * dy))

    def fill(self, col: int) -> None:
        pyxel.rect(self.x, self.y, self.w, self.h, col)

    def border(self, col: int) -> None:
        pyxel.rectb(self.x, self.y, self.w, self.h, col)

    def clip_begin(self) -> None:
        pyxel.clip(self.x, self.y, self.w, self.h)

    @staticmethod
    def clip_end() -> None:
        pyxel.clip()
