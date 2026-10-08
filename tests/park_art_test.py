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
from park_map import park_resources, park_tile


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


    def test_authored_park_keeps_services_transport_and_discovery_reachable(self):
        plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
        raw, records, attributes, palettes = park_resources(ROOT)
        self.assertLessEqual(len(raw) // 32, 504)
        self.assertEqual((len(records), len(attributes), len(palettes)), (122 * 16, 244, 512))
        flags = struct.unpack('<122H', attributes)
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
                self.assertIn(tile, range(122))
                if token in 'RP.FGB#T':
                    self.assertEqual(flags[tile] >> 12, 1)
        self.assertEqual((flags[71], flags[106]), (0x69, 0x69))
        for door, expected in (((13,5),583),((32,5),618)):
            self.assertEqual(park_tile(plan,*door), expected)
        self.assertTrue(plan['legend'][plan['rows'][5][11]][1])
        self.assertFalse(plan['legend'][plan['rows'][6][11]][1])


if __name__ == '__main__':
    unittest.main()
