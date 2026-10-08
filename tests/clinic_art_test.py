"""Clinic native capacity, draw layers and service/save layout contracts."""
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from clinic_art import apply_clinic, clinic_resources, clinic_tile, paving, align_ground, joined_wall
from maps import encode_layout


class ClinicArt(unittest.TestCase):
    def test_native_exit_layers_and_capacity_keep_actors_and_warp_visible(self):
        graphics,records,attributes,palettes=clinic_resources(ROOT)
        self.assertLessEqual(len(graphics)//32,504)
        self.assertEqual(len(records),106*16)
        self.assertEqual(len(palettes),512)
        flags=struct.unpack('<106H',attributes)
        self.assertEqual(flags[1],0x1065)
        self.assertEqual({i for i,flag in enumerate(flags) if flag>>12!=1},{52,53})
        self.assertEqual(flags[52:54],(0,0))
        self.assertEqual(records[52*16:52*16+8],records[2*16+8:3*16])
        self.assertEqual(records[53*16:53*16+8],records[2*16+8:3*16])
        for index in range(1,5):
            self.assertEqual(len({palettes[bank*32+index*2:bank*32+index*2+2]
                                  for bank in range(6,10)}),1)
        for record,bank in ((2,6),(6,7),(8,8),(7,9)):
            foreground=struct.unpack_from('<8H',records,record*16)[4:]
            self.assertEqual({value>>12 for value in foreground},{bank})

    def test_recovery_palette_phases_preserve_geometry_and_ground(self):
        graphics,records,attributes,palettes=clinic_resources(ROOT)
        for phase,bank in enumerate((10,11,12)):
            for corner,base in enumerate((28,29,30,31)):
                original=struct.unpack_from('<8H',records,base*16)
                animated=struct.unpack_from('<8H',records,(94+phase*4+corner)*16)
                self.assertEqual([v&0xfff for v in original],[v&0xfff for v in animated])
                self.assertEqual({v>>12 for v in animated[4:]},{bank})
                self.assertEqual(attributes[base*2:base*2+2],
                                 attributes[(94+phase*4+corner)*2:(95+phase*4+corner)*2])
            base=struct.unpack_from('<16H',palettes,7*32)
            current=struct.unpack_from('<16H',palettes,bank*32)
            self.assertEqual({i for i in range(16) if base[i]!=current[i]},{10,12,13})
        self.assertEqual(len(graphics)//32,328) # no duplicated pixel geometry

    def test_overlay_keeps_collision_elevation_and_existing_service_locations(self):
        plan=json.loads((ROOT/'romhack/content/services.json').read_text())
        self.assertEqual(plan['border_tile'],512) # never repeat the exit arrow outside
        width,height,original=encode_layout(plan)
        with tempfile.TemporaryDirectory() as directory:
            engine=Path(directory)
            map_path=engine/'data/layouts/LittlerootTown_ProfessorBirchsLab/map.bin'
            map_path.parent.mkdir(parents=True);map_path.write_bytes(original)
            for file in ('graphics.h','metatiles.h','headers.h'):
                path=engine/'src/data/tilesets'/file
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text('// baseline\n')
            changed=apply_clinic(ROOT,engine)
            output=map_path.read_bytes()
            self.assertEqual(len(output),width*height*2)
            for offset in range(0,len(output),2):
                before=struct.unpack_from('<H',original,offset)[0]
                after=struct.unpack_from('<H',output,offset)[0]
                self.assertEqual(before&0xfc00,after&0xfc00)
                self.assertTrue(512<=after&0x3ff<606)
            self.assertEqual(clinic_tile(plan,6,12),513)
            self.assertEqual(clinic_tile(plan,2,3),547) # full-size storage terminal
            self.assertEqual(clinic_tile(plan,10,2),605) # full-width team notes
            for npc in plan['npcs']:
                self.assertEqual(clinic_tile(plan,npc['x'],npc['y']),
                                 565 if npc['script']=='SF_PatrickShop' else 514)
            graphics=(engine/'src/data/tilesets/graphics.h').read_text()
            self.assertIn('gTilesetTiles_SFSouthParkClinic',graphics)
            self.assertIn('secondary/sf_south_park_clinic/tiles.png',graphics)
            self.assertTrue(all((engine/file).exists() for file in changed))

    def test_small_ground_repeat_and_connected_corners_do_not_stamp_card_frames(self):
        palette=clinic_resources(ROOT)[3][192:224]
        floor=paving(palette)
        self.assertEqual(floor[:8],floor[8:16])
        self.assertEqual(floor[:128],floor[128:])
        self.assertNotIn(4,floor) # shared dark prop outline is never floor grout
        band=bytes(5+y for y in range(8) for x in range(16))
        north=joined_wall(floor,band,'N');west=joined_wall(floor,band,'W')
        corner=joined_wall(floor,band,'NW')
        self.assertEqual(corner[:16],north[:16])
        self.assertEqual(corner[0::16],west[0::16])
        self.assertEqual(corner[8*16+8:8*16+16],floor[8*16+8:8*16+16])
        # Repeating material phase continues beneath floor-colored prop surrounds;
        # an outlined white prop interior is preserved rather than retiled.
        pixels=bytearray([1]*256)
        for y in range(4,12):
            for x in range(4,12):pixels[y*16+x]=4 if x in (4,11) or y in (4,11) else 1
        result=align_ground(pixels,16,16,floor)
        self.assertEqual(result[:16],floor[:16])
        self.assertEqual(result[5*16+5:5*16+11],bytes([1]*6))
        plan=json.loads((ROOT/'romhack/content/services.json').read_text())
        self.assertEqual({clinic_tile(plan,x,y) for x,y in ((0,1),(12,1),(0,12),(12,12))},
                         {597,598,599,600})

    def test_full_size_furniture_keeps_services_and_counter_approachable(self):
        from collections import deque
        plan=json.loads((ROOT/'romhack/content/services.json').read_text())
        self.assertFalse(any('r' in row for row in plan['rows']))
        occupied={(npc['x'],npc['y']) for npc in plan['npcs']}
        pending=deque([(6,11)]);reachable=set()
        while pending:
            x,y=pending.popleft()
            if (x,y) in reachable:continue
            reachable.add((x,y))
            for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0<=yy<len(plan['rows']) and 0<=xx<len(plan['rows'][yy]):
                    token=plan['rows'][yy][xx]
                    if not plan['legend'][token][1] and (xx,yy) not in occupied:
                        pending.append((xx,yy))
        for point in ((6,5),(2,4),(9,8),(9,11),(10,3),(11,7)):
            self.assertIn(point,reachable)
        front=next(event for event in plan['bg_events'] if event['script']=='SF_ClinicCounterShop')
        self.assertEqual((front['x'],front['y']),(9,10))
        self.assertEqual(front['player_facing_dir'],'BG_EVENT_PLAYER_FACING_NORTH')


if __name__=='__main__':unittest.main()
