from __future__ import annotations
from dataclasses import dataclass

from component.geometry.Shape import Shape, Drawable

@dataclass(frozen=True)
class Point(Shape, Drawable):
    x: int
    y: int

    def draw(self, ctx, col: int) -> None:
        ctx.gfx.pset(self.x, self.y, col)

    def contains(self, mx: int, my: int) -> bool:
        return self.x == mx and self.y == my
