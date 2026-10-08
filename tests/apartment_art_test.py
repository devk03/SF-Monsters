"""Apartment graphics must fit native VRAM and keep cells/border/exit independent."""
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ApartmentArt(unittest.TestCase):
    def test_native_scene_allocations_and_exit_behavior(self):
        directory = ROOT / 'assets/tiles/courier-apartment'
        metadata = json.loads((directory / 'conversion.json').read_text())
        self.assertEqual(metadata['native_size'], [176, 160])
        self.assertEqual(metadata['tile_count'], 444)
        self.assertLessEqual(metadata['tile_count'], 512)
        self.assertEqual((directory / 'tiles.4bpp').stat().st_size, 444 * 32)
        records = (directory / 'metatiles.bin').read_bytes()
        attributes = struct.unpack('<111H', (directory / 'attributes.bin').read_bytes())
        self.assertEqual([i for i, value in enumerate(attributes) if value], [104])
        self.assertEqual(attributes[104], 0x65)
        self.assertEqual(len(records), 111 * 16)
        for cell in range(110):
            entries = struct.unpack_from('<8H', records, cell * 16)
            self.assertEqual(entries[:4], (0x63b8, 0x63b9, 0x63ba, 0x63bb))
            self.assertEqual(entries[4:], tuple(0x6200 | (cell * 4 + q) for q in range(4)))
        palette = (directory / 'palettes.gbapal').read_bytes()
        self.assertEqual(len(palette), 512)
        self.assertEqual(palette[:192], bytes(192))
        self.assertEqual(palette[224:], bytes(288))


if __name__ == '__main__':
    unittest.main()
