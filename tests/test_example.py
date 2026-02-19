"""
Example tests demonstrating how to use the mock implementations.
"""
from tests.mocks import MockGraphics, MockKeySource, MockMouseSource
from component.geometry.Rect import Rect
from component.render import Colors
import component.input.Keys as Keys


def test_mock_graphics_records_calls():
    """Test that MockGraphics records all drawing calls."""
    gfx = MockGraphics()

    # Draw some shapes
    gfx.rect(10, 20, 30, 40, Colors.COLOR_RED)
    gfx.text(50, 60, "Hello", Colors.COLOR_WHITE)
    gfx.circ(100, 100, 25, Colors.COLOR_LIGHT_BLUE)

    # Verify calls were recorded
    assert len(gfx.calls) == 3
    assert gfx.calls[0] == ('rect', (10, 20, 30, 40, Colors.COLOR_RED))
    assert gfx.calls[1] == ('text', (50, 60, "Hello", Colors.COLOR_WHITE))
    assert gfx.calls[2] == ('circ', (100, 100, 25, Colors.COLOR_LIGHT_BLUE))

    # Use helper methods
    gfx.assert_rect_drawn(10, 20, 30, 40, Colors.COLOR_RED)
    gfx.assert_text_drawn(50, 60, "Hello", Colors.COLOR_WHITE)


def test_mock_key_source_simulates_input():
    """Test that MockKeySource simulates keyboard input."""
    keys = MockKeySource()

    # Initially no keys pressed
    assert not keys.btnp(Keys.KEY_A)
    assert not keys.btn(Keys.KEY_A)

    # Simulate pressing a key
    keys.press_key(Keys.KEY_A)
    assert keys.btnp(Keys.KEY_A)
    assert keys.btn(Keys.KEY_A)

    # Clear pressed state (end of frame)
    keys.clear_pressed()
    assert not keys.btnp(Keys.KEY_A)
    assert keys.btn(Keys.KEY_A)  # Still held down

    # Release the key
    keys.release_key(Keys.KEY_A)
    assert not keys.btnp(Keys.KEY_A)
    assert not keys.btn(Keys.KEY_A)


def test_mock_mouse_source_simulates_mouse():
    """Test that MockMouseSource simulates mouse input."""
    mouse = MockMouseSource(x=100, y=200)

    # Check initial position
    x, y = mouse.get_position()
    assert x == 100
    assert y == 200

    # Move mouse
    mouse.move_to(150, 250)
    x, y = mouse.get_position()
    assert x == 150
    assert y == 250

    # Simulate button press
    assert not mouse.is_button_pressed(Keys.MOUSE_BUTTON_LEFT)
    mouse.press_button(Keys.MOUSE_BUTTON_LEFT)
    assert mouse.is_button_pressed(Keys.MOUSE_BUTTON_LEFT)
    assert mouse.is_button_down(Keys.MOUSE_BUTTON_LEFT)

    # Simulate scroll
    mouse.scroll_up(3)
    assert mouse.get_wheel_delta() == 3


def test_component_with_mocks():
    """Test a component using mock implementations."""
    from component.button.Button import Button

    # Create a mock graphics and context
    gfx = MockGraphics()
    rect = Rect(10, 10, 50, 20)

    clicked = False

    def on_click():
        nonlocal clicked
        clicked = True

    button = Button(rect, "Test", 2, 3, on_click)

    # Create a minimal context
    class MockInput:
        mx = 25
        my = 20
        click = True

    class MockContext:
        def __init__(self, graphics):
            self.input = MockInput()
            self.gfx = graphics

    ctx = MockContext(gfx)

    # Test button update (should trigger click)
    button.update(ctx)
    assert clicked

    # Test button draw
    button.draw(ctx)
    assert len(gfx.calls) > 0
    # Check that a rectangle and text were drawn
    rect_calls = gfx.get_calls('rect')
    text_calls = gfx.get_calls('text')
    assert len(rect_calls) >= 1
    assert len(text_calls) >= 1


if __name__ == "__main__":
    # Run tests
    test_mock_graphics_records_calls()
    print("✓ test_mock_graphics_records_calls passed")

    test_mock_key_source_simulates_input()
    print("✓ test_mock_key_source_simulates_input passed")

    test_mock_mouse_source_simulates_mouse()
    print("✓ test_mock_mouse_source_simulates_mouse passed")

    test_component_with_mocks()
    print("✓ test_component_with_mocks passed")

    print("\nAll tests passed!")
