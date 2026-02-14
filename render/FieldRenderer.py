from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from component.geometry.Rect import Rect

import pyxel


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
    char_w: int = 4         # pyxel.text "cell" width
    blink_div: int = 20


class FieldRenderer:
    """
    Centralizes ALL Pyxel drawing for field-like components.
    Components should compute state; renderer draws it.
    """

    def __init__(self, style: FieldStyle | None = None):
        self.s = style or FieldStyle()

    def text_width_px(self, text: str) -> int:
        return len(text) * self.s.char_w

    def max_chars_in_px(self, px: int) -> int:
        return max(1, px // self.s.char_w)

    @staticmethod
    def clip_right(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[-max_chars:]

    def blink_on(self) -> bool:
        return (pyxel.frame_count // self.s.blink_div) % 2 == 0

    def draw_label(self, rect: Rect, label: str) -> None:
        pyxel.text(rect.x, rect.y - self.s.label_gap, label, self.s.text_col)

    def draw_field_box(self, rect: Rect, *, active: bool = False, open_: bool = False) -> None:
        rect.fill(self.s.bg_col)
        col = self.s.border_col
        if open_:
            col = self.s.border_open_col
        elif active:
            col = self.s.border_active_col
        rect.border(col)

    def draw_field_text(self, rect: Rect, text: str) -> None:
        pyxel.text(rect.x + self.s.pad_x, rect.y + self.s.text_y, text, self.s.text_col)

    def draw_caret(self, rect: Rect, caret_x_px: int) -> None:
        if not self.blink_on():
            return
        caret = Rect(caret_x_px, rect.y + self.s.caret_y, self.s.caret_w, self.s.caret_h)
        caret.fill(self.s.caret_col)

    def draw_selection(self, rect: Rect, sel_x_px: int, sel_w_px: int) -> None:
        if sel_w_px <= 0:
            return
        r = Rect(sel_x_px, rect.y + self.s.text_y, sel_w_px, self.s.caret_h)
        r.fill(self.s.selection_col)

    def draw_text_field(self, rect: Rect, *, label: Optional[str], text: str, active: bool, cursor_pos: int) -> None:
        if label:
            self.draw_label(rect, label)
        self.draw_field_box(rect, active=active)

        max_chars = self.max_chars_in_px(rect.w - (self.s.pad_x * 2))
        visible = self.clip_right(text, max_chars)
        self.draw_field_text(rect, visible)

        if active:
            visible_start = max(0, len(text) - max_chars)
            c = max(0, min(cursor_pos, len(text)) - visible_start)
            caret_x = rect.x + self.s.pad_x + c * self.s.char_w
            if caret_x < rect.x + rect.w - 2:
                self.draw_caret(rect, caret_x)

    def draw_dropdown_field(self, rect: Rect, *, label: Optional[str], value: str, open_: bool) -> None:
        if label:
            self.draw_label(rect, label)
        self.draw_field_box(rect, open_=open_)
        self.draw_field_text(rect, value)

        arrow = "^" if open_ else "v"
        pyxel.text(rect.x + rect.w - 8, rect.y + self.s.text_y, arrow, self.s.text_col)

    def draw_dropdown_popup(self, popup_rect: Rect, *, options: list[str], selected: str, row_h: int, outer_col: int = 1,
                            row_col: int = 2, row_sel_col: int = 3, border_col: int = 7) -> None:
        Rect(popup_rect.x - 1, popup_rect.y - 1, popup_rect.w + 2, popup_rect.h + 2).fill(outer_col)
        for i, opt in enumerate(options):
            r = Rect(popup_rect.x, popup_rect.y + i * row_h, popup_rect.w, row_h)
            r.fill(row_sel_col if opt == selected else row_col)
            r.border(border_col)
            pyxel.text(r.x + self.s.pad_x, r.y + self.s.text_y, str(opt), self.s.text_col)

    def draw_button(self, rect: Rect, text: str, *, hover: bool, base_col: int, hover_col: int, border_col: int = 7) -> None:
        rect.fill(hover_col if hover else base_col)
        rect.border(border_col)
        pyxel.text(rect.x + 6, rect.y + 5, text, self.s.text_col)


default_field_renderer = FieldRenderer()
