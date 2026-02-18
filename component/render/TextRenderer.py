from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from component.geometry.Rect import Rect
from component.render.abstract.Renderable import Renderable
from component.render.TextField import TextStyle, TextField


@dataclass(frozen=True)
class TextPaneMetrics:
    pad: int = 4
    header_h: int = 9
    header_y: int = 10
    scroll_y0: int = 20
    input_h: int = 16
    char_w: int = 4


@dataclass(frozen=True)
class _ScrollLayout:
    y0: int
    h: int
    line_h: int
    max_lines: int


class TextRenderer(Renderable):
    def __init__(self, *, metrics: TextPaneMetrics | None = None, text_field: TextField | None = None):
        self.m = metrics or TextPaneMetrics()
        self.t = text_field or TextField(TextStyle(char_w=self.m.char_w))
        self._state = None

    def update(self, ctx) -> None:
        return

    def draw(self, ctx) -> None:
        if self._state is None:
            return
        self.draw_pane(ctx, **self._state)

    def set_state(
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
        self._state = dict(
            x0=x0,
            y0=y0,
            w=w,
            h=h,
            title=title,
            scrollback=scrollback,
            scroll_offset=scroll_offset,
            visible_lines=visible_lines,
            line_spacing=line_spacing,
            font_scale=font_scale,
            prompt=prompt,
            input_buf=input_buf,
            input_cursor=input_cursor,
            has_selection=has_selection,
            selection_start=selection_start,
            selection_end=selection_end,
            blink_on=blink_on,
        )

    def draw_pane(
        self,
        ctx,
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
        pane = Rect(x0, y0, w, h)

        ctx.gfx.clip(pane.x, pane.y, pane.w, pane.h)
        try:
            self._draw_pane(ctx, pane)
            self._draw_header(ctx, pane, title)

            scroll_layout = self._scroll_layout(pane, visible_lines, line_spacing)
            lines = self._slice_scrollback(scrollback, scroll_layout.max_lines, scroll_offset)
            self._draw_scrollback(ctx, pane, scroll_layout, lines, font_scale)

            input_rect = self._input_rect(pane)
            self._draw_input(ctx, input_rect, prompt, input_buf, input_cursor, has_selection, selection_start, selection_end, blink_on)
        finally:
            ctx.gfx.clip_reset()  # reset

    @staticmethod
    def _draw_pane(ctx, pane: Rect) -> None:
        pane.fill(ctx, 0)

    def _draw_header(self, ctx, pane: Rect, title: str) -> None:
        header = Rect(pane.x, pane.y, pane.w, self.m.header_h)
        header.fill(ctx, 1)
        self.t.draw_text(ctx, x=pane.x + self.m.pad, y=pane.y + 2, text=title, col=7)

    def _scroll_layout(self, pane: Rect, visible_lines: int, line_spacing: int) -> _ScrollLayout:
        scroll_y0 = pane.y + (self.m.scroll_y0 - self.m.header_y)
        scroll_h = pane.h - (scroll_y0 - pane.y) - self.m.input_h
        line_h = max(1, int(line_spacing))
        max_lines = min(int(visible_lines), max(1, scroll_h // line_h))
        return _ScrollLayout(scroll_y0, scroll_h, line_h, max_lines)

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

    def _draw_scrollback(self, ctx, pane: Rect, layout: _ScrollLayout, lines: list[str], font_scale: int) -> None:
        y_start = layout.y0 + (layout.h - len(lines) * layout.line_h)
        self.t.draw_lines(
            ctx,
            x=pane.x + self.m.pad,
            y=y_start,
            lines=lines,
            line_h=layout.line_h,
            col=7,
            scale=max(1, int(font_scale)),
        )

    def _input_rect(self, pane: Rect) -> Rect:
        return Rect(pane.x, pane.y + pane.h - self.m.input_h, pane.w, self.m.input_h)

    def _draw_input(
        self,
        ctx,
        input_rect: Rect,
        prompt: str,
        input_buf: str,
        input_cursor: int,
        has_selection: bool,
        selection_start: int | None,
        selection_end: int | None,
        blink_on: bool,
    ) -> None:
        self._draw_input_box(ctx, input_rect)
        self.t.draw_input(
            ctx,
            rect=input_rect,
            pad=self.m.pad,
            prompt=prompt,
            input_buf=input_buf,
            input_cursor=input_cursor,
            blink_on=blink_on,
            has_selection=has_selection,
            selection_start=selection_start,
            selection_end=selection_end,
            prompt_col=7,
            text_col=7,
            selection_col=12,
            caret_col=7,
        )

    @staticmethod
    def _draw_input_box(ctx, r: Rect) -> None:
        r.fill(ctx, 1)
        Rect(r.x + 1, r.y + 1, r.w - 2, r.h - 2).border(ctx, 5)
