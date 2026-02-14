from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from component.geometry.Rect import Rect
from component.field.TextField import TextField

import pyxel


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
    """
    Owns:
      - dim overlay
      - panel rect + border
      - title bar + title text
      - close button (Rect hit-test + draw)
    Pane just asks: did_close(mx,my,click)?
    """

    def __init__(self, panel: Rect, title: str, *, theme: Optional[ModalTheme] = None, text: Optional[TextField] = None):
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

    def draw(self) -> None:
        self._draw_overlay()
        self.panel.fill(self.t.panel_fill)
        self.panel.border(self.t.panel_border)

        tb = self.title_bar
        tb.fill(self.t.title_fill)
        self.tf.draw_text(x=tb.x + 10, y=tb.y + 7, text=self.title, col=self.t.title_col)

        c = self.close_rect
        c.fill(self.t.close_fill)
        self.tf.draw_text(x=c.x + 2, y=c.y + 2, text="X", col=self.t.close_col)

    def _draw_overlay(self) -> None:
        # classic dotted overlay
        step = self.t.overlay_step
        for y in range(0, pyxel.height, step):
            for x in range(0, pyxel.width, step):
                pyxel.pset(x, y, self.t.overlay_col)
