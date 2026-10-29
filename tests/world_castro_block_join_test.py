"""Castro's joined block retains accessible notice and complete ends."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate

class CastroBlockJoinTest(unittest.TestCase):
    def test_both_walls_and_notice(self):
        p=next(p for p in generate(json.loads((ROOT/'romhack/world/world.json').read_text())) if p['world_id']=='castro')
        for y,left,right in ((37,26,45),(43,26,45)):
            wall=sorted((b for b in p['town_blocks'] if b['y']==y and left<=b['x']<right and b.get('height')==4),key=lambda b:b['x'])
            self.assertEqual(wall[0]['x'],left)
            for a,b in zip(wall,wall[1:]):self.assertEqual(a['x']+a['width'],b['x'])
            self.assertEqual(wall[-1]['x']+wall[-1]['width'],right)
            self.assertTrue(wall[0]['style'].split('__')[0].endswith('_l'))
            self.assertTrue(wall[-1]['style'].split('__')[0].endswith('_r'))
        event=next(e for e in p['bg_events'] if e.get('script')=='WBCourt_castro_1')
        self.assertEqual((event['x'],event['y']),(44,41))
        self.assertEqual(next(n for n in p['court_notices'] if n['script']=='WBCourt_castro_1')['standing'],[45,41])
        rows,legend=p['rows'],p['legend'];seen={(16,10)};q=deque(seen)
        while q:
            x,y=q.popleft()
            for pt in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                nx,ny=pt
                if 0<=nx<96 and 0<=ny<64 and pt not in seen and not legend[rows[ny][nx]][1]:seen.add(pt);q.append(pt)
        self.assertIn((45,41),seen)
        self.assertTrue(legend[rows[41][44]][1])

if __name__=='__main__': unittest.main()
