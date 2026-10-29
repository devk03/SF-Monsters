"""The North Beach street wall must preserve the nearby court and access."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from generate_world import generate
from world_tiles import compile_kit


class NorthBeachBlockTests(unittest.TestCase):
    def test_joined_wall_and_preserved_court(self):
        plan = next(p for p in generate(json.loads((ROOT / 'romhack/world/world.json').read_text()))
                    if p['world_id'] == 'north_beach')
        catalog = compile_kit(profile=plan['tile_profile'])['catalog']
        row = sorted((b for b in plan['town_blocks'] if b['y'] == 1 and 61 <= b['x'] < 81), key=lambda b: b['x'])
        self.assertEqual((row[0]['x'], row[-1]['x'] + row[-1]['width']), (61, 81))
        for left, right in zip(row, row[1:]):
            self.assertEqual(left['x'] + left['width'], right['x'])
        self.assertIn('left', catalog[row[0]['style']]['closed_edges'])
        self.assertEqual(plan['pedestrian_courts'][0]['rest'], [58, 4])
        self.assertEqual(plan['court_notices'][0]['object'], [59, 4])
        rows, legend = plan['rows'], plan['legend']
        seen, queue = {(16, 10)}, deque([(16, 10)])
        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= ny < len(rows) and 0 <= nx < len(rows[ny]) and (nx, ny) not in seen and not legend[rows[ny][nx]][1]:
                    seen.add((nx, ny)); queue.append((nx, ny))
        for point in ((58, 4), (61, 5), (69, 5), (65, 12)):
            self.assertIn(point, seen)


if __name__ == '__main__':
    unittest.main()
