from __future__ import annotations
from dataclasses import dataclass

from component.geometry.Shape import Shape, Drawable

@dataclass(frozen=True)
class Line(Shape, Drawable):
    x1: int
    y1: int
    x2: int
    y2: int

    def draw(self, ctx, col: int) -> None:
        ctx.gfx.line(self.x1, self.y1, self.x2, self.y2, col)

    def bounds(self) -> tuple[int, int, int, int]:
        x0 = min(self.x1, self.x2)
        y0 = min(self.y1, self.y2)
        x1 = max(self.x1, self.x2)
        y1 = max(self.y1, self.y2)
        return x0, y0, (x1 - x0), (y1 - y0)

    def contains(self, mx: int, my: int, tol: float = 0.75) -> bool:
        ax, ay, bx, by = self.x1, self.y1, self.x2, self.y2
        px, py = mx, my
        abx, aby = bx - ax, by - ay
        apx, apy = px - ax, py - ay
        denom = (abx * abx + aby * aby)
        if denom == 0:
            return (ax == px and ay == py)

        t = (apx * abx + apy * aby) / denom
        t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
        cx = ax + t * abx
        cy = ay + t * aby
        dx = px - cx
        dy = py - cy
        return (dx * dx + dy * dy) <= (tol * tol)
