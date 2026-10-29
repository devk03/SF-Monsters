"""The Outer Sunset house walls keep their relocated reading notice."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate
from world_tiles import compile_kit


class OuterSunsetJoinTest(unittest.TestCase):
    def test_two_joined_walls_and_notice(self):
        manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
        p=next(p for p in generate(manifest) if p['world_id']=='outer_sunset')
        catalog=compile_kit(profile=p['tile_profile'])['catalog']
        for y in (37,44):
            blocks=sorted((b for b in p['town_blocks'] if b['y']==y and 52<=b['x']<=60),key=lambda b:b['x'])
            self.assertEqual([(b['x'],b['width']) for b in blocks],[(52,3),(55,3),(58,3)])
            self.assertIn('left',catalog[blocks[0]['style']]['closed_edges'])
            self.assertIn('right',catalog[blocks[-1]['style']]['closed_edges'])
        notice=next(n for n in p['court_notices'] if n['script']=='WBCourt_outer_sunset_1')
        self.assertEqual((notice['object'],notice['standing']),([57,48],[57,49]))
        self.assertTrue(any((e['x'],e['y'],e['script'])==(57,48,notice['script']) for e in p['bg_events']))
        self.assertTrue(any((e['x'],e['y'])==(57,49) and e.get('name')=='pedestrian_court_1' for e in p['access_points']))
        for y in (49,50,51):self.assertFalse(p['legend'][p['rows'][y][57]][1])


if __name__=='__main__':unittest.main()
