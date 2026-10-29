"""Castro's theater crossing remains colorful and walkable."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from generate_world import generate
from world_tiles import compile_kit


class CastroCrossingTest(unittest.TestCase):
    def test_five_stripes_are_walkable_at_the_theater(self):
        manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
        plans = {p['world_id']: p for p in generate(manifest)}
        castro, north = plans['castro'], plans['north_beach']
        kit = compile_kit(profile=castro['tile_profile'])
        colors = ('red', 'gold', 'green', 'blue', 'violet')
        stripes = [kit['catalog']['castro_crossing_' + color]['tiles'][0][0] for color in colors]
        self.assertEqual(len(set(stripes)), len(colors))
        for y in range(11, 14):
            for x, expected in enumerate(stripes, 14):
                entry = castro['legend'][castro['rows'][y][x]]
                self.assertEqual(entry, [expected, False, 3])
        for row in north['rows']:
            self.assertFalse(any(north['legend'][cell][0] in stripes for cell in row))


if __name__ == '__main__':
    unittest.main()
