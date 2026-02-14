from __future__ import annotations

import pyxel

from component.geometry.Rect import Rect
from component.render.FieldRenderer import FieldRenderer, default_field_renderer


class NumberField:
    def __init__(self, rect: Rect, value: str, min_val: int, max_val: int, renderer: FieldRenderer | None = None):
        self.rect = rect
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.active = False
        self.cursor = len(value)
        self.r = renderer or default_field_renderer

    def blur(self) -> None:
        self.active = False

    def focus(self) -> None:
        self.active = True
        self.cursor = len(self.value)

    def _clamp(self) -> None:
        try:
            v = int(self.value) if self.value else 0
        except ValueError:
            v = self.min_val
        v = max(self.min_val, min(self.max_val, v))
        self.value = str(v)
        self.cursor = min(self.cursor, len(self.value))

    def update(self, mx: int, my: int, click: bool) -> None:
        if click:
            if self.rect.contains(mx, my):
                self.focus()
            else:
                self.blur()

        if not self.active:
            return

        if pyxel.btnp(pyxel.KEY_LEFT, 18, 2):
            self.cursor = max(0, self.cursor - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT, 18, 2):
            self.cursor = min(len(self.value), self.cursor + 1)

        if pyxel.btnp(pyxel.KEY_BACKSPACE, 18, 2) and self.cursor > 0:
            self.value = self.value[: self.cursor - 1] + self.value[self.cursor :]
            self.cursor -= 1

        if pyxel.btnp(pyxel.KEY_DELETE) and self.cursor < len(self.value):
            self.value = self.value[: self.cursor] + self.value[self.cursor + 1 :]

        for i in range(10):
            key = getattr(pyxel, f"KEY_{i}", None)
            if key and pyxel.btnp(key):
                self.value = self.value[: self.cursor] + str(i) + self.value[self.cursor :]
                self.cursor += 1

        self._clamp()

    def draw(self, label: str) -> None:
        self.r.draw_text_field(self.rect, label=label, text=self.value, active=self.active, cursor_pos=self.cursor)
