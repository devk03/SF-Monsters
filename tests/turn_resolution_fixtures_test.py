"""Protect turn-fixture oracles and fail-closed native transport boundaries.

These unit transcripts test guards only. They do not simulate a battle or count
as native mechanics evidence; the separate paired ROM runs provide that proof.
"""
from copy import deepcopy
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
import turn_resolution_fixtures as turn
from item_effect_fixtures import expected_mon


class Transcript:
    def __init__(self,rows):self.rows=list(rows);self.commands=[]
    def exchange(self,commands,lines):
        self.commands.extend(commands)
        if not lines:return []
        if not self.rows:raise AssertionError('Unexpected transport response request.')
        result=self.rows.pop(0)
        if len(result)!=lines:raise AssertionError('Wrong requested response width.')
        return result


SYMS={'gBattleControllerExecFlags':(0x02000100,4),'gBattleBufferA':(0x02001000,2048),
      'gActiveBattler':(0x02000200,1),'PlayerHandleSetMonData':(0x08000100,32),
      'OpponentHandleSetMonData':(0x08000200,32),
      'RunTurnActionsFunctions':(0x08000300,32)}


def priority_mon(hp,pp):
    """Independent encrypted delta for Pound1 -> QuickAttack98 at fixed PID0.

    Attack substructure starts at44. XOR encryption changes only encrypted low
    word by1^98=99, and the plain checksum increases by98-1=97.
    """
    result=bytearray(expected_mon(hp,0,pp,0))
    result[44]^=99
    struct.pack_into('<H',result,28,(int.from_bytes(result[28:30],'little')+97)&0xffff)
    return bytes(result)


def tackle_mon(hp,pp):
    # Independent1->33 delta: encrypted low byte XOR32, plain checksum+32.
    result=bytearray(expected_mon(hp,0,pp,0));result[44]^=32
    struct.pack_into('<H',result,28,(int.from_bytes(result[28:30],'little')+32)&0xffff)
    return bytes(result)


def observation(c):
    """Independently specified terminal snapshots, not a move implementation."""
    ko=c['endpoint']=='replacement-query'
    priority=c['id']=='slower-player-priority'
    miss=c['id']=='player-first-miss-reply'
    immune=c['id']=='normal-ghost-immunity-reply'
    old0=tackle_mon(90,[10,30,25,25]) if miss else priority_mon(90,[10,30,25,25]) if priority else expected_mon(18 if ko else 90,0,[10,30,25,25],0)
    old1=expected_mon(90,0,[10,30,25,25],0)
    bench=expected_mon(105,0,[10,30,25,25],0)
    initial=bytearray(352)
    for i,hp in enumerate([18 if ko else 90,90,0,0]):
        struct.pack_into('<H',initial,i*88,19)
        struct.pack_into('<H',initial,i*88+40,hp)
        struct.pack_into('<H',initial,i*88+12,33 if miss and i==0 else 98 if priority and i==0 else 1)
        initial[i*88+36]=10;initial[i*88+33:i*88+35]=bytes([9,9])
    if immune:initial[121:123]=bytes([7,7])
    state={'before':[old0+bench+bytes(400),old1+bytes(500),bytes([0x17])*0x3d88,bytes([0x28])*0xf2c],
           'initial_battle_mons':bytes(initial),'save_addresses':[0x02025000,0x0202a000]}
    after=bytearray(initial)
    for i,hp in enumerate([0,90] if ko else [72,90] if miss or immune else [72,72]):struct.pack_into('<H',after,i*88+40,hp)
    after[36]=10 if ko else 9;after[88+36]=9
    if ko:after[33:35]=bytes(2)
    results=bytearray(68);results[5]=1;struct.pack_into('<H',results,36,1)
    if ko:results[0]=1;results[2]=1
    else:results[19]=1;struct.pack_into('<H',results,34,33 if miss else 98 if priority else 1)
    packets=([{'slot':1,'packet':'0209000900000000'}, {'slot':0,'packet':'022a000000000000'},
              {'slot':0,'packet':'0228000000000000'}, {'slot':0,'packet':'1601000000000000'},
              {'slot':1,'packet':'3502000000000000','pending':True}] if ko else
             [{'slot':0,'packet':'0209000900000000'}, {'slot':1,'packet':'022a004800000000'},
              {'slot':1,'packet':'0209000900000000'}, {'slot':0,'packet':'022a004800000000'}])
    if miss or immune:packets=[{'slot':0,'packet':'0209000900000000'},{'slot':1,'packet':'0209000900000000'},{'slot':0,'packet':'022a004800000000'}]
    raw=[(tackle_mon(72,[9,30,25,25]) if miss else priority_mon(72,[9,30,25,25]) if priority else expected_mon(0 if ko else 72,0,[10 if ko else 9,30,25,25],0))+bench+bytes(400),
         expected_mon(90 if ko or miss or immune else 72,0,[9,30,25,25],0)+bytes(500),bytes(after),
         state['before'][2],state['before'][3],bytes(results),struct.pack('<I',833674724 if ko else 3063870748 if miss else 4231221723),
         b'\0',b'\0',b'\1' if ko else b'\0',bytes(4) if ko else bytes.fromhex('ffff0000'),
         bytes.fromhex('0100010000000000') if ko else bytes(8),struct.pack('<I',3 if ko else 0),
         struct.pack('<I',264),*[struct.pack('<I',a) for a in state['save_addresses']],b'\2',b'\1',
         bytes([1,0] if ko else [0,1]),struct.pack('<I',0x08000301)]
    trace=([{'opcode':3,'attacker':1},{'opcode':73,'attacker':1}] if ko else
           [{'opcode':3,'attacker':0},{'opcode':73,'attacker':0},
            {'opcode':3,'attacker':1},{'opcode':73,'attacker':1}])
    if miss:trace=[{'opcode':op,'attacker':side} for side,ops in [(0,[1,3,73]),(1,[1,3,4,5,12,73])] for op in ops]
    if immune:trace=[{'opcode':op,'attacker':side} for side in (0,1) for op in (1,3,4,5,6,7,11,12,0x15,73)]
    return state,raw,packets,trace


