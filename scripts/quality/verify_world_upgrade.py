"""Cold-load an actual earlier world Save after actor/collision changes."""
import argparse
import json
import struct
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker
from flash_audit import unpack_slot


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved',required=True,type=Path)
    parser.add_argument('--name',required=True)
    parser.add_argument('--destination',default='north_beach')
    args=parser.parse_args()
    saved=args.saved.resolve();expected=json.loads((saved/'save-result.json').read_text())
    manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    identity=manifest['native']
    if (expected['save_magic'],expected['save_schema']) != (identity['save_magic'],identity['save_schema']):
        raise ValueError('Upgrade fixtures must retain the same supported world identity')
    battery=(saved/'saved.sav').read_bytes()
    slots=[slot for n in (0,1) if (slot:=unpack_slot(battery,n))]
    _,sectors=max(slots,key=lambda item:item[0]);old=b''.join(sectors[n] for n in range(1,5))
    engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
                 ROOT/'.tools/benchmarks'/args.name,battery=saved/'saved.sav')
    try:
        c.step(0,180);c.tap(8,90);c.tap(8,90)
        for _ in range(4):c.tap(1,90)
        c.step(0,180)
        w=Walker(c,manifest);identifier,point=w.location();plan=w.plans[identifier]
        old_point=tuple(expected['position'][k] for k in ('x','y'))
        envelope={(n['x']+dx,n['y']+dy) for n in plan['npcs']
                  for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
                  for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
        if old_point not in envelope:
            raise ValueError('Fixture does not reproduce an actor occupying the old saved position')
        if point==old_point or point in envelope or plan['legend'][plan['rows'][point[1]][point[0]]][1]:
            raise ValueError('Continue did not relocate to safe free ground')
        if bool(c.read(c.symbols['gPlayerAvatar'],1)[0]&8)!=expected['surfing']:
            raise ValueError('Continue changed the saved traversal mode')
        relocated=c.position();c.checkpoint('relocated')
        for section in plan.get('world_sections',[]):w.go((section['x'],section['y']))
        w.travel(args.destination);c.checkpoint('safe-exit')
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        # Preserve badge and reserved contributor flags, including bits that are
        # currently unset. Map/repel runtime variables legitimately change on load.
        flags=range(0x20,0x4a)
        flags=list(flags)+list(range(0x867,0x86f))
        for flag in flags:
            before=bool(old[0x1270+flag//8]&(1<<(flag%8)))
            after=bool(c.read(pointer+0x1270+flag//8,1)[0]&(1<<(flag%8)))
            if before!=after:raise ValueError('Upgrade changed unrelated badge/module state')
        if (c.output/'safe-exit.sav').read_bytes()!=battery:
            raise ValueError('Continue/movement wrote the original Flash')
        result={'passed':True,'old_rom_sha256':expected['rom_sha256'],'new_rom_sha256':c.digest(),
                'old_position':expected['position'],'relocated_position':relocated,
                'safe_exit':c.position(),'destination':args.destination,'flash_unchanged':True,
                'traversal_mode_preserved':True,'badge_and_module_flags_preserved':True}
        (c.output/'upgrade-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
    finally:c.close()


if __name__=='__main__':main()
