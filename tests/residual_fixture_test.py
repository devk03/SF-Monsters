"""Protect residual evidence boundaries; native gameplay is checked by ROM fixtures."""
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
import residual_fixtures as residual
from mechanics_fixtures import GLOBALS

CASE = {'id':'rooted-full','derivation':'Full HP prevents an Ingrain healing event.',
        'status3':[1024,0], 'expected':{'hp':[90,90],'status':[0,0],'status3':[1024,0],
        'weather':0,'duration':0,'reflect_timer':0,'side_statuses':[0,0],'rng':0,
        'effects':[],'selected_damage':[],'hp_updates':[]}}


def symbols():
    return {name:(0x02001000+i*4096,size) for i,(name,size) in
            enumerate((GLOBALS|residual.ALLOCATIONS|{v:1 for v in residual.FUNCTIONS}).items())}


def resolve(value):
    return value if type(value) is int else {'MOVE_POUND':1,'TYPE_MYSTERY':9,
        'BATTLE_TYPE_BATTLE_TOWER':256,'HITMARKER_OBEYS':0x02000000}[value]


class Schema(unittest.TestCase):
    def test_catalog_requires_explicit_native_oracles(self):
        self.assertTrue(residual.validate(json.loads((ROOT/'data/quality/mechanics/residual.json').read_text())))
        for key in residual.FIELDS:
            c=deepcopy(CASE); del c['expected'][key]
            with self.subTest(missing=key),self.assertRaises(ValueError):
                residual.validate({'cases':[c]})

    def test_unsupported_controls_and_fainting_are_rejected(self):
        changes = [{'skip_script':True},{'double':True},{'attacker':{'speed':200}},
                   {'weather':8,'duration':0},{'status3':[True,0]}, {'rng_seed':2**32},
                   {'attacker':{'hp':0}}, {'attacker':{'hp':91}}, {'derivation':True}]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError):
                residual.validate({'cases':[{**deepcopy(CASE),**change}]})
        for key,value in [('hp',[0,90]),('status',[0,2**32]),('hp_updates',[[2,90]]),
                          ('selected_damage',[True]),('effects',['BattleScript_MoveEnd'])]:
            c=deepcopy(CASE);c['expected'][key]=value
            with self.subTest(oracle=key),self.assertRaises(ValueError):residual.validate({'cases':[c]})

    def test_duplicate_effective_setups_ignore_labels_oracles_and_explicit_defaults(self):
        labels={'BattleScript_EffectHit':0x08000100}
        c=deepcopy(CASE)
        c.update(id='another-label',derivation='Other prose.',attacker={'hp':90,'max_hp':90},
                 defender={'hp':90,'max_hp':90},rng_seed=0,weather=0,duration=0,reflect_timer=0)
        c['expected']['hp']=[89,90]
        with self.assertRaisesRegex(ValueError,'Duplicate effective'):
            residual.verify_unique_setups([CASE,c],symbols(),labels,resolve)
        c['status3']=[0,0]
        residual.verify_unique_setups([CASE,c],symbols(),labels,resolve)


class TransportBoundary(unittest.TestCase):
    def test_queries_link_transport_and_other_mon_writes_cannot_be_acknowledged(self):
        class Packet:
            def __init__(self,packet):self.packet=packet;self.cleared=False
            def exchange(self,commands,lines):
                if lines:return [self.packet.hex()]
                self.cleared=True;return []
        for flags,packet in [(16,bytes(8)),(1,bytes([18])+bytes(7)),
                             (1,bytes([2,40])+bytes(6)),(1,bytes([2,42,1])+bytes(5))]:
            driver=Packet(packet)
            with self.subTest(flags=flags,packet=packet.hex()),self.assertRaises(ValueError):
                residual.acknowledge(driver,symbols(),flags,[])
            self.assertFalse(driver.cleared)
        driver=Packet(bytes([2,42,0,79,0,0,0,0]));acks=[]
        residual.acknowledge(driver,symbols(),1,acks)
        self.assertTrue(driver.cleared)
        self.assertEqual(acks,[{'slot':0,'command':2,'header':'022a004f00000000'}])

    def exercise_completion(self,*,outcome=0,order=b'\0\1',stacks=None,bad_canary=False):
        syms=symbols();callback=syms['BattleTurnPassed'][0]|1
        word=lambda n:struct.pack('<I',n).hex()
        # Canned transport proves fail-closed receipt handling; it models no effects.
        final=['5a00','5a00','00000000','00000000','00040000','00000000',
               '0000','00','00','00000000','00000000',bytes([outcome]).hex(),order.hex()]
        guards=[v.hex() for v in residual.CANARIES.values()]
        if bad_canary:guards[-1]='00'*16
        rows=iter([
            ['return 00000000 steps 1','return 00000000 steps 1','00000000'],
            ['return 00000000 steps 1'],[word(0x08000100),word(callback),word(0)],
            ['return 00000000 steps 1'],[word(0x08000100),word(callback),word(0)],
            final,guards,stacks or ['00','00','0002','0a']])
        class Transcript:
            def exchange(self,commands,lines):return next(rows)
        with patch.object(residual,'setup',return_value=[]):
            return residual.run_case(Transcript(),deepcopy(CASE),syms,{},resolve,bytes(512))

    def test_completion_requires_empty_stacks_complete_trackers_order_and_no_outcome(self):
        self.assertTrue(self.exercise_completion()['pass'])
        for changes in [{'outcome':1},{'order':b'\1\0'},
                        {'stacks':['01','00','0002','0a']},
                        {'stacks':['00','00','0001','0a']},
                        {'stacks':['00','00','0002','09']}]:
            with self.subTest(changes=changes),self.assertRaisesRegex(ValueError,'finish cleanly'):
                self.exercise_completion(**changes)

    def test_canary_corruption_cannot_be_a_passing_receipt(self):
        with self.assertRaisesRegex(ValueError,'ABI boundary'):
            self.exercise_completion(bad_canary=True)

    def test_effect_cannot_dispatch_an_unreviewed_callback(self):
        syms=symbols();word=lambda v:struct.pack('<I',v).hex()
        labels={name:0x08000100 for name in residual.SCRIPTS}
        labels.update(BattleScript_FaintTarget=0x08000120,BattleScript_FaintAttacker=0x08000130)
        rows=iter([
            ['return 00000000 steps 1','return 00000000 steps 1','00000000'],
            ['return 00000001 steps 1'],
            [word(0x08000100),word(syms['RunBattleScriptCommands_PopCallbacksStack'][0]|1),word(0)],
            ['return 00000000 steps 1'],[word(0x08000100),word(0x08001001),word(0)]])
        class Transcript:
            def exchange(self,commands,lines):return next(rows)
        with patch.object(residual,'setup',return_value=[]),self.assertRaisesRegex(ValueError,'unreviewed callback'):
            residual.run_case(Transcript(),deepcopy(CASE),syms,labels,resolve,bytes(512))

    def test_truncated_native_reads_and_nonreturning_calls_are_rejected(self):
        class Short:
            def exchange(self,commands,lines):return ['00']
        with self.assertRaisesRegex(ValueError,'Incomplete'):residual.read(Short(),[(0x02000000,4)])
        with self.assertRaisesRegex(ValueError,'call failed'):residual.returned('timeout')


if __name__=='__main__':unittest.main()
