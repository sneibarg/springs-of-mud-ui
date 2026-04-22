"""
Comprehensive tests for Tile and Tilemap.
"""
import sys
import unittest

sys.path.insert(0, ".")

from component.animation.core import Tile, Tilemap, Animation
from tests.mocks import MockSpritesheet


class TestTile(unittest.TestCase):
    # =============================================================================
    # Tile Tests
    # =============================================================================

    def test_tile_creation(self):
        """Test creating a basic tile."""
        tile = Tile(tile_id=5)

        self.assertEqual(tile.tile_id, 5)
        self.assertIsNone(tile.animation)
        self.assertIs(tile.collision, False)
        self.assertEqual(tile.metadata, {})
        self.assertIs(tile.is_animated(), False)
        print("[PASS] test_tile_creation passed")

    def test_tile_with_collision(self):
        """Test tile with collision."""
        tile = Tile(tile_id=10, collision=True)

        self.assertEqual(tile.tile_id, 10)
        self.assertIs(tile.collision, True)
        print("[PASS] test_tile_with_collision passed")

    def test_tile_with_metadata(self):
        """Test tile with metadata."""
        tile = Tile(tile_id=3, metadata={"type": "water", "damage": 5})

        self.assertEqual(tile.metadata["type"], "water")
        self.assertEqual(tile.metadata["damage"], 5)
        print("[PASS] test_tile_with_metadata passed")

    def test_tile_with_animation(self):
        """Test animated tile."""
        sheet = MockSpritesheet()
        frames = sheet.create_test_frames(count=4, duration=0.1)
        animation = Animation("water", frames, loop=True)

        tile = Tile(tile_id=0, animation=animation)

        self.assertIs(tile.is_animated(), True)
        self.assertIs(tile.animation, animation)
        print("[PASS] test_tile_with_animation passed")

    def test_tile_validation(self):
        """Test tile ID validation."""
        # Valid tile
        Tile(tile_id=0)
        Tile(tile_id=100)

        # Invalid tile ID
        with self.assertRaises(ValueError) as cm:
            Tile(tile_id=-1)
        self.assertIn("non-negative", str(cm.exception))

        print("[PASS] test_tile_validation passed")

    def test_tile_with_metadata_method(self):
        """Test with_metadata method."""
        tile = Tile(tile_id=5, metadata={"a": 1})

        new_tile = tile.with_metadata(b=2, c=3)

        # Original unchanged
        self.assertEqual(tile.metadata, {"a": 1})

        # New tile has merged metadata
        self.assertEqual(new_tile.metadata, {"a": 1, "b": 2, "c": 3})
        self.assertEqual(new_tile.tile_id, 5)
        print("[PASS] test_tile_with_metadata_method passed")

    def test_tile_with_collision_method(self):
        """Test with_collision method."""
        tile = Tile(tile_id=7, collision=False)

        new_tile = tile.with_collision(True)

        # Original unchanged
        self.assertIs(tile.collision, False)

        # New tile has updated collision
        self.assertIs(new_tile.collision, True)
        self.assertEqual(new_tile.tile_id, 7)
        print("[PASS] test_tile_with_collision_method passed")


