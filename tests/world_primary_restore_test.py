"""A destination must recover its native art after a previous scene overwrites it."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_primary_restore import restoration,visible_native_slots,destination_restoration,borrowed_restoration,relocate_owned_records,relocate_atlas,relocate_visible_borrows
import struct


class PrimaryRestorationTests(unittest.TestCase):
    def test_native_cliff_visible_on_route_relocates_both_maps(self):
        # The route sees a borrowed cliff only through the neighboring map's
        # edge. Both scenes own an SF tile in that slot and must preserve it.
        legend={'.':[512,False,3], 'n':[2,True,3]}
        route={'world_id':'route','native_id':'ROUTE','tile_profile':'ridge',
               'rows':['........']*8,'legend':legend,'border_tile':1,
               'connections':[{'map':'TOWN','direction':'right','offset':0}]}
        town={'world_id':'town','native_id':'TOWN','tile_profile':'ridge',
              'rows':['n.......']+['........']*7,'legend':legend,'border_tile':1,
              'connections':[{'map':'ROUTE','direction':'left','offset':0}]}
        pixels=bytes([7])*64
        kit={'records':[[0x604c]*8], 'attributes':[0x1000]}
        def atlas(name):
            return {'world_id':name,'records':[],'record_ids':[],'attributes':[],
                    'tiles':[pixels],'tile_slots':[76],'own_primary_slots':[76]}
        records=b''.join(struct.pack('<8H',*([slot]*8)) for slot in (0,20,76))
        original=[atlas('route'),atlas('town')]
        revised,demands=relocate_visible_borrows([route,town],{'ridge':kit},original,records,{76})
        self.assertEqual(demands,{'route':[76],'town':[76]})
        for a in revised:
            self.assertNotIn(76,a['tile_slots'])
            self.assertEqual(a['records'][0][0]&0xfc00,0x6000)
            self.assertEqual(a['tiles'][0],pixels)
        self.assertEqual(original[0]['tile_slots'],[76])
        with self.assertRaisesRegex(ValueError,'no seam atlas'):
            relocate_visible_borrows([route,town],{'ridge':kit},original[:1],records,{76})

    def test_atlas_relocates_shared_tile_and_adds_own_override(self):
        pixels=bytes([3])*64
        kit={'records':[[0x604c]*8], 'attributes':[0x1000]}
        atlas={'records':[[0x784c]*8], 'record_ids':[513], 'attributes':[0x1000],
               'tiles':[pixels], 'tile_slots':[76], 'own_primary_slots':[76]}
        result,mapping=relocate_atlas(atlas,kit,{512},{76})
        slot=mapping[76]
        self.assertEqual(result['record_ids'],[513,512])
        self.assertEqual(result['records'][0][0],0x7800|slot)
        self.assertEqual(result['records'][1][0],0x6000|slot)
        self.assertEqual(dict(zip(result['tile_slots'],result['tiles']))[slot],pixels)
        self.assertEqual(atlas['record_ids'],[513])

    def test_foreign_mapping_to_unused_host_record_is_also_overridden(self):
        pixels=bytes([3])*64
        kit={'records':[[0x604c]*8], 'attributes':[0x1000]}
        atlas={'records':[], 'record_ids':[], 'attributes':[],
               'tiles':[pixels], 'tile_slots':[76], 'own_primary_slots':[76],
               'neighbors':[{'used':[512],'mapping':[512]}]}
        result,mapping=relocate_atlas(atlas,kit,set(),{76})
        self.assertEqual(result['record_ids'],[512])
        self.assertEqual(result['records'][0][0],0x6000|mapping[76])

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

    def test_shared_owned_and_foreign_references_move_together(self):
        # A foreign seam may reuse the host's tile with a different palette
        # and flip; both records must address the same relocated pixels.
        records={('own',512):[0x604c]*8,('foreign',0):[0x784c]*8}
        pixels=bytes([3])*64
        result=relocate_owned_records(records,{76:pixels},{76})
        slot=result['mapping'][76]
        self.assertEqual(result['graphics'][slot],pixels)
        self.assertEqual(result['records'][('own',512)][0],0x6000|slot)
        self.assertEqual(result['records'][('foreign',0)][0],0x7800|slot)

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

    def test_composite_sand_reserves_native_graphics_even_without_sand_map_cells(self):
        plan={'rows':['.'], 'legend':{'.':[1,False,3]}, 'tile_profile':'coast',
              'border_tile':1, 'connections':None}
        records=b''.join(struct.pack('<8H',*([264 if i==0x124 else 2]*8))
                         for i in range(0x125))
        slots=visible_native_slots(plan,{}, {'coast':{'uses_native_sand':True}},records)
        self.assertIn(264,slots)

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
