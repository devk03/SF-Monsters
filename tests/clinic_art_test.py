"""Clinic native capacity, draw layers and service/save layout contracts."""
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from clinic_art import apply_clinic, clinic_resources, clinic_tile
from maps import encode_layout


class ClinicArt(unittest.TestCase):
    def test_native_exit_layers_and_capacity_keep_actors_and_warp_visible(self):
        graphics,records,attributes,palettes=clinic_resources(ROOT)
        self.assertLessEqual(len(graphics)//32,504)
        self.assertEqual(len(records),81*16)
        self.assertEqual(len(palettes),512)
        flags=struct.unpack('<81H',attributes)
        self.assertEqual(flags[1],0x1065)
        self.assertTrue(all(flag>>12==1 for flag in flags))
        for index in range(1,5):
            self.assertEqual(len({palettes[bank*32+index*2:bank*32+index*2+2]
                                  for bank in range(6,10)}),1)
        for record,bank in ((2,6),(6,7),(8,8),(7,9)):
            foreground=struct.unpack_from('<8H',records,record*16)[4:]
            self.assertEqual({value>>12 for value in foreground},{bank})

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
                self.assertTrue(512<=after&0x3ff<593)
            self.assertEqual(clinic_tile(plan,6,12),513)
            self.assertEqual(clinic_tile(plan,2,3),518) # storage terminal
            self.assertEqual(clinic_tile(plan,10,2),519) # team notes
            for npc in plan['npcs']:
                self.assertEqual(clinic_tile(plan,npc['x'],npc['y']),514)
            graphics=(engine/'src/data/tilesets/graphics.h').read_text()
            self.assertIn('gTilesetTiles_SFSouthParkClinic',graphics)
            self.assertIn('secondary/sf_south_park_clinic/tiles.png',graphics)
            self.assertTrue(all((engine/file).exists() for file in changed))


if __name__=='__main__':unittest.main()
