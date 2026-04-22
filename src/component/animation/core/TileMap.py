"""
Tilemap implementation for tile-based levels.

Manages a 2D grid of tiles with rendering and update support.
"""
from __future__ import annotations
from component.animation.core.SpriteSheet import SpriteSheet
from component.animation.core.Tile import Tile
from component.animation.core.Frame import Frame


class Tilemap:
    """
    A 2D grid-based tilemap.

    Features:
    - Static and animated tiles
    - Camera/viewport support
    - Collision checking
    - Culling (only draws visible tiles)
    - Tile data import/export
    """

    def __init__(self, width: int, height: int, tile_size: int, tileset: SpriteSheet):
        """
        Initialize tilemap.

        Args:
            width: Width in tiles
            height: Height in tiles
            tile_size: Size of each tile in pixels
            tileset: SpriteSheet containing tile graphics

        Raises:
            ValueError: If dimensions or tile_size are invalid
        """
        if width <= 0:
            raise ValueError(f"Width must be positive, got {width}")
        if height <= 0:
            raise ValueError(f"Height must be positive, got {height}")
        if tile_size <= 0:
            raise ValueError(f"Tile size must be positive, got {tile_size}")

        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tileset = tileset
        self.tiles: list[list[Tile | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.time = 0.0

    def set_tile(self, x: int, y: int, tile: Tile | None) -> None:
        """
        Set tile at position.

        Args:
            x: Tile X coordinate (0-indexed)
            y: Tile Y coordinate (0-indexed)
            tile: Tile to place, or None to clear
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile

    def get_tile(self, x: int, y: int) -> Tile | None:
        """
        Get tile at position.

        Args:
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            Tile at position, or None if empty or out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if position is within tilemap bounds.

        Args:
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def has_collision(self, x: int, y: int) -> bool:
        """
        Check if tile at position has collision.

        Args:
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            True if tile exists and has collision, False otherwise
        """
        tile = self.get_tile(x, y)
        return tile is not None and tile.collision

    def fill(self, tile: Tile | None) -> None:
        """
        Fill entire tilemap with a tile.

        Args:
            tile: Tile to fill with, or None to clear all tiles
        """
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = tile

    def fill_rect(self, x: int, y: int, w: int, h: int, tile: Tile | None) -> None:
        """
        Fill a rectangular region with a tile.

        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            w: Width in tiles
            h: Height in tiles
            tile: Tile to fill with, or None to clear
        """
        for ty in range(y, min(y + h, self.height)):
            for tx in range(x, min(x + w, self.width)):
                if self.is_valid_position(tx, ty):
                    self.tiles[ty][tx] = tile

    def clear(self) -> None:
        """Clear all tiles (set to None)."""
        self.fill(None)

    def count_tiles(self, predicate=None) -> int:
        """
        Count tiles matching a predicate.

        Args:
            predicate: Function that takes a Tile and returns bool.
                      If None, counts all non-None tiles.

        Returns:
            Number of matching tiles
        """
        count = 0
        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    if predicate is None or predicate(tile):
                        count += 1
        return count

    def from_data(self, data: list[list[int | None]], tile_factory=None) -> None:
        """
        Load tilemap from 2D array of tile IDs.

        Args:
            data: 2D array of tile IDs (or None for empty)
            tile_factory: Optional function to create Tile from ID.
                         Signature: tile_factory(tile_id: int) -> Tile
                         If None, creates basic Tile(tile_id=id)
        """
        if len(data) != self.height:
            raise ValueError(f"Data height {len(data)} doesn't match tilemap height {self.height}")

        for y, row in enumerate(data):
            if len(row) != self.width:
                raise ValueError(f"Data row {y} width {len(row)} doesn't match tilemap width {self.width}")

            for x, tile_id in enumerate(row):
                if tile_id is None:
                    self.tiles[y][x] = None
                else:
                    if tile_factory:
                        self.tiles[y][x] = tile_factory(tile_id)
                    else:
                        self.tiles[y][x] = Tile(tile_id=tile_id)

    def to_data(self) -> list[list[int | None]]:
        """
        Export tilemap as 2D array of tile IDs.

        Returns:
            2D array where each element is a tile_id or None
        """
        return [
            [tile.tile_id if tile is not None else None for tile in row]
            for row in self.tiles
        ]

    def update(self, delta_time: float) -> None:
        """
        Update tilemap time (for animated tiles).

        Args:
            delta_time: Time elapsed since last update (in seconds)
        """
        self.time += delta_time

    def draw(self, ctx, camera_x: int = 0, camera_y: int = 0, viewport_width: int | None = None, viewport_height: int | None = None) -> None:
        """
        Draw tilemap with camera offset and optional culling.

        Args:
            ctx: Graphics context
            camera_x: Camera X offset in pixels
            camera_y: Camera Y offset in pixels
            viewport_width: Optional viewport width for culling
            viewport_height: Optional viewport height for culling
        """
        # Calculate visible tile range for culling
        if viewport_width is not None and viewport_height is not None:
            start_x = max(0, camera_x // self.tile_size)
            start_y = max(0, camera_y // self.tile_size)
            end_x = min(self.width, (camera_x + viewport_width) // self.tile_size + 1)
            end_y = min(self.height, (camera_y + viewport_height) // self.tile_size + 1)
        else:
            start_x, start_y = 0, 0
            end_x, end_y = self.width, self.height

        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                if tile is None:
                    continue

                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y

                # Get frame (animated or static)
                if tile.is_animated():
                    frame = tile.animation.get_frame_at(self.time)
                else:
                    # Default: assume 16 tiles per row (standard tileset layout)
                    frame = self.tileset.get_tile(
                        tile.tile_id % 16,
                        tile.tile_id // 16,
                        self.tile_size
                    )

                self.tileset.draw_frame(ctx, frame, screen_x, screen_y)

    def world_to_tile(self, world_x: float, world_y: float) -> tuple[int, int]:
        """
        Convert world coordinates to tile coordinates.

        Args:
            world_x: World X coordinate in pixels
            world_y: World Y coordinate in pixels

        Returns:
            Tuple of (tile_x, tile_y)
        """
        return int(world_x // self.tile_size), int(world_y // self.tile_size)

    def tile_to_world(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        """
        Convert tile coordinates to world coordinates (top-left corner).

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            Tuple of (world_x, world_y) in pixels
        """
        return tile_x * self.tile_size, tile_y * self.tile_size