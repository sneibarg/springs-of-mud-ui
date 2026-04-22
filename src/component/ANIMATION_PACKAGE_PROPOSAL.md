# Animation Package Proposal

## Overview

A comprehensive sprite and tile animation framework that provides:
- Frame-based animation system
- Sprite and tile management
- Spritesheet support
- Animation sequencing and timing
- NLP integration hooks for natural language frame generation

## PyxelEdit Feature Comparison

### PyxelEdit Provides:
- Tile/sprite editor with visual grid
- Tileset management
- Animation timeline
- Frame-by-frame editing
- Export to spritesheets

### Our Animation Package Will Provide:
- **Programmatic** sprite/tile creation and management
- **Runtime** animation playback and control
- **Reusable** animation definitions
- **Extensible** frame generation (including NLP)
- **Engine-agnostic** design (follows our Protocol pattern)
- **Integration** with existing component system

## Package Architecture

```
component/animation/
├── __init__.py
├── README.md
│
├── core/                      # Core animation concepts
│   ├── __init__.py
│   ├── Frame.py              # Single animation frame
│   ├── Spritesheet.py        # Spritesheet management
│   ├── Tileset.py            # Tileset management
│   └── Animation.py          # Animation sequence definition
│
├── sprites/                   # Sprite system
│   ├── __init__.py
│   ├── Sprite.py             # Base sprite class
│   ├── AnimatedSprite.py     # Sprite with animation
│   └── SpriteRenderer.py     # Sprite rendering
│
├── tiles/                     # Tile system
│   ├── __init__.py
│   ├── Tile.py               # Single tile
│   ├── Tilemap.py            # 2D grid of tiles
│   └── TileRenderer.py       # Tilemap rendering
│
├── controllers/               # Animation control
│   ├── __init__.py
│   ├── AnimationController.py    # Control animation playback
│   ├── StateAnimator.py          # State-based animations
│   └── Timeline.py               # Timeline sequencing
│
├── generators/                # Frame generation (NLP ready)
│   ├── __init__.py
│   ├── FrameGenerator.py     # Abstract frame generator
│   ├── ProceduralGenerator.py    # Algorithmic generation
│   └── NLPGenerator.py       # Natural language → frames (future)
│
└── effects/                   # Animation effects
    ├── __init__.py
    ├── Tween.py              # Interpolation/tweening
    ├── Easing.py             # Easing functions
    └── Transform.py          # Position/scale/rotation
```

## Core Components

### 1. Frame System

#### Frame
Represents a single frame in an animation.

```python
@dataclass
class Frame:
    """A single frame in an animation."""
    sprite_x: int          # X position in spritesheet
    sprite_y: int          # Y position in spritesheet
    width: int             # Frame width
    height: int            # Frame height
    duration: float        # Duration in seconds
    offset_x: int = 0      # Drawing offset X
    offset_y: int = 0      # Drawing offset Y
    flip_h: bool = False   # Horizontal flip
    flip_v: bool = False   # Vertical flip
    metadata: dict = field(default_factory=dict)  # For NLP tags, etc.
```

#### Spritesheet
Manages sprite/tile image data.

```python
class Spritesheet(ABC):
    """Abstract base class for spritesheet management."""

    @abstractmethod
    def get_frame(self, x: int, y: int, w: int, h: int) -> Frame:
        """Extract a frame from the spritesheet."""
        pass

    @abstractmethod
    def draw_frame(self, ctx, frame: Frame, x: int, y: int):
        """Draw a frame to screen."""
        pass

    def get_tile(self, tile_x: int, tile_y: int, tile_size: int) -> Frame:
        """Get a tile by grid coordinates."""
        return self.get_frame(
            tile_x * tile_size,
            tile_y * tile_size,
            tile_size,
            tile_size
        )
```

### 2. Animation System

#### Animation
Defines a sequence of frames.

