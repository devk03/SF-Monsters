"""Preserve accepted street pixels, public routes and real prop collisions."""
from collections import deque
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from city_dressing import decorate,strip,tile
from city_furniture import load
from park_map import park_resources,park_tile
from park_infill import resources

# These points are the intended street design, independently specified here.
SOLID={(11,7),(15,7),(17,7),(19,7),(23,7),(24,7),(26,7),(36,7),
       (37,7),(38,7),(18,11),(19,11),(34,11),(35,11)}
UPPER={(17,6),(36,6),(37,6),(38,6)}
BINDINGS={(17,6):120,(17,7):121,(36,6):120,(36,7):121,(19,7):122,
          (26,7):122,(11,7):123,(15,7):124,(23,7):125,(24,7):126,
          (37,6):127,(38,6):128,(37,7):129,(38,7):130,
          (18,11):131,(19,11):132,(34,11):133,(35,11):134}


def reachable(plan,start):
    blocked={(x,y) for y,row in enumerate(plan['rows']) for x,t in enumerate(row) if plan['legend'][t][1]}
    blocked|={(n['x'],n['y']) for n in plan['npcs']}
    seen={start};queue=deque(seen)
    while queue:
        x,y=queue.popleft()
        for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            a,b=point
            if 0<=a<40 and 0<=b<32 and point not in blocked|seen:
                seen.add(point);queue.append(point)
    return seen


class CityDressing(unittest.TestCase):
    def setUp(self):
        self.plan=json.loads((ROOT/'romhack/content/south-park.json').read_text())
        self.old=strip(self.plan)

    def test_exact_18_cell_overlay_and_only14_collision_changes(self):
        self.assertEqual(decorate(self.old),self.plan)
        changed={(x,y) for y,row in enumerate(self.plan['rows']) for x,t in enumerate(row)
                 if t!=self.old['rows'][y][x]}
        self.assertEqual(changed,SOLID|UPPER)
        for y,row in enumerate(self.plan['rows']):
            for x,token in enumerate(row):
                new=park_tile(self.plan,x,y)
                if (x,y) in changed:
                    self.assertEqual(new,BINDINGS[x,y])
                    self.assertEqual(self.old['rows'][y][x],'P')
                    self.assertEqual(self.plan['legend'][token],[0,(x,y) in SOLID,3])
                else:
                    self.assertEqual(new,park_tile(self.old,x,y))
                    self.assertEqual(self.plan['legend'][token],self.old['legend'][token])
        for key in ('npcs','warp_events','bg_events','metadata','tilesets','border_tile'):
            self.assertEqual(self.plan[key],self.old[key])

    def test_all_other_walkable_cells_remain_connected(self):
        self.assertEqual(reachable(self.plan,(7,26)),reachable(self.old,(7,26))-SOLID)
        visited=reachable(self.plan,(21,6))
        for point in ((21,7),(21,8),(13,5),(13,6),(13,7),(32,5),(32,6),(32,7),
                      (16,16),(16,17),(7,24),(7,26),(20,6),(22,6),(25,6),(28,6)):
            self.assertIn(point,visited)
        self.assertTrue(UPPER<=visited)
        self.assertFalse(SOLID&visited)

    def test_original395_tiles120_records_and_all_palettes_stay_exact(self):
        secondary=park_resources(ROOT);raw,records,attrs,palettes=resources(ROOT,secondary[1])
        baseline=ROOT/'assets/tiles/city-furniture-v1/baseline-v77'
        self.assertEqual(raw[:395*32],(baseline/'primary.4bpp').read_bytes())
        self.assertEqual(records[:120*16],(baseline/'metatiles.bin').read_bytes())
        self.assertEqual(attrs[:120*2],(baseline/'attributes.bin').read_bytes())
        self.assertEqual(palettes,(baseline/'palettes.gbapal').read_bytes())
        self.assertEqual((len(raw)//32,len(records)//16,len(attrs)//2),(449,135,135))
        self.assertLessEqual(len(raw)//32,512)
        expected_attrs=(0,0x1000,0x1000,0x1000,0x1000,0x1000,0x1000,
                        0,0,0x1000,0x1000,0x1000,0x1000,0x1000,0x1000)
        self.assertEqual(struct.unpack('<15H',attrs[240:]),expected_attrs)
        for index in range(120,135):
            self.assertEqual(records[index*16:index*16+8],secondary[1][312:320])
            words=struct.unpack_from('<4H',records,index*16+8)
            self.assertTrue(all(w>>12==5 and (w&1023)<449 for w in words))

    def test_no_footprint_or_collision_corruption_is_silently_stripped(self):
        corruptions=[]
        for point in ((17,6),(17,7),(21,7)):
            bad=deepcopy(self.plan);x,y=point;row=bad['rows'][y]
            bad['rows'][y]=row[:x]+('P' if point!=(21,7) else 'U')+row[x+1:]
            corruptions.append(bad)
        for field,value in ((1,False),(2,0)):
            bad=deepcopy(self.plan);bad['legend']['U'][field]=value;corruptions.append(bad)
        bad=deepcopy(self.plan);bad['city_furniture'][0]['x']=18;corruptions.append(bad)
        for bad in corruptions:
            with self.assertRaises(ValueError):strip(bad)
        bad=deepcopy(self.plan);bad['legend']['U'][1]=False
        with self.assertRaises(ValueError):tile(bad,17,7)

    def test_placement_refuses_events_or_nonpaving_and_duplicate_install(self):
        for point in ((17,6),(19,7),(18,11)):
            bad=deepcopy(self.old);bad['npcs'].append({'x':point[0],'y':point[1]})
            with self.assertRaises(ValueError):decorate(bad)
            bad=deepcopy(self.old);x,y=point;row=bad['rows'][y]
            bad['rows'][y]=row[:x]+'R'+row[x+1:]
            with self.assertRaises(ValueError):decorate(bad)
        with self.assertRaises(ValueError):decorate(self.plan)

    def test_native_props_have_opaque_bases_and_transparent_surroundings(self):
        cards=load(ROOT);self.assertEqual(len(cards),8)
        for card in cards:
            w,h=card['width'],card['height'];pixels=card['pixels']
            self.assertTrue(any(pixels[(h-4)*w:]))
            self.assertIn(0,pixels);self.assertTrue(any(pixels))
            self.assertEqual(card['bank'],5)


if __name__=='__main__':unittest.main()
