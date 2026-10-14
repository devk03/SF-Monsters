"""Fail-closed item-effect evidence guards; native ROM runs supply gameplay proof."""
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
import item_effect_fixtures as item
from mechanics_fixtures import GLOBALS

CASE={'id':'potion','derivation':'Potion adds20HP; function returns0 for an effect.',
      'item':'ITEM_POTION','expected':{'return_value':0,'hp':70,'status':0,'pp':[35,30,25,25],
      'battle_hp':50,'battle_status':0,'battle_status2':0,'battle_pp':[35,30,25,25],
      'healing_items':0,'controller_flags':0,'rng':305419896}}
# Recorded fixed native input from the verified reference fixture, not a fake item algorithm.
BEFORE_MON=bytes.fromhex('0000000044332211bbbbbbbbbbbbbbbbbbbb0202bbbbbbbbbbbbbb00df5c0000573322110cdb2311447522114533091173331611672d3b08443322114433221144332211442690b0bbccdd2e443322110000000032ff320069004c0037005c002d003700')


class Schema(unittest.TestCase):
    def test_catalog_has_complete_oracles_and_rejects_missing_observations(self):
        self.assertTrue(item.validate(json.loads((ROOT/'data/quality/mechanics/item-effects.json').read_text())))
        for key in item.EXPECTED:
            c=deepcopy(CASE);del c['expected'][key]
            with self.subTest(key=key),self.assertRaises(ValueError):item.validate({'cases':[c]})

    def test_unreviewed_paths_and_non_native_values_are_rejected(self):
        changes=[{'item':'ITEM_RARE_CANDY'},{'used_by_ai':True},{'bag_consumption':True},
                 {'item':'ITEM_REVIVE','in_battle':True},{'in_battle':1},{'hp':106},
                 {'pp':[36,30,25,25]},{'move_index':4},{'status':True},{'rng_seed':2**32},
                 {'pp_bonus':256},{'healing_items':-1},{'derivation':True}]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError):item.validate({'cases':[{**deepcopy(CASE),**change}]})
        for key,value in [('hp',106),('return_value',True),('rng',-1),('controller_flags',16),('pp',[1,2,3])]:
            c=deepcopy(CASE);c['expected'][key]=value
            with self.subTest(expected=key),self.assertRaises(ValueError):item.validate({'cases':[c]})

    def test_metadata_and_explicit_defaults_cannot_inflate_effective_case_count(self):
        syms={n:(0x02001000+i*4096,s) for i,(n,s) in enumerate((GLOBALS|item.ALLOCATIONS|{f:1 for f in item.FUNCTIONS}).items())}
        names=['NICKNAME','OT_NAME']+['MOVE'+str(i) for i in range(1,5)]+['PP'+str(i) for i in range(1,5)]+['HP','STATUS','PP_BONUSES','MET_LOCATION','MET_LEVEL','MET_GAME','POKEBALL','OT_GENDER']
        props={'MON_DATA_'+n:i for i,n in enumerate(names)}
        resolve=lambda value:value if type(value) is int else {'ITEM_POTION':13,'MOVE_POUND':1}[value]
        other=deepcopy(CASE);other.update(id='padding',derivation='Other wording.',hp=50,status=0,
             pp=[35,30,25,25],pp_bonus=0,move_index=0,in_battle=False,battle_status2=0,healing_items=0,rng_seed=item.SEED)
        other['expected']['hp']=71
        with self.assertRaisesRegex(ValueError,'Duplicate effective'):
            item.unique_programs([CASE,other],syms,resolve,props)
        other['hp']=51
        self.assertEqual(len(item.unique_programs([CASE,other],syms,resolve,props)),2)


