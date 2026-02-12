from typing import Callable, Optional


class MenuItem:
    def __init__(self, label: str, action: Optional[Callable] = None):
        self.label = label
        self.action = action
