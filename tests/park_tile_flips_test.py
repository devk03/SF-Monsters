"""Decode native BG words independently; preserve released pixels and door VRAM."""
from pathlib import Path
import hashlib
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from park_art import pack_park_cells
from park_map import park_resources


def decode_tile(raw, word):
    index = (word & 0x3ff) - 512
    if index < 0:
        if word != 0:
            raise AssertionError('Unexpected inherited primary graphics.')
        return bytes(64)
    tile = raw[index*32:(index+1)*32]
    if len(tile) != 32:
        raise AssertionError('BG word points outside supplied graphics.')
    rows = [[(tile[y*4+x//2] >> (4*(x % 2))) & 15
             for x in range(8)] for y in range(8)]
    if word & 0x400:
        rows = [list(reversed(row)) for row in rows]
    if word & 0x800:
        rows.reverse()
    return bytes(value for row in rows for value in row)


def cell_from_tiles(tiles):
    return b''.join(tiles[y//8*2][y%8*8:y%8*8+8]
                    + tiles[y//8*2+1][y%8*8:y%8*8+8] for y in range(16))


class NativeTileFlips(unittest.TestCase):
    def test_four_orientations_reuse_one_tile_in_every_secondary_palette(self):
        original = bytes((x*x + 3*y + x*y) % 16 for y in range(8) for x in range(8))
        horizontal = b''.join(original[y*8:(y+1)*8][::-1] for y in range(8))
        vertical = b''.join(original[y*8:(y+1)*8] for y in reversed(range(8)))
        variants = [original, horizontal, vertical, original[::-1]]
        cell = cell_from_tiles(variants)
        cells = [(cell, bank) for bank in range(6, 13)]
        raw, records, flags = pack_park_cells(cells, [0x1000]*len(cells))
        self.assertEqual(len(raw), 32)
        self.assertEqual(flags, struct.pack('<7H', *([0x1000]*7)))
        for bank, offset in zip(range(6, 13), range(0, len(records), 16)):
            words = struct.unpack_from('<8H', records, offset)
            self.assertEqual(words[:4], (0, 0, 0, 0))
            self.assertEqual([word & 0xc00 for word in words[4:]],
                             [0, 0x400, 0x800, 0xc00])
            for expected, word in zip(variants, words[4:]):
                self.assertEqual(word >> 12, bank)
                self.assertEqual(word & 0x3ff, 512)
                self.assertEqual(decode_tile(raw, word), expected)
        self.assertEqual(cells[0], (cell, 6))

    def test_symmetric_ties_keep_unflipped_first_binding(self):
        raw, records, _ = pack_park_cells([(bytes([15])*256, 12)]*2, [0, 0])
        self.assertEqual(raw, bytes([255])*32)
        self.assertEqual(struct.unpack('<16H', records),
                         (0, 0, 0, 0, *([0xc200]*4))*2)

    def test_door_reservation_allows_503_and_504_tiles_but_rejects_505(self):
        tiles = []
        for value in range(505):
            tile = bytearray(64)
            # Distinct asymmetric corner markers disallow cross-tile flips.
            tile[0], tile[1], tile[8] = 1, 2, 3
            for shift, position in enumerate((18, 19, 20)):
                tile[position] = (value >> (shift*4)) & 15
            tiles.append(bytes(tile))
        for count in (503, 504, 505):
            selected = tiles[:count]
            selected += [selected[0]]*((-count) % 4)
            cells = [(cell_from_tiles(selected[i:i+4]), 6)
                     for i in range(0, len(selected), 4)]
            if count == 505:
                with self.assertRaisesRegex(ValueError, 'VRAM capacity'):
                    pack_park_cells(cells, [0]*len(cells))
                continue
            raw, records, _ = pack_park_cells(cells, [0]*len(cells))
            self.assertEqual(len(raw)//32, count)
            words = struct.unpack('<'+'H'*(len(records)//2), records)
            self.assertLessEqual(max(word & 0x3ff for word in words), 1015)

    def test_all_released_v53_pixels_palettes_and_attributes_are_preserved(self):
        raw, records, attributes, palettes = park_resources(ROOT)
        decoded = bytearray()
        for word in struct.unpack('<'+'H'*(136*8), records[:136*16]):
            for index in decode_tile(raw, word):
                decoded.extend((index, word >> 12))
        # Pinned before this change, from the independently decoded v53 resource.
        self.assertEqual(hashlib.sha256(decoded).hexdigest(),
                         '74247ad02bc5624367da7f555d2faaf85f4b3d967d95886cb4a10ec3a4769ba0')
        self.assertEqual(hashlib.sha256(attributes[:272]).hexdigest(),
                         '6bc89718054757ea9191edc3af602b745a9655c6447711031be2bdc255624485')
        self.assertEqual(hashlib.sha256(palettes).hexdigest(),
                         '19aa2722f040f2d30e65c33f80bcf6c9681947e0612f4e8cb2e0ce4a742598af')
        self.assertLessEqual(len(raw)//32, 460)


if __name__ == '__main__':
    unittest.main()
