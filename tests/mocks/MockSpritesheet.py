"""
Mock Spritesheet implementation for testing animation components.
"""
from __future__ import annotations
from typing import List, Tuple, Dict
from component.animation.core import SpriteSheet
from component.animation.core import Frame


class MockSpritesheet(SpriteSheet):
    """
    Mock implementation of a spritesheet for testing.
    Records all drawing operations and provides test helpers.
    """

    def __init__(self, width: int = 256, height: int = 256):
        """
        Initialize mock spritesheet.

        Args:
            width: Width of the spritesheet in pixels
            height: Height of the spritesheet in pixels
        """
        self.width = width
        self.height = height
        self.draw_calls: List[Tuple[str, dict]] = []
        self._frames: Dict[Tuple[int, int, int, int], Frame] = {}

    def get_frame(self, x: int, y: int, w: int, h: int, duration: float = 0.1) -> Frame:
        """
        Get a frame from the spritesheet.

        Args:
            x: X position in spritesheet
            y: Y position in spritesheet
            w: Frame width
            h: Frame height
            duration: Frame duration

        Returns:
            Frame object
        """
        key = (x, y, w, h, duration)
        if key not in self._frames:
            self._frames[key] = Frame(
                sprite_x=x,
                sprite_y=y,
                width=w,
                height=h,
                duration=duration
            )
        return self._frames[key]

    def draw_frame(self, ctx, frame: Frame, x: int, y: int) -> None:
        """
        Draw a frame (records the call for testing).

        Args:
            ctx: Engine context (can be None for testing)
            frame: Frame to draw
            x: Screen X position
            y: Screen Y position
        """
        self.draw_calls.append(('draw_frame', {
            'frame': frame,
            'x': x,
            'y': y,
            'sprite_x': frame.sprite_x,
            'sprite_y': frame.sprite_y,
            'width': frame.width,
            'height': frame.height,
            'flip_h': frame.flip_h,
            'flip_v': frame.flip_v
        }))

    def clear_calls(self) -> None:
        """Clear recorded draw calls."""
        self.draw_calls = []

    def get_draw_count(self) -> int:
        """Get number of draw calls."""
        return len(self.draw_calls)

    def assert_frame_drawn(self, frame: Frame, x: int, y: int) -> None:
        """
        Assert that a specific frame was drawn at a position.

        Args:
            frame: Expected frame
            x: Expected X position
            y: Expected Y position

        Raises:
            AssertionError: If frame was not drawn as expected
        """
        for call_type, call_data in self.draw_calls:
            if (call_type == 'draw_frame' and
                call_data['frame'] == frame and
                call_data['x'] == x and
                call_data['y'] == y):
                return

        raise AssertionError(
            f"Frame not found: expected {frame} at ({x}, {y}), "
            f"got {len(self.draw_calls)} draw calls"
        )

    def get_last_draw(self) -> dict | None:
        """
        Get the last draw call data.

        Returns:
            Dictionary of last draw call data, or None if no calls
        """
        if not self.draw_calls:
            return None
        return self.draw_calls[-1][1]

    def create_test_frames(self, count: int, duration: float = 0.1) -> List[Frame]:
        """
        Create a list of test frames in a horizontal strip.

        Args:
            count: Number of frames to create
            duration: Duration for each frame

        Returns:
            List of Frame objects
        """
        frames = []
        frame_width = self.width // count

        for i in range(count):
            frame = Frame(
                sprite_x=i * frame_width,
                sprite_y=0,
                width=frame_width,
                height=32,  # Standard test height
                duration=duration,
                metadata={'index': i, 'test': True}
            )
            frames.append(frame)

        return frames
