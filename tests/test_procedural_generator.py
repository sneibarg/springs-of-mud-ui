"""
Tests for ProceduralGenerator animation generation.
"""
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from component.animation.core import Frame, ProceduralGenerator


class TestProceduralGeneratorProtocol(unittest.TestCase):
    """Tests for the FrameGenerator protocol implementation."""

    def setUp(self):
        self.gen = ProceduralGenerator()

    def test_generator_protocol_walk_cycle(self):
        """Test generate() with walk_cycle description."""
        frames = self.gen.generate("walk_cycle", frame_count=4, frame_width=16, frame_height=16)

        self.assertEqual(len(frames), 4)
        self.assertTrue(all(isinstance(f, Frame) for f in frames))
        self.assertEqual(frames[0].metadata["frame_type"], "walk")
        self.assertEqual(frames[0].sprite_x, 0)
        self.assertEqual(frames[1].sprite_x, 16)
        self.assertEqual(frames[2].sprite_x, 32)

    def test_generator_protocol_invalid(self):
        """Test generate() with invalid description."""
        with self.assertRaises(ValueError) as context:
            self.gen.generate("invalid_animation_type")
        self.assertIn("Unknown animation type", str(context.exception))


class TestWalkCycle(unittest.TestCase):
    """Tests for walk cycle generation."""

    def setUp(self):
        self.gen = ProceduralGenerator()

    def test_walk_cycle_basic(self):
        """Test basic walk cycle generation."""
        frames = self.gen.generate_walk_cycle(frame_count=4, frame_width=32, frame_height=32)

        self.assertEqual(len(frames), 4)
        for i, frame in enumerate(frames):
            self.assertEqual(frame.sprite_x, i * 32)
            self.assertEqual(frame.sprite_y, 0)
            self.assertEqual(frame.width, 32)
            self.assertEqual(frame.height, 32)
            self.assertEqual(frame.duration, 0.1)
            self.assertEqual(frame.metadata["step"], i)

    def test_walk_cycle_custom_params(self):
        """Test walk cycle with custom parameters."""
        frames = self.gen.generate_walk_cycle(
            start_x=100, start_y=50, frame_count=6,
            frame_width=16, frame_height=24, frame_duration=0.2
        )

        self.assertEqual(len(frames), 6)
        self.assertEqual(frames[0].sprite_x, 100)
        self.assertEqual(frames[0].sprite_y, 50)
        self.assertEqual(frames[0].width, 16)
        self.assertEqual(frames[0].height, 24)
        self.assertEqual(frames[0].duration, 0.2)
        self.assertEqual(frames[5].sprite_x, 100 + 5 * 16)


class TestBounce(unittest.TestCase):
    """Tests for bounce animation."""

    def setUp(self):
        self.gen = ProceduralGenerator()
        self.base_frame = Frame(sprite_x=0, sprite_y=0, width=16, height=16, duration=0.1)

    def test_bounce_basic(self):
        """Test basic bounce animation."""
        frames = self.gen.generate_bounce(self.base_frame, bounce_height=10, frame_count=8)

        self.assertEqual(len(frames), 8)
        self.assertTrue(all(f.width == 16 for f in frames))
        self.assertTrue(all(f.height == 16 for f in frames))

        # First and last frames should be at ground level
        self.assertEqual(frames[0].offset_y, 0)
        self.assertEqual(frames[-1].offset_y, 0)

        # Check that there's a peak somewhere in the middle (negative offset means up)
        offsets = [f.offset_y for f in frames]
        min_offset = min(offsets)
        self.assertLess(min_offset, 0)  # Should go up
        self.assertGreaterEqual(abs(min_offset), 9)  # Should be close to bounce_height (allowing for rounding)


