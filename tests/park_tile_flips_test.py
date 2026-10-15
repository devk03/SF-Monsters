"""Decode native BG words independently; preserve released pixels and door VRAM."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from park_art import pack_park_cells
from park_map import park_resources, park_tile
from park_infill import previous_plan


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
    def test_lavender_frontage_fills_only_twelve_gap_cells(self):
        plan = previous_plan(json.loads((ROOT/'romhack/content/south-park.json').read_text()))
        restored = json.loads(json.dumps(plan))
        dylan = next(n for n in restored['npcs'] if n['script'] == 'SF_DylanField')
        self.assertEqual(dylan['graphics'], 'OBJ_EVENT_GFX_SF_DYLAN_FIELD')
        dylan['graphics'] = 'OBJ_EVENT_GFX_MAN_3'
        jonathan = next(n for n in restored['npcs'] if n['script'] == 'SF_Muni_Return')
        self.assertEqual(jonathan['graphics'], 'OBJ_EVENT_GFX_SF_JONATHAN_PARK')
        jonathan['graphics'] = 'OBJ_EVENT_GFX_MAN_5'
        # Restore the later lower-west neighbor and its one relocated tree first.
        self.assertEqual(restored['rows'][20][19], 'T')
        row = restored['rows'][20]
        restored['rows'][20] = row[:19] + '.' + row[20:]
        for y, current, previous in ((20, 'abc', 'P.T'), (21, 'def', 'PPP'),
                                     (22, 'ghf', 'PPP'), (23, 'ijf', 'PPP')):
            row = restored['rows'][y]
            self.assertEqual(row[14:17], current)
            restored['rows'][y] = row[:14] + previous + row[17:]
        self.assertEqual(restored['legend'].pop('Q'), [660, False, 3])
        self.assertEqual(restored['legend'].pop('q'), [661, True, 0])
        row = restored['rows'][17]
        self.assertEqual(row[16:18], 'PP')
        restored['rows'][17] = row[:16] + '..' + row[18:]
        self.assertEqual(restored['warp_events'].pop(), {
            'x': 16, 'y': 16, 'elevation': 0,
            'dest_map': 'MAP_OLDALE_TOWN_HOUSE1', 'dest_warp_id': '0'})
        for y in range(13, 17):
            row = restored['rows'][y]
            restored['rows'][y] = row[:11] + 'P'*6 + row[17:]
        for y in range(2, 6):
            for x in range(26, 29):
                token = plan['rows'][y][x]
                self.assertTrue(plan['legend'][token][1])
                self.assertEqual(park_tile(plan, x, y), 648+(y-2)*3+x-26)
            row = restored['rows'][y]
            restored['rows'][y] = row[:26]+'PPP'+row[29:]
        # Entire map outside reviewed frontage additions, including v60 bench landing.
        self.assertEqual(hashlib.sha256(json.dumps(restored, sort_keys=True,
                         separators=(',', ':')).encode()).hexdigest(),
                         '89f6d3d31744419676f6bd2126b3d10290fb5ac2926c14a1fc54bb38295e00f1')
        self.assertNotEqual(plan['rows'][5][25], 'P')  # Abuts butter facade.
        self.assertNotEqual(plan['rows'][5][29], 'P')  # Abuts clinic facade.
        for x in range(26, 29):
            self.assertFalse(plan['legend'][plan['rows'][6][x]][1])
            self.assertFalse(plan['legend'][plan['rows'][7][x]][1])

    def test_lavender_native_art_has_its_own_palette_and_blocked_front(self):
        from PIL import Image
        raw, records, attrs, palettes = park_resources(ROOT)
        expected = Image.open(ROOT/'assets/tiles/sunset-rowhouse-lavender/native-preview.png').resize(
            (48, 64), Image.Resampling.NEAREST).tobytes()
        palette = (ROOT/'assets/tiles/sunset-rowhouse-lavender/house.gbapal').read_bytes()
        self.assertEqual(palettes[384:416], palette)
        self.assertEqual(hashlib.sha256(palette).hexdigest(),
                         'f453c43e03310151ed5ea3b6566e843f32d71137ed63818f29ca9fc6a8c3b3ea')
        for cell in range(12):
            offset = (136+cell)*16
            words = struct.unpack_from('<8H', records, offset)
            decoded = [decode_tile(raw, word) for word in words[4:]]
            pixels = cell_from_tiles(decoded)
            left, top = (cell % 3)*16, (cell//3)*16
            self.assertEqual(pixels, b''.join(expected[y*48+left:y*48+left+16]
                                             for y in range(top, top+16)))
            self.assertEqual([word >> 12 for word in words[4:]], [12]*4)
            self.assertEqual(records[offset:offset+8], records[19*16+8:20*16])
            self.assertEqual(struct.unpack_from('<H', attrs, (136+cell)*2)[0],
                             0 if cell < 9 else 0x1000)
        # Exact deduplication count varies with deliberately edited lawn art.
        # The shared resource test below retains the native door VRAM bound.

    def test_four_orientations_reuse_one_tile_in_every_secondary_palette(self):
        original = bytes((x*x + 3*y + x*y) % 16 for y in range(8) for x in range(8))
        horizontal = b''.join(original[y*8:(y+1)*8][::-1] for y in range(8))
        vertical = b''.join(original[y*8:(y+1)*8] for y in reversed(range(8)))
        variants = [original, horizontal, vertical, original[::-1]]
        cell = cell_from_tiles(variants)
        cells = [(cell, bank) for bank in range(6, 13)]
        raw, records, flags = pack_park_cells(cells, [0x1000]*len(cells), reuse_flips=True)
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
        raw, records, _ = pack_park_cells([(bytes([15])*256, 12)]*2, [0, 0], reuse_flips=True)
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
                    pack_park_cells(cells, [0]*len(cells), reuse_flips=True)
                continue
            raw, records, _ = pack_park_cells(cells, [0]*len(cells), reuse_flips=True)
            self.assertEqual(len(raw)//32, count)
            words = struct.unpack('<'+'H'*(len(records)//2), records)
            self.assertLessEqual(max(word & 0x3ff for word in words), 1015)

    def test_released_pixels_preserved_except_exact_authored_lawn_replacements(self):
        from terrain_art import load_native_grass
        from park_paving import load_paving
        raw, records, attributes, palettes = park_resources(ROOT)
        paving = load_paving(ROOT)
        baseline = ROOT/'assets/tiles/south-park-paving-v1/baseline-v74'
        old_paving_raw = (baseline/'tiles.4bpp').read_bytes()
        old_paving_records = (baseline/'metatiles.bin').read_bytes()
        current_grass, _ = load_native_grass(ROOT/'assets/tiles/sunset-terrain')
        old_grass = json.loads((ROOT/'tests/fixtures/coastal-lawn-v56.json').read_text())
        self.assertEqual(old_grass['source_sha256'],
                         'a905cc41244d7abe00ab13b71c4e2b8db0edf48d0251a7b18729e3dbec16e962')
        def quadrant(cell, index):
            left, top = (index % 2)*8, (index//2)*8
            return b''.join(cell[y*16+left:y*16+left+8] for y in range(top, top+8))
        decoded = bytearray()
        for offset, word in enumerate(struct.unpack('<'+'H'*(136*8), records[:136*16])):
            cell, layer_quadrant = divmod(offset, 8)
            pixels = decode_tile(raw, word)
            bank = word >> 12
            if (cell in (16,19) and layer_quadrant >= 4) or (40 <= cell < 136 and layer_quadrant < 4):
                self.assertEqual(bank, 4)
                self.assertEqual(pixels, quadrant(paving, layer_quadrant % 4))
                # Normalize only the independently checked paving quadrants;
                # retain the older full-render fingerprint for every other pixel.
                previous_word = struct.unpack_from('<H',old_paving_records,offset*2)[0]
                pixels = decode_tile(old_paving_raw, previous_word)
                bank = previous_word >> 12
            if cell in (20, 32, 33) and layer_quadrant >= 4:
                lawn = cell - 20
                self.assertEqual(word >> 12, 7)
                self.assertEqual(pixels, quadrant(current_grass[lawn], layer_quadrant - 4))
                # Compare the remaining released resource to its original hash,
                # restoring only these explicitly checked source-art quadrants.
                pixels = quadrant(bytes.fromhex(old_grass['cells'][str(lawn)]), layer_quadrant - 4)
            for index in pixels:
                decoded.extend((index, bank))
        # Pinned before this change, from the independently decoded v53 resource.
        self.assertEqual(hashlib.sha256(decoded).hexdigest(),
                         '74247ad02bc5624367da7f555d2faaf85f4b3d967d95886cb4a10ec3a4769ba0')
        self.assertEqual(hashlib.sha256(attributes[:272]).hexdigest(),
                         '6bc89718054757ea9191edc3af602b745a9655c6447711031be2bdc255624485')
        # New lavender facade occupies previously unused bank12 only.
        old_palettes = palettes[:384] + bytes(32) + palettes[416:]
        self.assertEqual(hashlib.sha256(old_palettes).hexdigest(),
                         '19aa2722f040f2d30e65c33f80bcf6c9681947e0612f4e8cb2e0ce4a742598af')
        self.assertLessEqual(len(raw)//32, 504)


if __name__ == '__main__':
    unittest.main()
