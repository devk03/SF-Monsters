"""Limits that keep authored teams safe for the native battle interfaces."""
import sys
import unittest
import hashlib
import json
from pathlib import Path
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from battle_content import trainer_record


class TrainerLimits(unittest.TestCase):
    def test_portrait_refresh_preserves_complete_teams_encounters_and_rewards(self):
        content = json.loads((Path(__file__).resolve().parents[1] /
                              'romhack/content/first-chapter-battles.json').read_text())
        expected = {'TRAINER_JOSH': 'TRAINER_PIC_WALDEN_YAN',
                    'TRAINER_TOMMY': 'TRAINER_PIC_STEVEN_HAO'}
        for trainer in content['trainers']:
            if trainer['id'] in expected:
                self.assertEqual(trainer['portrait'], expected[trainer['id']])
                trainer['portrait'] = 'TRAINER_PIC_POKEMANIAC'
        self.assertEqual(hashlib.sha256(json.dumps(content, sort_keys=True,
            separators=(',', ':')).encode()).hexdigest(),
            'e3a8dc08dea3100eb539cff40ef7578d06cf83c892cfa85ead26ca44dbc1bbb1')

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
