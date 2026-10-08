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
from cast_art import apply_cast, source_cells


class NativeCast(unittest.TestCase):
    def test_all_three_people_have_distinct_native_pose_cycles_and_one_palette(self):
        directory = ROOT / 'assets/characters/cognition-cast'
        metadata = json.loads((directory/'conversion.json').read_text())
        native_colors = struct.unpack('<16H', (directory/'cast.gbapal').read_bytes())
        identities = []
        for entry in metadata['characters']:
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
        self.assertEqual(len(set(identities)), 3)

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
                apply_cast(root, root/'engine-does-not-exist')


if __name__ == '__main__':
    unittest.main()
