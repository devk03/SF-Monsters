"""Keep native tile neighbors intact and reject malformed guide masks."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from interface_graphics import replace_header


class GuideHeader(unittest.TestCase):
    def test_only_thirteen_center_tiles_change_and_native_nibbles_are_correct(self):
        original = bytes(range(256)) * 32
        mask = bytearray(640)
        mask[80] = 1
        mask[-1] = 1
        expected = bytearray(original)
        expected[544:960] = b'\x11' * 416
        expected[582] = 0x1f
        expected[925] = 0xf1
        result = replace_header(original, mask)
        self.assertEqual(result, bytes(expected))
        self.assertEqual(replace_header(result, mask), result)
        self.assertEqual(original, bytes(range(256)) * 32)

    def test_invalid_layouts_or_palette_indices_cannot_modify_the_sheet(self):
        for raw, mask in [(bytes(8191), bytes(640)), (bytes(8192), bytes(639)),
                          (bytes(8192), bytes([2]) + bytes(639))]:
            with self.subTest(raw=len(raw), mask=len(mask)):
                with self.assertRaises(ValueError):
                    replace_header(raw, mask)


if __name__ == '__main__':
    unittest.main()
