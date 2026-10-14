"""Prevent holes or double-counting in the complete ordered GenIII type matrix."""
from collections import Counter
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/quality'))
from mechanics_fixtures import validate_cases


class TypeMatrix(unittest.TestCase):
    def test_existing_interactions_and_new_pairs_cover_exactly_seventeen_squared(self):
        directory = ROOT / 'data/quality/mechanics'
        old = json.loads((directory / 'type-effects.json').read_text())
        new = json.loads((directory / 'type-matrix.json').read_text())
        validate_cases(old)
        validate_cases(new)
        types = {'TYPE_' + name for name in new['matrix_types']}
        self.assertEqual(len(types), 17)
        self.assertNotIn('TYPE_MYSTERY', types)
        self.assertNotIn('TYPE_FAIRY', types)
        moves = new['move_types']
        self.assertEqual(set(moves.values()), types)
        pairs, counts = {}, []
        for catalog in (old, new):
            count = 0
            for case in catalog['cases']:
                attacker, defender = case.get('attacker', {}), case.get('defender', {})
                if (case.get('move') not in moves or
                        attacker.get('type1') != 'TYPE_MYSTERY' or attacker.get('type2') != 'TYPE_MYSTERY' or
                        defender.get('type1') != defender.get('type2') or defender.get('type1') not in types or
                        any((attacker.get('ability', 0), defender.get('ability', 0), defender.get('status2', 0))) or
                        case.get('damage', 100) != 100):
                    continue
                pair = moves[case['move']], defender['type1']
                self.assertNotIn(pair, pairs, 'A repeated pair cannot increase chart coverage.')
                flags = case['expected']
                self.assertIn(flags, (0, 2, 4, 8))
                self.assertEqual(case['expected_damage'], {0: 100, 2: 200, 4: 50, 8: 0}[flags])
                pairs[pair] = flags
                count += 1
            counts.append(count)
        self.assertEqual(counts, [42, 247])
        self.assertEqual(set(pairs), {(attack, defense) for attack in types for defense in types})
        self.assertEqual(Counter(pairs.values()), {0: 179, 2: 46, 4: 57, 8: 7})
        self.assertEqual(len(old['cases']) + len(new['cases']), 319)
        self.assertEqual(len(old['cases']) - counts[0], 30)  # Retain interaction/boundary scenarios.


if __name__ == '__main__':
    unittest.main()
