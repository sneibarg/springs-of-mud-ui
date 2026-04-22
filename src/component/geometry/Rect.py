from dataclasses import dataclass
from component.geometry.Shape import Shape, Drawable


@dataclass
class Rect(Shape, Drawable):
    x: int
    y: int
    w: int
    h: int

    def bounds(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    def contains(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h

    def fill(self, ctx, col: int) -> None:
        ctx.gfx.rect(self.x, self.y, self.w, self.h, col)

    def border(self, ctx, col: int) -> None:
        ctx.gfx.rectb(self.x, self.y, self.w, self.h, col)
