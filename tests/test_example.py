"""
Example tests demonstrating how to use the mock implementations.
"""
import unittest

from tests.mocks import MockGraphics, MockKeySource, MockMouseSource
from component.geometry.Rect import Rect
from component.render import Colors
import component.input.Keys as Keys


class TestMockImplementations(unittest.TestCase):
    def test_mock_graphics_records_calls(self):
        """Test that MockGraphics records all drawing calls."""
        gfx = MockGraphics()

        # Draw some shapes
        gfx.rect(10, 20, 30, 40, Colors.COLOR_RED)
        gfx.text(50, 60, "Hello", Colors.COLOR_WHITE)
        gfx.circ(100, 100, 25, Colors.COLOR_LIGHT_BLUE)

        # Verify calls were recorded
        self.assertEqual(len(gfx.calls), 3)
        self.assertEqual(gfx.calls[0], ("rect", (10, 20, 30, 40, Colors.COLOR_RED)))
        self.assertEqual(gfx.calls[1], ("text", (50, 60, "Hello", Colors.COLOR_WHITE)))
        self.assertEqual(gfx.calls[2], ("circ", (100, 100, 25, Colors.COLOR_LIGHT_BLUE)))

        # Use helper methods
        gfx.assert_rect_drawn(10, 20, 30, 40, Colors.COLOR_RED)
        gfx.assert_text_drawn(50, 60, "Hello", Colors.COLOR_WHITE)

    def test_mock_key_source_simulates_input(self):
        """Test that MockKeySource simulates keyboard input."""
        keys = MockKeySource()

        # Initially no keys pressed
        self.assertFalse(keys.btnp(Keys.KEY_A))
        self.assertFalse(keys.btn(Keys.KEY_A))

        # Simulate pressing a key
        keys.press_key(Keys.KEY_A)
        self.assertTrue(keys.btnp(Keys.KEY_A))
        self.assertTrue(keys.btn(Keys.KEY_A))

        # Clear pressed state (end of frame)
        keys.clear_pressed()
        self.assertFalse(keys.btnp(Keys.KEY_A))
        self.assertTrue(keys.btn(Keys.KEY_A))  # Still held down

        # Release the key
        keys.release_key(Keys.KEY_A)
        self.assertFalse(keys.btnp(Keys.KEY_A))
        self.assertFalse(keys.btn(Keys.KEY_A))

    def test_mock_mouse_source_simulates_mouse(self):
        """Test that MockMouseSource simulates mouse input."""
        mouse = MockMouseSource(x=100, y=200)

        # Check initial position
        x, y = mouse.get_position()
        self.assertEqual(x, 100)
        self.assertEqual(y, 200)

        # Move mouse
        mouse.move_to(150, 250)
        x, y = mouse.get_position()
        self.assertEqual(x, 150)
        self.assertEqual(y, 250)

        # Simulate button press
        self.assertFalse(mouse.is_button_pressed(Keys.MOUSE_BUTTON_LEFT))
        mouse.press_button(Keys.MOUSE_BUTTON_LEFT)
        self.assertTrue(mouse.is_button_pressed(Keys.MOUSE_BUTTON_LEFT))
        self.assertTrue(mouse.is_button_down(Keys.MOUSE_BUTTON_LEFT))

        # Simulate scroll
        mouse.scroll_up(3)
        self.assertEqual(mouse.get_wheel_delta(), 3)

    def test_component_with_mocks(self):
        """Test a component using mock implementations (Button)."""
        from component.button.Button import Button

        gfx = MockGraphics()
        rect = Rect(10, 10, 50, 20)

        clicked = False

        def on_click():
            nonlocal clicked
            clicked = True

        # Spy renderer to verify Button.draw delegates to FieldRenderer.draw_button
        class SpyRenderer:
            def __init__(self):
                self.calls = []

            def draw_button(
                self,
                ctx,
                rect,
                text,
                *,
                hover,
                base_col,
                hover_col,
                border_col,
            ):
                self.calls.append(
                    {
                        "ctx": ctx,
                        "rect": rect,
                        "text": text,
                        "hover": hover,
                        "base_col": base_col,
                        "hover_col": hover_col,
                        "border_col": border_col,
                    }
                )

        renderer = SpyRenderer()
        button = Button(rect, "Test", 2, 3, on_click, renderer=renderer)

        # Minimal context matching Button.update expectations
        class MockInput:
            mx = 25
            my = 20
            click = True

        class MockContext:
            def __init__(self, graphics):
                self.input = MockInput()
                self.gfx = graphics

        ctx = MockContext(gfx)

        # update should trigger click when inside rect and click=True
        button.update(ctx)
        self.assertTrue(clicked)
        self.assertIs(button.hover, True)

        # draw should delegate exactly once to renderer.draw_button
        button.draw(ctx)
        self.assertEqual(len(renderer.calls), 1)

        call = renderer.calls[0]
        self.assertIs(call["ctx"], ctx)
        self.assertEqual(call["rect"], rect)
        self.assertEqual(call["text"], "Test")
        self.assertIs(call["hover"], True)
        self.assertEqual(call["base_col"], 2)
        self.assertEqual(call["hover_col"], 3)
        self.assertEqual(call["border_col"], 7)


if __name__ == "__main__":
    unittest.main()
