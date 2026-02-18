from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CursorStyle:
    outline_col: int = 0
    main_col: int = 7
    fill_col: int = 10


class CursorRenderer:
    def __init__(self, style: CursorStyle | None = None):
        self.s = style or CursorStyle()

    def draw(self, ctx, mx: Optional[int] = None, my: Optional[int] = None) -> None:
        x = ctx.input.mx if mx is None else mx
        y = ctx.input.my if my is None else my

        self._draw_outline(ctx, x, y)
        self._draw_main(ctx, x, y)
        self._draw_fill(ctx, x, y)

    def _draw_outline(self, ctx, mx: int, my: int) -> None:
        g = ctx.gfx
        c = self.s.outline_col
        g.line(mx - 1, my, mx - 1, my + 9, c)
        g.line(mx + 1, my, mx + 1, my + 9, c)
        g.line(mx, my - 1, mx + 6, my + 5, c)
        g.line(mx, my + 1, mx + 6, my + 7, c)
        g.line(mx, my + 9, mx + 4, my + 7, c)

    def _draw_main(self, ctx, mx: int, my: int) -> None:
        g = ctx.gfx
        c = self.s.main_col
        g.rect(mx - 1, my, 3, 9, c)
        g.line(mx, my, mx, my + 8, c)
        g.line(mx, my, mx + 5, my + 5, c)
        g.line(mx, my + 8, mx + 3, my + 6, c)

    def _draw_fill(self, ctx, mx: int, my: int) -> None:
        g = ctx.gfx
        c = self.s.fill_col
        g.line(mx + 1, my + 3, mx + 3, my + 5, c)
        g.line(mx + 1, my + 4, mx + 2, my + 5, c)
