"""Controlled native field/battler end-turn phases plus selected effect scripts.

No move actions, full battle turn, controller presentation or durable save proof.
"""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
import time
from mechanics_fixtures import ROOT, build_driver, constants, digest, verify_bundle
from move_pipeline_fixtures import (setup as script_setup, rom_symbols,
                                   ALLOCATIONS as SCRIPT_ALLOCATIONS,
                                   CANARIES as SCRIPT_CANARIES)
from native_fixture_transport import Driver, writes
from native_abi import verify_native_layout

FUNCTIONS = {'DoFieldEndTurnEffects', 'DoBattlerEndTurnEffects', 'BattleScriptExecute',
             'RunBattleScriptCommands_PopCallbacksStack', 'BattleTurnPassed',
             'Cmd_datahpupdate', 'Cmd_end2', 'Cmd_weatherdamage', 'Cmd_checkteamslost',
             'ItemBattleEffects', 'AbilityBattleEffects', 'CreateMon'}
ALLOCATIONS = {**SCRIPT_ALLOCATIONS, 'gSideTimers':24, 'gWishFutureKnock':44,
               'gCurrentActionFuncId':1, 'gPlayerParty':600, 'gEnemyParty':600,
               'gPlayerPartyCount':1, 'gEnemyPartyCount':1, 'gBattlerPartyIndexes':8,
               'gLastUsedItem':2}
CALLBACKS = 0x0203f840
CANARIES = {**SCRIPT_CANARIES, CALLBACKS+36:bytes([0x96])*16}
FIELDS = {'hp', 'status', 'status3', 'weather', 'duration', 'reflect_timer',
          'side_statuses', 'rng', 'effects', 'selected_damage', 'hp_updates'}
BATTLER_FIELDS = {'hp', 'max_hp', 'status', 'item', 'ability', 'type1', 'type2'}
SCRIPTS = {'BattleScript_PoisonTurnDmg', 'BattleScript_BurnTurnDmg',
           'BattleScript_IngrainTurnHeal', 'BattleScript_ItemHealHP_End2',
           'BattleScript_LeechSeedTurnDrain', 'BattleScript_RainContinuesOrEnds',
           'BattleScript_DamagingWeatherContinues', 'BattleScript_SandStormHailEnds',
           'BattleScript_SunlightContinues', 'BattleScript_SunlightFaded',
           'BattleScript_SideStatusWoreOff'}
# Only reviewed writes and presentation commands. Never answer a controller query.
ACK_COMMANDS = {2, 16, 24, 27, 41, 43, 52}
ABI = [676, 0, 1, 3, 219, 32, 12, 36, 32, 36, 84, 12, 44, 40, 88, 40, 76, 40]
LAYOUT = ('sizeof(struct BattleStruct)', 'offsetof(struct BattleStruct, turnEffectsTracker)',
          'offsetof(struct BattleStruct, turnEffectsBattlerId)', 'offsetof(struct BattleStruct, turnCountersTracker)',
          'offsetof(struct BattleStruct, turnSideTracker)', 'sizeof(struct BattleResources)',
          'offsetof(struct BattleResources, battleCallbackStack)', 'sizeof(struct BattleCallbacksStack)',
          'offsetof(struct BattleCallbacksStack, size)', 'sizeof(struct BattleScriptsStack)',
          'sizeof(struct BattleHistory)', 'sizeof(struct SideTimer)', 'sizeof(struct WishFutureKnock)',
          'offsetof(struct WishFutureKnock, weatherDuration)', 'sizeof(struct BattlePokemon)',
          'offsetof(struct BattlePokemon, hp)', 'offsetof(struct BattlePokemon, status1)',
          'sizeof(struct BattleScripting)')