class TurnSchema(unittest.TestCase):
    def test_three_oracles_have_independent_damage_rng_and_priority_derivations(self):
        turn.validate_cases(turn.CASES)
        state=0;draws=[]
        for _ in range(9):state=(state*0x41c64e6d+0x6073)&0xffffffff;draws.append((state,state>>16))
        base=((22*40*100//100)//50)+2
        self.assertEqual(base,19)
        self.assertEqual([base*(100-draws[i][1]%16)//100 for i in (2,6)],[18,18])
        self.assertEqual(draws[3][0],turn.CASES[1]['expected_rng'])
        self.assertEqual(draws[8][0],turn.CASES[0]['expected_rng'])
        self.assertEqual(turn.CASES[0]['expected_hp'],[72,72])
        self.assertEqual(turn.CASES[1]['expected_pp'],[10,9])
        priority=turn.CASES[2]
        self.assertEqual(priority['moves'],[98,1])
        self.assertEqual(priority['speeds'],[90,110])
        self.assertEqual(priority['expected_order'],[0,1])
        self.assertEqual(priority['expected_rng'],draws[8][0])
        self.assertEqual(priority['expected_hp'],[72,72])
        self.assertEqual(priority['expected_pp'],[9,9])

    def test_unknown_controls_incomplete_oracles_and_duplicate_effective_setups_fail(self):
        for change in [{'skip_controller':True},{'expected_rng':True},{'player_hp':106},
                       {'speeds':[90,90]},{'derivation':''},{'expected_hp':[0,72]},
                       {'expected_updates':[[0,99,9]]},{'moves':[True,1]},{'moves':[98,98]},
                       {'moves':[1]},{'types':[[9,9],[True,7]]},{'types':[[9,9],[7]]},
                       {'types':[[9,9],[7,9]]},{'types':[[7,7],[9,9]]},{'types':[[9,9],[18,18]]},
                       {'types':[[9,9],(9,9)]},{'rng_seed':True},{'rng_seed':-1},{'rng_seed':0x100000000},{'expected_order':[1,0]},{'expected_order':[0,True]}]:
            c=deepcopy(turn.CASES[0]);c.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):turn.validate_cases([c])
        for key in turn.CASES[0]:
            c=deepcopy(turn.CASES[0]);del c[key]
            with self.subTest(missing=key),self.assertRaises(ValueError):turn.validate_cases([c])
        duplicate=deepcopy(turn.CASES[0]);duplicate.update(id='different-label',derivation='Other prose.',expected_rng=1)
        with self.assertRaisesRegex(ValueError,'effective'):turn.validate_cases([turn.CASES[0],duplicate])
        with self.assertRaises(ValueError):turn.call({'f':(0x08000000,4)},'f',*range(9))

    def test_priority_secure_moves_and_checksum_are_independent_of_observed_native_objects(self):
        for hp,pp in [(90,[10,30,25,25]),(72,[9,30,25,25])]:
            self.assertEqual(turn.expected_turn_mon(hp,pp,98),priority_mon(hp,pp))
            self.assertEqual(turn.expected_turn_mon(hp,pp,1),expected_mon(hp,0,pp,0))
        # The same speeds and HP as the KO setup remain distinct with a new move.
        priority=deepcopy(turn.CASES[2]);priority.update(player_hp=18)
        turn.validate_cases([turn.CASES[1],priority])

    def test_first_miss_draws_and_secure_move_bytes_are_derived_independently(self):
        c=turn.CASES[3];state=30;draws=[]
        for _ in range(6):state=(state*0x41c64e6d+0x6073)&0xffffffff;draws.append(state>>16)
        self.assertEqual(c['rng_seed'],30)
        self.assertEqual(draws,[46397,47244,24877,5747,11048,46750])
        self.assertEqual(draws[0]%100+1,98);self.assertGreater(98,95)
        self.assertLessEqual(draws[1]%100+1,100);self.assertNotEqual(draws[2]%16,0)
        self.assertEqual(19*(100-draws[3]%16)//100,18)
        self.assertEqual(c['expected_rng'],state)
        self.assertEqual(c['expected_hp'],[72,90]);self.assertEqual(c['expected_pp'],[9,9])
        self.assertEqual(c['expected_updates'],[[0,9,9],[1,9,9],[0,42,72]])
        for hp,pp in [(90,[10,30,25,25]),(72,[9,30,25,25])]:
            self.assertEqual(turn.expected_turn_mon(hp,pp,33),tackle_mon(hp,pp))

    def test_immunity_keeps_nine_draws_and_is_a_distinct_battle_only_type_setup(self):
        c=turn.CASES[4];state=0;draws=[]
        for _ in range(9):state=(state*0x41c64e6d+0x6073)&0xffffffff;draws.append(state>>16)
        self.assertEqual(c['types'],[[9,9],[7,7]])
        self.assertTrue(all(case['types']==[[9,9],[9,9]] for case in turn.CASES[:4]))
        self.assertEqual(c['moves'],[1,1]);self.assertEqual(c['expected_order'],[0,1])
        self.assertEqual(draws,[0,59774,21105,12720,36418,58060,44997,26587,64563])
        self.assertNotEqual(draws[1]%16,0);self.assertNotEqual(draws[5]%16,0)
        self.assertEqual(0*(100-draws[2]%16)//100,0)
        self.assertEqual(19*(100-draws[6]%16)//100,18)
        self.assertEqual(c['expected_rng'],state)
        self.assertEqual(c['expected_hp'],[72,90]);self.assertEqual(c['expected_pp'],[9,9])
        self.assertEqual(c['expected_updates'],[[0,9,9],[1,9,9],[0,42,72]])
        # SameHP/speeds/moves/seed as living-two-hits, independently distinct types.
        turn.validate_cases([turn.CASES[0],c])
        state,raw,_,_=observation(c)
        self.assertEqual(raw[2][121:123],bytes([7,7]))
        self.assertEqual(raw[0],expected_mon(72,0,[9,30,25,25],0)+state['before'][0][100:])
        self.assertEqual(raw[1],expected_mon(90,0,[9,30,25,25],0)+state['before'][1][100:])


class NativeControllerBoundary(unittest.TestCase):
    def test_setmondata_uses_actual_native_setter_and_never_transport_clears_it(self):
        for slot,name in [(0,'PlayerHandleSetMonData'),(1,'OpponentHandleSetMonData')]:
            d=Transcript([[struct.pack('<I',1<<slot).hex()],['0209000900000000'],
                          ['return 00000000 steps 12'],['00000000']])
            self.assertIsNone(turn.service_controllers(d,SYMS,turn.CASES[0],[]))
            self.assertFalse(d.rows)
            self.assertTrue(any(v.startswith('call %x'%SYMS[name][0]) for v in d.commands))
            self.assertFalse(any(v.startswith('write 2000100 ') for v in d.commands))

    def test_missing_native_completion_wrong_slot_requests_and_masks_fail(self):
        d=Transcript([['01000000'],['0209000900000000'],['return 00000000 steps 12'],['01000000']])
        with self.assertRaisesRegex(ValueError,'own controller'):turn.service_controllers(d,SYMS,turn.CASES[0],[])
        for rows in [[['04000000']], [['01000000'],['0209010900000000']],
                     [['01000000'],['0200000900000000']], [['01000000'],['1200000000000000']]]:
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                turn.service_controllers(Transcript(rows),SYMS,turn.CASES[0],[])

    def test_replacement_query_and_opponent_standby_remain_unanswered(self):
        rows=[['03000000'],['1601000000000000'],['3502000000000000']]
        d=Transcript(rows);log=[]
        self.assertEqual(turn.service_controllers(d,SYMS,turn.CASES[1],log),'replacement-query')
        self.assertFalse(any(v.startswith(('write ','call ')) for v in d.commands))
        self.assertEqual(len(log),2)
        for altered in [[['01000000'],['1601000000000000']],
                        [['03000000'],['1600000000000000']],
                        [['03000000'],['1601000000000000'],['3501000000000000']]]:
            with self.subTest(rows=altered),self.assertRaises(ValueError):
                turn.service_controllers(Transcript(altered),SYMS,turn.CASES[1],[])
        with self.assertRaises(ValueError):turn.service_controllers(Transcript(rows),SYMS,turn.CASES[0],[])

    def test_truncated_reads_and_instruction_exhaustion_are_fatal(self):
        for value in ('','00','zzzzzzzz'):
            with self.subTest(value=value),self.assertRaises(ValueError):turn.read(Transcript([[value]]),[(0x02000000,4)])
        for returned in ('return 00000000 steps 2000000','return 00000000 steps 0','garbage'):
            with self.assertRaises(ValueError):turn.invoke(Transcript([[returned]]),{'f':(0x08000000,4)},'f')

    def test_callbacks_ram_scripts_and_internal_choice_commands_fail_closed(self):
        syms={name:(0x08000100+i*16,16) for i,name in enumerate(sorted(turn.CALLBACKS))}
        rom=bytearray(1024)
        name='RunBattleScriptCommands'
        for main,pointer in [(0x080003ff,0x08000000),(syms[name][0]|1,0x02000000),
                             (syms[name][0]|1,0x08000400)]:
            with self.subTest(main=main,pointer=pointer),self.assertRaises(ValueError):
                turn.dispatch(main,pointer,10,syms,rom)
        for opcode in (0x5a,0x5b,0x67):
            rom[0]=opcode
            with self.assertRaisesRegex(ValueError,'choice'):turn.dispatch(syms[name][0]|1,0x08000000,10,syms,rom)
        # A new action initializes its script itself; an old NULL cursor must
        # not be mistaken for an interpreter dereference at that point.
        self.assertEqual(turn.dispatch(syms['RunTurnActionsFunctions'][0]|1,0,0,syms,rom),
                         ('RunTurnActionsFunctions',None))

    def test_finite_dispatch_and_wall_clock_limits_stop_before_unbounded_work(self):
        syms={'SetActionsAndBattlersTurnOrder':(0x08000100,16),'HandleTurnActionSelectionState':(0x08000200,16)}
        with patch.object(turn,'setup',return_value={}),patch.object(turn,'invoke'),\
             patch.object(turn,'MAX_DISPATCHES',0):
            with self.assertRaisesRegex(ValueError,'dispatch limit'):
                turn.run_case(Transcript([]),turn.CASES[0],syms,lambda v:0,{},bytes(1024))
        with patch.object(turn,'setup',return_value={}),patch.object(turn,'invoke'),\
             patch.object(turn.time,'monotonic',side_effect=[0,2]),patch.object(turn,'CASE_SECONDS',1):
            with self.assertRaisesRegex(ValueError,'deadline'):
                turn.run_case(Transcript([]),turn.CASES[0],syms,lambda v:0,{},bytes(1024))


class TerminalOracles(unittest.TestCase):
    def assess(self,c,raw=None,guards=None,packets=None,trace=None):
        state,base,basepackets,basetrace=observation(c)
        return turn.assess(c,state,base if raw is None else raw,
            list(turn.CANARIES.values()) if guards is None else guards,
            basepackets if packets is None else packets,SYMS,lambda v:255,c['endpoint'],
            basetrace if trace is None else trace)

    def test_living_turn_and_partial_ko_boundary_have_distinct_complete_oracles(self):
        for c in turn.CASES:self.assertTrue(self.assess(c)['passed'])

    def test_changed_secure_bytes_nonparticipants_saves_counts_stacks_and_rng_cannot_pass(self):
        c=turn.CASES[0]
        for index,offset in [(0,28),(0,120),(1,500),(2,200),(3,4),(4,8),(5,3),
                             (6,0),(7,0),(8,0),(10,0),(11,0),(12,0),(13,0),
                             (14,0),(15,0),(16,0),(17,0),(18,0)]:
            raw=observation(c)[1];b=bytearray(raw[index]);b[offset]^=1;raw[index]=bytes(b)
            with self.subTest(index=index,offset=offset):self.assertFalse(self.assess(c,raw=raw)['passed'])
        guards=list(turn.CANARIES.values());guards[0]=bytes(16)
        self.assertFalse(self.assess(c,guards=guards)['passed'])
        with self.assertRaises(ValueError):self.assess(c,raw=observation(c)[1][:-1])

    def test_priority_cannot_pass_with_speed_order_or_pound_secure_bytes(self):
        c=turn.CASES[2]
        raw=observation(c)[1];raw[18]=bytes([1,0])
        self.assertFalse(self.assess(c,raw=raw)['checks']['ordered_actions'])
        raw=observation(c)[1];raw[0]=observation(turn.CASES[0])[1][0]
        self.assertFalse(self.assess(c,raw=raw)['checks']['full_parties'])
        raw=observation(c)[1];changed=bytearray(raw[5]);changed[34]=1;raw[5]=bytes(changed)
        self.assertFalse(self.assess(c,raw=raw)['checks']['full_battle_results'])
        _,_,_,trace=observation(c)
        trace=[dict(row,attacker=1-row['attacker']) for row in trace]
        self.assertFalse(self.assess(c,trace=trace)['checks']['executed_pp_order'])

    def test_miss_cannot_hide_enemy_hp_write_second_action_or_wrong_rng(self):
        c=turn.CASES[3];_,_,packets,trace=observation(c)
        for corrupted in (packets+[{'slot':1,'packet':'022a004800000000'}],packets[:-1]):
            self.assertFalse(self.assess(c,packets=corrupted)['passed'])
        raw=observation(c)[1];raw[6]=struct.pack('<I',4231221723)
        self.assertFalse(self.assess(c,raw=raw)['checks']['rng'])
        raw=observation(c)[1];changed=bytearray(raw[2]);struct.pack_into('<H',changed,128,72);raw[2]=bytes(changed)
        self.assertFalse(self.assess(c,raw=raw)['checks']['full_battle_mons'])
        for corrupted in (trace[:3],trace+[{'opcode':4,'attacker':0}],
                          [row for row in trace if not(row['opcode']==73 and row['attacker']==0)]):
            self.assertFalse(self.assess(c,trace=corrupted)['checks']['first_miss_then_reply_path'])

    def test_immunity_requires_damage_path_intact_ghost_types_and_no_enemy_hp_packet(self):
        c=turn.CASES[4];_,_,packets,trace=observation(c)
        for opcode in (1,3,4,5,6,7,11,12,0x15,73):
            altered=[row for row in trace if not(row['attacker']==0 and row['opcode']==opcode)]
            with self.subTest(opcode=opcode):self.assertFalse(self.assess(c,trace=altered)['passed'])
        altered=trace.copy();altered[3],altered[4]=altered[4],altered[3]
        self.assertFalse(self.assess(c,trace=altered)['checks']['immune_path_then_reply'])
        self.assertFalse(self.assess(c,trace=trace[:10])['passed'])
        self.assertFalse(self.assess(c,packets=packets+[{'slot':1,'packet':'022a005a00000000'}])['checks']['immune_path_then_reply'])
        raw=observation(c)[1];changed=bytearray(raw[2]);changed[121:123]=bytes([9,9]);raw[2]=bytes(changed)
        self.assertFalse(self.assess(c,raw=raw)['checks']['full_battle_mons'])
        raw=observation(c)[1];raw[6]=struct.pack('<I',3063870748)
        self.assertFalse(self.assess(c,raw=raw)['checks']['rng'])

    def test_dropped_second_action_wrong_packet_and_skipped_moveend_cannot_pass(self):
        c=turn.CASES[0];_,_,packets,trace=observation(c)
        self.assertFalse(self.assess(c,packets=packets[:-1])['passed'])
        self.assertFalse(self.assess(c,trace=trace[:2])['passed'])
        self.assertFalse(self.assess(c,trace=[r for r in trace if r['opcode']!=73])['passed'])
        for index in (12,19):
            raw=observation(turn.CASES[1])[1];raw[index]=bytes(4)
            self.assertFalse(self.assess(turn.CASES[1],raw=raw)['passed'])
        # Restoring Mystery types after faint would hide native cleanup behavior.
        raw=observation(turn.CASES[1])[1];b=bytearray(raw[2]);b[33:35]=bytes([9,9]);raw[2]=bytes(b)
        self.assertFalse(self.assess(turn.CASES[1],raw=raw)['passed'])


if __name__=='__main__':unittest.main()
