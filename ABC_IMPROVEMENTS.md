# Abstract Base Class (ABC) Improvements

## Overview

The codebase now uses Python's `abc` module to define clear contracts for base classes and ensure proper implementation of required methods. This complements the existing Protocol-based design.

## When to Use ABC vs Protocol

### Use Protocol When:
- Defining **structural** interfaces (duck typing)
- Working with **external** code you don't control
- Need **implicit** implementation (no inheritance required)
- Examples: `Graphics`, `KeySource`, `MouseSource`

### Use ABC When:
- Creating **explicit base classes** that provide shared functionality
- Want to **enforce** method implementation at instantiation time
- Providing **default implementations** or helper methods
- Creating a **class hierarchy** with shared behavior
- Examples: `Shape`, `Renderable`

## Key Differences

```python
# Protocol - Structural (duck typing)
class Graphics(Protocol):
    def rect(self, x, y, w, h, col): ...

# Any class with this method signature satisfies the protocol
class MyGraphics:  # No inheritance needed!
    def rect(self, x, y, w, h, col):
        print("Drawing rect")

#--- ABC - Explicit base class
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def contains(self, x, y) -> bool:
        pass

# MUST inherit and implement abstract methods
class Circle(Shape):  # Inheritance required
    def contains(self, x, y) -> bool:
        return True  # Implementation required
```

## Improvements Implemented

### 1. Geometry Base Classes

**Files Created:**
- `component/geometry/Shape.py`

**Purpose:** Provide a common interface and shared functionality for all geometric shapes.

#### Shape ABC

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def bounds(self) -> tuple[int, int, int, int]:
        """Return bounding box (x, y, width, height)"""
        pass

    @abstractmethod
    def contains(self, mx: int, my: int) -> bool:
        """Check if point is inside shape"""
        pass

    def intersects(self, other: Shape) -> bool:
        """Default implementation using bounding boxes"""
        # Shared logic for all shapes!
        ...

    def center(self) -> tuple[int, int]:
        """Calculate center point"""
        # Shared logic for all shapes!
        ...
```

#### Drawable ABC

```python
class Drawable(ABC):
    def draw(self, ctx, col: int) -> None:
        """Default: calls fill()"""
        self.fill(ctx, col)

    def fill(self, ctx, col: int) -> None:
        raise NotImplementedError(...)

    def border(self, ctx, col: int) -> None:
        raise NotImplementedError(...)
```

**Benefits:**
- All shapes now have `intersects()` and `center()` methods for free
- Consistent interface across all geometry types
- Enforces implementation of `bounds()` and `contains()`
- Optional methods (`fill`, `border`) with helpful error messages

**Updated Classes:**
- `Rect` - now extends `Shape, Drawable`
- `Circle` - now extends `Shape, Drawable`
- `Ellipse` - now extends `Shape, Drawable`
- `Triangle` - now extends `Shape, Drawable`
- `Line` - now extends `Shape, Drawable`
- `Point` - now extends `Shape, Drawable`

### 2. Renderable ABC

**File:** `component/render/abstract/Renderable.py`

**Before:**
```python
class Renderable:
    def update(self, ctx): pass
    def draw(self, ctx): pass
```

**After:**
```python
from abc import ABC, abstractmethod

class Renderable(ABC):
    @abstractmethod
    def update(self, ctx) -> None:
        """Update component state"""
        pass

    @abstractmethod
    def draw(self, ctx) -> None:
        """Draw the component"""
        pass
```

**Benefits:**
- Enforces implementation of both methods
- Clear documentation of requirements
- Type checkers can verify compliance
- Instantiation fails early if methods missing

## Usage Examples

### Using Shape ABC

```python
from component.geometry import Rect, Circle

rect = Rect(10, 10, 50, 30)
circle = Circle(100, 100, 25)

# All shapes have these methods:
print(rect.bounds())      # (10, 10, 50, 30)
print(circle.center())    # (100, 100)
print(rect.intersects(circle))  # True/False

# Polymorphism works naturally
shapes: list[Shape] = [rect, circle]
for shape in shapes:
    if shape.contains(mouse_x, mouse_y):
        shape.fill(ctx, COLOR_RED)
