from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from component.geometry.Rect import Rect
from component.field.TextField import TextField

import pyxel


@dataclass
class TextInputModel:
    value: str = ""
    cursor: int = 0
    active: bool = False


class TextInputField:
    """
    Text clipboard box component:
      - owns keyboard handling (pyxel)
      - owns drawing (Rect + TextField)
      - exposes model.value for pane to read/write
    """

    def __init__(
        self, rect: Rect, model: TextInputModel, *, max_len: int = 100, border_idle: int = 5, border_active: int = 11,
            fill_col: int = 0, text_col: int = 7, caret_col: int = 7, blink_div: int = 20, text_field: Optional[TextField] = None, mask_char: Optional[str] = None):
        self.rect = rect
        self.model = model
        self.max_len = max_len
        self.border_idle = border_idle
        self.border_active = border_active
        self.fill_col = fill_col
        self.text_col = text_col
        self.caret_col = caret_col
        self.blink_div = blink_div
        self.tf = text_field or TextField()
        self.mask_char = mask_char

    def focus(self) -> None:
        self.model.active = True
        self.model.cursor = min(self.model.cursor, len(self.model.value))

    def blur(self) -> None:
        self.model.active = False

    def set_value(self, v: str) -> None:
        self.model.value = v[: self.max_len]
        self.model.cursor = min(self.model.cursor, len(self.model.value))

    def update(self, mx: int, my: int, click: bool) -> None:
        if click:
            if self.rect.contains(mx, my):
                self.focus()
            else:
                self.blur()

        if not self.model.active:
            return

        if pyxel.btnp(pyxel.KEY_LEFT, 18, 2):
            self.model.cursor = max(0, self.model.cursor - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT, 18, 2):
            self.model.cursor = min(len(self.model.value), self.model.cursor + 1)

        if pyxel.btnp(pyxel.KEY_BACKSPACE, 18, 2) and self.model.cursor > 0:
            v = self.model.value
            self.model.value = v[: self.model.cursor - 1] + v[self.model.cursor :]
            self.model.cursor -= 1

        if pyxel.btnp(pyxel.KEY_DELETE) and self.model.cursor < len(self.model.value):
            v = self.model.value
            self.model.value = v[: self.model.cursor] + v[self.model.cursor + 1 :]

        if len(self.model.value) >= self.max_len:
            return

        shift = pyxel.btn(pyxel.KEY_SHIFT)

        for i in range(26):
            key = getattr(pyxel, f"KEY_{chr(ord('A') + i)}", None)
            if key and pyxel.btnp(key):
                ch = chr(ord("a") + i)
                if shift:
                    ch = ch.upper()
                self._insert(ch)
                return

        for i in range(10):
            key = getattr(pyxel, f"KEY_{i}", None)
            if key and pyxel.btnp(key):
                self._insert(str(i))
                return

        mapping = [
            (getattr(pyxel, "KEY_PERIOD", None), "."),
            (getattr(pyxel, "KEY_COLON", None), ":"),
            (getattr(pyxel, "KEY_SLASH", None), "/"),
            (getattr(pyxel, "KEY_MINUS", None), "-"),
            (getattr(pyxel, "KEY_SPACE", None), " "),
            (getattr(pyxel, "KEY_APOSTROPHE", None), "@" if shift else "'"),
        ]
        for key, ch in mapping:
            if key is not None and pyxel.btnp(key):
                self._insert(ch)
                return

    def _insert(self, ch: str) -> None:
        v = self.model.value
        c = self.model.cursor
        self.model.value = v[:c] + ch + v[c:]
        self.model.cursor += 1

    def draw(self) -> None:
        self.rect.fill(self.fill_col)
        self.rect.border(self.border_active if self.model.active else self.border_idle)

        raw = self.model.value
        txt = raw if self.mask_char is None else (self.mask_char * len(raw))

        max_chars = max(1, (self.rect.w - 8) // self.tf.s.char_w)
        visible = txt[-max_chars:] if len(txt) > max_chars else txt

        self.tf.draw_text(x=self.rect.x + 4, y=self.rect.y + 3, text=visible, col=self.text_col)

        if not self.model.active:
            return

        if (pyxel.frame_count // self.blink_div) % 2 != 0:
            return

        visible_start = max(0, len(txt) - max_chars)
        caret_pos = max(0, self.model.cursor - visible_start)
        cx = self.rect.x + 4 + caret_pos * self.tf.s.char_w
        if cx < self.rect.x + self.rect.w - 2:
            Rect(cx, self.rect.y + 3, 3, 5).fill(self.caret_col)
