"""Visit compact town/scenic compositions using ordinary native controller travel."""
import argparse,json
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',required=True,type=Path)
    parser.add_argument('--name',required=True);args=parser.parse_args();state=args.state.resolve()
    engine=ROOT/'.tools/pokeemerald-world-host';manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',ROOT/'.tools/benchmarks'/args.name,
                 state=state,battery=state.with_suffix('.sav'));visited=[]
    try:
        w=Walker(c,manifest)
        for area in manifest['areas']+[{'id':manifest['league']['venue']}]:
            identifier=area['id'];w.travel(identifier);plan=w.plans[identifier]
            points=[(14,8)] if plan.get('town_blocks') and identifier not in ('golden_gate_park','lands_end','sutro_tower','angel_island') else []
            points += [(p['x'],p['y']) for p in plan.get('scenic_viewpoints',[])]
            if not points:points=[(16,8)]
            for number,point in enumerate(dict.fromkeys(points)):
                w.go(point);c.step(0,120);c.checkpoint(identifier+f'-{number}')
            visited.append(identifier);print(identifier,flush=True)
        c.checkpoint('tour-end')
        (c.output/'scene-tour.json').write_text(json.dumps({'rom_sha256':c.digest(),'controller_only':True,
            'areas':visited,'scope':'native placement/viewpoint tour, not human art approval'},indent=2))
    finally:c.close()


if __name__=='__main__':main()
