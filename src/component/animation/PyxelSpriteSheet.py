from component.animation.core.SpriteSheet import SpriteSheet
from component.animation.core.Frame import Frame

import pyxel


class PyxelSpriteSheet(SpriteSheet):
    """
    SpriteSheet implementation using Pyxel's image banks.

    Pyxel supports up to 3 image banks (0, 1, 2), each can be 256x256 pixels.
    """

    def __init__(self, image_bank: int, color_key: int = 0):
        """
        Initialize a Pyxel sprite sheet.

        Args:
            image_bank: Pyxel image bank number (0, 1, or 2)
            color_key: Transparent color index (default: 0 = black)
        """
        if image_bank not in (0, 1, 2):
            raise ValueError(f"Pyxel image bank must be 0, 1, or 2, got {image_bank}")

        self.image_bank = image_bank
        self.color_key = color_key

    def get_frame(self, x: int, y: int, w: int, h: int, duration: float = 0.1) -> Frame:
        """
        Create a Frame from sprite sheet coordinates.

        Args:
            x: X coordinate in sprite sheet
            y: Y coordinate in sprite sheet
            w: Width of the frame
            h: Height of the frame
            duration: Default duration for this frame

        Returns:
            Frame object with specified bounds
        """
        return Frame(
            sprite_x=x,
            sprite_y=y,
            width=w,
            height=h,
            duration=duration
        )

    def draw_frame(self, ctx, frame: Frame, x: int, y: int) -> None:
        """
        Draw a frame using Pyxel's blt (block transfer) function.

        Handles:
        - Drawing offsets (frame.offset_x, frame.offset_y)
        - Horizontal/vertical flipping (negative width/height in Pyxel)
        - Color key transparency

        Args:
            ctx: Graphics context (unused, Pyxel draws directly)
            frame: Frame to draw
            x: X position on screen
            y: Y position on screen
        """
        draw_x = x + frame.offset_x
        draw_y = y + frame.offset_y

        draw_width = frame.width * (-1 if frame.flip_h else 1)
        draw_height = frame.height * (-1 if frame.flip_v else 1)

        pyxel.blt(
            draw_x,
            draw_y,
            self.image_bank,
            frame.sprite_x,
            frame.sprite_y,
            draw_width,
            draw_height,
            colkey=self.color_key
        )
