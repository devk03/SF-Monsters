"""The Mission street wall stays joined while its court remains usable."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from generate_world import generate


class MissionCourtBlockTest(unittest.TestCase):
    def test_north_frontage_and_relocated_notice(self):
        plan = next(p for p in generate(json.loads((ROOT / 'romhack/world/world.json').read_text()))
                    if p['world_id'] == 'mission')
        blocks = sorted((b for b in plan['town_blocks'] if b['y'] == 37 and 42 <= b['x'] <= 54), key=lambda b:b['x'])
        self.assertEqual([(b['x'],b['width']) for b in blocks],
                         [(42,3),(45,3),(48,2),(50,2),(52,2),(54,3)])
        self.assertEqual([b['style'].split('__')[0].rsplit('_',1)[-1] for b in blocks],
                         ['l','m','m','m','m','r'])
        rows, legend = plan['rows'], plan['legend']
        for y in range(37,41):
            for x in range(48,52):
                self.assertTrue(legend[rows[y][x]][1])
        sign = next(e for e in plan['bg_events'] if e.get('script') == 'WBCourt_mission_1')
        self.assertEqual((sign['x'],sign['y']), (58,40))
        self.assertTrue(legend[rows[40][58]][1])
        self.assertEqual(sign['player_facing_dir'], 'BG_EVENT_PLAYER_FACING_ANY')
        self.assertEqual(next(e for e in plan['court_notices'] if e['script'] == sign['script'])['standing'], [58,41])
        # The sign approach and all three cells of the little court remain
        # accessible from the district arrival after the wall is built.
        seen, queue = {(16,10)}, deque([(16,10)])
        while queue:
            x,y = queue.popleft()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                nx,ny = p
                if 0 <= nx < 96 and 0 <= ny < 64 and p not in seen and not legend[rows[ny][nx]][1]:
                    seen.add(p);queue.append(p)
        self.assertTrue({(58,41),(58,42),(58,43)} <= seen)
        for x in range(42,59):
            for y in (41,42,43):
                if (x,y) in seen:
                    self.assertIn(legend[rows[y][x]][0], (589,590))


if __name__ == '__main__':
    unittest.main()
