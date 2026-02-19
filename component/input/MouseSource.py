"""
Mouse input abstraction for the component package.
Provides a protocol for mouse input that can be implemented by different game engines.
"""
from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass


class MouseSource(Protocol):
    """Protocol for mouse input sources."""

    def get_position(self) -> tuple[int, int]:
        """Get the current mouse position (x, y)."""
        ...

    def is_button_pressed(self, button: int) -> bool:
        """Check if a mouse button was just pressed this frame."""
        ...

    def is_button_down(self, button: int) -> bool:
        """Check if a mouse button is currently held down."""
        ...

    def get_wheel_delta(self) -> int:
        """Get the mouse wheel scroll delta (positive=up, negative=down)."""
        ...


@dataclass(frozen=True)
class PyxelMouseSource:
    """Default MouseSource backed by Pyxel."""

    def get_position(self) -> tuple[int, int]:
        import pyxel
        return (pyxel.mouse_x, pyxel.mouse_y)

    def is_button_pressed(self, button: int) -> bool:
        import pyxel
        return pyxel.btnp(button)

    def is_button_down(self, button: int) -> bool:
        import pyxel
        return pyxel.btn(button)

    def get_wheel_delta(self) -> int:
        import pyxel
        return pyxel.mouse_wheel
