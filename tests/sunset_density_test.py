"""Protect actual roads, old quests and native cache space during Sunset infill."""
from collections import deque
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts/romhack')]
from sunset_density import BASE, decorate, strip, footprint, remap, extend
from native_resources import named_addresses
from maps import encode_layout


def reachable(plan):
    denied = {(n['x'], n['y']) for n in plan['npcs']}
    seen = {(28, 22)}
    queue = deque(seen)
    while queue:
        x, y = queue.popleft()
        for a, b in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if 0 <= a < 32 and 0 <= b < 32 and (a, b) not in denied | seen:
                if not plan['legend'][plan['rows'][b][a]][1]:
                    seen.add((a, b)); queue.append((a, b))
    return seen


class SunsetDensity(unittest.TestCase):
    def setUp(self):
        self.old = json.loads((ROOT/BASE/'source-plan.json').read_text())
        self.plan = decorate(self.old, ROOT)

    def test_three_empty_lots_preserve_all_roads_services_and_remaining_routes(self):
        self.assertEqual(strip(self.plan, ROOT), self.old)
        cells = footprint()
        self.assertEqual(len(cells), 45)
        walls = {p for p, (_, token) in cells.items() if token == 'C'}
        self.assertEqual(len(walls), 36)
        self.assertEqual(reachable(self.plan), reachable(self.old)-walls)
        for y, row in enumerate(self.old['rows']):
            for x, token in enumerate(row):
                if (x, y) in cells:
                    self.assertEqual(token, '.')
                else:
                    self.assertEqual(self.plan['rows'][y][x], token)
        for point in ((16, 8), (16, 9), (23, 17), (21, 19), (23, 19), (25, 19), (28, 22)):
            self.assertIn(point, reachable(self.plan))

    def test_native_remap_changes_only_the_literal_compact_home_ids(self):
        original = encode_layout(self.plan)[2]
        changed = remap(self.plan, original, ROOT)
        self.assertEqual(len(changed), 2048)
        for i, (a, b) in enumerate(zip(struct.unpack('<1024H', original), struct.unpack('<1024H', changed))):
            point = (i % 32, i // 32)
            if point in footprint():
                record, token = footprint()[point]
                self.assertEqual(b & 1023, record)
                self.assertEqual(b & 0xfc00, 0xc00 if token == 'C' else 0x3000)
            else:
                self.assertEqual(a, b)

    def test_changed_roads_escaped_tokens_or_collision_fail_closed(self):
        for x, y, token in ((28, 4, '.'), (27, 4, 'C'), (28, 8, 'C')):
            bad = deepcopy(self.plan); row = bad['rows'][y]
            bad['rows'][y] = row[:x]+token+row[x+1:]
            with self.assertRaises(ValueError): strip(bad, ROOT)
        bad = deepcopy(self.plan); bad['legend']['C'][1] = False
        with self.assertRaises(ValueError): strip(bad, ROOT)
        bad = deepcopy(self.old); row = bad['rows'][4]
        bad['rows'][4] = row[:28]+'P'+row[29:]
        with self.assertRaises(ValueError): decorate(bad, ROOT)

    def test_actual_old_resources_extend_without_wave_or_door_cache_aliases(self):
        target = ROOT/'.tools/romhack-drafts/0.0.79-park-density-preview/185cab500852af16e5229e9005cc601b7a16ac6cf764ce30778a7a15bbe820db'
        if not (target/'target.gba').exists():
            self.skipTest('Private local v79 cartridge required for legacy resource input.')
        rom = (target/'target.gba').read_bytes()
        self.assertEqual(hashlib.sha256(rom).hexdigest(), target.name)
        names = {'gMetatiles_Petalburg', 'gMetatileAttributes_Petalburg', 'gTilesetPalettes_Petalburg'}
        addresses = named_addresses(target/'target.elf', names)
        def read(name, size):
            start = addresses[name]-0x08000000
            return rom[start:start+size]
        old = ((ROOT/BASE/'secondary.4bpp').read_bytes(), read('gMetatiles_Petalburg', 3104),
               read('gMetatileAttributes_Petalburg', 388), read('gTilesetPalettes_Petalburg', 512))
        graphics, records, attrs, palettes = extend(ROOT, *old)
        self.assertEqual((len(graphics), len(records), len(attrs), len(palettes)), (16384, 3696, 462, 512))
        self.assertEqual(graphics[:401*32], old[0][:401*32])
        self.assertEqual(graphics[491*32:], bytes(21*32))
        self.assertEqual(records[:3104], old[1]); self.assertEqual(attrs[:388], old[2])
        self.assertEqual(palettes[:256], old[3][:256]); self.assertEqual(palettes[320:], old[3][320:])
        for index in range(194, 231):
            for word in struct.unpack_from('<8H', records, index*16):
                self.assertNotIn((word & 1023)-512, range(240, 248))
                self.assertLess(word & 1023, 1016)
        bad = bytearray(old[0]); bad[10] ^= 1
        with self.assertRaises(ValueError): extend(ROOT, bytes(bad), *old[1:])


if __name__ == '__main__': unittest.main()
