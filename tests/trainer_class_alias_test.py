"""Two-person class display hook preserves ordinary fallbacks and special modes."""
from pathlib import Path
import subprocess
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / 'scripts/romhack'))
from trainer_class_alias import GETTER, ALIASED_GETTER, transform, apply_alias


class ScopedClassAlias(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Portable source fragments keep routine checks usable without a ROM or
        # private engine checkout. The complete pinned-source test is optional.
        cls.pokemon = '#include "constants/trainers.h"\n' + '''const u8 *GetTrainerClassNameFromId(u16 trainerId)
{
    if (trainerId >= TRAINERS_COUNT)
        trainerId = TRAINER_NONE;
    return gTrainerClassNames[gTrainers[trainerId].trainerClass];
}
// Unrelated source remains exact.
'''
        special = ('GetSecretBaseTrainerClass()', 'GetUnionRoomTrainerClass()',
            'GetFrontierBrainTrainerClass()', 'GetFrontierOpponentClass(gTrainerBattleOpponent_A)',
            'GetTrainerHillOpponentClass(gTrainerBattleOpponent_A)', 'GetEreaderTrainerClassId()',
            'GetFrontierOpponentClass(gTrainerBattleOpponent_B)',
            'GetTrainerHillOpponentClass(gTrainerBattleOpponent_B)')
        cls.messages = '#include "palette.h"\n' + '\n'.join(
            'toCpy = gTrainerClassNames['+value+'];' for value in special)
        for side in ('A','B'):
            cls.messages += '\ntoCpy = gTrainerClassNames[gTrainers[gTrainerBattleOpponent_'+side+'].trainerClass];'
        cls.messages += '\n// Unrelated class/template data stays exact.\n'

    def test_source_changes_only_reviewed_getter_lookups_and_includes(self):
        p,m = transform(self.pokemon,self.messages)
        restored_p = p.replace('#include "constants/opponents.h"\n','').replace(ALIASED_GETTER,GETTER)
        restored_m = m.replace('#include "pokemon.h"\n','')
        for side in ('A','B'):
            restored_m = restored_m.replace(
                f'toCpy = GetTrainerClassNameFromId(gTrainerBattleOpponent_{side});',
                f'toCpy = gTrainerClassNames[gTrainers[gTrainerBattleOpponent_{side}].trainerClass];')
        self.assertEqual(restored_p,self.pokemon)
        self.assertEqual(restored_m,self.messages)
        self.assertLess(p.index('trainerId >= TRAINERS_COUNT'),p.index('trainerId == TRAINER_JOSH'))
        self.assertIn('trainerId == TRAINER_TOMMY',p)
        self.assertIn('gTrainers[trainerId].trainerClass == TRAINER_CLASS_POKEMANIAC',p)
        self.assertNotIn('gTrainerClassNames[TRAINER_CLASS_POKEMANIAC] =',p)

    def test_existing_species_overlays_and_all_special_battle_branches_stay_exact(self):
        marker='\n// Existing species overlay is preserved.\n'
        p,m = transform(self.pokemon+marker,self.messages)
        self.assertTrue(p.endswith(marker))
        special = ('GetSecretBaseTrainerClass()', 'GetUnionRoomTrainerClass()',
            'GetFrontierBrainTrainerClass()', 'GetFrontierOpponentClass(gTrainerBattleOpponent_A)',
            'GetTrainerHillOpponentClass(gTrainerBattleOpponent_A)', 'GetEreaderTrainerClassId()',
            'GetFrontierOpponentClass(gTrainerBattleOpponent_B)',
            'GetTrainerHillOpponentClass(gTrainerBattleOpponent_B)')
        for expression in special:
            self.assertEqual(m.count('gTrainerClassNames['+expression+']'),
                             self.messages.count('gTrainerClassNames['+expression+']'))

    def test_stale_duplicate_or_partial_anchors_fail_before_installing(self):
        for p,m in [(self.pokemon.replace('trainerId >= TRAINERS_COUNT','trainerId > TRAINERS_COUNT'),self.messages),
                    (self.pokemon+GETTER,self.messages),
                    (self.pokemon,self.messages.replace('gTrainerBattleOpponent_A].trainerClass','gTrainerBattleOpponent_A].trainerClassX')),
                    (self.pokemon,self.messages.replace('gTrainerBattleOpponent_B].trainerClass','gTrainerBattleOpponent_B].trainerClassX')),
                    (self.pokemon,self.messages.replace('#include "palette.h"','#include "pokemon.h"'))]:
            with self.assertRaises(ValueError):transform(p,m)
        with self.assertRaises(ValueError):transform(*transform(self.pokemon,self.messages))


    def test_failed_second_source_cannot_partially_write_first_source(self):
        engine = ROOT / '.tools' / ('class-alias-test-' + uuid.uuid4().hex)
        (engine/'src').mkdir(parents=True)
        first,second = engine/'src/pokemon.c',engine/'src/battle_message.c'
        first.write_text(self.pokemon)
        second.write_text(self.messages.replace('gTrainerBattleOpponent_B].trainerClass','stale_B'))
        before = (first.read_bytes(),second.read_bytes())
        with self.assertRaises(ValueError):apply_alias(ROOT,engine)
        self.assertEqual((first.read_bytes(),second.read_bytes()),before)

    def test_repeat_build_refreshes_only_its_own_complete_hook(self):
        engine = ROOT / '.tools' / ('class-alias-test-' + uuid.uuid4().hex)
        (engine/'src').mkdir(parents=True)
        first,second = engine/'src/pokemon.c',engine/'src/battle_message.c'
        first.write_text(self.pokemon);second.write_text(self.messages)
        apply_alias(ROOT,engine)
        once = (first.read_text(),second.read_text())
        apply_alias(ROOT,engine)
        self.assertEqual((first.read_text(),second.read_text()),once)
        marker = '\n// Later unrelated overlay stays exact.\n'
        first.write_text(first.read_text()+marker)
        apply_alias(ROOT,engine)
        self.assertEqual((first.read_text(),second.read_text()),(once[0]+marker,once[1]))
        # An incomplete prior hook fails without touching either current file.
        second.write_text(second.read_text().replace('GetTrainerClassNameFromId(gTrainerBattleOpponent_B)', 'stale_B'))
        before = (first.read_bytes(),second.read_bytes())
        with self.assertRaises(ValueError):apply_alias(ROOT,engine)
        self.assertEqual((first.read_bytes(),second.read_bytes()),before)

    @unittest.skipUnless((ROOT/'.tools/pokeemerald-host/.git').exists(),
                         'Optional full pinned-engine source check; portable guards run without it.')
    def test_complete_pinned_engine_sources_preserve_every_unrelated_byte(self):
        engine = ROOT/'.tools/pokeemerald-host'
        p,m = [subprocess.check_output(['git','show',
            '731ad5bfd6e6f265508d0efcca0ba42f9dcf5881:'+name],cwd=engine,text=True)
            for name in ('src/pokemon.c','src/battle_message.c')]
        new_p,new_m = transform(p,m)
        restored_p = new_p.replace('#include "constants/opponents.h"\n','').replace(ALIASED_GETTER,GETTER)
        restored_m = new_m.replace('#include "pokemon.h"\n','')
        for side in ('A','B'):
            restored_m = restored_m.replace(
                f'toCpy = GetTrainerClassNameFromId(gTrainerBattleOpponent_{side});',
                f'toCpy = gTrainerClassNames[gTrainers[gTrainerBattleOpponent_{side}].trainerClass];')
        self.assertEqual((restored_p,restored_m),(p,m))


if __name__ == '__main__':
    unittest.main()
