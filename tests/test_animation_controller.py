"""
Comprehensive tests for AnimationController.
"""
import sys
import unittest

sys.path.insert(0, ".")

from component.animation.core import Animation, AnimationController
from tests.mocks import MockSpritesheet


class TestAnimationController(unittest.TestCase):
    # =============================================================================
    # AnimationController Tests
    # =============================================================================

    def test_controller_creation(self):
        """Test creating AnimationController."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("test", frames, loop=True)

        controller = AnimationController(animation)

        self.assertIs(controller.animation, animation)
        self.assertEqual(controller.time, 0.0)
        self.assertIs(controller.playing, True)
        self.assertEqual(controller.speed, 1.0)
        self.assertIs(controller.is_playing(), True)
        print("[PASS] test_controller_creation passed")

    def test_controller_autoplay(self):
        """Test controller autoplay parameter."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=2)
        animation = Animation("test", frames)

        # With autoplay=True (default)
        controller1 = AnimationController(animation)
        self.assertIs(controller1.is_playing(), True)

        # With autoplay=False
        controller2 = AnimationController(animation, autoplay=False)
        self.assertIs(controller2.is_playing(), False)
        print("[PASS] test_controller_autoplay passed")

    def test_controller_update(self):
        """Test controller update advances time."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("test", frames, loop=True)
        controller = AnimationController(animation)

        # Initial time
        self.assertEqual(controller.time, 0.0)

        # Update
        controller.update(0.15)
        self.assertLess(abs(controller.time - 0.15), 0.001)

        # Update again
        controller.update(0.1)
        self.assertLess(abs(controller.time - 0.25), 0.001)
        print("[PASS] test_controller_update passed")

    def test_controller_get_current_frame(self):
        """Test getting current frame."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("test", frames, loop=True)
        controller = AnimationController(animation)

        # At time 0, should be first frame
        frame = controller.get_current_frame()
        self.assertEqual(frame, frames[0])

        # Advance to second frame
        controller.update(0.15)
        frame = controller.get_current_frame()
        self.assertEqual(frame, frames[1])
        print("[PASS] test_controller_get_current_frame passed")

    def test_controller_get_current_frame_index(self):
        """Test getting current frame index."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("test", frames, loop=True)
        controller = AnimationController(animation)

        self.assertEqual(controller.get_current_frame_index(), 0)

        controller.update(0.15)
        self.assertEqual(controller.get_current_frame_index(), 1)

        controller.update(0.1)
        self.assertEqual(controller.get_current_frame_index(), 2)
        print("[PASS] test_controller_get_current_frame_index passed")

    def test_controller_play_pause(self):
        """Test play and pause."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=2, duration=0.1)
        animation = Animation("test", frames)
        controller = AnimationController(animation)

        # Start playing
        self.assertIs(controller.is_playing(), True)

        # Pause
        controller.pause()
        self.assertIs(controller.is_playing(), False)

        # Update should not advance time when paused
        time_before = controller.time
        controller.update(0.1)
        self.assertEqual(controller.time, time_before)

        # Resume
        controller.play()
        self.assertIs(controller.is_playing(), True)

        # Update should advance time
        controller.update(0.1)
        self.assertGreater(controller.time, time_before)
        print("[PASS] test_controller_play_pause passed")

    def test_controller_reset(self):
        """Test reset functionality."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=3, duration=0.1)
        animation = Animation("test", frames)
        controller = AnimationController(animation)

        # Advance time
        controller.update(0.25)
        self.assertGreater(controller.time, 0)

        # Reset
        controller.reset()
        self.assertEqual(controller.time, 0.0)
        self.assertIs(controller.is_finished(), False)
        print("[PASS] test_controller_reset passed")

    def test_controller_stop(self):
        """Test stop functionality."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=3, duration=0.1)
        animation = Animation("test", frames)
        controller = AnimationController(animation)

        # Advance time
        controller.update(0.15)
        self.assertGreater(controller.time, 0)
        self.assertIs(controller.is_playing(), True)

        # Stop
        controller.stop()
        self.assertEqual(controller.time, 0.0)
        self.assertIs(controller.is_playing(), False)
        print("[PASS] test_controller_stop passed")

    def test_controller_looping_animation(self):
        """Test looping animation behavior."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=2, duration=0.1)
        animation = Animation("test", frames, loop=True)
        controller = AnimationController(animation)

        # Advance beyond duration
        controller.update(1.0)

        # Should still be playing
        self.assertIs(controller.is_playing(), True)
        self.assertIs(controller.is_finished(), False)
        print("[PASS] test_controller_looping_animation passed")

    def test_controller_non_looping_animation(self):
        """Test non-looping animation completion."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=2, duration=0.1)
        animation = Animation("test", frames, loop=False)
        controller = AnimationController(animation)

        # Should be playing initially
        self.assertIs(controller.is_playing(), True)
        self.assertIs(controller.is_finished(), False)

        # Advance to middle
        controller.update(0.1)
        self.assertIs(controller.is_playing(), True)
        self.assertIs(controller.is_finished(), False)

        # Advance past end
        controller.update(0.2)

        # Should stop and be finished
        self.assertIs(controller.is_playing(), False)
        self.assertIs(controller.is_finished(), True)
        self.assertLess(abs(controller.time - 0.2), 0.001)  # Clamped to duration
        print("[PASS] test_controller_non_looping_animation passed")

    def test_controller_set_animation(self):
        """Test changing animation."""
        sheet = MockSpritesheet()
        frames1 = sheet.create_test_frames(count=2, duration=0.1)
        frames2 = sheet.create_test_frames(count=4, duration=0.2)
        animation1 = Animation("anim1", frames1)
        animation2 = Animation("anim2", frames2)

        controller = AnimationController(animation1)
        controller.update(0.15)
        self.assertGreater(controller.time, 0)

        # Change animation (should reset time by default)
        controller.set_animation(animation2)
        self.assertIs(controller.animation, animation2)
        self.assertEqual(controller.time, 0.0)
        self.assertIs(controller.is_finished(), False)
        print("[PASS] test_controller_set_animation passed")

    def test_controller_set_animation_preserve_time(self):
        """Test changing animation without resetting time."""
        sheet = MockSpritesheet()
        frames1 = sheet.create_test_frames(count=2, duration=0.1)
        frames2 = sheet.create_test_frames(count=4, duration=0.2)
        animation1 = Animation("anim1", frames1)
        animation2 = Animation("anim2", frames2)

        controller = AnimationController(animation1)
        controller.update(0.15)
        time_before = controller.time

        # Change animation without resetting time
        controller.set_animation(animation2, reset_time=False)
        self.assertIs(controller.animation, animation2)
        self.assertEqual(controller.time, time_before)
        print("[PASS] test_controller_set_animation_preserve_time passed")

    def test_controller_set_speed(self):
        """Test speed control."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("test", frames)
        controller = AnimationController(animation)

        # Normal speed
        controller.update(0.1)
        self.assertLess(abs(controller.time - 0.1), 0.001)

        # Double speed
        controller.set_speed(2.0)
        controller.update(0.1)
        self.assertLess(abs(controller.time - 0.3), 0.001)  # 0.1 + (0.1 * 2.0)

        # Half speed
        controller.reset()
        controller.set_speed(0.5)
        controller.update(0.1)
        self.assertLess(abs(controller.time - 0.05), 0.001)  # 0.1 * 0.5
        print("[PASS] test_controller_set_speed passed")

    def test_controller_set_speed_validation(self):
        """Test speed validation."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=2)
        animation = Animation("test", frames)
        controller = AnimationController(animation)

        # Negative speed should raise
        with self.assertRaises(ValueError):
            controller.set_speed(-1.0)

        # Zero speed should raise
        with self.assertRaises(ValueError):
            controller.set_speed(0.0)

        print("[PASS] test_controller_set_speed_validation passed")

    def test_controller_set_time(self):
        """Test setting time directly."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("test", frames)
        controller = AnimationController(animation)

        # Set to specific time
        controller.set_time(0.25)
        self.assertLess(abs(controller.time - 0.25), 0.001)
        self.assertIs(controller.is_finished(), False)

        # Get frame at that time
        frame = controller.get_current_frame()
        self.assertEqual(frame, frames[2])  # Third frame (0.2-0.3)
        print("[PASS] test_controller_set_time passed")

    def test_controller_set_time_validation(self):
        """Test time validation."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=2)
        animation = Animation("test", frames)
        controller = AnimationController(animation)

        # Negative time should raise
        with self.assertRaises(ValueError):
            controller.set_time(-0.1)

        print("[PASS] test_controller_set_time_validation passed")

    def test_controller_get_progress(self):
        """Test getting playback progress."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("test", frames)  # Total duration: 0.4
        controller = AnimationController(animation)

        # At start
        self.assertEqual(controller.get_progress(), 0.0)

        # At 25%
        controller.update(0.1)
        self.assertLess(abs(controller.get_progress() - 0.25), 0.001)

        # At 50%
        controller.update(0.1)
        self.assertLess(abs(controller.get_progress() - 0.5), 0.001)

        # At 100%
        controller.update(0.2)
        self.assertEqual(controller.get_progress(), 1.0)

        # Beyond 100% (clamped)
        controller.update(0.5)
        self.assertEqual(controller.get_progress(), 1.0)
        print("[PASS] test_controller_get_progress passed")


if __name__ == "__main__":
    unittest.main()
