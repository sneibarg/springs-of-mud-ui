"""
Mock MouseSource implementation for testing.
Allows simulating mouse input in tests.
"""
from __future__ import annotations
from typing import Set


class MockMouseSource:
    """
    Mock implementation of the MouseSource protocol.
    Allows programmatic control of mouse state for testing.
    """

    def __init__(self, x: int = 0, y: int = 0):
        """
        Initialize the mock mouse source.

        Args:
            x: Initial mouse x position
            y: Initial mouse y position
        """
        self._x = x
        self._y = y
        self._pressed_buttons: Set[int] = set()  # Buttons pressed this frame
        self._down_buttons: Set[int] = set()     # Buttons currently held down
        self._wheel_delta = 0

    def get_position(self) -> tuple[int, int]:
        """Get the current mouse position."""
        return (self._x, self._y)

    def is_button_pressed(self, button: int) -> bool:
        """Check if a mouse button was just pressed this frame."""
        return button in self._pressed_buttons

    def is_button_down(self, button: int) -> bool:
        """Check if a mouse button is currently held down."""
        return button in self._down_buttons

    def get_wheel_delta(self) -> int:
        """Get the mouse wheel scroll delta."""
        return self._wheel_delta

    # Test helper methods
    def set_position(self, x: int, y: int) -> None:
        """
        Set the mouse position.

        Args:
            x: New x position
            y: New y position
        """
        self._x = x
        self._y = y

    def move_to(self, x: int, y: int) -> None:
        """Alias for set_position."""
        self.set_position(x, y)

    def move_by(self, dx: int, dy: int) -> None:
        """
        Move the mouse by a relative amount.

        Args:
            dx: Change in x
            dy: Change in y
        """
        self._x += dx
        self._y += dy

    def press_button(self, button: int) -> None:
        """
        Simulate pressing a mouse button.

        Args:
            button: Button code (0=left, 1=right, 2=middle)
        """
        self._pressed_buttons.add(button)
        self._down_buttons.add(button)

    def release_button(self, button: int) -> None:
        """
        Simulate releasing a mouse button.

        Args:
            button: Button code to release
        """
        self._pressed_buttons.discard(button)
        self._down_buttons.discard(button)

    def click(self, button: int = 0) -> None:
        """
        Simulate a click (press and release in same frame).

        Args:
            button: Button code to click
        """
        self.press_button(button)

    def set_wheel_delta(self, delta: int) -> None:
        """
        Set the wheel scroll delta.

        Args:
            delta: Wheel delta (positive=up, negative=down)
        """
        self._wheel_delta = delta

    def scroll_up(self, amount: int = 1) -> None:
        """Simulate scrolling up."""
        self._wheel_delta = amount

    def scroll_down(self, amount: int = 1) -> None:
        """Simulate scrolling down."""
        self._wheel_delta = -amount

    def clear_pressed(self) -> None:
        """Clear pressed buttons (simulating end of frame)."""
        self._pressed_buttons.clear()
        self._wheel_delta = 0

    def clear_all(self) -> None:
        """Clear all mouse state."""
        self._pressed_buttons.clear()
        self._down_buttons.clear()
        self._wheel_delta = 0
