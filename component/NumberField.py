import pyxel

from component.Rect import Rect


class NumberField:
    """
    Simple numeric field: click-to-focus, type digits, arrows move cursor, backspace/delete.
    Value stored as string (like your current code), validated to min/max.
    """
    def __init__(self, rect: Rect, value: str, min_val: int, max_val: int):
        self.rect = rect
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.active = False
        self.cursor = len(value)

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
        pyxel.text(self.rect.x, self.rect.y - 13, label, 7)
        pyxel.rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h, 0)
        pyxel.rectb(self.rect.x, self.rect.y, self.rect.w, self.rect.h, 11 if self.active else 5)

        # fit tail
        max_chars = max(1, (self.rect.w - 8) // 4)
        txt = self.value[-max_chars:] if len(self.value) > max_chars else self.value
        pyxel.text(self.rect.x + 4, self.rect.y + 3, txt, 7)

        if self.active and (pyxel.frame_count // 20) % 2 == 0:
            # cursor within visible tail
            visible_start = max(0, len(self.value) - max_chars)
            c = max(0, self.cursor - visible_start)
            cx = self.rect.x + 4 + c * 4
            if cx < self.rect.x + self.rect.w - 2:
                pyxel.rect(cx, self.rect.y + 3, 3, 5, 7)