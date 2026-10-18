"""User-facing street variety and safe native paint selection."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from world_tiles import compile_kit
from generate_world import generate
from world_towns import URBAN
from world_architecture import fronts,paint_palette
import struct


class BuildingVarietyTests(unittest.TestCase):
    def test_paint_changes_facades_without_recoloring_paving_or_replacing_pixels(self):
        for profile in ('neighborhood','mixed_use','culture','stadium'):
            kit=compile_kit(profile=profile)
            for name,card in kit['catalog'].items():
                if '__' not in name:continue
                base=kit['catalog'][name.split('__')[0]]
                for row,oldrow in zip(card['tiles'],base['tiles']):
                    for tile,old in zip(row,oldrow):
                        newwords=kit['records'][tile-512];oldwords=kit['records'][old-512]
                        self.assertEqual(newwords[:4],oldwords[:4],(profile,name,'paving'))
                        self.assertEqual([w&0xfff for w in newwords],[w&0xfff for w in oldwords])
                        banks={w>>12 for w in newwords[4:]};self.assertEqual(len(banks),1)
                        bank=banks.pop();self.assertIn(bank,(9,11,12))
                        self.assertEqual(kit['palettes'][bank][2:10],kit['palettes'][6][2:10], 'roof and glass')
                        self.assertNotEqual(kit['palettes'][bank],kit['palettes'][6])

    def test_new_fronts_have_green_and_blue_walls_not_just_different_trim(self):
        palette=compile_kit(profile='mixed_use')['palettes'][6]
        for name,width,_,pixels in fronts('mixed_use'):
            wall=pixels[8*width+3]
            for scheme,dominant in (('sage',1),('slate',2)):
                color=struct.unpack('<16H',paint_palette(palette,scheme))[wall]
                rgb=[(color>>shift)&31 for shift in (0,5,10)]
                self.assertGreater(rgb[dominant],max(v for i,v in enumerate(rgb) if i!=dominant),(name,scheme))

    def test_each_urban_district_draws_multiple_forms_and_the_new_paints(self):
        manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
        kits={}
        for plan in generate(manifest):
            if plan['world_id'] not in URBAN:continue
            profile=plan['tile_profile']
            if profile not in kits:kits[profile]=compile_kit(profile=profile)
            catalog=kits[profile]['catalog']
            blocks=[b for b in plan['town_blocks'] if 'closed_edges' in catalog[b['style']]]
            forms={b['style'].split('__')[0].removesuffix('_lr').removesuffix('_l').removesuffix('_r') for b in blocks}
            with self.subTest(area=plan['world_id']):
                self.assertGreaterEqual(len(forms),4)
                if profile not in ('industrial','civic'):
                    paints={b['style'].split('__')[1] if '__' in b['style'] else 'warm' for b in blocks}
                    self.assertEqual(paints,{'warm','sage','slate'})
                    for block in blocks:
                        self.assertFalse(any(other is not block and other['style']==block['style']
                            and other['y']==block['y'] and other['x']+other['width']==block['x'] for other in blocks),
                            'Identical adjoining facade stamps')


if __name__=='__main__':unittest.main()
