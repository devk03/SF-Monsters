"""North Beach's rejoined central fronts retain a reachable reading notice."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate


class NorthBeachCentralBlockTest(unittest.TestCase):
    def test_complete_walls_and_notice(self):
        plan=next(p for p in generate(json.loads((ROOT/'romhack/world/world.json').read_text())) if p['world_id']=='north_beach')
        for y,left,right in ((37,26,43),(44,26,45)):
            wall=sorted((b for b in plan['town_blocks'] if b['y']==y and left<=b['x']<right and b['height']==4),key=lambda b:b['x'])
            self.assertEqual(wall[0]['x'],left)
            for a,b in zip(wall,wall[1:]):
                self.assertEqual(a['x']+a['width'],b['x'])
            self.assertEqual(wall[-1]['x']+wall[-1]['width'],right)
            self.assertTrue(wall[0]['style'].split('__')[0].endswith('_l'))
            self.assertTrue(wall[-1]['style'].split('__')[0].endswith('_r'))
        notice=next(n for n in plan['court_notices'] if n['script']=='WBCourt_north_beach_1')
        self.assertEqual((notice['object'],notice['standing']),([44,41],[45,41]))
        event=next(e for e in plan['bg_events'] if e.get('script')==notice['script'])
        self.assertEqual((event['x'],event['y']),(44,41))
        rows,legend=plan['rows'],plan['legend']
        seen,queue={(16,10)},deque([(16,10)])
        while queue:
            x,y=queue.popleft()
            for pt in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                nx,ny=pt
                if 0<=nx<96 and 0<=ny<64 and pt not in seen and not legend[rows[ny][nx]][1]:
                    seen.add(pt);queue.append(pt)
        self.assertIn((45,41),seen)
        self.assertTrue(legend[rows[41][44]][1])
        for x in (42,43,44):
            self.assertFalse(legend[rows[48][x]][1])


if __name__=='__main__':
    unittest.main()