```python
@dataclass
class Animation:
    """An animation sequence."""
    name: str
    frames: list[Frame]
    loop: bool = True
    speed: float = 1.0     # Playback speed multiplier

    def duration(self) -> float:
        """Total duration of animation."""
        return sum(f.duration for f in self.frames) / self.speed

    def get_frame_at(self, time: float) -> Frame:
        """Get the frame at a specific time."""
        if not self.frames:
            raise ValueError("Animation has no frames")

        if not self.loop and time >= self.duration():
            return self.frames[-1]

        # Handle looping
        time = time % self.duration() if self.loop else time
        elapsed = 0.0

        for frame in self.frames:
            frame_duration = frame.duration / self.speed
            if elapsed + frame_duration > time:
                return frame
            elapsed += frame_duration

        return self.frames[-1]
```

#### AnimationController
Controls animation playback.

```python
class AnimationController:
    """Controls animation playback."""

    def __init__(self, animation: Animation):
        self.animation = animation
        self.time = 0.0
        self.playing = True
        self.speed = 1.0

    def update(self, delta_time: float) -> None:
        """Update animation time."""
        if self.playing:
            self.time += delta_time * self.speed

            if not self.animation.loop:
                duration = self.animation.duration()
                if self.time >= duration:
                    self.time = duration
                    self.playing = False

    def get_current_frame(self) -> Frame:
        """Get the current frame."""
        return self.animation.get_frame_at(self.time)

    def play(self) -> None:
        self.playing = True

    def pause(self) -> None:
        self.playing = False

    def reset(self) -> None:
        self.time = 0.0

    def set_animation(self, animation: Animation) -> None:
        """Switch to a different animation."""
        self.animation = animation
        self.reset()
```

### 3. Sprite System

#### AnimatedSprite
A sprite with animation support.

```python
class AnimatedSprite:
    """A sprite that can be animated."""

    def __init__(
        self,
        spritesheet: Spritesheet,
        x: int = 0,
        y: int = 0,
        animations: dict[str, Animation] | None = None
    ):
        self.spritesheet = spritesheet
        self.x = x
        self.y = y
        self.animations = animations or {}
        self.controller: AnimationController | None = None
        self.current_animation: str | None = None

    def add_animation(self, name: str, animation: Animation) -> None:
        """Add an animation."""
        self.animations[name] = animation

    def play(self, name: str) -> None:
        """Play an animation by name."""
        if name not in self.animations:
            raise ValueError(f"Animation '{name}' not found")

        if self.current_animation != name:
            self.current_animation = name
            self.controller = AnimationController(self.animations[name])
            self.controller.play()

    def update(self, delta_time: float) -> None:
        """Update the animation."""
        if self.controller:
            self.controller.update(delta_time)

    def draw(self, ctx) -> None:
        """Draw the sprite."""
        if self.controller:
            frame = self.controller.get_current_frame()
            self.spritesheet.draw_frame(ctx, frame, self.x, self.y)
```

### 4. Tile System

#### Tile
A single tile with optional animation.

```python
@dataclass
class Tile:
    """A tile in a tilemap."""
    tile_id: int
    animation: Animation | None = None
    collision: bool = False
    metadata: dict = field(default_factory=dict)
```

#### Tilemap
2D grid of tiles.

```python
class Tilemap:
    """A 2D grid of tiles."""

    def __init__(
        self,
        width: int,
        height: int,
        tile_size: int,
        tileset: Spritesheet
    ):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tileset = tileset
        self.tiles: list[list[Tile | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.time = 0.0  # For animated tiles

    def set_tile(self, x: int, y: int, tile: Tile | None) -> None:
        """Set a tile at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile

    def get_tile(self, x: int, y: int) -> Tile | None:
        """Get tile at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def update(self, delta_time: float) -> None:
        """Update animated tiles."""
        self.time += delta_time

    def draw(self, ctx, camera_x: int = 0, camera_y: int = 0) -> None:
        """Draw the tilemap."""
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile is None:
                    continue

                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y

                # Get frame (static or animated)
                if tile.animation:
                    frame = tile.animation.get_frame_at(self.time)
                else:
                    frame = self.tileset.get_tile(
                        tile.tile_id % 16,  # Assuming 16-wide tileset
                        tile.tile_id // 16,
                        self.tile_size
                    )

                self.tileset.draw_frame(ctx, frame, screen_x, screen_y)
```

