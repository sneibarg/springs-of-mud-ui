from __future__ import annotations

from typing import Callable, Optional

from component.geometry.Rect import Rect
from component.render.FieldRenderer import FieldRenderer, default_field_renderer


class Button:
    """
    Pattern:
      - update(ctx)
      - draw(ctx)

    Button owns hit-test + click behavior.
    Rendering is delegated to FieldRenderer (component.render), which can use ctx.gfx.
    """

    def __init__(
        self,
        rect: Rect,
        text: str,
        base_col: int,
        hover_col: int,
        on_click: Callable[[], None],
        *,
        renderer: Optional[FieldRenderer] = None,
        border_col: int = 7,
    ):
        self.rect = rect
        self.text = text
        self.base_col = base_col
        self.hover_col = hover_col
        self.border_col = border_col
        self.on_click = on_click
        self.hover = False
        self.r = renderer or default_field_renderer

    def update(self, ctx) -> None:
        mx, my, click = ctx.input.mx, ctx.input.my, ctx.input.click
        self.hover = self.rect.contains(mx, my)
        if click and self.hover:
            self.on_click()

    def draw(self, ctx) -> None:
        self.r.draw_button(
            ctx,
            self.rect,
            self.text,
            hover=self.hover,
            base_col=self.base_col,
            hover_col=self.hover_col,
            border_col=self.border_col,
        )
