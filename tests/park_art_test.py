"""Native South Park resource bounds, palette isolation and facade dimensions."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from park_art import load_buildings, pack_park_cells, facade_cells


class ParkResources(unittest.TestCase):
    def test_facade_cells_keep_bottom_door_at_the_center_of_each_native_footprint(self):
        frames, palettes = load_buildings(ROOT)
        self.assertEqual([len(frame) for frame in frames], [8960, 8960])
        self.assertEqual([len(palette) for palette in palettes], [32, 32])
        for frame, bank in zip(frames, (8, 9)):
            cells = facade_cells(frame, 112, 80, bank)
            self.assertEqual(len(cells), 35)
            # Door's lower cell is row four, column three; preserve pixel order.
            expected = b''.join(frame[y * 112 + 48:y * 112 + 64] for y in range(64, 80))
            self.assertEqual(cells[31], (expected, bank))
            self.assertTrue(any(expected))

    def test_identical_pixels_share_vram_without_sharing_palette_or_layer_flags(self):
        cell = bytes([3]) * 256
        graphics, records, attributes = pack_park_cells([(cell, 6), (cell, 9)], [0x1000, 0x60])
        self.assertEqual(graphics, bytes([0x33]) * 32)
        first, second = (struct.unpack_from('<8H', records, offset) for offset in (0, 16))
        self.assertEqual(first[:4], (0, 0, 0, 0))
        self.assertEqual(first[4:], (0x6200,) * 4)
        self.assertEqual(second[4:], (0x9200,) * 4)
        self.assertEqual(struct.unpack('<2H', attributes), (0x1000, 0x60))

    def test_bad_native_records_and_secondary_tile_overflow_are_rejected(self):
        for cells, flags in [([(bytes(255), 6)], [0]), ([(bytes([16])*256, 6)], [0]),
                             ([(bytes(256), 5)], [0]), ([(bytes(256), 6)], [])]:
            with self.subTest(cells=cells[:1]), self.assertRaises(ValueError):
                pack_park_cells(cells, flags)
        cells = []
        for block in range(129):
            tiles = [bytes([(index >> (4 * shift)) & 15 for shift in range(3)] + [1] * 61)
                     for index in range(block * 4, block * 4 + 4)]
            pixels = b''.join(tiles[(y//8)*2][(y%8)*8:(y%8)*8+8] +
                              tiles[(y//8)*2+1][(y%8)*8:(y%8)*8+8] for y in range(16))
            cells.append((pixels, 6))
        with self.assertRaisesRegex(ValueError, 'VRAM capacity'):
            pack_park_cells(cells, [0x1000] * len(cells))


if __name__ == '__main__':
    unittest.main()
