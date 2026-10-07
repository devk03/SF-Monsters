"""Limits that keep authored teams safe for the native battle interfaces."""
import sys
import unittest
from pathlib import Path
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from battle_content import trainer_record


class TrainerLimits(unittest.TestCase):
    def setUp(self):
        self.team = {'id': 'TRAINER_ROXANNE_1', 'name': 'SCOTT WU',
                     'class': 'TRAINER_CLASS_LEADER', 'portrait': 'TRAINER_PIC_LEADER_BRAWLY',
                     'party': [{'species': 'SPECIES_RALTS', 'level': 8, 'moves': ['MOVE_CONFUSION']}]}

    def test_valid_native_team(self):
        trainer_record(self.team)

    def test_rejects_oversized_party_and_move_list(self):
        for party in [[], self.team['party'] * 7]:
            with self.assertRaises(ValueError): trainer_record({**self.team, 'party': party})
        team = deepcopy(self.team); team['party'][0]['moves'] *= 5
        with self.assertRaises(ValueError): trainer_record(team)

    def test_level_and_name_bounds(self):
        for level in [0, 101]:
            team = deepcopy(self.team); team['party'][0]['level'] = level
            with self.assertRaises(ValueError): trainer_record(team)
        with self.assertRaises(ValueError): trainer_record({**self.team, 'name': 'X' * 13})
        with self.assertRaises(ValueError): trainer_record({**self.team, 'id': 'not a native slot'})


if __name__ == '__main__':
    unittest.main()