### 5. State-Based Animation

#### StateAnimator
Manages animations based on state.

```python
class StateAnimator:
    """Manages state-based animations."""

    def __init__(self, sprite: AnimatedSprite):
        self.sprite = sprite
        self.state_map: dict[str, str] = {}  # state → animation name
        self.current_state: str | None = None

    def register_state(self, state: str, animation_name: str) -> None:
        """Register a state with its animation."""
        self.state_map[state] = animation_name

    def set_state(self, state: str) -> None:
        """Change to a new state."""
        if state == self.current_state:
            return

        if state not in self.state_map:
            raise ValueError(f"State '{state}' not registered")

        self.current_state = state
        animation_name = self.state_map[state]
        self.sprite.play(animation_name)

    def update(self, delta_time: float) -> None:
        """Update animation."""
        self.sprite.update(delta_time)

    def draw(self, ctx) -> None:
        """Draw sprite."""
        self.sprite.draw(ctx)
```

### 6. Frame Generation (NLP Ready)

#### FrameGenerator Protocol
Abstract interface for frame generation.

```python
class FrameGenerator(Protocol):
    """Protocol for generating animation frames."""

    def generate(self, description: str, **kwargs) -> list[Frame]:
        """Generate frames from a description."""
        ...
```

#### ProceduralGenerator
Algorithmic frame generation.

```python
class ProceduralGenerator:
    """Generate frames procedurally."""

    def generate_walk_cycle(
        self,
        spritesheet: Spritesheet,
        start_x: int,
        start_y: int,
        frame_count: int,
        frame_width: int,
        frame_height: int,
        frame_duration: float = 0.1
    ) -> list[Frame]:
        """Generate a walk cycle animation."""
        frames = []
        for i in range(frame_count):
            frames.append(Frame(
                sprite_x=start_x + i * frame_width,
                sprite_y=start_y,
                width=frame_width,
                height=frame_height,
                duration=frame_duration,
                metadata={"frame_type": "walk", "step": i}
            ))
        return frames

    def generate_bounce(
        self,
        spritesheet: Spritesheet,
        base_frame: Frame,
        bounce_height: int,
        frame_count: int
    ) -> list[Frame]:
        """Generate a bounce animation."""
        frames = []
        for i in range(frame_count):
            # Sine wave for smooth bounce
            import math
            t = i / frame_count
            offset_y = int(math.sin(t * math.pi) * bounce_height)

            frame = Frame(
                sprite_x=base_frame.sprite_x,
                sprite_y=base_frame.sprite_y,
                width=base_frame.width,
                height=base_frame.height,
                duration=0.05,
                offset_y=-offset_y,
                metadata={"frame_type": "bounce", "step": i}
            )
            frames.append(frame)
        return frames
```

#### NLPGenerator (Future Sprint)
Natural language to frames.

```python
class NLPGenerator:
    """Generate frames from natural language descriptions."""

    def __init__(self, nlp_service: NLPService):
        self.nlp_service = nlp_service
        self.procedural = ProceduralGenerator()

    def generate(self, description: str, spritesheet: Spritesheet) -> list[Frame]:
        """
        Generate frames from natural language.

        Examples:
        - "character walking 4 frames"
        - "coin spinning slowly 8 frames"
        - "enemy attack with 3 frame wind-up and 2 frame strike"
        - "door opening smoothly over 6 frames"
        """
        # Parse description with NLP
        intent = self.nlp_service.parse(description)

        # Extract parameters
        animation_type = intent.get("type", "walk")
        frame_count = intent.get("frame_count", 4)
        speed = intent.get("speed", "normal")

        # Map to procedural generation
        if animation_type == "walk":
            return self.procedural.generate_walk_cycle(
                spritesheet,
                frame_count=frame_count,
                ...
            )
        elif animation_type == "spin":
            return self.procedural.generate_spin(
                spritesheet,
                frame_count=frame_count,
                ...
            )
        # ... more animation types

        return []
```

