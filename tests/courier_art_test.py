"""Validate native player frame order, tile geometry and actual stepping variants."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from courier_art import native_strip


class CourierArt(unittest.TestCase):
    def setUp(self):
        self.frames = []
        for index in range(18):
            frame = bytearray(1 + x // 8 + 2 * (y // 8) for y in range(32) for x in range(16))
            frame[0], frame[1] = index % 15 + 1, index // 15 + 1
            self.frames.append(bytes(frame))

    def test_native_frame_indices_and_16_by_32_tile_order_are_independent_of_atlas_layout(self):
        for mode, indices in [('walk', [0, 6, 12, 1, 2, 7, 8, 13, 14]),
                              ('run', [3, 9, 15, 4, 5, 10, 11, 16, 17])]:
            pixels, raw = native_strip(self.frames, mode)
            self.assertEqual(len(pixels), 144 * 32)
            self.assertEqual(len(raw), 9 * 256)
            for slot, source in enumerate(indices):
                first_byte = (source % 15 + 1) | ((source // 15 + 1) << 4)
                expected = bytes([first_byte]) + b'\x11' * 31
                expected += b''.join(bytes([color * 17]) * 32 for color in range(2, 9))
                self.assertEqual(raw[slot * 256:(slot + 1) * 256], expected)
                self.assertEqual(pixels[slot * 16:slot * 16 + 16], self.frames[source][:16])

    def test_missing_blank_invalid_and_duplicate_steps_fail_before_shipping(self):
        fixtures = [self.frames[:-1], [bytes(512)] * 18,
                    [bytes([16]) + frame[1:] for frame in self.frames]]
        copied = self.frames.copy(); copied[2] = copied[1]; fixtures.append(copied)
        for frames in fixtures:
            with self.assertRaises(ValueError):
                native_strip(frames, 'walk')
        with self.assertRaises(ValueError):
            native_strip(self.frames, 'bike')

    def test_shipped_sheet_has_consistent_native_size_palette_and_distinct_three_pose_cycles(self):
        from PIL import Image
        directory = ROOT / 'assets/characters/courier-native'
        palettes = []
        for mode in ('walk', 'run'):
            image = Image.open(directory / (mode + '.png'))
            self.assertEqual(image.size, (144, 32))
            self.assertEqual(image.mode, 'P')
            self.assertEqual(image.info['transparency'], 0)
            palettes.append(image.getpalette()[:48])
            frames = [image.crop((i * 16, 0, i * 16 + 16, 32)).tobytes() for i in range(9)]
            for sequence in ((0, 3, 4), (1, 5, 6), (2, 7, 8)):
                self.assertEqual(len({frames[i] for i in sequence}), 3)
            self.assertTrue(all(any(frame) and max(frame) <= 15 for frame in frames))
        self.assertEqual(palettes[0], palettes[1])
        self.assertEqual((directory / 'courier.gbapal').stat().st_size, 32)


if __name__ == '__main__':
    unittest.main()
