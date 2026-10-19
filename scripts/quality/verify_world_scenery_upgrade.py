"""Cold Continue an actual earlier Save where new scenery occupies the old tile."""
import argparse,json,struct
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker
from flash_audit import unpack_slot


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved',required=True,type=Path);parser.add_argument('--name',required=True)
    args=parser.parse_args();saved=args.saved.resolve()
    expected=json.loads((saved/'save-result.json').read_text())
    battery=(saved/'saved.sav').read_bytes()
    _,sections=max(slot for n in (0,1) if (slot:=unpack_slot(battery,n)))
    old=b''.join(sections[n] for n in range(1,5))
    engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',
                 ROOT/'.tools/benchmarks'/args.name,battery=saved/'saved.sav')
    def large(address,size):
        return b''.join(c.read(address+i,min(256,size-i)) for i in range(0,size,256))
    try:
        c.step(0,180);c.tap(8,90);c.tap(8,90)
        for _ in range(4):c.tap(1,90)
        c.step(0,180);w=Walker(c,json.loads((ROOT/'romhack/world/world.json').read_text()))
        identifier,point=w.location();plan=w.plans[identifier]
        previous=expected['position'];old_point=(previous['x'],previous['y'])
        if ((c.position()['group'],c.position()['number'])!=(previous['group'],previous['number'])
                or not plan['legend'][plan['rows'][old_point[1]][old_point[0]]][1]
                or point==old_point or plan['legend'][plan['rows'][point[1]][point[0]]][1]):
            raise ValueError('Fixture did not prove recovery from actual newly blocked ground')
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        sb2,=struct.unpack('<I',c.read(c.symbols['gSaveBlock2Ptr'],4))
        key,=struct.unpack('<I',c.read(sb2+0xac,4));old_key,=struct.unpack_from('<I',sections[0],0xac)
        money,=struct.unpack('<I',c.read(pointer+0x490,4));old_money,=struct.unpack_from('<I',old,0x490)
        if ((money^key)!=(old_money^old_key)
                or large(c.symbols['gPlayerParty'],600)!=old[0x238:0x490]
                or large(pointer+0x1270,0x12c)!=old[0x1270:0x139c]):
            raise ValueError('Scenery recovery changed party, money or saved flags')
        restored=c.position();c.checkpoint('recovered')
        if plan.get('room'):
            # New room furniture can occupy a tile from an earlier indoor Save.
            # Prove its fixed exit still reaches the district and the return door.
            w.travel(plan['room']['area']);w.travel(identifier)
        else:
            room=next(r['id'] for r in w.manifest['interiors'] if r['area']==identifier)
            w.travel(room);w.travel(identifier)
        c.checkpoint('safe-return')
        if (c.output/'safe-return.sav').read_bytes()!=battery:
            raise ValueError('Scenery recovery or safe return rewrote Flash')
        result=dict(passed=True,rom_sha256=c.digest(),old_rom_sha256=expected['rom_sha256'],
                    old_position=previous,recovered_position=restored,room_return_proven=True,
                    party_money_flags_flash_preserved=True,scope='actual ordinary Save on newly blocked ground')
        (c.output/'scenery-upgrade-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result))
    finally:c.close()


if __name__=='__main__':main()
