from __future__ import annotations
from typing import Callable
from component.geometry.Rect import Rect
from render.FieldRenderer import FieldRenderer, default_field_renderer


class Button:
    def __init__(
        self,
        rect: Rect,
        text: str,
        base_col: int,
        hover_col: int,
        on_click: Callable[[], None],
        renderer: FieldRenderer | None = None,
    ):
        self.rect = rect
        self.text = text
        self.base_col = base_col
        self.hover_col = hover_col
        self.on_click = on_click
        self.hover = False
        self.r = renderer or default_field_renderer

    def update(self, mx: int, my: int, click: bool) -> None:
        self.hover = self.rect.contains(mx, my)
        if click and self.hover:
            self.on_click()

    def draw(self) -> None:
        self.r.draw_button(self.rect, self.text, hover=self.hover, base_col=self.base_col, hover_col=self.hover_col)
