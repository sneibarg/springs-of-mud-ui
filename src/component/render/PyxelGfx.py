import pyxel

from component.render.api.Graphics import Graphics


class PyxelGfx(Graphics):
    def cls(self, col: int) -> None:
        pyxel.cls(col)

    def clip(self, x: int, y: int, w: int, h: int) -> None:
        pyxel.clip(x, y, w, h)

    def clip_reset(self) -> None:
        pyxel.clip()

    def pset(self, x: int, y: int, col: int) -> None:
        pyxel.pset(x, y, col)

    def line(self, x1: int, y1: int, x2: int, y2: int, col: int) -> None:
        pyxel.line(x1, y1, x2, y2, col)

    def rect(self, x: int, y: int, w: int, h: int, col: int) -> None:
        pyxel.rect(x, y, w, h, col)

    def rectb(self, x: int, y: int, w: int, h: int, col: int) -> None:
        pyxel.rectb(x, y, w, h, col)

    def circ(self, x: int, y: int, r: int, col: int) -> None:
        pyxel.circ(x, y, r, col)

    def circb(self, x: int, y: int, r: int, col: int) -> None:
        pyxel.circb(x, y, r, col)

    def elli(self, x: int, y: int, rx: int, ry: int, col: int) -> None:
        pyxel.elli(x, y, rx, ry, col)

    def ellib(self, x: int, y: int, rx: int, ry: int, col: int) -> None:
        pyxel.ellib(x, y, rx, ry, col)

    def tri(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, col: int) -> None:
        pyxel.tri(x1, y1, x2, y2, x3, y3, col)

    def trib(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, col: int) -> None:
        pyxel.trib(x1, y1, x2, y2, x3, y3, col)

    def text(self, x: int, y: int, s: str, col: int) -> None:
        pyxel.text(x, y, s, col)
