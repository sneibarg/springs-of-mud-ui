from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


class KeySource(Protocol):
    def btnp(self, key: int, hold: int = 0, period: int = 0) -> bool: ...
    def btn(self, key: int) -> bool: ...


@dataclass(frozen=True)
class PyxelKeySource:
    """Default KeySource backed by pyxel (kept in component package)."""
    def btnp(self, key: int, hold: int = 0, period: int = 0) -> bool:
        import pyxel
        if hold or period:
            return pyxel.btnp(key, hold=hold, repeat=period)
        return pyxel.btnp(key)

    def btn(self, key: int) -> bool:
        import pyxel
        return pyxel.btn(key)
