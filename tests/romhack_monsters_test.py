"""Creature authoring limits that protect native tables and save identities."""
from copy import deepcopy
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from monsters import check_monster, check_catalog, png_palette, check_progression, apply_progression, install_creature_art, apply_enemy_elevation


class MonsterContracts(unittest.TestCase):
    def setUp(self):
        self.mon = json.loads((ROOT / 'romhack/content/monsters.json').read_text())['monsters'][0]

    def test_complete_native_record_and_art(self):
        catalog = json.loads((ROOT / 'romhack/content/monsters.json').read_text())['monsters']
        check_catalog(catalog)
        for mon in catalog:
            with self.subTest(species=mon['species']):
                check_monster(mon)
                art = ROOT / mon['art']
                palettes = [png_palette(art / (name + '.png'), size) for name, size in
                            [('front', (64, 64)), ('anim_front', (64, 128)), ('back', (64, 64))]]
                self.assertTrue(all(palette == palettes[0] for palette in palettes))
        with self.assertRaises(ValueError): png_palette(art / 'front.png', (32, 32))

    def test_reapplying_authored_art_rebuilds_newer_inherited_make_outputs(self):
        # No ROM fixture: these are our real indexed art sources and a small
        # dependency rule exercising the same timestamp contract as native Make.
        directory = Path(tempfile.mkdtemp(prefix='creature-art-cache-', dir=ROOT/'.tools'))
        source, engine = directory/'authored', directory/'engine'
        source.mkdir(); engine.mkdir()
        art = ROOT/'assets/monsters/sproutslug/native-v1'
        names = ['front.png', 'anim_front.png', 'back.png', 'icon.png', 'normal.pal', 'shiny.pal']
        for name in names:
            shutil.copyfile(art/name, source/name)
            os.utime(source/name, (1000, 1000))
            shutil.copy2(source/name, engine/name)  # The previous installer.
            (engine/('built-'+name)).write_bytes(b'INHERITED CACHE')
            os.utime(engine/('built-'+name), (2000, 2000))
        makefile = 'all: ' + ' '.join('built-'+name for name in names) + '\n'
        makefile += ''.join(f'built-{name}: {name}\n\tcp {name} built-{name}\n' for name in names)
        (engine/'Makefile').write_text(makefile)
        command = ['make', '-s', '--no-print-directory', 'all']
        subprocess.run(command, cwd=engine, check=True, capture_output=True)
        self.assertTrue(all((engine/('built-'+name)).read_bytes() == b'INHERITED CACHE' for name in names),
                        'The old preserved-mtime input must reproduce the stale build first')
        palette_lines = (art/'normal.pal').read_text().splitlines()[3:]
        palette = bytes(int(channel) for line in palette_lines for channel in line.split())
        install_creature_art(source, engine, palette)
        subprocess.run(command, cwd=engine, check=True, capture_output=True)
        for name in names:
            with self.subTest(asset=name):
                self.assertEqual((engine/('built-'+name)).read_bytes(), (source/name).read_bytes())
        # Evidence is retained; no removal operation is needed for this fixture.

    def test_name_stats_and_learnset_bounds(self):
        changes = [{'name': 'X' * 11}, {'category': 'X' * 12}, {'stats': {'baseHP': 50}},
                   {'learnset': [[6, 'MOVE_EMBER'], [5, 'MOVE_SCRATCH']]},
                   {'learnset': [[101, 'MOVE_EMBER']]}, {'species': 'unsafe slot'},
                   {'icon_palette': 6}, {'migration_move': [1, 'MOVE_SURF']}]
        changes.extend({'enemy_elevation': value} for value in [None, True, -1, 33, 1.5])
        changes.append({'coordinates': {'front': [72, 56, 4], 'back': [56, 56, 4]}})
        changes.extend([{'evolutions': [{'level': 101, 'species': 'SPECIES_COMBUSKEN'}]},
                        {'evolutions': [{'level': 16, 'species': self.mon['species']}]}])
        for fields in changes:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                check_monster({**deepcopy(self.mon), **fields})

    def test_grounded_replacement_preserves_other_species_flight(self):
        header = 'const u8 gEnemyMonElevation[NUM_SPECIES] =\n{\n    [SPECIES_MAGNEMITE] = 16,\n    [SPECIES_WINGULL] = 16,\n};\n'
        grounded = apply_enemy_elevation(header, 'SPECIES_MAGNEMITE', 0)
        self.assertEqual(grounded, header.replace('[SPECIES_MAGNEMITE] = 16', '[SPECIES_MAGNEMITE] = 0'))
        inserted = apply_enemy_elevation(grounded, 'SPECIES_TREECKO', 0)
        self.assertEqual(inserted.count('[SPECIES_TREECKO] = 0,'), 1)
        self.assertEqual(apply_enemy_elevation(inserted, 'SPECIES_TREECKO', 0), inserted)
        self.assertIn('[SPECIES_WINGULL] = 16,', inserted)

    def test_authored_evolution_targets_thresholds_and_cycles(self):
        line = []
        for species, symbol, name in [('SPECIES_TORCHIC', 'Torchic', 'CINDERCOY'),
                                      ('SPECIES_COMBUSKEN', 'Combusken', 'ASHRUNNER'),
                                      ('SPECIES_BLAZIKEN', 'Blaziken', 'SOLHOWL')]:
            mon = deepcopy(self.mon)
            mon.update(species=species, symbol=symbol, name=name,
                       engine_asset_dir=symbol.lower(), evolutions=[])
            line.append(mon)
        line[0]['evolutions'] = [{'level': 16, 'species': line[1]['species']}]
        line[1]['evolutions'] = [{'level': 36, 'species': line[2]['species']}]
        check_catalog(line)
        with self.assertRaises(ValueError): check_catalog(line[:2])
        wrong = deepcopy(line); wrong[1]['evolutions'][0]['level'] = 12
        with self.assertRaises(ValueError): check_catalog(wrong)
        cycle = deepcopy(line); cycle[2]['evolutions'] = [{'level': 50, 'species': line[0]['species']}]
        with self.assertRaises(ValueError): check_catalog(cycle)
        repeated = deepcopy(line); repeated[1]['engine_asset_dir'] = line[0]['engine_asset_dir']
        with self.assertRaises(ValueError): check_catalog(repeated)

    def test_native_progression_keeps_saved_experience_curve(self):
        record = '''    [SPECIES_TORCHIC] = {
            .baseHP = 48, .catchRate = 45, .expYield = 65,
            .evYield_HP = 0, .evYield_Attack = 0, .evYield_Defense = 0,
            .evYield_Speed = 0, .evYield_SpAttack = 1, .evYield_SpDefense = 0,
            .growthRate = GROWTH_MEDIUM_SLOW, .friendship = STANDARD_FRIENDSHIP,
        },'''
        progression = {'growth_rate': 'GROWTH_MEDIUM_SLOW', 'catch_rate': 100,
                       'exp_yield': 55, 'ev_yield': [1, 0, 0, 0, 1, 0]}
        output = apply_progression(record, progression)
        for fragment in ['.catchRate = 100', '.expYield = 55', '.evYield_HP = 1',
                         '.growthRate = GROWTH_MEDIUM_SLOW', '.baseHP = 48',
                         '.friendship = STANDARD_FRIENDSHIP']:
            self.assertIn(fragment, output)
        with self.assertRaises(ValueError):
            apply_progression(record, {**progression, 'growth_rate': 'GROWTH_FAST'})

    def test_progression_rejects_truncation_and_excess_effort_rewards(self):
        progression = self.mon['progression']
        for fields in [{'catch_rate': 0}, {'catch_rate': 256}, {'exp_yield': True},
                       {'exp_yield': 256}, {'growth_rate': 'GROWTH_UNKNOWN'},
                       {'ev_yield': [0] * 5}, {'ev_yield': [4, 0, 0, 0, 0, 0]},
                       {'ev_yield': [1] * 6}, {'ev_yield': [True, 0, 0, 0, 0, 0]}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                check_progression({**deepcopy(progression), **fields})


if __name__ == '__main__': unittest.main()