def integer(value, maximum):
    return type(value) is int and 0 <= value <= maximum


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases,list) or not 1 <= len(cases) <= 32:
        raise ValueError('Use 1–32 independent residual cases.')
    ids = set()
    for c in cases:
        if not isinstance(c,dict) or set(c)-{'id','derivation','attacker','defender','status3',
                'weather','duration','reflect_timer','rng_seed','expected'}:
            raise ValueError('Unknown residual control.')
        if not isinstance(c.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',c['id']) or c['id'] in ids or not isinstance(c.get('derivation'),str) or not c['derivation'].strip():
            raise ValueError('Require unique IDs and independent derivations.')
        ids.add(c['id'])
        for slot in ('attacker','defender'):
            mon = c.get(slot,{})
            if not isinstance(mon,dict) or set(mon)-BATTLER_FIELDS:
                raise ValueError('Unsupported residual battler control.')
            if not integer(mon.get('hp',90),65535) or not integer(mon.get('max_hp',90),65535) or not 0 < mon.get('hp',90) <= mon.get('max_hp',90):
                raise ValueError('Use living battlers with valid native HP.')
        for key,limit in [('weather',127),('duration',255),('reflect_timer',255),('rng_seed',0xffffffff)]:
            if not integer(c.get(key,0),limit): raise ValueError('Invalid residual scalar control.')
        if c.get('weather',0) not in (0,1,4,8,16,32,64) or (c.get('weather',0) in (1,8,32) and c.get('duration',0)==0):
            raise ValueError('Use a reviewed single weather with a nonzero temporary duration.')
        status3 = c.get('status3',[0,0])
        if not isinstance(status3,list) or len(status3)!=2 or any(not integer(v,0xffffffff) or v not in (0,5,1024) for v in status3):
            raise ValueError('Use reviewed rooted/seeded states for two battlers.')
        e = c.get('expected')
        if not isinstance(e,dict) or set(e)!=FIELDS: raise ValueError('Every final residual observation needs an explicit oracle.')
        for key,limit in [('hp',65535),('status',0xffffffff),('status3',0xffffffff),('side_statuses',65535)]:
            if not isinstance(e[key],list) or len(e[key])!=2 or any(not integer(v,limit) for v in e[key]):
                raise ValueError('Residual pair oracle exceeds its native width.')
        if any(v==0 for v in e['hp']): raise ValueError('Faint resolution is outside this profile.')
        for key,limit in [('weather',65535),('duration',255),('reflect_timer',255),('rng',0xffffffff)]:
            if not integer(e[key],limit): raise ValueError('Invalid residual scalar oracle.')
        if not isinstance(e['effects'],list) or any(not isinstance(v,str) or v not in SCRIPTS for v in e['effects']):
            raise ValueError('Require reviewed native effect script labels.')
        if not isinstance(e['selected_damage'],list) or any(type(v) is not int or not -65535 <= v <= 65535 for v in e['selected_damage']):
            raise ValueError('Require explicit signed battler effect damage.')
        if not isinstance(e['hp_updates'],list) or any(not isinstance(v,list) or len(v)!=2 or not integer(v[0],1) or not integer(v[1],65535) for v in e['hp_updates']):
            raise ValueError('Require explicit queued HP update oracles.')
    return cases


def setup(c, syms, labels, resolve):
    base = {'move':'MOVE_POUND', 'rng_seed':c.get('rng_seed',0),
            'attacker':{'hp':90,'max_hp':90,'speed':110,**c.get('attacker',{})},
            'defender':{'hp':90,'max_hp':90,'speed':100,**c.get('defender',{})}}
    commands,_ = script_setup(base,syms,labels,resolve)
    values = {'gBattleMainFunc':struct.pack('<I',syms['BattleTurnPassed'][0]|1),
              'gCurrentActionFuncId':bytes(1), 'gSideTimers':bytes([c.get('reflect_timer',0)])+bytes(23),
              'gSideStatuses':struct.pack('<HH',1 if c.get('reflect_timer',0) else 0,0),
              'gWishFutureKnock':bytes(40)+bytes([c.get('duration',0)])+bytes(3),
              'gBattleWeather':struct.pack('<H',c.get('weather',0)),
              'gStatuses3':struct.pack('<4I',*c.get('status3',[0,0]),0,0),
              'gBattlerPartyIndexes':bytes(8), 'gLastUsedItem':bytes(2),
              'gBattleMoveDamage':bytes(4), 'gBattleOutcome':bytes(1),
              'gPlayerParty':bytes(600), 'gEnemyParty':bytes(600),
              'gPlayerPartyCount':b'\1','gEnemyPartyCount':b'\1'}
    for name,value in values.items(): commands += writes(syms[name][0],value)
    commands += writes(0x0203f000+12,struct.pack('<I',CALLBACKS))+writes(CALLBACKS,bytes(36))
    for a,v in CANARIES.items(): commands += writes(a,v)
    # Real encrypted living party fixtures keep native checkteamslost independent
    # of the loaded campaign. Controller ACKs do not synchronize their HP.
    for name in ('gPlayerParty','gEnemyParty'):
        commands.append(call(syms,'CreateMon',syms[name][0],1,50,31,1,0,1,0))
    commands += writes(syms['gRngValue'][0],struct.pack('<I',c.get('rng_seed',0)))
    return commands


def call(syms,name,*args):
    return f'call {syms[name][0]:x} '+ ' '.join(f'{v:x}' for v in (*args,*([0]*(8-len(args)))))


def verify_unique_setups(cases,syms,labels,resolve):
    programs = [tuple(setup(c,syms,labels,resolve)) for c in cases]
    if len(set(programs))!=len(cases): raise ValueError('Duplicate effective residual setup.')


def read(driver, specs):
    rows = driver.exchange([f'read {a:x} {n:x}' for a,n in specs],len(specs))
    values = [bytes.fromhex(v) for v in rows]
    if any(len(v)!=n for v,(_,n) in zip(values,specs)): raise ValueError('Incomplete native residual read.')
    return values


def returned(row):
    if not re.fullmatch(r'return [0-9a-f]{8} steps \d+',row): raise ValueError('Native residual call failed.')
    return int(row.split()[1],16)


def acknowledge(driver,syms,flags,acks):
    if flags & ~3: raise ValueError('Unexpected controller slots or LINK transport.')
    slots = [s for s in range(2) if flags & (1<<s)]
    for slot,packet in zip(slots,read(driver,[(syms['gBattleBufferA'][0]+s*512,8) for s in slots]) if slots else []):
        if packet[0] not in ACK_COMMANDS: raise ValueError('Unreviewed controller response request.')
        if packet[0]==2 and (packet[1]!=42 or packet[2]!=0): raise ValueError('Unreviewed SetMonData request.')
        acks.append({'slot':slot,'command':packet[0],'header':packet.hex()})
    if flags: driver.exchange(writes(syms['gBattleControllerExecFlags'][0],bytes(4)),0)


def run_case(driver,c,syms,labels,resolve,rom):
    rows = driver.exchange(setup(c,syms,labels,resolve)+[f'read {syms["gRngValue"][0]:x} 4'],3)
    for row in rows[:2]: returned(row)
    if int.from_bytes(bytes.fromhex(rows[2]),'little')!=c.get('rng_seed',0): raise ValueError('Residual seed setup failed.')
    effects,damage,trace,acks = [],[],[],[]
    deadline = time.monotonic()+20
    def invoke(name):
        if time.monotonic()>=deadline: raise ValueError('Residual case exceeded its 20-second bound.')
        return returned(driver.exchange([call(syms,name)],1)[0])
    def state():
        return [int.from_bytes(v,'little') for v in read(driver,[(syms[n][0],4) for n in
                ('gBattlescriptCurrInstr','gBattleMainFunc','gBattleControllerExecFlags')])]
    callback = syms['BattleTurnPassed'][0]|1
    for phase in ('DoFieldEndTurnEffects','DoBattlerEndTurnEffects'):
        for selection in range(32):
            result = invoke(phase)
            pointer,main,flags = state()
            acknowledge(driver,syms,flags,acks)
            if result==0:
                if main!=callback: raise ValueError('Residual selector completed with an active callback.')
                break
            if result!=1 or main!=(syms['RunBattleScriptCommands_PopCallbacksStack'][0]|1):
                raise ValueError('Unexpected residual selection or callback.')
            entry = next((name for name in SCRIPTS if labels[name]==pointer),None)
            if entry is None: raise ValueError('Unreviewed residual effect script.')
            effects.append(entry)
            if phase=='DoBattlerEndTurnEffects':
                damage.append(int.from_bytes(read(driver,[(syms['gBattleMoveDamage'][0],4)])[0],'little',signed=True))
            for step in range(1024):
                if not 0 <= pointer-0x08000000 < len(rom): raise ValueError('Residual left cartridge script region.')
                opcode = rom[pointer-0x08000000]
                # Never allow move-end, fainting or a new action to become evidence.
                if pointer in (labels['BattleScript_FaintTarget'],labels['BattleScript_FaintAttacker']) or opcode in (26,35,73):
                    raise ValueError('Residual entered unsupported faint/action resolution.')
                invoke('RunBattleScriptCommands_PopCallbacksStack')
                after,main,flags = state()
                trace.append({'phase':phase,'entry':entry,'before':hex(pointer),'opcode':opcode,'after':hex(after),'controller':flags})
                acknowledge(driver,syms,flags,acks)
                pointer = after
                if main==callback:
                    if opcode!=62: raise ValueError('Residual callback returned without native end2.')
                    break
                if main!=(syms['RunBattleScriptCommands_PopCallbacksStack'][0]|1):
                    raise ValueError('Residual dispatcher changed to an unreviewed callback.')
            else: raise ValueError('Residual effect exceeded 1024 interpreter calls.')
        else: raise ValueError('Residual phase exceeded 32 selections.')
    mons = syms['gBattleMons'][0]
    specs = [(mons+i*88+off,n) for off,n in [(40,2),(76,4)] for i in range(2)]
    specs += [(syms['gStatuses3'][0]+i*4,4) for i in range(2)]
    specs += [(syms[n][0]+off,nbytes) for n,off,nbytes in [('gBattleWeather',0,2),('gWishFutureKnock',40,1),
              ('gSideTimers',0,1),('gSideStatuses',0,4),('gRngValue',0,4),('gBattleOutcome',0,1),('gBattlerByTurnOrder',0,2)]]
    raw = read(driver,specs); nums = [int.from_bytes(v,'little') for v in raw]
    guards = read(driver,list((a,len(v)) for a,v in CANARIES.items()))
    if guards!=list(CANARIES.values()): raise ValueError('Residual scratch crossed a native ABI boundary.')
    stacks = read(driver,[(CALLBACKS+32,1),(0x0203f800+32,1),(0x0203c000,2),(0x0203c003,1)])
    if stacks != [b'\0',b'\0',b'\0\2',b'\x0a'] or nums[11]!=0 or raw[12]!=b'\0\1':
        raise ValueError('Residual phases did not finish cleanly or battle outcome/order changed.')
    actual = {'hp':nums[:2],'status':nums[2:4],'status3':nums[4:6], 'weather':nums[6],
              'duration':nums[7],'reflect_timer':nums[8],'side_statuses':list(struct.unpack('<HH',raw[9])),
              'rng':nums[10],'effects':effects,'selected_damage':damage,
              'hp_updates':[[a['slot'],int.from_bytes(bytes.fromhex(a['header'])[3:5],'little')] for a in acks if a['command']==2]}
    return {'id':c['id'],'actual':actual,'expected':c['expected'],'pass':actual==c['expected'],
            'trace':trace,'controller_acknowledgements':acks,'scratch_canaries_intact':True,
            'native_callbacks_restored':True,'field_and_battler_phases_complete':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom','reference-elf','reference-state','candidate-rom','candidate-elf','candidate-state'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--cases',type=Path,default=ROOT/'data/quality/mechanics/residual.json')
    parser.add_argument('--name',required=True); args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',args.name): parser.error('Use a safe evidence name.')
    output = ROOT/'.tools/benchmarks'/args.name
    if output.exists(): parser.error('Preserve prior evidence; choose a fresh name.')
    cases = validate(json.loads(args.cases.read_text())); output.mkdir(parents=True)
    source = output/'residual-layout.c'
    source.write_text('#include "global.h"\n#include "battle.h"\n#include <stddef.h>\nconst unsigned residual_layout[] = {'+', '.join(LAYOUT)+'};\n')
    engine = ROOT/'.tools/pokeemerald-host'
    layout = verify_native_layout(engine,output,source,ABI)
    executable,core = build_driver(); resolve = constants(engine)
    dependencies = ['mechanics_fixtures.py','move_pipeline_fixtures.py','native_fixture_transport.py','native_abi.py','function_fixture.c']
    evidence = {'kind':'Native field/battler residual phases and selected effect scripts; controlled RAM',
                'core':core,'layout':layout,'runner_sha256':digest(Path(__file__)),'cases_sha256':digest(args.cases),
                'dependencies':{name:digest(ROOT/'scripts/quality'/name) for name in dependencies},
                'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'source_worktree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
                'limits':['Controlled two-battler end-turn entry; no move actions or move-end dispatch',
                          'Reviewed controller writes/animations only acknowledged; no presentation or party synchronization',
                          'Living native party fixtures prevent unrelated team-loss decisions; no faint handling',
                          'No durable save, full-turn, full-mechanics or human quality approval'],
                'full_turn_proven':False,'presentation_proven':False,'durable_save_proven':False,'full_mechanics_gate_complete':False,'sides':{}}
    for side in ('reference','candidate'):
        rom,elf,state = (getattr(args,side+'_'+n) for n in ('rom','elf','state'))
        identity,syms = verify_bundle(side,rom,elf,state,output,FUNCTIONS,ALLOCATIONS)
        labels = rom_symbols(elf)
        if not SCRIPTS|{'BattleScript_EffectHit','BattleScript_FaintTarget','BattleScript_FaintAttacker'} <= set(labels):
            raise ValueError('Pinned residual script labels missing.')
        verify_unique_setups(cases,syms,labels,resolve)
        driver = Driver(executable,rom,state,output/side)
        try: results = [run_case(driver,c,syms,labels,resolve,rom.read_bytes()) for c in cases]
        finally: driver.close()
        if driver.process.returncode or digest(rom)!=identity['rom_sha256']: raise ValueError('Residual driver failed or ROM changed.')
        evidence['sides'][side] = {**identity,'cases':results}
    passed = sum(a['pass'] and b['pass'] for a,b in zip(evidence['sides']['reference']['cases'],evidence['sides']['candidate']['cases']))
    evidence.update(passed=passed,total=len(cases))
    (output/'result.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'passed':passed,'total':len(cases),'evidence':str(output)}))
    if passed!=len(cases): raise SystemExit(1)


if __name__=='__main__': main()