class TestSpin(unittest.TestCase):
    """Tests for spin animation."""

    def setUp(self):
        self.gen = ProceduralGenerator()
        self.base_frame = Frame(sprite_x=0, sprite_y=0, width=16, height=16, duration=0.1)

    def test_spin_clockwise(self):
        """Test clockwise spin animation."""
        frames = self.gen.generate_spin(self.base_frame, frame_count=8, clockwise=True)

        self.assertEqual(len(frames), 8)
        self.assertTrue(all(isinstance(f, Frame) for f in frames))

        # Check that flips change throughout animation
        flip_states = [(f.flip_h, f.flip_v) for f in frames]
        self.assertGreater(len(set(flip_states)), 1)  # Should have different flip states
        self.assertTrue(all(f.metadata["clockwise"] for f in frames))

    def test_spin_counter_clockwise(self):
        """Test counter-clockwise spin animation."""
        frames = self.gen.generate_spin(self.base_frame, frame_count=8, clockwise=False)

        self.assertEqual(len(frames), 8)
        self.assertTrue(all(not f.metadata["clockwise"] for f in frames))

    def test_spin_minimum_frames(self):
        """Test spin with less than minimum frames."""
        frames = self.gen.generate_spin(self.base_frame, frame_count=2)

        # Should be clamped to 4
        self.assertEqual(len(frames), 4)


class TestFade(unittest.TestCase):
    """Tests for fade animations."""

    def setUp(self):
        self.gen = ProceduralGenerator()
        self.base_frame = Frame(sprite_x=0, sprite_y=0, width=16, height=16, duration=0.1)

    def test_fade_in(self):
        """Test fade in animation."""
        frames = self.gen.generate_fade_in(self.base_frame, frame_count=10)

        self.assertEqual(len(frames), 10)

        # First frame should be fully transparent
        self.assertEqual(frames[0].metadata["alpha"], 0.0)

        # Last frame should be fully opaque
        self.assertEqual(frames[-1].metadata["alpha"], 1.0)

        # Alpha should increase monotonically
        alphas = [f.metadata["alpha"] for f in frames]
        self.assertEqual(alphas, sorted(alphas))

    def test_fade_out(self):
        """Test fade out animation."""
        frames = self.gen.generate_fade_out(self.base_frame, frame_count=10)

        self.assertEqual(len(frames), 10)

        # First frame should be fully opaque
        self.assertEqual(frames[0].metadata["alpha"], 1.0)

        # Last frame should be fully transparent
        self.assertEqual(frames[-1].metadata["alpha"], 0.0)

        # Alpha should decrease monotonically
        alphas = [f.metadata["alpha"] for f in frames]
        self.assertEqual(alphas, sorted(alphas, reverse=True))


class TestScale(unittest.TestCase):
    """Tests for scale animations."""

    def setUp(self):
        self.gen = ProceduralGenerator()
        self.base_frame = Frame(sprite_x=0, sprite_y=0, width=16, height=16, duration=0.1)

    def test_scale(self):
        """Test scale animation."""
        frames = self.gen.generate_scale(self.base_frame, start_scale=0.5, end_scale=1.5, frame_count=10)

        self.assertEqual(len(frames), 10)

        # First frame should be at start scale
        self.assertAlmostEqual(frames[0].metadata["scale"], 0.5, places=2)

        # Last frame should be at end scale
        self.assertAlmostEqual(frames[-1].metadata["scale"], 1.5, places=2)

        # Scale should increase monotonically
        scales = [f.metadata["scale"] for f in frames]
        self.assertEqual(scales, sorted(scales))


class TestPulse(unittest.TestCase):
    """Tests for pulse animations."""

    def setUp(self):
        self.gen = ProceduralGenerator()
        self.base_frame = Frame(sprite_x=0, sprite_y=0, width=16, height=16, duration=0.1)

    def test_pulse(self):
        """Test pulse animation."""
        frames = self.gen.generate_pulse(self.base_frame, min_scale=0.9, max_scale=1.1, frame_count=10, cycles=1)

        self.assertEqual(len(frames), 10)

        # All scales should be between min and max
        scales = [f.metadata["scale"] for f in frames]
        self.assertTrue(all(0.9 <= s <= 1.1 for s in scales))

        # Should have variation (pulse effect)
        self.assertGreater(len(set(scales)), 1)

    def test_pulse_multiple_cycles(self):
        """Test pulse animation with multiple cycles."""
        frames = self.gen.generate_pulse(self.base_frame, min_scale=0.9, max_scale=1.1, frame_count=20, cycles=2)

        self.assertEqual(len(frames), 20)
        scales = [f.metadata["scale"] for f in frames]
        self.assertTrue(all(0.9 <= s <= 1.1 for s in scales))


