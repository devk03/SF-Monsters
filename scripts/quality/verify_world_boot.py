"""Fresh native SF menu, Back/options return and real new-game Dogpatch spawn."""
import argparse
import json
import struct

from world_probe import Controller, ROOT
from walk_world import Walker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    engine = ROOT / '.tools/pokeemerald-world-host'
    c = Controller(engine / 'sf-world-blockout.gba', engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / args.name)

    def callback():
        return struct.unpack('<I', c.read(c.symbols['gMain'] + 4, 4))[0] & ~1

    def menu_ready():
        for n in range(16):
            task = c.read(c.symbols['gTasks'] + n * 40, 5)
            if task[4] and (struct.unpack_from('<I', task)[0] & ~1) == (c.symbols['Task_HandleMainMenuInput'] & ~1):
                return True
        return False

    def wait_menu():
        for _ in range(60):
            if menu_ready():
                return
            c.step(0, 30)
        raise ValueError('SF menu did not become ready without title-screen input')

    try:
        c.step(0, 180)
        wait_menu(); c.picture('sf-menu')
        c.tap(2, 90); wait_menu(); c.picture('back-to-sf-menu')
        c.tap(128); c.tap(1, 120); c.picture('native-options')
        if callback() == (c.symbols['CB2_MainMenu'] & ~1):
            raise ValueError('Options did not open from the SF menu')
        c.tap(2, 120); wait_menu(); c.picture('options-to-sf-menu')
        c.tap(64); c.tap(1, 120)
        for _ in range(64):
            if callback() == (c.symbols['CB2_Overworld'] & ~1):
                break
            c.tap(1, 120)
        else:
            raise ValueError('Native character/name flow did not reach the world')
        c.step(0, 180)
        w = Walker(c, json.loads((ROOT / 'romhack/world/world.json').read_text()))
        if w.location()[0] != 'dogpatch':
            raise ValueError('New SF Adventure did not begin in Dogpatch')
        c.checkpoint('newgame')
        result = dict(passed=True, rom_sha256=c.digest(), position=c.position(),
                      back_returns_sf_menu=True, options_returns_sf_menu=True,
                      native_newgame_reached_dogpatch=True,
                      scope='Fresh native boot/naming/spawn; ordinary Save/Continue checked separately')
        (c.output / 'boot-result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result))
    finally:
        c.close()


if __name__ == '__main__':
    main()
