"""Capture vectors must be explicit, bounded and encodable by the guarded driver."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/quality'))
from capture_fixtures import validate, program, FUNCTIONS, ALLOCATIONS
from mechanics_fixtures import GLOBALS


class CaptureFixtures(unittest.TestCase):
    def setUp(self):
        self.document = {'cases': [{'id': 'one-shake', 'ball': 'ITEM_POKE_BALL',
            'derivation': 'Odds35; seed0 gives one passing draw then failure.',
            'expected': {'pointer': 'BattleScript_ShakeBallThrow', 'animation': 1,
                'controller': 1, 'rng': 3917380458, 'attempts': 1, 'master': 0,
                'caught_ball': 4, 'chooser': 1, 'party_count': 1, 'map_type': 1}}]}

    def test_rejects_partial_oracles_ignored_controls_and_illegal_capture_states(self):
        validate(self.document)
        for key, value in [('expected', {'animation': 1}), ('derivation', ''),
                           ('ball', 'ITEM_NONE'), ('ball', 'ITEM_REPEAT_BALL'),
                           ('full_party', 1), ('hp', 91), ('max_hp', 0),
                           ('rng_seed', True), ('attempt_count', 256), ('turn', 256),
                           ('dex_state', 'caught'), ('safari_factor', 20), ('seed', 3)]:
            bad = deepcopy(self.document)
            bad['cases'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(bad)
        for value in ('BattleScript_Unreviewed', [], True):
            bad = deepcopy(self.document)
            bad['cases'][0]['expected']['pointer'] = value
            with self.subTest(pointer=value), self.assertRaises(ValueError):
                validate(bad)
        with self.assertRaises(ValueError):
            validate({'cases': self.document['cases'] * 2})

    def test_catalog_declares_all_twelve_native_ball_branches_with_complete_oracles(self):
        path = Path(__file__).resolve().parents[1] / 'data/quality/mechanics/capture.json'
        cases = validate(json.loads(path.read_text()))
        self.assertEqual({case['ball'] for case in cases}, {'ITEM_' + name + '_BALL' for name in
            ('POKE', 'GREAT', 'ULTRA', 'MASTER', 'NET', 'DIVE', 'NEST', 'TIMER',
             'LUXURY', 'PREMIER', 'REPEAT', 'SAFARI')})
        self.assertEqual({case['dex_state'] for case in cases if case['ball'] == 'ITEM_REPEAT_BALL'},
                         {'none', 'seen', 'caught', 'owned-only'})

    def test_large_controller_buffer_uses_bounded_ram_writes_and_complete_observations(self):
        globals_ = {**GLOBALS, **ALLOCATIONS}
        syms = {name: (0x02000000 + index * 2048, size)
                for index, (name, size) in enumerate(globals_.items())}
        syms.update({name: (0x08000100 + index * 16, 16) for index, name in enumerate(sorted(FUNCTIONS))})
        values = {'SPECIES_BULBASAUR': 1, 'ITEM_POKE_BALL': 4, 'ITEM_ULTRA_BALL': 2,
                  'ITEM_MASTER_BALL': 1, 'MOVE_POUND': 1}
        resolve = lambda v: v if type(v) is int else values[v]
        sequence, reads = program(self.document['cases'][0], syms, resolve, {'MON_DATA_POKEBALL': 38})
        written = {}
        for line in sequence.splitlines():
            if line.startswith('write '):
                _, address, payload = line.split()
                self.assertEqual(len(payload) % 2, 0)
                self.assertLessEqual(len(payload), 2048)
                written[int(address, 16)] = bytes.fromhex(payload)
        start = syms['gBattleBufferA'][0]
        self.assertEqual(written[start] + written[start + 1024], bytes([165]) * 2048)
        self.assertEqual(written[0x02028000][4:6], bytes([0, 10]))
        underwater = deepcopy(self.document['cases'][0])
        underwater['underwater'] = True
        underwater['expected']['map_type'] = 5
        underwater_sequence, _ = program(underwater, syms, resolve, {'MON_DATA_POKEBALL': 38})
        saved_location = next(line.split()[2] for line in underwater_sequence.splitlines()
                              if line.startswith('write 2028000 '))
        self.assertEqual(bytes.fromhex(saved_location)[4:6], bytes([0, 50]))
        self.assertIn(f'call {syms["GetCurrentMapType"][0]:x} ', underwater_sequence)
        self.assertEqual(set(reads), {'pointer', 'animation', 'controller', 'rng',
                                     'attempts', 'master', 'chooser', 'party_count'})
        self.assertTrue(sequence.startswith('reset\n'))


if __name__ == '__main__':
    unittest.main()
