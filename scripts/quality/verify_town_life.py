"""Controller-only neighborhood services and safe return proof; no quality approval."""
import argparse
import json
from pathlib import Path
from world_probe import Controller, ROOT
from walk_world import Walker


def close_dialogue(c):
    for _ in range(32):
        if c.read(c.symbols['sGlobalScriptContextStatus'],1)[0] == 2:
            return
        c.tap(1,60)
    raise ValueError('Town conversation did not release control')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',required=True,type=Path)
    parser.add_argument('--name',required=True)
    parser.add_argument('--only',help='One room ID for a bounded first smoke')
    args=parser.parse_args()
    manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    engine=ROOT/'.tools/pokeemerald-world-host'
    state=args.state.resolve()
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
                 ROOT/'.tools/benchmarks'/args.name,state=state,battery=state.with_suffix('.sav'))
    checked=[]
    try:
        w=Walker(c,manifest)
        rooms=[r for r in manifest['interiors'] if not args.only or r['id']==args.only]
        if not rooms:raise ValueError('No matching authored room')
        for room in rooms:
            w.travel(room['area']);w.go((16,8));c.picture(room['area']+'-street')
            w.travel(room['id']);c.picture(room['area']+'-room')
            if w.location()[1] != tuple(room['arrival']):raise ValueError('Door arrival differs')
            # Talk across each actual native counter, not through a script call.
            w.go(tuple(room['services']['rest']['standing']));c.tap(64);c.tap(1,60);c.picture(room['area']+'-rest-dialogue')
            if c.read(c.symbols['sGlobalScriptContextStatus'],1)[0]==2:
                raise ValueError('Rest counter did not reach its actor')
            close_dialogue(c)
            w.go(tuple(room['services']['shop']['standing']));c.tap(64);c.tap(1,60)
            if c.read(c.symbols['sGlobalScriptContextStatus'],1)[0]==2:
                raise ValueError('Shop counter did not reach its actor')
            for _ in range(5):c.tap(1,60)
            c.picture(room['area']+'-shop')
            for _ in range(8):c.tap(2,60)
            if c.read(c.symbols['sGlobalScriptContextStatus'],1)[0]!=2:
                raise ValueError('Shop cancellation left the field script active')
            w.travel(room['area'])
            if w.location()[1] != tuple(room['outside_arrival']):raise ValueError('Door return differs')
            checked.append({'area':room['area'],'room':room['id'],'rest_counter_released':True,
                            'shop_cancel_released':True,'safe_return':c.position()})
            print('Native local stop:',room['area'],flush=True)
        c.checkpoint('returned')
        (c.output/'town-life-result.json').write_text(json.dumps({
            'passed':True,'rom_sha256':c.digest(),'rooms':len(checked),'checked':checked,
            'scope':'actual door/counter/menu/return smoke; injured-party healing, economy, art and dialogue quality separate'},indent=2))
    finally:c.close()


if __name__=='__main__':main()
