from __future__ import annotations
from typing import Optional
from component.geometry.Rect import Rect
from component.field.TextField import TextField, TextStyle
from component.menu.MenuDropdown import MenuDropdown
from component.menu.MenuList import MenuList

import pyxel


class MenuBar:
    def __init__(self, x: int = 0, y: int = 0, width: int = 400, height: int = 10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.menus: list[MenuDropdown] = []
        self.active_menu: Optional[MenuDropdown] = None
        self.hovered_item_idx: Optional[int] = None
        self.text = TextField(TextStyle(col=7, char_w=4, scale=1))
        self.renderer = MenuList(self.text)

    def add_menu(self, label: str) -> MenuDropdown:
        menu = MenuDropdown(label)
        if self.menus:
            last = self.menus[-1]
            menu.x = last.x + last.width + 4
        else:
            menu.x = self.x + 2

        menu.y = self.y + self.height
        menu.width = self.renderer.label_width(label)

        self.menus.append(menu)
        return menu

    def update(self) -> None:
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        click = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

        if click:
            if self._click_bar(mx, my):
                return
            if self._click_dropdown(mx, my):
                return
            self._close_all()
        else:
            self._update_hover(mx, my)

    def draw(self) -> None:
        bar = Rect(self.x, self.y, self.width, self.height)
        self.renderer.draw_bar(bar=bar)

        for menu in self.menus:
            self.renderer.draw_label(menu=menu, bar_y=self.y, bar_h=self.height, active=(self.active_menu == menu))

        if self.active_menu and self.active_menu.is_open:
            self.renderer.draw_dropdown(menu=self.active_menu, hovered_idx=self.hovered_item_idx)

    def _bar_rect(self) -> Rect:
        return Rect(self.x, self.y, self.width, self.height)

    def _label_rect(self, menu: MenuDropdown) -> Rect:
        return Rect(menu.x, self.y, self.renderer.label_width(menu.label), self.height)

    def _click_bar(self, mx: int, my: int) -> bool:
        if not self._bar_rect().contains(mx, my):
            return False

        for menu in self.menus:
            if self._label_rect(menu).contains(mx, my):
                self._toggle(menu)
                return True

        self._close_all()
        return True

    def _click_dropdown(self, mx: int, my: int) -> bool:
        if not (self.active_menu and self.active_menu.is_open):
            return False

        dd = self.renderer.dropdown_rect(self.active_menu)
        if not dd.contains(mx, my):
            return False

        idx = (my - dd.y) // self.renderer.m.item_h
        if 0 <= idx < len(self.active_menu.items):
            item = self.active_menu.items[idx]
            self._close_all()
            if item.action:
                item.action()
        else:
            self._close_all()

        return True

    def _update_hover(self, mx: int, my: int) -> None:
        self.hovered_item_idx = None
        if not (self.active_menu and self.active_menu.is_open):
            return

        dd = self.renderer.dropdown_rect(self.active_menu)
        if not dd.contains(mx, my):
            return

        idx = (my - dd.y) // self.renderer.m.item_h
        if 0 <= idx < len(self.active_menu.items):
            self.hovered_item_idx = idx

    def _toggle(self, menu: MenuDropdown) -> None:
        if self.active_menu == menu and menu.is_open:
            self._close_all()
            return

        self._close_all()
        self.active_menu = menu
        menu.is_open = True
        self.hovered_item_idx = None

    def _close_all(self) -> None:
        for m in self.menus:
            m.is_open = False
        self.active_menu = None
        self.hovered_item_idx = None
