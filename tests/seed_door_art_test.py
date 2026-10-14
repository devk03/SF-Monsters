"""Native animation geometry, opaque openings and stable architectural pixels."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from seed_door_art import ASSET, MOVING, load, reference, validate


def decode_stage(raw):
    pixels = bytearray(512)
    for tile in range(8):
        left, top = (tile % 2) * 8, (tile // 2) * 8
        for y in range(8):
            for x in range(8):
                value = raw[tile * 32 + y * 4 + x // 2]
                pixels[(top + y) * 16 + left + x] = value >> ((x % 2) * 4) & 15
    return bytes(pixels)


class SeedDoorArtTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset = load(ROOT)
        cls.frames = cls.asset['frames']
        cls.original, cls.palette = reference(ROOT)

    def test_three_native_offsets_decode_to_the_original_indices(self):
        raw = (ROOT / ASSET / 'frames.4bpp').read_bytes()
        self.assertEqual(len(raw), 768)
        for index, frame in enumerate(self.frames):
            self.assertEqual(decode_stage(raw[index * 256:(index + 1) * 256]), frame)

    def test_window_and_palette_are_exact_and_aperture_is_centered(self):
        self.assertEqual(self.palette,
                         (ROOT / 'assets/tiles/sunset-rowhouse-butter/house.gbapal').read_bytes())
        self.assertEqual(self.asset['metadata']['palette_bank'], 11)
        self.assertEqual(MOVING[0] + MOVING[2], 16)
        self.assertGreaterEqual(MOVING[1], 8)
        for frame in self.frames:
            self.assertEqual(frame[:128], self.original[:128])

    def test_only_the_inset_leaf_moves_and_portal_never_exposes_ground(self):
        left, top, right, bottom = MOVING
        moving = {y * 16 + x for y in range(top, bottom) for x in range(left, right)}
        for frame in self.frames:
            self.assertTrue(all(frame[i] for i in moving))
            self.assertTrue(all(frame[i] == self.frames[0][i]
                                for i in range(512) if i not in moving))
        # Each stage visibly opens further; identical/redrawn wall poses do not count.
        dark = [sum(frame[i] in (13, 14, 15) for i in moving) for frame in self.frames]
        self.assertLess(dark[0], dark[1])
        self.assertLess(dark[1], dark[2])

    def test_changed_window_is_rejected(self):
        frames = [bytearray(f) for f in self.frames]
        frames[0][0] = (frames[0][0] + 1) % 16
        with self.assertRaisesRegex(ValueError, 'window'):
            validate([bytes(f) for f in frames], self.original)

    def test_jittering_jamb_is_rejected(self):
        frames = [bytearray(f) for f in self.frames]
        frames[1][20 * 16 + 13] = (frames[1][20 * 16 + 13] + 1) % 16
        with self.assertRaisesRegex(ValueError, 'inset leaf'):
            validate([bytes(f) for f in frames], self.original)

    def test_transparent_portal_and_duplicate_stage_are_rejected(self):
        frames = [bytearray(f) for f in self.frames]
        frames[2][20 * 16 + 8] = 0
        with self.assertRaisesRegex(ValueError, 'opaque'):
            validate([bytes(f) for f in frames], self.original)
        with self.assertRaisesRegex(ValueError, 'distinct'):
            validate([self.frames[0], self.frames[1], self.frames[1]], self.original)


if __name__ == '__main__':
    unittest.main()
