from __future__ import annotations
from typing import Optional
from component.geometry import Rect
from component.menu.MenuList import MenuList
from component.menu.MenuDropdown import MenuDropdown
from component.render.TextField import TextField, TextStyle


class MenuBar:
    """
    Engine-pattern MenuBar:
      - update(ctx): uses ctx.input only
      - draw(ctx): delegates all drawing to MenuList renderer
    """

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

        menu.x = self._next_menu_x()
        menu.y = self.y + self.height
        menu.width = self.renderer.label_width(label)

        self.menus.append(menu)
        return menu

    def update(self, ctx) -> None:
        mx, my = ctx.input.mx, ctx.input.my
        click = getattr(ctx.input, "click", False)  # prefer ctx.input.click in InputState

        if click:
            if self._handle_click(mx, my):
                return
            self._close_all()
            return

        self._update_hover(mx, my)

    def draw(self, ctx) -> None:
        bar = self._bar_rect()
        self.renderer.draw_bar(ctx, bar=bar)

        for menu in self.menus:
            self.renderer.draw_label(
                ctx,
                menu=menu,
                bar_y=self.y,
                bar_h=self.height,
                active=(self.active_menu == menu),
            )

        if self._has_open_menu():
            self.renderer.draw_dropdown(ctx, menu=self.active_menu, hovered_idx=self.hovered_item_idx)

    def _bar_rect(self) -> Rect:
        return Rect(self.x, self.y, self.width, self.height)

    def _label_rect(self, menu: MenuDropdown) -> Rect:
        return Rect(menu.x, self.y, self.renderer.label_width(menu.label), self.height)

    def _next_menu_x(self) -> int:
        if not self.menus:
            return self.x + 2
        last = self.menus[-1]
        return last.x + last.width + 4

    def _handle_click(self, mx: int, my: int) -> bool:
        # click on bar?
        if self._bar_rect().contains(mx, my):
            return self._click_bar(mx, my)

        # click inside open dropdown?
        if self._has_open_menu():
            if self._click_dropdown(mx, my):
                return True

        return False

    def _click_bar(self, mx: int, my: int) -> bool:
        for menu in self.menus:
            if self._label_rect(menu).contains(mx, my):
                self._toggle(menu)
                return True

        self._close_all()
        return True

    def _click_dropdown(self, mx: int, my: int) -> bool:
        menu = self.active_menu
        if not menu:
            return False

        dd = self.renderer.dropdown_rect(menu)
        if not dd.contains(mx, my):
            return False

        idx = self._dropdown_index(dd, my)
        if 0 <= idx < len(menu.items):
            item = menu.items[idx]
            self._close_all()
            if item.action:
                item.action()
        else:
            self._close_all()

        return True

    def _update_hover(self, mx: int, my: int) -> None:
        self.hovered_item_idx = None
        if not self._has_open_menu():
            return

        menu = self.active_menu
        dd = self.renderer.dropdown_rect(menu)
        if not dd.contains(mx, my):
            return

        idx = self._dropdown_index(dd, my)
        if 0 <= idx < len(menu.items):
            self.hovered_item_idx = idx

    def _dropdown_index(self, dropdown_rect: Rect, my: int) -> int:
        return (my - dropdown_rect.y) // self.renderer.m.item_h

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

    def _has_open_menu(self) -> bool:
        return self.active_menu is not None and self.active_menu.is_open
