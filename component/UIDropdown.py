import pyxel

from typing import List, Optional
from component.Rect import Rect


class UIDropdown:
    def __init__(self, rect: Rect, options: List[str], value: str):
        self.rect = rect
        self.options = options
        self.value = value
        self.open = False

    def close(self) -> None:
        self.open = False

    def popup_rect(self) -> Rect:
        return Rect(self.rect.x, self.rect.y + self.rect.h, self.rect.w, len(self.options) * self.rect.h)

    def update(self, mx: int, my: int, click: bool) -> bool:
        changed = False
        if click:
            if self.rect.contains(mx, my):
                self.open = not self.open
                return False

            if self.open:
                pr = self.popup_rect()
                if pr.contains(mx, my):
                    idx = (my - pr.y) // self.rect.h
                    if 0 <= idx < len(self.options):
                        new_val = self.options[idx]
                        if new_val != self.value:
                            self.value = new_val
                            changed = True
                    self.open = False
                else:
                    self.open = False
        return changed

    def draw(self, label: Optional[str] = None) -> None:
        if label:
            pyxel.text(self.rect.x, self.rect.y - 13, label, 7)

        pyxel.rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h, 0)
        pyxel.rectb(self.rect.x, self.rect.y, self.rect.w, self.rect.h, 11 if self.open else 5)
        pyxel.text(self.rect.x + 4, self.rect.y + 3, str(self.value), 7)
        pyxel.text(self.rect.x + self.rect.w - 8, self.rect.y + 3, "^" if self.open else "v", 7)

    def draw_popup(self) -> None:
        if not self.open:
            return

        pr = self.popup_rect()
        pyxel.rect(pr.x - 1, pr.y - 1, pr.w + 2, pr.h + 2, 1)

        for i, opt in enumerate(self.options):
            y = pr.y + i * self.rect.h
            fill = 3 if opt == self.value else 2
            pyxel.rect(pr.x, y, pr.w, self.rect.h, fill)
            pyxel.rectb(pr.x, y, pr.w, self.rect.h, 7)
            pyxel.text(pr.x + 4, y + 3, str(opt), 7)
