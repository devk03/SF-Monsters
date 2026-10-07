"""Creature authoring limits that protect native tables and save identities."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from monsters import check_monster, png_palette


class MonsterContracts(unittest.TestCase):
    def setUp(self):
        self.mon = json.loads((ROOT / 'romhack/content/monsters.json').read_text())['monsters'][0]

    def test_complete_native_record_and_art(self):
        catalog = json.loads((ROOT / 'romhack/content/monsters.json').read_text())['monsters']
        for mon in catalog:
            with self.subTest(species=mon['species']):
                check_monster(mon)
                art = ROOT / mon['art']
                palettes = [png_palette(art / (name + '.png'), size) for name, size in
                            [('front', (64, 64)), ('anim_front', (64, 128)), ('back', (64, 64))]]
                self.assertTrue(all(palette == palettes[0] for palette in palettes))
        with self.assertRaises(ValueError): png_palette(art / 'front.png', (32, 32))

    def test_name_stats_and_learnset_bounds(self):
        changes = [{'name': 'X' * 11}, {'stats': {'baseHP': 50}},
                   {'learnset': [[6, 'MOVE_EMBER'], [5, 'MOVE_SCRATCH']]},
                   {'learnset': [[101, 'MOVE_EMBER']]}, {'species': 'unsafe slot'},
                   {'icon_palette': 6}, {'migration_move': [1, 'MOVE_SURF']}]
        changes.append({'coordinates': {'front': [72, 56, 4], 'back': [56, 56, 4]}})
        for fields in changes:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                check_monster({**deepcopy(self.mon), **fields})


if __name__ == '__main__': unittest.main()
