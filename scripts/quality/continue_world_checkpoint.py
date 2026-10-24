"""Cold-boot a native Flash save; prove safe position and ordinary movement."""
import argparse
import json
import struct
from pathlib import Path
from world_probe import Controller, ROOT
from world_cold_continue import cold_continue
from walk_world import Walker, DELTAS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved', type=Path, required=True,
                        help='Directory containing saved.sav and save-result.json')
    parser.add_argument('--name', required=True)
    parser.add_argument('--allow-upgrade',action='store_true',
                        help='Verify an earlier ordinary Save with the same supported world identity')
    args = parser.parse_args()
    saved = args.saved.resolve()
    expected = json.loads((saved / 'save-result.json').read_text())
    engine = ROOT / '.tools/pokeemerald-world-host'
    c = Controller(engine / 'sf-world-blockout.gba', engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / args.name, battery=saved / 'saved.sav')
    w = Walker(c, json.loads((ROOT / 'romhack/world/world.json').read_text()))
    try:
        if expected['rom_sha256'] != c.digest() and not args.allow_upgrade:
            raise ValueError('Cold Continue receipt belongs to a different ROM')
        if args.allow_upgrade and (expected['save_magic'],expected['save_schema']) != (
                w.manifest['native']['save_magic'],w.manifest['native']['save_schema']):
            raise ValueError('Earlier Save has an incompatible world identity')
        cold_continue(c)
        if c.position() != expected['position']:
            raise ValueError('Cold native Continue changed the saved position')
        if bool(c.read(c.symbols['gPlayerAvatar'], 1)[0] & 8) != expected['surfing']:
            raise ValueError('Cold native Continue changed the traversal mode')
        from flash_audit import unpack_slot
        battery=(saved/'saved.sav').read_bytes()
        _,sectors=max(slot for n in (0,1) if (slot:=unpack_slot(battery,n)))
        old=b''.join(sectors[n] for n in range(1,5))
        def read(address,size):
            return b''.join(c.read(address+i,min(512,size-i)) for i in range(0,size,512))
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        sb2,=struct.unpack('<I',c.read(c.symbols['gSaveBlock2Ptr'],4))
        key,=struct.unpack('<I',c.read(sb2+0xac,4))
        old_key,=struct.unpack_from('<I',sectors[0],0xac)
        def bag(raw,cipher):
            return [(item,quantity^(cipher&65535)) for item,quantity in struct.iter_unpack('<HH',raw)]
        new_flags=read(pointer+0x1270,0x12c)
        old_flags=old[0x1270:0x139c]
        flag_changes=[i*8+bit for i,(a,b) in enumerate(zip(old_flags,new_flags))
                      for bit in range(8) if (a^b)&(1<<bit)]
        # Native tv.c updates FLAG_SYS_TV_WATCH during load/clock refresh.
        # This volatile bit is reported; every other saved flag must match.
        unexpected_flags=set(flag_changes)-{0x891}
        protected={
            'party/held items':read(c.symbols['gPlayerParty'],600)==old[0x238:0x490],
            'party count':c.read(c.symbols['gPlayerPartyCount'],1)==old[0x234:0x235],
            'money':(struct.unpack('<I',c.read(pointer+0x490,4))[0]^key)==(struct.unpack_from('<I',old,0x490)[0]^old_key),
            'inventory':bag(read(pointer+0x560,0x2e8),key)==bag(old[0x560:0x848],old_key),
            'flags':not unexpected_flags,
            'chapter':read(pointer+0x139c+0xf8*2,10)==old[0x139c+0xf8*2:0x139c+0xfd*2]}
        if not all(protected.values()):
            raise ValueError('Cold Continue changed '+', '.join(k for k,v in protected.items() if not v))
        identifier, (x, y) = w.location()
        plan = w.plans[identifier]
        for direction in ('right', 'left', 'down', 'up'):
            dx, dy = DELTAS[direction]
            nx, ny = x + dx, y + dy
            if (0 <= nx < len(plan['rows'][0]) and 0 <= ny < len(plan['rows'])
                    and not plan['legend'][plan['rows'][ny][nx]][1]):
                if any((npc['x'], npc['y']) == (nx, ny) for npc in plan['npcs']):
                    continue
                w.walk(direction, wet=plan['rows'][ny][nx] == 'W')
                if w.location() == (identifier, (x, y)):
                    raise ValueError('Cold Continue left controls stuck')
                break
        else:
            raise ValueError('No safe movement test beside the cold Continue position')
        c.checkpoint('continued')
        if (c.output / 'continued.sav').read_bytes() != (saved / 'saved.sav').read_bytes():
            raise ValueError('Cold Continue or movement modified the original Flash')
        result = {'passed': True, 'restored_position': expected['position'],
                  'movement_position': c.position(), 'surfing': expected['surfing'],
                  'flash_unchanged': True, 'rom_sha256': c.digest()}
        result.update(old_rom_sha256=expected['rom_sha256'],party_money_inventory_flags_chapter_preserved=True)
        result['native_tv_flag_changes']=[hex(flag) for flag in flag_changes]
        (c.output / 'continue-result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    finally:
        c.close()


if __name__ == '__main__':
    main()
