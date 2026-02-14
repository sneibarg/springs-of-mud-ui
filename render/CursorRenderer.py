from __future__ import annotations

import pyxel


class CursorRenderer:
    def draw(self, mx: int | None = None, my: int | None = None) -> None:
        mx = pyxel.mouse_x if mx is None else mx
        my = pyxel.mouse_y if my is None else my

        self.draw_outline(mx, my)
        self.draw_main(mx, my)
        self.draw_fill(mx, my)

    @staticmethod
    def draw_outline(mx, my) -> None:
        pyxel.line(mx - 1, my, mx - 1, my + 9, 0)
        pyxel.line(mx + 1, my, mx + 1, my + 9, 0)
        pyxel.line(mx, my - 1, mx + 6, my + 5, 0)
        pyxel.line(mx, my + 1, mx + 6, my + 7, 0)
        pyxel.line(mx, my + 9, mx + 4, my + 7, 0)

    @staticmethod
    def draw_main(mx, my) -> None:
        pyxel.rect(mx - 1, my, 3, 9, 7)
        pyxel.line(mx, my, mx, my + 8, 7)
        pyxel.line(mx, my, mx + 5, my + 5, 7)
        pyxel.line(mx, my + 8, mx + 3, my + 6, 7)

    @staticmethod
    def draw_fill(mx, my) -> None:
        pyxel.line(mx + 1, my + 3, mx + 3, my + 5, 10)
        pyxel.line(mx + 1, my + 4, mx + 2, my + 5, 10)