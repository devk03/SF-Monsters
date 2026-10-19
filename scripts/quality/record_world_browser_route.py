"""Record a finite native town/service/map loop for real browser replay.

This supplies controller inputs and native scene references. Only a subsequent
foreground browser observation can establish browser completion or audio health.
"""
import argparse
import hashlib
import json
from pathlib import Path

from walk_world import Walker, KEYS
from world_probe import Controller, ROOT
from verify_town_life import close_dialogue


class BrowserWalker(Walker):
    """Use real held keys compatible with the SDK's70ms minimum key hold.

    The standard native walker can release a direction after one frame as soon
    as a coordinate changes. Such a pulse is stretched by normal browser input,
    so it is not an equivalent replay. Keep this recorder's taps at8frames.
    """
    def walk(self, direction, *, wet=False):
        if wet:
            raise ValueError('This browser reference supports dry street walking only')
        before = self.location()
        for _ in range(4):
            self.c.tap(KEYS[direction], 45)
            if self.location() != before:
                if self.location()[0] != before[0]:
                    self.c.step(0, 120)
                    self.transitions.append([before[0], self.location()[0]])
                return self.location()
        raise ValueError(f'Browser held-key movement blocked: {before} {direction}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    state = args.state.resolve()
    engine = ROOT / '.tools/pokeemerald-world-host'
    c = Controller(engine / 'sf-world-blockout.gba', engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / args.name, state=state,
                   battery=state.with_suffix('.sav'))
    manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
    scenes = []

    def byte(symbol):
        return c.read(c.symbols[symbol], 1)[0]

    def scene(name):
        c.checkpoint(name)
        scenes.append({'name': name, 'map': w.location()[0],
                       'position': c.position(),
                       'at_frame': sum(frames for _, frames in c.inputs)})

    def guide():
        c.tap(8, 45)
        count = byte('sNumStartMenuActions')
        actions = list(c.read(c.symbols['sCurrentStartMenuActions'], count))
        target = actions.index(13)
        for _ in range((target - byte('sStartMenuCursorPos')) % count):
            c.tap(128)
        c.tap(1, 90)
        if byte('sSFGuideWindow') == 255:
            raise ValueError('Browser route reference failed to open the SF Map')
        scene('sf-map')
        c.tap(16, 30)
        c.tap(1, 30)
        if not byte('sSFGuideDetails'):
            raise ValueError('SF Map details did not open')
        scene('sf-map-details')
        c.tap(2, 60)
        if byte('sSFGuideWindow') == 255 or byte('sSFGuideDetails'):
            raise ValueError('B did not return from details to the map')
        c.tap(8, 60)
        if byte('sSFGuideWindow') != 255:
            raise ValueError('Start did not restore the field')

    try:
        w = BrowserWalker(c, manifest)
        if w.location()[0] != 'noe_valley':
            raise ValueError('Use a matching Noe Valley native checkpoint')
        origin = w.location()
        guide()
        w.travel('noe_valley_room')
        scene('repair-cafe')
        w.go((5, 7))
        c.step(64, 8)
        c.step(0, 12)
        c.tap(1, 60)
        if byte('sGlobalScriptContextStatus') == 2:
            raise ValueError('Rest counter did not start its native conversation')
        close_dialogue(c)
        scene('rest-service-returned')
        w.travel('noe_valley')
        w.travel('mission_bay')
        scene('mission-bay')
        w.travel('mission_bay_room')
        scene('neighborhood-cafe')
        w.travel('gym_6')
        scene('gym-site')
        # The site is a contributor stub; do not earn or alter its stamp here.
        w.travel('noe_valley')
        w.go(origin[1])
        scene('returned')
        if w.location() != origin:
            raise ValueError('Reference loop did not return to its start')
    finally:
        c.close()

    # Merge identical adjacent masks without changing a single input frame.
    rows = []
    for mask, frames in c.inputs:
        if rows and rows[-1][0] == mask:
            rows[-1][1] += frames
        else:
            rows.append([mask, frames])
    frames = sum(count for _, count in rows)
    seconds = frames * 280896 / 16777216
    if not 1 <= len(rows) <= 1000 or not 0 < seconds <= 599:
        raise ValueError('Recorded loop exceeds the existing browser replay bounds')
    route = ''.join(f'{mask},{count}\n' for mask, count in rows).encode()
    (c.output / 'route.csv').write_bytes(route)
    result = {'passed': True, 'rom_sha256': c.digest(),
              'state_input_sha256': hashlib.sha256(state.read_bytes()).hexdigest(),
              'input_sha256': hashlib.sha256(route).hexdigest(),
              'rows': len(rows), 'frames': frames, 'seconds': seconds,
              'maps': sorted(w.seen), 'scenes': scenes,
              'browser_completion_proven': False,
              'minimum_key_hold_frames': 8,
              'scope': 'Native reference for a bounded town/service/map browser loop; '
                       'full58-map native/WASM coverage and browser acceptance are separate'}
    (c.output / 'route-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'scenes'}))


if __name__ == '__main__':
    main()
