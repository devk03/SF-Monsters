"""Protect collision/save coordinates and independent native coastal animation slots."""
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from maps import encode_layout
from terrain_art import load_terrain, remap_terrain, terrain_variant, TOKENS


class CoastalTerrain(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / 'romhack/content/sunset.json').read_text())

    def test_ground_replacement_keeps_collision_elevation_and_every_event_coordinate(self):
        original = encode_layout(self.plan)[2]
        changed, counts = remap_terrain(self.plan, original)
        before, after = struct.unpack('<1024H', original), struct.unpack('<1024H', changed)
        expected = {y * 32 + x for y, row in enumerate(self.plan['rows'])
                    for x, token in enumerate(row) if token in TOKENS}
        differences = {i for i, (a, b) in enumerate(zip(before, after)) if a != b}
        self.assertEqual(differences, expected)
        self.assertEqual(sum(counts.values()), len(expected))
        self.assertTrue(all(a & 0xfc00 == b & 0xfc00 for a, b in zip(before, after)))
        # Existing transit interaction stays blocked at its original coordinates.
        self.assertEqual(after[17 * 32 + 10] & 0xfc00, before[17 * 32 + 10] & 0xfc00)
        self.assertEqual(after[17 * 32 + 10] & 0x3ff, 580)
        # Only grass art changes at the existing encounter patch.
        self.assertEqual(after[11 * 32 + 7] & 0x3ff, 576)
        with self.assertRaises(ValueError):
            remap_terrain(self.plan, bytes(len(original)))

    def test_border_rails_turn_toward_the_authored_walkable_side(self):
        self.assertEqual(terrain_variant(self.plan, 31, 0), 16)
        self.assertEqual(terrain_variant(self.plan, 31, 31), 17)
        self.assertEqual(terrain_variant(self.plan, 31, 15), 6)
        self.assertEqual(terrain_variant(self.plan, 20, 0), 5)
        with self.assertRaises(ValueError):
            terrain_variant(self.plan, 10, 16)  # A road is not coastal terrain.

    def test_native_atlas_and_wave_frames_fit_their_dedicated_allocations(self):
        cells, palette, waves = load_terrain(ROOT)
        self.assertEqual((len(cells), len(palette), len(waves)), (19, 32, 768))
        self.assertTrue(all(len(cell) == 256 and 1 <= min(cell) <= max(cell) <= 15
                            for cell in cells))
        self.assertEqual(len({waves[i:i + 256] for i in range(0, 768, 256)}), 3)
        # Every stage begins with ocean, then shoreline, eight 8x8 tiles total.
        for offset in (0, 256, 512):
            self.assertEqual(len(waves[offset:offset + 256]), 8 * 32)


if __name__ == '__main__':
    unittest.main()
