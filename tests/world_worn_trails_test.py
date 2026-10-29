"""Visible dirt trails must read as connected paths, not diagonal tile islands."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate
from world_district_layouts import raster_path,worn_path


def reachable(cells,start):
    seen={start};pending=deque([start])
    while pending:
        x,y=pending.popleft()
        for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if point in cells and point not in seen:
                seen.add(point);pending.append(point)
    return seen


class WornTrailTests(unittest.TestCase):
    def test_twin_lane_cannot_certify_an_isolated_summit(self):
        from world_twin_summits import furnish
        grid=[['.' for _ in range(96)] for _ in range(64)]
        for row in grid:row[32]='#'
        plan={'world_id':'twin_peaks','legend':{'.':[1,False,3],'#':[11,True,3]},
              'npcs':[]}
        draft={'trail':set(),'lanes':{(16,10),(45,18)},'protected':set(),
               'faces':{},'stairs':{},'rims':[]}
        with self.assertRaisesRegex(ValueError,'strands'):
            furnish(plan,grid,draft,None)

    def test_diagonal_trails_share_edges_without_widening_the_walking_corridor(self):
        for line in ([(2,2),(13,9)],[(13,2),(2,9)],
                     [(2,2),(8,12),(19,5)],[(4,4),(4,4)],
                     [(2,2),(7,2),(7,8)]):
            with self.subTest(line=line):
                trail=worn_path(line)
                self.assertEqual(reachable(trail,line[0]),trail)
                self.assertTrue(set(line)<=trail)
                self.assertTrue(trail<=raster_path(line,radius=1))
                self.assertTrue(raster_path(line,radius=0)<=trail)
                self.assertEqual(trail,worn_path(list(reversed(line))))

    def test_existing_straight_trail_width_is_unchanged(self):
        for line in ([(3,2),(3,19)],[(2,7),(28,7)]):
            self.assertEqual(worn_path(line),raster_path(line,radius=0))

    def test_actual_twin_hillside_dirt_connects_without_using_grass_as_a_bridge(self):
        manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
        plan=next(p for p in generate(manifest) if p['world_id']=='twin_peaks')
        # This unobstructed declared hillside segment has no furniture/actor
        # exception. Grass being walkable must not hide a broken painted path.
        dirt={(x,y) for y in range(12,25) for x in range(60,81)
              if plan['legend'][plan['rows'][y][x]][0]==0x124}
        self.assertIn((60,12),dirt);self.assertIn((80,24),dirt)
        self.assertIn((80,24),reachable(dirt,(60,12)))


if __name__=='__main__':unittest.main()
