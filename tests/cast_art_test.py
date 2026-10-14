"""Protect frame encoding and coherent palette use for the shipped SF cast."""
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from cast_art import apply_cast, source_cells, GROUPS, registered_groups, verified_cast, catalog


class NativeCast(unittest.TestCase):
    def test_karpathy_shares_palette_without_changing_roons_cartridge_pixels(self):
        import hashlib
        directory = ROOT/'assets/characters/sunset-cast'
        source = (directory/'roon/quantization-palette.gbapal').read_bytes()
        shared = (directory/'cast.gbapal').read_bytes()
        self.assertEqual(shared[:30], source[:30])
        self.assertEqual(struct.unpack_from('<H', shared, 30)[0], 31 | 27 << 5 | 23 << 10)
        roon = Image.open(directory/'roon/walk.png')
        self.assertNotIn(15, roon.tobytes())
        self.assertEqual(hashlib.sha256((directory/'roon/walk.4bpp').read_bytes()).hexdigest(),
                         'e5dc40733671ee6bb4f7198253e6cf812f8eeb5fdd8d4e16a8585497592d91fc')
        karpathy = Image.open(directory/'karpathy/walk.png')
        self.assertIn(15, karpathy.tobytes())
        self.assertNotEqual(karpathy.tobytes(), roon.tobytes())

    def test_stock_slot_replacement_cannot_claim_another_map_or_script(self):
        parent = ROOT/'.tools/cast-ownership-tests'; parent.mkdir(exist_ok=True)
        folder = Path(tempfile.mkdtemp(prefix='case-', dir=parent))
        asset = folder/'assets/characters/sunset-cast'; asset.mkdir(parents=True)
        entry = next(e for e in catalog(ROOT, 'assets/characters/sunset-cast')
                     if e['slug']=='karpathy')
        for change in ({'map':'services.json'}, {'script':'SF_AnotherPerson'},
                       {'reserved_slot':'OBJ_EVENT_GFX_MAN_1'}):
            (asset/'cast.json').write_text(json.dumps({'characters':[dict(entry, **change)]}))
            with self.assertRaisesRegex(ValueError, 'reviewed authored'):
                catalog(folder, 'assets/characters/sunset-cast')

    def test_replaced_stock_graphics_cannot_recolor_a_second_authored_npc(self):
        import shutil
        parent = ROOT/'.tools/cast-ownership-tests'; parent.mkdir(exist_ok=True)
        folder = Path(tempfile.mkdtemp(prefix='case-', dir=parent))
        (folder/'assets').symlink_to(ROOT/'assets', target_is_directory=True)
        content = folder/'romhack/content'
        shutil.copytree(ROOT/'romhack/content', content)
        path = content/'services.json'; plan = json.loads(path.read_text())
        plan['npcs'].append({'id':99,'x':1,'y':1,'graphics':'OBJ_EVENT_GFX_SCIENTIST_1',
                              'script':'SF_UnrelatedScientist'})
        path.write_text(json.dumps(plan))
        with self.assertRaisesRegex(ValueError, 'another authored owner'):
            registered_groups(folder)

    def test_roons_corrected_west_steps_alternate_and_wander_area_is_clear(self):
        directory = ROOT/'assets/characters/sunset-cast/roon'
        image = Image.open(directory/'walk.png')
        steps = [image.crop((index*16,0,index*16+16,32)).tobytes() for index in (7,8)]
        feet = [[x for x in range(16) if pose[29*16+x]] for pose in steps]
        self.assertTrue(feet[0] and feet[1])
        self.assertLess(max(feet[0]), 8)
        self.assertGreaterEqual(min(feet[1]), 8)
        plan = json.loads((ROOT/'romhack/content/sunset.json').read_text())
        roon = next(npc for npc in plan['npcs'] if npc['script']=='SF_Roon')
        self.assertEqual((roon['movement'],roon['range_x'],roon['range_y']),
                         ('MOVEMENT_TYPE_WANDER_AROUND',1,1))
        occupied = {(npc['x'],npc['y']) for npc in plan['npcs'] if npc is not roon}
        occupied |= {(warp['x'],warp['y']) for warp in plan['warp_events']}
        for y in range(roon['y']-1,roon['y']+2):
            for x in range(roon['x']-1,roon['x']+2):
                self.assertFalse(plan['legend'][plan['rows'][y][x]][1])
                self.assertNotIn((x,y),occupied)

    def test_registered_people_have_distinct_native_pose_cycles_and_group_palettes(self):
        records = []
        for asset, symbol, tag, value in GROUPS:
            directory = ROOT / asset
            metadata = json.loads((directory/'conversion.json').read_text())
            records.extend((directory,entry) for entry in metadata['characters'])
        identities = []
        for directory,entry in records:
            native_colors = struct.unpack('<16H', (directory/'cast.gbapal').read_bytes())
            path = directory/entry['slug']
            image = Image.open(path/'walk.png')
            self.assertEqual(image.size, (144, 32))
            self.assertEqual(image.info['transparency'], 0)
            palette = image.getpalette()[:48]
            encoded_colors = tuple(sum(round(palette[i*3+c]*31/255) << (5*c)
                                       for c in range(3)) for i in range(16))
            self.assertEqual(encoded_colors, native_colors)
            frames = [image.crop((i*16,0,i*16+16,32)).tobytes() for i in range(9)]
            for indices in ((0,3,4), (1,5,6), (2,7,8)):
                self.assertEqual(len({frames[i] for i in indices}), 3)
            for frame in frames:
                self.assertTrue(any(frame)); self.assertLessEqual(max(frame), 15)
                self.assertFalse(any(frame[30*16:]))
            raw = (path/'walk.4bpp').read_bytes()
            # Independent GBA contract: each frame is eight 8x8 tiles, with
            # the left pixel in the lower nibble of each packed byte.
            unpacked = []
            for frame_index in range(9):
                decoded = bytearray(512)
                for ty in range(4):
                    for tx in range(2):
                        tile = raw[frame_index*256+(ty*2+tx)*32:][:32]
                        for y in range(8):
                            for x in range(8):
                                decoded[(ty*8+y)*16+tx*8+x] = (tile[y*4+x//2] >> (4*(x%2))) & 15
                unpacked.append(bytes(decoded))
            self.assertEqual(unpacked, frames)
            identities.append(frames[0])
        self.assertEqual(len(set(identities)), len(records))

    def test_a_new_cast_group_cannot_replace_an_existing_native_graphics_slot(self):
        from copy import deepcopy
        from unittest.mock import patch
        prepared = {asset:deepcopy(verified_cast(ROOT,asset)) for asset,*_ in GROUPS}
        existing = prepared[GROUPS[0][0]][0][0]
        additional = prepared[GROUPS[1][0]][0][0]
        additional['reserved_slot'] = existing['reserved_slot']
        with patch('cast_art.verified_cast',side_effect=lambda root,asset:prepared[asset]):
            with self.assertRaisesRegex(ValueError,'collide on reserved_slot'):
                registered_groups(ROOT)

    def test_independent_special_palettes_cannot_recolor_people_on_the_same_map(self):
        from copy import deepcopy
        from unittest.mock import patch
        prepared = {asset:deepcopy(verified_cast(ROOT,asset)) for asset,*_ in GROUPS}
        prepared[GROUPS[1][0]][0][0]['map'] = prepared[GROUPS[0][0]][0][0]['map']
        with patch('cast_art.verified_cast',side_effect=lambda root,asset:prepared[asset]):
            with self.assertRaisesRegex(ValueError,'share its special palette'):
                registered_groups(ROOT)

    def test_registered_character_must_be_used_by_its_actual_service_event(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
            content=root/'romhack/content';content.mkdir(parents=True)
            maps = {entry['map'] for asset,*_ in GROUPS for entry in verified_cast(ROOT,asset)[0]}
            for name in maps:
                shutil.copy2(ROOT/'romhack/content'/name,content/name)
            plan=json.loads((content/'services.json').read_text())
            plan['npcs'][0]['graphics']='OBJ_EVENT_GFX_WOMAN_1'
            (content/'services.json').write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError,'registered graphics: justine-moore'):
                registered_groups(root)

    def test_missing_or_collapsed_pose_rows_are_rejected_before_compilation(self):
        for rows, columns in ((2,3),(3,2),(3,4)):
            image = Image.new('RGBA', (80,120))
            for row in range(rows):
                for column in range(columns):
                    image.paste((255,255,255,255),(column*20+2,row*32+2,column*20+12,row*32+26))
            with self.assertRaises(ValueError):
                source_cells(image)

    def test_stale_palette_cannot_be_applied_to_an_engine(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT/'assets/characters/cognition-cast',root/'assets/characters/cognition-cast')
            (root/'assets/characters/cognition-cast/cast.gbapal').write_bytes(bytes(32))
            with self.assertRaisesRegex(ValueError, 'palette differs'):
                apply_cast(root, root/'engine-does-not-exist', lambda path: '')


if __name__ == '__main__':
    unittest.main()
