"""Protect field collision/save coordinates and road tiles during facade replacement."""
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from house_art import compose_tiles, remap_houses
from maps import encode_layout
from native_resources import bounded_span


class HouseArt(unittest.TestCase):
    def test_only_six_facades_change_without_changing_collision_or_elevation(self):
        plan = json.loads((ROOT / 'romhack/content/sunset.json').read_text())
        original = encode_layout(plan)[2]
        changed, origins = remap_houses(plan, original)
        self.assertEqual(origins, [[13, 4], [22, 4], [13, 10], [22, 10], [13, 25], [22, 25]])
        before, after = struct.unpack('<1024H', original), struct.unpack('<1024H', changed)
        differences = {index for index, values in enumerate(zip(before, after)) if values[0] != values[1]}
        expected = {(y + dy) * 32 + x + dx for x, y in origins for dy in range(5) for dx in range(5)}
        self.assertEqual(differences, expected)
        self.assertTrue(all(a & 0xfc00 == b & 0xfc00 for a, b in zip(before, after)))
        self.assertEqual(after[4 * 32 + 13] & 0x3ff, 612)
        self.assertEqual(after[29 * 32 + 26] & 0x3ff, 636)
        with self.assertRaises(ValueError):
            remap_houses(plan, bytes(len(original)))

    def test_road_quadrants_and_other_records_survive_unique_house_tile_encoding(self):
        original = b''.join(bytes([i]) * 32 for i in range(159))
        records = bytearray(2304)
        struct.pack_into('<8H', records, 16, 0x2002, 0x2003, 0x2003, 0x2002,
                         0x5250, 0x5251, 0x5260, 0x5261)
        # Every authored tile is distinct, so the allocator must skip all road tiles.
        owned = b''.join(bytes([i + 1]) * 32 for i in range(100))
        graphics, replaced, count = compose_tiles(original, owned, bytes(records))
        self.assertEqual(count, 100)
        for index in (80, 81, 96, 97):
            self.assertEqual(graphics[index * 32:index * 32 + 32], original[index * 32:index * 32 + 32])
        self.assertEqual(replaced[:1600], records[:1600])
        self.assertEqual(replaced[2000:], records[2000:])
        for y in range(5):
            for x in range(5):
                words = struct.unpack_from('<8H', replaced, (100 + y * 5 + x) * 16)
                for word, delta in zip(words[4:], (0, 1, 10, 11)):
                    index = (word & 0x3ff) - 512
                    self.assertEqual(word >> 12, 10)
                    tile = y * 20 + x * 2 + delta
                    self.assertEqual(graphics[index * 32:index * 32 + 32], owned[tile * 32:tile * 32 + 32])
        records[16] ^= 1
        with self.assertRaises(ValueError):
            compose_tiles(original, owned, bytes(records))

    def test_unsized_resource_requires_a_following_cartridge_end_symbol(self):
        self.assertEqual(bounded_span({'a': 0x083ec210, 'b': 0x083eca10}, 'a', 'b'), (0x3ec210, 2048))
        for addresses in ({'a': 0x03000000, 'b': 0x03000800}, {'a': 0x08001000, 'b': 0x08001000}):
            with self.assertRaises(ValueError):
                bounded_span(addresses, 'a', 'b')


if __name__ == '__main__':
    unittest.main()
