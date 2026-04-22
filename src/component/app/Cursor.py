from __future__ import annotations
from dataclasses import dataclass
from component.render import CursorRenderer


@dataclass
class Cursor:
    cursor_renderer: CursorRenderer
    z_index: int = 40

    def update(self, ctx) -> None:
        pass

    def draw(self, ctx) -> None:
        self.cursor_renderer.draw(ctx)
