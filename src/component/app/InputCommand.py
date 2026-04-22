from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from component.app.ModalGate import ModalGate


@dataclass
class InputCommand:
    gate: ModalGate
    on_command: Callable[[str], None]
    z_index: int = 5

    def update(self, ctx) -> None:
        if self.gate.is_blocking():
            return

        cmd = ctx.text_input.update()
        if cmd is None:
            return

        ctx.scroll_offset = 0
        self.on_command(cmd)

    def draw(self, ctx) -> None:
        pass
