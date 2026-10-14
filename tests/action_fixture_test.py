"""Prevent incomplete or mislabeled doubles evidence from entering the catalog."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/quality'))
from action_fixtures import validate


class ActionFixtures(unittest.TestCase):
    def test_rejects_incomplete_or_ambiguous_ordering_expectations(self):
        document = {'cases': [{'id': 'four-distinct-speeds', 'expected_order': [0, 2, 1, 3],
                               'derivation': 'Speeds120>100>80>60.'}]}
        validate(document)
        for key, value in [('expected_order', [0, 1, 1, 3]), ('expected_order', [0, 1]),
                           ('expected_order', [False, 2, 1, 3]), ('actions', ['B_ACTION_USE_MOVE']),
                           ('actions', ['B_ACTION_NONE'] * 4), ('battle_flags', 2),
                           ('quick_claw_draw', 65536), ('derivation', '')]:
            bad = deepcopy(document)
            bad['cases'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(bad)
        with self.assertRaises(ValueError):
            validate({'cases': document['cases'] * 2})


if __name__ == '__main__':
    unittest.main()
