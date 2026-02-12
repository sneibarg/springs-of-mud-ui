from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
from component.button.Button import Button
from component.geometry.Rect import Rect

import pyxel


@dataclass(frozen=True)
class DialogStyle:
    panel_fill: int = 1
    panel_border: int = 8
    title_fill: int = 8
    title_text: int = 7
    body_text: int = 7
    overlay_color: int = 0  # used by pset stipple
    ok_base: int = 3
    ok_hover: int = 11


class MessageDialog:
    def __init__(self, width: int = 200, height: int = 100, style: DialogStyle | None = None):
        self.visible = False
        self.title = ""
        self.message = ""
        self.width = width
        self.height = height
        self.on_close: Optional[Callable[[], None]] = None
        self.style = style or DialogStyle()
        self.rect = Rect(0, 0, self.width, self.height)
        self.ok_button: Optional[Button] = None

    def show(self, title: str, message: str, on_close: Optional[Callable[[], None]] = None) -> None:
        self.title = title
        self.message = message
        self.visible = True
        self.on_close = on_close

        x = (pyxel.width - self.width) // 2
        y = (pyxel.height - self.height) // 2
        self.rect = Rect(x, y, self.width, self.height)

        ok_w, ok_h = 40, 15
        ok_x = x + self.width // 2 - ok_w // 2
        ok_y = y + self.height - 25

        self.ok_button = Button(rect=Rect(ok_x, ok_y, ok_w, ok_h), text="OK", base_col=self.style.ok_base, hover_col=self.style.ok_hover,on_click=self.hide)

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

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_KP_ENTER):
            self.hide()

    def draw(self) -> None:
        if not self.visible:
            return

        self._draw_overlay()
        self._draw_panel()
        self._draw_title_bar()
        self._draw_message_body()

        if self.ok_button:
            self.ok_button.draw()

    @staticmethod
    def _draw_overlay() -> None:
        for y in range(0, pyxel.height, 2):
            for x in range(0, pyxel.width, 2):
                pyxel.pset(x, y, 0)

    def _draw_panel(self) -> None:
        s = self.style
        r = self.rect
        pyxel.rect(r.x, r.y, r.w, r.h, s.panel_fill)
        pyxel.rectb(r.x, r.y, r.w, r.h, s.panel_border)

    def _draw_title_bar(self) -> None:
        s = self.style
        r = self.rect
        pyxel.rect(r.x, r.y, r.w, 15, s.title_fill)
        title_x = r.x + (r.w - len(self.title) * 4) // 2
        pyxel.text(title_x, r.y + 5, self.title, s.title_text)

    def _draw_message_body(self) -> None:
        s = self.style
        r = self.rect

        lines = self._wrap_text(self.message, max_chars=(r.w - 20) // 4)
        text_y = r.y + 25
        for line in lines[:5]:
            pyxel.text(r.x + 10, text_y, line, s.body_text)
            text_y += 8

    @staticmethod
    def _wrap_text(text: str, max_chars: int) -> list[str]:
        if not text:
            return [""]

        words = text.split()
        lines: list[str] = []
        cur = ""
        for w in words:
            test = f"{cur} {w}".strip()
            if len(test) <= max_chars:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w

        if cur:
            lines.append(cur)

        return lines
