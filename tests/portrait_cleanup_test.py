"""Native drawing recipes must fail when their source or pixel contract changes."""
from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from trainer_portraits import portrait_cleanup


class PortraitCleanup(unittest.TestCase):
    def setUp(self):
        self.before = bytes(65) + b'\x08' + bytes(4030)
        self.after = bytes(65) + b'\x01' + bytes(4030)
        self.source, self.palette = b'original art', bytes(32)
        digest = lambda data: hashlib.sha256(data).hexdigest()
        self.recipe = {'format': 1, 'intent': 'One independently specified native eye pixel.',
            'source_sha256': digest(self.source), 'palette_sha256': digest(self.palette),
            'before_sha256': digest(self.before), 'after_sha256': digest(self.after),
            'changes': [{'x': 1, 'y': 1, 'old': 8, 'new': 1}]}

    def test_exact_native_edit_preserves_every_other_pixel(self):
        self.assertEqual(portrait_cleanup(self.before, self.recipe, self.source, self.palette), self.after)

    def test_source_palette_or_native_input_cannot_change_silently(self):
        for pixels, source, palette in [(self.before, b'new art', self.palette),
                (self.before, self.source, b'\x01' + bytes(31)),
                (bytes(4096), self.source, self.palette)]:
            with self.assertRaises(ValueError):
                portrait_cleanup(pixels, self.recipe, source, palette)

    def test_invalid_or_ambiguous_edit_is_rejected(self):
        invalid = [{'x': 64}, {'y': -1}, {'new': 16}, {'x': True},
                   {'old': 7}, {'new': 8}, {'extra': 1}]
        for change in invalid:
            recipe = deepcopy(self.recipe); recipe['changes'][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                portrait_cleanup(self.before, recipe, self.source, self.palette)
        for changes in ([], self.recipe['changes'] * 2):
            with self.assertRaises(ValueError):
                portrait_cleanup(self.before, dict(self.recipe, changes=changes), self.source, self.palette)

    def test_output_and_recipe_version_are_pinned(self):
        for change in ({'format': True}, {'format': 2}, {'intent': ''}, {'after_sha256': '0' * 64}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                portrait_cleanup(self.before, dict(self.recipe, **change), self.source, self.palette)


if __name__ == '__main__':
    unittest.main()
