"""Navigate generated geometry with native controller input and read-only checks."""
import json
import struct
import sys
from collections import deque

from world_probe import Controller, ROOT
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from generate_world import generate

KEYS = {'right': 16, 'left': 32, 'up': 64, 'down': 128}
DELTAS = {'right': (1, 0), 'left': (-1, 0), 'up': (0, -1), 'down': (0, 1)}


class Walker:
    def __init__(self, controller, manifest):
        self.c, self.manifest = controller, manifest
        self.plans = {p['world_id']: p for p in generate(manifest)}
        groups = json.loads((ROOT / '.tools/pokeemerald-world-host/data/maps/map_groups.json').read_text())
        self.ids = {(g, n): name for g, group in enumerate(groups['group_order'])
                    for n, name in enumerate(groups[group])}
        self.names = {p['engine_map']: p['world_id'] for p in self.plans.values()}
        self.native = {p['native_id']: p['world_id'] for p in self.plans.values()}
        self.seen, self.transitions = set(), []

    def location(self):
        p = self.c.position()
        identifier = self.names[self.ids[(p['group'], p['number'])]]
        self.seen.add(identifier)
        return identifier, (p['x'], p['y'])

    def walk(self, direction, *, wet=False):
        before = self.location()
        for attempt in range(3):
            for frame in range(48):
                self.c.step(KEYS[direction], 1)
                if self.location() != before:
                    self.c.step(0, 30)
                    if self.location()[0] != before[0]:
                        self.c.step(0, 120)
                        self.transitions.append([before[0], self.location()[0]])
                    return self.location()
            if not wet:
                break
            self.c.step(0, 20)
            # Native HM prompts, never memory pokes or scripted warp shortcuts.
            for _ in range(7):
                self.c.tap(1, 36)
            self.c.step(0, 100)
        raise ValueError(f'Native movement blocked: {before} {direction}, wet={wet}')

    def path(self, plan, start, target):
        blocked = {(n['x'], n['y']) for n in plan['npcs']}
        blocked |= {(e['x'], e['y']) for e in plan['coord_events']
                    if (e['x'], e['y']) != target}
        pending, previous = deque([start]), {start: None}
        while pending:
            point = pending.popleft()
            if point == target:
                result = []
                while previous[point]:
                    prior, direction = previous[point]
                    result.append(direction); point = prior
                return result[::-1]
            for direction, (dx, dy) in DELTAS.items():
                nx, ny = point[0] + dx, point[1] + dy
                if not (0 <= nx < 32 and 0 <= ny < 24):
                    continue
                token = plan['rows'][ny][nx]
                if not plan['legend'][token][1] and (nx, ny) not in blocked and (nx, ny) not in previous:
                    previous[nx, ny] = (point, direction); pending.append((nx, ny))
        raise ValueError('No in-map path to native target')

    def go(self, target):
        identifier, start = self.location()
        plan = self.plans[identifier]
        for direction in self.path(plan, start, target):
            here = self.location()[1]
            dx, dy = DELTAS[direction]
            token = plan['rows'][here[1] + dy][here[0] + dx]
            self.walk(direction, wet=token in 'WV')
        self.c.step(0, 120)
        return self.location()

    def travel(self, destination):
        start = self.location()[0]
        pending, previous = deque([start]), {start: None}
        while pending and destination not in previous:
            node = pending.popleft()
            plan = self.plans[node]
            edges = [(self.native[l['map']], ('port', l['direction']))
                     for l in plan['connections'] or []]
            edges += [(p['target_id'], ('warp', (p['x'], p['y'])))
                      for p in plan['access_points'] if p['kind'] in ('gym_entry', 'gym_exit')]
            for target, action in edges:
                if target not in previous:
                    previous[target] = node, action; pending.append(target)
        if destination not in previous:
            raise ValueError('Unreachable world destination')
        actions, node = [], destination
        while previous[node]:
            prior, action = previous[node]
            actions.append((node, action)); node = prior
        for target, (kind, action) in actions[::-1]:
            if kind == 'warp':
                self.go(action)
            else:
                point = {'left': (0, 12), 'right': (31, 12),
                         'up': (16, 0), 'down': (16, 23)}[action]
                self.go(point); self.walk(action)
            if self.location()[0] != target:
                raise ValueError(f'Native transition missed {target}: {self.location()}')
        self.c.observations.append({'destination': destination, 'position': self.c.position()})

    def interact(self):
        self.go((12, 10)); self.c.tap(64); self.c.tap(1, 60)
        for _ in range(6):
            self.c.tap(2, 30)

    def badge(self, number):
        pointer, = struct.unpack('<I', self.c.read(self.c.symbols['gSaveBlock1Ptr'], 4))
        flag = 0x866 + number
        return bool(self.c.read(pointer + 0x1270 + flag // 8, 1)[0] & (1 << (flag % 8)))


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--stop-after', type=int, default=8)
    args = parser.parse_args()
    engine = ROOT / '.tools/pokeemerald-world-host'
    state = ROOT / args.state
    c = Controller(engine / 'sf-world-blockout.gba', engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / args.name, state=state,
                   battery=state.with_suffix('.sav'))
    w = Walker(c, json.loads((ROOT / 'romhack/world/world.json').read_text()))
    try:
        for n in range(1, args.stop_after + 1):
            if w.badge(n):
                continue
            if n == 8:
                for node in ('treasure_island', 'sutro_tower', 'lands_end'):
                    w.travel(node); w.interact(); c.picture(node)
            w.travel('gym_' + str(n)); w.interact()
            if not w.badge(n):
                raise ValueError(f'Gym {n} did not grant native access stamp')
            c.checkpoint('stamp-' + str(n)); print('Native stamp', n, flush=True)
        if args.stop_after == 8:
            w.travel('angel_island'); c.checkpoint('league')
            for node in ('route_' + f'{n:02d}' for n in range(1, 19)):
                w.travel(node); w.go((16, 12))
            w.travel('dogpatch'); c.checkpoint('returned-home')
        (c.output / 'coverage.json').write_text(json.dumps({
            'seen': sorted(w.seen), 'transitions': w.transitions,
            'scope': 'Native controller traversal; visual/native save gates separate'}, indent=2))
    except Exception:
        c.checkpoint('failure')
        raise
    finally:
        c.close()


if __name__ == '__main__':
    main()
