"""Street variants must preserve traversal, event coordinates and native orientation."""
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from maps import encode_layout
from street_art import road_variant, remap_roads, rotate_pixels, load_streets


class Streets(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / 'romhack/content/sunset.json').read_text())

    def test_only_roads_change_without_altering_collision_elevation_or_events(self):
        original = encode_layout(self.plan)[2]
        changed, counts = remap_roads(self.plan, original)
        before, after = struct.unpack('<1024H', original), struct.unpack('<1024H', changed)
        expected = {y * 32 + x for y, row in enumerate(self.plan['rows']) for x, token in enumerate(row) if token == 'P'}
        actual = {i for i, (a, b) in enumerate(zip(before, after)) if a != b}
        self.assertEqual(actual, expected)
        self.assertEqual(sum(counts.values()), len(expected))
        self.assertTrue(all(a & 0xfc00 == b & 0xfc00 for a, b in zip(before, after)))
        self.assertEqual(after[17 * 32 + 10], before[17 * 32 + 10])  # Existing transit sign.
        self.assertEqual(road_variant(self.plan, 10, 1), 1)  # Closed north road edge.
        self.assertEqual(road_variant(self.plan, 9, 1), 5)  # Outer northwest corner.
        self.assertEqual(road_variant(self.plan, 9, 16), 9)  # Concave junction corner.
        with self.assertRaises(ValueError):
            remap_roads(self.plan, bytes(len(original)))

    def test_clockwise_rotation_keeps_exact_pixel_coordinates(self):
        pixels = bytearray(256); pixels[0], pixels[15], pixels[240] = 1, 2, 3
        rotated = rotate_pixels(bytes(pixels), 1)
        self.assertEqual((rotated[15], rotated[255], rotated[0]), (1, 2, 3))
        self.assertEqual(rotate_pixels(rotate_pixels(bytes(pixels), 1), 3), bytes(pixels))
        with self.assertRaises(ValueError):
            rotate_pixels(bytes(255), 0)

    def test_shipped_streets_are_opaque_native_cells_with_one_shared_palette(self):
        variants, palette = load_streets(ROOT)
        self.assertEqual(len(variants), 18)
        self.assertEqual(len(palette), 32)
        self.assertTrue(all(len(tile) == 256 and min(tile) >= 1 and max(tile) <= 15 for tile in variants))


if __name__ == '__main__':
    unittest.main()
