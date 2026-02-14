from __future__ import annotations
from typing import Callable, Optional
from component.button.Button import Button
from component.geometry.Rect import Rect

import pyxel


class MessageDialog:
    def __init__(self, width: int = 200, height: int = 100):
        self.visible = False
        self.title = ""
        self.message = ""
        self.width = width
        self.height = height
        self.on_close: Optional[Callable[[], None]] = None
        self.panel = Rect(0, 0, width, height)
        self.ok_button: Optional[Button] = None

    def show(self, title: str, message: str, on_close: Optional[Callable] = None) -> None:
        self.title = title
        self.message = message
        self.visible = True
        self.on_close = on_close

        x = (pyxel.width - self.width) // 2
        y = (pyxel.height - self.height) // 2
        self.panel = Rect(x, y, self.width, self.height)

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

        self._draw_overlay()
        self.panel.draw(fill=1, border=8)

        title_rect = Rect(self.panel.x, self.panel.y, self.panel.w, 15)
        title_rect.fill(8)

        title_x = self.panel.x + (self.panel.w - len(self.title) * 4) // 2
        pyxel.text(title_x, self.panel.y + 5, self.title, 7)

        self._draw_message_body()

        if self.ok_button:
            self.ok_button.draw()

    @staticmethod
    def _draw_overlay() -> None:
        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

    def _draw_message_body(self) -> None:
        max_chars = (self.panel.w - 20) // 4
        lines = self._wrap(self.message, max_chars)
        y = self.panel.y + 25
        for line in lines[:5]:
            pyxel.text(self.panel.x + 10, y, line, 7)
            y += 8

    @staticmethod
    def _wrap(text: str, max_chars: int) -> list[str]:
        words = text.split()
        lines = []
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
