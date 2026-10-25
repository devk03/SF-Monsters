"""Independent RGB555 reconstruction protects real art across profile boundaries."""
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from generate_world import generate
from world_tiles import compile_kit
from world_trail_ground import WORN_IDS
from world_seams import make_atlases,margin_points


def quadrant(word,tiles,palettes):
    raw=tiles[word & 1023]
    colors=struct.unpack('<16H',palettes[word >> 12])
    result=[]
    for y in range(8):
        for x in range(8):
            sx=7-x if word & 0x400 else x
            sy=7-y if word & 0x800 else y
            index=raw[sy*8+sx]
            result.append(colors[index] if index else None)
    return result


class SeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        cls.kits={p:compile_kit(profile=p) for p in {m.get('tile_profile','residential') for m in cls.plans}}
        fixture=json.loads((ROOT/'tests/fixtures/world-general-reservations.json').read_text())
        cls.reserved=set(fixture['reserved_tiles'])
        cls.banks=set(fixture['reserved_banks'])
        cls.locks={int(k):{int(i):v for i,v in entries.items()} for k,entries in fixture['palette_locks'].items()}
        cls.primary_banks={int(k):set(v) for k,v in fixture['primary_banks'].items()}
        cls.atlases=make_atlases(cls.plans,cls.kits,cls.reserved,cls.banks,cls.locks,cls.primary_banks)

    def test_every_foreign_margin_quad_keeps_exact_colors_alpha_handedness_and_behavior(self):
        native={p['native_id']:p for p in self.plans}
        for atlas in self.atlases:
            plan=next(p for p in self.plans if p['world_id']==atlas['world_id'])
            host=self.kits[plan['tile_profile']]
            actual_tiles={512+i:t for i,t in enumerate(host['tiles'])}
            actual_tiles.update(zip(atlas['tile_slots'],atlas['tiles']))
            actual_palettes=dict(host['palettes'],**{})
            actual_palettes.update(atlas['palettes'])
            for neighbor in atlas['neighbors']:
                foreign=self.kits[native[neighbor['native_id']]['tile_profile']]
                source_tiles={512+i:t for i,t in enumerate(foreign['tiles'])}
                source_tiles.update(foreign.get('primary_tiles',{}))
                for identifier in neighbor['used']:
                    if identifier<512:continue
                    mapped=neighbor['mapping'][identifier-512]
                    if mapped not in atlas['record_ids']:
                        words=host['records'][mapped-512];attribute=host['attributes'][mapped-512]
                    else:
                        index=atlas['record_ids'].index(mapped)
                        words=atlas['records'][index];attribute=atlas['attributes'][index]
                    expected=foreign['records'][identifier-512]
                    self.assertEqual(attribute,foreign['attributes'][identifier-512])
                    for a,b in zip(words,expected):
                        if b&1023<512 and b>>12<6:
                            self.assertEqual(a,b,'Native General grass words remain exact')
                            continue
                        self.assertEqual(quadrant(a,actual_tiles,actual_palettes),
                                         quadrant(b,source_tiles,foreign['palettes']),
                                         (atlas['world_id'],neighbor['native_id'],identifier))

    def test_extension_allocations_cannot_overwrite_terrain_animation_doors_or_ui_palettes(self):
        for atlas in self.atlases:
            self.assertFalse(set(atlas['tile_slots']) & self.reserved)
            self.assertFalse(set(atlas['palettes']) & (set(atlas['reserved_palettes'])|{14,15}))
            if 3 in atlas['palettes']:
                colors=struct.unpack('<16H',atlas['palettes'][3])
                for index,color in self.locks[3].items():self.assertEqual(colors[index],color)
            self.assertTrue(all(0<i<1024 for i in atlas['record_ids']))
            self.assertFalse(set(atlas['record_ids']) & set(self.primary_banks))
            self.assertEqual(len(set(atlas['tile_slots'])),len(atlas['tiles']))

    def test_exhausted_graphics_and_palette_capacity_fail_instead_of_substituting_art(self):
        with self.assertRaisesRegex(ValueError,'graphics slots|overwrites native primary graphics'):
            make_atlases(self.plans,self.kits,set(range(1024)),self.banks)
        with self.assertRaisesRegex(ValueError,'palette colors'):
            make_atlases(self.plans,self.kits,self.reserved,set(range(16)))

    def test_native_east_margin_has_eight_columns_other_sides_have_seven(self):
        p={'rows':['.'*32]*24}
        self.assertEqual(set(margin_points(p,'left')),{(x,y) for x in range(25,32) for y in range(24)})
        self.assertEqual(set(margin_points(p,'right')),{(x,y) for x in range(8) for y in range(24)})
        self.assertEqual(len(margin_points(p,'up')),32*7)
        self.assertEqual(len(margin_points(p,'down')),32*7)

    def test_small_connector_imports_only_native_clipped_large_town_window(self):
        town={'rows':['.'*96]*64}
        route={'rows':['.'*32]*24}
        # fieldmap.c: x=offset+7=-25, x2=25; source padded width=47.
        # Thus horizontal edges copy town columns25..71, not all96columns.
        for direction,ys in [('up',range(57,64)),('down',range(7))]:
            self.assertEqual(set(margin_points(town,direction,route,-32)),
                             {(x,y) for x in range(25,72) for y in ys})
        # Vertical copies use the source padded height38, starting town row13.
        for direction,xs in [('left',range(89,96)),('right',range(8))]:
            self.assertEqual(set(margin_points(town,direction,route,-20)),
                             {(x,y) for x in xs for y in range(13,51)})


