"""
Window management abstraction for the component package.
Provides a protocol for window operations that can be implemented by different game engines.
"""
from __future__ import annotations
from typing import Protocol


class Window(Protocol):
    """Protocol for window management."""

    def get_size(self) -> tuple[int, int]:
        """Get the current window size (width, height)."""
        ...

    def set_title(self, title: str) -> None:
        """Set the window title."""
        ...

    def set_fps(self, fps: int) -> None:
        """Set the target frames per second."""
        ...

    def quit(self) -> None:
        """Close the window and quit the application."""
        ...

    def is_running(self) -> bool:
        """Check if the window is still running."""
        ...


class PyxelWindow:
    """Default Window implementation backed by Pyxel."""

    def __init__(self, width: int, height: int, title: str = "Game", fps: int = 60, display_scale: int = 1):
        """
        Initialize the Pyxel window.

        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
            fps: Target frames per second
            display_scale: Display scaling factor
        """
        import pyxel
        self._width = width
        self._height = height
        self._title = title
        self._fps = fps
        pyxel.init(width, height, title=title, fps=fps, display_scale=display_scale)
        pyxel.mouse(True)

    def get_size(self) -> tuple[int, int]:
        return (self._width, self._height)

    def set_title(self, title: str) -> None:
        self._title = title
        # Note: Pyxel doesn't support changing title after init

    def set_fps(self, fps: int) -> None:
        self._fps = fps
        # Note: Pyxel doesn't support changing FPS after init

    def quit(self) -> None:
        import pyxel
        pyxel.quit()

    def is_running(self) -> bool:
        # Pyxel doesn't expose this, assume always running
        return True
