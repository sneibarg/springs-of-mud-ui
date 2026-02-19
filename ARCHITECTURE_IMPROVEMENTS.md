# Architecture Improvements - Component Package Abstraction

## Summary
The component package has been improved to provide better abstraction from Pyxel, making the game engine more extensible and allowing users to easily create their own MUD experience with different rendering backends.

## Changes Implemented

### 1. Created Key Constants Module
**File:** `component/input/Keys.py`
- Centralized all keyboard key constants
- Components no longer need to import pyxel for key constants
- Makes it easier to map keys when swapping game engines

### 2. Fixed Direct Pyxel Rendering Calls
**Files Modified:**
- `component/app/GameWorld.py` - Now uses `ctx.gfx` instead of direct pyxel calls
- `component/app/Divider.py` - Now uses `ctx.gfx` instead of direct pyxel calls

### 3. Updated Input Components to Use Key Constants
**Files Modified:**
- `component/input/TextInput.py` - Uses Keys constants instead of pyxel.KEY_*
- `component/input/NumberField.py` - Uses Keys constants instead of pyxel.KEY_*
- `component/input/TextInputField.py` - Uses Keys constants instead of pyxel.KEY_*

### 4. Created MouseSource Protocol
**File:** `component/input/MouseSource.py`
- Protocol for mouse input abstraction
- PyxelMouseSource implementation included
- Supports position, button presses, and wheel scrolling

### 5. Created Window Protocol
**File:** `component/app/Window.py`
- Protocol for window management abstraction
- PyxelWindow implementation included
- Handles window size, title, FPS, and quit operations

### 6. Extracted Color Constants
**File:** `component/render/Colors.py`
- Centralized color palette constants
- Based on Pyxel's 16-color palette
- Includes semantic aliases (COLOR_SUCCESS, COLOR_ERROR, etc.)

### 7. Added Mock Implementations for Testing
**Files Created:**
- `tests/mocks/MockGraphics.py` - Records all graphics calls for verification
- `tests/mocks/MockKeySource.py` - Simulates keyboard input
- `tests/mocks/MockMouseSource.py` - Simulates mouse input
- `tests/test_example.py` - Example tests demonstrating usage

## Current Architecture

### Abstraction Layers
```
┌─────────────────────────────────────────┐
│         User Application Layer          │
│         (ui/, domain/, etc.)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Component Package (Pure)         │
│  • Protocols:                           │
│    - Graphics, KeySource, MouseSource   │
│    - Window                             │
│  • Constants:                           │
│    - Keys (keyboard constants)          │
│    - Colors (color palette)             │
│  • UI Components:                       │
│    - Button, TextInput, NumberField     │
│  • Geometry:                            │
│    - Rect, Circle, Line, etc.           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Engine Package (Pyxel-Specific)      │
│  • PyxelDriver (initialization)         │
│  • PyxelGfx (Graphics implementation)   │
│  • PyxelKeySource (KeySource impl)      │
│  • PyxelMouseSource (MouseSource impl)  │
│  • PyxelWindow (Window implementation)  │
└─────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Testing Layer (Optional)          │
│  • MockGraphics                         │
│  • MockKeySource                        │
│  • MockMouseSource                      │
└─────────────────────────────────────────┘
```

### Protocol-Based Design

#### Graphics Protocol
- **Interface:** `component/render/api/Graphics.py`
- **Implementation:** `component/render/PyxelGfx.py`
- **Usage:** Components use `ctx.gfx` to draw

#### KeySource Protocol
- **Interface:** `component/input/KeySource.py`
- **Implementation:** `PyxelKeySource` in same file
- **Usage:** Input components inject KeySource dependency

#### MouseSource Protocol
- **Interface:** `component/input/MouseSource.py`
- **Implementation:** `PyxelMouseSource` in same file
- **Usage:** Components can inject MouseSource for mouse input

#### Window Protocol
- **Interface:** `component/app/Window.py`
- **Implementation:** `PyxelWindow` in same file
- **Usage:** Engine layer for window management

## Remaining Pyxel Dependencies

### In Component Package (Acceptable)
1. **component/render/PyxelGfx.py** - Pyxel implementation of Graphics protocol ✓
2. **component/input/KeySource.py** - PyxelKeySource implementation ✓
3. **component/input/TextInput.py** - Uses pyxel.btnp() but with Keys constants ✓

### In Engine Package (Expected)
- `engine/PyxelDriver.py` - Pyxel-specific driver
- `engine/MudClientApp.py` - Instantiates PyxelDriver and PyxelGfx

## How to Extend with a Different Engine

To use a different game engine (e.g., Pygame, Arcade):

### Step 1: Implement the Graphics Protocol
```python
# component/render/PygameGfx.py
from component.render.api.Graphics import Graphics
import pygame

class PygameGfx(Graphics):
    def __init__(self, surface):
        self.surface = surface

    def rect(self, x, y, w, h, col):
        pygame.draw.rect(self.surface, col, (x, y, w, h))

    # ... implement all other methods
```

### Step 2: Implement the KeySource Protocol
```python
# component/input/PygameKeySource.py
from component.input.KeySource import KeySource
from component.input.Keys import Keys
import pygame

class PygameKeySource(KeySource):
    def btnp(self, key, hold=0, period=0):
        # Map Keys constants to pygame keys
        # Implement button press detection
        pass

    def btn(self, key):
        # Implement button hold detection
        pass
```

### Step 3: Create a New Driver
```python
# engine/PygameDriver.py
class PygameDriver:
    def __init__(self, title, w, h):
        pygame.init()
        self.screen = pygame.display.set_mode((w, h))
        # ... initialization

    def run(self, update_fn, draw_fn):
        # Game loop
        pass
```

### Step 4: Update App Initialization
Replace PyxelDriver and PyxelGfx with your implementations in `MudClientApp`.

**No changes needed to component/ code!**

## Benefits of This Architecture

1. **Separation of Concerns** - Component logic separate from rendering implementation
2. **Testability** - Easy to create mock Graphics/KeySource for testing
3. **Extensibility** - Users can swap game engines without modifying components
4. **Maintainability** - Clear boundaries between layers
5. **Reusability** - Components work with any Graphics/KeySource implementation

## Testing with Mock Implementations

The project now includes comprehensive mock implementations that make testing components easy without requiring Pyxel or any game engine:

### Example Test
```python
from tests.mocks import MockGraphics, MockKeySource
from component.button.Button import Button
from component.geometry.Rect import Rect

def test_button_click():
    # Create mocks
    gfx = MockGraphics()

    # Create test component
    clicked = False
    def on_click():
        nonlocal clicked
        clicked = True

    button = Button(Rect(10, 10, 50, 20), "Test", 2, 3, on_click)

    # Simulate click
    class MockContext:
        class input:
            mx, my, click = 25, 20, True
        gfx = gfx

    button.update(MockContext())
    assert clicked

    # Verify rendering
    button.draw(MockContext())
    assert len(gfx.get_calls('rect')) > 0
    assert len(gfx.get_calls('text')) > 0
```

### Running Tests
```bash
python tests/test_example.py
```

## Future Improvements

### Potential Enhancements
- Add example implementation with a different engine (Pygame)
- Document component creation guidelines
- Create audio protocol for sound abstraction
- Add more comprehensive test coverage
