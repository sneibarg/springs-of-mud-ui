from __future__ import annotations
from typing import Callable, Optional
from component.button.Button import Button
from component.geometry.Rect import Rect
from component.render.TextField import TextField, TextStyle


class Overlay:
    def __init__(self, step: int = 2, col: int = 0):
        self.step = step
        self.col = col

    def draw(self, ctx) -> None:
        w = ctx.layout.w
        h = ctx.layout.h
        step = max(1, self.step)
        col = self.col
        for y in range(0, h, step):
            for x in range(0, w, step):
                ctx.gfx.pset(x, y, col)


class MessageDialog:
    def __init__(self, width: int = 200, height: int = 100, text: TextField | None = None):
        self.visible = False
        self.title = ""
        self.message = ""
        self.width = width
        self.height = height
        self.on_close: Optional[Callable[[], None]] = None
        self.overlay = Overlay(step=2, col=0)
        self.panel = Rect(0, 0, width, height)
        self.title_bar = Rect(0, 0, width, 15)
        self.ok_button: Optional[Button] = None
        self.text = text or TextField(TextStyle(col=7, char_w=4, scale=1))
        self._layout_dirty = True

    def show(self, ctx, title: str, message: str, on_close: Optional[Callable[[], None]] = None) -> None:
        self.title = title
        self.message = message
        self.visible = True
        self.on_close = on_close
        self._layout(ctx)

    def hide(self) -> None:
        was_visible = self.visible
        self.visible = False
        if was_visible and self.on_close:
            self.on_close()

    def update(self, ctx) -> None:
        if not self.visible:
            return

        if self._layout_dirty:
            self._layout(ctx)

        mx, my, _ = self._mouse(ctx)

        if self.ok_button:
            self.ok_button.update(ctx)

        if self._enter_pressed(ctx):
            self.hide()

    def draw(self, ctx) -> None:
        if not self.visible:
            return

        if self._layout_dirty:
            self._layout(ctx)

        self.overlay.draw(ctx)
        self._draw_panel(ctx)
        self._draw_title(ctx)
        self._draw_body(ctx)

        if self.ok_button:
            self.ok_button.draw(ctx)

    def _layout(self, ctx) -> None:
        x = (ctx.layout.w - self.width) // 2
        y = (ctx.layout.h - self.height) // 2

        self.panel = Rect(x, y, self.width, self.height)
        self.title_bar = Rect(x, y, self.width, 15)

        ok_rect = Rect(x + self.width // 2 - 20, y + self.height - 25, 40, 15)
        self.ok_button = Button(rect=ok_rect, text="OK", base_col=3, hover_col=11, on_click=self.hide)
        self._layout_dirty = False

    def _draw_panel(self, ctx) -> None:
        self.panel.fill(ctx, 1)
        self.panel.border(ctx, 8)
        self.title_bar.fill(ctx, 8)

    def _draw_title(self, ctx) -> None:
        title_x = self.panel.x + (self.panel.w - len(self.title) * self.text.s.char_w) // 2
        self.text.draw_text(ctx, x=title_x, y=self.panel.y + 5, text=self.title, col=7)

    def _draw_body(self, ctx) -> None:
        max_chars = max(1, (self.panel.w - 20) // self.text.s.char_w)
        lines = self._wrap(self.message, max_chars)

        x = self.panel.x + 10
        y = self.panel.y + 25
        self.text.draw_lines(ctx, x=x, y=y, lines=lines[:5], line_h=8, col=7, scale=1)

    @staticmethod
    def _mouse(ctx) -> tuple[int, int, bool]:
        return ctx.input.mx, ctx.input.my, ctx.input.click

    @staticmethod
    def _enter_pressed(ctx) -> bool:
        return bool(ctx.input.enter)

    @staticmethod
    def _wrap(text: str, max_chars: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        cur = ""

        for w in words:
            test = (cur + " " + w).strip()
            if len(test) <= max_chars:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w

        if cur:
            lines.append(cur)
        return lines
