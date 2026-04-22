from component.animation.core import Frame, Animation
from tests.mocks import MockSpritesheet

import sys
import unittest

sys.path.insert(0, ".")


class TestFrame(unittest.TestCase):
    def test_frame_creation(self):
        frame = Frame(
            sprite_x=0,
            sprite_y=0,
            width=32,
            height=32,
            duration=0.1,
        )

        self.assertEqual(frame.sprite_x, 0)
        self.assertEqual(frame.sprite_y, 0)
        self.assertEqual(frame.width, 32)
        self.assertEqual(frame.height, 32)
        self.assertEqual(frame.duration, 0.1)
        self.assertEqual(frame.offset_x, 0)
        self.assertEqual(frame.offset_y, 0)
        self.assertIs(frame.flip_h, False)
        self.assertIs(frame.flip_v, False)
        self.assertEqual(frame.metadata, {})
        print("[PASS] test_frame_creation passed")

    def test_frame_with_offsets(self):
        frame = Frame(
            sprite_x=32,
            sprite_y=64,
            width=16,
            height=24,
            duration=0.15,
            offset_x=-2,
            offset_y=3,
        )

        self.assertEqual(frame.offset_x, -2)
        self.assertEqual(frame.offset_y, 3)
        print("[PASS] test_frame_with_offsets passed")

    def test_frame_with_flips(self):
        frame = Frame(
            sprite_x=0,
            sprite_y=0,
            width=32,
            height=32,
            duration=0.1,
            flip_h=True,
            flip_v=True,
        )

        self.assertIs(frame.flip_h, True)
        self.assertIs(frame.flip_v, True)
        print("[PASS] test_frame_with_flips passed")

    def test_frame_with_metadata(self):
        frame = Frame(
            sprite_x=0,
            sprite_y=0,
            width=32,
            height=32,
            duration=0.1,
            metadata={"type": "walk", "step": 1, "description": "left foot forward"},
        )

        self.assertEqual(frame.metadata["type"], "walk")
        self.assertEqual(frame.metadata["step"], 1)
        self.assertEqual(frame.metadata["description"], "left foot forward")
        print("[PASS] test_frame_with_metadata passed")

    def test_frame_validation(self):
        with self.assertRaises(ValueError):
            Frame(0, 0, 0, 32, 0.1)

        with self.assertRaises(ValueError):
            Frame(0, 0, 32, -1, 0.1)

        with self.assertRaises(ValueError):
            Frame(0, 0, 32, 32, 0)

        print("[PASS] test_frame_validation passed")

    def test_frame_bounds(self):
        frame = Frame(
            sprite_x=64,
            sprite_y=128,
            width=48,
            height=64,
            duration=0.1,
        )

        bounds = frame.bounds()
        self.assertEqual(bounds, (64, 128, 48, 64))
        print("[PASS] test_frame_bounds passed")

    def test_frame_with_metadata_method(self):
        frame = Frame(
            sprite_x=0,
            sprite_y=0,
            width=32,
            height=32,
            duration=0.1,
            metadata={"type": "walk"},
        )

        new_frame = frame.with_metadata(step=2, direction="right")

        self.assertNotIn("step", frame.metadata)
        self.assertNotIn("direction", frame.metadata)
        self.assertEqual(new_frame.metadata["type"], "walk")
        self.assertEqual(new_frame.metadata["step"], 2)
        self.assertEqual(new_frame.metadata["direction"], "right")
        self.assertEqual(new_frame.sprite_x, frame.sprite_x)
        self.assertEqual(new_frame.width, frame.width)
        print("[PASS] test_frame_with_metadata_method passed")


