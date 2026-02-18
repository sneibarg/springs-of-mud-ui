from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from component.geometry import Rect
from component.menu.MenuDropdown import MenuDropdown
from component.render.TextField import TextField


@dataclass(frozen=True)
class MenuMetrics:
    char_w: int = 4
    pad_x: int = 4
    bar_text_y: int = 2
    item_h: int = 10
    item_text_y: int = 2
    dropdown_pad_y: int = 1
    bar_bg: int = 1
    bar_active_bg: int = 5
    dropdown_bg: int = 1
    dropdown_border: int = 5
    item_hover_bg: int = 5
    text_col: int = 7


class MenuList:
    def __init__(self, text: TextField, metrics: MenuMetrics | None = None):
        self.text = text
        self.m = metrics or MenuMetrics()

    def label_width(self, label: str) -> int:
        return len(label) * self.m.char_w + 8

    def dropdown_width(self, menu: MenuDropdown) -> int:
        if not menu.items:
            return 0
        return max(self.label_width(it.label) for it in menu.items)

    def dropdown_rect(self, menu: MenuDropdown) -> Rect:
        return Rect(menu.x, menu.y, self.dropdown_width(menu), menu.get_height())

    def draw_bar(self, ctx, *, bar: Rect) -> None:
        bar.fill(ctx, self.m.bar_bg)

    def draw_label(self, ctx, *, menu: MenuDropdown, bar_y: int, bar_h: int, active: bool) -> None:
        w = self.label_width(menu.label)
        if active:
            Rect(menu.x, bar_y, w, bar_h).fill(ctx, self.m.bar_active_bg)
        self.text.draw_text(ctx, x=menu.x + self.m.pad_x, y=bar_y + self.m.bar_text_y, text=menu.label, col=self.m.text_col)

    def draw_dropdown(self, ctx, *, menu: MenuDropdown, hovered_idx: Optional[int]) -> None:
        if not menu.items:
            return

        panel = self.dropdown_rect(menu)
        panel.fill(ctx, self.m.dropdown_bg)
        panel.border(ctx, self.m.dropdown_border)
        yy = panel.y + self.m.dropdown_pad_y
        for idx, it in enumerate(menu.items):
            if hovered_idx == idx:
                Rect(panel.x + 1, yy, panel.w - 2, self.m.item_h - 1).fill(ctx, self.m.item_hover_bg)

            self.text.draw_text(ctx, x=panel.x + self.m.pad_x, y=yy + self.m.item_text_y, text=it.label, col=self.m.text_col)
            yy += self.m.item_h
