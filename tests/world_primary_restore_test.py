"""A destination must recover its native art after a previous scene overwrites it."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_primary_restore import restoration,visible_native_slots,destination_restoration,borrowed_restoration,relocate_owned_records
import struct


class PrimaryRestorationTests(unittest.TestCase):
    def test_conflicting_owned_tile_moves_without_changing_native_or_flip(self):
        owned={76:bytes([7])*64}
        records={512:[0x604c,0x644c,0x204c,0x6200,0,0,0,0]}
        result=relocate_owned_records(records,owned,{76},{513})
        self.assertEqual(result['mapping'],{76:514})
        self.assertEqual(result['graphics'][514],owned[76])
        self.assertEqual(result['records'][512][:4],[0x6202,0x6602,0x204c,0x6200])
        self.assertEqual(records[512][0],0x604c)
        with self.assertRaisesRegex(ValueError,'Missing owned'):
            relocate_owned_records(records,{}, {76})
        with self.assertRaisesRegex(ValueError,'Insufficient'):
            relocate_owned_records(records,owned,{76},set(range(512,1024)))

    def test_borrowed_plan_rejects_untracked_older_map_writes(self):
        original={7:bytes([2])*64,11:bytes([3])*64}
        plan=borrowed_restoration({7,11},{20},original,{7,30},{7})
        self.assertEqual([slot for slot,_ in plan],[7])
        with self.assertRaisesRegex(ValueError,'outside the borrowed set'):
            borrowed_restoration({7,11},{20},original,{7,11},{7})
        with self.assertRaisesRegex(ValueError,'collide'):
            borrowed_restoration({7,11},{11},original,{7},{7})
        with self.assertRaisesRegex(ValueError,'range'):
            borrowed_restoration({7},{20},original,{512},{7})

    def test_restore_does_not_assume_only_previous_scene_can_be_dirty(self):
        original={7:bytes([2])*64,11:bytes([3])*64}
        scene={7:bytes([9])*64,11:original[11]}  # Map A overwrote slot7.
        scene[11]=bytes([8])*64  # Map B wrote only slot11.
        scene.update(destination_restoration({7}, {20}, original))
        self.assertEqual(scene[7],original[7])  # Map C needs A's old slot.
        with self.assertRaisesRegex(ValueError,'Missing'):
            destination_restoration({7,11},{20},{7:original[7]})

    def test_visible_native_slots_include_borders_and_clipped_neighbors(self):
        legend={'.':[1,False,3], 'b':[3,True,3], 'v':[4,False,3], 'x':[5,False,3], 's':[512,True,3]}
        neighbor={'rows':['v'+'.'*19]+['.'*20 for _ in range(10)]+['x'+'.'*19],
                  'legend':legend,'tile_profile':'forest'}
        plan={'rows':['s'+'.'*19,'.'*20],'legend':legend,'tile_profile':'town',
              'border_metatiles':[3], 'connections':[{'map':'neighbor','direction':'right','offset':0}]}
        records=b''.join(struct.pack('<8H',*([i*10]*8)) for i in range(6))
        kits={'town':{'records':[[0x2011]*8]},'forest':{'uses_native_grass':True}}
        slots=visible_native_slots(plan,{'neighbor':neighbor},kits,records)
        self.assertEqual(slots,{10,17,20,30,40})
        plan['connections']=None
        self.assertEqual(visible_native_slots(plan,{}, kits,records),{10,17,20,30})

    def test_transition_recovers_only_needed_native_tiles(self):
        original={7:bytes([2])*64, 11:bytes([3])*64, 15:bytes([4])*64}
        scene={7:bytes([9])*64,11:bytes([8])*64,15:original[15]}
        plan=restoration({7,11},{7,15},{20},original)
        self.assertEqual([slot for slot,_ in plan],[7])
        scene.update(plan)
        self.assertEqual(scene[7],original[7])
        self.assertEqual(scene[15],original[15])
        self.assertEqual(scene[11],bytes([8])*64)

    def test_rejects_collision_and_missing_native_data(self):
        with self.assertRaisesRegex(ValueError,'collide'):
            restoration({7},{7},{7},{7:bytes(64)})
        with self.assertRaisesRegex(ValueError,'Missing'):
            restoration({7},{7},{20},{})
        with self.assertRaises(ValueError):
            restoration({512},{7},set(),{})


if __name__=='__main__':unittest.main()