```

### Creating Custom Shapes

```python
from component.geometry.Shape import Shape, Drawable
from dataclasses import dataclass

@dataclass
class Pentagon(Shape, Drawable):
    x: int
    y: int
    size: int

    # MUST implement these (abstract methods)
    def bounds(self) -> tuple[int, int, int, int]:
        return (self.x - self.size, self.y - self.size,
                self.size * 2, self.size * 2)

    def contains(self, mx: int, my: int) -> bool:
        # Your hit test logic
        return False

    # Optional: implement drawing
    def fill(self, ctx, col: int) -> None:
        # Your drawing logic
        pass

    # Get these for free:
    # - intersects(other)
    # - center()
```

### Creating Renderable Components

```python
from component.render.abstract.Renderable import Renderable
from dataclasses import dataclass

@dataclass
class MyComponent(Renderable):
    x: int
    y: int

    # MUST implement both methods
    def update(self, ctx) -> None:
        # Handle input, update state
        pass

    def draw(self, ctx) -> None:
        # Render the component
        ctx.gfx.rect(self.x, self.y, 100, 50, 7)
```

## Error Detection

ABCs catch errors at instantiation time:

```python
# This will FAIL at runtime:
class BadShape(Shape):
    pass  # Missing required methods!

shape = BadShape()  # TypeError: Can't instantiate abstract class
                    # BadShape with abstract methods bounds, contains
```

## Testing Benefits

ABCs make testing easier by providing clear contracts:

```python
def test_shape_contract():
    """Test that all shapes implement the Shape contract"""
    from component.geometry import Rect, Circle, Triangle

    shapes = [
        Rect(0, 0, 10, 10),
        Circle(5, 5, 10),
        Triangle(0, 0, 10, 0, 5, 10)
    ]

    for shape in shapes:
        # All shapes MUST have these methods
        assert hasattr(shape, 'bounds')
        assert hasattr(shape, 'contains')
        assert hasattr(shape, 'intersects')
        assert hasattr(shape, 'center')

        # Test the interface
        bounds = shape.bounds()
        assert len(bounds) == 4
        assert isinstance(shape.contains(0, 0), bool)
```

## Design Guidelines

### 1. Choose the Right Tool

```python
# Use Protocol for interfaces
class Storage(Protocol):
    def save(self, data: str) -> None: ...
    def load(self) -> str: ...

# Use ABC for base classes with shared logic
class Widget(ABC):
    @abstractmethod
    def render(self): pass

    def validate(self):  # Shared implementation
        """All widgets use this validation"""
        return True
```

### 2. Abstract vs Concrete Methods

```python
class BaseComponent(ABC):
    # Abstract - MUST be implemented
    @abstractmethod
    def update(self, ctx): pass

    # Concrete - CAN be overridden
    def reset(self):
        """Default reset behavior"""
        self.state = {}

    # Concrete with no implementation - optional
    def on_click(self):
        """Override to handle clicks"""
        pass
```

### 3. Multiple Inheritance

```python
# Combine ABCs for powerful contracts
class InteractiveShape(Shape, Renderable):
    """A shape that can be rendered and updated"""
    pass

# Now must implement:
# - bounds(), contains() from Shape
# - update(), draw() from Renderable
```

## Benefits Summary

1. **Compile-time Verification** - Catch missing methods early
2. **Self-Documenting** - Clear contracts in code
3. **Shared Functionality** - Common methods in base class
4. **Polymorphism** - Type-safe collections of related objects
5. **IDE Support** - Better autocomplete and type checking
6. **Maintainability** - Changes to base class propagate automatically

## Protocol vs ABC Quick Reference

| Feature | Protocol | ABC |
|---------|----------|-----|
| Inheritance required | No | Yes |
| Runtime checking | No (unless `@runtime_checkable`) | Yes |
| Can provide implementations | No | Yes |
| Best for | Duck typing, external code | Class hierarchies, shared logic |
| Type checking | Structural | Nominal |
| When to use | Interfaces, flexible contracts | Base classes, enforcement |

## Future Opportunities

Consider ABCs for:
- `Modal` base class for all modals/dialogs
- `InputField` base class for text/number inputs
- `Renderer` base class for different rendering strategies
- `NetworkClient` base class for different protocols
