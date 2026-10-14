"""Native South Park resource bounds, palette isolation and facade dimensions."""
from pathlib import Path
import struct
import json
from collections import deque
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from park_art import load_buildings, pack_park_cells, facade_cells
from park_map import park_resources, park_tile, prune_unused_terrain, FACADES
from park_signs import sign_cells


class ParkResources(unittest.TestCase):
    def test_service_signs_are_distinct_without_moving_history_or_service_doors(self):
        plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
        raw, records, attributes, palettes = park_resources(ROOT)
        self.assertEqual([park_tile(plan, *point) for point in ((10,6),(29,6),(33,20))],
                         [646,647,540])
        self.assertEqual([park_tile(plan, *point) for point in ((13,5),(32,5))], [583,618])
        self.assertNotEqual(sign_cells()[0][0], sign_cells()[1][0])
        self.assertEqual(palettes[7*32:8*32],
                         (ROOT / 'assets/tiles/sunset-terrain/terrain.gbapal').read_bytes())
        for index, (pixels, bank) in enumerate(sign_cells(), 134):
            self.assertEqual(struct.unpack_from('<H', attributes, index*2)[0], 0x1000)
            self.assertEqual(records[index*16:index*16+8], records[19*16+8:20*16])
            decoded = bytearray(256)
            for quadrant, word in enumerate(struct.unpack_from('<4H', records, index*16+8)):
                self.assertEqual(word >> 12, bank)
                offset = ((word & 1023)-512)*32
                self.assertLess(offset+31, 504*32)  # Door animation owns the last eight tiles.
                for y in range(8):
                    for x in range(8):
                        decoded[(quadrant//2*8+y)*16+quadrant%2*8+x] = (
                            raw[offset+(7-y if word & 0x800 else y)*4
                                +(7-x if word & 0x400 else x)//2]
                            >> ((7-x if word & 0x400 else x)%2*4)) & 15
            self.assertEqual(bytes(decoded), pixels)
            self.assertEqual({pixels[i] for i in (0,15,240,255)}, {0})
        for x, y in ((10,7),(29,7)):
            self.assertFalse(plan['legend'][plan['rows'][y][x]][1])

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


    def test_authored_park_keeps_services_transport_and_discovery_reachable(self):
        plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
        raw, records, attributes, palettes = park_resources(ROOT)
        self.assertLessEqual(len(raw) // 32, 504)
        self.assertEqual((len(records), len(attributes), len(palettes)), (148 * 16, 296, 512))
        flags = struct.unpack('<148H', attributes)
        occupied = {(n['x'], n['y']) for n in plan['npcs']}
        start = (13, 6); visited = {start}; queue = deque([start])
        while queue:
            x, y = queue.popleft()
            for xx, yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if not (0 <= xx < 40 and 0 <= yy < 32) or (xx,yy) in visited | occupied:
                    continue
                if not plan['legend'][plan['rows'][yy][xx]][1]:
                    visited.add((xx,yy));queue.append((xx,yy))
        for target in ((13,5),(32,5),(7,24),(26,17),(34,22),(18,20),(33,19)):
            self.assertIn(target, visited)
        for y, row in enumerate(plan['rows']):
            for x, token in enumerate(row):
                tile = park_tile(plan, x, y) - 512
                self.assertIn(tile, range(148))
                if token in 'RP.FGB#T':
                    self.assertEqual(flags[tile] >> 12, 1)
        self.assertEqual((flags[71], flags[106]), (0x1069, 0x1069))
        for tile in list(range(40, 68)) + list(range(75, 103)) + list(range(110, 119)) + list(range(122, 131)) + list(range(136, 145)):
            self.assertEqual(flags[tile] >> 12, 0)
        for tile in list(range(68, 75)) + list(range(103, 110)) + list(range(119, 122)) + list(range(131, 134)) + list(range(145, 148)):
            self.assertEqual(flags[tile] >> 12, 1)
        for door, expected in (((13,5),583),((32,5),618)):
            self.assertEqual(park_tile(plan,*door), expected)
        self.assertTrue(plan['legend'][plan['rows'][5][11]][1])
        self.assertFalse(plan['legend'][plan['rows'][6][11]][1])

    def test_pruning_cannot_change_any_referenced_cell_or_facade_animation(self):
        plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
        cells = [(bytes([i % 15 + 1]) * 256, 7) for i in range(148)]
        result = prune_unused_terrain(cells, plan)
        changed = {i for i, pair in enumerate(zip(cells, result)) if pair[0] != pair[1]}
        self.assertEqual(changed, {21, 22, 23, 30, 31, 34, 35})
        referenced = {park_tile(plan, x, y) - 512
                      for y, row in enumerate(plan['rows']) for x in range(len(row))}
        referenced.add(plan['border_tile'] - 512)
        self.assertFalse(changed & referenced)
        for i in referenced | set(range(40, 148)) | set(range(20)):
            self.assertEqual(result[i], cells[i])
        self.assertEqual(cells[21][0], bytes([7]) * 256)  # Input stays intact.
        for index in changed:
            with self.subTest(border_cell=index):
                plan['border_tile'] = 512 + index
                self.assertEqual(prune_unused_terrain(cells, plan)[index], cells[index])

    def test_new_facade_keeps_its_native_pixels_palette_and_sidewalk_underlay(self):
        from PIL import Image
        raw, records, attributes, palettes = park_resources(ROOT)
        plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
        expected = Image.open(ROOT / 'assets/tiles/sunset-rowhouse-butter/native-preview.png').resize(
            (48, 64), Image.Resampling.NEAREST).tobytes()
        self.assertEqual(palettes[11 * 32:12 * 32],
                         (ROOT / 'assets/tiles/sunset-rowhouse-butter/house.gbapal').read_bytes())
        for cell in range(12):
            # Global ID635 also occurs in the shared Sunset door table. Native
            # behavior must keep this decorative facade out of door animation.
            self.assertEqual(struct.unpack_from('<H', attributes, (122 + cell) * 2)[0] & 255, 0)
            self.assertTrue(plan['legend'][plan['rows'][2 + cell // 3][23 + cell % 3]][1])
            words = struct.unpack_from('<8H', records, (122 + cell) * 16)
            self.assertEqual(records[(122 + cell) * 16:(122 + cell) * 16 + 8],
                             records[19 * 16 + 8:20 * 16])
            pixels = bytearray(256)
            for quadrant, word in enumerate(words[4:]):
                self.assertEqual(word >> 12, 11)
                offset = ((word & 1023) - 512) * 32
                for y in range(8):
                    for x in range(8):
                        pixels[(quadrant // 2 * 8 + y) * 16 + quadrant % 2 * 8 + x] = (
                            raw[offset + (7-y if word & 0x800 else y)*4
                                + (7-x if word & 0x400 else x)//2]
                            >> ((7-x if word & 0x400 else x)%2*4)) & 15
            left, top = cell % 3 * 16, cell // 3 * 16
            self.assertEqual(bytes(pixels), b''.join(
                expected[y * 48 + left:y * 48 + left + 16] for y in range(top, top + 16)))

    def test_western_houses_block_all_footprints_and_keep_both_public_approaches(self):
        plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
        # The previous empty plaza is now one compact street wall, never a path.
        for y in range(13, 17):
            for x in range(11, 17):
                self.assertTrue(plan['legend'][plan['rows'][y][x]][1], (x, y))
        for left, first in ((11, 622), (14, 634)):
            for dy in range(4):
                for dx in range(3):
                    self.assertEqual(park_tile(plan, left+dx, 13+dy), first+dy*3+dx)
        # Two unobstructed sidewalk rows face the cross street; the garden and
        # road sides both reconnect below the houses. No fake walk-through door.
        approaches = ([(x, y) for y in (11, 12, 17) for x in range(10, 18)]
                      + [(x, y) for x in (10, 17) for y in range(13, 17)])
        for x, y in approaches:
            self.assertFalse(plan['legend'][plan['rows'][y][x]][1], (x, y))
        self.assertFalse(any(11 <= event['x'] < 17 and 13 <= event['y'] < 17
                             for key in ('npcs', 'warp_events', 'bg_events')
                             for event in plan[key]))

    def test_compact_frontage_keeps_two_clear_sidewalk_rows_and_service_anchors(self):
        plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
        gap = maximum = 0
        for token in plan['rows'][5][10:36]:
            gap = gap + 1 if token == 'P' else 0
            maximum = max(maximum, gap)
        self.assertLessEqual(maximum, 3)
        for y in (6, 7):
            for x in range(11, 36):
                if (x, y) == (29, 6):
                    continue  # Existing clinic sign.
                self.assertFalse(plan['legend'][plan['rows'][y][x]][1])
        self.assertEqual([(w['x'], w['y']) for w in plan['warp_events']], [(13, 5), (32, 5)])
        for x, y in ((19, 4), (24, 4)):
            self.assertTrue(plan['legend'][plan['rows'][y][x]][1])
        self.assertEqual([f[:2] for f in FACADES if f[4] == 110], [(18, 2), (11, 20), (11, 13)])


if __name__ == '__main__':
    unittest.main()
