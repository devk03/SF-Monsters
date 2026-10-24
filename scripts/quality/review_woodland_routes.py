"""Controller-only route captures and full live-native background review maps."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from world_probe import Controller,ROOT
from walk_world import Walker
from verify_world_seams import RenderAudit
from extract_world_review_maps import background


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,required=True)
    parser.add_argument('--name',required=True)
    parser.add_argument('--maps',default='route_14_mid,route_15,route_15_mid')
    args=parser.parse_args();state=args.state.resolve();engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
        ROOT/'.tools/benchmarks'/args.name,state=state,battery=state.with_suffix('.sav'))
    receipts=[]
    try:
        w=Walker(c,json.loads((ROOT/'romhack/world/world.json').read_text()));audit=RenderAudit(c)
        for identifier in args.maps.split(','):
            w.travel(identifier);plan=w.plans[identifier]
            if not plan.get('green_route_design'):raise ValueError('Expected an authored woodland route')
            w.go((16,12));c.step(0,120)
            audit.check(w,identifier+'-live-render')
            c.checkpoint(identifier)
            target=c.output/(identifier+'-full-map.png')
            background(audit,plan).resize((1024,768),Image.Resampling.NEAREST).save(target)
            receipts.append(dict(id=identifier,label=plan['label'],map=str(target),
                map_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                gameplay=str(c.output/(identifier+'.png')),live_render_verified=True))
            print(identifier,flush=True)
        (c.output/'routes.json').write_text(json.dumps(dict(rom_sha256=c.digest(),controller_only=True,
            routes=receipts,scope='Actual native route travel/render captures; optional wild encounters not exercised'),indent=2)+'\n')
    finally:c.close()


if __name__=='__main__':main()
