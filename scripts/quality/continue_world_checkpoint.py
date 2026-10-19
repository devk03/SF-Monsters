"""Cold-boot a native Flash save; prove safe position and ordinary movement."""
import argparse
import json
from pathlib import Path
from world_probe import Controller, ROOT
from world_cold_continue import cold_continue
from walk_world import Walker, DELTAS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved', type=Path, required=True,
                        help='Directory containing saved.sav and save-result.json')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    saved = args.saved.resolve()
    expected = json.loads((saved / 'save-result.json').read_text())
    engine = ROOT / '.tools/pokeemerald-world-host'
    c = Controller(engine / 'sf-world-blockout.gba', engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / args.name, battery=saved / 'saved.sav')
    w = Walker(c, json.loads((ROOT / 'romhack/world/world.json').read_text()))
    try:
        if expected['rom_sha256'] != c.digest():
            raise ValueError('Cold Continue receipt belongs to a different ROM')
        cold_continue(c)
        if c.position() != expected['position']:
            raise ValueError('Cold native Continue changed the saved position')
        if bool(c.read(c.symbols['gPlayerAvatar'], 1)[0] & 8) != expected['surfing']:
            raise ValueError('Cold native Continue changed the traversal mode')
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
        (c.output / 'continue-result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    finally:
        c.close()


if __name__ == '__main__':
    main()
