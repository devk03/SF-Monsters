"""Generated-stat oracles must describe legal inputs and explicit content mappings."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/quality'))
from stat_fixtures import validate


class StatFixtures(unittest.TestCase):
    def setUp(self):
        self.document = {'cases': [{'id': 'neutral', 'expected': [120, 120, 69, 69, 65, 85, 85],
                                   'derivation': 'Explicit level50 neutral fixed-IV31 vector.'}]}

    def test_rejects_invalid_generation_and_effort_values(self):
        for key, value in [('nature', 25), ('iv', 32), ('level', 0), ('nature', True),
                           ('evs', [256, 0, 0, 0, 0, 0]), ('evs', [100] * 6),
                           ('ivs', [31] * 5), ('derivation', '')]:
            bad = deepcopy(self.document)
            bad['cases'][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate(bad)

    def test_sf_content_difference_cannot_silently_replace_reference_oracle(self):
        document = deepcopy(self.document)
        document['cases'][0]['candidate_expected'] = [123, 123, 75, 62, 84, 81, 65]
        with self.assertRaisesRegex(ValueError, 'content mapping'):
            validate(document)
        document['cases'][0]['intentional_content_difference'] = 'Declared SF base stats differ; formulas are unchanged.'
        validate(document)
        with self.assertRaises(ValueError):
            validate({'cases': document['cases'] * 2})


if __name__ == '__main__':
    unittest.main()
