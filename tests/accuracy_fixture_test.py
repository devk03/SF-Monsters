"""Keep native accuracy evidence explicit about outcomes and random transitions."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/quality'))
from accuracy_fixtures import validate


class AccuracyFixtures(unittest.TestCase):
    def test_rejects_missing_rng_outcomes_and_ignored_controls(self):
        document = {'cases': [{'id': 'rain-thunder', 'expected_hit': True,
                               'expected_flags': 0, 'expected_message': 0,
                               'rng_seed': 0, 'expected_rng': 0,
                               'derivation': 'Rain Thunder takes no accuracy draw.'}]}
        validate(document)
        for key, value in [('expected_hit', None), ('expected_rng', None),
                           ('rng_seed', -1), ('expected_flags', True),
                           ('expected_message', 256), ('protect', 1),
                           ('sure_hit_battler', 4), ('doubles', True), ('derivation', '')]:
            bad = deepcopy(document)
            bad['cases'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(bad)
        with self.assertRaises(ValueError):
            validate({'cases': document['cases'] * 2})


if __name__ == '__main__':
    unittest.main()
