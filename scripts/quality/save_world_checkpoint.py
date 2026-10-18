"""Use the ordinary native Save menu, then export its Flash for a cold boot."""
import argparse
import json
import struct
from pathlib import Path
from world_probe import Controller, ROOT
from flash_audit import unpack_slot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--rom',type=Path,help='Immutable matching cartridge for an upgrade fixture')
    parser.add_argument('--elf',type=Path,help='Its matching immutable ELF')
    args = parser.parse_args()
    if bool(args.rom) != bool(args.elf):parser.error('Provide --rom and --elf together')
    engine = ROOT / '.tools/pokeemerald-world-host'
    state = args.state.resolve()
    c = Controller(args.rom or engine / 'sf-world-blockout.gba', args.elf or engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / args.name, state=state,
                   battery=state.with_suffix('.sav'))
    try:
        expected = c.position()
        avatar = c.read(c.symbols['gPlayerAvatar'], 1)[0]
        c.tap(8, 60)
        count = c.read(c.symbols['sNumStartMenuActions'], 1)[0]
        actions = list(c.read(c.symbols['sCurrentStartMenuActions'], count))
        target = actions.index(5)  # pinned MENU_ACTION_SAVE
        cursor = c.read(c.symbols['sStartMenuCursorPos'], 1)[0]
        for _ in range((target - cursor) % count):
            c.tap(128)
        c.tap(1, 80)
        for _ in range(8):
            c.tap(1, 120)
        c.step(0, 240); c.checkpoint('saved')
        battery = (c.output / 'saved.sav').read_bytes()
        slots = [slot for n in (0, 1) if (slot := unpack_slot(battery, n))]
        if not slots:
            raise ValueError('Ordinary native Save produced no valid Flash slot')
        counter, sections = max(slots, key=lambda slot: slot[0])
        save = b''.join(sections[n] for n in range(1, 5))
        position = struct.unpack_from('<hhBB', save)
        if position != tuple(expected[k] for k in ('x', 'y', 'group', 'number')):
            raise ValueError('Native Flash position differs from the saved field position')
        identity = json.loads((ROOT / 'romhack/world/world.json').read_text())['native']
        if struct.unpack_from('<HH', save, 0x158c) != (identity['save_magic'], identity['save_schema']):
            raise ValueError('Ordinary Save lost the blockout identity')
        result = {'passed': True, 'flash_counter': counter, 'position': expected,
                  'surfing': bool(avatar & 8), 'rom_sha256': c.digest(),
                  'save_magic':identity['save_magic'],'save_schema':identity['save_schema'],
                  'scope': 'ordinary native Save and checksums; cold Continue checked separately'}
        (c.output / 'save-result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    finally:
        c.close()


if __name__ == '__main__':
    main()
