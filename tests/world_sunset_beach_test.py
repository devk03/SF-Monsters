"""The coastal beach must be reachable without opening the ocean to walking."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from generate_world import generate


class SunsetBeachTests(unittest.TestCase):
    def test_beach_reachable_and_water_stays_solid(self):
        manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
        plan = next(p for p in generate(manifest) if p['world_id'] == 'outer_sunset')
        rows, legend = plan['rows'], plan['legend']
        seen = {(14, 8)}
        queue = deque(seen)
        while queue:
            x, y = queue.popleft()
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if (0 <= ny < len(rows) and 0 <= nx < len(rows[ny])
                        and (nx,ny) not in seen and not legend[rows[ny][nx]][1]):
                    seen.add((nx,ny)); queue.append((nx,ny))
        for point in ((10,35), (10,45), (16,32), (94,32)):
            self.assertIn(point, seen)
        self.assertEqual(legend[rows[35][10]][0], 0x124)  # Native sand.
        self.assertTrue(legend[rows[35][5]][1])  # Ocean cannot be walked on.
        self.assertFalse(any(b['style']=='street_tree' and (b['x'],b['y'])==(12,32) for b in plan['town_blocks']))
        for _,x,y in plan['sunset_dunes']['plantings']:
            self.assertIn((x,y),seen)
            self.assertFalse(legend[rows[y][x]][1])
        for point in ((12,32),(13,33)):
            self.assertIn(point,seen)
            self.assertEqual(legend[rows[point[1]][point[0]]][0],0x124)
        from world_sunset_beach_edge import STRIP, SOUTH, PLANTS
        plants = {(x,y) for _,x,y in PLANTS}
        for x,y in STRIP | SOUTH:
            self.assertIn((x,y),seen)
            self.assertFalse(legend[rows[y][x]][1])
            if (x,y) not in plants:
                self.assertEqual(legend[rows[y][x]][0],0x124)
        self.assertEqual(len(plan['sunset_beach_edge']['plantings']),len(PLANTS))



if __name__ == '__main__':
    unittest.main()
