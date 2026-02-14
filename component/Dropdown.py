from __future__ import annotations
from typing import List, Optional
from component.geometry.Rect import Rect
from render.FieldRenderer import FieldRenderer, default_field_renderer


class Dropdown:
    def __init__(self, rect: Rect, options: List[str], value: str, renderer: FieldRenderer | None = None):
        self.rect = rect
        self.options = options
        self.value = value
        self.open = False
        self.r = renderer or default_field_renderer

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
        self.r.draw_dropdown_field(self.rect, label=label, value=str(self.value), open_=self.open)

    def draw_popup(self) -> None:
        if not self.open:
            return
        pr = self.popup_rect()
        self.r.draw_dropdown_popup(pr, options=self.options, selected=str(self.value), row_h=self.rect.h)