class TestShake(unittest.TestCase):
    """Tests for shake animation."""

    def setUp(self):
        self.gen = ProceduralGenerator()
        self.base_frame = Frame(sprite_x=0, sprite_y=0, width=16, height=16, duration=0.1)

    def test_shake(self):
        """Test shake animation."""
        frames = self.gen.generate_shake(self.base_frame, shake_amount=3, frame_count=10)

        self.assertEqual(len(frames), 10)

        # All offsets should be within shake amount
        for frame in frames:
            self.assertLessEqual(abs(frame.offset_x), 3)
            self.assertLessEqual(abs(frame.offset_y), 3)

        # Should have variation
        offsets_x = [f.offset_x for f in frames]
        offsets_y = [f.offset_y for f in frames]
        self.assertGreater(len(set(offsets_x)), 1)
        self.assertGreater(len(set(offsets_y)), 1)


class TestSlide(unittest.TestCase):
    """Tests for slide animations."""

    def setUp(self):
        self.gen = ProceduralGenerator()
        self.base_frame = Frame(sprite_x=0, sprite_y=0, width=16, height=16, duration=0.1)

    def test_slide_linear(self):
        """Test slide animation with linear easing."""
        frames = self.gen.generate_slide(
            self.base_frame, start_x=-100, start_y=0, end_x=0, end_y=0,
            frame_count=11, easing="linear"
        )

        self.assertEqual(len(frames), 11)

        # First frame at start position
        self.assertEqual(frames[0].offset_x, -100)
        self.assertEqual(frames[0].offset_y, 0)

        # Last frame at end position
        self.assertEqual(frames[-1].offset_x, 0)
        self.assertEqual(frames[-1].offset_y, 0)

        # Linear interpolation
        self.assertEqual(frames[5].offset_x, -50)

    def test_slide_ease_in(self):
        """Test slide animation with ease_in."""
        frames = self.gen.generate_slide(
            self.base_frame, start_x=0, start_y=0, end_x=100, end_y=0,
            frame_count=10, easing="ease_in"
        )

        self.assertEqual(len(frames), 10)
        self.assertEqual(frames[0].offset_x, 0)
        self.assertEqual(frames[-1].offset_x, 100)
        self.assertEqual(frames[0].metadata["easing"], "ease_in")

    def test_slide_ease_out(self):
        """Test slide animation with ease_out."""
        frames = self.gen.generate_slide(
            self.base_frame, start_x=0, start_y=0, end_x=100, end_y=0,
            frame_count=10, easing="ease_out"
        )

        self.assertEqual(len(frames), 10)
        self.assertEqual(frames[0].offset_x, 0)
        self.assertEqual(frames[-1].offset_x, 100)
        self.assertEqual(frames[0].metadata["easing"], "ease_out")

    def test_slide_ease_in_out(self):
        """Test slide animation with ease_in_out."""
        frames = self.gen.generate_slide(
            self.base_frame, start_x=0, start_y=0, end_x=100, end_y=0,
            frame_count=10, easing="ease_in_out"
        )

        self.assertEqual(len(frames), 10)
        self.assertEqual(frames[0].offset_x, 0)
        self.assertEqual(frames[-1].offset_x, 100)
        self.assertEqual(frames[0].metadata["easing"], "ease_in_out")

    def test_slide_vertical(self):
        """Test vertical slide animation."""
        frames = self.gen.generate_slide(
            self.base_frame, start_x=0, start_y=-50, end_x=0, end_y=50,
            frame_count=11, easing="linear"
        )

        self.assertEqual(len(frames), 11)
        self.assertEqual(frames[0].offset_y, -50)
        self.assertEqual(frames[-1].offset_y, 50)
        self.assertEqual(frames[5].offset_y, 0)

    def test_slide_diagonal(self):
        """Test diagonal slide animation."""
        frames = self.gen.generate_slide(
            self.base_frame, start_x=-100, start_y=-100, end_x=100, end_y=100,
            frame_count=11, easing="linear"
        )

        self.assertEqual(len(frames), 11)
        self.assertEqual(frames[0].offset_x, -100)
        self.assertEqual(frames[0].offset_y, -100)
        self.assertEqual(frames[-1].offset_x, 100)
        self.assertEqual(frames[-1].offset_y, 100)


if __name__ == "__main__":
    unittest.main()
