"""Controlled native chosen-turn resolution; no UI, campaign or durable-save proof.

Native data-write controllers apply party updates. Presentation-only packets are
acknowledged explicitly; choice queries are never answered. The KO profile stops
at the unanswered replacement query and is not a completed-turn claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import signal
import struct
import subprocess
import time

from mechanics_fixtures import (ROOT, SOURCE, HOST_BUILD, REVISION, verified_host_build,
    verify_bundle, constants, digest, battle_mon)
from native_fixture_transport import Driver, writes
from native_abi import verify_native_layout
from stat_fixtures import property_ids
from item_effect_fixtures import expected_mon, OWNER, MOVES, BASE_PP

CASES = (
    {'id':'living-two-hits', 'player_hp':90, 'enemy_hp':90, 'speeds':[110,90],
     'moves':[1,1], 'expected_order':[0,1], 'rng_seed':0, 'types':[[9,9],[9,9]],
     'endpoint':'next-turn', 'expected_hp':[72,72], 'expected_pp':[9,9],
     'expected_rng':4231221723, 'turns':1, 'faints':0,
     'expected_updates':[[0,9,9],[1,42,72],[1,9,9],[0,42,72]],
     'derivation':'Level50, power40, attack/defense100, neutral non-STAB types: base19. '
        'Seed0 draws0/59774/21105/12720 yield18; next36418/58060/44997/26587 yield18. '
        'No speed tie. BattleTurnPassed consumes ninth LCG draw; both PP10->9.'},
    {'id':'player-ko-replacement-boundary', 'player_hp':18, 'enemy_hp':90, 'speeds':[90,110],
     'moves':[1,1], 'expected_order':[1,0], 'rng_seed':0, 'types':[[9,9],[9,9]],
     'endpoint':'replacement-query', 'expected_hp':[0,90], 'expected_pp':[10,9],
     'expected_rng':833674724, 'turns':0, 'faints':1,
     'expected_updates':[[1,9,9],[0,42,0],[0,40,0]],
     'derivation':'Enemy acts first without tie; same first-hit18 reaches playerHP0. '
        'Four RNG draws only before unanswered player replacement; player move never runs. '
        'Healthy bench prevents defeat. FaintClearSetData restores native Rattata Normal/Normal '
        'from the declared Mystery-type battle override. No EXP, replacement response or completed turn claimed.'},
    {'id':'slower-player-priority', 'player_hp':90, 'enemy_hp':90, 'speeds':[90,110],
     'moves':[98,1], 'expected_order':[0,1], 'rng_seed':0, 'types':[[9,9],[9,9]],
     'endpoint':'next-turn', 'expected_hp':[72,72], 'expected_pp':[9,9],
     'expected_rng':4231221723, 'turns':1, 'faints':0,
     'expected_updates':[[0,9,9],[1,42,72],[1,9,9],[0,42,72]],
     'derivation':'Pinned Emerald731ad5bf battle_moves: QuickAttack98 power40/accuracy100/priority1; '
        'Pound1 power40/accuracy100/priority0. GetWhoStrikesFirst compares priority before speed '
        'without Random on unequal priorities, so player90 precedes enemy110. '
        'EFFECT_QUICK_ATTACK maps to the same BattleScript_EffectHit as Pound. '
        'Controlled level50/attack100/defense100/Mystery types give base19 and18 damage each. '
        'Seed0 eight hit draws0/59774/21105/12720/36418/58060/44997/26587, '
        'then BattleTurnPassed ninth draw gives4231221723; both PP10->9.'},
    {'id':'player-first-miss-reply', 'player_hp':90, 'enemy_hp':90, 'speeds':[110,90],
     'moves':[33,1], 'expected_order':[0,1], 'rng_seed':30, 'types':[[9,9],[9,9]],
     'endpoint':'next-turn', 'expected_hp':[72,90], 'expected_pp':[9,9],
     'expected_rng':3063870748, 'turns':1, 'faints':0,
     'expected_updates':[[0,9,9],[1,9,9],[0,42,72]],
     'derivation':'Pinned Emerald731ad5bfd6e6f265508d0efcca0ba42f9dcf5881: '
        'Tackle33 EFFECT_HIT/power35/accuracy95/priority0 vs Pound1 power40/accuracy100/priority0. '
        'Faster player110 acts before enemy90 without a tie draw. Seed30 LCG upper16 draws '
        '46397/47244/24877/5747/11048/46750. First accuracy46397%100+1=98>95 misses. '
        'EffectHit jumps to PrintMoveMissed: attackstring/PP reduction/moveend, no crit,damage or HP write. '
        'Enemy accuracy47244%100+1=45 hits; crit24877%16=13 is noncritical; '
        'base19*(100-5747%16)//100=18 damage; chance0 still consumes11048. '
        'BattleTurnPassed consumes sixth draw, state3063870748. '
        'Both moves are recorded before accuracy resolution, both PP10->9, only player takes damage.'},
    {'id':'normal-ghost-immunity-reply', 'player_hp':90, 'enemy_hp':90, 'speeds':[110,90],
     'moves':[1,1], 'expected_order':[0,1], 'rng_seed':0, 'types':[[9,9],[7,7]],
     'endpoint':'next-turn', 'expected_hp':[72,90], 'expected_pp':[9,9],
     'expected_rng':4231221723, 'turns':1, 'faints':0,
     'expected_updates':[[0,9,9],[1,9,9],[0,42,72]],
     'derivation':'Pinned Emerald731ad5bfd6e6f265508d0efcca0ba42f9dcf5881: '
        'Pound1/EFFECT_HIT/power40/accuracy100/priority0; player110 precedes enemy90 without tie draw. '
        'Only live BattleMon types change: playerMystery9/9,enemyGhost7/7; secure Rattata parties retain their natural species. '
        'No early immunity preemption: player accuracy0 rolls1,crit59774%16=14 noncritical,base19. '
        'Cmd_typecalc applies Normal->Ghost0 once,sets DOESNT_AFFECT_FOE8 and zeroes damage. '
        'Adjustnormaldamage still draws21105;chance0 still draws12720. HP opcodes execute but emit no enemy HP write. '
        'Enemy accuracy36418 rolls19,crit58060%16=12 noncritical,damage44997%16=5 gives18;chance draws26587. '
        'Neither attacker has Normal STAB;Mystery target stays neutral. Endturn ninth draw gives4231221723. '
        'Both PP10->9,both lastmoves1,only player HP90->72; Ghost types remain7/7 without faint cleanup.'},
)
FUNCTIONS = {'CreateMon','SetMonData','SetActionsAndBattlersTurnOrder',
    'CheckFocusPunch_ClearVarsBeforeTurnStarts','RunTurnActionsFunctions',
    'HandleEndTurn_ContinueBattle','BattleTurnPassed','HandleTurnActionSelectionState',
    'RunBattleScriptCommands_PopCallbacksStack','RunBattleScriptCommands',
    'PlayerHandleSetMonData','OpponentHandleSetMonData','Cmd_moveend','Cmd_tryfaintmon',
    'HandleAction_UseMove','HandleAction_TryFinish','HandleFaintedMonActions','FaintClearSetData',
    'SetPlayerMonData','SetOpponentMonData','Cmd_openpartyscreen',
    'PlayerBufferExecCompleted','OpponentBufferExecCompleted'}
CALLBACKS = {'CheckFocusPunch_ClearVarsBeforeTurnStarts','RunTurnActionsFunctions',
    'HandleEndTurn_ContinueBattle','BattleTurnPassed','RunBattleScriptCommands_PopCallbacksStack',
    'RunBattleScriptCommands'}
ALLOCATIONS = {'gMain':1084,'gPlayerParty':600,'gEnemyParty':600,'gPlayerPartyCount':1,
    'gEnemyPartyCount':1,'gBattlerPartyIndexes':8,'gBattleResults':68,'gBattleOutcome':1,
    'gBattleBufferA':2048,'gBattleBufferB':2048,'gBattlerControllerFuncs':16,
    'gChosenMoveByBattler':8,'gCurrentTurnActionNumber':1,'gCurrentActionFuncId':1,
    'gChosenMove':2,'gChosenMovePos':1,'gBattleTextBuff1':16,'gBattleTextBuff2':16,
    'gBattleTextBuff3':16,'gMultiHitCounter':1,'gDynamicBasePower':2,
    'gPauseCounterBattle':2,'gSaveBlock1Ptr':4,'gSaveBlock2Ptr':4}
ALLOCATIONS.update({'gWindows':384,'gSideTimers':24,'gWishFutureKnock':44,
    'gLastMoves':8,'gLastResultingMoves':8,'gLastPrintedMoves':8,'gLockedMoves':8,
    'gLastHitBy':4,'gLastUsedItem':2})
VALUE=0x0203f500
CANARIES={VALUE-16:bytes([0xA6])*16,VALUE+16:bytes([0x6A])*16}
PRESENTATION={15,16,24,26,27,41,43,45,51,52,10}  # Faint10/cry45/visibility51 do not apply party data.
SET_REQUESTS={9:1,40:4,42:2}
MAX_DISPATCHES=4096
CASE_SECONDS=45


def protocol_contract(engine):
    """Verify packet and script byte values against the pinned native enums."""
    from mechanics_fixtures import EMERALD_REVISION
    def enum(header,member):
        text=subprocess.check_output(['git','show',EMERALD_REVISION+':include/'+header],cwd=engine,text=True,timeout=10)
        for body in re.findall(r'enum(?:\s+\w+)?\s*\{(.*?)\}',text,re.S):
            clean=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S)
            names=[v.strip() for v in clean.split(',') if v.strip()]
            if member not in names:continue
            if any(not re.fullmatch('[A-Z][A-Z_0-9]*',v) for v in names):
                raise ValueError('Pinned native protocol enum needs review.')
            return {v:i for i,v in enumerate(names)}
        raise ValueError('Missing pinned protocol enum.')
    commands=enum('battle_controllers.h','CONTROLLER_GETMONDATA')
    requests=enum('battle_controllers.h','REQUEST_ALL_BATTLE')
    scripts=enum('constants/battle_script_commands.h','B_SCR_OP_ATTACKCANCELER')
    expected={'CONTROLLER_SETMONDATA':2,'CONTROLLER_CHOOSEPOKEMON':22,'CONTROLLER_LINKSTANDBYMSG':53,
              'REQUEST_PPMOVE1_BATTLE':9,'REQUEST_STATUS_BATTLE':40,'REQUEST_HP_BATTLE':42,
              'B_SCR_OP_PPREDUCE':3,'B_SCR_OP_MOVEEND':73,
              'B_SCR_OP_ACCURACYCHECK':1,'B_SCR_OP_CRITCALC':4,'B_SCR_OP_DAMAGECALC':5,
              'B_SCR_OP_HEALTHBARUPDATE':11,'B_SCR_OP_DATAHPUPDATE':12,
              'B_SCR_OP_TYPECALC':6,'B_SCR_OP_ADJUSTNORMALDAMAGE':7,'B_SCR_OP_SETEFFECTWITHCHANCE':0x15,
              'B_SCR_OP_YESNOBOXLEARNMOVE':0x5a,'B_SCR_OP_YESNOBOXSTOPLEARNINGMOVE':0x5b,
              'B_SCR_OP_YESNOBOX':0x67}
    actual={name:(commands|requests|scripts)[name] for name in expected}
    if actual!=expected:raise ValueError('Pinned native packet/script contract changed.')
    return actual


def validate_cases(cases):
    if not isinstance(cases,(tuple,list)) or not 1<=len(cases)<=8:
        raise ValueError('Use one to eight explicitly derived controlled turn cases.')
    ids,setups=set(),set()
    required={'id','player_hp','enemy_hp','speeds','endpoint','expected_hp','expected_pp',
              'expected_rng','turns','faints','expected_updates','derivation','moves','expected_order','rng_seed','types'}
    for c in cases:
        if not isinstance(c,dict) or set(c)!=required or not isinstance(c['derivation'],str) or not c['derivation'].strip():
            raise ValueError('Require the complete strict turn schema and independent derivation.')
        if not isinstance(c['id'],str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',c['id']) or c['id'] in ids:
            raise ValueError('Controlled turn IDs must be unique and safe.')
        ids.add(c['id'])
        integer=lambda v,low,high:type(v) is int and low<=v<=high
        if not integer(c['player_hp'],1,105) or not integer(c['enemy_hp'],1,105) or \
           not isinstance(c['speeds'],list) or len(c['speeds'])!=2 or \
           any(not integer(v,1,65535) for v in c['speeds']) or c['speeds'][0]==c['speeds'][1]:
            raise ValueError('Use bounded living HP and unequal native speeds.')
        if not isinstance(c['moves'],list) or any(type(v) is not int for v in c['moves']) or \
           tuple(c['moves']) not in {(1,1),(98,1),(33,1)} or not isinstance(c['expected_order'],list) or \
           any(type(v) is not int for v in c['expected_order']) or sorted(c['expected_order'])!=[0,1]:
            raise ValueError('Declare reviewed per-battler moves and a complete strict action order.')
        if not isinstance(c['types'],list) or len(c['types'])!=2 or any(
            not isinstance(pair,list) or len(pair)!=2 or any(type(v) is not int for v in pair) for pair in c['types']) or \
            tuple(map(tuple,c['types'])) not in {((9,9),(9,9)),((9,9),(7,7))}:
            raise ValueError('Require the reviewed two complete live battle-only type pairs.')
        if c['types'][1]==[7,7] and (c['moves']!=[1,1] or c['endpoint']!='next-turn'):
            raise ValueError('Ghost override is limited to the reviewed full-turn Pound profile.')
        order=[0,1] if c['moves'][0]==98 or c['speeds'][0]>c['speeds'][1] else [1,0]
        if c['expected_order']!=order:
            raise ValueError('Declared action order contradicts pinned move priorities and speeds.')
        for key,high in [('expected_hp',105),('expected_pp',35)]:
            if not isinstance(c[key],list) or len(c[key])!=2 or any(not integer(v,0,high) for v in c[key]):
                raise ValueError('Require two complete HP/PP integer oracles.')
        if not integer(c['rng_seed'],0,0xffffffff) or not integer(c['expected_rng'],0,0xffffffff) or not integer(c['turns'],0,1) or not integer(c['faints'],0,1):
            raise ValueError('RNG, turn and faint oracles must fit this finite profile.')
        if c['endpoint'] not in {'next-turn','replacement-query'} or \
           (c['endpoint']=='next-turn' and (0 in c['expected_hp'] or c['turns']!=1 or c['faints'])) or \
           (c['endpoint']=='replacement-query' and (c['expected_hp'][0]!=0 or not c['expected_hp'][1] or c['turns'] or c['faints']!=1)):
            raise ValueError('Do not conflate a living full turn with an unanswered KO boundary.')
        if not isinstance(c['expected_updates'],list) or not c['expected_updates'] or any(
            not isinstance(row,list) or len(row)!=3 or not integer(row[0],0,1) or type(row[1]) is not int or row[1] not in SET_REQUESTS or
            not integer(row[2],0,(1<<(8*SET_REQUESTS[row[1]]))-1) for row in c['expected_updates']):
            raise ValueError('Declare every native party-write packet independently.')
        key=(c['player_hp'],c['enemy_hp'],tuple(c['speeds']),tuple(c['moves']),c['rng_seed'],tuple(map(tuple,c['types'])))
        if key in setups:raise ValueError('Duplicate effective turn setup cannot add coverage.')
        setups.add(key)
    return cases


def call(syms,name,*args):
    if len(args)>8 or any(type(v) is not int or not 0<=v<=0xffffffff for v in args):
        raise ValueError('Native calls require at most eight unsigned register/stack arguments.')
    return 'call %x %s' % (syms[name][0], ' '.join('%x'%v for v in (*args,*([0]*(8-len(args))))))


def read(driver, specs):
    rows=driver.exchange(['read %x %x'%(a,n) for a,n in specs],len(specs))
    result=[]
    for row,(_,size) in zip(rows,specs):
        if not re.fullmatch('[0-9a-f]{%d}'%(size*2),row):
            raise ValueError('Incomplete native turn observation.')
        result.append(bytes.fromhex(row))
    if len(result)!=len(specs): raise ValueError('Missing native turn observation.')
    return result


def invoke(driver,syms,name,*args):
    row=driver.exchange([call(syms,name,*args)],1)[0]
    match=re.fullmatch(r'return ([0-9a-f]{8}) steps (\d+)',row)
    if not match or not 0<int(match[2])<2000000:
        raise ValueError('Native turn callback did not return within its instruction limit.')
    return int(match[1],16)


def verify_abi(engine,output):
    source=output/'turn-resolution-layout.c'
    fields=['sizeof(struct Pokemon)','sizeof(struct BattlePokemon)','sizeof(struct BattleStruct)',
        'sizeof(struct BattleResources)','sizeof(struct BattleScriptsStack)',
        'sizeof(struct BattleCallbacksStack)','offsetof(struct BattleScriptsStack,size)',
        'offsetof(struct BattleCallbacksStack,size)','offsetof(struct BattleStruct,chosenMovePositions)',
        'offsetof(struct BattleResults,battleTurnCounter)','offsetof(struct BattleStruct,moveTarget)',
        'sizeof(struct Main)','sizeof(struct Window)','offsetof(struct Window,tileData)',
        'sizeof(struct WindowTemplate)','sizeof(struct ResourceFlags)']
    # inBattle is a bitfield; prove its byte mask with a native constant object
    # rather than applying offsetof or assuming the host compiler's packing.
    source.write_text('#include "global.h"\n#include "battle.h"\n#include "window.h"\n#include <stddef.h>\n'
        'const unsigned turn_resolution_layout[] = {'+', '.join(fields)+'};\n'
        'const struct Main turn_resolution_main_flag = {.inBattle=TRUE};\n')
    proof=verify_native_layout(engine,output,source,[100,88,676,32,36,36,32,32,0x80,0x13,12,1084,12,8,8,16])
    obj=output/'turn-resolution-layout.o';binary=output/'turn-resolution-layout.bin'
    subprocess.run(['arm-none-eabi-as','-mthumb-interwork','-o',str(obj),str(source.with_suffix('.s'))],check=True,timeout=10)
    subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.rodata',str(obj),str(binary)],check=True,timeout=10)
    symbols=subprocess.check_output(['arm-none-eabi-nm','-S','--defined-only',str(obj)],text=True,timeout=10)
    match=re.search(r'^([0-9a-f]+) ([0-9a-f]+) [A-Za-z] turn_resolution_main_flag$',symbols,re.M)
    flag=bytearray(1084);flag[0x439]=2
    if not match or int(match[2],16)!=1084 or binary.read_bytes()[int(match[1],16):int(match[1],16)+1084]!=flag:
        raise ValueError('Pinned Main.inBattle mask changed.')
    proof['main_flag_probe_sha256']=digest(binary)
    return proof


def build_turn_driver(output):
    core=verified_host_build()
    if subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True,timeout=10).strip()!=REVISION:
        raise ValueError('Pinned native core source changed.')
    executable=output/'turn-resolution-function-fixture'
    frameworks=['-framework','CoreFoundation'] if platform.system()=='Darwin' else []
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-D_GNU_SOURCE','-DBUILD_STATIC',
        '-I'+str(SOURCE/'include'),'-I'+str(HOST_BUILD/'include'),
        str(ROOT/'scripts/quality/function_fixture.c'),str(HOST_BUILD/'libmgba.a'),
        '-lm','-lpthread',*frameworks,'-o',str(executable)],check=True,timeout=60)
    return executable,{**core,'driver_source_sha256':digest(ROOT/'scripts/quality/function_fixture.c'),
                       'driver_binary_sha256':digest(executable)}


def valid_ram(address,length):
    return 0x02000000<=address and address+length<=0x02040000


def expected_turn_mon(hp,pp,move):
    """Source-derived secure moves/checksum; never uses native observed bytes.

    Fixed PID0 uses GAEM substructure order; secure attacks begin at plain12.
    All twelve u32 words use OT11223344 XOR, and checksum sums24 plain u16.
    """
    result=bytearray(expected_mon(hp,0,pp,0))
    plain=bytearray(struct.pack('<12I',*[v^OWNER for v in struct.unpack_from('<12I',result,32)]))
    struct.pack_into('<H',plain,12,move)
    struct.pack_into('<H',result,28,sum(struct.unpack('<24H',plain))&0xffff)
    struct.pack_into('<12I',result,32,*[v^OWNER for v in struct.unpack('<12I',plain)])
    return bytes(result)


def setup(driver,c,syms,resolve,props):
    driver.exchange(['reset'],0)
    main,resource,structure,save1,save2=read(driver,[(syms[n][0],size) for n,size in
        [('gMain',1084),('gBattleResources',4),('gBattleStruct',4),
         ('gSaveBlock1Ptr',4),('gSaveBlock2Ptr',4)]])
    resource,structure,save1,save2=[int.from_bytes(v,'little') for v in (resource,structure,save1,save2)]
    if not main[0x439]&2 or any(not valid_ram(a,n) for a,n in
        [(resource,32),(structure,676),(save1,0x3d88),(save2,0xf2c)]):
        raise ValueError('Require an actual live in-battle snapshot with native resources.')
    resources=read(driver,[(resource,32)])[0]
    flags=struct.unpack_from('<I',resources,4)[0]
    script_stack,callback_stack,history=struct.unpack_from('<I',resources,8)[0],struct.unpack_from('<I',resources,12)[0],struct.unpack_from('<I',resources,24)[0]
    window=read(driver,[(syms['gWindows'][0],12)])[0]
    width,height=window[3:5];tiles=struct.unpack_from('<I',window,8)[0]
    if not 1<=width<=30 or not 1<=height<=20 or window[0]>3 or not valid_ram(tiles,width*height*32):
        raise ValueError('Snapshot does not have a live allocated battle message window.')
    if any(not valid_ram(a,n) for a,n in [(script_stack,36),(callback_stack,36),(history,84),(flags,16)]):
        raise ValueError('Snapshot battle stacks/history are not allocated.')
    protected=[(save1,0x3d88),(save2,0xf2c),(resource,32),(structure,676),
               (script_stack,36),(callback_stack,36),(history,84),(flags,16),(tiles,width*height*32)]
    protected.extend((address,size) for address,size in syms.values() if valid_ram(address,size))
    if any(a<VALUE+32 and VALUE-16<a+n for a,n in protected):
        raise ValueError('Turn scratch overlaps native snapshot resources.')
    def write(a,b):driver.exchange(writes(a,b),0)
    def put(name,b):write(syms[name][0],b)
    write(structure,bytes(676));write(script_stack,bytes(36));write(callback_stack,bytes(36));write(history,bytes(84));write(flags,bytes(16))
    for a,b in CANARIES.items():write(a,b)
    put('gPlayerParty',bytes(600));put('gEnemyParty',bytes(600))
    for side,(base,hps) in enumerate([(syms['gPlayerParty'][0],[c['player_hp'],105]),(syms['gEnemyParty'][0],[c['enemy_hp']])]):
        for index,hp in enumerate(hps):
            mon=base+index*100
            invoke(driver,syms,'CreateMon',mon,19,50,31,1,0,1,OWNER)
            def set_data(name,value):
                write(VALUE,value if isinstance(value,bytes) else struct.pack('<I',value))
                invoke(driver,syms,'SetMonData',mon,props[name],VALUE)
            set_data('MON_DATA_NICKNAME',bytes([187])*10);set_data('MON_DATA_OT_NAME',bytes([187])*7)
            for i,move in enumerate([c['moves'][side] if index==0 else 1,*MOVES[1:]]):set_data('MON_DATA_MOVE'+str(i+1),move)
            for i,pp in enumerate([10,30,25,25]):set_data('MON_DATA_PP'+str(i+1),pp)
            for name,value in [('HP',hp),('STATUS',0),('PP_BONUSES',0),('MET_LOCATION',21),
                ('MET_LEVEL',50),('MET_GAME',3),('POKEBALL',4),('OT_GENDER',1)]:set_data('MON_DATA_'+name,value)
    mons=[]
    for i,hp in enumerate([c['player_hp'],c['enemy_hp'],0,0]):
        mon=bytearray(battle_mon({'species':19,'hp':hp,'max_hp':105,'speed':c['speeds'][i] if i<2 else 0,
            'type1':c['types'][i][0] if i<2 else 9,'type2':c['types'][i][1] if i<2 else 9},resolve))
        struct.pack_into('<4H',mon,12,c['moves'][i] if i<2 else 1,*MOVES[1:]);struct.pack_into('<I',mon,20,0x3fffffff)
        mon[36:40]=bytes([10,30,25,25]);mon[43]=70;mon[48:59]=bytes([187])*10+b'\xff'
        mon[60:68]=bytes([187])*7+b'\xff';struct.pack_into('<III',mon,68,125000,0,0)
        struct.pack_into('<I',mon,84,OWNER);mons.append(bytes(mon))
    initial=b''.join(mons)
    values={'gBattleMons':initial,'gBattlerPositions':bytes(range(4)),'gBattlersCount':b'\2',
        'gBattlerAttacker':b'\0','gBattlerTarget':b'\1','gActiveBattler':b'\0',
        'gAbsentBattlerFlags':b'\x0c','gPlayerPartyCount':b'\2','gEnemyPartyCount':b'\1',
        'gBattlerPartyIndexes':bytes(8),'gBattleTypeFlags':struct.pack('<I',264),  # TRAINER | BATTLE_TOWER, never LINK.
        'gBattleResults':bytes(68),'gBattleOutcome':b'\0','gChosenMoveByBattler':struct.pack('<4H',*c['moves'],0,0),
        'gChosenActionByBattler':bytes(4),'gBattleControllerExecFlags':bytes(4),
        'gBattleBufferA':bytes(2048),'gBattleBufferB':bytes(2048),
        'gDisableStructs':bytes(112),'gProtectStructs':bytes(64),'gSpecialStatuses':bytes(80),
        'gStatuses3':bytes(16),'gSideStatuses':bytes(4),'gBattleScripting':bytes(40),
        'gBattleCommunication':bytes(8),'gHitMarker':struct.pack('<I',resolve('HITMARKER_OBEYS')),
        'gMoveResultFlags':b'\0','gBattleWeather':bytes(2),'gCurrentTurnActionNumber':b'\0',
        'gCurrentActionFuncId':b'\0','gCurrMovePos':b'\0','gCurrentMove':struct.pack('<H',c['moves'][c['expected_order'][0]]),
        'gChosenMove':struct.pack('<H',c['moves'][c['expected_order'][0]]),'gChosenMovePos':b'\0','gRandomTurnNumber':b'\xff\xff',
        'gRngValue':struct.pack('<I',c['rng_seed']),'gSideTimers':bytes(24),'gWishFutureKnock':bytes(44),
        'gLastMoves':bytes(8),'gLastResultingMoves':bytes(8),'gLastPrintedMoves':bytes(8),
        'gLockedMoves':bytes(8),'gLastHitBy':bytes(4),'gLastUsedItem':bytes(2)}
    for name,b in values.items():put(name,b)
    # All scripted moves use slot0 and target the opposite battler.
    write(structure+12,bytes([1,0,0,0]));write(structure+0x80,bytes(4))
    before=read(driver,[(syms['gPlayerParty'][0],600),(syms['gEnemyParty'][0],600),
                         (save1,0x3d88),(save2,0xf2c)])
    expected_before=[expected_turn_mon(c['player_hp'],[10,30,25,25],c['moves'][0])+expected_mon(105,0,[10,30,25,25],0)+bytes(400),
                     expected_turn_mon(c['enemy_hp'],[10,30,25,25],c['moves'][1])+bytes(500)]
    if before[:2]!=expected_before:
        raise ValueError('Native initial parties differ from the independent complete-object oracle.')
    return {'initial_battle_mons':initial,'before':before,'save_addresses':[save1,save2],
            'script_stack':script_stack,'callback_stack':callback_stack,'structure':structure,
            'snapshot_window':{'width':width,'height':height,'tiles':hex(tiles)}}


def service_controllers(driver,syms,case,log):
    flags=int.from_bytes(read(driver,[(syms['gBattleControllerExecFlags'][0],4)])[0],'little')
    if flags&~3:raise ValueError('Unexpected controller slot or LINK transport.')
    for slot in range(2):
        if not flags&(1<<slot):continue
        packet=read(driver,[(syms['gBattleBufferA'][0]+slot*512,8)])[0]
        log.append({'slot':slot,'packet':packet.hex()})
        command=packet[0]
        if command==22:  # Native enum CONTROLLER_CHOOSEPOKEMON.
            if case['endpoint']!='replacement-query' or slot!=0 or flags!=3 or packet!=bytes.fromhex('1601000000000000'):
                raise ValueError('Unreviewed party selection request.')
            standby=read(driver,[(syms['gBattleBufferA'][0]+512,8)])[0]
            if standby[:4]!=bytes.fromhex('35020000'):
                raise ValueError('Replacement boundary has an unexpected opposing controller request.')
            log.append({'slot':1,'packet':standby.hex(),'pending':True})
            return 'replacement-query'
        if command==2:
            if packet[1] not in SET_REQUESTS or packet[2]!=0:
                raise ValueError('Unreviewed native data-write request or party mask.')
            driver.exchange(writes(syms['gActiveBattler'][0],bytes([slot])),0)
            invoke(driver,syms,'PlayerHandleSetMonData' if slot==0 else 'OpponentHandleSetMonData')
            after=int.from_bytes(read(driver,[(syms['gBattleControllerExecFlags'][0],4)])[0],'little')
            if after!=flags&~(1<<slot):raise ValueError('Native setter did not complete exactly its own controller.')
            flags=after
        elif command in PRESENTATION:
            flags &= ~(1<<slot)
            driver.exchange(writes(syms['gBattleControllerExecFlags'][0],struct.pack('<I',flags)),0)
        else:raise ValueError('Unreviewed controller command%d; no response fabricated.'%command)
    return None


def dispatch(main,pointer,action,syms,rom):
    names={(syms[name][0]|1):name for name in CALLBACKS}
    if main not in names:raise ValueError('Unreviewed native turn callback%08x'%main)
    name=names[main]
    consumes_script=name in {'RunBattleScriptCommands','RunBattleScriptCommands_PopCallbacksStack'} or \
        (name=='RunTurnActionsFunctions' and action==10)
    if consumes_script and not 0x08000000<=pointer<0x08000000+len(rom):
        raise ValueError('Native turn script left cartridge address space.')
    opcode=rom[pointer-0x08000000] if consumes_script else None
    if opcode in (0x5a,0x5b,0x67):raise ValueError('Unanswered native script choice request.')
    return name,opcode


def run_case(driver,c,syms,resolve,props,rom):
    start=time.monotonic();state=setup(driver,c,syms,resolve,props)
    trace,packets=[],[]
    driver.turn_trace=trace;driver.turn_packets=packets
    invoke(driver,syms,'SetActionsAndBattlersTurnOrder')
    terminal=syms['HandleTurnActionSelectionState'][0]|1
    endpoint=None
    for step in range(MAX_DISPATCHES):
        if time.monotonic()-start>CASE_SECONDS:raise ValueError('Turn fixture exceeded its case deadline.')
        endpoint=service_controllers(driver,syms,c,packets)
        if endpoint:break
        main,pointer,action=read(driver,[(syms['gBattleMainFunc'][0],4),
            (syms['gBattlescriptCurrInstr'][0],4),(syms['gCurrentActionFuncId'][0],1)])
        main=int.from_bytes(main,'little');pointer=int.from_bytes(pointer,'little')
        if main==terminal:
            if c['endpoint']!='next-turn':raise ValueError('KO fixture reached next-turn choice without replacement.')
            endpoint='next-turn';break
        name,opcode=dispatch(main,pointer,action[0],syms,rom)
        depth=read(driver,[(state['script_stack']+32,1),(state['callback_stack']+32,1)])
        if any(v[0]>8 for v in depth):raise ValueError('Native turn stack crossed its ABI capacity.')
        attacker=read(driver,[(syms['gBattlerAttacker'][0],1)])[0][0]
        trace.append({'step':step,'callback':name,'script':hex(pointer),
                      'opcode':opcode,'attacker':attacker})
        invoke(driver,syms,name)
    else:raise ValueError('Turn fixture exceeded its dispatch limit.')
    specs=[(syms['gPlayerParty'][0],600),(syms['gEnemyParty'][0],600),
        (syms['gBattleMons'][0],352),(state['save_addresses'][0],0x3d88),
        (state['save_addresses'][1],0xf2c),(syms['gBattleResults'][0],68),
        (syms['gRngValue'][0],4),(syms['gBattleOutcome'][0],1),
        (state['script_stack']+32,1),(state['callback_stack']+32,1),
        (syms['gChosenActionByBattler'][0],4),(syms['gChosenMoveByBattler'][0],8),
        (syms['gBattleControllerExecFlags'][0],4),(syms['gBattleTypeFlags'][0],4),
        (syms['gSaveBlock1Ptr'][0],4),(syms['gSaveBlock2Ptr'][0],4),
        (syms['gPlayerPartyCount'][0],1),(syms['gEnemyPartyCount'][0],1),
        (syms['gBattlerByTurnOrder'][0],2),(state['callback_stack'],4)]
    observed=read(driver,specs)
    guards=read(driver,[(a,len(b)) for a,b in CANARIES.items()])
    return assess(c,state,observed,guards,packets,syms,resolve,endpoint,trace,time.monotonic()-start)


def assess(c,state,observed,guards,packets,syms,resolve,endpoint,trace,elapsed=0):
    """Compare completed native observations to fixed independent postconditions."""
    sizes=[600,600,352,0x3d88,0xf2c,68,4,1,1,1,4,8,4,4,4,4,1,1,2,4]
    if len(observed)!=len(sizes) or any(len(value)!=size for value,size in zip(observed,sizes)):
        raise ValueError('Incomplete full-party/turn postcondition observation.')
    hp,pp=c['expected_hp'],c['expected_pp']
    expected_parties=[expected_turn_mon(hp[0],[pp[0],30,25,25],c['moves'][0])+state['before'][0][100:],
                      expected_turn_mon(hp[1],[pp[1],30,25,25],c['moves'][1])+state['before'][1][100:]]
    expected_battle=bytearray(state['initial_battle_mons'])
    for i in range(2):struct.pack_into('<H',expected_battle,i*88+40,hp[i]);expected_battle[i*88+36]=pp[i]
    if c['endpoint']=='replacement-query':expected_battle[33:35]=b'\0\0'  # Native faint cleanup restores Rattata's types.
    expected_results=bytearray(68);expected_results[0]=c['faints'];expected_results[5]=1
    expected_results[19]=c['turns'];struct.pack_into('<H',expected_results,36,c['moves'][1])
    if c['endpoint']=='next-turn':struct.pack_into('<H',expected_results,34,c['moves'][0])
    else:expected_results[2]=1  # Native openpartyscreen increments before the unanswered mandatory query.
    updates=[]
    for packet in packets:
        raw=bytes.fromhex(packet['packet'])
        if raw[0]==2:updates.append([packet['slot'],raw[1],int.from_bytes(raw[3:3+SET_REQUESTS[raw[1]]],'little')])
    checks={'endpoint':endpoint==c['endpoint'],'full_parties':observed[:2]==expected_parties,
        'full_battle_mons':observed[2]==expected_battle,'save_blocks':observed[3:5]==state['before'][2:],
        'rng':int.from_bytes(observed[6],'little')==c['expected_rng'],'outcome':observed[7]==b'\0',
        'faints':observed[5][0]==c['faints'],'turns':observed[5][19]==c['turns'],
        'full_battle_results':observed[5]==expected_results,
        'native_write_packets':updates==c['expected_updates'],
        'pending_controllers':observed[12]==struct.pack('<I',0 if endpoint=='next-turn' else 3),
        'nonlink_rules':observed[13]==struct.pack('<I',264),
        'save_pointers':observed[14:16]==[struct.pack('<I',a) for a in state['save_addresses']],
        'party_counts':observed[16:18]==[b'\2',b'\1'],
        'ordered_actions':observed[18]==bytes(c['expected_order']),
        'stacks':observed[8:10]==([b'\0',b'\0'] if endpoint=='next-turn' else [b'\0',b'\1']),
        'canaries':guards==list(CANARIES.values())}
    if endpoint=='next-turn':
        checks.update(actions_reset=observed[10]==bytes([resolve('B_ACTION_NONE')])*2+bytes(2) and observed[11]==bytes(8))
    else:checks['pending_native_callback']=observed[19]==struct.pack('<I',syms['RunTurnActionsFunctions'][0]|1)
    checks['executed_pp_order']=[row['attacker'] for row in trace if row['opcode']==3]==(c['expected_order'] if endpoint=='next-turn' else [1])
    checks['move_end_executed']=73 in {row['opcode'] for row in trace}
    if c['id']=='player-first-miss-reply':
        player={row['opcode'] for row in trace if row['attacker']==0}
        enemy={row['opcode'] for row in trace if row['attacker']==1}
        checks['first_miss_then_reply_path']={1,3,73}<=player and not player&{4,5,11,12} and {1,3,4,5,12,73}<=enemy

    if c['id']=='normal-ghost-immunity-reply':
        required=[1,3,4,5,6,7,11,12,0x15,73]
        def immune_path(attacker):
            path=[row['opcode'] for row in trace if row['attacker']==attacker]
            return all(code in path for code in required) and \
                [path.index(code) for code in required]==sorted(path.index(code) for code in required)
        checks['immune_path_then_reply']=immune_path(0) and immune_path(1) and \
            not any(slot==1 and request==42 for slot,request,value in updates)
    return {'id':c['id'],'endpoint':endpoint,'passed':all(checks.values()),'checks':checks,
        'trace':trace,'controller_packets':packets,'observed_rng':int.from_bytes(observed[6],'little'),
        'observed_hp':[int.from_bytes(observed[2][i*88+40:i*88+42],'little') for i in range(2)],
        'observed_pp':[observed[2][i*88+36] for i in range(2)],
        'observed_turns':observed[5][19], 'observed_faints':observed[5][0],
        'party_sha256':[hashlib.sha256(b).hexdigest() for b in observed[:2]],
        'expected_party_sha256':[hashlib.sha256(b).hexdigest() for b in expected_parties],
        'snapshot_window':state.get('snapshot_window'),
        'seconds':elapsed}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['reference-rom','reference-elf','reference-state','candidate-rom','candidate-elf','candidate-state']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--name',required=True)
    args=parser.parse_args()
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,60}',args.name):parser.error('Use a safe new private run name.')
    output=ROOT/'.tools'/('turn-resolution-'+args.name)
    if output.exists():parser.error('Preserve old evidence; choose a new run name.')
    output.mkdir(parents=True)
    result={'passed':False,'scope':__doc__,'cases':CASES,'sides':{},'errors':[],
        'limits':{'overall_seconds':240,'case_seconds':CASE_SECONDS,'dispatches_per_case':MAX_DISPATCHES,
                  'instructions_per_call':2000000,'driver_seconds':120,'native_response_seconds':10},
        'disclosures':{
            'party':'Native CreateMon/SetMonData: fixedPID0/OT11223344 Rattata19,level50,IV31,EV0, fixed A names; two player slots and one enemy, all other slots zero.',
            'battle_overrides':'Both live battlers use controlled attack/defense/spAttack/spDefense100, per-case live types (Mystery9/9, or enemyGhost7/7), ability0, no item, neutral stages, maxHP105, chosen per-case Pound1, QuickAttack98 or Tackle33 slot0, PP10 and explicitly listed speeds/HP. These stats/types are not inferred from naturally created Rattata.',
            'rules':'TRAINER|BATTLE_TOWER=264 suppresses badge bonuses without LINK transport. Choices are preselected fixture RAM, not player-input evidence.',
            'controllers':'SETMONDATA is applied by actual native per-side handlers. Only explicitly listed presentation commands are ACKed; replacement and standby remain pending.',
            'claims':'Four living full chosen-turn resolutions (speed, priority, first-miss reply and Normal/Ghost immunity) and one partial KO replacement boundary. No battle UI, animation, audio, EXP, replacement completion, durable save or campaign proof.'},
        'runner_sha256':digest(Path(__file__)),'frozen_dependencies':{name:digest(ROOT/'scripts/quality'/name)
            for name in ['function_fixture.c','native_fixture_transport.py','native_abi.py',
                         'mechanics_fixtures.py','stat_fixtures.py','item_effect_fixtures.py']}}
    def wall_timeout(signum,frame):
        raise TimeoutError('Turn profile exceeded its240-second overall deadline.')
    previous_handler=signal.signal(signal.SIGALRM,wall_timeout)
    signal.alarm(240)
    try:
        validate_cases(CASES)
        result['protocol']=protocol_contract(ROOT/'.tools/pokeemerald-host')
        result['abi']=verify_abi(ROOT/'.tools/pokeemerald-host',output)
        executable,result['core']=build_turn_driver(output)
        resolve=constants(ROOT/'.tools/pokeemerald-host');props=property_ids(ROOT/'.tools/pokeemerald-host')
        for label in ['reference','candidate']:
            rom,elf,state=[getattr(args,label+'_'+part) for part in ['rom','elf','state']]
            identity,syms=verify_bundle(label,rom,elf,state,output,FUNCTIONS,ALLOCATIONS)
            identity['paths']={name:str(path.resolve()) for name,path in [('rom',rom),('elf',elf),('state',state)]}
            metadata=json.loads(state.with_suffix('.json').read_text())
            if metadata.get('controller_only') is not True:
                raise ValueError('Require a controller-derived in-battle snapshot lineage.')
            identity['capture_metadata_sha256']=digest(state.with_suffix('.json'))
            driver=Driver(executable,rom,state,output/label)
            side={'identity':identity,'cases':[]};result['sides'][label]=side
            try:
                for c in CASES:side['cases'].append(run_case(driver,c,syms,resolve,props,rom.read_bytes()))
            except (OSError,ValueError,KeyError,subprocess.SubprocessError):
                side['failure_trace']=getattr(driver,'turn_trace',[])
                side['failure_packets']=getattr(driver,'turn_packets',[])
                raise
            finally:driver.close()
            if digest(rom)!=identity['rom_sha256']:raise ValueError('Input cartridge changed during execution.')
        if any(digest(ROOT/'scripts/quality'/name)!=value for name,value in result['frozen_dependencies'].items()):
            raise ValueError('A shared fixture dependency changed during the run.')
        fields=['endpoint','observed_hp','observed_pp','observed_rng','observed_turns','observed_faints','party_sha256']
        result['paired']=[{'id':c['id'],'normalized_match':all(a[field]==b[field] for field in fields)}
            for c,a,b in zip(CASES,result['sides']['reference']['cases'],result['sides']['candidate']['cases'])]
        result['passed']=len(result['sides'])==2 and all(len(side['cases'])==len(CASES) for side in result['sides'].values()) and \
            len(result['paired'])==len(CASES) and all(row['normalized_match'] for row in result['paired']) and \
            all(c['passed'] for side in result['sides'].values() for c in side['cases'])
    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as error:
        result['errors'].append(str(error))
    finally:
        signal.alarm(0);signal.signal(signal.SIGALRM,previous_handler)
    result['counts']={'distinct_scenarios':len(CASES),'living_full_turn':sum(c['endpoint']=='next-turn' for c in CASES),'partial_ko_boundary':sum(c['endpoint']=='replacement-query' for c in CASES),
        'matched_reference':sum(c['passed'] for c in result['sides'].get('reference',{}).get('cases',[])),
        'matched_candidate':sum(c['passed'] for c in result['sides'].get('candidate',{}).get('cases',[]))}
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'errors':result['errors'],'output':str(output)}))
    raise SystemExit(0 if result['passed'] else 1)


if __name__=='__main__':main()
