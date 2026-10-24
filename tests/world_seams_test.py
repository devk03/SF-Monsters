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
        cls.reserved=set(range(16))|{20,166,211}|set(range(432,512))
        cls.banks={1,2,4,5}
        cls.locks={3:{1:0x7fff,2:0x6b5a,3:0x5ef7,4:0x5294,13:0x2d70}}
        cls.primary_banks={1:{0,2},11:{0,1,5},179:{0,4},368:{0,4}}
        # Pinned General woodland/tall-grass references now occur on the maps.
        cls.primary_banks.update({tile:{0,2} for tile in (4,13,0x1d4,0x1d5,0x1dc,0x1dd,0x1e4,0x1e5)})
        cls.primary_banks.update({tile:{0,2} for tile in WORN_IDS})
        cls.reserved.update({249,250,265,266,281,282,297,298})
        cls.reserved.update({25,41,204,205,384,385,400,401,416,417,418,419,420,421})
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
                for identifier in neighbor['used']:
                    if identifier<512:continue
                    mapped=neighbor['mapping'][identifier-512]
                    if mapped<atlas['first']:
                        words=host['records'][mapped-512];attribute=host['attributes'][mapped-512]
                    else:
                        words=atlas['records'][mapped-atlas['first']];attribute=atlas['attributes'][mapped-atlas['first']]
                    expected=foreign['records'][identifier-512]
                    self.assertEqual(attribute,foreign['attributes'][identifier-512])
                    for a,b in zip(words,expected):
                        if b&1023<512:
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
            self.assertLessEqual(atlas['first']+len(atlas['records']),1024)
            self.assertEqual(len(set(atlas['tile_slots'])),len(atlas['tiles']))

    def test_exhausted_graphics_and_palette_capacity_fail_instead_of_substituting_art(self):
        with self.assertRaisesRegex(ValueError,'graphics slots'):
            make_atlases(self.plans,self.kits,set(range(512)),self.banks)
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


if __name__=='__main__':unittest.main()
