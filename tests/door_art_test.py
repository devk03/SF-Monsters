"""Door frames must obey the engine's 256-byte stage offsets and tile layout."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from door_art import native_frames


class DoorEncoding(unittest.TestCase):
    def test_each_stage_keeps_top_and_bottom_metatiles_together(self):
        frames = [bytes(y // 8 * 2 + x // 8 + 1 + stage * 2
                        for y in range(32) for x in range(16))
                  for stage in range(3)]
        encoded = native_frames(frames)
        self.assertEqual(len(encoded), 768)
        for stage in range(3):
            # Native format: eight 8x8 tiles, four-bit pixels, low nibble first.
            expected = b''.join(bytes([color * 17]) * 32
                                for color in range(1 + stage * 2, 9 + stage * 2))
            self.assertEqual(encoded[stage * 256:(stage + 1) * 256], expected)

    def test_bad_dimensions_palette_and_indistinguishable_stages_are_rejected(self):
        frames = [bytes([value]) * 512 for value in (1, 2, 3)]
        for bad in (frames[:2], [frames[0][:-1], *frames[1:]],
                    [bytes([16]) * 512, *frames[1:]],
                    [bytes(512), *frames[1:]], [frames[0]] * 3):
            with self.subTest(frames=tuple(map(len, bad))), self.assertRaises(ValueError):
                native_frames(bad)


if __name__ == '__main__':
    unittest.main()
