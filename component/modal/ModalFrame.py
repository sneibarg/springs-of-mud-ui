from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from component.geometry.Rect import Rect
from component.render.TextField import TextField


@dataclass(frozen=True)
class ModalTheme:
    overlay_step: int = 2
    overlay_col: int = 0
    panel_fill: int = 1
    panel_border: int = 5
    title_fill: int = 5
    title_col: int = 7
    close_fill: int = 8
    close_col: int = 7


class ModalFrame:
    def __init__(
        self,
        panel: Rect,
        title: str,
        *,
        theme: Optional[ModalTheme] = None,
        text: Optional[TextField] = None,
    ):
        self.panel = panel
        self.title = title
        self.t = theme or ModalTheme()
        self.tf = text or TextField()

    @property
    def title_bar(self) -> Rect:
        return Rect(self.panel.x, self.panel.y, self.panel.w, 20)

    @property
    def close_rect(self) -> Rect:
        return Rect(self.panel.x + self.panel.w - 15, self.panel.y + 5, 10, 10)

    def did_close(self, mx: int, my: int, click: bool) -> bool:
        return click and self.close_rect.contains(mx, my)

    def draw(self, ctx) -> None:
        self._draw_overlay(ctx)

        self.panel.fill(ctx, self.t.panel_fill)
        self.panel.border(ctx, self.t.panel_border)

        tb = self.title_bar
        tb.fill(ctx, self.t.title_fill)
        self.tf.draw_text(ctx, x=tb.x + 10, y=tb.y + 7, text=self.title, col=self.t.title_col)

        c = self.close_rect
        c.fill(ctx, self.t.close_fill)
        self.tf.draw_text(ctx, x=c.x + 2, y=c.y + 2, text="X", col=self.t.close_col)

    def _draw_overlay(self, ctx) -> None:
        step = self.t.overlay_step
        w = ctx.layout.w
        h = ctx.layout.h
        for y in range(0, h, step):
            for x in range(0, w, step):
                ctx.gfx.pset(x, y, self.t.overlay_col)