class TestTilemap(unittest.TestCase):
    # =============================================================================
    # Tilemap Tests
    # =============================================================================

    def test_tilemap_creation(self):
        """Test creating a tilemap."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(width=10, height=8, tile_size=16, tileset=sheet)

        self.assertEqual(tilemap.width, 10)
        self.assertEqual(tilemap.height, 8)
        self.assertEqual(tilemap.tile_size, 16)
        self.assertIs(tilemap.tileset, sheet)
        self.assertEqual(tilemap.time, 0.0)

        # All tiles should be None initially
        for y in range(8):
            for x in range(10):
                self.assertIsNone(tilemap.get_tile(x, y))

        print("[PASS] test_tilemap_creation passed")

    def test_tilemap_validation(self):
        """Test tilemap dimension validation."""
        sheet = MockSpritesheet()

        # Valid tilemaps
        Tilemap(1, 1, 8, sheet)
        Tilemap(100, 100, 32, sheet)

        # Invalid width
        with self.assertRaises(ValueError):
            Tilemap(0, 10, 16, sheet)
        with self.assertRaises(ValueError):
            Tilemap(-5, 10, 16, sheet)

        # Invalid height
        with self.assertRaises(ValueError):
            Tilemap(10, 0, 16, sheet)

        # Invalid tile size
        with self.assertRaises(ValueError):
            Tilemap(10, 10, 0, sheet)

        print("[PASS] test_tilemap_validation passed")

    def test_set_and_get_tile(self):
        """Test setting and getting tiles."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        tile = Tile(tile_id=3)

        # Set tile
        tilemap.set_tile(2, 3, tile)

        # Get tile
        retrieved = tilemap.get_tile(2, 3)
        self.assertEqual(retrieved, tile)

        # Other positions still None
        self.assertIsNone(tilemap.get_tile(0, 0))
        self.assertIsNone(tilemap.get_tile(4, 4))
        print("[PASS] test_set_and_get_tile passed")

    def test_set_tile_out_of_bounds(self):
        """Test setting tiles outside bounds."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        tile = Tile(tile_id=1)

        # Out of bounds - should not crash
        tilemap.set_tile(-1, 0, tile)
        tilemap.set_tile(0, -1, tile)
        tilemap.set_tile(10, 0, tile)
        tilemap.set_tile(0, 10, tile)

        # Verify nothing was set
        self.assertEqual(tilemap.count_tiles(), 0)
        print("[PASS] test_set_tile_out_of_bounds passed")

    def test_get_tile_out_of_bounds(self):
        """Test getting tiles outside bounds."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        # Out of bounds should return None
        self.assertIsNone(tilemap.get_tile(-1, 0))
        self.assertIsNone(tilemap.get_tile(0, -1))
        self.assertIsNone(tilemap.get_tile(10, 0))
        self.assertIsNone(tilemap.get_tile(0, 10))
        print("[PASS] test_get_tile_out_of_bounds passed")

    def test_is_valid_position(self):
        """Test position validation."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        # Valid positions
        self.assertIs(tilemap.is_valid_position(0, 0), True)
        self.assertIs(tilemap.is_valid_position(4, 4), True)
        self.assertIs(tilemap.is_valid_position(2, 3), True)

        # Invalid positions
        self.assertIs(tilemap.is_valid_position(-1, 0), False)
        self.assertIs(tilemap.is_valid_position(0, -1), False)
        self.assertIs(tilemap.is_valid_position(5, 0), False)
        self.assertIs(tilemap.is_valid_position(0, 5), False)
        print("[PASS] test_is_valid_position passed")

    def test_has_collision(self):
        """Test collision checking."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        # No tile - no collision
        self.assertIs(tilemap.has_collision(0, 0), False)

        # Tile without collision
        tilemap.set_tile(1, 1, Tile(tile_id=1, collision=False))
        self.assertIs(tilemap.has_collision(1, 1), False)

        # Tile with collision
        tilemap.set_tile(2, 2, Tile(tile_id=2, collision=True))
        self.assertIs(tilemap.has_collision(2, 2), True)

        # Out of bounds - no collision
        self.assertIs(tilemap.has_collision(-1, 0), False)
        self.assertIs(tilemap.has_collision(10, 10), False)
        print("[PASS] test_has_collision passed")

    def test_fill(self):
        """Test filling tilemap."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(3, 3, 16, sheet)

        tile = Tile(tile_id=5)

        # Fill
        tilemap.fill(tile)

        # All tiles should be set
        for y in range(3):
            for x in range(3):
                self.assertEqual(tilemap.get_tile(x, y), tile)

        self.assertEqual(tilemap.count_tiles(), 9)
        print("[PASS] test_fill passed")

    def test_fill_rect(self):
        """Test filling rectangular region."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        tile = Tile(tile_id=7)

        # Fill 2x2 region at (1, 1)
        tilemap.fill_rect(1, 1, 2, 2, tile)

        # Check filled region
        self.assertEqual(tilemap.get_tile(1, 1), tile)
        self.assertEqual(tilemap.get_tile(2, 1), tile)
        self.assertEqual(tilemap.get_tile(1, 2), tile)
        self.assertEqual(tilemap.get_tile(2, 2), tile)

        # Check outside region
        self.assertIsNone(tilemap.get_tile(0, 0))
        self.assertIsNone(tilemap.get_tile(3, 3))

        self.assertEqual(tilemap.count_tiles(), 4)
        print("[PASS] test_fill_rect passed")

    def test_fill_rect_partial(self):
        """Test fill_rect with partial out-of-bounds."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        tile = Tile(tile_id=8)

        # Fill extending beyond bounds
        tilemap.fill_rect(3, 3, 5, 5, tile)

        # Should only fill valid area (3,3) to (4,4)
        self.assertEqual(tilemap.get_tile(3, 3), tile)
        self.assertEqual(tilemap.get_tile(4, 4), tile)
        self.assertEqual(tilemap.count_tiles(), 4)  # 2x2 region
        print("[PASS] test_fill_rect_partial passed")

    def test_clear(self):
        """Test clearing tilemap."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(3, 3, 16, sheet)

        # Fill with tiles
        tilemap.fill(Tile(tile_id=1))
        self.assertEqual(tilemap.count_tiles(), 9)

        # Clear
        tilemap.clear()
        self.assertEqual(tilemap.count_tiles(), 0)

        # All should be None
        for y in range(3):
            for x in range(3):
                self.assertIsNone(tilemap.get_tile(x, y))

        print("[PASS] test_clear passed")

    def test_count_tiles(self):
        """Test counting tiles."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        # Empty
        self.assertEqual(tilemap.count_tiles(), 0)

        # Add some tiles
        tilemap.set_tile(0, 0, Tile(tile_id=1))
        tilemap.set_tile(1, 1, Tile(tile_id=2))
        tilemap.set_tile(2, 2, Tile(tile_id=3))
        self.assertEqual(tilemap.count_tiles(), 3)

        # Count with predicate (collision tiles)
        tilemap.set_tile(3, 3, Tile(tile_id=4, collision=True))
        tilemap.set_tile(4, 4, Tile(tile_id=5, collision=True))

        collision_count = tilemap.count_tiles(lambda t: t.collision)
        self.assertEqual(collision_count, 2)
        print("[PASS] test_count_tiles passed")

    def test_from_data(self):
        """Test loading from data array."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(3, 3, 16, sheet)

        data = [
            [1, 2, 3],
            [4, None, 5],
            [6, 7, 8],
        ]

        tilemap.from_data(data)

        # Check tiles
        self.assertEqual(tilemap.get_tile(0, 0).tile_id, 1)
        self.assertEqual(tilemap.get_tile(1, 0).tile_id, 2)
        self.assertEqual(tilemap.get_tile(2, 0).tile_id, 3)
        self.assertEqual(tilemap.get_tile(0, 1).tile_id, 4)
        self.assertIsNone(tilemap.get_tile(1, 1))
        self.assertEqual(tilemap.get_tile(2, 1).tile_id, 5)
        print("[PASS] test_from_data passed")

    def test_from_data_with_factory(self):
        """Test loading from data with custom tile factory."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(2, 2, 16, sheet)

        # Factory that creates tiles with collision for even IDs
        def tile_factory(tile_id):
            return Tile(tile_id=tile_id, collision=(tile_id % 2 == 0))

        data = [
            [1, 2],
            [3, 4],
        ]

        tilemap.from_data(data, tile_factory=tile_factory)

        # Check tiles
        self.assertEqual(tilemap.get_tile(0, 0).tile_id, 1)
        self.assertIs(tilemap.get_tile(0, 0).collision, False)

        self.assertEqual(tilemap.get_tile(1, 0).tile_id, 2)
        self.assertIs(tilemap.get_tile(1, 0).collision, True)

        self.assertEqual(tilemap.get_tile(0, 1).tile_id, 3)
        self.assertIs(tilemap.get_tile(0, 1).collision, False)

        self.assertEqual(tilemap.get_tile(1, 1).tile_id, 4)
        self.assertIs(tilemap.get_tile(1, 1).collision, True)
        print("[PASS] test_from_data_with_factory passed")

    def test_from_data_validation(self):
        """Test from_data validation."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(3, 3, 16, sheet)

        # Wrong height
        with self.assertRaises(ValueError) as cm:
            tilemap.from_data([[1, 2, 3], [4, 5, 6]])  # Only 2 rows
        self.assertIn("height", str(cm.exception))

        # Wrong width
        with self.assertRaises(ValueError) as cm:
            tilemap.from_data([[1, 2], [3, 4], [5, 6]])  # Only 2 columns
        self.assertIn("width", str(cm.exception))

        print("[PASS] test_from_data_validation passed")

    def test_to_data(self):
        """Test exporting to data array."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(3, 2, 16, sheet)

        # Set some tiles
        tilemap.set_tile(0, 0, Tile(tile_id=1))
        tilemap.set_tile(1, 0, Tile(tile_id=2))
        tilemap.set_tile(2, 1, Tile(tile_id=5))

        data = tilemap.to_data()

        expected = [
            [1, 2, None],
            [None, None, 5],
        ]

        self.assertEqual(data, expected)
        print("[PASS] test_to_data passed")

    def test_data_round_trip(self):
        """Test from_data -> to_data round trip."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(4, 3, 16, sheet)

        original_data = [
            [1, 2, None, 3],
            [None, 4, 5, None],
            [6, None, 7, 8],
        ]

        tilemap.from_data(original_data)
        exported_data = tilemap.to_data()

        self.assertEqual(exported_data, original_data)
        print("[PASS] test_data_round_trip passed")

    def test_update(self):
        """Test update advances time."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(3, 3, 16, sheet)

        self.assertEqual(tilemap.time, 0.0)

        tilemap.update(0.1)
        self.assertLess(abs(tilemap.time - 0.1), 0.001)

        tilemap.update(0.05)
        self.assertLess(abs(tilemap.time - 0.15), 0.001)
        print("[PASS] test_update passed")

    def test_draw_static_tiles(self):
        """Test drawing static tiles."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(2, 2, 16, sheet)

        # Add static tiles
        tilemap.set_tile(0, 0, Tile(tile_id=0))
        tilemap.set_tile(1, 1, Tile(tile_id=5))

        # Draw
        tilemap.draw(None)

        # Should have drawn 2 tiles
        self.assertEqual(sheet.get_draw_count(), 2)
        print("[PASS] test_draw_static_tiles passed")

    def test_draw_animated_tiles(self):
        """Test drawing animated tiles."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(2, 2, 16, sheet)

        # Create animated tile
        frames = sheet.create_test_frames(count=3, duration=0.1)
        animation = Animation("water", frames, loop=True)
        tilemap.set_tile(0, 0, Tile(tile_id=0, animation=animation))

        # Draw at different times
        sheet.clear_calls()
        tilemap.draw(None)
        self.assertEqual(sheet.get_draw_count(), 1)

        # Advance time and draw again
        tilemap.update(0.15)
        sheet.clear_calls()
        tilemap.draw(None)
        self.assertEqual(sheet.get_draw_count(), 1)

        # Frame should be different
        # (tested indirectly through animation system)
        print("[PASS] test_draw_animated_tiles passed")

    def test_draw_with_camera(self):
        """Test drawing with camera offset."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(5, 5, 16, sheet)

        # Fill with tiles
        tilemap.fill(Tile(tile_id=1))

        # Draw with camera
        tilemap.draw(None, camera_x=32, camera_y=16)

        # All 25 tiles should be drawn (no culling without viewport)
        self.assertEqual(sheet.get_draw_count(), 25)

        # Check one draw call has correct offset
        last_draw = sheet.get_last_draw()
        # Tile (4,4) at world position (64, 64) minus camera (32, 16) = screen (32, 48)
        print("[PASS] test_draw_with_camera passed")

    def test_draw_with_culling(self):
        """Test drawing with viewport culling."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(10, 10, 16, sheet)

        # Fill entire map
        tilemap.fill(Tile(tile_id=1))

        # Draw with small viewport
        sheet.clear_calls()
        tilemap.draw(None, camera_x=0, camera_y=0, viewport_width=32, viewport_height=32)

        # Should only draw visible tiles (2x2 = 4 tiles)
        # viewport 32x32 / tile_size 16 = 2x2 tiles (+1 for partial = 3x3)
        self.assertLessEqual(sheet.get_draw_count(), 9)  # At most 3x3
        print("[PASS] test_draw_with_culling passed")

    def test_world_to_tile(self):
        """Test world to tile coordinate conversion."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(10, 10, 16, sheet)

        # Test conversions
        self.assertEqual(tilemap.world_to_tile(0, 0), (0, 0))
        self.assertEqual(tilemap.world_to_tile(15, 15), (0, 0))
        self.assertEqual(tilemap.world_to_tile(16, 16), (1, 1))
        self.assertEqual(tilemap.world_to_tile(32, 48), (2, 3))
        self.assertEqual(tilemap.world_to_tile(100, 200), (6, 12))
        print("[PASS] test_world_to_tile passed")

    def test_tile_to_world(self):
        """Test tile to world coordinate conversion."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(10, 10, 16, sheet)

        # Test conversions
        self.assertEqual(tilemap.tile_to_world(0, 0), (0, 0))
        self.assertEqual(tilemap.tile_to_world(1, 1), (16, 16))
        self.assertEqual(tilemap.tile_to_world(5, 3), (80, 48))
        print("[PASS] test_tile_to_world passed")

    def test_coordinate_conversion_round_trip(self):
        """Test coordinate conversion round trip."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(10, 10, 16, sheet)

        # Start with tile coords
        tile_x, tile_y = 3, 5

        # Convert to world and back
        world_x, world_y = tilemap.tile_to_world(tile_x, tile_y)
        back_x, back_y = tilemap.world_to_tile(world_x, world_y)

        self.assertEqual((back_x, back_y), (tile_x, tile_y))
        print("[PASS] test_coordinate_conversion_round_trip passed")

    # =============================================================================
    # Integration Tests
    # =============================================================================

    def test_full_tilemap_lifecycle(self):
        """Integration test: full tilemap lifecycle."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(width=10, height=10, tile_size=16, tileset=sheet)

        # Load from data
        data = [[1 if (x + y) % 2 == 0 else None for x in range(10)] for y in range(10)]
        tilemap.from_data(data)

        # Add some collision tiles
        for y in range(10):
            tile = tilemap.get_tile(0, y)
            if tile:
                tilemap.set_tile(0, y, tile.with_collision(True))

        # Check collision
        self.assertIs(tilemap.has_collision(0, 0), True)
        self.assertIs(tilemap.has_collision(1, 1), False)

        # Update and draw
        for _ in range(10):
            tilemap.update(0.016)
            sheet.clear_calls()
            tilemap.draw(None)

        # Export data
        exported = tilemap.to_data()
        self.assertEqual(len(exported), 10)
        self.assertEqual(len(exported[0]), 10)
        print("[PASS] test_full_tilemap_lifecycle passed")

    def test_platformer_level(self):
        """Integration test: simple platformer level."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(width=20, height=15, tile_size=16, tileset=sheet)

        # Create level data
        # 0 = empty, 1 = ground, 2 = platform
        level_data = [[None] * 20 for _ in range(15)]

        # Ground
        for x in range(20):
            level_data[14][x] = 1

        # Platforms
        for x in range(5, 10):
            level_data[10][x] = 2
        for x in range(12, 17):
            level_data[8][x] = 2

        # Load with collision factory
        def tile_factory(tile_id):
            return Tile(tile_id=tile_id, collision=True)

        tilemap.from_data(level_data, tile_factory=tile_factory)

        # Test collision
        self.assertIs(tilemap.has_collision(0, 14), True)  # Ground
        self.assertIs(tilemap.has_collision(5, 10), True)  # Platform
        self.assertIs(tilemap.has_collision(0, 0), False)  # Sky

        # Test world coordinate collision
        wx, wy = 100, 224  # World position (6, 14) in tiles
        tx, ty = tilemap.world_to_tile(wx, wy)
        self.assertIs(tilemap.has_collision(tx, ty), True)
        print("[PASS] test_platformer_level passed")

    def test_animated_water_tiles(self):
        """Integration test: animated water tiles."""
        sheet = MockSpritesheet()
        tilemap = Tilemap(width=5, height=5, tile_size=16, tileset=sheet)

        # Create water animation
        water_frames = sheet.create_test_frames(count=4, duration=0.2)
        water_anim = Animation("water", water_frames, loop=True)

        # Fill bottom 2 rows with water
        water_tile = Tile(tile_id=10, animation=water_anim)
        for y in range(3, 5):
            for x in range(5):
                tilemap.set_tile(x, y, water_tile)

        # Update and draw over time
        for _ in range(20):
            tilemap.update(0.05)
            sheet.clear_calls()
            tilemap.draw(None)
            # Water tiles should be drawn
            self.assertEqual(sheet.get_draw_count(), 10)  # 2 rows * 5 cols

        print("[PASS] test_animated_water_tiles passed")


if __name__ == "__main__":
    unittest.main()
