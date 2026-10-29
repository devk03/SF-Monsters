"""Sutro Baths must remain a reachable landmark, not a blocked route."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate
from world_lands_end_baths import POOLS,prepare


class LandsEndBathsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
        cls.plan=next(p for p in generate(manifest) if p['world_id']=='lands_end')

    def test_old_stops_and_new_courtyard_reachable_from_local_arrival(self):
        plan=self.plan;rows=plan['rows'];legend=plan['legend']
        seen={(12,10)};queue=deque(seen)
        while queue:
            x,y=queue.popleft()
            for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
                nx,ny=x+dx,y+dy
                if 0<=ny<len(rows) and 0<=nx<len(rows[ny]) and (nx,ny) not in seen and not legend[rows[ny][nx]][1]:
                    seen.add((nx,ny));queue.append((nx,ny))
        for point in ((19,32),(10,36),(61,40),(29,48),(94,32)):
            self.assertIn(point,seen)
        for pool in POOLS:
            for x,y in pool:self.assertTrue(legend[rows[y][x]][1],(x,y))
        # The promenade actually crosses the pre-existing trail; it must not
        # become two visually disconnected strips or block that route.
        crossing=[legend[rows[32][x]] for x in range(14,20)]
        from world_tiles import compile_kit
        walk={tile for row in compile_kit(profile='nature')['catalog']['baths_walk']['tiles'] for tile in row}
        self.assertTrue(all(cell[0] in walk and not cell[1] for cell in crossing))
        self.assertEqual([(n['x'],n['y']) for n in plan['npcs']],[(12,9),(14,37),(65,41)])

    def test_reserved_landmark_rejects_a_route_or_event_conflict(self):
        p={'world_id':'lands_end','access_points':[],'bg_events':[], 'coord_events':[],'npcs':[]}
        with self.assertRaisesRegex(ValueError,'overlaps'):
            prepare(p,{(20,26)},set())
        p['npcs']=[{'x':20,'y':24}]
        with self.assertRaisesRegex(ValueError,'event'):
            prepare(p,set(),set())
        p['npcs']=[{'x':8,'y':32,'range_x':1}]
        with self.assertRaisesRegex(ValueError,'event'):
            prepare(p,set(),set())