class TestAnimation(unittest.TestCase):
    def test_animation_creation(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1),
            Frame(32, 0, 32, 32, 0.1),
            Frame(64, 0, 32, 32, 0.1),
        ]

        animation = Animation(name="walk", frames=frames)

        self.assertEqual(animation.name, "walk")
        self.assertEqual(len(animation.frames), 3)
        self.assertIs(animation.loop, True)
        self.assertEqual(animation.speed, 1.0)
        print("[PASS] test_animation_creation passed")

    def test_animation_duration(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1),
            Frame(32, 0, 32, 32, 0.2),
            Frame(64, 0, 32, 32, 0.15),
        ]

        animation = Animation(name="test", frames=frames)

        self.assertLess(abs(animation.duration() - 0.45), 0.001)
        print("[PASS] test_animation_duration passed")

    def test_animation_duration_with_speed(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1),
            Frame(32, 0, 32, 32, 0.1),
        ]

        anim1 = Animation(name="normal", frames=frames, speed=1.0)
        self.assertLess(abs(anim1.duration() - 0.2), 0.001)

        anim2 = Animation(name="fast", frames=frames, speed=2.0)
        self.assertLess(abs(anim2.duration() - 0.1), 0.001)

        anim3 = Animation(name="slow", frames=frames, speed=0.5)
        self.assertLess(abs(anim3.duration() - 0.4), 0.001)
        print("[PASS] test_animation_duration_with_speed passed")

    def test_animation_get_frame_at(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1),  # 0.0 - 0.1
            Frame(32, 0, 32, 32, 0.2),  # 0.1 - 0.3
            Frame(64, 0, 32, 32, 0.1),  # 0.3 - 0.4
        ]

        animation = Animation(name="test", frames=frames, loop=True)

        self.assertEqual(animation.get_frame_at(0.05), frames[0])
        self.assertEqual(animation.get_frame_at(0.15), frames[1])
        self.assertEqual(animation.get_frame_at(0.35), frames[2])

        print("[PASS] test_animation_get_frame_at passed")

    def test_animation_looping(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1),
            Frame(32, 0, 32, 32, 0.1),
        ]

        animation = Animation(name="test", frames=frames, loop=True)

        # Duration is 0.2 seconds
        self.assertLess(abs(animation.duration() - 0.2), 0.001)

        frame_at_025 = animation.get_frame_at(0.25)
        self.assertEqual(frame_at_025, frames[0])

        frame_at_05 = animation.get_frame_at(0.5)
        self.assertEqual(frame_at_05, frames[0])

        print("[PASS] test_animation_looping passed")

    def test_animation_non_looping(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1),
            Frame(32, 0, 32, 32, 0.1),
        ]

        animation = Animation(name="test", frames=frames, loop=False)

        self.assertEqual(animation.get_frame_at(0.05), frames[0])
        self.assertEqual(animation.get_frame_at(0.15), frames[1])
        self.assertEqual(animation.get_frame_at(0.3), frames[1])
        self.assertEqual(animation.get_frame_at(1.0), frames[1])

        print("[PASS] test_animation_non_looping passed")

    def test_animation_get_frame_index_at(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1),
            Frame(32, 0, 32, 32, 0.1),
            Frame(64, 0, 32, 32, 0.1),
        ]

        animation = Animation(name="test", frames=frames, loop=True)

        self.assertEqual(animation.get_frame_index_at(0.05), 0)
        self.assertEqual(animation.get_frame_index_at(0.15), 1)
        self.assertEqual(animation.get_frame_index_at(0.25), 2)
        self.assertEqual(animation.get_frame_index_at(0.35), 0)

        print("[PASS] test_animation_get_frame_index_at passed")

    def test_animation_frame_count(self):
        frames = [Frame(i * 32, 0, 32, 32, 0.1) for i in range(5)]
        animation = Animation(name="test", frames=frames)

        self.assertEqual(animation.frame_count(), 5)
        print("[PASS] test_animation_frame_count passed")

    def test_animation_with_speed(self):
        frames = [Frame(0, 0, 32, 32, 0.1), Frame(32, 0, 32, 32, 0.1)]
        animation = Animation(name="original", frames=frames, speed=1.0)
        fast_animation = animation.with_speed(2.0)

        self.assertEqual(animation.speed, 1.0)
        self.assertLess(abs(animation.duration() - 0.2), 0.001)
        self.assertEqual(fast_animation.speed, 2.0)
        self.assertLess(abs(fast_animation.duration() - 0.1), 0.001)
        self.assertEqual(fast_animation.name, "original")  # Name copied

        print("[PASS] test_animation_with_speed passed")

    def test_animation_reversed(self):
        frames = [
            Frame(0, 0, 32, 32, 0.1, metadata={"index": 0}),
            Frame(32, 0, 32, 32, 0.1, metadata={"index": 1}),
            Frame(64, 0, 32, 32, 0.1, metadata={"index": 2}),
        ]

        animation = Animation(name="forward", frames=frames)
        reversed_anim = animation.reversed()

        self.assertEqual(reversed_anim.name, "forward_reversed")
        self.assertEqual(reversed_anim.frames[0].metadata["index"], 2)
        self.assertEqual(reversed_anim.frames[1].metadata["index"], 1)
        self.assertEqual(reversed_anim.frames[2].metadata["index"], 0)
        self.assertEqual(animation.frames[0].metadata["index"], 0)

        print("[PASS] test_animation_reversed passed")

    def test_animation_validation(self):
        with self.assertRaises(ValueError):
            Animation(name="empty", frames=[])

        with self.assertRaises(ValueError):
            frames = [Frame(0, 0, 32, 32, 0.1)]
            Animation(name="invalid_speed", frames=frames, speed=0)

        print("[PASS] test_animation_validation passed")


