from __future__ import annotations
from typing import Optional
from component.geometry.Rect import Rect
from component.input.KeySource import KeySource, PyxelKeySource
import component.input.Keys as Keys
from component.render.FieldRenderer import FieldRenderer, default_field_renderer


class NumberField:
    def __init__(
        self,
        rect: Rect,
        value: str,
        min_val: int,
        max_val: int,
        *,
        renderer: Optional[FieldRenderer] = None,
        keys: Optional[KeySource] = None,
    ):
        self.rect = rect
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.active = False
        self.cursor = len(value)
        self.r = renderer or default_field_renderer
        self.keys: KeySource = keys or PyxelKeySource()
        self._clamp()

    def blur(self) -> None:
        self.active = False

    def focus(self) -> None:
        self.active = True
        self.cursor = min(self.cursor, len(self.value))

    def _clamp(self) -> None:
        try:
            v = int(self.value) if self.value else 0
        except ValueError:
            v = self.min_val
        v = max(self.min_val, min(self.max_val, v))
        self.value = str(v)
        self.cursor = min(self.cursor, len(self.value))

    def update(self, ctx) -> None:
        mx, my, click = ctx.input.mx, ctx.input.my, ctx.input.click

        if click:
            if self.rect.contains(mx, my):
                self.focus()
            else:
                self.blur()

        if not self.active:
            return

        if self.keys.btnp(Keys.KEY_LEFT, 18, 2):
            self.cursor = max(0, self.cursor - 1)
        if self.keys.btnp(Keys.KEY_RIGHT, 18, 2):
            self.cursor = min(len(self.value), self.cursor + 1)

        if self.keys.btnp(Keys.KEY_BACKSPACE, 18, 2) and self.cursor > 0:
            v = self.value
            c = self.cursor
            self.value = v[: c - 1] + v[c:]
            self.cursor = c - 1

        if self.keys.btnp(Keys.KEY_DELETE) and self.cursor < len(self.value):
            v = self.value
            c = self.cursor
            self.value = v[:c] + v[c + 1 :]

        for i in range(10):
            key = getattr(Keys, f"KEY_{i}")
            if self.keys.btnp(key):
                v = self.value
                c = self.cursor
                self.value = v[:c] + str(i) + v[c:]
                self.cursor = c + 1
                break

        self._clamp()

    def draw(self, ctx, label: str) -> None:
        self.r.draw_text_field(
            ctx,
            self.rect,
            label=label,
            text=self.value,
            active=self.active,
            cursor_pos=self.cursor,
        )
