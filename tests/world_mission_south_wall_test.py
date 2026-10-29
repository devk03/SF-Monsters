"""Mission's added frontage stays continuous without losing its court."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from generate_world import generate


class MissionSouthWallTest(unittest.TestCase):
    def test_join_and_court_reachability(self):
        manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
        plan = next(p for p in generate(manifest) if p['world_id'] == 'mission')
        blocks = sorted((b for b in plan['town_blocks'] if b['y'] == 44 and 42 <= b['x'] <= 54), key=lambda b: b['x'])
        self.assertEqual([(b['x'], b['width']) for b in blocks], [(42,3),(45,3),(48,2),(50,2),(52,2),(54,3)])
        self.assertEqual([b['style'].split('__')[0].rsplit('_',1)[-1] for b in blocks], ['l','m','m','m','m','r'])
        sign = next(e for e in plan['bg_events'] if e.get('script') == 'WBCourt_mission_1')
        self.assertEqual((sign['x'], sign['y']), (51,40))
        checkpoint = next(e for e in plan['access_points'] if e.get('name') == 'pedestrian_court_1')
        self.assertEqual((checkpoint['x'],checkpoint['y']), (50,40))
        rows, legend = plan['rows'], plan['legend']
        seen, q = {(16,10)}, deque([(16,10)])
        while q:
            x,y = q.popleft()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                nx,ny = p
                if 0 <= nx < 96 and 0 <= ny < 64 and p not in seen and not legend[rows[ny][nx]][1]:
                    seen.add(p); q.append(p)
        self.assertIn((50,40),seen)
        for y in range(44,48):
            for x in range(48,52):
                self.assertTrue(legend[rows[y][x]][1])
        for x in range(48,52):
            self.assertIn(legend[rows[48][x]][0], (589,590))
            self.assertIn((x,48),seen)
        court = next(c for c in plan['pedestrian_courts'] if c['zone'] == 1)
        self.assertEqual((court['kind'],court['bounds']),('nook',[49,39,51,41]))


if __name__ == '__main__':
    unittest.main()
