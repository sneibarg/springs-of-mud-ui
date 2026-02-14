from __future__ import annotations
from typing import Callable, Optional
from component.button.Button import Button
from component.geometry.Rect import Rect
from component.field.TextField import TextField, TextStyle

import pyxel


class Overlay:
    """
    Dims the screen. Kept as a component so MessageDialog has no pyxel.pset calls.
    """
    def __init__(self, step: int = 2, col: int = 0):
        self.step = step
        self.col = col

    def draw(self) -> None:
        for y in range(0, pyxel.height, self.step):
            for x in range(0, pyxel.width, self.step):
                pyxel.pset(x, y, self.col)


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

    def show(self, title: str, message: str, on_close: Optional[Callable[[], None]] = None) -> None:
        self.title = title
        self.message = message
        self.visible = True
        self.on_close = on_close

        x = (pyxel.width - self.width) // 2
        y = (pyxel.height - self.height) // 2

        self.panel = Rect(x, y, self.width, self.height)
        self.title_bar = Rect(x, y, self.width, 15)

        ok_rect = Rect(x + self.width // 2 - 20, y + self.height - 25, 40, 15)
        self.ok_button = Button(rect=ok_rect, text="OK", base_col=3, hover_col=11, on_click=self.hide)

    def hide(self) -> None:
        was_visible = self.visible
        self.visible = False
        if was_visible and self.on_close:
            self.on_close()

    def update(self) -> None:
        if not self.visible:
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        click = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

        if self.ok_button:
            self.ok_button.update(mx, my, click)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.hide()

    def draw(self) -> None:
        if not self.visible:
            return

        self.overlay.draw()
        self._draw_panel()
        self._draw_title()
        self._draw_body()

        if self.ok_button:
            self.ok_button.draw()

    def _draw_panel(self) -> None:
        self.panel.fill(1)
        self.panel.border(8)
        self.title_bar.fill(8)

    def _draw_title(self) -> None:
        title_x = self.panel.x + (self.panel.w - len(self.title) * self.text.s.char_w) // 2
        self.text.draw_text(x=title_x, y=self.panel.y + 5, text=self.title, col=7)

    def _draw_body(self) -> None:
        max_chars = max(1, (self.panel.w - 20) // self.text.s.char_w)
        lines = self._wrap(self.message, max_chars)

        x = self.panel.x + 10
        y = self.panel.y + 25
        line_h = 8  # matches your previous spacing

        self.text.draw_lines(x=x, y=y, lines=lines[:5], line_h=line_h, col=7, scale=1)

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