class ReceiptBoundary(unittest.TestCase):
    def transcript(self,c=None):
        c=deepcopy(c or CASE)
        battle=bytearray(352);struct.pack_into('<H',battle,40,50);battle[36:40]=bytes([35,30,25,25])
        one,two=item.save_blocks()
        before={'mon':BEFORE_MON,'creation_template':BEFORE_MON,'party_all600':BEFORE_MON+bytes(500),
                'battle_mons':bytes(battle),'save1':one,'save2':two,
                'gBattleResults':bytes(68),'gBattleControllerExecFlags':bytes(4),
                'gBattleBufferA':bytes([165])*2048,'gBattleBufferB':bytes([90])*2048,
                'gMain':bytes(1084),'rng':struct.pack('<I',305419896),
                'gSaveBlock1Ptr':struct.pack('<I',item.SAVE1),'gSaveBlock2Ptr':struct.pack('<I',item.SAVE2),
                'gMapHeader':bytes(28),'gBattlerInMenuId':bytes(1),'gPotentialItemEffectBattler':bytes(1),
                'gActiveBattler':bytes(1),'gPlayerPartyCount':b'\1','gBattlerPartyIndexes':bytes(8),
                'gDisableStructs':bytes(112),'gBattleMoveDamage':bytes(4),'gBattleTypeFlags':bytes(4)}
        after=dict(before);mon=bytearray(BEFORE_MON);struct.pack_into('<H',mon,86,70);after['mon']=bytes(mon)
        after['party_all600']=bytes(mon)+bytes(500)
        if c['expected']['controller_flags']:
            battle=bytearray(after['battle_mons']);struct.pack_into('<H',battle,40,70);after['battle_mons']=bytes(battle)
            results=bytearray(68);results[3]=1;after['gBattleResults']=bytes(results)
            after['gBattleControllerExecFlags']=b'\1\0\0\0'
            after['gBattleBufferA']=bytes(4)+before['gBattleBufferA'][4:]
        events=[('return','effect_return',0)];rows=['return 00000000 steps 100']
        for prefix,state in [('before:',before),('after:',after)]:
            for name,value in state.items():events.append(('read',prefix+name,len(value)));rows.append(value.hex())
        for a,value in item.CANARIES.items():events.append(('read','guard:'+str(a),len(value)));rows.append(value.hex())
        return c,rows,events

    def change(self,rows,events,tag,offset=0):
        index=next(i for i,(_,name,_) in enumerate(events) if name==tag)
        value=bytearray.fromhex(rows[index]);value[offset]^=1;rows[index]=value.hex()

    def test_complete_object_and_every_declared_resource_must_match(self):
        c,rows,events=self.transcript()
        self.assertTrue(item.observe(c,rows,events)['pass'])
        for tag,offset in [('after:mon',8),('after:mon',32),('after:mon',86),
                           ('after:party_all600',599),('after:creation_template',8),
                           ('after:battle_mons',0),('after:battle_mons',40),('after:battle_mons',351),
                           ('after:save1',0x562),('after:save2',10),('after:gMain',0),
                           ('after:gBattleBufferA',2047),('after:gBattleBufferB',0),
                           ('after:gBattleResults',4),('after:rng',0)]:
            c,rows,events=self.transcript();self.change(rows,events,tag,offset)
            with self.subTest(tag=tag,offset=offset):self.assertFalse(item.observe(c,rows,events)['pass'])

    def test_no_effect_return_is_not_accepted_as_a_successful_potion(self):
        c,rows,events=self.transcript();rows[0]='return 00000001 steps 100'
        self.assertFalse(item.observe(c,rows,events)['pass'])

    def test_native_healing_query_remains_pending_without_a_fabricated_response(self):
        c=deepcopy(CASE);c['in_battle']=True
        c['expected'].update(battle_hp=70,healing_items=1,controller_flags=1)
        c,rows,events=self.transcript(c);got=item.observe(c,rows,events)
        self.assertTrue(got['pass'])
        self.assertEqual(got['pending_controller_request'],{'command':0,'request':0,'party_mask':0,'answered':False})
        for tag in ('after:gBattleControllerExecFlags','after:gBattleBufferA'):
            c,rows,events=self.transcript(c);self.change(rows,events,tag)
            with self.subTest(tag=tag):self.assertFalse(item.observe(c,rows,events)['pass'])

    def test_setup_must_match_the_independent_whole_object_and_seed(self):
        for tag in ('before:mon','before:rng'):
            c,rows,events=self.transcript();self.change(rows,events,tag)
            with self.subTest(tag=tag),self.assertRaisesRegex(ValueError,'setup disagrees'):
                item.observe(c,rows,events)

    def test_native_overruns_missing_or_truncated_reads_and_bad_returns_reject(self):
        c,rows,events=self.transcript();self.change(rows,events,'guard:'+str(item.MON+100))
        with self.assertRaisesRegex(ValueError,'ABI boundary'):item.observe(c,rows,events)
        c,rows,events=self.transcript()
        with self.assertRaisesRegex(ValueError,'Incomplete'):item.observe(c,rows[:-1],events)
        rows[1]='00'
        with self.assertRaisesRegex(ValueError,'truncated'):item.observe(c,rows,events)
        c,rows,events=self.transcript();rows[0]='timeout'
        with self.assertRaisesRegex(ValueError,'did not return'):item.observe(c,rows,events)
        c,rows,events=self.transcript()
        index=next(i for i,(_,tag,_) in enumerate(events) if tag=='after:save1')
        del rows[index];del events[index]
        with self.assertRaisesRegex(ValueError,'Incomplete declared'):item.observe(c,rows,events)


if __name__=='__main__':unittest.main()
