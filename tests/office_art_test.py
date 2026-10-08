"""Native office capacity, script compatibility and authored room coverage."""
from pathlib import Path
import json
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from office_art import office_resources, office_tile


class OfficeArt(unittest.TestCase):
    def test_native_gate_floor_exit_and_draw_layers_keep_their_game_contracts(self):
        graphics,records,attributes,palettes=office_resources(ROOT)
        flags=struct.unpack('<81H',attributes)
        self.assertEqual(flags[2],0x1000) # script opens metatile 0x202
        self.assertEqual(flags[1],0x1065) # native south-arrow warp
        self.assertTrue(all(flag>>12==1 for flag in flags))
        self.assertLessEqual(len(graphics)//32,504)
        self.assertEqual(len(records),81*16)
        self.assertEqual(len(palettes),512)
        bank=lambda record:{value>>12 for value in struct.unpack_from('<8H',records,record*16)[4:]}
        self.assertEqual(bank(2),{6})
        self.assertEqual(bank(22),{7}) # workstation
        self.assertEqual(bank(30),{8}) # vegetation
        self.assertEqual(bank(75),{9}) # relay
        for index in range(1,5):
            colors=[palettes[bank*32+index*2:bank*32+index*2+2] for bank in range(6,10)]
            self.assertEqual(len(set(colors)),1)

    def test_every_current_cell_has_original_art_without_losing_events_or_warps(self):
        plan=json.loads((ROOT/'romhack/content/cognition.json').read_text())
        tiles=[office_tile(plan,x,y) for y,row in enumerate(plan['rows']) for x in range(len(row))]
        self.assertTrue(all(512<=tile<593 for tile in tiles))
        self.assertEqual(office_tile(plan,8,21),513)
        self.assertEqual(office_tile(plan,8,8),516)
        self.assertEqual(office_tile(plan,3,12),587)
        self.assertEqual(office_tile(plan,13,12),588)
        self.assertEqual(office_tile(plan,1,6),540) # incident terminal lower-left
        self.assertEqual(office_tile(plan,5,19),591) # team whiteboard
        self.assertEqual(office_tile(plan,1,15),582) # coffee counter
        for x,y in ((8,3),(8,7),(8,16),(4,10),(12,10)):
            self.assertEqual(office_tile(plan,x,y),515 if plan['rows'][y][x]=='r' else 514)


if __name__=='__main__':unittest.main()
