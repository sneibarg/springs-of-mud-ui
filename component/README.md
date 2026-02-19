# Component Package

The `component` package provides a clean, engine-agnostic UI component library for building MUD clients and game UIs. All components are designed to work with any game engine through protocol-based abstractions.

## Architecture

### Core Principles

1. **Protocol-Based Design** - Components depend on protocols (interfaces), not concrete implementations
2. **Engine Independence** - No direct dependencies on Pyxel or any specific game engine
3. **Testability** - Easy to test with mock implementations
4. **Extensibility** - Swap game engines without modifying component code

### Package Structure

```
component/
├── app/              # Application-level components
│   ├── Window.py     # Window management protocol
│   ├── GameWorld.py  # Game world rendering
│   ├── TextPane.py   # Text display pane
│   └── ...
├── button/           # Button components
│   └── Button.py
├── geometry/         # Geometric primitives
│   ├── Rect.py
│   ├── Circle.py
│   └── ...
├── input/            # Input handling
│   ├── Keys.py           # Key constants
│   ├── KeySource.py      # Keyboard input protocol
│   ├── MouseSource.py    # Mouse input protocol
│   ├── TextInput.py      # Text input component
│   └── ...
├── list/             # List components
│   └── ListBox.py
├── menu/             # Menu components
│   ├── MenuBar.py
│   └── ...
├── modal/            # Modal dialogs
│   └── ...
└── render/           # Rendering abstractions
    ├── api/
    │   └── Graphics.py   # Graphics protocol
    ├── Colors.py         # Color constants
    ├── PyxelGfx.py      # Pyxel implementation
    └── ...
```

## Key Abstractions

### Graphics Protocol

All drawing is done through the `Graphics` protocol:

```python
from component.render.api.Graphics import Graphics

class Graphics(Protocol):
    def cls(self, col: int) -> None: ...
    def rect(self, x: int, y: int, w: int, h: int, col: int) -> None: ...
    def text(self, x: int, y: int, s: str, col: int) -> None: ...
    # ... more methods
```

Components receive a `Graphics` implementation via the engine context:

```python
def draw(self, ctx):
    ctx.gfx.rect(10, 10, 100, 50, Colors.COLOR_BLUE)
    ctx.gfx.text(20, 20, "Hello", Colors.COLOR_WHITE)
```

### KeySource Protocol

Keyboard input is handled through the `KeySource` protocol:

```python
from component.input.KeySource import KeySource

class KeySource(Protocol):
    def btnp(self, key: int, hold: int = 0, period: int = 0) -> bool: ...
    def btn(self, key: int) -> bool: ...
```

Use with key constants:

```python
import component.input.Keys as Keys

if self.keys.btnp(Keys.KEY_RETURN):
    # Handle Enter key press
    pass
```

### MouseSource Protocol

Mouse input through the `MouseSource` protocol:

```python
from component.input.MouseSource import MouseSource

class MouseSource(Protocol):
    def get_position(self) -> tuple[int, int]: ...
    def is_button_pressed(self, button: int) -> bool: ...
    def get_wheel_delta(self) -> int: ...
```

### Constants

#### Key Constants (`component.input.Keys`)

```python
import component.input.Keys as Keys

# Letter keys
Keys.KEY_A, Keys.KEY_B, ...

# Arrow keys
Keys.KEY_LEFT, Keys.KEY_RIGHT, Keys.KEY_UP, Keys.KEY_DOWN

# Special keys
Keys.KEY_RETURN, Keys.KEY_BACKSPACE, Keys.KEY_SPACE

# Modifier keys
Keys.KEY_LCTRL, Keys.KEY_LSHIFT, Keys.KEY_LALT

# Mouse buttons
Keys.MOUSE_BUTTON_LEFT, Keys.MOUSE_BUTTON_RIGHT
```

#### Color Constants (`component.render.Colors`)

```python
from component.render import Colors

# Standard 16-color palette
Colors.COLOR_BLACK, Colors.COLOR_WHITE, Colors.COLOR_RED, ...

# Semantic aliases
Colors.COLOR_BACKGROUND, Colors.COLOR_FOREGROUND
Colors.COLOR_SUCCESS, Colors.COLOR_ERROR, Colors.COLOR_WARNING
```

## Creating Components

### Basic Component Pattern

```python
from __future__ import annotations
from dataclasses import dataclass
from component.geometry.Rect import Rect
from component.render import Colors

@dataclass
class MyComponent:
    rect: Rect
    z_index: int = 10  # Optional: for rendering order

    def update(self, ctx) -> None:
        """Update component state based on input."""
        mx, my = ctx.input.mx, ctx.input.my
        if self.rect.contains(mx, my):
            # Handle hover
            pass

    def draw(self, ctx) -> None:
        """Draw the component."""
        self.rect.fill(ctx, Colors.COLOR_BLUE)
        ctx.gfx.text(self.rect.x + 5, self.rect.y + 5, "My Component", Colors.COLOR_WHITE)
```

### Component with Keyboard Input

```python
from component.input.KeySource import KeySource, PyxelKeySource
import component.input.Keys as Keys

class InputComponent:
    def __init__(self, keys: KeySource | None = None):
        self.keys = keys or PyxelKeySource()

    def update(self, ctx) -> None:
        if self.keys.btnp(Keys.KEY_RETURN):
            # Handle Enter key
            pass
```

## Testing Components

Use mock implementations for testing:

```python
from tests.mocks import MockGraphics, MockKeySource
from component.button.Button import Button
from component.geometry.Rect import Rect

def test_button():
    # Create mocks
    gfx = MockGraphics()
    keys = MockKeySource()

    # Create component
    clicked = False
    def on_click():
        nonlocal clicked
        clicked = True

    button = Button(Rect(10, 10, 50, 20), "Test", 2, 3, on_click)

    # Create mock context
    class MockContext:
        class input:
            mx, my, click = 25, 20, True
        gfx = gfx

    # Test
    button.update(MockContext())
    assert clicked

    button.draw(MockContext())
    assert len(gfx.get_calls('rect')) > 0
```

## Swapping Game Engines

To use a different game engine:

1. **Implement the Graphics protocol** for your engine
2. **Implement the KeySource protocol** (map Keys constants to your engine's keys)
3. **Implement the MouseSource protocol** if needed
4. **Pass your implementations** via the engine context

Example with Pygame:

```python
# your_engine/PygameGfx.py
from component.render.api.Graphics import Graphics
import pygame

class PygameGfx(Graphics):
    def __init__(self, surface):
        self.surface = surface

    def rect(self, x, y, w, h, col):
        pygame.draw.rect(self.surface, col, (x, y, w, h))

    # Implement all other Graphics methods...
```

Then use it in your app:

```python
from your_engine.PygameGfx import PygameGfx

# In your game loop
gfx = PygameGfx(screen)
ctx.gfx = gfx

# All components will now use Pygame for rendering!
```

## Examples

See `tests/test_example.py` for complete examples of:
- Testing with mock implementations
- Creating custom components
- Using protocols

See `ARCHITECTURE_IMPROVEMENTS.md` for architectural details and best practices.
