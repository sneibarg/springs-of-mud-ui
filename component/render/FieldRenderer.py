from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from component.geometry.Rect import Rect


@dataclass(frozen=True)
class FieldStyle:
    text_col: int = 7
    bg_col: int = 0
    border_col: int = 5
    border_active_col: int = 11
    border_open_col: int = 11
    caret_col: int = 7
    selection_col: int = 12
    label_gap: int = 13     # label above field
    pad_x: int = 4
    text_y: int = 3         # inside field
    caret_y: int = 3
    caret_w: int = 3
    caret_h: int = 5
    char_w: int = 4
    blink_div: int = 20


class FieldRenderer:
    def __init__(self, style: FieldStyle | None = None):
        self.s = style or FieldStyle()

    def text_width_px(self, text: str) -> int:
        return len(text) * self.s.char_w

    def max_chars_in_px(self, px: int) -> int:
        return max(1, px // self.s.char_w)

    @staticmethod
    def clip_right(text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[-max_chars:]

    def blink_on(self, ctx) -> bool:
        return (ctx.input.frame_count // self.s.blink_div) % 2 == 0

    def draw_label(self, ctx, rect: Rect, label: str) -> None:
        ctx.gfx.text(rect.x, rect.y - self.s.label_gap, label, self.s.text_col)

    def draw_field_box(self, ctx, rect: Rect, *, active: bool = False, open_: bool = False) -> None:
        rect.fill(ctx, self.s.bg_col)
        col = self.s.border_open_col if open_ else (self.s.border_active_col if active else self.s.border_col)
        rect.border(ctx, col)

    def draw_field_text(self, ctx, rect: Rect, text: str) -> None:
        ctx.gfx.text(rect.x + self.s.pad_x, rect.y + self.s.text_y, text, self.s.text_col)

    def draw_caret(self, ctx, rect: Rect, caret_x_px: int) -> None:
        if not self.blink_on(ctx):
            return
        Rect(caret_x_px, rect.y + self.s.caret_y, self.s.caret_w, self.s.caret_h).fill(ctx, self.s.caret_col)

    def draw_selection(self, ctx, rect: Rect, sel_x_px: int, sel_w_px: int) -> None:
        if sel_w_px <= 0:
            return
        Rect(sel_x_px, rect.y + self.s.text_y, sel_w_px, self.s.caret_h).fill(ctx, self.s.selection_col)

    def draw_text_field(
        self,
        ctx,
        rect: Rect,
        *,
        label: Optional[str],
        text: str,
        active: bool,
        cursor_pos: int,
    ) -> None:
        if label:
            self.draw_label(ctx, rect, label)

        self.draw_field_box(ctx, rect, active=active)

        max_chars = self.max_chars_in_px(rect.w - (self.s.pad_x * 2))
        visible = self.clip_right(text, max_chars)
        self.draw_field_text(ctx, rect, visible)

        if not active:
            return

        visible_start = max(0, len(text) - max_chars)
        c = max(0, min(cursor_pos, len(text)) - visible_start)
        caret_x = rect.x + self.s.pad_x + c * self.s.char_w
        if caret_x < rect.x + rect.w - 2:
            self.draw_caret(ctx, rect, caret_x)

    def draw_dropdown_field(
        self,
        ctx,
        rect: Rect,
        *,
        label: Optional[str],
        value: str,
        open_: bool,
    ) -> None:
        if label:
            self.draw_label(ctx, rect, label)

        self.draw_field_box(ctx, rect, open_=open_)
        self.draw_field_text(ctx, rect, value)

        arrow = "^" if open_ else "v"
        ctx.gfx.text(rect.x + rect.w - 8, rect.y + self.s.text_y, arrow, self.s.text_col)

    def draw_dropdown_popup(
        self,
        ctx,
        popup_rect: Rect,
        *,
        options: list[str],
        selected: str,
        row_h: int,
        outer_col: int = 1,
        row_col: int = 2,
        row_sel_col: int = 3,
        border_col: int = 7,
    ) -> None:
        Rect(popup_rect.x - 1, popup_rect.y - 1, popup_rect.w + 2, popup_rect.h + 2).fill(ctx, outer_col)

        for i, opt in enumerate(options):
            r = Rect(popup_rect.x, popup_rect.y + i * row_h, popup_rect.w, row_h)
            r.fill(ctx, row_sel_col if opt == selected else row_col)
            r.border(ctx, border_col)
            ctx.gfx.text(r.x + self.s.pad_x, r.y + self.s.text_y, str(opt), self.s.text_col)

    def draw_button(
        self,
        ctx,
        rect: Rect,
        text: str,
        *,
        hover: bool,
        base_col: int,
        hover_col: int,
        border_col: int = 7,
    ) -> None:
        rect.fill(ctx, hover_col if hover else base_col)
        rect.border(ctx, border_col)
        ctx.gfx.text(rect.x + 6, rect.y + 5, text, self.s.text_col)


default_field_renderer = FieldRenderer()
