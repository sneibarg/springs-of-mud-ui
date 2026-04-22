"""
Procedural Generator for creating animation frames algorithmically.

This module provides a comprehensive set of procedural animation generation methods
including walk cycles, bounces, spins, fades, scales, shakes, and slides.
"""
from component.animation.core import SpriteSheet, Frame
import math


class ProceduralGenerator:
    """
    Generates animation frames procedurally using algorithms.

    Implements the FrameGenerator protocol for creating frames based on
    mathematical patterns and animation principles.
    """

    def generate(self, description: str, **kwargs) -> list[Frame]:
        """
        Generate frames based on a description string.

        Args:
            description: Animation type identifier (e.g., "walk_cycle", "bounce", "spin")
            **kwargs: Additional parameters specific to the animation type

        Returns:
            List of Frame objects

        Raises:
            ValueError: If description is not recognized
        """
        description = description.lower().strip()

        generators = {
            "walk_cycle": self.generate_walk_cycle,
            "bounce": self.generate_bounce,
            "spin": self.generate_spin,
            "fade_in": self.generate_fade_in,
            "fade_out": self.generate_fade_out,
            "scale": self.generate_scale,
            "pulse": self.generate_pulse,
            "shake": self.generate_shake,
            "slide": self.generate_slide,
        }

        if description not in generators:
            raise ValueError(f"Unknown animation type: {description}. Available: {', '.join(generators.keys())}")

        return generators[description](**kwargs)

    def generate_walk_cycle(self, spritesheet: SpriteSheet = None, start_x: int = 0, start_y: int = 0,
                            frame_count: int = 4, frame_width: int = 32, frame_height: int = 32,
                            frame_duration: float = 0.1) -> list[Frame]:
        """
        Generate a walk cycle animation from a sprite sheet.

        Args:
            spritesheet: Source sprite sheet (optional, for validation)
            start_x: Starting x coordinate in sprite sheet
            start_y: Starting y coordinate in sprite sheet
            frame_count: Number of frames in the walk cycle
            frame_width: Width of each frame
            frame_height: Height of each frame
            frame_duration: Duration of each frame in seconds

        Returns:
            List of Frame objects representing the walk cycle
        """
        frames = []
        for i in range(frame_count):
            frames.append(Frame(
                sprite_x=start_x + i * frame_width,
                sprite_y=start_y,
                width=frame_width,
                height=frame_height,
                duration=frame_duration,
                metadata={"frame_type": "walk", "step": i}
            ))
        return frames

    def generate_bounce(self, base_frame: Frame, bounce_height: int = 10, frame_count: int = 8,
                       frame_duration: float = 0.05) -> list[Frame]:
        """
        Generate a bounce animation using a sine wave pattern.

        Args:
            base_frame: The base frame to apply bounce effect to
            bounce_height: Maximum vertical displacement in pixels
            frame_count: Number of frames in the bounce
            frame_duration: Duration of each frame in seconds

        Returns:
            List of Frame objects with varying offset_y values
        """
        frames = []
        for i in range(frame_count):
            # Use (frame_count - 1) to ensure last frame reaches t=1.0
            t = i / (frame_count - 1) if frame_count > 1 else 0.0
            offset_y = int(math.sin(t * math.pi) * bounce_height)
            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                offset_y=-offset_y,
                metadata={"frame_type": "bounce", "step": i}
            )
            frames.append(frame)
        return frames

    def generate_spin(self, base_frame: Frame, frame_count: int = 8, frame_duration: float = 0.05,
                     clockwise: bool = True) -> list[Frame]:
        """
        Generate a spin/rotation animation.

        Creates frames with horizontal and vertical flips to simulate rotation.

        Args:
            base_frame: The base frame to rotate
            frame_count: Number of frames in the rotation (minimum 4)
            frame_duration: Duration of each frame in seconds
            clockwise: Direction of rotation

        Returns:
            List of Frame objects with flip_h and flip_v variations
        """
        if frame_count < 4:
            frame_count = 4

        frames = []
        steps_per_quarter = max(1, frame_count // 4)

        for i in range(frame_count):
            quarter = (i // steps_per_quarter) % 4

            # Determine flip states based on rotation quarter
            if clockwise:
                flip_h = quarter in [1, 2]
                flip_v = quarter in [2, 3]
            else:
                flip_h = quarter in [0, 3]
                flip_v = quarter in [1, 2]

            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                flip_h=flip_h,
                flip_v=flip_v,
                metadata={"frame_type": "spin", "step": i, "clockwise": clockwise}
            )
            frames.append(frame)

        return frames

    def generate_fade_in(self, base_frame: Frame, frame_count: int = 10,
                        frame_duration: float = 0.05) -> list[Frame]:
        """
        Generate a fade-in animation.

        Uses metadata to store alpha values that can be used during rendering.

        Args:
            base_frame: The base frame to fade in
            frame_count: Number of frames in the fade
            frame_duration: Duration of each frame in seconds

        Returns:
            List of Frame objects with increasing alpha values in metadata
        """
        frames = []
        for i in range(frame_count):
            alpha = i / (frame_count - 1) if frame_count > 1 else 1.0
            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                metadata={"frame_type": "fade_in", "step": i, "alpha": alpha}
            )
            frames.append(frame)
        return frames

    def generate_fade_out(self, base_frame: Frame, frame_count: int = 10,
                         frame_duration: float = 0.05) -> list[Frame]:
        """
        Generate a fade-out animation.

        Uses metadata to store alpha values that can be used during rendering.

        Args:
            base_frame: The base frame to fade out
            frame_count: Number of frames in the fade
            frame_duration: Duration of each frame in seconds

        Returns:
            List of Frame objects with decreasing alpha values in metadata
        """
        frames = []
        for i in range(frame_count):
            alpha = 1.0 - (i / (frame_count - 1) if frame_count > 1 else 0.0)
            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                metadata={"frame_type": "fade_out", "step": i, "alpha": alpha}
            )
            frames.append(frame)
        return frames

    def generate_scale(self, base_frame: Frame, start_scale: float = 0.5, end_scale: float = 1.5,
                      frame_count: int = 10, frame_duration: float = 0.05) -> list[Frame]:
        """
        Generate a scale animation.

        Uses metadata to store scale values that can be used during rendering.

        Args:
            base_frame: The base frame to scale
            start_scale: Starting scale factor
            end_scale: Ending scale factor
            frame_count: Number of frames in the animation
            frame_duration: Duration of each frame in seconds

        Returns:
            List of Frame objects with varying scale values in metadata
        """
        frames = []
        for i in range(frame_count):
            t = i / (frame_count - 1) if frame_count > 1 else 1.0
            scale = start_scale + (end_scale - start_scale) * t
            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                metadata={"frame_type": "scale", "step": i, "scale": scale}
            )
            frames.append(frame)
        return frames

    def generate_pulse(self, base_frame: Frame, min_scale: float = 0.9, max_scale: float = 1.1,
                      frame_count: int = 10, frame_duration: float = 0.05, cycles: int = 1) -> list[Frame]:
        """
        Generate a pulse animation using a sine wave for scale.

        Args:
            base_frame: The base frame to pulse
            min_scale: Minimum scale factor
            max_scale: Maximum scale factor
            frame_count: Number of frames in the animation
            frame_duration: Duration of each frame in seconds
            cycles: Number of complete pulse cycles

        Returns:
            List of Frame objects with pulsing scale values in metadata
        """
        frames = []
        for i in range(frame_count):
            t = (i / frame_count) * cycles * 2 * math.pi
            scale = min_scale + (max_scale - min_scale) * (0.5 + 0.5 * math.sin(t))
            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                metadata={"frame_type": "pulse", "step": i, "scale": scale}
            )
            frames.append(frame)
        return frames

    def generate_shake(self, base_frame: Frame, shake_amount: int = 3, frame_count: int = 10,
                      frame_duration: float = 0.03) -> list[Frame]:
        """
        Generate a shake/jitter animation.

        Creates random-looking but deterministic offsets for a shake effect.

        Args:
            base_frame: The base frame to shake
            shake_amount: Maximum pixel offset in any direction
            frame_count: Number of frames in the shake
            frame_duration: Duration of each frame in seconds

        Returns:
            List of Frame objects with varying offset_x and offset_y values
        """
        frames = []
        for i in range(frame_count):
            # Use sine waves with different frequencies for pseudo-random but smooth shake
            offset_x = int(math.sin(i * 1.7) * shake_amount)
            offset_y = int(math.cos(i * 2.3) * shake_amount)

            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                offset_x=offset_x,
                offset_y=offset_y,
                metadata={"frame_type": "shake", "step": i}
            )
            frames.append(frame)
        return frames

    def generate_slide(self, base_frame: Frame, start_x: int = -100, start_y: int = 0,
                      end_x: int = 0, end_y: int = 0, frame_count: int = 15,
                      frame_duration: float = 0.05, easing: str = "linear") -> list[Frame]:
        """
        Generate a slide animation from one position to another.

        Args:
            base_frame: The base frame to slide
            start_x: Starting x offset
            start_y: Starting y offset
            end_x: Ending x offset
            end_y: Ending y offset
            frame_count: Number of frames in the slide
            frame_duration: Duration of each frame in seconds
            easing: Easing function ("linear", "ease_in", "ease_out", "ease_in_out")

        Returns:
            List of Frame objects with interpolated offset values
        """
        frames = []
        for i in range(frame_count):
            t = i / (frame_count - 1) if frame_count > 1 else 1.0

            # Apply easing
            if easing == "ease_in":
                t = t * t
            elif easing == "ease_out":
                t = 1 - (1 - t) * (1 - t)
            elif easing == "ease_in_out":
                t = 3 * t * t - 2 * t * t * t

            offset_x = int(start_x + (end_x - start_x) * t)
            offset_y = int(start_y + (end_y - start_y) * t)

            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=frame_duration,
                offset_x=offset_x,
                offset_y=offset_y,
                metadata={"frame_type": "slide", "step": i, "easing": easing}
            )
            frames.append(frame)
        return frames
