from dataclasses import dataclass


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    def contains(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h
