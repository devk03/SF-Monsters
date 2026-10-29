import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/quality'))
from audit_metatile_usage import audit_profile


class MetatileUsageAuditTest(unittest.TestCase):
    def test_duplicate_attributes_ownership_and_map_use_are_independent(self):
        kit = {'records': [[1] * 8, [1] * 8, [1] * 8, [2] * 8],
               'attributes': [7, 7, 8, 7],
               'catalog': {'shared': {'tiles': [[512, 514], [512, 514]]},
                           'other': {'tiles': [[513]]}}}
        plans = [{'world_id': 'town', 'rows': ['ab'],
                  'legend': {'a': [512, False, 3], 'b': [1, False, 3]},
                  'border_tile': 514}]
        result = audit_profile(kit, plans)
        self.assertEqual(result['duplicate_records'],
                         [{'ids': [512, 513], 'record': [1] * 8, 'attribute': 7}])
        self.assertEqual(result['map_used_ids'], [512, 514])
        self.assertEqual(result['map_unused_ids'], [513, 515])
        self.assertEqual(result['card_owned_ids_by_card']['shared'], [512, 514])
        self.assertEqual(result['card_unowned_ids'], [515])


if __name__ == '__main__':
    unittest.main()
