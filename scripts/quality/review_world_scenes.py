"""Visit compact town/scenic compositions using ordinary native controller travel."""
import argparse,json
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',required=True,type=Path)
    parser.add_argument('--name',required=True)
    parser.add_argument('--engine',type=Path,default=ROOT/'.tools/pokeemerald-world-host')
    parser.add_argument('--only-area',help='Capture one destination after a verified interrupted tour')
    parser.add_argument('--areas',help='Capture an explicit comma-separated destination subset')
    parser.add_argument('--street-views',action='store_true',help='Inspect both sides and ends of each urban block')
    args=parser.parse_args()
    if args.only_area and args.areas:parser.error('Choose one destination selector')
    selected=set(args.areas.split(',')) if args.areas else ({args.only_area} if args.only_area else None)
    state=args.state.resolve()
    engine=args.engine.resolve();manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    allowed={a['id'] for a in manifest['areas']}|{manifest['league']['venue']}
    if selected and not selected<=allowed:raise ValueError('Unknown destination selection')
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',ROOT/'.tools/benchmarks'/args.name,
                 state=state,battery=state.with_suffix('.sav'));visited=[]
    try:
        w=Walker(c,manifest)
        for area in manifest['areas']+[{'id':manifest['league']['venue']}]:
            if selected and area['id'] not in selected:continue
            identifier=area['id'];w.travel(identifier);plan=w.plans[identifier]
            points=[(14,8)] if plan.get('town_blocks') and identifier not in ('golden_gate_park','lands_end','sutro_tower','angel_island') else []
            if args.street_views and plan.get('street_design'):
                occupied={(n['x']+dx,n['y']+dy) for n in plan['npcs']
                    for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
                    for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
                occupied|={(e['x'],e['y']) for e in plan['coord_events']}
                free=[(x,y) for y in (8,9,10,14,15) for x in range(2,30)
                      if not plan['legend'][plan['rows'][y][x]][1] and (x,y) not in occupied]
                for x,y in ((7,8),(24,8),(7,15),(24,15)):
                    for candidate in sorted(free,key=lambda p:abs(x-p[0])+abs(y-p[1])):
                        try:w.path(plan,w.location()[1],candidate)
                        except ValueError:continue
                        points.append(candidate);break
                    else:raise ValueError('No reachable street review viewpoint')
            points += [(p['x'],p['y']) for p in plan.get('scenic_viewpoints',[])]
            if plan.get('expanded_design'):
                blocked={(n['x']+dx,n['y']+dy) for n in plan['npcs']
                    for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
                    for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
                blocked|={(e['x'],e['y']) for e in plan['coord_events']}
                free=[(x,y) for y,row in enumerate(plan['rows']) for x,t in enumerate(row)
                      if not plan['legend'][t][1] and (x,y) not in blocked
                      and 2<=x<len(row)-2 and 2<=y<len(plan['rows'])-2]
                for target in ((44,28),(76,42),(40,52)):
                    for candidate in sorted(free,key=lambda p:(abs(p[0]-target[0])+abs(p[1]-target[1]),p[1],p[0])):
                        try:w.path(plan,w.location()[1],candidate)
                        except ValueError:continue
                        points.append(candidate);break
                    else:raise ValueError('Expanded district has no reachable review viewpoint')
            if not points:points=[(16,8)]
            for number,point in enumerate(dict.fromkeys(points)):
                w.go(point);c.step(0,120);c.checkpoint(identifier+f'-{number}')
            visited.append(identifier);print(identifier,flush=True)
        c.checkpoint('tour-end')
        (c.output/'scene-tour.json').write_text(json.dumps({'rom_sha256':c.digest(),'controller_only':True,
            'areas':visited,'scope':('selected destination' if selected else 'all destination')+' native placement/viewpoint tour, not human art approval'},indent=2))
    finally:c.close()


if __name__=='__main__':main()
