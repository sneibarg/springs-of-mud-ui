from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from component.geometry.Rect import Rect
from component.render.TextField import TextField


@dataclass(frozen=True)
class ListBoxStyle:
    bg_col: int = 0
    border_col: int = 5
    header_col: int = 7
    header_y_pad: int = 3
    text_col: int = 7
    row_hover_col: int = 2
    row_selected_col: int = 5
    text_x_pad: int = 3
    text_y_pad: int = 2


class ListBox:
    def __init__(
        self,
        box_rect: Rect,
        items_rect: Rect,
        *,
        header: str = "",
        row_h: int = 12,
        text: Optional[TextField] = None,
        style: Optional[ListBoxStyle] = None,
    ):
        self.box = box_rect
        self.items = items_rect
        self.header = header
        self.row_h = row_h
        self.tf = text or TextField()
        self.s = style or ListBoxStyle()
        self.hovered_idx: Optional[int] = None

    def update_hover(self, ctx, item_count: int) -> None:
        mx, my = ctx.input.mx, ctx.input.my
        self.hovered_idx = None

        if item_count <= 0:
            return
        if not self.items.contains(mx, my):
            return

        idx = (my - self.items.y) // self.row_h
        if 0 <= idx < item_count and self._row_visible(idx):
            self.hovered_idx = idx

    def click_index(self, ctx, item_count: int) -> Optional[int]:
        if not ctx.input.click:
            return None

        mx, my = ctx.input.mx, ctx.input.my
        if item_count <= 0:
            return None
        if not self.items.contains(mx, my):
            return None

        idx = (my - self.items.y) // self.row_h
        if 0 <= idx < item_count and self._row_visible(idx):
            return idx
        return None

    def _row_visible(self, idx: int) -> bool:
        """Prevent clicks/hover beyond the visible area inside the box."""
        y = self.items.y + idx * self.row_h
        return (y + self.row_h) <= (self.box.y + self.box.h - 1)

    def draw(self, ctx, *, items: Sequence[str], selected_idx: Optional[int] = None) -> None:
        self.box.fill(ctx, self.s.bg_col)
        self.box.border(ctx, self.s.border_col)
        if self.header:
            self.tf.draw_text(ctx,
                x=self.box.x + self.s.text_x_pad,
                y=self.box.y + self.s.header_y_pad,
                text=self.header,
                col=self.s.header_col,
            )

        max_chars = max(1, (self.items.w - (self.s.text_x_pad * 2)) // self.tf.s.char_w)

        y = self.items.y
        for idx, label in enumerate(items):
            if y + self.row_h > self.box.y + self.box.h - 1:
                break

            row = Rect(self.items.x + 1, y, self.items.w - 2, self.row_h - 1)
            if selected_idx is not None and idx == selected_idx:
                row.fill(ctx, self.s.row_selected_col)
            elif self.hovered_idx is not None and idx == self.hovered_idx:
                row.fill(ctx, self.s.row_hover_col)

            txt = self._clip(label, max_chars)
            self.tf.draw_text(ctx, x=self.items.x + self.s.text_x_pad, y=y + self.s.text_y_pad, text=txt, col=self.s.text_col)
            y += self.row_h

    def _clip(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        if max_chars <= 2:
            return text[:max_chars]
        return text[: max_chars - 2] + ".."