class SharedAllocationTests(unittest.TestCase):
    def fixture(self):
        palette=struct.pack('<16H',*range(16))
        def kit(pixel,records=1):
            return {'tiles':[bytes([pixel])*64], 'primary_tiles':{},
                    'records':[[0x6200]*8 for _ in range(records)],
                    'attributes':[0x1000]*records,'palettes':{6:palette}}
        def plan(name,profile):
            return {'world_id':name,'native_id':name,'tile_profile':profile,
                    'rows':['.'*8]*8,'legend':{'.':(512,False)},'connections':[]}
        a,b=plan('A','a'),plan('B','b')
        a['connections']=[{'map':'B','direction':'right','offset':0}]
        return [a,b],{'a':kit(1,512),'b':kit(2)}

    def test_full_host_records_and_primary_graphics_preserve_foreign_pixels(self):
        from world_shared_primary import REQUIRED_METATILES
        plans,kits=self.fixture()
        atlas=make_atlases(plans,kits,set(range(512)),{0,1,2,3,4,5})[0]
        identifier=atlas['neighbors'][0]['mapping'][0]
        self.assertLess(identifier,512,'Foreign record spills into unused primary metatile space')
        self.assertNotIn(identifier,REQUIRED_METATILES)
        self.assertTrue(all(512<s<1024 for s in atlas['tile_slots']),
                        'Only unused secondary graphics are available in this fixture')
        words=atlas['records'][atlas['record_ids'].index(identifier)]
        loaded={512:kits['a']['tiles'][0],**dict(zip(atlas['tile_slots'],atlas['tiles']))}
        for word in words:
            self.assertEqual(quadrant(word,loaded,kits['a']['palettes']),[2]*64)
        # The authored host graphic is retained while the margin is imported.
        self.assertEqual(quadrant(0x6200,loaded,kits['a']['palettes']),[1]*64)
        with self.assertRaisesRegex(ValueError,'graphics slots'):
            make_atlases(plans,kits,set(range(1024)),{0,1,2,3,4,5})

    def test_same_profile_margin_loads_own_primary_art_absent_from_host_cells(self):
        plans,kits=self.fixture();plans[1]['tile_profile']='a'
        kits['a']['records'][1]=[0x6012]*8
        kits['a']['primary_tiles']={18:bytes([3])*64}
        plans[1]['legend']={'.':(513,False)}
        atlases=make_atlases(plans,kits,set(range(16)),{0,1,2,3,4,5})
        self.assertEqual(atlases[0]['own_primary_slots'],[18])
        self.assertEqual(atlases[1]['own_primary_slots'],[18], 'Warp-only entry still loads its own art')
        self.assertEqual(atlases[0]['tiles'][0],bytes([3])*64)
        with self.assertRaisesRegex(ValueError,'overwrites native'):
            make_atlases(plans,kits,{18},{0,1,2,3,4,5})


if __name__=='__main__':unittest.main()
