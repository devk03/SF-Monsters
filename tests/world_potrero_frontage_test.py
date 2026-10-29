"""The west Potrero block should be dense and still accessible."""
import json
import sys
import unittest
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate
from world_tiles import compile_kit


class PotreroFrontageTests(unittest.TestCase):
    def test_joined_hill_fronts_have_a_walkable_street_and_real_ends(self):
        manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
        plan=next(p for p in generate(manifest) if p['world_id']=='potrero_hill')
        kit=compile_kit(profile=plan['tile_profile'])
        blocks=sorted((b for b in plan['town_blocks'] if b['y']==24 and 4<=b['x']<=27),key=lambda b:b['x'])
        self.assertGreaterEqual(len(blocks),7)
        self.assertEqual(blocks[0]['x'],4)
        for a,b in zip(blocks,blocks[1:]):self.assertEqual(a['x']+a['width'],b['x'])
        self.assertEqual(kit['catalog'][blocks[0]['style']]['closed_edges'],['left'])
        self.assertEqual(kit['catalog'][blocks[-1]['style']]['closed_edges'],['right'])
        self.assertGreaterEqual(len({kit['catalog'][b['style']]['architecture_type'] for b in blocks}),5)
        # Inserting this northern block must not renumber the established
        # southern frontage or change its collision footprint for old saves.
        south=[(b['x'],b['style']) for b in plan['town_blocks'] if b['y']==49 and 4<=b['x']<=16]
        self.assertEqual(south,[(4,'deco_l'),(7,'arcade_m__sage'),(10,'walkup_m'),
                                (13,'gable_m__sage'),(16,'walkup_r__slate')])
        rows,legend=plan['rows'],plan['legend']
        start=(5,9);seen={start};queue=deque([start])
        self.assertFalse(legend[rows[start[1]][start[0]]][1])
        while queue:
            x,y=queue.popleft()
            for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
                nx,ny=x+dx,y+dy
                if 0<=ny<len(rows) and 0<=nx<len(rows[ny]) and (nx,ny) not in seen and not legend[rows[ny][nx]][1]:
                    seen.add((nx,ny));queue.append((nx,ny))
        for x in range(4,28):self.assertIn((x,29),seen)
        self.assertTrue(all((event['x'],event['y']) not in {(x,y) for x in range(4,28) for y in range(24,28)}
                            for event in plan['npcs']+plan['bg_events']+plan['coord_events']))
