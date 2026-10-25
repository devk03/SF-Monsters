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
    def test_large_urban_blocks_do_not_leave_ten_by_ten_empty_lawns(self):
        manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
        for plan in generate(manifest):
            if plan['world_id'] not in URBAN:continue
            kit=compile_kit(profile=plan['tile_profile'])
            grass=chr(0x100+kit['catalog']['grass']['tiles'][0][0]-512)
            rows=plan['rows']
            for y in range(len(rows)-9):
                for x in range(len(rows[0])-9):
                    self.assertFalse(all(row[x:x+10]==grass*10 for row in rows[y:y+10]),
                                     (plan['world_id'],x,y,'unprogrammed10x10lawn'))

    def test_grass_references_original_general_terrain_and_palette(self):
        for profile in ('neighborhood','mixed_use','industrial','civic','culture','stadium','nature'):
            kit=compile_kit(profile=profile)
            grass=kit['catalog']['grass']['tiles'][0][0]
            self.assertEqual(kit['records'][grass-512][:4],[0x2002,0x2003,0x2003,0x2002])
            self.assertFalse(kit['catalog']['grass']['blocked'])
            for card in kit['catalog'].values():
                for row in card['tiles']:
                    for tile in row:
                        native=[word for word in kit['records'][tile-512] if word&1023<512 and word>>12<6]
                        self.assertTrue(all(word in (0x2002,0x2003) for word in native))
                        for word in kit['records'][tile-512]:
                            if word&1023<512 and word>>12>=6:
                                self.assertIn(word&1023,kit['primary_tiles'])

    def test_attachment_variants_change_only_real_party_wall_pixels(self):
        from world_rich_facades import facade
        from world_architecture import FORMS
        for name in FORMS:
            w,h,isolated=facade(name)
            _,_,middle=facade(name,())
            _,_,left=facade(name,('left',))
            _,_,right=facade(name,('right',))
            with self.subTest(form=name):
                self.assertEqual(len({isolated,middle,left,right}),4)
                for y in range(h):
                    for x in range(2,w-2):
                        at=y*w+x
                        self.assertEqual((middle[at],left[at],right[at]),(isolated[at],)*3)
                self.assertEqual(middle[62*w:],isolated[62*w:],'foundation remains continuous')

    def test_paint_changes_facades_without_recoloring_paving_or_replacing_pixels(self):
        for profile in ('neighborhood','mixed_use','culture','stadium','industrial','civic'):
            kit=compile_kit(profile=profile)
            for name,card in kit['catalog'].items():
                if '__' not in name:continue
                base=kit['catalog'][name.split('__')[0]]
                for row,oldrow in zip(card['tiles'],base['tiles']):
                    for tile,old in zip(row,oldrow):
                        newwords=kit['records'][tile-512];oldwords=kit['records'][old-512]
                        self.assertEqual(newwords[:4],oldwords[:4],(profile,name,'paving'))
                        self.assertEqual([w&0xfff for w in newwords],[w&0xfff for w in oldwords])
                        scheme=name.split('__')[1]
                        wanted=struct.unpack('<16H',paint_palette(kit['palettes'][6],scheme))
                        for newword,oldword in zip(newwords[4:],oldwords[4:]):
                            slot=oldword&1023
                            pixels=kit['tiles'][slot-512] if slot>=512 else kit['primary_tiles'][slot]
                            colors=struct.unpack('<16H',kit['palettes'][newword>>12])
                            self.assertEqual([colors[p] if p else None for p in pixels],
                                             [wanted[p] if p else None for p in pixels],(profile,name,slot))


    def test_new_fronts_have_green_and_blue_walls_not_just_different_trim(self):
        palette=compile_kit(profile='mixed_use')['palettes'][6]
        for name,width,_,pixels in fronts('mixed_use'):
            for scheme,dominant in (('sage',1),('slate',2)):
                colors=struct.unpack('<16H',paint_palette(palette,scheme))
                visible=[colors[p] for p in pixels if p]
                colored=sum(((c>>(dominant*5))&31)>max((c>>(i*5))&31
                    for i in range(3) if i!=dominant) for c in visible)
                self.assertGreater(colored,len(visible)//4,(name,scheme,'painted wall area'))

    def test_each_urban_district_draws_multiple_forms_and_the_new_paints(self):
        manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
        kits={}
        for plan in generate(manifest):
            if plan['world_id'] not in URBAN:continue
            profile=plan['tile_profile']
            if profile not in kits:kits[profile]=compile_kit(profile=profile)
            catalog=kits[profile]['catalog']
            blocks=[b for b in plan['town_blocks'] if 'closed_edges' in catalog[b['style']]]
            forms={catalog[b['style']]['architecture_type'] for b in blocks}
            with self.subTest(area=plan['world_id']):
                self.assertGreaterEqual(len(forms),8)
                self.assertLessEqual(len(kits[profile]['tiles']),512)
                self.assertLessEqual(len(kits[profile]['records']),512)
                if profile in ('industrial','civic'):
                    self.assertTrue(any('__sage' in b['style'] for b in blocks))
                else:
                    paints={b['style'].split('__')[1] if '__' in b['style'] else 'warm' for b in blocks}
                    self.assertEqual(paints,{'warm','sage','slate'})
                    for block in blocks:
                        self.assertFalse(any(other is not block and other['style']==block['style']
                            and other['y']==block['y'] and other['x']+other['width']==block['x'] for other in blocks),
                            'Identical adjoining facade stamps')

    def test_authored_parcels_keep_clear_frontage_and_readable_notices(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        for identifier,left,right,rows in [('dogpatch',50,58,(21,22,29,30)),('mission',42,56,(21,22,29,30)),('north_beach',72,81,(21,22))]:
            p=next(p for p in plans if p['world_id']==identifier)
            self.assertIn('authored_parcel',p)
            for y in rows:
                for x in range(left,right+1):
                    self.assertFalse(p['legend'][p['rows'][y][x]][1],(identifier,x,y,'frontage approach blocked'))
            notice=p['parcel_notices'][0];x,y=notice['object'];sx,sy=notice['standing']
            self.assertTrue(p['legend'][p['rows'][y][x]][1])
            self.assertFalse(p['legend'][p['rows'][sy][sx]][1])
            self.assertTrue(any(e['script']==notice['script'] and (e['x'],e['y'])==(x,y) for e in p['bg_events']))

    def test_district_frontage_mixes_express_industry_downtown_and_homes(self):
        from collections import Counter
        from world_architecture import FORMS
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        for identifier,preferred,minimum in [('dogpatch',{'workshop'},.2),
                ('financial_district',{'deco','flats'},.35),
                ('outer_sunset',{'walkup','duplex','gable'},.5)]:
            p=next(p for p in plans if p['world_id']==identifier)
            catalog=compile_kit(profile=p['tile_profile'])['catalog']
            counts=Counter(catalog[b['style']].get('architecture_type') for b in p['town_blocks']
                           if catalog[b['style']].get('architecture_type') in FORMS)
            self.assertGreater(sum(counts[n] for n in preferred)/sum(counts.values()),minimum,identifier)

    def test_every_urban_district_has_two_usable_planted_cut_throughs(self):
        plans=generate(json.loads((ROOT/'romhack/world/world.json').read_text()))
        for p in plans:
            if p['world_id'] not in URBAN:continue
            self.assertEqual(len(p['pedestrian_courts']),2,p['world_id'])
            for court,notice in zip(p['pedestrian_courts'],p['court_notices']):
                x,top=court['x'],court['top']
                for y in range(top-3,top+6):
                    self.assertFalse(p['legend'][p['rows'][y][x+1]][1],(p['world_id'],x+1,y))
                ox,oy=notice['object']
                self.assertTrue(p['legend'][p['rows'][oy][ox]][1])
                self.assertTrue(any(e['script']==notice['script'] for e in p['bg_events']))


if __name__=='__main__':unittest.main()
