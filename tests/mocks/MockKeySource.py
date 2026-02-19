"""
Mock KeySource implementation for testing.
Allows simulating keyboard input in tests.
"""
from __future__ import annotations
from typing import Dict, Set


class MockKeySource:
    """
    Mock implementation of the KeySource protocol.
    Allows programmatic control of key states for testing.
    """

    def __init__(self):
        """Initialize the mock key source."""
        self._pressed_keys: Set[int] = set()  # Keys pressed this frame
        self._down_keys: Set[int] = set()     # Keys currently held down
        self._key_press_counts: Dict[int, int] = {}  # Track press counts for repeat

    def btnp(self, key: int, hold: int = 0, period: int = 0) -> bool:
        """
        Check if a key was just pressed.

        Args:
            key: Key code to check
            hold: Frames to hold before repeat (not fully implemented in mock)
            period: Repeat period (not fully implemented in mock)

        Returns:
            True if the key was pressed this frame
        """
        return key in self._pressed_keys

    def btn(self, key: int) -> bool:
        """
        Check if a key is currently held down.

        Args:
            key: Key code to check

        Returns:
            True if the key is currently held
        """
        return key in self._down_keys

    # Test helper methods
    def press_key(self, key: int) -> None:
        """
        Simulate pressing a key (single frame press).

        Args:
            key: Key code to press
        """
        self._pressed_keys.add(key)
        self._down_keys.add(key)

    def release_key(self, key: int) -> None:
        """
        Simulate releasing a key.

        Args:
            key: Key code to release
        """
        self._pressed_keys.discard(key)
        self._down_keys.discard(key)

    def hold_key(self, key: int) -> None:
        """
        Simulate holding a key down (without triggering btnp).

        Args:
            key: Key code to hold
        """
        self._down_keys.add(key)

    def clear_pressed(self) -> None:
        """Clear all pressed keys (simulating end of frame)."""
        self._pressed_keys.clear()

    def clear_all(self) -> None:
        """Clear all key states."""
        self._pressed_keys.clear()
        self._down_keys.clear()
        self._key_press_counts.clear()

    def is_pressed(self, key: int) -> bool:
        """Check if a key was pressed this frame (alias for testing)."""
        return key in self._pressed_keys

    def is_down(self, key: int) -> bool:
        """Check if a key is held down (alias for testing)."""
        return key in self._down_keys
