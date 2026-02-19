"""
Mock Graphics implementation for testing.
Records all graphics calls for verification in tests.
"""
from __future__ import annotations
from typing import List, Tuple, Any


class MockGraphics:
    """
    Mock implementation of the Graphics protocol.
    Records all method calls for verification in unit tests.
    """

    def __init__(self):
        """Initialize the mock graphics with an empty call log."""
        self.calls: List[Tuple[str, Any]] = []
        self._clip_stack: List[Tuple[int, int, int, int]] = []

    def clear_calls(self) -> None:
        """Clear the recorded calls."""
        self.calls = []

    def get_calls(self, method_name: str | None = None) -> List[Tuple[str, Any]]:
        """
        Get recorded calls, optionally filtered by method name.

        Args:
            method_name: If provided, only return calls to this method

        Returns:
            List of (method_name, args) tuples
        """
        if method_name:
            return [call for call in self.calls if call[0] == method_name]
        return self.calls

    def cls(self, col: int) -> None:
        """Clear screen with color."""
        self.calls.append(('cls', (col,)))

    def clip(self, x: int, y: int, w: int, h: int) -> None:
        """Set clipping region."""
        self.calls.append(('clip', (x, y, w, h)))
        self._clip_stack.append((x, y, w, h))

    def clip_reset(self) -> None:
        """Reset clipping region."""
        self.calls.append(('clip_reset', ()))
        if self._clip_stack:
            self._clip_stack.pop()

    def pset(self, x: int, y: int, col: int) -> None:
        """Draw a pixel."""
        self.calls.append(('pset', (x, y, col)))

    def line(self, x1: int, y1: int, x2: int, y2: int, col: int) -> None:
        """Draw a line."""
        self.calls.append(('line', (x1, y1, x2, y2, col)))

    def rect(self, x: int, y: int, w: int, h: int, col: int) -> None:
        """Draw a filled rectangle."""
        self.calls.append(('rect', (x, y, w, h, col)))

    def rectb(self, x: int, y: int, w: int, h: int, col: int) -> None:
        """Draw a rectangle border."""
        self.calls.append(('rectb', (x, y, w, h, col)))

    def circ(self, x: int, y: int, r: int, col: int) -> None:
        """Draw a filled circle."""
        self.calls.append(('circ', (x, y, r, col)))

    def circb(self, x: int, y: int, r: int, col: int) -> None:
        """Draw a circle border."""
        self.calls.append(('circb', (x, y, r, col)))

    def elli(self, x: int, y: int, rx: int, ry: int, col: int) -> None:
        """Draw a filled ellipse."""
        self.calls.append(('elli', (x, y, rx, ry, col)))

    def ellib(self, x: int, y: int, rx: int, ry: int, col: int) -> None:
        """Draw an ellipse border."""
        self.calls.append(('ellib', (x, y, rx, ry, col)))

    def tri(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, col: int) -> None:
        """Draw a filled triangle."""
        self.calls.append(('tri', (x1, y1, x2, y2, x3, y3, col)))

    def trib(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, col: int) -> None:
        """Draw a triangle border."""
        self.calls.append(('trib', (x1, y1, x2, y2, x3, y3, col)))

    def text(self, x: int, y: int, s: str, col: int) -> None:
        """Draw text."""
        self.calls.append(('text', (x, y, s, col)))

    # Helper methods for testing
    def assert_called_with(self, method_name: str, *args) -> None:
        """Assert that a method was called with specific arguments."""
        matching_calls = [call for call in self.calls if call[0] == method_name and call[1] == args]
        if not matching_calls:
            raise AssertionError(
                f"Expected call to {method_name}{args}, but not found in {self.get_calls(method_name)}"
            )

    def assert_rect_drawn(self, x: int, y: int, w: int, h: int, col: int) -> None:
        """Assert that a rectangle was drawn with specific parameters."""
        self.assert_called_with('rect', x, y, w, h, col)

    def assert_text_drawn(self, x: int, y: int, text: str, col: int) -> None:
        """Assert that text was drawn with specific parameters."""
        self.assert_called_with('text', x, y, text, col)
