"""Read every actual street/shop sign with native controls and no state writes."""
import argparse,json,struct
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker,KEYS
from verify_town_life import close_dialogue


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',required=True,type=Path)
    parser.add_argument('--name',required=True)
    parser.add_argument('--park-stops',action='store_true',help='Read the 15 expanded reserve stops instead of the original 26 street signs')
    parser.add_argument('--parcel-notices',action='store_true',help='Read the two authored urban parcel notices')
    args=parser.parse_args()
    if args.park_stops and args.parcel_notices:parser.error('Choose one sign subset')
    state=args.state.resolve()
    engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
                 ROOT/'.tools/benchmarks'/args.name,state=state,battery=state.with_suffix('.sav'))
    checked=[]
    def read_large(address,size):
        return b''.join(c.read(address+i,min(256,size-i)) for i in range(0,size,256))
    def snapshot():
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        return (read_large(pointer+0x560,0x2b0),read_large(pointer+0x1270,0x12c),
                c.read(pointer+0x490,4),read_large(c.symbols['gPlayerParty'],600))
    try:
        w=Walker(c,json.loads((ROOT/'romhack/world/world.json').read_text()))
        for identifier,plan in w.plans.items():
            signs=plan.get('park_stops' if args.park_stops else 'parcel_notices' if args.parcel_notices else 'street_signs',[])
            if not signs:continue
            w.travel(identifier)
            for sign in signs:
                standing=tuple(sign['standing']);obj=tuple(sign['object'])
                w.go(standing);before=snapshot()
                delta=(obj[0]-standing[0],obj[1]-standing[1])
                direction={(1,0):'right',(-1,0):'left',(0,1):'down',(0,-1):'up'}[delta]
                c.step(KEYS[direction],1);c.step(0,12);c.tap(1,60)
                if c.read(c.symbols['sGlobalScriptContextStatus'],1)[0]==2:
                    raise ValueError('Street sign did not open its native dialogue')
                c.picture(identifier+'-'+sign['style'])
                close_dialogue(c)
                if w.location()!=(identifier,standing) or snapshot()!=before:
                    raise ValueError('Reading a street sign moved the player or changed protected state')
                checked.append({'area':identifier,'style':sign['style'],'safe_return':list(standing),
                                'party_money_inventory_flags_unchanged':True})
            print(identifier,flush=True)
        expected=15 if args.park_stops else 2 if args.parcel_notices else 26
        if len(checked)!=expected:raise ValueError('Not all '+str(expected)+' intended signs were exercised')
        c.checkpoint('read-all-signs')
        if (c.output/'read-all-signs.sav').read_bytes()!=state.with_suffix('.sav').read_bytes():
            raise ValueError('Reading street signs rewrote ordinary Flash')
        result=dict(passed=True,rom_sha256=c.digest(),signs=len(checked),checked=checked,
                    scope='actual native sign interaction and return; human art and text review separate')
        (c.output/'signs-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='checked'}))
    finally:c.close()


if __name__=='__main__':main()
