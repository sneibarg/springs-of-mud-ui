from __future__ import annotations
from engine.context.InputState import InputState

import pyxel


class PyxelDriver:
    def __init__(self, *, title: str, w: int, h: int, fps: int = 60, display_scale: int = 3):
        pyxel.init(w, h, title=title, fps=fps, display_scale=display_scale)
        pyxel.mouse(True)

    @staticmethod
    def sample_input() -> InputState:
        return InputState(mx=pyxel.mouse_x, my=pyxel.mouse_y, click=pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT), wheel=pyxel.mouse_wheel, frame_count=pyxel.frame_count)

    @staticmethod
    def clear(col: int = 0) -> None:
        pyxel.cls(col)

    @staticmethod
    def run(update_fn, draw_fn) -> None:
        pyxel.run(update_fn, draw_fn)

    @staticmethod
    def quit() -> None:
        pyxel.quit()
