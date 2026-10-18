"""Exercise the SF map from interiors, reserved gyms and active native Surf."""
import argparse,json,struct
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',required=True,type=Path)
    parser.add_argument('--name',required=True);args=parser.parse_args();state=args.state.resolve()
    engine=ROOT/'.tools/pokeemerald-world-host';manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',ROOT/'.tools/benchmarks'/args.name,
                 state=state,battery=state.with_suffix('.sav'));checked=[]
    try:
        w=Walker(c,manifest)
        def open_guide(expected):
            before=c.position();mode=c.read(c.symbols['gPlayerAvatar'],1)[0]&8
            c.tap(8,60);count=c.read(c.symbols['sNumStartMenuActions'],1)[0]
            actions=list(c.read(c.symbols['sCurrentStartMenuActions'],count));cursor=c.read(c.symbols['sStartMenuCursorPos'],1)[0]
            for _ in range((actions.index(13)-cursor)%count):c.tap(128)
            c.tap(1,90)
            if c.read(c.symbols['sSFGuideSelected'],1)[0]!=expected:raise ValueError('Guide selected the wrong parent destination')
            if c.read(c.symbols['sSFGuideWindow'],1)[0]==255:raise ValueError('Guide failed to allocate its context window')
            return before,mode
        def closed(before,mode):
            if c.position()!=before or c.read(c.symbols['gPlayerAvatar'],1)[0]&8!=mode:
                raise ValueError('Guide exit changed map position or traversal mode')
            if c.read(c.symbols['sSFGuideWindow'],1)[0]!=255:raise ValueError('Guide exit retained an allocated window')
        for destination,selection in (('dogpatch_room',0),('gym_1',3),('route_17',13)):
            w.travel(destination)
            if destination=='route_17':w.go((16,12))
            before,mode=open_guide(selection);c.picture(destination+'-map')
            c.tap(1,30);c.picture(destination+'-details');c.tap(2,60)
            if c.read(c.symbols['sSFGuideWindow'],1)[0]!=255:raise ValueError('B did not return to the menu')
            c.tap(2,60);closed(before,mode)
            before,mode=open_guide(selection);c.tap(8,60);closed(before,mode)
            identifier,(x,y)=w.location()
            target=(x+1,y) if destination!='route_17' else (16,13)
            w.go(target)
            if c.position()==before:raise ValueError('Guide exit left field controls frozen')
            checked.append({'context':destination,'selected':selection,'b_return':True,'start_exit':True,
                            'reopen':True,'movement_resumed':True,'surf_mode':bool(mode)})
            c.checkpoint(destination+'-returned');print(destination,flush=True)
        result={'passed':True,'rom_sha256':c.digest(),'contexts':checked,'scope':'native guide contexts and both exit modes; human visual approval separate'}
        (c.output/'guide-contexts.json').write_text(json.dumps(result,indent=2))
    finally:c.close()


if __name__=='__main__':main()
