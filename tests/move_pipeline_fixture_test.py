"""Guard the bounded move-script fixture, not a simulated battle implementation."""
from copy import deepcopy
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/quality'))
import move_pipeline_fixtures as pipeline
from mechanics_fixtures import GLOBALS

CASE = {'id': 'neutral', 'move': 'MOVE_POUND', 'rng_seed': 0,
        'derivation': 'Base19, no STAB, 99 percent ->18, four RNG draws.',
        'expected': {'attacker_hp': 90, 'defender_hp': 282, 'pp': 9,
                     'defender_status': 0, 'flags': 0, 'rng': 833674724}}


def packet(slot, request, value, size):
    # Native controller ABI: opcode, request, party mask, little-endian payload.
    return {'slot': slot, 'command': 2,
            'header': (bytes([2, request, 0])+value.to_bytes(size,'little')+bytes(4)).hex()[:16]}


class Schema(unittest.TestCase):
    def test_metadata_and_explicit_defaults_cannot_pad_effective_setup_coverage(self):
        syms = {name:(0x02001000+i*4096,size)
                for i,(name,size) in enumerate((GLOBALS|pipeline.ALLOCATIONS).items())}
        labels = {'BattleScript_EffectHit':0x08000100, 'BattleScript_EffectBurnHit':0x08000110}
        constants = {'MOVE_POUND':1, 'TYPE_MYSTERY':9,
                     'BATTLE_TYPE_BATTLE_TOWER':256, 'HITMARKER_OBEYS':0x02000000}
        def resolve(value):
            return value if type(value) is int else constants[value]
        duplicate = deepcopy(CASE)
        duplicate.update(id='different-label', derivation='Different prose.', pp=10,
                         attacker={'type1':9, 'type2':9}, defender={'hp':300, 'max_hp':300})
        duplicate['expected']['defender_hp'] = 283
        with self.assertRaisesRegex(ValueError,'Duplicate effective pipeline setup'):
            pipeline.verify_unique_setups([CASE,duplicate],syms,labels,resolve)
        duplicate['rng_seed'] = 7
        pipeline.verify_unique_setups([CASE,duplicate],syms,labels,resolve)

    def test_catalog_has_explicit_oracles_and_strict_controls(self):
        import json
        document = json.loads((ROOT/'data/quality/mechanics/move-pipeline.json').read_text())
        self.assertTrue(pipeline.validate(document))
        for key,value in [('skip_accuracy',True), ('double',True), ('controller_response',0)]:
            case = deepcopy(CASE);case[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                pipeline.validate({'cases':[case]})

    def test_missing_or_non_native_expectations_cannot_be_inferred(self):
        for key in pipeline.EXPECTED:
            case = deepcopy(CASE);del case['expected'][key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                pipeline.validate({'cases':[case]})
        for key,value in [('rng',2**32), ('flags',256), ('pp',True), ('defender_hp',0)]:
            case = deepcopy(CASE);case['expected'][key] = value
            with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                pipeline.validate({'cases':[case]})

    def test_unreviewed_moves_battler_fields_and_duplicate_ids_are_rejected(self):
        for changes in [{'move':'MOVE_SURF'}, {'defender':{'unused_stat':1}}, {'rng_seed':True}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                pipeline.validate({'cases':[{**deepcopy(CASE),**changes}]})
        with self.assertRaises(ValueError):
            pipeline.validate({'cases':[deepcopy(CASE),deepcopy(CASE)]})


class NativeBoundary(unittest.TestCase):
    def test_controller_payloads_must_match_the_independent_hp_pp_status_oracle(self):
        good = [packet(0,9,9,1),packet(1,42,282,2)]
        self.assertTrue(pipeline.verify_queued_updates(CASE,good))
        for bad in [[packet(0,9,8,1),good[1]], [good[0],packet(1,42,283,2)],
                    [packet(1,9,9,1),good[1]], good[:1]]:
            with self.subTest(packets=bad):
                self.assertFalse(pipeline.verify_queued_updates(CASE,bad))
        burn = deepcopy(CASE);burn['expected']['defender_status'] = 16
        self.assertFalse(pipeline.verify_queued_updates(burn,good))
        self.assertTrue(pipeline.verify_queued_updates(burn,good+[packet(1,40,16,4)]))
        with self.assertRaises(ValueError):
            pipeline.verify_queued_updates(CASE,[packet(0,0,9,1)])

    def test_miss_and_hit_paths_cannot_skip_the_native_script_chain(self):
        hit = [{'opcode':x} for x in [0,1,2,3,4,5,6,7,11,12,21,25]]
        self.assertTrue(pipeline.verify_path(hit,False))
        self.assertFalse(pipeline.verify_path([v for v in hit if v['opcode']!=5],False))
        miss = [{'opcode':x} for x in [0,1,2,3]]
        self.assertTrue(pipeline.verify_path(miss,True))
        self.assertFalse(pipeline.verify_path(miss+[{'opcode':5}],True))

    def exercise_guard(self, controller=0, opcode=None, canary_bad=False, pointer=None):
        syms = {name:(0x02001000+i*4096,1) for i,name in enumerate(
            set(pipeline.ALLOCATIONS)|set(pipeline.FUNCTIONS)|{
                'gRngValue','gBattleMons','gBattlescriptCurrInstr','gBattleControllerExecFlags',
                'gMoveResultFlags','gBattleResources','gBattleStruct','gBattleScripting',
                'gBattleCommunication','gHitMarker','gBattleTypeFlags','gDisableStructs',
                'gSpecialStatuses','gSideStatuses','gCurrMovePos','gBattlerByTurnOrder',
                'gLastUsedAbility','gLastLandedMoves','gLastHitByType'})}
        labels = {'BattleScript_EffectHit':0x08000100,'BattleScript_EffectBurnHit':0x08000110,
                  'BattleScript_MoveEnd':0x08000120,'BattleScript_FaintTarget':0x08000130}
        values = iter([
            ['00000000'],
            ['return 00000000 steps 10',struct.pack('<I',pointer or labels['BattleScript_MoveEnd']).hex(),
             struct.pack('<I',controller).hex()],
            *([[(bytes([opcode])+bytes(7)).hex()]] if opcode is not None else []),
            ['5a00','1a01','09','00000000','00','e4ddb031'],
            [('00'*16 if canary_bad and i==0 else value.hex()) for i,value in enumerate(pipeline.CANARIES.values())]
        ])
        class Transcript:
            def exchange(self, commands, lines):
                if lines==0:return []
                return next(values)
        # This canned transport tests guard handling only; it does not model moves.
        with patch.object(pipeline,'setup',return_value=([], 'BattleScript_EffectHit')):
            return pipeline.run_case(Transcript(),deepcopy(CASE),syms,labels,lambda x:0,bytes(512))

    def test_controller_queries_link_transport_and_ram_script_pointers_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'Unreviewed controller'):
            self.exercise_guard(controller=1,opcode=18)  # CHOOSEACTION needs a real response.
        with self.assertRaisesRegex(ValueError,'LINK transport'):
            self.exercise_guard(controller=16)
        with self.assertRaisesRegex(ValueError,'script region'):
            self.exercise_guard(pointer=0x0203f000)

    def test_scratch_overruns_are_fatal_before_any_pass(self):
        with self.assertRaisesRegex(ValueError,'ABI boundary'):
            self.exercise_guard(canary_bad=True)


if __name__=='__main__':
    unittest.main()
