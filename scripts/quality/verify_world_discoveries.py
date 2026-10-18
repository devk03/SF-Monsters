"""Controller-only local favor/discovery rewards and replay protection."""
import argparse,json,re,struct,sys
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker,KEYS
from verify_town_life import close_dialogue
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from world_discoveries import load


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',required=True,type=Path)
    parser.add_argument('--name',required=True);args=parser.parse_args()
    state=args.state.resolve();engine=ROOT/'.tools/pokeemerald-world-host'
    areas,catalog=load();manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',ROOT/'.tools/benchmarks'/args.name,
                 state=state,battery=state.with_suffix('.sav'));checked=[]
    try:
        w=Walker(c,manifest);values={f['name']:f['value'] for f in catalog['flags']}
        item_source=(engine/'include/constants/items.h').read_text()
        item_enum=item_source.split('enum {',1)[1].split('};',1)[0]
        if re.search(r'^\s+ITEM_\w+\s*=',item_enum,re.M):raise ValueError('Pinned sequential native item IDs changed')
        items={name:value for value,name in enumerate(re.findall(r'^\s+(ITEM_\w+),',item_enum,re.M))}
        def pointer(name):return struct.unpack('<I',c.read(c.symbols[name],4))[0]
        def flag(name):
            n=values[name];return bool(c.read(pointer('gSaveBlock1Ptr')+0x1270+n//8,1)[0]&(1<<(n%8)))
        def quantity(name):
            key=struct.unpack('<I',c.read(pointer('gSaveBlock2Ptr')+0xac,4))[0]&65535
            raw=c.read(pointer('gSaveBlock1Ptr')+0x560,120);total=0
            for offset in range(0,120,4):
                item,count=struct.unpack_from('<HH',raw,offset)
                if item==items[name]:total+=count^key
            return total
        def interact(standing,obj):
            w.go(tuple(standing));dx,dy=obj[0]-standing[0],obj[1]-standing[1]
            direction={(1,0):'right',(-1,0):'left',(0,1):'down',(0,-1):'up'}[(dx,dy)]
            c.step(KEYS[direction],1);c.step(0,12);c.tap(1,60)
            if c.read(c.symbols['sGlobalScriptContextStatus'],1)[0]==2:raise ValueError('Declared interaction did not start')
            close_dialogue(c)
        if any(flag(n) for n in values):raise ValueError('Use an actual earlier save with all local activities uncompleted')
        for area,spec in areas.items():
            w.travel(area);before=quantity(spec['item']);prior={n:flag(n) for n in values}
            if spec['kind']=='favor':
                npc=next(n for n in w.plans[area]['npcs'] if n['script']==f'WBTown_{area}_{spec["resident_index"]}')
                standing=(npc['x'],npc['y']-1)
                interact(standing,(npc['x'],npc['y']))
                if flag(spec['done_flag']) or quantity(spec['item'])!=before:raise ValueError('Request granted an early reward')
            interact(spec['standing'],spec['object'])
            if spec['kind']=='favor':
                if not flag(spec['found_flag']) or flag(spec['done_flag']) or quantity(spec['item'])!=before:
                    raise ValueError('Found favor object did not remain pending for its owner')
                interact(standing,(npc['x'],npc['y']))
            if not flag(spec['done_flag']) or quantity(spec['item'])!=before+1:raise ValueError('Local reward not granted exactly once')
            interact(spec['standing'],spec['object'])
            if spec['kind']=='favor':interact(standing,(npc['x'],npc['y']))
            if quantity(spec['item'])!=before+1:raise ValueError('Repeat interaction duplicated a reward')
            own={spec['done_flag'],spec['found_flag']}
            if any(flag(n)!=old for n,old in prior.items() if n not in own):raise ValueError('Local activity changed another district flag')
            checked.append({'area':area,'kind':spec['kind'],'reward':spec['item'],'quantity_before':before,
                            'quantity_after':quantity(spec['item']),'repeat_reward_rejected':True})
            c.picture(area+'-discovery');print(area,flush=True)
        c.checkpoint('completed-discoveries')
        result={'passed':True,'rom_sha256':c.digest(),'activities':len(checked),'checked':checked,
                'scope':'real field interactions, quantities, flags and replay protection; full-bag retry checked separately'}
        (c.output/'discoveries-result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='checked'}))
    finally:
        (c.output/'partial-discoveries.json').write_text(json.dumps(checked,indent=2));c.close()


if __name__=='__main__':main()
