"""Source reachability and independent native decode for original primary infill."""
from collections import deque
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from park_frontage import load
from park_infill import PLACEMENTS, APRON_ROWS, APRON_CARDS, previous_plan, resources
from park_map import park_resources, park_tile
from sidewalk_thresholds import load as load_thresholds


def reachable(plan):
    allowed = {(x,y) for y,row in enumerate(plan['rows']) for x,t in enumerate(row)
               if not plan['legend'][t][1]} - {(n['x'],n['y']) for n in plan['npcs']}
    seen = {(7,26)};queue = deque(seen)
    while queue:
        x,y = queue.popleft()
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if p in allowed and p not in seen:seen.add(p);queue.append(p)
    return seen


class PrimaryInfill(unittest.TestCase):
    def test_map_changes_only_53_solid_cells_and_primary_binding(self):
        plan = json.loads((ROOT/'romhack/content/south-park.json').read_text())
        old = previous_plan(plan)
        self.assertEqual(hashlib.sha256(json.dumps(old,sort_keys=True,
            separators=(',',':')).encode()).hexdigest(),
            '127e66fcca7545f970b98de53764d13081a7a7d3fefb0613f796303acf67f1d4')
        cells = {(x,y) for _,_,left,top,w,h,_ in PLACEMENTS
                 for y in range(top,top+h) for x in range(left,left+w)}
        self.assertEqual(len(cells),53)
        actual = {(x,y) for y,row in enumerate(plan['rows']) for x,t in enumerate(row)
                  if t != old['rows'][y][x]}
        self.assertEqual(cells,actual)
        for x,y in cells:
            self.assertEqual(plan['legend'][plan['rows'][y][x]],[0,True,0])
            self.assertIn(park_tile(plan,x,y),range(1,54))
        aprons={(left+i,top) for left,top,tiles in APRON_ROWS for i in range(len(tiles))}
        self.assertEqual(len(aprons),44)
        self.assertFalse(aprons&cells)
        for x,y in aprons:
            self.assertEqual(plan['rows'][y][x],'P')
            self.assertEqual(plan['legend']['P'],[699,False,3])
            self.assertIn(park_tile(plan,x,y),range(54,65))
        for x,y in reachable(old)-cells-aprons:
            self.assertEqual(park_tile(plan,x,y),park_tile(old,x,y))
        self.assertEqual(reachable(old)-cells,reachable(plan))
        for key in ('npcs','warp_events','bg_events','metadata','border_tile'):
            self.assertEqual(plan[key],old[key])
        events = plan['npcs']+plan['warp_events']+plan['bg_events']
        self.assertFalse(cells & {(e['x'],e['y']) for e in events})
        safe = reachable(plan)-{(e['x'],e['y']) for e in plan['warp_events']}
        self.assertLessEqual(max(min(abs(x-a)+abs(y-b) for a,b in safe)
                                 for x,y in cells),3)
        self.assertEqual(plan['tilesets']['primary'],'gTileset_SFParkFrontage')

    def test_all_primary_cells_decode_exact_pixels_palette_underlay_and_priority(self):
        secondary = park_resources(ROOT);raw,records,attrs,palettes = resources(ROOT,secondary[1])
        self.assertEqual((len(raw)//32,len(records)//16,len(attrs)//2,len(palettes)),
                         (235,65,65,512))
        self.assertEqual(raw[:32],bytes(32))
        self.assertEqual(palettes[128:160],
            (ROOT/'assets/tiles/south-park-paving-v1/paving.gbapal').read_bytes())
        self.assertEqual(palettes[160:192],
            (ROOT/'assets/tiles/sidewalk-thresholds-v1/thresholds.gbapal').read_bytes())
        self.assertEqual(palettes[192:],bytes(320))
        cards = {c['name']:c for c in load(ROOT)}
        for _,name,_,_,width,height,first in PLACEMENTS:
            card = cards[name]
            self.assertEqual(palettes[card['bank']*32:(card['bank']+1)*32],card['palette'])
            for index in range(width*height):
                words = struct.unpack_from('<8H',records,(first+index)*16)
                self.assertEqual(records[(first+index)*16:(first+index)*16+8],
                                 secondary[1][19*16+8:20*16])
                pixels = bytearray(256)
                for q,word in enumerate(words[4:]):
                    self.assertEqual(word>>12,card['bank'])
                    tile = word&1023;self.assertLess(tile,len(raw)//32)
                    for y in range(8):
                        for x in range(8):
                            xx = 7-x if word&1024 else x;yy = 7-y if word&2048 else y
                            pixels[(q//2*8+y)*16+q%2*8+x] = raw[tile*32+yy*4+xx//2]>>(xx%2*4)&15
                left,top = index%width*16,index//width*16
                expected = b''.join(card['pixels'][y*card['width']+left:y*card['width']+left+16]
                                    for y in range(top,top+16))
                self.assertEqual(bytes(pixels),expected)
                self.assertEqual(struct.unpack_from('<H',attrs,(first+index)*2)[0],
                                 0x1000 if index//width==height-1 else 0)

    def test_primary_rejects_secondary_underlay_outside_existing_residency(self):
        records = bytearray(park_resources(ROOT)[1])
        for word in (0x4000,0x43f8,0x6200,0x7200):
            bad = records[:];struct.pack_into('<H',bad,19*16+8,word)
            with self.assertRaisesRegex(ValueError,'underlay'):resources(ROOT,bytes(bad))

    def test_shallow_thresholds_decode_on_ground_without_replacing_existing_art(self):
        secondary=park_resources(ROOT);raw,records,attrs,palettes=resources(ROOT,secondary[1])
        cards=load_thresholds(ROOT)
        for name,first in APRON_CARDS:
            card=cards[name];width=card['width']//16
            for index in range(width):
                words=struct.unpack_from('<8H',records,(first+index)*16)
                self.assertEqual(records[(first+index)*16:(first+index)*16+8],secondary[1][312:320])
                self.assertEqual(struct.unpack_from('<H',attrs,(first+index)*2)[0],0x1000)
                pixels=bytearray(256)
                for q,word in enumerate(words[4:]):
                    self.assertEqual(word>>12,5);tile=word&1023
                    self.assertLess(tile,235)
                    for y in range(8):
                        for x in range(8):
                            xx=7-x if word&1024 else x;yy=7-y if word&2048 else y
                            pixels[(q//2*8+y)*16+q%2*8+x]=raw[tile*32+yy*4+xx//2]>>(xx%2*4)&15
                expected=b''.join(card['pixels'][y*card['width']+index*16:y*card['width']+index*16+16]
                                  for y in range(16))
                if name=='coffee':
                    expected=bytes(card['pixels'][y*card['width']+card['width']-1-(index*16+x)]
                                   for y in range(16) for x in range(16))
                self.assertEqual(bytes(pixels),expected)
                self.assertEqual(pixels[128:],bytes(128))

    def test_aprons_cannot_expand_into_walls_or_change_elevation(self):
        from copy import deepcopy
        plan=json.loads((ROOT/'romhack/content/south-park.json').read_text())
        for blocked in (True,False):
            changed=deepcopy(plan)
            changed['legend']['P']=[699,blocked,0]
            with self.assertRaisesRegex(ValueError,'walkable elevation3'):park_tile(changed,3,6)


if __name__ == '__main__':
    unittest.main()
