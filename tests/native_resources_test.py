"""Preserve palette tails/neighbors and encode the actual split subtitle sprite layout."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from native_resources import replace_resource
from title_art import tiles8


class NativeResources(unittest.TestCase):
    def test_palette_prefix_preserves_tail_and_all_other_cartridge_bytes(self):
        rom = b'LEFT' + bytes(range(16)) + b'RIGHT'
        expected = b'LEFT' + b'NEW!' + bytes(range(4, 16)) + b'RIGHT'
        result = replace_resource(rom, rom, 4, 16, b'NEW!', True)
        self.assertEqual(result, expected)
        self.assertEqual(replace_resource(result, rom, 4, 16, b'NEW!', True), expected)
        self.assertEqual(rom, b'LEFT' + bytes(range(16)) + b'RIGHT')

    def test_overflow_invalid_allocations_and_unrelated_prior_edits_are_rejected(self):
        linked = bytes(range(32))
        for rom, offset, capacity, data in [(linked, -1, 8, b'NEW'),
            (linked, 28, 8, b'NEW'), (linked, 4, 2, b'NEW'),
            (linked[:4] + b'BAD!' + linked[8:], 4, 8, b'NEW')]:
            with self.subTest(offset=offset, capacity=capacity):
                with self.assertRaises(ValueError):
                    replace_resource(rom, linked, offset, capacity, data)

    def test_subtitle_left_and_right_64x32_sprites_are_contiguous(self):
        pixels = (b'\x01' * 64 + b'\x02' * 64) * 32
        self.assertEqual(tiles8(pixels, 128, 32, 8, 4), b'\x01' * 2048 + b'\x02' * 2048)
        with self.assertRaises(ValueError):
            tiles8(pixels, 128, 32, 0, 4)


if __name__ == '__main__':
    unittest.main()
