"""
Tile data structure for tilemaps.

Represents a single tile with optional animation and metadata.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from component.animation.core.Animation import Animation


@dataclass
class Tile:
    """
    Represents a single tile in a tilemap.

    A tile can be:
    - Static: Just a tile_id that references a frame in the tileset
    - Animated: Has an Animation that plays over time
    - Interactive: Has metadata for game logic (collision, triggers, etc.)
    """

    tile_id: int
    """Tile identifier (used to look up frame in tileset if not animated)"""

    animation: Animation | None = None
    """Optional animation for animated tiles"""

    collision: bool = False
    """Whether this tile has collision (blocks movement)"""

    metadata: dict = field(default_factory=dict)
    """Custom metadata for game logic"""

    def __post_init__(self):
        """Validate tile data."""
        if self.tile_id < 0:
            raise ValueError(f"Tile ID must be non-negative, got {self.tile_id}")

    def is_animated(self) -> bool:
        """
        Check if tile is animated.

        Returns:
            True if tile has an animation, False otherwise
        """
        return self.animation is not None

    def with_metadata(self, **kwargs) -> 'Tile':
        """
        Create a copy of this tile with updated metadata.

        Args:
            **kwargs: Metadata key-value pairs to add/update

        Returns:
            New Tile with merged metadata
        """
        new_metadata = {**self.metadata, **kwargs}
        return Tile(
            tile_id=self.tile_id,
            animation=self.animation,
            collision=self.collision,
            metadata=new_metadata
        )

    def with_collision(self, collision: bool) -> 'Tile':
        """
        Create a copy of this tile with different collision.

        Args:
            collision: New collision value

        Returns:
            New Tile with updated collision
        """
        return Tile(
            tile_id=self.tile_id,
            animation=self.animation,
            collision=collision,
            metadata=self.metadata
        )