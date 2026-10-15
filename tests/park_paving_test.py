"""Portable guards for a palette-preserving, one-tile sidewalk candidate."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/romhack'))
from park_paving import ASSET, encode_paving, load_paving, repeated


class PavingResources(unittest.TestCase):
    def setUp(self):
        # Preserve the tiny fixture directory for inspection; do not delete it.
        self.root = Path(tempfile.mkdtemp(prefix='sf-park-paving-test-'))
        self.directory = self.root/ASSET
        self.directory.mkdir(parents=True)
        street = self.root/'assets/tiles/sunset-streets'
        street.mkdir(parents=True)
        shutil.copy2(ROOT/'assets/tiles/sunset-streets/street.gbapal', street/'street.gbapal')
        # Synthetic codec fixture; never installed as game artwork.
        image = Image.new('RGB', (8, 8), (222, 213, 189))
        for i in range(8):
            image.putpixel((i, 7), (189, 180, 172))
            image.putpixel((7, i), (189, 180, 172))
        image.save(self.directory/'source.png')
        (self.directory/'prompt.md').write_text('Synthetic portable conversion fixture.\n')
        self.original_palette = (street/'street.gbapal').read_bytes()
        encode_paving(self.root)

    def rehash(self, name):
        path = self.directory/'conversion.json'
        metadata = json.loads(path.read_text())
        metadata['files'][name] = hashlib.sha256((self.directory/name).read_bytes()).hexdigest()
        path.write_text(json.dumps(metadata))

    def test_conversion_keeps_existing_colors_and_one_unique_native_quadrant(self):
        pixels = load_paving(self.root)
        master = (self.directory/'master8.indices').read_bytes()
        self.assertEqual(master.count(1), 49)
        self.assertEqual(master.count(2), 15)
        self.assertEqual(pixels, repeated(master))
        quadrants = {bytes(pixels[(y+dy)*16+x+dx] for y in range(8) for x in range(8))
                     for dy in (0, 8) for dx in (0, 8)}
        self.assertEqual(len(quadrants), 1)
        self.assertEqual((self.root/'assets/tiles/sunset-streets/street.gbapal').read_bytes(), self.original_palette)
        metadata = (self.directory/'conversion.json').read_bytes()
        encode_paving(self.root)
        self.assertEqual((self.directory/'conversion.json').read_bytes(), metadata)

    def test_source_or_prompt_changes_require_explicit_reconversion(self):
        for name in ('source.png', 'prompt.md'):
            path = self.directory/name
            original = path.read_bytes()
            path.write_bytes(original+b'x')
            with self.subTest(name=name), self.assertRaises(ValueError):
                load_paving(self.root)
            path.write_bytes(original)

    def test_rehashed_png_palette_cannot_disagree_with_native_palette(self):
        path = self.directory/'paving.png'
        with Image.open(path) as image:
            changed = image.copy()
        colors = changed.getpalette()
        colors[3] = 0
        changed.putpalette(colors)
        changed.save(path, bits=4)
        self.rehash('paving.png')
        with self.assertRaises(ValueError):
            load_paving(self.root)

    def test_changed_master_cannot_silently_desynchronize_the_large_tile(self):
        path = self.directory/'master8.indices'
        raw = bytearray(path.read_bytes())
        raw[0] = 2
        path.write_bytes(raw)
        self.rehash('master8.indices')
        with self.assertRaises(ValueError):
            load_paving(self.root)

    def test_rejects_transparent_out_of_palette_dark_and_bad_size_masters(self):
        for master in (bytes(64), bytes([1]*63+[3]), bytes([1]*47+[2]*17), bytes([1]*64), bytes(63)):
            with self.subTest(master=master), self.assertRaises(ValueError):
                repeated(master)

    def test_palette_and_non_square_sources_fail_closed(self):
        path = self.root/'assets/tiles/sunset-streets/street.gbapal'
        path.write_bytes(bytes(32))
        with self.assertRaises(ValueError):
            load_paving(self.root)
        path.write_bytes(self.original_palette)
        Image.new('RGB', (16, 8)).save(self.directory/'source.png')
        with self.assertRaises(ValueError):
            encode_paving(self.root)


if __name__ == '__main__':
    unittest.main()
