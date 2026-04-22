"""
Comprehensive tests for AnimatedSprite.
"""
import sys
import unittest

sys.path.insert(0, ".")

from component.animation.core import Animation, AnimatedSprite
from tests.mocks import MockSpritesheet


class TestAnimatedSprite(unittest.TestCase):
    # =============================================================================
    # AnimatedSprite Tests
    # =============================================================================

    def test_sprite_creation(self):
        """Test creating AnimatedSprite."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet, x=100, y=200)

        self.assertIs(sprite.spritesheet, sheet)
        self.assertEqual(sprite.x, 100)
        self.assertEqual(sprite.y, 200)
        self.assertEqual(sprite.animations, {})
        self.assertIsNone(sprite.controller)
        self.assertIsNone(sprite.current_animation)
        self.assertIs(sprite.visible, True)
        self.assertEqual(sprite.velocity_x, 0.0)
        self.assertEqual(sprite.velocity_y, 0.0)
        print("[PASS] test_sprite_creation passed")

    def test_sprite_creation_with_animations(self):
        """Test creating sprite with initial animations."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4)
        animations = {
            "walk": Animation("walk", frames),
            "run": Animation("run", frames),
        }

        sprite = AnimatedSprite(sheet, animations=animations)

        self.assertEqual(len(sprite.animations), 2)
        self.assertIn("walk", sprite.animations)
        self.assertIn("run", sprite.animations)
        print("[PASS] test_sprite_creation_with_animations passed")

    def test_add_animation(self):
        """Test adding animations."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=3)
        animation = Animation("idle", frames)

        sprite.add_animation("idle", animation)

        self.assertIn("idle", sprite.animations)
        self.assertIs(sprite.animations["idle"], animation)
        print("[PASS] test_add_animation passed")

    def test_add_animation_validation(self):
        """Test animation name validation."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=2)
        animation = Animation("test", frames)

        # Empty name should raise
        with self.assertRaises(ValueError):
            sprite.add_animation("", animation)

        print("[PASS] test_add_animation_validation passed")

    def test_has_animation(self):
        """Test checking if animation exists."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=2)
        sprite.add_animation("walk", Animation("walk", frames))

        self.assertIs(sprite.has_animation("walk"), True)
        self.assertIs(sprite.has_animation("run"), False)
        print("[PASS] test_has_animation passed")

    def test_play_animation(self):
        """Test playing an animation."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=4, duration=0.1)
        sprite.add_animation("walk", Animation("walk", frames))

        # Play animation
        sprite.play("walk")

        self.assertEqual(sprite.current_animation, "walk")
        self.assertIsNotNone(sprite.controller)
        self.assertIs(sprite.is_playing(), True)
        print("[PASS] test_play_animation passed")

    def test_play_nonexistent_animation(self):
        """Test playing animation that doesn't exist."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        with self.assertRaises(ValueError) as cm:
            sprite.play("nonexistent")
        self.assertIn("not found", str(cm.exception))

        print("[PASS] test_play_nonexistent_animation passed")

    def test_play_animation_switching(self):
        """Test switching between animations."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames1 = sheet.create_test_frames(count=2, duration=0.1)
        frames2 = sheet.create_test_frames(count=4, duration=0.15)
        sprite.add_animation("walk", Animation("walk", frames1))
        sprite.add_animation("run", Animation("run", frames2))

        # Play first animation
        sprite.play("walk")
        sprite.update(0.15)
        self.assertEqual(sprite.current_animation, "walk")

        # Switch to second animation
        sprite.play("run")
        self.assertEqual(sprite.current_animation, "run")
        self.assertEqual(sprite.controller.time, 0.0)  # Should reset
        print("[PASS] test_play_animation_switching passed")

    def test_play_restart(self):
        """Test restarting current animation."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=4, duration=0.1)
        sprite.add_animation("walk", Animation("walk", frames))

        # Play and advance
        sprite.play("walk")
        sprite.update(0.15)
        self.assertGreater(sprite.controller.time, 0)

        # Play again without restart flag (should not restart)
        sprite.play("walk")
        self.assertGreater(sprite.controller.time, 0)

        # Play with restart flag
        sprite.play("walk", restart=True)
        self.assertEqual(sprite.controller.time, 0.0)
        print("[PASS] test_play_restart passed")

    def test_stop_pause_resume(self):
        """Test stop, pause, and resume."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=4, duration=0.1)
        sprite.add_animation("walk", Animation("walk", frames))

        sprite.play("walk")
        sprite.update(0.15)

        # Pause
        sprite.pause()
        self.assertIs(sprite.is_playing(), False)
        time_paused = sprite.controller.time

        # Update should not advance time
        sprite.update(0.1)
        self.assertEqual(sprite.controller.time, time_paused)

        # Resume
        sprite.resume()
        self.assertIs(sprite.is_playing(), True)
        sprite.update(0.1)
        self.assertGreater(sprite.controller.time, time_paused)

        # Stop
        sprite.stop()
        self.assertIs(sprite.is_playing(), False)
        self.assertEqual(sprite.controller.time, 0.0)
        print("[PASS] test_stop_pause_resume passed")

    def test_update_animation(self):
        """Test update advances animation."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=4, duration=0.1)
        sprite.add_animation("walk", Animation("walk", frames, loop=True))
        sprite.play("walk")

        # Update
        sprite.update(0.15)

        # Should be on second frame
        frame = sprite.get_current_frame()
        self.assertEqual(frame, frames[1])
        print("[PASS] test_update_animation passed")

    def test_update_with_velocity(self):
        """Test update moves sprite with velocity."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet, x=100, y=100)

        sprite.set_velocity(50, -30)  # 50 pixels/sec right, 30 pixels/sec up

        # Update for 0.1 seconds
        sprite.update(0.1)

        self.assertLess(abs(sprite.x - 105.0), 0.001)  # 100 + 50 * 0.1
        self.assertLess(abs(sprite.y - 97.0), 0.001)   # 100 + (-30) * 0.1

        # Update again
        sprite.update(0.2)

        self.assertLess(abs(sprite.x - 115.0), 0.001)  # 105 + 50 * 0.2
        self.assertLess(abs(sprite.y - 91.0), 0.001)   # 97 + (-30) * 0.2
        print("[PASS] test_update_with_velocity passed")

    def test_draw(self):
        """Test drawing sprite."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet, x=50, y=75)

        frames = sheet.create_test_frames(count=2, duration=0.1)
        sprite.add_animation("idle", Animation("idle", frames))
        sprite.play("idle")

        # Draw
        sprite.draw(None)

        # Check that frame was drawn
        self.assertEqual(sheet.get_draw_count(), 1)
        last_draw = sheet.get_last_draw()
        self.assertEqual(last_draw["x"], 50)
        self.assertEqual(last_draw["y"], 75)
        self.assertEqual(last_draw["frame"], frames[0])
        print("[PASS] test_draw passed")

    def test_draw_when_invisible(self):
        """Test drawing when sprite is invisible."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=2)
        sprite.add_animation("idle", Animation("idle", frames))
        sprite.play("idle")

        # Make invisible
        sprite.visible = False

        # Draw should not draw anything
        sprite.draw(None)
        self.assertEqual(sheet.get_draw_count(), 0)
        print("[PASS] test_draw_when_invisible passed")

    def test_draw_without_animation(self):
        """Test drawing when no animation is playing."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        # Draw without animation
        sprite.draw(None)

        # Should not draw anything
        self.assertEqual(sheet.get_draw_count(), 0)
        print("[PASS] test_draw_without_animation passed")

    def test_get_current_frame(self):
        """Test getting current frame."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        # No animation
        self.assertIsNone(sprite.get_current_frame())

        # With animation
        frames = sheet.create_test_frames(count=3, duration=0.1)
        sprite.add_animation("walk", Animation("walk", frames))
        sprite.play("walk")

        frame = sprite.get_current_frame()
        self.assertEqual(frame, frames[0])

        sprite.update(0.15)
        frame = sprite.get_current_frame()
        self.assertEqual(frame, frames[1])
        print("[PASS] test_get_current_frame passed")

    def test_is_playing(self):
        """Test is_playing check."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        # No animation
        self.assertIs(sprite.is_playing(), False)

        # With animation
        frames = sheet.create_test_frames(count=2)
        sprite.add_animation("idle", Animation("idle", frames))
        sprite.play("idle")
        self.assertIs(sprite.is_playing(), True)

        sprite.pause()
        self.assertIs(sprite.is_playing(), False)
        print("[PASS] test_is_playing passed")

    def test_is_finished(self):
        """Test is_finished for non-looping animations."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=2, duration=0.1)
        sprite.add_animation("die", Animation("die", frames, loop=False))
        sprite.play("die")

        # Not finished yet
        self.assertIs(sprite.is_finished(), False)

        # Advance partway
        sprite.update(0.15)
        self.assertIs(sprite.is_finished(), False)

        # Advance past end
        sprite.update(0.1)
        self.assertIs(sprite.is_finished(), True)
        print("[PASS] test_is_finished passed")

    def test_set_position(self):
        """Test setting position."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet, x=0, y=0)

        sprite.set_position(123, 456)

        self.assertEqual(sprite.x, 123)
        self.assertEqual(sprite.y, 456)
        print("[PASS] test_set_position passed")

    def test_set_velocity(self):
        """Test setting velocity."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        sprite.set_velocity(100, -50)

        self.assertEqual(sprite.velocity_x, 100)
        self.assertEqual(sprite.velocity_y, -50)
        print("[PASS] test_set_velocity passed")

    def test_set_speed(self):
        """Test setting animation speed."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=4, duration=0.1)
        sprite.add_animation("walk", Animation("walk", frames))
        sprite.play("walk")

        # Set double speed
        sprite.set_speed(2.0)
        sprite.update(0.1)

        # Should advance twice as fast
        self.assertLess(abs(sprite.controller.time - 0.2), 0.001)
        print("[PASS] test_set_speed passed")

    def test_animation_changed_callback(self):
        """Test animation change callback."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        frames = sheet.create_test_frames(count=2)
        sprite.add_animation("walk", Animation("walk", frames))
        sprite.add_animation("run", Animation("run", frames))

        # Track callback calls
        callback_calls = []

        def on_changed(new_anim, old_anim):
            callback_calls.append((new_anim, old_anim))

        sprite.on_animation_changed(on_changed)

        # Play first animation
        sprite.play("walk")
        self.assertEqual(len(callback_calls), 1)
        self.assertEqual(callback_calls[0], ("walk", None))

        # Switch animation
        sprite.play("run")
        self.assertEqual(len(callback_calls), 2)
        self.assertEqual(callback_calls[1], ("run", "walk"))

        # Play same animation (should not trigger callback)
        sprite.play("run")
        self.assertEqual(len(callback_calls), 2)

        # Play with restart (should trigger callback)
        sprite.play("run", restart=True)
        self.assertEqual(len(callback_calls), 3)
        self.assertEqual(callback_calls[2], ("run", "run"))
        print("[PASS] test_animation_changed_callback passed")

    # =============================================================================
    # Integration Tests
    # =============================================================================

    def test_full_sprite_lifecycle(self):
        """Integration test: full sprite lifecycle."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet, x=0, y=0)

        # Create animations
        idle_frames = sheet.get_frames_strip(0, 0, 32, 32, count=2, duration=0.5)
        walk_frames = sheet.get_frames_strip(0, 32, 32, 32, count=4, duration=0.15)
        sprite.add_animation("idle", Animation("idle", idle_frames, loop=True))
        sprite.add_animation("walk", Animation("walk", walk_frames, loop=True))

        # Start with idle
        sprite.play("idle")
        self.assertEqual(sprite.current_animation, "idle")

        # Update and draw
        sprite.update(0.016)
        sprite.draw(None)
        self.assertEqual(sheet.get_draw_count(), 1)

        # Switch to walk and move
        sprite.play("walk")
        sprite.set_velocity(100, 0)

        # Simulate several frames
        for _ in range(10):
            sprite.update(0.016)
            sprite.draw(None)

        # Verify sprite moved
        self.assertGreater(sprite.x, 0)

        # Verify animation advanced
        self.assertGreater(sprite.controller.time, 0)

        # Verify frames were drawn
        self.assertEqual(sheet.get_draw_count(), 11)  # 1 + 10
        print("[PASS] test_full_sprite_lifecycle passed")

    def test_sprite_with_state_machine(self):
        """Integration test: simple state machine with sprite."""
        sheet = MockSpritesheet()
        sprite = AnimatedSprite(sheet)

        # Setup animations
        idle_frames = sheet.create_test_frames(count=2, duration=0.5)
        walk_frames = sheet.create_test_frames(count=4, duration=0.15)
        jump_frames = sheet.create_test_frames(count=3, duration=0.1)

        sprite.add_animation("idle", Animation("idle", idle_frames, loop=True))
        sprite.add_animation("walk", Animation("walk", walk_frames, loop=True))
        sprite.add_animation("jump", Animation("jump", jump_frames, loop=False))

        # Simple state machine
        state = "idle"
        sprite.play("idle")

        # Idle state
        sprite.update(0.016)
        self.assertEqual(sprite.current_animation, "idle")

        # Trigger walk
        state = "walk"
        sprite.play("walk")
        sprite.set_velocity(50, 0)
        sprite.update(0.016)
        self.assertEqual(sprite.current_animation, "walk")
        self.assertGreater(sprite.x, 0)

        # Trigger jump
        state = "jump"
        sprite.play("jump")
        sprite.set_velocity(0, -100)

        # Jump until finished
        for _ in range(20):
            sprite.update(0.016)
            if sprite.is_finished():
                break

        self.assertIs(sprite.is_finished(), True)

        # Return to idle
        state = "idle"
        sprite.play("idle")
        sprite.set_velocity(0, 0)
        self.assertEqual(sprite.current_animation, "idle")
        print("[PASS] test_sprite_with_state_machine passed")


if __name__ == "__main__":
    unittest.main()