## Integration with Existing System

### As Game Component

```python
from dataclasses import dataclass
from component import AnimatedSprite, Animation, Frame


@dataclass
class Player:
    """Player component with animation."""
    sprite: AnimatedSprite
    z_index: int = 50

    def update(self, ctx) -> None:
        # Update based on input
        if ctx.input.mx > self.sprite.x:
            self.sprite.play("walk_right")
        elif ctx.input.mx < self.sprite.x:
            self.sprite.play("walk_left")
        else:
            self.sprite.play("idle")

        # Update animation
        delta_time = 1.0 / 60.0  # Assuming 60 FPS
        self.sprite.update(delta_time)

    def draw(self, ctx) -> None:
        self.sprite.draw(ctx)
```

### With State Machine

```python

from component import StateAnimator

player_sprite = AnimatedSprite(spritesheet, x=100, y=100)
player_sprite.add_animation("idle", idle_animation)
player_sprite.add_animation("walk", walk_animation)
player_sprite.add_animation("attack", attack_animation)

animator = StateAnimator(player_sprite)
animator.register_state("idle", "idle")
animator.register_state("moving", "walk")
animator.register_state("attacking", "attack")

# In game loop
if is_attacking:
    animator.set_state("attacking")
elif is_moving:
    animator.set_state("moving")
else:
    animator.set_state("idle")

animator.update(delta_time)
animator.draw(ctx)
```

## Pyxel-Specific Implementation

```python
from component import Spritesheet
import pyxel


class PyxelSpritesheet(Spritesheet):
    """Pyxel implementation of Spritesheet."""

    def __init__(self, image_bank: int):
        self.image_bank = image_bank

    def get_frame(self, x: int, y: int, w: int, h: int) -> Frame:
        return Frame(
            sprite_x=x,
            sprite_y=y,
            width=w,
            height=h,
            duration=0.1
        )

    def draw_frame(self, ctx, frame: Frame, x: int, y: int):
        pyxel.blt(
            x + frame.offset_x,
            y + frame.offset_y,
            self.image_bank,
            frame.sprite_x,
            frame.sprite_y,
            frame.width * (-1 if frame.flip_h else 1),
            frame.height * (-1 if frame.flip_v else 1),
            colkey=0  # Transparent color
        )
```

## NLP Integration Design

### Phase 1: Simple Pattern Matching
```python
patterns = {
    r"(\w+) walking (\d+) frames": lambda m: ("walk", int(m.group(2))),
    r"(\w+) idle": lambda m: ("idle", 1),
    r"spin (\d+) times": lambda m: ("spin", int(m.group(1)) * 8),
}
```

### Phase 2: Intent Recognition
```python
# Using a service like spaCy, NLTK, or Hugging Face
intent_map = {
    "walk": generate_walk,
    "run": generate_run,
    "jump": generate_jump,
    "attack": generate_attack,
}
```

### Phase 3: AI-Assisted Generation
```python
# Integration with GPT/Claude for complex descriptions
"A character triumphantly raising their sword after defeating an enemy"
→ Generated: wind-up, raise, hold, lower sequence
```

## Benefits

1. **Reusable** - Define animations once, use everywhere
2. **Composable** - Mix and match animations and effects
3. **Testable** - Engine-agnostic, easy to mock
4. **Extensible** - Add new generators, effects, transitions
5. **NLP-Ready** - Designed with natural language integration in mind
6. **Type-Safe** - Full type hints and ABC enforcement
7. **Performant** - Efficient frame lookup and caching

## Next Steps

1. Implement core Frame and Animation classes
2. Create Spritesheet ABC with Pyxel implementation
3. Build AnimatedSprite and AnimationController
4. Implement Tilemap system
5. Add procedural generators
6. Design NLP service interface
7. Create comprehensive examples and documentation
