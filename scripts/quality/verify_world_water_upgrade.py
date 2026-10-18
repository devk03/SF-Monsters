"""Cold-continue real earlier land/Surf saves against a newly widened bay route."""
import argparse,json,struct
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker
from flash_audit import unpack_slot


def check(saved,name,surfing):
    expected=json.loads((saved/'save-result.json').read_text());battery=(saved/'saved.sav').read_bytes()
    if expected['surfing']!=surfing:raise ValueError('Earlier ordinary Save has the wrong traversal mode')
    _,sections=max(slot for n in (0,1) if (slot:=unpack_slot(battery,n)))
    old=b''.join(sections[n] for n in range(1,5))
    manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    if (expected['save_magic'],expected['save_schema'])!=(manifest['native']['save_magic'],manifest['native']['save_schema']):
        raise ValueError('Water upgrade must preserve the supported save identity')
    engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
                 ROOT/'.tools/benchmarks'/name,battery=saved/'saved.sav')
    try:
        c.step(0,180);c.tap(8,90);c.tap(8,90)
        for _ in range(4):c.tap(1,90)
        c.step(0,180);w=Walker(c,manifest);identifier,point=w.location();plan=w.plans[identifier]
        old_point=tuple(expected['position'][k] for k in ('x','y'))
        if identifier!='route_17' or plan['rows'][old_point[1]][old_point[0]]!='W':
            raise ValueError('Fixture no longer covers the actual old shore/new bay geometry')
        actual_surf=bool(c.read(c.symbols['gPlayerAvatar'],1)[0]&8)
        if actual_surf!=surfing or (plan['rows'][point[1]][point[0]]=='W')!=surfing:
            raise ValueError('Continue silently changed land/water mode')
        if not surfing and point==old_point:raise ValueError('Old dry save was not recovered out of new water')
        if surfing and c.position()!=expected['position']:raise ValueError('Valid Surf save unnecessarily relocated')
        restored=c.position();c.checkpoint('continued')
        if not surfing:
            w.go((5,12));before=w.location()
            try:w.walk('right',wet=True)
            except ValueError:
                if w.location()!=before:raise
            else:raise ValueError('Continue let a pre-badge save bypass the Surf gate')
        w.travel('north_beach');c.checkpoint('safe-exit')
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        for flag in list(range(0x20,0x4a))+list(range(0x867,0x86f)):
            if bool(old[0x1270+flag//8]&(1<<(flag%8)))!=bool(c.read(pointer+0x1270+flag//8,1)[0]&(1<<(flag%8))):
                raise ValueError('Upgrade changed an unrelated badge/module flag')
        if (c.output/'safe-exit.sav').read_bytes()!=battery:raise ValueError('Cold Continue/movement changed Flash')
        result={'passed':True,'mode':'surf' if surfing else 'land','old_rom_sha256':expected['rom_sha256'],
                'new_rom_sha256':c.digest(),'old_position':expected['position'],'continued_position':restored,
                'exit_position':c.position(),'flash_unchanged':True,'badge_module_flags_unchanged':True,
                'pre_badge_surf_rejected':not surfing}
        (c.output/'water-upgrade-result.json').write_text(json.dumps(result,indent=2));return result
    finally:c.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--land-save',required=True,type=Path);parser.add_argument('--surf-save',required=True,type=Path)
    parser.add_argument('--name',required=True);args=parser.parse_args()
    for surfing,saved in ((False,args.land_save),(True,args.surf_save)):
        print(json.dumps(check(saved.resolve(),args.name+('-surf' if surfing else '-land'),surfing)),flush=True)


if __name__=='__main__':main()
