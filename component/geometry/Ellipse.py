from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Ellipse:
    x: int
    y: int
    rx: int
    ry: int

    def fill(self, ctx, col: int) -> None:
        ctx.gfx.elli(self.x, self.y, self.rx, self.ry, col)

    def border(self, ctx, col: int) -> None:
        ctx.gfx.ellib(self.x, self.y, self.rx, self.ry, col)

    def bounds(self) -> tuple[int, int, int, int]:
        return self.x - self.rx, self.y - self.ry, self.rx * 2, self.ry * 2

    def contains(self, mx: int, my: int) -> bool:
        if self.rx <= 0 or self.ry <= 0:
            return False
        dx = mx - self.x
        dy = my - self.y
        return (dx * dx) / (self.rx * self.rx) + (dy * dy) / (self.ry * self.ry) <= 1.0
