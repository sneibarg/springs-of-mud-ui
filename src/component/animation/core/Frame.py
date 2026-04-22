"""
Frame dataclass for animation system.
Represents a single frame in an animation sequence.
"""
from dataclasses import dataclass, field


@dataclass
class Frame:
    sprite_x: int
    sprite_y: int
    width: int
    height: int
    duration: float
    offset_x: int = 0
    offset_y: int = 0
    flip_h: bool = False
    flip_v: bool = False
    metadata: dict = field(default_factory=dict)  # Additional data (tags, NLP descriptions, etc.)

    def __post_init__(self):
        if self.width <= 0:
            raise ValueError(f"Frame width must be positive, got {self.width}")
        if self.height <= 0:
            raise ValueError(f"Frame height must be positive, got {self.height}")
        if self.duration <= 0:
            raise ValueError(f"Frame duration must be positive, got {self.duration}")

    def bounds(self) -> tuple[int, int, int, int]:
        return self.sprite_x, self.sprite_y, self.width, self.height

    def with_metadata(self, **kwargs) -> 'Frame':
        new_metadata = {**self.metadata, **kwargs}
        return Frame(sprite_x=self.sprite_x, sprite_y=self.sprite_y, width=self.width, height=self.height,
                     duration=self.duration, offset_x=self.offset_x, offset_y=self.offset_y, flip_h=self.flip_h,
                     flip_v=self.flip_v, metadata=new_metadata)
    