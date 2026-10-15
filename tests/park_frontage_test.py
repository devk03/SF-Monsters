"""Original frontage resources reject stale recipes and inconsistent native data."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import unittest
import uuid
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from park_frontage import ASSET, load


class FrontageAssets(unittest.TestCase):
    def fixture(self):
        root = ROOT / '.tools' / ('frontage-test-' + uuid.uuid4().hex)
        directory = root / ASSET
        directory.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / ASSET, directory)
        return root, directory

    def update_hash(self, directory, name):
        path = directory / 'conversion.json'
        info = json.loads(path.read_text())
        card = next(card for card in info['cards'] if name in card['files'])
        card['files'][name] = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        path.write_text(json.dumps(info))

    def test_real_cards_have_distinct_native_pixels_and_isolated_banks(self):
        cards = load(ROOT)
        self.assertEqual([(c['name'], c['width'], c['height'], c['bank']) for c in cards],
            [('brick',48,80,0),('sage',48,80,1),('sandstone',48,80,2),('coffee',32,64,3)])
        self.assertEqual(len({hashlib.sha256(c['pixels']).hexdigest() for c in cards}), 4)
        self.assertEqual(len({c['palette'] for c in cards}), 4)
        for card in cards:
            self.assertEqual(len(card['pixels']), card['width'] * card['height'])
            self.assertLessEqual(max(card['pixels']), 15)

    def test_changed_source_or_prompt_requires_regeneration(self):
        for filename in ('source.png', 'prompt.md'):
            root, directory = self.fixture()
            with (directory / filename).open('ab') as stream:
                stream.write(b'changed')
            with self.assertRaisesRegex(ValueError, 'source/prompt'):
                load(root)

    def test_consistent_hashes_cannot_hide_invalid_native_palette(self):
        root, directory = self.fixture()
        data = bytearray((directory / 'brick.gbapal').read_bytes())
        struct.pack_into('<H', data, 2, 0x8001)
        (directory / 'brick.gbapal').write_bytes(data)
        self.update_hash(directory, 'brick.gbapal')
        with self.assertRaisesRegex(ValueError, 'RGB555'):
            load(root)

    def test_consistent_hashes_cannot_hide_preview_index_disagreement(self):
        root, directory = self.fixture()
        data = bytearray((directory / 'sage.indices').read_bytes());data[0] ^= 1
        (directory / 'sage.indices').write_bytes(data)
        self.update_hash(directory, 'sage.indices')
        with self.assertRaisesRegex(ValueError, 'preview differs'):
            load(root)

    def test_wrong_card_bank_or_incomplete_resource_set_is_rejected(self):
        for mode in ('bank', 'files'):
            root, directory = self.fixture();path = directory / 'conversion.json'
            info = json.loads(path.read_text())
            if mode == 'bank':info['cards'][3]['bank'] = 11
            else:info['cards'][3]['files'].pop('coffee.indices')
            path.write_text(json.dumps(info))
            with self.assertRaises(ValueError):load(root)


if __name__ == '__main__':
    unittest.main()
