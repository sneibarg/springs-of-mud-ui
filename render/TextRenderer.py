from __future__ import annotations
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
    """
    Renders the right text pane:
      - background + header
      - scrollback (with vertical scroll_offset)
      - input box with prompt, selection highlight, and caret

    Keeps drawing concerns out of MudClientUI.
    """

    def __init__(self, metrics: TextPaneMetrics | None = None):
        self.m = metrics or TextPaneMetrics()

    def _slice_scrollback(self, scrollback: deque[str], max_lines: int, scroll_offset: int) -> list[str]:
        total = len(scrollback)
        if total == 0:
            return []

        if scroll_offset > 0:
            end_idx = max(0, total - scroll_offset)
            start_idx = max(0, end_idx - max_lines)
            return list(scrollback)[start_idx:end_idx]

        return list(scrollback)[-max_lines:]

    def draw(
            self,
            *,
            x0: int,
            y0: int,
            w: int,
            h: int,
            title: str,
            scrollback: deque[str],
            scroll_offset: int,
            visible_lines: int,
            line_spacing: int,
            font_scale: int,
            prompt: str,
            input_buf: str,
            input_cursor: int,
            has_selection: bool,
            selection_start: int | None,
            selection_end: int | None,
            blink_on: bool,
    ) -> None:
        m = self.m

        pyxel.clip(x0, y0, w, h)

        # Pane background + header
        pyxel.rect(x0, y0, w, h, 0)
        pyxel.rect(x0, y0, w, m.header_h, 1)
        pyxel.text(x0 + m.pad, y0 + 2, title, 7)

        # Scroll area
        input_h = m.input_h
        scroll_y0 = y0 + (m.scroll_y0 - m.header_y)  # keep your original relative spacing
        scroll_h = h - (scroll_y0 - y0) - input_h
        line_h = max(1, line_spacing)

        max_lines = min(visible_lines, max(1, scroll_h // line_h))
        lines = self._slice_scrollback(scrollback, max_lines, scroll_offset)

        # bottom-align scrollback within scroll area
        y = scroll_y0 + (scroll_h - len(lines) * line_h)

        if font_scale > 1:
            for line in lines:
                for dx in range(font_scale):
                    for dy in range(font_scale):
                        pyxel.text(x0 + m.pad + dx, y + dy, line, 7)
                y += line_h * font_scale
        else:
            for line in lines:
                pyxel.text(x0 + m.pad, y, line, 7)
                y += line_h

        # Input box
        box_y = y0 + h - input_h
        pyxel.rect(x0, box_y, w, input_h, 1)
        pyxel.rectb(x0 + 1, box_y + 1, w - 2, input_h - 2, 5)

        prompt_w_px = len(prompt) * m.char_w
        input_box_w_px = w - (m.pad * 2) - prompt_w_px
        max_visible_chars = max(1, input_box_w_px // m.char_w)

        # horizontal scroll to keep cursor visible
        if input_cursor < max_visible_chars:
            view_start = 0
        else:
            view_start = input_cursor - max_visible_chars + 1

        visible_text = input_buf[view_start:view_start + max_visible_chars]

        # Prompt
        pyxel.text(x0 + m.pad, box_y + 5, prompt, 7)

        # Selection highlight
        if has_selection and selection_start is not None and selection_end is not None:
            sel_start = min(selection_start, selection_end)
            sel_end = max(selection_start, selection_end)

            visible_sel_start = max(0, sel_start - view_start)
            visible_sel_end = min(len(visible_text), sel_end - view_start)

            if visible_sel_start < len(visible_text) and visible_sel_end > 0:
                sel_x = x0 + m.pad + prompt_w_px + visible_sel_start * m.char_w
                sel_w = (visible_sel_end - visible_sel_start) * m.char_w
                pyxel.rect(sel_x, box_y + 5, sel_w, 5, 12)

        # Input text
        pyxel.text(x0 + m.pad + prompt_w_px, box_y + 5, visible_text, 7)

        # Caret
        if blink_on:
            visible_cursor = input_cursor - view_start
            cursor_x = x0 + m.pad + prompt_w_px + visible_cursor * m.char_w
            pyxel.rect(cursor_x, box_y + 12, 3, 1, 7)

        pyxel.clip()
