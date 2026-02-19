from __future__ import annotations
from dataclasses import dataclass

from component.geometry.Shape import Shape, Drawable

@dataclass(frozen=True)
class Triangle(Shape, Drawable):
    x1: int
    y1: int
    x2: int
    y2: int
    x3: int
    y3: int

    def fill(self, ctx, col: int) -> None:
        ctx.gfx.tri(self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, col)

    def border(self, ctx, col: int) -> None:
        ctx.gfx.trib(self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, col)

    def bounds(self) -> tuple[int, int, int, int]:
        x0 = min(self.x1, self.x2, self.x3)
        y0 = min(self.y1, self.y2, self.y3)
        x1 = max(self.x1, self.x2, self.x3)
        y1 = max(self.y1, self.y2, self.y3)
        return x0, y0, (x1 - x0), (y1 - y0)

    def contains(self, mx: int, my: int) -> bool:
        def sign(px, py, ax, ay, bx, by) -> int:
            return (px - bx) * (ay - by) - (ax - bx) * (py - by)

        b1 = sign(mx, my, self.x1, self.y1, self.x2, self.y2) < 0
        b2 = sign(mx, my, self.x2, self.y2, self.x3, self.y3) < 0
        b3 = sign(mx, my, self.x3, self.y3, self.x1, self.y1) < 0
        return (b1 == b2) and (b2 == b3)
