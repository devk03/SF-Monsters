"""Use native controls to prove the scenic pond bank blocks walking and Surf."""
import argparse,hashlib,json,struct
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker,KEYS
from verify_world_seams import RenderAudit
from extract_world_review_maps import background


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,required=True);parser.add_argument('--name',required=True)
    args=parser.parse_args();state=args.state.resolve();engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
        ROOT/'.tools/benchmarks'/args.name,state=state,battery=state.with_suffix('.sav'))
    def large(address,size):return b''.join(c.read(address+i,min(256,size-i)) for i in range(0,size,256))
    def protected():
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        return (large(pointer+0x560,0x2b0),large(pointer+0x1270,0x12c),
                c.read(pointer+0x490,4),large(c.symbols['gPlayerParty'],600))
    checked=[]
    try:
        w=Walker(c,json.loads((ROOT/'romhack/world/world.json').read_text()));w.travel('golden_gate_park')
        plan=w.plans['golden_gate_park'];pond=plan['scenic_pond']
        for index,point in enumerate(pond['south_bank']):
            w.go(tuple(point));before=protected();position=c.position()
            c.step(KEYS['up'],48);c.step(0,30)
            if c.position()!=position:raise ValueError('Scenic bank allowed walking into water')
            c.tap(1,60)
            if c.position()!=position or c.read(c.symbols['gPlayerAvatar'],1)[0]&8:
                raise ValueError('Scenic bank offered or entered Surf')
            if c.read(c.symbols['sGlobalScriptContextStatus'],1)[0]!=2:
                raise ValueError('Scenic bank opened an unintended field script')
            if protected()!=before:raise ValueError('Pond interaction changed protected state')
            c.picture('bank-'+str(index));checked.append(point)
        audit=RenderAudit(c);audit.check(w,'native-pond-render')
        image=background(audit,plan);target=c.output/'golden_gate_park-full-map.png'
        image.save(target)
        c.checkpoint('pond-bank-tested')
        if (c.output/'pond-bank-tested.sav').read_bytes()!=state.with_suffix('.sav').read_bytes():
            raise ValueError('Scenic pond test changed ordinary Flash')
        result=dict(passed=True,rom_sha256=c.digest(),banks=len(checked),checked=checked,
                    walking_blocked=True,surf_not_offered=True,protected_state_and_flash_unchanged=True,
                    live_render_verified=True,full_background=str(target),full_background_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),scope='Native scenic bank interaction; real bay Surf uses separate routes')
        (c.output/'pond-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    finally:c.close()


if __name__=='__main__':main()