class TestMockSpritesheet(unittest.TestCase):
    # =============================================================================
    # Integration Tests with MockSpritesheet
    # =============================================================================

    def test_mock_spritesheet_basic(self):
        spritesheet = MockSpritesheet(width=256, height=256)
        frame = spritesheet.get_frame(0, 0, 32, 32)

        self.assertEqual(frame.sprite_x, 0)
        self.assertEqual(frame.sprite_y, 0)
        self.assertEqual(frame.width, 32)
        self.assertEqual(frame.height, 32)

        print("[PASS] test_mock_spritesheet_basic passed")

    def test_mock_spritesheet_draw_tracking(self):
        spritesheet = MockSpritesheet()
        frame = Frame(0, 0, 32, 32, 0.1)

        self.assertEqual(spritesheet.get_draw_count(), 0)
        spritesheet.draw_frame(None, frame, 100, 200)
        self.assertEqual(spritesheet.get_draw_count(), 1)

        last_draw = spritesheet.get_last_draw()
        self.assertEqual(last_draw["x"], 100)
        self.assertEqual(last_draw["y"], 200)
        self.assertEqual(last_draw["frame"], frame)

        print("[PASS] test_mock_spritesheet_draw_tracking passed")

    def test_mock_spritesheet_create_test_frames(self):
        spritesheet = MockSpritesheet(width=256, height=256)
        frames = spritesheet.create_test_frames(count=4, duration=0.15)

        self.assertEqual(len(frames), 4)
        self.assertEqual(frames[0].sprite_x, 0)
        self.assertEqual(frames[1].sprite_x, 64)  # 256 / 4 = 64
        self.assertEqual(frames[2].sprite_x, 128)
        self.assertEqual(frames[3].sprite_x, 192)

        for frame in frames:
            self.assertEqual(frame.duration, 0.15)
            self.assertIs(frame.metadata["test"], True)

        print("[PASS] test_mock_spritesheet_create_test_frames passed")

    def test_animation_with_mock_spritesheet(self):
        """Integration test: Animation with MockSpritesheet."""
        spritesheet = MockSpritesheet()

        frames = spritesheet.create_test_frames(count=3, duration=0.1)
        animation = Animation(name="walk", frames=frames, loop=True)

        self.assertEqual(animation.frame_count(), 3)
        self.assertLess(abs(animation.duration() - 0.3), 0.001)

        frame_at_0 = animation.get_frame_at(0.05)
        frame_at_1 = animation.get_frame_at(0.15)
        frame_at_2 = animation.get_frame_at(0.25)

        self.assertEqual(frame_at_0, frames[0])
        self.assertEqual(frame_at_1, frames[1])
        self.assertEqual(frame_at_2, frames[2])
        for i, frame in enumerate(frames):
            spritesheet.draw_frame(None, frame, i * 40, 100)

        self.assertEqual(spritesheet.get_draw_count(), 3)

        print("[PASS] test_animation_with_mock_spritesheet passed")


if __name__ == "__main__":
    unittest.main()
