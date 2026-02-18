from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Circle:
    x: int
    y: int
    r: int

    def fill(self, ctx, col: int) -> None:
        ctx.gfx.circ(self.x, self.y, self.r, col)

    def border(self, ctx, col: int) -> None:
        ctx.gfx.circb(self.x, self.y, self.r, col)

    def contains(self, mx: int, my: int) -> bool:
        dx = mx - self.x
        dy = my - self.y
        return (dx * dx + dy * dy) <= (self.r * self.r)

    def bounds(self) -> tuple[int, int, int, int]:
        return self.x - self.r, self.y - self.r, self.r * 2, self.r * 2
