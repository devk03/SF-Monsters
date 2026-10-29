"""The complete Mission mural frontage keeps its pedestrian viewpoint."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate


class MissionMuralStreetTest(unittest.TestCase):
    def test_full_frontage_and_viewpoint(self):
        plan=next(p for p in generate(json.loads((ROOT/'romhack/world/world.json').read_text())) if p['world_id']=='mission')
        row=sorted((b for b in plan['town_blocks'] if b['y']==24 and 13<=b['x']<=25),key=lambda b:b['x'])
        self.assertEqual([(b['x'],b['width']) for b in row],[(13,2),(15,3),(18,3),(21,3),(24,2)])
        self.assertEqual([b['style'].split('__')[0].rsplit('_',1)[-1] for b in row],['l','m','m','m','r'])
        self.assertTrue(any(b['style']=='mission_sun_mural' and (b['x'],b['y'])==(9,26) for b in plan['town_blocks']))
        rows,legend=plan['rows'],plan['legend']
        for x in range(15,27):
            self.assertIn(legend[rows[28][x]][0],(589,590))
            self.assertFalse(legend[rows[28][x]][1])
        seen,q={(16,10)},deque([(16,10)])
        while q:
            x,y=q.popleft()
            for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0<=nx<96 and 0<=ny<64 and (nx,ny) not in seen and not legend[rows[ny][nx]][1]:
                    seen.add((nx,ny));q.append((nx,ny))
        self.assertIn((10,29),seen)
        for x in range(15,26):self.assertIn((x,28),seen)


if __name__=='__main__':unittest.main()
