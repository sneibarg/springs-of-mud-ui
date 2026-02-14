import pyxel
from typing import List, Optional

from component.geometry.Rect import Rect


class UIDropdown:
    def __init__(self, rect: Rect, options: List[str], value: str):
        self.rect = rect
        self.options = options
        self.value = value
        self.open = False
        self._pad_x = 4
        self._pad_y = 3
        self._arrow_w = 8

    def close(self) -> None:
        self.open = False

    def popup_rect(self) -> Rect:
        return Rect(self.rect.x, self.rect.y + self.rect.h, self.rect.w, len(self.options) * self.rect.h)

    def update(self, mx: int, my: int, click: bool) -> bool:
        changed = False
        if not click:
            return False

        if self.rect.contains(mx, my):
            self.open = not self.open
            return False

        if not self.open:
            return False

        pr = self.popup_rect()
        if pr.contains(mx, my):
            idx = (my - pr.y) // self.rect.h
            if 0 <= idx < len(self.options):
                new_val = self.options[idx]
                if new_val != self.value:
                    self.value = new_val
                    changed = True

        self.open = False
        return changed

    def draw(self, label: Optional[str] = None) -> None:
        if label:
            pyxel.text(self.rect.x, self.rect.y - 13, label, 7)

        self._draw_closed_box()
        self._draw_value_text()
        self._draw_arrow()

    def draw_popup(self) -> None:
        if not self.open:
            return

        pr = self.popup_rect()
        self._draw_popup_backplate(pr)
        self._draw_popup_items(pr)

    def _draw_closed_box(self) -> None:
        self.rect.fill(0)
        self.rect.border(11 if self.open else 5)

    def _draw_value_text(self) -> None:
        pyxel.text(self.rect.x + self._pad_x, self.rect.y + self._pad_y, str(self.value), 7)

    def _draw_arrow(self) -> None:
        arrow = "^" if self.open else "v"
        pyxel.text(self.rect.x + self.rect.w - self._arrow_w, self.rect.y + self._pad_y, arrow, 7)

    @staticmethod
    def _draw_popup_backplate(pr: Rect) -> None:
        Rect(pr.x - 1, pr.y - 1, pr.w + 2, pr.h + 2).fill(1)

    def _draw_popup_items(self, pr: Rect) -> None:
        for i, opt in enumerate(self.options):
            item_y = pr.y + i * self.rect.h
            item = Rect(pr.x, item_y, pr.w, self.rect.h)

            fill = 3 if opt == self.value else 2
            item.fill(fill)
            item.border(7)
            pyxel.text(item.x + self._pad_x, item.y + self._pad_y, str(opt), 7)
