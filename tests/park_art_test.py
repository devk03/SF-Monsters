"""Native South Park resource bounds, palette isolation and facade dimensions."""
from pathlib import Path
import struct
import json
import hashlib
from collections import deque
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from park_density import strip as strip_density
from park_art import load_buildings, pack_park_cells, facade_cells
from park_map import park_resources, park_tile, prune_unused_terrain, FACADES
from park_signs import sign_cells
from seed_door_art import load as load_seed_door
from maps import encode_layout
from park_infill import previous_plan
from park_tile_flips_test import decode_tile, cell_from_tiles


class ParkResources(unittest.TestCase):
    def test_lower_west_neighbor_changes_only_thirteen_cells_without_new_resources(self):
        plan = previous_plan(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
        previous = json.loads(json.dumps(plan))
        expected = {}
        for y, current, old in ((20, 'abc', 'P.T'), (21, 'def', 'PPP'),
                                (22, 'ghf', 'PPP'), (23, 'ijf', 'PPP')):
            row = previous['rows'][y]
            self.assertEqual(row[14:17], current)
            previous['rows'][y] = row[:14] + old + row[17:]
            for x in range(14, 17):
                expected[(x, y)] = 634 + (y - 20) * 3 + x - 14
                self.assertEqual(plan['legend'][current[x - 14]][1:], [True, 0])
        self.assertEqual(plan['rows'][20][19], 'T')
        row = previous['rows'][20]
        previous['rows'][20] = row[:19] + '.' + row[20:]
        expected[(19, 20)] = 541
        self.assertEqual(plan['legend']['T'][1:], [True, 3])
        dylan = next(n for n in previous['npcs'] if n['script'] == 'SF_DylanField')
        self.assertEqual(dylan['graphics'], 'OBJ_EVENT_GFX_SF_DYLAN_FIELD')
        dylan['graphics'] = 'OBJ_EVENT_GFX_MAN_3'
        jonathan = next(n for n in previous['npcs'] if n['script'] == 'SF_Muni_Return')
        self.assertEqual(jonathan['graphics'], 'OBJ_EVENT_GFX_SF_JONATHAN_PARK')
        jonathan['graphics'] = 'OBJ_EVENT_GFX_MAN_5'
        # Pin the complete preceding map, including events, not just the patch.
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True,
            separators=(',', ':')).encode()).hexdigest(),
            'c4e3245db44e54b62607be148c951fc73f00efccaab668d80ba8b6c4d2d57c50')
        changed = {(x, y) for y, row in enumerate(plan['rows']) for x, token in enumerate(row)
                   if token != previous['rows'][y][x]}
        self.assertEqual(changed, set(expected))
        # The real map installer replaces low ten bits after encode_layout.
        def words(p):
            width, height, data = encode_layout(p)
            return {(x, y): (struct.unpack_from('<H', data, (y * width + x) * 2)[0] & 0xFC00)
                    | park_tile(p, x, y) for y in range(height) for x in range(width)}
        before, after = words(previous), words(plan)
        self.assertEqual({point for point in before if before[point] != after[point]}, changed)
        for point, tile in expected.items():
            self.assertEqual(after[point], tile | 0xC00 | (0x3000 if point == (19, 20) else 0))
        # This v69 map checkpoint predates the later explicit paving reskin.
        # Preserve its original resource fingerprints; the new paving auditor
        # independently checks every current decoded quadrant against them.
        baseline = ROOT/'assets/tiles/south-park-paving-v1/baseline-v74'
        resources = tuple((baseline/name).read_bytes() for name in
                          ('tiles.4bpp','metatiles.bin','attributes.bin','palettes.gbapal'))
        self.assertEqual([(len(data), hashlib.sha256(data).hexdigest()) for data in resources], [
            (16096, '1028cc530238a128ba379d2de5f8153cdbf2eb6c1054f67501f5e4900ce2b6c8'),
            (2400, 'c5a357ba4d453bb0e856b09a594334303b50ead542ef7081b92a243a7269a0c8'),
            (300, '5d75b62c2517473238cfe7967401f492d506a41ffbbd5de58ea9c99ad39eab2f'),
            (512, '73e3ba1b6d1f0a9385e97e92eba6a4a2d1268384e4cdf6f45f452a49fda512db')])

    def test_lower_west_neighbor_preserves_routes_encounters_and_recovery_candidates(self):
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
        # Eleven newly blocked house cells plus the relocated tree = twelve.
        footprint = {(x, y) for y in range(20, 24) for x in range(14, 17)}
        new_blocks = footprint - {(16, 20)} | {(19, 20)}
        self.assertEqual(len(new_blocks), 12)
        self.assertTrue(all(plan['legend'][plan['rows'][y][x]][1] for x, y in new_blocks))
        events = plan['npcs'] + plan['warp_events'] + plan['bg_events']
        self.assertFalse(new_blocks & {(e['x'], e['y']) for e in events})
        occupied = {(n['x'], n['y']) for n in plan['npcs']}
        walkable = {(x, y) for y, row in enumerate(plan['rows']) for x, token in enumerate(row)
                    if not plan['legend'][token][1]} - occupied
        def flood(allowed):
            seen = {(7, 26)}; queue = deque(seen)
            while queue:
                x, y = queue.popleft()
                for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if point in allowed and point not in seen:
                        seen.add(point); queue.append(point)
            return seen
        before, after = flood(walkable | new_blocks), flood(walkable)
        self.assertEqual(before - new_blocks, after)
        self.assertEqual(before - after, new_blocks)
        for point in ((17,21),(19,21),(18,20),(18,22),  # All four bench approaches.
                      (13,6),(32,6),(16,17),(7,24),(26,17),(34,22)):
            self.assertIn(point, after)
        for y in (19, 24):
            for x in range(10, 18):
                self.assertIn((x, y), after)
        grass = {(x, y) for y, row in enumerate(plan['rows']) for x, token in enumerate(row) if token == 'G'}
        self.assertEqual(grass, {(17,18),(18,18),(31,21),(32,21),(21,23),(22,23)})
        self.assertLessEqual(grass, after)
        # Source-level availability only; root validates native old-save relocation.
        safe = after - {(e['x'], e['y']) for e in plan['warp_events']}
        for x, y in new_blocks:
            self.assertLessEqual(min(abs(x-xx) + abs(y-yy) for xx, yy in safe), 2)

    def test_service_signs_are_distinct_without_moving_history_or_service_doors(self):
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
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
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
        raw, records, attributes, palettes = park_resources(ROOT)
        self.assertLessEqual(len(raw) // 32, 504)
        self.assertEqual((len(records), len(attributes), len(palettes)), (150 * 16, 300, 512))
        flags = struct.unpack('<150H', attributes)
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
                native_tile = park_tile(plan, x, y)
                if native_tile < 512:
                    if 18<=x<29 and 2<=y<7:
                        self.assertEqual(native_tile,65+(y-2)*11+x-18)
                        self.assertEqual(plan['legend'][token][1:],[False,3] if y==6 else [True,0])
                    elif token in 'uU':
                        self.assertIn(native_tile,range(120,135))
                        self.assertEqual(plan['legend'][token],[0,token=='U',3])
                    else:
                        self.assertIn(token, 'WXY')
                    continue  # New primary resources have separate exact pixel/attribute checks.
                tile = native_tile - 512
                self.assertIn(tile, range(150))
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
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
        cells = [(bytes([i % 15 + 1]) * 256, 7) for i in range(150)]
        result = prune_unused_terrain(cells, plan)
        changed = {i for i, pair in enumerate(zip(cells, result)) if pair[0] != pair[1]}
        self.assertEqual(changed, {21, 22, 23, 30, 31, 34, 35})
        referenced = {park_tile(plan, x, y) - 512
                      for y, row in enumerate(plan['rows']) for x in range(len(row))
                      if park_tile(plan, x, y) >= 512}
        referenced.add(plan['border_tile'] - 512)
        self.assertFalse(changed & referenced)
        for i in referenced | set(range(40, 150)) | set(range(20)):
            self.assertEqual(result[i], cells[i])
        self.assertEqual(cells[21][0], bytes([7]) * 256)  # Input stays intact.
        for index in changed:
            with self.subTest(border_cell=index):
                plan['border_tile'] = 512 + index
                self.assertEqual(prune_unused_terrain(cells, plan)[index], cells[index])

    def test_new_facade_keeps_its_native_pixels_palette_and_sidewalk_underlay(self):
        from PIL import Image
        raw, records, attributes, palettes = park_resources(ROOT)
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
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

    def test_western_houses_block_walls_and_leave_only_the_seed_room_entry_open(self):
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
        # The previous empty plaza is now one compact street wall, never a path.
        for y in range(13, 17):
            for x in range(11, 17):
                self.assertEqual(plan['legend'][plan['rows'][y][x]][1],
                                 (x, y) != (16, 16), (x, y))
        for left, first in ((11, 622), (14, 634)):
            for dy in range(4):
                for dx in range(3):
                    point = (left+dx, 13+dy)
                    expected = {(16, 16):660, (16, 15):661}.get(point, first+dy*3+dx)
                    self.assertEqual(park_tile(plan, *point), expected)
        # Two unobstructed sidewalk rows face the cross street; the garden and
        # road sides both reconnect below the houses. Only the real entry is open.
        approaches = ([(x, y) for y in (11, 12, 17) for x in range(10, 18)]
                      + [(x, y) for x in (10, 17) for y in range(13, 17)])
        for x, y in approaches:
            self.assertFalse(plan['legend'][plan['rows'][y][x]][1], (x, y))
        self.assertFalse(any(11 <= event['x'] < 17 and 13 <= event['y'] < 17
                             for key in ('npcs', 'warp_events', 'bg_events')
                             for event in plan[key] if (event['x'], event['y']) != (16, 16)))

    def test_seed_room_door_uses_centered_cards_and_keeps_other_facades_blocked(self):
        raw, records, attributes, palettes = park_resources(ROOT)
        closed = load_seed_door(ROOT)['frames'][0]
        for index, expected in ((149, closed[:256]), (148, closed[256:])):
            words = struct.unpack_from('<8H', records, index*16)
            self.assertEqual(cell_from_tiles([decode_tile(raw, w) for w in words[4:]]), expected)
            self.assertTrue(all(w >> 12 == 11 for w in words[4:]))
        flags = struct.unpack('<150H', attributes)
        self.assertEqual((flags[133], flags[148], flags[149]), (0x1000, 0x1069, 0))
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
        self.assertEqual(plan['warp_events'][2], {
            'x': 16, 'y': 16, 'elevation': 0,
            'dest_map': 'MAP_OLDALE_TOWN_HOUSE1', 'dest_warp_id': '0'})
        self.assertTrue(plan['legend'][plan['rows'][5][25]][1])
        self.assertFalse(plan['legend'][plan['rows'][16][16]][1])
        self.assertEqual(park_tile(plan, 25, 5), 105)  # Same blocked wall, connected artwork.
        self.assertEqual(plan['legend']['q'], [661, True, 0])
        for point in ((16,17),(17,17)):
            self.assertEqual(plan['rows'][point[1]][point[0]], 'P')

    def test_compact_frontage_keeps_clear_approach_row_and_declared_curbside_bases(self):
        plan = strip_density(json.loads((ROOT / 'romhack/content/south-park.json').read_text()))
        gap = maximum = 0
        for token in plan['rows'][5][10:36]:
            gap = gap + 1 if token == 'P' else 0
            maximum = max(maximum, gap)
        self.assertLessEqual(maximum, 3)
        for y in (6, 7):
            for x in range(11, 36):
                if (x, y) == (29, 6):
                    continue  # Existing clinic sign.
                solid={(11,7),(15,7),(17,7),(19,7),(23,7),(24,7),(26,7)}
                self.assertEqual(plan['legend'][plan['rows'][y][x]][1],(x,y) in solid)
        for x in (13,20,21,22,25,28,32):
            self.assertFalse(plan['legend'][plan['rows'][7][x]][1])
        self.assertEqual([(w['x'], w['y']) for w in plan['warp_events']], [(13, 5), (32, 5), (16, 16)])
        for x, y in ((19, 4), (24, 4)):
            self.assertTrue(plan['legend'][plan['rows'][y][x]][1])
        self.assertEqual([f[:2] for f in FACADES if f[4] == 110], [(18, 2), (11, 20), (11, 13)])


if __name__ == '__main__':
    unittest.main()
