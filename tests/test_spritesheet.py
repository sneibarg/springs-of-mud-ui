import unittest

from tests.mocks import MockGraphics
from component.geometry.Rect import Rect
from component.button.Button import Button  # <-- import the class, not the package/module


class TestButtonWithMocks(unittest.TestCase):
    def test_component_with_mocks(self):
        """Test a component using mock implementations (Button)."""
        gfx = MockGraphics()
        rect = Rect(10, 10, 50, 20)

        clicked = False

        def on_click():
            nonlocal clicked
            clicked = True

        # Minimal renderer spy that matches FieldRenderer.draw_button signature
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
                    (
                        "draw_button",
                        (ctx, rect, text),
                        {
                            "hover": hover,
                            "base_col": base_col,
                            "hover_col": hover_col,
                            "border_col": border_col,
                        },
                    )
                )

        renderer = SpyRenderer()
        button = Button(rect, "Test", 2, 3, on_click, renderer=renderer)

        # Minimal ctx/input to match Button.update expectations
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

        # draw should delegate to renderer.draw_button exactly once
        button.draw(ctx)
        self.assertEqual(len(renderer.calls), 1)

        name, args, kwargs = renderer.calls[0]
        self.assertEqual(name, "draw_button")
        self.assertIs(args[0], ctx)
        self.assertEqual(args[1], rect)
        self.assertEqual(args[2], "Test")
        self.assertIs(kwargs["hover"], True)
        self.assertEqual(kwargs["base_col"], 2)
        self.assertEqual(kwargs["hover_col"], 3)
        self.assertEqual(kwargs["border_col"], 7)


if __name__ == "__main__":
    unittest.main()
