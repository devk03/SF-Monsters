"""Authored icon provenance and native atlas format, independent of importer code."""
from pathlib import Path
import sys
import unittest
import uuid
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from monster_atlas import atlas_assets
from monsters import png_palette


class AuthoredAtlas(unittest.TestCase):
    def test_unequal_panels_keep_the_outer_flipper_and_ground_line(self):
        scratch = ROOT / '.tools' / ('atlas-test-' + uuid.uuid4().hex)
        scratch.mkdir(parents=True)
        image = Image.new('RGBA', (30, 16)); draw = ImageDraw.Draw(image)
        for left, right in [(0, 12), (12, 22), (22, 30)]:
            draw.rectangle((left + 2, 1, right - 2, 6), fill=(255, 0, 0, 255))
        draw.point((11, 6), fill=(0, 255, 0, 255))
        draw.rectangle((2, 10, 5, 13), fill=(0, 0, 255, 255))
        draw.rectangle((12, 10, 15, 13), fill=(0, 0, 255, 255))
        image.save(scratch / 'source.png')
        path = scratch / 'icons.pal'
        colors = [(0, 0, 0), (0, 0, 255)] + [(255, 0, 0)] * 14
        path.write_text('JASC-PAL\n0100\n16\n' + '\n'.join('%d %d %d' % c for c in colors) + '\n')
        layout = {'battle': [[0, 0, 12, 8], [12, 0, 22, 8], [22, 0, 30, 8]],
                  'icons': [[0, 8, 10, 16], [10, 8, 20, 16]], 'pad_frames': True}
        atlas_assets(scratch / 'source.png', scratch / 'native', layout, path)
        front = Image.open(scratch / 'native/front.png').convert('RGBA')
        back = Image.open(scratch / 'native/back.png').convert('RGBA')
        self.assertTrue(any(p[:3] == (0, 255, 0) and p[3] for p in front.get_flattened_data()))
        self.assertEqual(front.getchannel('A').getbbox()[3], back.getchannel('A').getbbox()[3])

    def test_authored_icons_keep_the_shared_palette_and_alternate_frame(self):
        scratch = ROOT / '.tools' / ('atlas-test-' + uuid.uuid4().hex)
        scratch.mkdir(parents=True)
        image = Image.new('RGBA', (24, 16)); draw = ImageDraw.Draw(image)
        for x in [0, 8, 16]: draw.rectangle((x + 2, 1, x + 5, 6), fill=(255, 0, 0, 255))
        draw.rectangle((2, 10, 5, 13), fill=(0, 0, 255, 255))
        draw.rectangle((10, 10, 13, 13), fill=(0, 0, 255, 255))
        draw.rectangle((10, 14, 11, 14), fill=(0, 255, 0, 255))
        image.save(scratch / 'source.png')
        palette = [(0, 0, 0), (0, 0, 255), (255, 0, 0), (0, 255, 0)] + [(0, 0, 0)] * 12
        path = scratch / 'icons.pal'
        path.write_text('JASC-PAL\n0100\n16\n' + '\n'.join('%d %d %d' % c for c in palette) + '\n')
        layout = {'battle': [[0, 0, 8, 8], [8, 0, 16, 8], [16, 0, 24, 8]],
                  'icons': [[0, 8, 8, 16], [8, 8, 16, 16]]}
        atlas_assets(scratch / 'source.png', scratch / 'native', layout, path)
        front = Image.open(scratch / 'native/front.png').convert('RGBA')
        icon = Image.open(scratch / 'native/icon.png').convert('RGBA')
        self.assertEqual(front.size, (64, 64)); self.assertEqual(icon.size, (32, 64))
        self.assertFalse(any(p[:3] == (0, 0, 255) and p[3] for p in front.get_flattened_data()))
        self.assertTrue(any(p[:3] == (0, 0, 255) and p[3] for p in icon.get_flattened_data()))
        self.assertFalse(any(p[:3] == (0, 255, 0) and p[3] for p in icon.crop((0, 0, 32, 32)).get_flattened_data()))
        self.assertTrue(any(p[:3] == (0, 255, 0) and p[3] for p in icon.crop((0, 32, 32, 64)).get_flattened_data()))
        expected = bytes(c for color in palette for c in color)
        self.assertEqual(png_palette(scratch / 'native/icon.png', (32, 64)), expected)
        palettes = [png_palette(scratch / ('native/' + name + '.png'), size)
                    for name, size in [('front', (64, 64)), ('back', (64, 64)), ('anim_front', (64, 128))]]
        self.assertEqual(palettes[0], palettes[1]); self.assertEqual(palettes[0], palettes[2])


if __name__ == '__main__': unittest.main()
