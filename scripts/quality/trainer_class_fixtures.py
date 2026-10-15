"""Native pure-getter aliases; no introduction, UI, durable-save or campaign proof."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import signal
import struct
import subprocess
import time

from mechanics_fixtures import ROOT,verify_bundle,digest
from check_creature_resources import Cartridge
from native_fixture_transport import Driver,writes
from native_abi import verify_native_layout
from turn_resolution_fixtures import build_turn_driver,call,read

BEFORE_HASH='1f404cb626cafde1edeb2d786d41e76471dd1a62446539dcd3e8bdea82186249'
TABLE_HASH='745460e89506abe565d5353287129f91cab9b347248254289f546d1f489acdce'
BUILDER=bytes.fromhex('bccfc3c6bebfccff')
POKEMANIAC=bytes.fromhex('cac9c51bc7bbc8c3bbbdff0000')
LEADER=bytes.fromhex('c6bfbbbebfccff000000000000')
IDS=tuple(range(855))+(855,65535)
ALIASES={320,321}
GETTER='GetTrainerClassNameFromId'
ALLOCATIONS={'gPlayerParty':600,'gEnemyParty':600,'gPlayerPartyCount':1,'gEnemyPartyCount':1,
             'gSaveBlock1Ptr':4,'gSaveBlock2Ptr':4,'gPokemonStoragePtr':4}
FAST=('gSaveBlock1Ptr','gSaveBlock2Ptr','gPokemonStoragePtr','gRngValue',
      'gPlayerPartyCount','gEnemyPartyCount')
CANARIES={0x03007d00:bytes([0xA5])*16,0x03007e20:bytes([0x5A])*16}
MAX_GETTER_STEPS=512
SIDE_SECONDS=60
STRIDES=(8,16,8,16) # flags0/default,1/custom,2/item-default,3/item-custom; native ABI proved.


def sha(data):return hashlib.sha256(data).hexdigest()


def span(cart,address,length):
    """Resolve an indirect team/function span with the same ROM/ELF section bounds."""
    if type(address) is not int or type(length) is not int or length<1:
        raise ValueError('Require a positive bounded ROM resource span.')
    offset=address-0x08000000
    if offset<0 or offset+length>len(cart.rom):raise ValueError('Indirect resource outside cartridge.')
    for _,kind,flags,base,file_offset,capacity,*_ in cart.sections:
        if kind==1 and flags&2 and base<=address and address+length<=base+capacity:
            start=file_offset+address-base
            if start+length>len(cart.elf) or cart.rom[offset:offset+length]!=cart.elf[start:start+length]:
                raise ValueError('Indirect ROM/ELF resource bytes differ.')
            return cart.rom[offset:offset+length]
    raise ValueError('Indirect resource has no file-backed ELF section.')


def resources(rom,elf,aliased):
    cart=Cartridge(rom,elf)
    table=cart.data('gTrainerClassNames');trainers=cart.data('gTrainers')
    if len(table)!=66*13 or sha(table)!=TABLE_HASH or table[23*13:24*13]!=POKEMANIAC or table[32*13:33*13]!=LEADER:
        raise ValueError('All66 original class rows must remain byte-exact.')
    if len(trainers)!=855*40:raise ValueError('Require855 complete native40-byte trainers.')
    for row in range(66):
        value=table[row*13:(row+1)*13]
        if 255 not in value:raise ValueError('Class row lacks a bounded native EOS.')
    alias=None
    if aliased:
        if cart.data('gSFBuilderClassName')!=BUILDER:raise ValueError('Require the exact single8-byte BUILDER constant.')
        alias=cart.symbols['gSFBuilderClassName'][0]
        base=cart.symbols['gTrainerClassNames'][0]
        if alias<base+len(table) and base<alias+8:raise ValueError('Alias overlaps original class table.')
    teams=[]
    for index in range(855):
        record=trainers[index*40:(index+1)*40]
        flags,category,count=record[0],record[1],record[32]
        if category>=66 or flags>3 or count>6:raise ValueError('Native trainer class/party allocation is invalid.')
        pointer=struct.unpack_from('<I',record,36)[0]
        if count and pointer%2:raise ValueError('Native team pointer is unaligned.')
        teams.append(span(cart,pointer,count*STRIDES[flags]) if count else b'')
        if index in ALIASES and (category!=23 or flags!=3 or count!=2 or len(teams[-1])!=32):
            raise ValueError('SF aliases require unchanged class23 and two native custom-item team records.')
    return {'cart':cart,'table':table,'trainers':trainers,'teams':teams,'alias':alias,
            'table_address':cart.symbols['gTrainerClassNames'][0]}


def compare_resources(before,after):
    checks={'all66_class_rows':before['table']==after['table'],
            'all855_scalar_records':all(before['trainers'][i*40:i*40+36]==after['trainers'][i*40:i*40+36] for i in range(855)),
            'all855_resolved_teams':before['teams']==after['teams'],
            'walden_steven_team32':all(len(before['teams'][i])==32 and before['teams'][i]==after['teams'][i] for i in ALIASES)}
    return checks


def expected_label(data,trainer_id,aliased):
    if type(trainer_id) is not int or not 0<=trainer_id<=65535:raise ValueError('Require native u16 trainer ID.')
    index=trainer_id if trainer_id<855 else 0
    category=data['trainers'][index*40+1]
    if aliased and index in ALIASES:
        if category!=23 or data['alias'] is None:raise ValueError('Alias class or constant is invalid.')
        return data['alias'],BUILDER
    row=data['table'][category*13:(category+1)*13]
    return data['table_address']+category*13,row[:row.index(255)+1]


def assess_return(line,expected,data):
    match=re.fullmatch(r'return ([0-9a-f]{8}) steps (\d+)',line)
    if not match or not 0<int(match[2])<MAX_GETTER_STEPS:raise ValueError('Getter did not return within its512-instruction audit bound.')
    pointer=int(match[1],16);address,label=expected
    return {'passed':pointer==address and span(data['cart'],pointer,len(label))==label,
            'pointer':hex(pointer),'expected_pointer':hex(address),'label_hex':label.hex(),'instructions':int(match[2])}


def verify_abi(engine,output):
    source=output/'trainer-class-layout.c'
    fields=['sizeof(struct Trainer)','offsetof(struct Trainer,trainerClass)','offsetof(struct Trainer,partySize)',
            'offsetof(struct Trainer,aiFlags)','offsetof(struct Trainer,party)',
            'sizeof(struct TrainerMonNoItemDefaultMoves)','sizeof(struct TrainerMonNoItemCustomMoves)',
            'sizeof(struct TrainerMonItemDefaultMoves)','sizeof(struct TrainerMonItemCustomMoves)',
            'sizeof(struct SaveBlock1)','sizeof(struct SaveBlock2)','sizeof(struct PokemonStorage)',
            'sizeof(struct Pokemon)','TRAINERS_COUNT','TRAINER_JOSH','TRAINER_TOMMY','TRAINER_CLASS_POKEMANIAC']
    source.write_text('#include "global.h"\n#include "data.h"\n#include "pokemon_storage_system.h"\n'
        '#include "constants/opponents.h"\n#include "constants/trainers.h"\n#include <stddef.h>\n'
        'const unsigned trainer_class_layout[]={'+','.join(fields)+'};\n')
    return verify_native_layout(engine,output,source,[40,1,32,28,36,8,16,8,16,0x3d88,0xf2c,0x83d0,100,855,320,321,23])


def ram(address,length):return 0x02000000<=address and address+length<=0x02040000


def protected_specs(driver,syms):
    fast=[(syms[name][0],syms[name][1]) for name in FAST]
    values=read(driver,fast)
    pointers=[int.from_bytes(value,'little') for value in values[:3]]
    sizes=[0x3d88,0xf2c,0x83d0]
    if any(not ram(address,length) for address,length in zip(pointers,sizes)):
        raise ValueError('Snapshot must contain valid native save/storage pointers.')
    specs=[(syms[name][0],syms[name][1]) for name in ['gPlayerParty','gEnemyParty','gBattleMons']]
    specs+=list(zip(pointers,sizes))+fast+[(a,len(b)) for a,b in CANARIES.items()]
    if any(a<c+len(value) and c<a+n for a,n in specs[:-2] for c,value in CANARIES.items()):
        raise ValueError('Canary overlaps a protected critical allocation.')
    return specs,fast,values


def run_getters(driver,data,syms,aliased):
    start=time.monotonic();driver.exchange(['reset'],0)
    specs,fast,fast_before=protected_specs(driver,syms)
    for address,value in CANARIES.items():driver.exchange(writes(address,value),0)
    before=read(driver,specs);rows=[]
    for trainer_id in IDS:
        if time.monotonic()-start>=SIDE_SECONDS:raise ValueError('Getter side exceeded its60-second deadline.')
        line=driver.exchange([call(syms,GETTER,trainer_id)],1)[0]
        row=assess_return(line,expected_label(data,trainer_id,aliased),data)
        row.update(trainer_id=trainer_id,fast_state_unchanged=read(driver,fast)==fast_before)
        row['passed']=row['passed'] and row['fast_state_unchanged'];rows.append(row)
    after=read(driver,specs)
    protected=[{'address':hex(a),'bytes':n,'before_sha256':sha(b),'after_sha256':sha(v),'passed':b==v}
               for (a,n),b,v in zip(specs,before,after)]
    return {'passed':len(rows)==857 and all(r['passed'] for r in rows) and all(r['passed'] for r in protected),
            'calls':rows,'protected':protected,'seconds':time.monotonic()-start,
            'canaries':before[-2:]==list(CANARIES.values()) and after[-2:]==list(CANARIES.values())}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for side in ('before','after'):
        for part in ('rom','elf','state'):parser.add_argument('--'+side+'-'+part,type=Path,required=True)
    parser.add_argument('--name',required=True);args=parser.parse_args()
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,60}',args.name):parser.error('Use a safe unique private run name.')
    output=ROOT/'.tools'/('trainer-class-'+args.name)
    if output.exists():parser.error('Preserve previous evidence; use a new run name.')
    output.mkdir(parents=True)
    result={'passed':False,'scope':__doc__,'errors':[],'sides':{},'runner_sha256':digest(Path(__file__)),
            'limits':{'overall_seconds':240,'side_seconds':SIDE_SECONDS,'ids_per_side':857,
                      'native_hard_instruction_cap':2000000,'accepted_instructions_per_getter':MAX_GETTER_STEPS,
                      'driver_seconds':120,'response_seconds':10},
            'disclosures':'Only declared parties, battle mons, save/storage blocks, pointer/count/RNG values and canaries are checked. Temporary CPU registers and driver call stack may change. No opaque-RAM or UI proof.',
            'dependencies':{name:digest(ROOT/'scripts/quality'/name) for name in
                ['function_fixture.c','native_fixture_transport.py','native_abi.py','turn_resolution_fixtures.py','mechanics_fixtures.py','check_creature_resources.py']}}
    def timeout(signum,frame):raise TimeoutError('Getter audit exceeded its240-second overall deadline.')
    previous=signal.signal(signal.SIGALRM,timeout);signal.alarm(240)
    try:
        if digest(args.before_rom)!=BEFORE_HASH:raise ValueError('Before cartridge must be immutable approved SF v72, not Emerald reference.')
        result['abi']=verify_abi(ROOT/'.tools/pokeemerald-host',output)
        executable,result['core']=build_turn_driver(output)
        bundles={}
        for side in ('before','after'):
            rom,elf,state=[getattr(args,side+'_'+part) for part in ('rom','elf','state')]
            identity,syms=verify_bundle(side,rom,elf,state,output,{GETTER},ALLOCATIONS)
            identity['paths']={name:str(path.resolve()) for name,path in [('rom',rom),('elf',elf),('state',state)]}
            metadata=state.with_suffix('.json');identity['metadata_sha256']=digest(metadata)
            if json.loads(metadata.read_text()).get('controller_only') is not True:
                raise ValueError('Require genuine controller-derived snapshot lineage.')
            address,size=syms[GETTER]
            if address%2 or not 2<=size<=256:raise ValueError('Getter function has an unexpected native allocation.')
            data=resources(rom,elf,side=='after');span(data['cart'],address,size)
            bundles[side]=data
            driver=Driver(executable,rom,state,output/side)
            try:observed=run_getters(driver,data,syms,side=='after')
            finally:driver.close()
            result['sides'][side]={'identity':identity,**observed,
                'table_sha256':sha(data['table']),'trainer_scalars_sha256':sha(b''.join(data['trainers'][i*40:i*40+36] for i in range(855))),
                'resolved_team_sha256':[sha(team) for team in data['teams']]}
            if digest(rom)!=identity['rom_sha256'] or digest(elf)!=identity['elf_sha256'] or digest(state)!=identity['state_sha256']:
                raise ValueError('A tested input changed during the audit.')
        result['resource_checks']=compare_resources(bundles['before'],bundles['after'])
        if any(digest(ROOT/'scripts/quality'/name)!=value for name,value in result['dependencies'].items()):
            raise ValueError('Frozen audit dependency changed during execution.')
        result['passed']=all(result['resource_checks'].values()) and all(s['passed'] and s['canaries'] for s in result['sides'].values())
    except (OSError,ValueError,KeyError,TypeError,struct.error,TimeoutError,subprocess.SubprocessError) as error:result['errors'].append(str(error))
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,previous)
    result['counts']={'expected_per_side':857,**{side:sum(row['passed'] for row in data['calls']) for side,data in result['sides'].items()}}
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'errors':result['errors'],'output':str(output)}))
    raise SystemExit(0 if result['passed'] else 1)


if __name__=='__main__':main()
