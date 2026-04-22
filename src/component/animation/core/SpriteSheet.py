"""
Abstract base class for sprite sheet management.

A SpriteSheet handles loading and drawing sprite frames from image data.
"""
from abc import ABC, abstractmethod
from component.animation.core.Frame import Frame


class SpriteSheet(ABC):
    """
    Abstract base class for sprite sheet implementations.

    A SpriteSheet is responsible for:
    - Creating Frame objects from sprite coordinates
    - Drawing frames to the screen with proper transformations
    - Providing convenient access to tile-based sprites
    """

    @abstractmethod
    def get_frame(self, x: int, y: int, w: int, h: int, duration: float = 0.1) -> Frame:
        """
        Create a Frame object from sprite sheet coordinates.

        Args:
            x: X coordinate in sprite sheet
            y: Y coordinate in sprite sheet
            w: Width of the frame
            h: Height of the frame
            duration: Default duration for this frame (can be overridden in Animation)

        Returns:
            Frame object with specified bounds
        """
        pass

    @abstractmethod
    def draw_frame(self, ctx, frame: Frame, x: int, y: int) -> None:
        """
        Draw a frame to the screen with all transformations applied.

        Handles:
        - Drawing offsets (frame.offset_x, frame.offset_y)
        - Horizontal/vertical flipping (frame.flip_h, frame.flip_v)
        - Color key transparency

        Args:
            ctx: Graphics context (contains gfx abstraction)
            frame: Frame to draw
            x: X position on screen
            y: Y position on screen
        """
        pass

    def get_tile(self, tile_x: int, tile_y: int, tile_size: int, duration: float = 0.1) -> Frame:
        """
        Convenience method for tile-based sprite sheets.

        For sprite sheets organized in a grid, this converts tile coordinates
        to pixel coordinates and creates a Frame.

        Args:
            tile_x: Tile column (0-indexed)
            tile_y: Tile row (0-indexed)
            tile_size: Size of each tile in pixels
            duration: Default duration for this frame

        Returns:
            Frame object for the specified tile
        """
        return self.get_frame(
            tile_x * tile_size,
            tile_y * tile_size,
            tile_size,
            tile_size,
            duration
        )

    def get_frames_strip(self, x: int, y: int, w: int, h: int, count: int, duration: float = 0.1) -> list[Frame]:
        """
        Get a horizontal strip of frames (common for animations).

        Args:
            x: Starting X coordinate
            y: Y coordinate
            w: Width of each frame
            h: Height of each frame
            count: Number of frames in the strip
            duration: Duration for each frame

        Returns:
            List of Frame objects
        """
        return [
            self.get_frame(x + (i * w), y, w, h, duration)
            for i in range(count)
        ]

    def get_frames_grid(self, x: int, y: int, w: int, h: int, cols: int, rows: int, duration: float = 0.1) -> list[Frame]:
        """
        Get a grid of frames (common for sprite sheets).

        Frames are returned in row-major order (left to right, top to bottom).

        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            w: Width of each frame
            h: Height of each frame
            cols: Number of columns
            rows: Number of rows
            duration: Duration for each frame

        Returns:
            List of Frame objects in row-major order
        """
        frames = []
        for row in range(rows):
            for col in range(cols):
                frames.append(
                    self.get_frame(x + (col * w), y + (row * h), w, h, duration)
                )
        return frames
