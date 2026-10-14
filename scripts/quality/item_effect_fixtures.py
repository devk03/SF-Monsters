"""Native table-based item effects on controlled Pokemon objects; no bag/turn/UI/save proof."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
from mechanics_fixtures import ROOT, battle_setup, battle_mon, build_driver, constants, digest, verify_bundle
from native_fixture_transport import writes
from native_abi import verify_native_layout
from stat_fixtures import property_ids

FUNCTIONS = {'CreateMon','SetMonData','CopyMon','ExecuteTableBasedItemEffect','PokemonUseItemEffects',
             'HealStatusConditions','CalculatePPWithBonus'}
ALLOCATIONS = {'gMain':1084,'gSaveBlock1Ptr':4,'gSaveBlock2Ptr':4,'gMapHeader':28,
               'gBattlerInMenuId':1,'gPotentialItemEffectBattler':1,'gBattlerPartyIndexes':8,
               'gBattleResults':68,'gBattleBufferA':2048,'gBattleBufferB':2048,
               'gPlayerParty':600,'gPlayerPartyCount':1}
MON,VALUE,SAVE1,SAVE2 = 0x0203f400,0x0203f500,0x02028000,0x0202c000
OWNER,SEED = 0x11223344,0x12345678
MOVES,BASE_PP = [1,43,55,52],[35,30,25,25]
ITEMS = {'ITEM_POTION','ITEM_SUPER_POTION','ITEM_MAX_POTION','ITEM_FULL_RESTORE',
         'ITEM_REVIVE','ITEM_MAX_REVIVE','ITEM_ANTIDOTE','ITEM_BURN_HEAL','ITEM_ICE_HEAL',
         'ITEM_AWAKENING','ITEM_PARALYZE_HEAL','ITEM_FULL_HEAL','ITEM_ETHER',
         'ITEM_MAX_ETHER','ITEM_ELIXIR','ITEM_MAX_ELIXIR'}
EXPECTED = {'return_value','hp','status','pp','battle_hp','battle_status','battle_status2',
            'battle_pp','healing_items','controller_flags','rng'}
CANARIES = {a:bytes([value])*16 for a,value in [(MON-16,161),(MON+100,162),
            (VALUE-16,163),(VALUE+16,164),(SAVE1-16,165),(SAVE1+0x3d88,166),
            (SAVE2-16,167),(SAVE2+0xf2c,168)]}
LAYOUT = ('sizeof(struct Pokemon)','sizeof(struct BoxPokemon)','sizeof(struct BattlePokemon)',
          'offsetof(struct Pokemon, status)','offsetof(struct Pokemon, level)',
          'offsetof(struct Pokemon, hp)','offsetof(struct Pokemon, maxHP)',
          'offsetof(struct BoxPokemon, checksum)','offsetof(struct BoxPokemon, secure)',
          'offsetof(struct BattlePokemon, pp)','offsetof(struct BattlePokemon, hp)',
          'offsetof(struct BattlePokemon, status1)','offsetof(struct BattlePokemon, status2)',
          'sizeof(struct SaveBlock1)','sizeof(struct SaveBlock2)','sizeof(struct Main)',
          'offsetof(struct Main, state)','offsetof(struct MapHeader, regionMapSectionId)',
          'sizeof(struct DisableStruct)','offsetof(struct BattleResults, numHealingItemsUsed)')
ABI = [100,80,88,80,84,86,88,28,32,36,40,76,80,0x3d88,0xf2c,1084,1080,20,28,3]
OBSERVATIONS = {'mon':100,'creation_template':100,'party_all600':600,'battle_mons':352,
    'save1':0x3d88,'save2':0xf2c,'gSaveBlock1Ptr':4,'gSaveBlock2Ptr':4,'gMain':1084,
    'gMapHeader':28,'gBattlerInMenuId':1,'gPotentialItemEffectBattler':1,'gActiveBattler':1,
    'gPlayerPartyCount':1,'gBattlerPartyIndexes':8,'gBattleResults':68,'gDisableStructs':112,
    'gBattleBufferA':2048,'gBattleBufferB':2048,'gBattleControllerExecFlags':4,
    'gBattleMoveDamage':4,'gBattleTypeFlags':4,'rng':4}


def uint(value,limit): return type(value) is int and 0 <= value <= limit


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases,list) or not 1 <= len(cases) <= 64: raise ValueError('Use1–64 independent item effects.')
    ids=set()
    for c in cases:
        if not isinstance(c,dict) or set(c)-{'id','derivation','item','hp','status','pp','pp_bonus',
                'move_index','in_battle','battle_status2','healing_items','rng_seed','expected'}:
            raise ValueError('Unknown item fixture control.')
        if not isinstance(c.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',c['id']) or c['id'] in ids or not isinstance(c.get('derivation'),str) or not c['derivation'].strip():
            raise ValueError('Unique item IDs and independent derivations required.')
        ids.add(c['id'])
        if c.get('item') not in ITEMS or type(c.get('in_battle',False)) is not bool: raise ValueError('Use a reviewed item and boolean battle mode.')
        for key,default,limit in [('hp',50,105),('status',0,4095),('pp_bonus',0,255),('move_index',0,3),
                                  ('battle_status2',0,0xffffffff),('healing_items',0,255),('rng_seed',SEED,0xffffffff)]:
            if not uint(c.get(key,default),limit): raise ValueError('Invalid native item input: '+key)
        if c.get('in_battle',False) and c['item'] in {'ITEM_REVIVE','ITEM_MAX_REVIVE'}:
            raise ValueError('Battle revive/copy-to-party dispatch is outside this profile.')
        pp=c.get('pp',BASE_PP)
        if not isinstance(pp,list) or len(pp)!=4 or any(not uint(v,base*(5+((c.get('pp_bonus',0)>>(2*i))&3))//5) for i,(v,base) in enumerate(zip(pp,BASE_PP))):
            raise ValueError('Starting PP must fit the four native move maxima.')
        e=c.get('expected')
        if not isinstance(e,dict) or set(e)!=EXPECTED: raise ValueError('Complete independent object/battle/resource/RNG expectations required.')
        for key,limit in [('return_value',1),('hp',105),('status',4095),('battle_hp',105),
                          ('battle_status',4095),('battle_status2',0xffffffff),('healing_items',255),('controller_flags',1),('rng',0xffffffff)]:
            if not uint(e[key],limit): raise ValueError('Expected item observation exceeds its native bound.')
        for key in ('pp','battle_pp'):
            if not isinstance(e[key],list) or len(e[key])!=4 or any(not uint(v,255) for v in e[key]): raise ValueError('Require four explicit PP oracles.')
    return cases


def expected_mon(hp,status,pp,bonus):
    """Independent full fixed-PID0 Rattata19/level50/IV31/EV0 object oracle."""
    plain=bytearray(48)
    struct.pack_into('<HHIBBH',plain,0,19,0,125000,bonus,70,0)
    struct.pack_into('<4H4B',plain,12,*MOVES,*pp)
    struct.pack_into('<BBHII',plain,36,0,21,50|(3<<7)|(4<<11)|(1<<15),0x3fffffff,0)
    result=bytearray(100);struct.pack_into('<II',result,0,0,OWNER)
    result[8:18]=bytes([187])*10;result[18:20]=bytes([2,2]);result[20:27]=bytes([187])*7
    struct.pack_into('<H',result,28,sum(struct.unpack('<24H',plain))&65535)
    struct.pack_into('<12I',result,32,*[v^OWNER for v in struct.unpack('<12I',plain)])
    struct.pack_into('<IBB7H',result,80,status,50,255,hp,105,76,55,92,45,55)
    return bytes(result)


def save_blocks():
    one,two=bytearray(0x3d88),bytearray(0xf2c)
    one[4:6]=bytes([0,10]);struct.pack_into('<HH',one,0x560,13,5)
    two[:8]=bytes([187])*7+b'\xff';two[8]=1;struct.pack_into('<I',two,10,OWNER)
    return bytes(one),bytes(two)


def program(c,syms,resolve,props):
    initial={'species':19,'hp':c.get('hp',50),'max_hp':105,'status':c.get('status',0),
             'status2':c.get('battle_status2',0),'attack':76,'defense':55,'speed':92,
             'sp_attack':45,'sp_defense':55}
    lines=battle_setup({'attacker':initial,'rng_seed':c.get('rng_seed',SEED)},syms,resolve)
    lines=[v for v in lines if not v.startswith('read ')]
    events=[]
    def write(a,v):lines.extend(writes(a,v))
    def call(name,*args):
        lines.append(f'call {syms[name][0]:x} '+' '.join(f'{v:x}' for v in (*args,*([0]*(8-len(args))))));events.append(('return',None,0))
    def set_data(name,value):
        write(VALUE,value if isinstance(value,bytes) else struct.pack('<I',value));call('SetMonData',MON,props[name],VALUE)
    def read(tag,a,n):lines.append(f'read {a:x} {n:x}');events.append(('read',tag,n))
    one,two=save_blocks();main=bytearray(1084);main[0x439]=2 if c.get('in_battle',False) else 0
    battle=bytearray(battle_mon(initial,resolve));struct.pack_into('<4H',battle,12,*MOVES)
    struct.pack_into('<I',battle,20,0x3fffffff);battle[32]=50;battle[43]=70
    battle[48:59]=bytes([187])*10+b'\xff';battle[60:68]=bytes([187])*7+b'\xff'
    struct.pack_into('<III',battle,68,125000,0,c.get('status',0));struct.pack_into('<I',battle,84,OWNER)
    battle[36:40]=bytes(c.get('pp',BASE_PP));battle[59]=c.get('pp_bonus',0)
    results=bytearray(68);results[3]=c.get('healing_items',0)
    resources={'gSaveBlock1Ptr':struct.pack('<I',SAVE1),'gSaveBlock2Ptr':struct.pack('<I',SAVE2),
               'gMain':main,'gMapHeader':bytes(20)+bytes([21])+bytes(7),
               'gBattlerInMenuId':b'\0','gPotentialItemEffectBattler':b'\0','gActiveBattler':b'\0',
               'gPlayerPartyCount':b'\1',
               'gBattlerPartyIndexes':bytes(8),'gBattleResults':results,'gDisableStructs':bytes(112),
               'gBattleBufferA':bytes([0xa5])*2048,'gBattleBufferB':bytes([0x5a])*2048,
               'gBattleControllerExecFlags':bytes(4),'gBattleMoveDamage':bytes(4),'gBattleTypeFlags':bytes(4)}
    write(SAVE1,one);write(SAVE2,two);write(syms['gBattleMons'][0],battle)
    for name,value in resources.items():write(syms[name][0],value)
    write(syms['gPlayerParty'][0],bytes(600))
    for a,v in CANARIES.items():write(a,v)
    call('CreateMon',MON,19,50,31,1,0,1,OWNER)
    set_data('MON_DATA_NICKNAME',bytes([187])*10);set_data('MON_DATA_OT_NAME',bytes([187])*7)
    for i,move in enumerate(MOVES):set_data('MON_DATA_MOVE'+str(i+1),move)
    for i,pp in enumerate(c.get('pp',BASE_PP)):set_data('MON_DATA_PP'+str(i+1),pp)
    for name,value in [('HP',c.get('hp',50)),('STATUS',c.get('status',0)),('PP_BONUSES',c.get('pp_bonus',0)),
                       ('MET_LOCATION',21),('MET_LEVEL',50),('MET_GAME',3),('POKEBALL',4),('OT_GENDER',1)]:set_data('MON_DATA_'+name,value)
    # The native API and its queued GetMonData must refer to the same party slot.
    call('CopyMon',syms['gPlayerParty'][0],MON,100)
    write(syms['gRngValue'][0],struct.pack('<I',c.get('rng_seed',SEED)))
    specs={'mon':(syms['gPlayerParty'][0],100),'creation_template':(MON,100),
           'party_all600':(syms['gPlayerParty'][0],600),'battle_mons':(syms['gBattleMons'][0],352),
           'save1':(SAVE1,len(one)),'save2':(SAVE2,len(two)),**{n:(syms[n][0],len(v)) for n,v in resources.items()},
           'rng':(syms['gRngValue'][0],4)}
    for tag,(a,n) in specs.items():read('before:'+tag,a,n)
    call('ExecuteTableBasedItemEffect',syms['gPlayerParty'][0],resolve(c['item']),0,c.get('move_index',0));events[-1]=('return','effect_return',0)
    for tag,(a,n) in specs.items():read('after:'+tag,a,n)
    for a,v in CANARIES.items():read('guard:'+str(a),a,len(v))
    return '\n'.join(lines)+'\n',events


def observe(c,rows,events):
    if len(rows)!=len(events):raise ValueError('Incomplete native item transcript.')
    values={}
    for row,(kind,tag,size) in zip(rows,events):
        if kind=='return':
            if not re.fullmatch(r'return [0-9a-f]{8} steps \d+',row):raise ValueError('Native item call did not return.')
            value=int(row.split()[1],16)
        else:
            value=bytes.fromhex(row)
            if len(value)!=size:raise ValueError('Native item read was truncated.')
        if tag:values[tag]=value
    for a,v in CANARIES.items():
        if values['guard:'+str(a)]!=v:raise ValueError('Native item write crossed a scratch ABI boundary.')
    before={k[7:]:v for k,v in values.items() if k.startswith('before:')}
    after={k[6:]:v for k,v in values.items() if k.startswith('after:')}
    if any(set(state)!=set(OBSERVATIONS) or any(len(state[name])!=size for name,size in OBSERVATIONS.items()) for state in (before,after)):
        raise ValueError('Incomplete declared native item object/resources.')
    initial_mon=expected_mon(c.get('hp',50),c.get('status',0),c.get('pp',BASE_PP),c.get('pp_bonus',0))
    if before['mon']!=initial_mon or before['creation_template']!=initial_mon or before['party_all600']!=initial_mon+bytes(500) or int.from_bytes(before['rng'],'little')!=c.get('rng_seed',SEED):
        raise ValueError('Native item setup disagrees with independent complete-object/RNG oracle.')
    e=c['expected'];wanted=dict(before)
    wanted['mon']=expected_mon(e['hp'],e['status'],e['pp'],c.get('pp_bonus',0))
    wanted['party_all600']=wanted['mon']+bytes(500)
    battle=bytearray(before['battle_mons']);struct.pack_into('<H',battle,40,e['battle_hp'])
    struct.pack_into('<II',battle,76,e['battle_status'],e['battle_status2']);battle[36:40]=bytes(e['battle_pp'])
    wanted['battle_mons']=bytes(battle)
    results=bytearray(before['gBattleResults']);results[3]=e['healing_items'];wanted['gBattleResults']=bytes(results)
    wanted['gBattleControllerExecFlags']=struct.pack('<I',e['controller_flags']);wanted['rng']=struct.pack('<I',e['rng'])
    if e['controller_flags']:
        buffer=bytearray(before['gBattleBufferA']);buffer[:4]=bytes(4);wanted['gBattleBufferA']=bytes(buffer)
    checks={name:after[name]==value for name,value in wanted.items()}
    return {'id':c['id'],'pass':values['effect_return']==e['return_value'] and all(checks.values()),
            'return_value':values['effect_return'],'expected_return_value':e['return_value'],'checks':checks,
            'mon_before':before['mon'].hex(),'mon_after':after['mon'].hex(),'mon_expected':wanted['mon'].hex(),
            'resource_hashes':{name:{'before':sha(before[name]),'after':sha(after[name]),'expected':sha(wanted[name])} for name in wanted},
            'expected':e,'scratch_canaries_intact':True,
            'pending_controller_request':{'command':0,'request':0,'party_mask':0,'answered':False} if e['controller_flags'] else None}


def unique_programs(cases,syms,resolve,props):
    programs=[program(c,syms,resolve,props) for c in cases]
    if len({p for p,_ in programs})!=len(cases):raise ValueError('Duplicate effective item fixtures.')
    return programs


def sha(data):
    import hashlib
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom','reference-elf','reference-state','candidate-rom','candidate-elf','candidate-state'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--cases',type=Path,default=ROOT/'data/quality/mechanics/item-effects.json')
    parser.add_argument('--name',required=True);args=parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',args.name):parser.error('Use a safe evidence name.')
    output=ROOT/'.tools/benchmarks'/args.name
    if output.exists():parser.error('Preserve prior evidence; choose another name.')
    cases=validate(json.loads(args.cases.read_text()));output.mkdir(parents=True)
    source=output/'item-layout.c'
    source.write_text('#include "global.h"\n#include "battle.h"\n#include <stddef.h>\nconst unsigned item_layout[] = {'+', '.join(LAYOUT)+'};\nconst struct Main item_main_flag = {.inBattle=TRUE};\n')
    engine=ROOT/'.tools/pokeemerald-host';layout=verify_native_layout(engine,output,source,ABI)
    subprocess.run(['arm-none-eabi-as','-mthumb-interwork','-o',str(output/'item-layout.o'),str(output/'item-layout.s')],check=True,timeout=10)
    subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.rodata',str(output/'item-layout.o'),str(output/'item-layout.bin')],check=True,timeout=10)
    symbols=subprocess.check_output(['arm-none-eabi-nm','-S','--defined-only',str(output/'item-layout.o')],text=True)
    match=re.search(r'^([0-9a-f]+) ([0-9a-f]+) [A-Za-z] item_main_flag$',symbols,re.M)
    data=(output/'item-layout.bin').read_bytes();flag=bytearray(1084);flag[0x439]=2
    if not match or int(match[2],16)!=1084 or data[int(match[1],16):int(match[1],16)+1084]!=flag:raise ValueError('Pinned Main.inBattle byte mask changed.')
    layout['in_battle_mask_probe_sha256']=digest(output/'item-layout.bin')
    executable,core=build_driver();resolve=constants(engine);props=property_ids(engine)
    dependencies=['mechanics_fixtures.py','native_fixture_transport.py','native_abi.py','stat_fixtures.py','function_fixture.c']
    evidence={'kind':'Native ExecuteTableBasedItemEffect function calls, controlled Pokemon/battle resources',
              'core':core,'layout':layout,'runner_sha256':digest(Path(__file__)),'cases_sha256':digest(args.cases),
              'dependencies':{n:digest(ROOT/'scripts/quality'/n) for n in dependencies},'sides':{},
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'limits':['No bag-item-use script or inventory consumption path invoked','Battle healing may queue GetMonData; no response is fabricated',
                        'No controller UI, battle action/turn, field-menu flow or durable save proof'],
              'bag_consumption_proven':False,'full_turn_proven':False,'presentation_proven':False,'durable_save_proven':False,'full_mechanics_gate_complete':False}
    for side in ('reference','candidate'):
        rom,elf,state=(getattr(args,side+'_'+n) for n in ('rom','elf','state'))
        identity,syms=verify_bundle(side,rom,elf,state,output,FUNCTIONS,ALLOCATIONS)
        programs=unique_programs(cases,syms,resolve,props)
        sequence=''.join(p for p,_ in programs);(output/(side+'-commands.txt')).write_text(sequence)
        process=subprocess.run([str(executable),str(rom),str(state)],input=sequence,capture_output=True,text=True,timeout=60)
        (output/(side+'-stdout.txt')).write_text(process.stdout);(output/(side+'-stderr.txt')).write_text(process.stderr)
        if process.returncode or digest(rom)!=identity['rom_sha256']:raise ValueError('Native item driver failed or ROM changed.')
        rows=process.stdout.splitlines();results=[]
        for c,(_,events) in zip(cases,programs):
            results.append(observe(c,rows[:len(events)],events));rows=rows[len(events):]
        if rows:raise ValueError('Unexpected trailing item observations.')
        evidence['sides'][side]={**identity,'cases':results}
    passed=sum(a['pass'] and b['pass'] for a,b in zip(evidence['sides']['reference']['cases'],evidence['sides']['candidate']['cases']))
    evidence.update(passed=passed,total=len(cases));(output/'result.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'passed':passed,'total':len(cases),'evidence':str(output)}))
    if passed!=len(cases):raise SystemExit(1)


if __name__=='__main__':main()
