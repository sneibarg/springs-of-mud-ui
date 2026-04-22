"""
Animated sprite implementation.

Combines a SpriteSheet with multiple Animations and an AnimationController
to create a fully-featured animated sprite.
"""
from __future__ import annotations
from typing import Callable
from component.animation.core.SpriteSheet import SpriteSheet
from component.animation.core.AnimationController import AnimationController
from component.animation.core.Animation import Animation
from component.animation.core.Frame import Frame


class AnimatedSprite:
    """
    A sprite with animation support.

    Features:
    - Multiple named animations
    - Position management (x, y)
    - Animation switching with optional callbacks
    - Velocity support for movement
    - Visibility control
    - Integration with AnimationController
    """

    def __init__(
        self,
        spritesheet: SpriteSheet,
        x: float = 0,
        y: float = 0,
        animations: dict[str, Animation] | None = None
    ):
        """
        Initialize animated sprite.

        Args:
            spritesheet: SpriteSheet to draw frames from
            x: Initial X position
            y: Initial Y position
            animations: Dictionary of named animations
        """
        self.spritesheet = spritesheet
        self.x = x
        self.y = y
        self.animations = animations or {}
        self.controller: AnimationController | None = None
        self.current_animation: str | None = None

        # Movement
        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0

        # Visibility
        self.visible: bool = True

        # Animation change callback
        self._on_animation_changed: Callable[[str, str | None], None] | None = None

    def add_animation(self, name: str, animation: Animation) -> None:
        """
        Add a named animation.

        Args:
            name: Animation name (used with play())
            animation: Animation object

        Raises:
            ValueError: If animation name is empty
        """
        if not name:
            raise ValueError("Animation name cannot be empty")
        self.animations[name] = animation

    def has_animation(self, name: str) -> bool:
        """
        Check if animation exists.

        Args:
            name: Animation name

        Returns:
            True if animation exists, False otherwise
        """
        return name in self.animations

    def play(self, name: str, restart: bool = False) -> None:
        """
        Play a named animation.

        Args:
            name: Animation name
            restart: If True, restart animation even if already playing

        Raises:
            ValueError: If animation not found
        """
        if name not in self.animations:
            raise ValueError(f"Animation '{name}' not found")

        # Check if we need to change animation
        if self.current_animation != name or restart:
            old_animation = self.current_animation
            self.current_animation = name
            self.controller = AnimationController(self.animations[name])
            self.controller.play()

            # Trigger callback
            if self._on_animation_changed:
                self._on_animation_changed(name, old_animation)

    def stop(self) -> None:
        """Stop current animation and reset to first frame."""
        if self.controller:
            self.controller.stop()

    def pause(self) -> None:
        """Pause current animation (preserves time)."""
        if self.controller:
            self.controller.pause()

    def resume(self) -> None:
        """Resume paused animation."""
        if self.controller:
            self.controller.play()

    def update(self, delta_time: float) -> None:
        """
        Update sprite animation and position.

        Args:
            delta_time: Time elapsed since last update (in seconds)
        """
        # Update animation
        if self.controller:
            self.controller.update(delta_time)

        # Update position with velocity
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

    def draw(self, ctx) -> None:
        """
        Draw sprite at current position.

        Args:
            ctx: Graphics context
        """
        if not self.visible:
            return

        if self.controller:
            frame = self.controller.get_current_frame()
            self.spritesheet.draw_frame(ctx, frame, int(self.x), int(self.y))

    def get_current_frame(self) -> Frame | None:
        """
        Get current animation frame.

        Returns:
            Current Frame, or None if no animation playing
        """
        if self.controller:
            return self.controller.get_current_frame()
        return None

    def is_playing(self) -> bool:
        """
        Check if animation is currently playing.

        Returns:
            True if playing, False otherwise
        """
        return self.controller is not None and self.controller.is_playing()

    def is_finished(self) -> bool:
        """
        Check if current non-looping animation has finished.

        Returns:
            True if animation finished, False otherwise
        """
        return self.controller is not None and self.controller.is_finished()

    def set_position(self, x: float, y: float) -> None:
        """
        Set sprite position.

        Args:
            x: X position
            y: Y position
        """
        self.x = x
        self.y = y

    def set_velocity(self, vx: float, vy: float) -> None:
        """
        Set sprite velocity.

        Args:
            vx: X velocity (pixels per second)
            vy: Y velocity (pixels per second)
        """
        self.velocity_x = vx
        self.velocity_y = vy

    def set_speed(self, speed: float) -> None:
        """
        Set animation playback speed.

        Args:
            speed: Speed multiplier
        """
        if self.controller:
            self.controller.set_speed(speed)

    def on_animation_changed(self, callback: Callable[[str, str | None], None]) -> None:
        """
        Register callback for animation changes.

        Callback signature: callback(new_animation: str, old_animation: str | None)

        Args:
            callback: Function to call when animation changes
        """
        self._on_animation_changed = callback
