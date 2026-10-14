"""Require complete independent command observations and legal native inputs."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/quality'))
from battle_command_fixtures import validate


class BattleCommandFixtures(unittest.TestCase):
    def test_rejects_incomplete_or_ignored_resource_oracles(self):
        document = {'profile': 'pp', 'cases': [{'id': 'ordinary-cost',
            'expected': {'pp': 9, 'pointer': 0x0203f601, 'controller': 1, 'hitmarker': 0, 'rng': 0},
            'derivation': 'One of10 PP consumed; controller update queued.'}]}
        validate(document)
        for key, value in [('expected', {'pp': 9}), ('pp', 256), ('pp', True),
                           ('rng_seed', -1), ('double', 1), ('mimicked', 1),
                           ('damage', 20), ('derivation', '')]:
            bad = deepcopy(document)
            bad['cases'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(bad)
        with self.assertRaises(ValueError):
            validate({'profile': 'unknown', 'cases': document['cases']})
        with self.assertRaises(ValueError):
            validate({'profile': 'pp', 'cases': document['cases'] * 2})


if __name__ == '__main__':
    unittest.main()
