from __future__ import annotations
from dataclasses import dataclass


@dataclass
class GameWorld:
    z_index: int = 0

    def update(self, ctx) -> None:
        pass

    def draw(self, ctx) -> None:
        x0 = ctx.layout.game_x
        y0 = 10
        w = ctx.layout.game_w
        h = ctx.layout.game_h - 10

        ctx.gfx.clip(x0, y0, w, h)
        for y in range(y0, y0 + h, 8):
            for x in range(x0, x0 + w, 8):
                col = 1 if ((x // 8 + y // 8) % 2 == 0) else 2
                ctx.gfx.rect(x, y, 8, 8, col)
        ctx.gfx.clip_reset()
