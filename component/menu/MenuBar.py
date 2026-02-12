from typing import Optional
from component.menu.MenuDropdown import MenuDropdown

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

    def add_menu(self, label: str) -> MenuDropdown:
        menu = MenuDropdown(label)
        if self.menus:
            last_menu = self.menus[-1]
            menu.x = last_menu.x + last_menu.width + 4
        else:
            menu.x = self.x + 2

        menu.y = self.y + self.height
        menu.width = len(label) * 4 + 8
        self.menus.append(menu)
        return menu

    def update(self) -> None:
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # Check menu labels
            if self.y <= my < self.y + self.height:
                for menu in self.menus:
                    label_width = len(menu.label) * 4 + 8
                    if menu.x <= mx < menu.x + label_width:
                        # Toggle menu
                        if self.active_menu == menu:
                            self.active_menu = None
                        else:
                            self.active_menu = menu
                            menu.is_open = True
                        return

            if self.active_menu:
                item_y = self.active_menu.y + 1
                max_width = max(len(item.label) * 4 + 8 for item in self.active_menu.items)

                for idx, item in enumerate(self.active_menu.items):
                    if (self.active_menu.x <= mx < self.active_menu.x + max_width and
                        item_y <= my < item_y + 10):
                        if item.action:
                            item.action()
                        self.active_menu = None
                        return
                    item_y += 10

            # Click outside - close menu
            self.active_menu = None

        # Track hover for highlighting
        if self.active_menu:
            item_y = self.active_menu.y + 1
            max_width = max(len(item.label) * 4 + 8 for item in self.active_menu.items)
            self.hovered_item_idx = None

            for idx, item in enumerate(self.active_menu.items):
                if (self.active_menu.x <= mx < self.active_menu.x + max_width and
                    item_y <= my < item_y + 10):
                    self.hovered_item_idx = idx
                    break
                item_y += 10

    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.width, self.height, 1)

        for menu in self.menus:
            label_width = len(menu.label) * 4 + 8
            if self.active_menu == menu:
                pyxel.rect(menu.x, self.y, label_width, self.height, 5)
            pyxel.text(menu.x + 4, self.y + 2, menu.label, 7)

        if self.active_menu:
            self._draw_dropdown(self.active_menu)

    def _draw_dropdown(self, menu: MenuDropdown) -> None:
        max_width = max(len(item.label) * 4 + 8 for item in menu.items)
        dropdown_height = menu.get_height()

        pyxel.rect(menu.x, menu.y, max_width, dropdown_height, 1)
        pyxel.rectb(menu.x, menu.y, max_width, dropdown_height, 5)

        item_y = menu.y + 1
        for idx, item in enumerate(menu.items):
            if self.hovered_item_idx == idx:
                pyxel.rect(menu.x + 1, item_y, max_width - 2, 9, 5)
            pyxel.text(menu.x + 4, item_y + 2, item.label, 7)
            item_y += 10
