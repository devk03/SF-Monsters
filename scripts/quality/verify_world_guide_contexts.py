"""Check native city-map location, backing palette and controls in all58maps."""
import argparse,json,struct,subprocess,sys
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',required=True,type=Path);parser.add_argument('--name',required=True)
    parser.add_argument('--group',choices=('places','routes','interiors'))
    args=parser.parse_args();state=args.state.resolve()
    if args.group is None:
        groups=[]
        for group in ('places','routes','interiors'):
            name=args.name+'-'+group
            subprocess.run([sys.executable,__file__,'--state',str(state),'--name',name,'--group',group],check=True)
            groups.append(json.loads((ROOT/'.tools/benchmarks'/name/'guide-contexts.json').read_text()))
        contexts=[c for result in groups for c in result['contexts']]
        if len(contexts)!=58 or len({c['map'] for c in contexts})!=58 or len({r['rom_sha256'] for r in groups})!=1:
            raise ValueError('Bounded guide groups do not cover exactly58maps on one cartridge')
        output=ROOT/'.tools/benchmarks'/args.name;output.mkdir(exist_ok=False)
        result=dict(passed=True,rom_sha256=groups[0]['rom_sha256'],maps=58,groups=[args.name+'-'+g for g in ('places','routes','interiors')],contexts=contexts,scope='Three bounded native guide-context groups; browser performance/visual acceptance separate')
        (output/'guide-contexts.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='contexts'}));return
    engine=ROOT/'.tools/pokeemerald-world-host'
    manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    areas=[a['id'] for a in manifest['areas']]+[manifest['league']['venue']]
    pixels={key:(round(point[0]*224/100),16+round(point[1]*112/100))
            for key,point in manifest['city_guide']['positions'].items()}
    interiors={x['id']:x['area'] for x in manifest['gyms']+manifest['interiors']}
    routes={r['id']:r for r in manifest['routes']}
    routes['league_route']={'from':manifest['league']['from_area'],'to':manifest['league']['venue']}
    symbol_rows=subprocess.check_output(['arm-none-eabi-nm','-S','--defined-only',
        str(engine/'sf-world-blockout.elf')],text=True).splitlines()
    edge_bytes=next(int(row.split()[1],16) for row in symbol_rows if row.split()[-1]=='sSFGuideEdges')
    if edge_bytes%len(routes) or edge_bytes//len(routes)<17:
        raise ValueError('Compiled region route table has an unsupported native stride')
    edge_stride=edge_bytes//len(routes)
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',ROOT/'.tools/benchmarks'/args.name,
                 state=state,battery=state.with_suffix('.sav'));checked=[]
    def byte(symbol):return c.read(c.symbols[symbol],1)[0]
    def read_large(address,length):
        return b''.join(c.read(address+i,min(256,length-i)) for i in range(0,length,256))
    def snapshot():
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        return (read_large(pointer+0x238,600),c.read(pointer+0x234,1),c.read(pointer+0x490,4),
                read_large(pointer+0x560,0x2b0),read_large(pointer+0x1270,0x32c))
    def palette():return c.read(c.symbols['gPlttBufferUnfaded']+13*32,32)+c.read(c.symbols['gPlttBufferFaded']+13*32,32)
    def open_map():
        c.tap(8,45);count=byte('sNumStartMenuActions')
        actions=list(c.read(c.symbols['sCurrentStartMenuActions'],count));target=actions.index(13)
        for _ in range((target-byte('sStartMenuCursorPos'))%count):c.tap(128)
        c.tap(1,90)
        if byte('sSFGuideWindow')==255:raise ValueError('SF map did not open in this context')
    try:
        w=Walker(c,manifest)
        for owner in w.plans:
            group='interiors' if owner in interiors else 'routes' if owner in routes else 'places'
            if group!=args.group:continue
            w.travel(owner)
            if owner=='route_17':w.go((16,12))
            position=c.position();before=snapshot();colors=palette()
            mode=byte('gPlayerAvatar')&8
            if owner=='route_17' and not mode:raise ValueError('Active-Surf context was accidentally dry')
            parent=interiors.get(owner,owner);kind=2 if owner in interiors else 0
            if owner in routes:
                route=routes[owner];parent=route['from'];a,b=pixels[parent],pixels[route['to']]
                # Read the compiled route's authored chart vertices, then derive
                # its half-distance independently of the producer's midpoint.
                edge_id=list(routes).index(owner);edge=c.read(c.symbols['sSFGuideEdges']+edge_id*edge_stride,17)
                points=[tuple(edge[5+n*2:7+n*2]) for n in range(edge[4])]
                if not 2<=edge[4]<=6 or points[0]!=a or points[-1]!=b:
                    raise ValueError('Compiled region corridor endpoints differ from its world connection')
                lengths=[max(abs(x-u),abs(y-v)) for (x,y),(u,v) in zip(points,points[1:])]
                remaining=sum(lengths)//2
                for (x,y),(u,v),length in zip(points,points[1:],lengths):
                    if remaining<=length:
                        def interpolate(start,end):
                            delta=end-start
                            return start+((remaining*abs(delta)+length//2)//length)*(1 if delta>=0 else -1)
                        here=(interpolate(x,u),interpolate(y,v));break
                    remaining-=length
                kind=1
            else:here=pixels[parent]
            open_map()
            expected=(areas.index(parent),here[0],here[1],kind)
            actual=tuple(byte(n) for n in ('sSFGuideCurrent','sSFGuideHereX','sSFGuideHereY','sSFGuideContext'))
            if actual!=expected or byte('sSFGuideSelected')!=expected[0]:raise ValueError(f'Wrong native current location: {owner}: {actual}, expected {expected}')
            c.picture('map-'+owner)
            c.tap(16,30);c.tap(1,30)
            if not byte('sSFGuideDetails'):raise ValueError('A did not open place details')
            c.tap(2,60)
            if byte('sSFGuideWindow')==255 or byte('sSFGuideDetails'):raise ValueError('B did not return from details to the map')
            if tuple(byte(n) for n in ('sSFGuideCurrent','sSFGuideHereX','sSFGuideHereY','sSFGuideContext'))!=expected:
                raise ValueError('Browsing moved the current-location marker')
            c.tap(8,60)  # Start closes directly to the field, including on Surf.
            if byte('sSFGuideWindow')!=255:raise ValueError('Start did not close the map')
            if c.position()!=position or byte('gPlayerAvatar')&8!=mode or snapshot()!=before or palette()!=colors:
                raise ValueError(f"{owner}: guide return mismatch: position={c.position()!=position},mode={(byte('gPlayerAvatar')&8)!=mode},protected={snapshot()!=before},palette={palette()!=colors}")
            open_map();c.tap(2,60);c.tap(2,60)
            if byte('sSFGuideWindow')!=255 or c.position()!=position or byte('gPlayerAvatar')&8!=mode or snapshot()!=before or palette()!=colors:
                raise ValueError('Reopen and B/B failed to restore the field')
            plan=w.plans[owner];_,point=w.location()
            events={(e['x'],e['y']) for e in plan['coord_events']}
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                target=point[0]+dx,point[1]+dy
                if not 1<=target[0]<=30 or not 1<=target[1]<=22 or target in events:continue
                if bool(plan['rows'][target[1]][target[0]] in ('W','V'))!=bool(mode):continue
                try:path=w.path(plan,point,target)
                except ValueError:continue
                if len(path)!=1:continue
                w.go(target)
                if c.position()==position:raise ValueError('Guide exit left field controls frozen')
                w.go(point);break
            else:raise ValueError('No adjacent movement-resume check point')
            checked.append({'map':owner,'place':parent,'marker':list(here),'kind':kind,'movement_resumed':True,'surf_mode_preserved':bool(mode)})
            print(owner,flush=True)
        if len(checked)!={'places':18,'routes':19,'interiors':21}[args.group]:raise ValueError('Guide group coverage is incomplete')
        c.checkpoint('guide-context-returned')
        if (c.output/'guide-context-returned.sav').read_bytes()!=state.with_suffix('.sav').read_bytes():
            raise ValueError('Reading the city map rewrote ordinary Flash')
        result=dict(passed=True,rom_sha256=c.digest(),maps=len(checked),current_location_palette_and_state_preserved=True,
                    controller_only=True,contexts=checked,scope='Actual native guide contexts and controls; visual approval separate')
        (c.output/'guide-contexts.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='contexts'}))
    finally:c.close()


if __name__=='__main__':main()
