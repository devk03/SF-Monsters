"""Threshold assets must stay shallow, transparent and palette-consistent."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from sidewalk_thresholds import ASSET,load
from PIL import Image


class ThresholdAssets(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='sf-threshold-test-'))
        self.directory=self.root/ASSET
        shutil.copytree(ROOT/ASSET,self.directory)

    def metadata(self,change):
        path=self.directory/'conversion.json'
        info=json.loads(path.read_text());change(info)
        path.write_text(json.dumps(info))

    def test_all_four_original_candidates_leave_the_lower_half_open(self):
        cards=load(self.root)
        self.assertEqual(set(cards),{'bay','brick','sage','coffee'})
        for name,card in cards.items():
            self.assertEqual((card['width'],card['height']),(32 if name=='coffee' else 48,16))
            self.assertEqual(card['pixels'][card['width']*8:],bytes(card['width']*8))
            self.assertEqual(card['bank'],5)

    def test_modified_source_or_prompt_requires_explicit_regeneration(self):
        for name in ('source.png','prompt.md'):
            path=self.directory/name;original=path.read_bytes()
            path.write_bytes(original+b'changed')
            with self.assertRaisesRegex(ValueError,'source/prompt'):load(self.root)
            path.write_bytes(original)

    def test_native_palette_and_card_geometry_are_bounded(self):
        for key,value in [('bank',4),('alpha_threshold',0)]:
            old=(self.directory/'conversion.json').read_bytes()
            self.metadata(lambda info:info.update({key:value}))
            with self.assertRaises(ValueError):load(self.root)
            (self.directory/'conversion.json').write_bytes(old)
        self.metadata(lambda info:info['cards'][0].update(size=[64,16]))
        with self.assertRaisesRegex(ValueError,'geometry'):load(self.root)

    def test_self_consistent_pixel_hashes_cannot_fill_walkable_paving_with_a_slab(self):
        image=Image.open(self.directory/'brick.png');image.putpixel((0,15),1)
        image.save(self.directory/'brick.png',bits=4,transparency=0)
        (self.directory/'brick.indices').write_bytes(image.tobytes())
        self.metadata(lambda info:info['cards'][1].update(files={name:hashlib.sha256(
            (self.directory/name).read_bytes()).hexdigest() for name in ('brick.png','brick.indices')}))
        with self.assertRaisesRegex(ValueError,'lower eight rows'):load(self.root)

    def test_rehashed_preview_cannot_disagree_with_consumed_palette(self):
        image=Image.open(self.directory/'bay.png');palette=image.getpalette()
        palette[3:6]=[255,0,0];image.putpalette(palette)
        image.save(self.directory/'bay.png',bits=4,transparency=0)
        self.metadata(lambda info:info['cards'][0]['files'].update({
            'bay.png':hashlib.sha256((self.directory/'bay.png').read_bytes()).hexdigest()}))
        with self.assertRaisesRegex(ValueError,'preview palette'):load(self.root)


if __name__=='__main__':unittest.main()
