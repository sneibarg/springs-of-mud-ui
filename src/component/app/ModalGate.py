from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


class VisibleThing(Protocol):
    visible: bool


@dataclass
class ModalGate:
    modals: list[VisibleThing]

    def is_blocking(self) -> bool:
        return any(m.visible for m in self.modals)
