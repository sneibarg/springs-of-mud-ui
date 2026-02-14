from __future__ import annotations
from component.geometry.Rect import Rect
from collections import deque
from dataclasses import dataclass

import pyxel


@dataclass(frozen=True)
class TextPaneMetrics:
    pad: int = 4
    header_h: int = 9
    header_y: int = 10
    scroll_y0: int = 20
    input_h: int = 16
    char_w: int = 4  # Pyxel text is effectively 4px wide per char


class TextRenderer:
    def __init__(self, metrics: TextPaneMetrics | None = None):
        self.m = metrics or TextPaneMetrics()

    def draw(self, *, x0: int, y0: int, w: int, h: int, title: str, scrollback: deque[str], scroll_offset: int,
             visible_lines: int, line_spacing: int, font_scale: int, prompt: str, input_buf: str, input_cursor: int,
             has_selection: bool, selection_start: int | None, selection_end: int | None, blink_on: bool) -> None:
        pane = Rect(x0, y0, w, h)
        pane.clip_begin()
        try:
            self._draw_pane_background(pane)
            self._draw_header(x0=x0, y0=y0, w=w, title=title)

            scroll_y0, scroll_h, line_h, max_lines = self._compute_scrollback_layout(y0=y0, h=h, visible_lines=visible_lines, line_spacing=line_spacing            )
            lines = self._slice_scrollback(scrollback, max_lines, scroll_offset)

            self._draw_scrollback_text(x0=x0, y_start=scroll_y0, scroll_h=scroll_h, line_h=line_h, lines=lines, font_scale=font_scale)

            input_rect = self._draw_input_box(x0=x0, y0=y0, w=w, h=h)
            view_start, visible_text = self._compute_input_view(w=w, prompt=prompt, input_buf=input_buf, input_cursor=input_cursor)

            self._draw_prompt(x0=x0, y=input_rect.y, prompt=prompt)
            self._draw_selection(x0=x0, y=input_rect.y, prompt=prompt, view_start=view_start, visible_text=visible_text,
                                 has_selection=has_selection, selection_start=selection_start, selection_end=selection_end)
            self._draw_input_text(x0=x0, y=input_rect.y, prompt=prompt, visible_text=visible_text)
            self._draw_caret(x0=x0, y=input_rect.y, prompt=prompt, view_start=view_start, input_cursor=input_cursor,blink_on=blink_on)
        finally:
            pane.clip_end()

    @staticmethod
    def _draw_pane_background(pane: Rect) -> None:
        pane.fill(0)

    def _draw_header(self, *, x0: int, y0: int, w: int, title: str) -> None:
        Rect(x0, y0, w, self.m.header_h).fill(1)
        pyxel.text(x0 + self.m.pad, y0 + 2, title, 7)

    def _compute_scrollback_layout(self, *, y0: int, h: int, visible_lines: int, line_spacing: int) -> tuple[int, int, int, int]:
        m = self.m
        scroll_y0 = y0 + (m.scroll_y0 - m.header_y)
        scroll_h = h - (scroll_y0 - y0) - m.input_h
        line_h = max(1, line_spacing)
        max_lines = min(visible_lines, max(1, scroll_h // line_h))
        return scroll_y0, scroll_h, line_h, max_lines

    @staticmethod
    def _slice_scrollback(scrollback: deque[str], max_lines: int, scroll_offset: int) -> list[str]:
        total = len(scrollback)
        if total == 0:
            return []

        if scroll_offset > 0:
            end_idx = max(0, total - scroll_offset)
            start_idx = max(0, end_idx - max_lines)
            return list(scrollback)[start_idx:end_idx]

        return list(scrollback)[-max_lines:]

    def _draw_scrollback_text(self, *, x0: int, y_start: int, scroll_h: int, line_h: int, lines: list[str], font_scale: int) -> None:
        y = y_start + (scroll_h - len(lines) * line_h)
        if font_scale > 1:
            self._draw_scaled_lines(x=x0 + self.m.pad, y=y, lines=lines, line_h=line_h, scale=font_scale)
        else:
            self._draw_lines(x=x0 + self.m.pad, y=y, lines=lines, line_h=line_h)

    @staticmethod
    def _draw_lines(*, x: int, y: int, lines: list[str], line_h: int) -> None:
        yy = y
        for line in lines:
            pyxel.text(x, yy, line, 7)
            yy += line_h

    @staticmethod
    def _draw_scaled_lines(*, x: int, y: int, lines: list[str], line_h: int, scale: int) -> None:
        yy = y
        for line in lines:
            for dx in range(scale):
                for dy in range(scale):
                    pyxel.text(x + dx, yy + dy, line, 7)
            yy += line_h * scale

    def _draw_input_box(self, *, x0: int, y0: int, w: int, h: int) -> Rect:
        box_y = y0 + h - self.m.input_h
        r = Rect(x0, box_y, w, self.m.input_h)
        r.fill(1)
        Rect(x0 + 1, box_y + 1, w - 2, self.m.input_h - 2).border(5)
        return r

    def _compute_input_view(self, *, w: int, prompt: str, input_buf: str, input_cursor: int) -> tuple[int, str]:
        m = self.m
        prompt_w_px = len(prompt) * m.char_w
        input_box_w_px = w - (m.pad * 2) - prompt_w_px
        max_visible_chars = max(1, input_box_w_px // m.char_w)

        view_start = 0 if input_cursor < max_visible_chars else (input_cursor - max_visible_chars + 1)
        visible_text = input_buf[view_start:view_start + max_visible_chars]
        return view_start, visible_text

    def _draw_prompt(self, *, x0: int, y: int, prompt: str) -> None:
        pyxel.text(x0 + self.m.pad, y + 5, prompt, 7)

    def _draw_input_text(self, *, x0: int, y: int, prompt: str, visible_text: str) -> None:
        px = x0 + self.m.pad + len(prompt) * self.m.char_w
        pyxel.text(px, y + 5, visible_text, 7)

    def _draw_selection(self, *, x0: int, y: int, prompt: str, view_start: int, visible_text: str, has_selection: bool,
                        selection_start: int | None, selection_end: int | None) -> None:
        if not has_selection or selection_start is None or selection_end is None:
            return

        sel_start = min(selection_start, selection_end)
        sel_end = max(selection_start, selection_end)

        visible_sel_start = max(0, sel_start - view_start)
        visible_sel_end = min(len(visible_text), sel_end - view_start)

        if visible_sel_start >= len(visible_text) or visible_sel_end <= 0:
            return

        prompt_w_px = len(prompt) * self.m.char_w
        sel_x = x0 + self.m.pad + prompt_w_px + visible_sel_start * self.m.char_w
        sel_w = (visible_sel_end - visible_sel_start) * self.m.char_w
        Rect(sel_x, y + 5, sel_w, 5).fill(12)

    def _draw_caret(self, *, x0: int, y: int, prompt: str, view_start: int, input_cursor: int, blink_on: bool) -> None:
        if not blink_on:
            return

        prompt_w_px = len(prompt) * self.m.char_w
        visible_cursor = input_cursor - view_start
        cursor_x = x0 + self.m.pad + prompt_w_px + visible_cursor * self.m.char_w
        Rect(cursor_x, y + 12, 3, 1).fill(7)
