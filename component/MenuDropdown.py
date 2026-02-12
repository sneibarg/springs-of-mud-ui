from typing import Optional, Callable
from component.MenuItem import MenuItem


class MenuDropdown:
    def __init__(self, label: str):
        self.label = label
        self.items: list[MenuItem] = []
        self.is_open = False
        self.x = 0
        self.y = 0
        self.width = 0

    def add_item(self, label: str, action: Optional[Callable] = None) -> None:
        self.items.append(MenuItem(label, action))

    def get_height(self) -> int:
        return len(self.items) * 10 + 2