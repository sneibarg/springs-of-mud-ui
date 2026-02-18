from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def draw(self, ctx, col: int) -> None:
        ctx.gfx.pset(self.x, self.y, col)

    def contains(self, mx: int, my: int) -> bool:
        return self.x == mx and self.y == my
