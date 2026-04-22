"""
Animation playback controller.

Manages the playback state and timing for a single Animation.
"""
from component.animation.core.Animation import Animation
from component.animation.core.Frame import Frame


class AnimationController:
    """
    Controls playback of an Animation.

    Handles:
    - Play/pause/reset functionality
    - Playback speed control
    - Time tracking
    - Non-looping animation completion
    - Frame retrieval at current time
    """

    def __init__(self, animation: Animation, autoplay: bool = True):
        """
        Initialize animation controller.

        Args:
            animation: Animation to control
            autoplay: Whether to start playing immediately (default: True)
        """
        self.animation = animation
        self.time = 0.0
        self.playing = autoplay
        self.speed = 1.0
        self._finished = False

    def update(self, delta_time: float) -> None:
        """
        Update animation time.

        Args:
            delta_time: Time elapsed since last update (in seconds)
        """
        if not self.playing:
            return

        # Advance time with speed modifier
        self.time += delta_time * self.speed

        # Handle non-looping animations
        if not self.animation.loop:
            duration = self.animation.duration()
            if self.time >= duration:
                self.time = duration
                self.playing = False
                self._finished = True

    def get_current_frame(self) -> Frame:
        """
        Get the frame at current playback time.

        Returns:
            Current Frame based on playback time
        """
        return self.animation.get_frame_at(self.time)

    def get_current_frame_index(self) -> int:
        """
        Get the index of the current frame.

        Returns:
            Current frame index (0-based)
        """
        return self.animation.get_frame_index_at(self.time)

    def play(self) -> None:
        """Start or resume playback."""
        self.playing = True

    def pause(self) -> None:
        """Pause playback (time is preserved)."""
        self.playing = False

    def stop(self) -> None:
        """Stop playback and reset to beginning."""
        self.playing = False
        self.reset()

    def reset(self) -> None:
        """Reset playback time to 0."""
        self.time = 0.0
        self._finished = False

    def is_playing(self) -> bool:
        """
        Check if animation is currently playing.

        Returns:
            True if playing, False if paused or stopped
        """
        return self.playing

    def is_finished(self) -> bool:
        """
        Check if non-looping animation has finished.

        For looping animations, always returns False.

        Returns:
            True if animation is non-looping and has completed
        """
        return self._finished

    def set_animation(self, animation: Animation, reset_time: bool = True) -> None:
        """
        Change the current animation.

        Args:
            animation: New animation to play
            reset_time: Whether to reset time to 0 (default: True)
        """
        self.animation = animation
        self._finished = False
        if reset_time:
            self.reset()

    def set_speed(self, speed: float) -> None:
        """
        Set playback speed multiplier.

        Args:
            speed: Speed multiplier (1.0 = normal, 2.0 = double speed, 0.5 = half speed)
        """
        if speed <= 0:
            raise ValueError(f"Speed must be positive, got {speed}")
        self.speed = speed

    def set_time(self, time: float) -> None:
        """
        Set playback time directly.

        Args:
            time: Time to set (in seconds)
        """
        if time < 0:
            raise ValueError(f"Time cannot be negative, got {time}")
        self.time = time
        self._finished = False

    def get_progress(self) -> float:
        """
        Get playback progress as a ratio.

        Returns:
            Progress from 0.0 to 1.0 (clamped)
        """
        duration = self.animation.duration()
        if duration == 0:
            return 0.0
        return min(1.0, self.time / duration)
