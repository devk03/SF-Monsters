"""Protect world/state ownership and independently authored contribution behavior."""
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from content_modules import load_modules, apply_module_layouts, script_with_module, lint_script
from check_module import check, check_scope
from generate_world import generate, write_world
from world_scripts import map_script
from module_playtest import apply_playtest, MAGIC


class ModulesTest(unittest.TestCase):
    def setUp(self):
        (ROOT / '.tools').mkdir(exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix='module-contract-tests-', dir=ROOT / '.tools'))
        self.packages = self.root / 'modules'
        shutil.copytree(ROOT / 'romhack/modules', self.packages)
        self.manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())

    def activate(self, identifier='gym_1'):
        path = self.packages / identifier / 'module.json'
        meta = json.loads(path.read_text()); meta['status'] = 'draft'
        path.write_text(json.dumps(meta))

    def test_stub_packages_preserve_all_original_map_and_script_bytes(self):
        original = generate(self.manifest)
        modules = load_modules(self.manifest, self.packages)
        self.assertEqual(apply_module_layouts(original, modules), original)
        by_world = {m['contract']['world_id']: m for m in modules.values()}
        for plan in original:
            script = map_script(self.manifest, plan)
            self.assertEqual(script_with_module(script, by_world.get(plan['world_id'])), script)

    def test_local_script_edits_cannot_grant_global_badges_or_completion(self):
        module = load_modules(self.manifest, self.packages)['gym_1']
        for flag in ('FLAG_BADGE01_GET', 'FLAG_UNUSED_0x40FC', module['contract']['completion_flag']):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                lint_script('SFMod_gym_1_Run::\n    setflag '+flag+'\n    sfmodule_return 0\n', module['contract'])

    def test_script_cannot_write_shared_vars_jump_out_or_inject_directives(self):
        contract = load_modules(self.manifest, self.packages)['gym_1']['contract']
        for command in ('setvar VAR_UNUSED_0x40FC, 1', 'goto EventScript_UseSurf',
                        '.include "foreign.inc"', 'setvar VAR_RESULT, 1; end',
                        'setflag 0x867', 'call SFMod_gym_2_Run'):
            with self.subTest(command=command), self.assertRaises(ValueError):
                lint_script('SFMod_gym_1_Run::\n    '+command+'\n    sfmodule_return 0\n', contract)

    def test_private_puzzle_state_is_allowed(self):
        contract = load_modules(self.manifest, self.packages)['gym_1']['contract']
        source = 'SFMod_gym_1_Run::\n    setflag '+contract['flags'][0]+'\n    sfmodule_return 0\n'
        self.assertEqual(lint_script(source, contract), source)

    def test_trainer_battle_must_explicitly_rejoin_the_module_after_victory(self):
        contract = load_modules(self.manifest, self.packages)['gym_1']['contract']
        source = ('SFMod_gym_1_Run::\n'
                  '    trainerbattle_single TRAINER_ROXANNE_1, SFMod_gym_1_Intro, SFMod_gym_1_Defeat\n'
                  'SFMod_gym_1_Won::\n    sfmodule_return 1\n'
                  'SFMod_gym_1_Intro::\n    .string "Ready?$"\n'
                  'SFMod_gym_1_Defeat::\n    .string "Done.$"\n')
        with self.assertRaises(ValueError): lint_script(source, contract)
        valid = source.replace('SFMod_gym_1_Defeat\n', 'SFMod_gym_1_Defeat, SFMod_gym_1_Won\n')
        self.assertEqual(lint_script(valid, contract), valid)

    def test_enabled_module_gets_guarded_call_without_editing_neighbor_scripts(self):
        self.activate('gym_8')
        modules = load_modules(self.manifest, self.packages)
        plan = next(p for p in generate(self.manifest) if p['world_id']=='gym_8')
        script = script_with_module(map_script(self.manifest, plan), modules['gym_8'])
        self.assertLess(script.index('compare VAR_UNUSED_0x40FC, 1'), script.index('goto SFMod_gym_8_Run'))
        self.assertLess(script.index('setvar VAR_RESULT, 0'), script.index('goto SFMod_gym_8_Run'))
        self.assertLess(script.index('goto_if_ne WB_gym_8_ModuleDone'), script.index('setflag FLAG_BADGE08_GET'))
        reward = script.split('WB_gym_8_ModuleReturn::', 1)[1]
        # A contributor NPC can enter the script directly; core output still
        # requires the incoming badge and crisis checkpoint on every path.
        self.assertLess(reward.index('goto_if_unset FLAG_BADGE07_GET'), reward.index('setflag FLAG_BADGE08_GET'))
        self.assertLess(reward.index('compare VAR_UNUSED_0x40FC, 1'), reward.index('setflag FLAG_BADGE08_GET'))
        for other in generate(self.manifest):
            if other['world_id']=='gym_8': continue
            self.assertNotIn('SFMod_gym_8_', map_script(self.manifest, other))

    def test_room_override_cannot_block_native_arrival_or_exit(self):
        self.activate(); plans = generate(self.manifest)
        room = next(p for p in plans if p['world_id']=='gym_1')
        for x,y in ((16,16),(16,20),(12,10)):
            with self.subTest(position=(x,y)):
                rows = list(room['rows']); row = list(rows[y]); row[x]='#'; rows[y]=''.join(row)
                (self.packages/'gym_1/layout.json').write_text(json.dumps({'rows':rows}))
                with self.assertRaises(ValueError): check(self.packages)

    def test_mission_cannot_override_shared_neighborhood_layout(self):
        self.activate('mission_stadium')
        (self.packages/'mission_stadium/layout.json').write_text(json.dumps({'rows':['.'*32]*24}))
        with self.assertRaises(ValueError): load_modules(self.manifest,self.packages)

    def test_cross_package_team_and_state_allocations_fail(self):
        path=self.packages/'contracts.json'; catalog=json.loads(path.read_text())
        catalog['modules'][1]['trainer_slots']=catalog['modules'][0]['trainer_slots']
        path.write_text(json.dumps(catalog))
        with self.assertRaises(ValueError): load_modules(self.manifest,self.packages)

    def test_external_input_symlink_is_rejected(self):
        path=self.packages/'gym_1/content.inc'; preserved=self.root/'saved.inc';path.rename(preserved)
        path.symlink_to(preserved)
        with self.assertRaises(ValueError): load_modules(self.manifest,self.packages)

    def test_pr_scope_rejects_shared_and_other_package_changes(self):
        self.assertEqual(check_scope('gym_1',['romhack/modules/gym_1/content.inc']),[])
        self.assertEqual(check_scope('gym_1',['romhack/world/world.json','romhack/modules/gym_2/module.json']),
                         ['romhack/modules/gym_2/module.json','romhack/world/world.json'])

    def test_playtest_uses_separate_identity_spawn_and_cold_start_initializer(self):
        self.activate('gym_8'); modules=load_modules(self.manifest,self.packages)
        out=self.root/'generated'; _,content=write_world(self.manifest,out,self.packages)
        fixture=apply_playtest(out,content,modules,'gym_8','ready')
        self.assertFalse(fixture['campaign_evidence']);self.assertEqual(fixture['save_magic'],MAGIC)
        self.assertEqual(content['spawn']['map'],'Route131')
        script=(out/'gym_8.inc').read_text()
        self.assertIn('setflag FLAG_BADGE07_GET',script)
        self.assertIn('setvar VAR_UNUSED_0x40FC, 1',script)
        self.assertIn('givemon SPECIES_MARILL, 100',script)
        self.assertNotIn('setflag FLAG_BADGE08_GET\nSFModuleQA_Ready',script)
        self.assertNotIn('VAR_UNUSED_0x40F8, 22338',(out/'dogpatch.inc').read_text())

    def test_unmet_playtest_does_not_inject_prerequisites(self):
        self.activate('gym_8'); modules=load_modules(self.manifest,self.packages)
        out=self.root/'locked'; _,content=write_world(self.manifest,out,self.packages)
        apply_playtest(out,content,modules,'gym_8','locked')
        script=(out/'gym_8.inc').read_text().split('SFModuleQA_Ready::')[0]
        self.assertNotIn('setflag FLAG_BADGE07_GET',script)
        self.assertNotIn('setvar VAR_UNUSED_0x40FC, 1',script)


if __name__=='__main__': unittest.main()
