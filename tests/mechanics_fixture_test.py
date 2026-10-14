"""Keep native fixture controls explicit; expectations cannot be inferred or padded."""
from copy import deepcopy
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/quality'))
from mechanics_fixtures import battle_mon, validate_cases


class MechanicsFixtures(unittest.TestCase):
    def setUp(self):
        self.document = {'cases': [{'id': 'physical-neutral', 'expected': 19,
                                   'derivation': '17 intermediate plus2.'}]}

    def test_rejects_padding_missing_oracle_and_silently_ignored_controls(self):
        for field, value in [('expected', True), ('derivation', ''), ('doubles', True),
                             ('double', 1), ('critical', 3), ('absent', 16)]:
            document = deepcopy(self.document)
            document['cases'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_cases(document)
        with self.assertRaises(ValueError):
            validate_cases({'cases': self.document['cases'] * 2})

    def test_fixture_matches_native_battlemon_abi_and_rejects_invalid_stats(self):
        data = battle_mon({'attack': 201, 'sp_attack': 77, 'hp': 30, 'max_hp': 90,
                           'attack_stage': 4, 'level': 50, 'status': 16}, int)
        self.assertEqual(len(data), 88)
        # Pinned BattlePokemon ABI: physical02, special08, stages18, HP28/max2C.
        self.assertEqual(struct.unpack_from('<H', data, 2)[0], 201)
        self.assertEqual(struct.unpack_from('<H', data, 8)[0], 77)
        self.assertEqual((data[25], data[28]), (4, 6))
        self.assertEqual((struct.unpack_from('<H', data, 40)[0],
                          struct.unpack_from('<H', data, 44)[0]), (30, 90))
        self.assertEqual(struct.unpack_from('<I', data, 76)[0], 16)
        for changes in ({'defense': 0}, {'level': 101}, {'sp_attack_stage': 13}, {'defence': 100}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                battle_mon(changes, int)

    def test_turn_ties_need_explicit_seed_and_rng_transition(self):
        document = {'function': 'GetWhoStrikesFirst', 'cases': [{
            'id': 'odd-tie', 'expected': 2, 'rng_seed': 3,
            'expected_rng': 3310570426, 'derivation': 'One LCG step gives0xC5534BBA.'}]}
        validate_cases(document)
        missing = deepcopy(document)
        del missing['cases'][0]['rng_seed']
        with self.assertRaisesRegex(ValueError, 'explicit seed'):
            validate_cases(missing)
        for field, value in [('rng_seed', -1), ('expected_rng', True),
                             ('quick_claw_draw', 65536), ('ignore_moves', 1)]:
            bad = deepcopy(document)
            bad['cases'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_cases(bad)
        with self.assertRaisesRegex(ValueError, 'supported'):
            validate_cases({**document, 'function': 'ArbitraryRoutine'})

    def test_type_effects_require_damage_and_flags_as_separate_oracles(self):
        document = {'function': 'TypeCalc', 'cases': [{
            'id': 'levitate', 'expected': 9, 'expected_damage': 100,
            'defender': {'ability': 26}, 'derivation': 'Blocked flag9 preserves intermediate100.'}]}
        validate_cases(document)
        for field, value in [('expected_damage', None), ('expected_damage', True),
                             ('damage', -1), ('damage', 1000001), ('double', True)]:
            bad = deepcopy(document)
            bad['cases'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_cases(bad)
        raw = battle_mon({'type1': 10, 'type2': 12, 'status2': 1 << 29}, int)
        self.assertEqual(raw[33:35], bytes([10, 12]))
        self.assertEqual(struct.unpack_from('<I', raw, 80)[0], 1 << 29)



if __name__ == '__main__':
    unittest.main()
