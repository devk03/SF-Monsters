"""Exercise every native connection and gym warp in a finite Euler circuit."""
import argparse
import json
from pathlib import Path
from world_probe import Controller, ROOT
from walk_world import Walker


def circuit(plans, native, start):
    edges = {}
    for identifier, plan in plans.items():
        edges[identifier] = [(native[l['map']], 'port', l['direction'])
                             for l in plan['connections'] or []]
        edges[identifier] += [(p['target_id'], 'warp', (p['x'], p['y']))
                              for p in plan['access_points']
                              if p['kind'] in ('gym_entry', 'gym_exit', 'room_entry', 'room_exit')]
    total = sum(map(len, edges.values()))
    stack, result = [(start, None)], []
    while stack:
        node, arrival = stack[-1]
        if edges[node]:
            target, kind, action = edges[node].pop()
            stack.append((target, (node, target, kind, action)))
        else:
            stack.pop()
            if arrival:
                result.append(arrival)
    if len(result) != total:
        raise ValueError('Native event/connection graph is not one closed circuit')
    return result[::-1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', required=True, type=Path)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    engine, state = ROOT / '.tools/pokeemerald-world-host', args.state.resolve()
    c = Controller(engine / 'sf-world-blockout.gba', engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / args.name, state=state,
                   battery=state.with_suffix('.sav'))
    w = Walker(c, json.loads((ROOT / 'romhack/world/world.json').read_text()))
    checked = []
    try:
        start = w.location()[0]
        for owner, target, kind, action in circuit(w.plans, w.native, start):
            if w.location()[0] != owner:
                raise ValueError('Native circuit diverged before the next edge')
            if kind == 'port':
                rows=w.plans[owner]['rows'];width,height=len(rows[0]),len(rows)
                w.go({'left': (0, height//2), 'right': (width-1, height//2),
                      'up': (width//2, 0), 'down': (width//2, height-1)}[action])
                w.walk(action)
            else:
                w.go(action)
            if w.location()[0] != target:
                raise ValueError('Native edge landed in the wrong destination')
            checked.append({'from': owner, 'to': target, 'kind': kind,
                            'position': c.position()})
        if w.location()[0] != start or len(w.seen) != len(w.plans):
            raise ValueError('Circuit did not return safely after visiting every map')
        c.checkpoint('returned')
        result = {'passed': True, 'rom_sha256': c.digest(), 'maps': len(w.seen),
                  'connections': sum(e['kind'] == 'port' for e in checked),
                  'gym_warps': sum(e['kind']=='warp' and (e['from'].startswith('gym_') or e['to'].startswith('gym_')) for e in checked),
                  'room_warps': sum(e['kind']=='warp' and (e['from'].endswith('_room') or e['to'].endswith('_room')) for e in checked),
                  'checked': checked, 'seen': sorted(w.seen)}
        (c.output / 'returns-result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps({k: v for k, v in result.items() if k not in ('checked', 'seen')}))
    finally:
        (c.output / 'partial-edges.json').write_text(json.dumps(checked, indent=2))
        c.close()


if __name__ == '__main__':
    main()
