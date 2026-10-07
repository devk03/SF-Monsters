"""Native asset contracts: palette identity, sprite dimensions and transparency."""
import uuid
import unittest
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from monster_art import native_assets


class NativeArt(unittest.TestCase):
    def test_shared_palette_and_native_sprite_shapes(self):
        # Preserve fixtures, including successful runs, under ignored storage.
        root = Path(__file__).resolve().parents[1] / '.tools/art-fixtures' / uuid.uuid4().hex
        root.mkdir(parents=True)
        source = Image.new('RGBA', (48, 16))
        for cell in range(3):
            for x in range(4, 12):
                for y in range(4, 12): source.putpixel((cell * 16 + x, y), (180, 70 + cell * 20, 40, 255))
        source.save(root / 'source.png')
        native_assets(root / 'source.png', root / 'output', [0, 0, 16, 16])
        palettes = []
        for name, size in [('front', (64, 64)), ('anim_front', (64, 128)), ('back', (64, 64)), ('icon', (32, 64))]:
            image = Image.open(root / 'output' / (name + '.png'))
            self.assertEqual(image.size, size)
            self.assertEqual(image.info['transparency'], 0)
            self.assertLessEqual(image.getextrema()[1], 15)
            self.assertEqual(image.getpixel((0, 0)), 0)
            self.assertGreater(image.getpixel((size[0] // 2, size[0] // 2)), 0)
            palettes.append(image.getpalette())
        self.assertTrue(all(palette == palettes[0] for palette in palettes))
        self.assertEqual(len((root / 'output/normal.pal').read_text().splitlines()), 19)


if __name__ == '__main__': unittest.main()
