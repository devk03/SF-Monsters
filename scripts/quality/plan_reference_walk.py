"""Plan controller input from pinned original map cells; replay remains authoritative."""
from pathlib import Path
import argparse
import heapq
import json
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / '.tools/pokeemerald'
PIN = '731ad5bfd6e6f265508d0efcca0ba42f9dcf5881'
GRASS = {13, 21, 0x1c6, 0x1c7, 0x25}
STEPS = [(0, -1, 64), (1, 0, 16), (-1, 0, 32), (0, 1, 128)]


def original(path):
    return subprocess.check_output(['git', 'show', PIN + ':' + path], cwd=ENGINE)


def plan(name, start, goal):
    if not re.fullmatch(r'[A-Za-z0-9_]+', name):
        raise ValueError('Use a pinned native map name.')
    metadata = json.loads(original(f'data/maps/{name}/map.json'))
    layouts = json.loads(original('data/layouts/layouts.json'))['layouts']
    layout = next(row for row in layouts if row['id'] == metadata['layout'])
    width, height = layout['width'], layout['height']
    data = original(layout['blockdata_filepath'])
    if len(data) != width * height * 2:
        raise ValueError('Native map dimensions do not match its cells.')
    cells = struct.unpack('<' + 'H' * (width * height), data)
    # Avoid authored NPC locations conservatively, including currently hidden ones.
    blocked = {(row['x'], row['y']) for row in metadata['object_events']} - {start, goal}

    def available(point):
        x, y = point
        return (0 <= x < width and 0 <= y < height and point not in blocked
                and not cells[y * width + x] & 0xc00)

    if not available(start) or not available(goal):
        raise ValueError('Endpoint is outside the static walkable map.')
    costs, previous, queue = {start: 0}, {}, [(0, start)]
    while queue:
        cost, point = heapq.heappop(queue)
        if cost != costs[point]:
            continue
        if point == goal:
            break
        for dx, dy, key in STEPS:
            next_point = point[0] + dx, point[1] + dy
            if not available(next_point):
                continue
            tile = cells[next_point[1] * width + next_point[0]] & 1023
            next_cost = cost + 1 + (20 if tile in GRASS else 0)
            if next_cost < costs.get(next_point, float('inf')):
                costs[next_point] = next_cost
                previous[next_point] = point, key
                heapq.heappush(queue, (next_cost, next_point))
    if goal not in costs:
        raise ValueError('No static walking path reaches this endpoint.')
    keys, point = [], goal
    while point != start:
        point, key = previous[point]
        keys.append(key)
    runs = []
    for key in reversed(keys):
        if runs and runs[-1][0] == key:
            runs[-1][1] += 16
        else:
            runs.append([key, 16])
    return runs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map', required=True)
    parser.add_argument('--start', type=int, nargs=2, required=True)
    parser.add_argument('--goal', type=int, nargs=2, required=True)
    parser.add_argument('--exit-up', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.resolve().relative_to(ROOT / '.tools/benchmarks')
    runs = plan(args.map, tuple(args.start), tuple(args.goal))
    rows = [line for key, duration in runs for line in (f'{key},{duration}', '0,40')]
    if args.exit_up:
        rows.append('64,16')
    rows.append('0,240')
    # Keep every previous controller plan; never overwrite benchmark evidence.
    with args.output.open('x') as file:
        file.write('\n'.join(rows) + '\n')
    print(json.dumps({'map': args.map, 'runs': runs,
                      'status': 'planned only; encounters/terrain/events need replay verification'}))


if __name__ == '__main__':
    main()
