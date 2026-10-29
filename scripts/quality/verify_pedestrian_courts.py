"""Walk each planted court's passage both ways, confined to its reserved footprint."""
import argparse,copy,json,time
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker
from verify_world_seams import RenderAudit


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,required=True);parser.add_argument('--name',required=True)
    args=parser.parse_args();state=args.state.resolve();engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
        ROOT/'.tools/benchmarks'/args.name,state=state,battery=state.with_suffix('.sav'))
    c.deadline=time.monotonic()+600
    audit=RenderAudit(c)
    checked=[]
    try:
        w=Walker(c,json.loads((ROOT/'romhack/world/world.json').read_text()))
        for identifier,plan in w.plans.items():
            courts=plan.get('pedestrian_courts',[])
            if not courts:continue
            w.travel(identifier)
            for index,court in enumerate(courts):
                rest=tuple(court['rest'])
                if court.get('kind')=='nook':
                    left,top,right,bottom=court['bounds'];entry=(rest[0],bottom)
                else:
                    left=court['x'];top=court['top']-3;right=left+2;bottom=court['top']+5
                    entry=(left+1,bottom)
                local=copy.deepcopy(plan);local['legend']['!']=[11,True,3]
                local['rows']=[''.join(t if left<=xx<=right and top<=y<=bottom else '!'
                    for xx,t in enumerate(row)) for y,row in enumerate(plan['rows'])]
                w.go(entry);before=audit.protected();friends=list(audit.friendships);steps=audit.steps;trace=[list(entry)]
                for target in (rest,entry):
                    for _ in range(32):
                        current,here=w.location()
                        if current!=identifier:raise ValueError('Court walk unexpectedly left its district')
                        if here==target:break
                        # The owning path planner excludes complete NPC movement
                        # envelopes; blocking everything outside the footprint
                        # prevents a successful detour around the whole block.
                        direction=w.path(local,here,target)[0];w.walk(direction)
                        current,here=w.location()
                        if current!=identifier or not(left<=here[0]<=right and top<=here[1]<=bottom):
                            raise ValueError('Native court traversal left its reserved footprint')
                        trace.append(list(here))
                    else:raise ValueError('Court passage did not reach its endpoint')
                after=audit.protected()
                bound=4*((((audit.steps-steps)&0xffffffff)+127)//128)
                if any(new<old or new-old>bound for old,new in zip(friends,audit.friendships)):
                    raise ValueError("Friendship exceeded native walking-step bounds")
                if after!=before:
                    changes=[{'field':name,'before':old.hex() if isinstance(old,bytes) else old,'after':new.hex() if isinstance(new,bytes) else new} for name,old,new in zip(('party','party_count','money','bag','flags','chapter'),before,after) if old!=new]
                    (c.output/'protected-state-difference.json').write_text(json.dumps({'area':identifier,'court':index,'changes':changes,'friendship_bound':bound},indent=2))
                    c.checkpoint('state-change')
                    raise ValueError('Court traversal changed protected state: '+json.dumps(changes))
                checked.append(dict(area=identifier,index=index,entry=list(entry),court=list(rest),trace=trace,
                    both_directions=True,npc_envelopes_excluded=True))
            print(identifier,flush=True)
        if len(checked)!=26:raise ValueError('Not all 26 court passages were walked')
        c.checkpoint('all-courts-traversed')
        if (c.output/'all-courts-traversed.sav').read_bytes()!=state.with_suffix('.sav').read_bytes():
            raise ValueError('Court traversal changed ordinary Flash')
        result=dict(passed=True,rom_sha256=c.digest(),courts=len(checked),checked=checked,
                    protected_state_and_flash_unchanged=True,party_exception='Only checksum-validated friendship increases within native walking-step bounds',scope='Native entry-to-court and return inside each reserved passage or nook; not human composition approval')
        (c.output/'courts-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='checked'}))
    finally:c.close()


if __name__=='__main__':main()
