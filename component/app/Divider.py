from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Divider:
    z_index: int = 15

    def update(self, ctx) -> None:
        pass

    def draw(self, ctx) -> None:
        ctx.gfx.rect(ctx.layout.game_w, 10, ctx.layout.gutter, ctx.layout.h - 10, 5)
