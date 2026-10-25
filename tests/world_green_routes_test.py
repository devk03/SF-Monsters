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

    def test_exposed_forest_fronts_include_native_trunk_bases(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        for p in plans:
            if not (p.get('green_route_design') or p.get('native_park_design')):continue
            rows,legend=p['rows'],p['legend'];bases=0
            if p['world_id']=='sutro_tower':
                self.assertEqual(p['border_metatiles'],[14,14,22,22])
                for y in range(2,len(rows)-2,2):
                    for x in range(2,len(rows[0])-2):
                        if legend[rows[y][x]][0]==14:self.assertEqual(legend[rows[y+1][x]][0],22)
                continue
            for y in range(2,len(rows)-4,2):
                for x in range(2,len(rows[0])-2,2):
                    top=[legend[rows[y][x+dx]][0] for dx in (0,1)]
                    below=[legend[rows[y+2][x+dx]][0] for dx in (0,1)]
                    if top==[0x1d4,0x1d5] and below!=top:
                        self.assertEqual(below,[0x1e4,0x1e5],p['world_id']+': exposed canopy needs its actual lower edge')
                        bases+=1
            self.assertGreater(bases,0)

    def test_expanded_reserves_keep_complete_native_canopies(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        parks=[p for p in plans if p.get('native_park_design')]
        self.assertEqual(len(parks),5)
        for p in parks:
            expected=[14,14,22,22] if p['world_id']=='sutro_tower' else [0x1d4,0x1d5,0x1dc,0x1dd]
            trees=set(expected)
            self.assertEqual(p['border_metatiles'],expected)
            count=0
            for y in range(2,62,2):
                for x in range(2,94,2):
                    cells=[p['legend'][p['rows'][y+dy][x+dx]][0] for dy in (0,1) for dx in (0,1)]
                    if any(t in trees for t in cells):
                        self.assertEqual(cells,expected);count+=1
            self.assertGreater(count,100)

    def test_park_branches_have_readable_furnished_stops_and_integrated_forest(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        parks=[p for p in plans if p.get('native_park_design')]
        for p in parks:
            self.assertEqual(len(p['park_stops']),3)
            for stop in p['park_stops']:
                x,y=stop['object'];sx,sy=stop['standing']
                self.assertEqual(p['legend'][p['rows'][y][x]],[3,True,3])
                self.assertFalse(p['legend'][p['rows'][sy][sx]][1])
                self.assertIn('fixture',stop)
                self.assertTrue(any(e['x']==x and e['y']==y and e['script']==stop['script'] for e in p['bg_events']))
            forest=sum(p['legend'][p['rows'][y][x]][0] in {14,22,0x1d4,0x1d5,0x1dc,0x1dd,0x1e4,0x1e5}
                       for y in range(4,20) for x in range(4,28))
            self.assertGreater(forest,30,'Legacy filler must integrate with the native reserve forest')

    def test_park_pond_is_scenery_with_a_walkable_native_bank(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        park=next(p for p in plans if p['world_id']=='golden_gate_park')
        pond=park['scenic_pond']
        for x,y in pond['water']:
            _,blocked,elevation=park['legend'][park['rows'][y][x]]
            self.assertTrue(blocked);self.assertEqual(elevation,3)
        for x,y in pond['south_bank']:
            self.assertEqual(park['legend'][park['rows'][y][x]],[1,False,3])
        self.assertIn(0xa1,{park['legend'][park['rows'][y][x]][0] for x,y in pond['water']})
        # A cove separates the northern lobes, while the complete water body
        # stays connected. This rejects the former rectangular pond.
        water={tuple(point) for point in pond['water']}
        north=min(y for x,y in water)
        edge=sorted(x for x,y in water if y==north)
        self.assertTrue(any(x not in edge for x in range(min(edge),max(edge)+1)))
        seen={next(iter(water))};pending=list(seen)
        while pending:
            x,y=pending.pop()
            for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if point in water and point not in seen:seen.add(point);pending.append(point)
        self.assertEqual(seen,water)
        self.assertEqual({tuple(p) for p in pond['south_bank']},{(x,44) for x in range(58,76)})



if __name__=='__main__':unittest.main()
