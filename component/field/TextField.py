from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence
from component.geometry.Rect import Rect

import pyxel


@dataclass(frozen=True)
class TextStyle:
    col: int = 7
    char_w: int = 4          # Pyxel font width in pixels
    char_h: int = 6          # Roughly; mostly used for caret/selection heights
    scale: int = 1           # "Bold-ish" pixel scale (draw multiple times)


class TextField:
    """
    Centralizes pyxel.text usage.

    - draw_text: draw a single string
    - draw_lines: draw multiple lines (optionally scaled)
    - draw_input: prompt + visible text + selection + caret inside an clipboard rect
    """

    def __init__(self, style: TextStyle | None = None):
        self.s = style or TextStyle()

    def draw_text(self, *, x: int, y: int, text: str, col: int | None = None, scale: int | None = None) -> None:
        c = self.s.col if col is None else col
        sc = self.s.scale if scale is None else scale

        if sc <= 1:
            pyxel.text(x, y, text, c)
            return

        for dx in range(sc):
            for dy in range(sc):
                pyxel.text(x + dx, y + dy, text, c)

    def draw_lines(self, *, x: int, y: int, lines: Sequence[str] | Iterable[str], line_h: int, col: int | None = None, scale: int | None = None) -> None:
        c = self.s.col if col is None else col
        sc = self.s.scale if scale is None else scale

        yy = y
        if sc <= 1:
            for line in lines:
                pyxel.text(x, yy, line, c)
                yy += line_h
            return

        for line in lines:
            for dx in range(sc):
                for dy in range(sc):
                    pyxel.text(x + dx, yy + dy, line, c)
            yy += line_h * sc

    def max_chars_in_width(self, *, w_px: int) -> int:
        return max(1, w_px // self.s.char_w)

    def slice_for_cursor(self, *, buf: str, cursor: int, max_chars: int) -> tuple[int, str]:
        view_start = 0 if cursor < max_chars else (cursor - max_chars + 1)
        return view_start, buf[view_start:view_start + max_chars]

    def draw_input(
        self,
        *,
        rect: Rect,
        pad: int,
        prompt: str,
        input_buf: str,
        input_cursor: int,
        blink_on: bool,
        has_selection: bool,
        selection_start: int | None,
        selection_end: int | None,
        prompt_col: int = 7,
        text_col: int = 7,
        selection_col: int = 12,
        caret_col: int = 7,
        text_y_offset: int = 5,
        selection_h: int = 5,
        caret_y_offset: int = 12,
        caret_w: int = 3,
        caret_h: int = 1,
    ) -> tuple[int, str]:
        """
        Draw prompt + visible slice + selection + caret within rect.
        Returns (view_start, visible_text) so callers can reuse.
        """
        prompt_w_px = len(prompt) * self.s.char_w
        input_box_w_px = rect.w - (pad * 2) - prompt_w_px
        max_visible = self.max_chars_in_width(w_px=input_box_w_px)

        view_start, visible_text = self.slice_for_cursor(buf=input_buf, cursor=input_cursor, max_chars=max_visible)

        self.draw_text(x=rect.x + pad, y=rect.y + text_y_offset, text=prompt, col=prompt_col)

        if has_selection and selection_start is not None and selection_end is not None:
            sel_start = min(selection_start, selection_end)
            sel_end = max(selection_start, selection_end)

            visible_sel_start = max(0, sel_start - view_start)
            visible_sel_end = min(len(visible_text), sel_end - view_start)

            if visible_sel_start < len(visible_text) and visible_sel_end > 0:
                sx = rect.x + pad + prompt_w_px + visible_sel_start * self.s.char_w
                sw = (visible_sel_end - visible_sel_start) * self.s.char_w
                Rect(sx, rect.y + text_y_offset, sw, selection_h).fill(selection_col)

        tx = rect.x + pad + prompt_w_px
        self.draw_text(x=tx, y=rect.y + text_y_offset, text=visible_text, col=text_col)

        if blink_on:
            visible_cursor = input_cursor - view_start
            cx = rect.x + pad + prompt_w_px + visible_cursor * self.s.char_w
            Rect(cx, rect.y + caret_y_offset, caret_w, caret_h).fill(caret_col)

        return view_start, visible_text
