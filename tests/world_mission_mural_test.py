"""The Mission's new mural frontage must remain distinct and reachable."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate


class MissionMuralTests(unittest.TestCase):
    def test_original_mural_and_shops_keep_the_street_accessible(self):
        new=(ROOT/'assets/tiles/mission-mural-sun-v1/mural.indices').read_bytes()
        old=(ROOT/'assets/tiles/neighborhood-landmarks-v1/mural.indices').read_bytes()
        self.assertEqual(len(new),64*32)
        self.assertNotEqual(new,old)
        self.assertLessEqual(max(new),15)
        plan=next(p for p in generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
                  if p['world_id']=='mission')
        blocks={(b['style'],b['x'],b['y']) for b in plan['town_blocks']}
        self.assertIn(('mission_sun_mural',9,26),blocks)
        self.assertIn(('mission_mural_backdrop',9,24),blocks)
        self.assertTrue(any(style.startswith('shophouse') and x==4 and y==24 for style,x,y in blocks))
        self.assertTrue(any(style.startswith('shophouse') and x==13 and y==24 for style,x,y in blocks))
        rows,legend=plan['rows'],plan['legend'];start=(5,9);seen={start};queue=deque([start])
        while queue:
            x,y=queue.popleft()
            for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
                nx,ny=x+dx,y+dy
                if 0<=ny<len(rows) and 0<=nx<len(rows[ny]) and (nx,ny) not in seen and not legend[rows[ny][nx]][1]:
                    seen.add((nx,ny));queue.append((nx,ny))
        for point in ((10,29),(48,21),(79,45)):self.assertIn(point,seen)
        # The backing connects the wall vertically to the painting, and the
        # existing walkway in front remains passable to both neighboring shops.
        for y in range(24,28):
            for x in range(9,13):self.assertTrue(legend[rows[y][x]][1])
        for x in range(4,15):self.assertIn((x,29),seen)

