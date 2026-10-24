"""Protect the user's rejection of repeated painted forest corridors."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate
from world_trail_ground import WORN_IDS


class GreenRouteTests(unittest.TestCase):
    def test_native_grass_paths_whole_trees_and_distinct_geometry(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        routes=[p for p in plans if p.get('green_route_design')]
        self.assertGreaterEqual(len(routes),11)
        self.assertEqual(len({tuple(p['rows']) for p in routes}),len(routes))
        trees={0x1d4,0x1d5,0x1dc,0x1dd}
        for plan in routes:
            with self.subTest(route=plan['world_id']):
                rows,legend=plan['rows'],plan['legend']
                ground={legend[t][0] for row in rows for t in row if not legend[t][1]}
                self.assertTrue({1,13}<=ground<=({1,4,13}|WORN_IDS),'Native grass/flowers replace the white corridor')
                self.assertEqual(plan['border_metatiles'],[0x1d4,0x1d5,0x1dc,0x1dd])
                self.assertEqual(len(plan['town_blocks']),1,'Each branch retains its intended rest stop')
                self.assertLess(len(plan['encounter_positions']),20,'Encounter grass is a patch, not a perimeter outline')
                for y in range(2,22,2):
                    for x in range(2,30,2):
                        footprint=[legend[rows[y+dy][x+dx]][0] for dy in (0,1) for dx in (0,1)]
                        if any(tile in trees for tile in footprint):
                            self.assertEqual(footprint,[0x1d4,0x1d5,0x1dc,0x1dd],'Do not cut partial tree silhouettes')

    def test_expanded_reserves_keep_complete_native_canopies(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        parks=[p for p in plans if p.get('native_park_design')]
        self.assertEqual(len(parks),5)
        for p in parks:
            trees={0x1d4,0x1d5,0x1dc,0x1dd}
            self.assertEqual(p['border_metatiles'],[0x1d4,0x1d5,0x1dc,0x1dd])
            count=0
            for y in range(2,62,2):
                for x in range(2,94,2):
                    if x<32 and y<24:continue
                    cells=[p['legend'][p['rows'][y+dy][x+dx]][0] for dy in (0,1) for dx in (0,1)]
                    if any(t in trees for t in cells):
                        self.assertEqual(cells,[0x1d4,0x1d5,0x1dc,0x1dd]);count+=1
            self.assertGreater(count,100)


if __name__=='__main__':unittest.main()
