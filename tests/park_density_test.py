"""Accepted art preservation, denser parcels and intact sidewalks/quest routes."""
from collections import deque
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/romhack'),str(ROOT/'scripts/quality')]
from park_density import strip,decorate
from park_map import park_resources,park_tile
from park_infill import resources
from compact_townhouses import load
from connected_frontage_audit import cell_pixels


def expected_cells():
    result={}
    # Four-cell townhome pair, with five western/east-side existing parcels.
    for left,top,front in ((1,1,True),(1,12,True),(1,20,True),(10,13,False),(10,20,False)):
        for y in range(4):
            for x in range(4):result[left+x,top+y]=(135+y*4+x,True)
        if front:
            for x in range(4):result[left+x,top+4]=(531,False)
    # Park-facing coral/cream/lilac row; neither park grass nor curb props move.
    for x,source in enumerate((0,1,2,5,6,7,8,9,10)):
        for y in range(4):result[25+x,11+y]=(65+y*11+source,True)
    return result


def reachable(plan):
    denied={(x,y) for y,row in enumerate(plan['rows']) for x,t in enumerate(row) if plan['legend'][t][1]}
    denied|={(n['x'],n['y']) for n in plan['npcs']}
    seen={(7,26)};queue=deque(seen)
    while queue:
        x,y=queue.popleft()
        for a,b in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=a<40 and 0<=b<32 and (a,b) not in denied|seen:
                seen.add((a,b));queue.append((a,b))
    return seen


class ParkDensity(unittest.TestCase):
    def setUp(self):
        self.plan=json.loads((ROOT/'romhack/content/south-park.json').read_text())
        self.old=json.loads((ROOT/'assets/tiles/park-density-v1/baseline-v78/source-plan.json').read_text())

    def test_exact_parcels_and_every_other_map_word_preserved(self):
        self.assertEqual(strip(self.plan),self.old);self.assertEqual(decorate(self.old),self.plan)
        cells=expected_cells();self.assertEqual(len(cells),128)
        changed=collision=newsolid=freed=primary=0
        for y,row in enumerate(self.plan['rows']):
            for x,t in enumerate(row):
                oldt=self.old['rows'][y][x];before=park_tile(self.old,x,y)
                after=park_tile(self.plan,x,y);a=self.plan['legend'][t];b=self.old['legend'][oldt]
                changed+=(after,a[1:])!=(before,b[1:]);collision+=a[1:]!=b[1:];primary+=after<512
                if (x,y) in cells:
                    record,solid=cells[x,y];self.assertEqual((after,a[1:]),(record,[solid,0 if solid else 3]))
                    newsolid+=solid and not b[1];freed+=not solid and b[1]
                else:self.assertEqual((after,a),(before,b))
        self.assertEqual((changed,collision,newsolid,freed,primary),(125,65,56,9,189))
        for field in ('npcs','warp_events','bg_events','city_furniture','metadata','tilesets','border_tile'):
            self.assertEqual(self.plan[field],self.old[field])

    def test_both_sidewalks_park_habitat_and_all_remaining_routes_stay_open(self):
        before=reachable(self.old);after=reachable(self.plan)
        solid={p for p,(_,wall) in expected_cells().items() if wall and not self.old['legend'][self.old['rows'][p[1]][p[0]]][1]}
        freed={p for p,(_,wall) in expected_cells().items() if not wall and self.old['legend'][self.old['rows'][p[1]][p[0]]][1]}
        self.assertEqual(after,(before-solid)|freed)
        for x in (5,9):
            for y in range(1,31):self.assertEqual(self.plan['rows'][y][x],self.old['rows'][y][x])
        for point in ((13,5),(32,5),(16,16),(16,17),(21,7),(21,8),(21,11),(7,24),(7,26)):
            self.assertIn(point,after)
        for y,row in enumerate(self.old['rows']):
            for x,t in enumerate(row):
                if t in '.GBT' or (6<=x<=8) or (8<=y<=10):self.assertEqual(self.plan['rows'][y][x],t)

    def test_native_append_preserves_all_v78_resources_and_decodes_complete_pair(self):
        secondary=park_resources(ROOT);raw,records,attrs,palettes=resources(ROOT,secondary[1])
        baseline=ROOT/'assets/tiles/park-density-v1/baseline-v78'
        self.assertEqual((len(raw)//32,len(records)//16,len(attrs)//2),(511,151,151))
        self.assertEqual(raw[:449*32],(baseline/'primary.4bpp').read_bytes())
        self.assertEqual(records[:135*16],(baseline/'primary-metatiles.bin').read_bytes())
        self.assertEqual(attrs[:270],(baseline/'primary-attributes.bin').read_bytes())
        self.assertEqual(palettes,(baseline/'primary-palettes.bin').read_bytes())
        for value,name in zip(secondary,('secondary.4bpp','secondary-metatiles.bin','secondary-attributes.bin','secondary-palettes.bin')):
            self.assertEqual(value,(baseline/name).read_bytes())
        result=bytearray(4096)
        for index in range(16):
            cell=cell_pixels(raw,struct.unpack_from('<4H',records,(135+index)*16+8),bank=5)
            self.assertEqual(records[(135+index)*16:(135+index)*16+8],secondary[1][312:320])
            self.assertEqual(struct.unpack_from('<H',attrs,(135+index)*2)[0],0x1000 if index//4==3 else 0)
            for y in range(16):
                at=(index//4*16+y)*64+index%4*16;result[at:at+16]=cell[y*16:(y+1)*16]
        self.assertEqual(bytes(result),load(ROOT)[0])

    def test_invalid_collision_escape_or_unrelated_field_cannot_be_stripped(self):
        for x,y,token in ((1,1,'P'),(1,5,'V'),(9,13,'V')):
            bad=deepcopy(self.plan);row=bad['rows'][y];bad['rows'][y]=row[:x]+token+row[x+1:]
            with self.assertRaises(ValueError):strip(bad)
        for field,value in (('metadata',{'weather':'WEATHER_RAIN'}),('npcs',[])):
            bad=deepcopy(self.plan);bad[field]=value
            with self.assertRaises(ValueError):strip(bad)


if __name__=='__main__':unittest.main()
