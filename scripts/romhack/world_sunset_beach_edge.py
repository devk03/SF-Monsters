"""Join Ocean Beach's sand to its street edge without blocking old saves."""

SAND = chr(0x800 + 0x124)
STRIP = {(12, y) for start in (24, 36, 48) for y in range(start, start + 6)}
SOUTH = {(x, y) for y in range(56, 63) for x in range(13, 16)} | {(12, y) for y in range(60, 63)}
PLANTS = (('dune_grass_3', 12, 25), ('dune_grass_2', 12, 38),
          ('dune_grass_1', 12, 50), ('dune_grass_3', 14, 58),
          ('dune_grass_2', 13, 61))


def furnish(plan, grid, cards, lanes, occupied, sea, shore):
    if plan['world_id'] != 'outer_sunset':
        return
    changed = STRIP | SOUTH
    actors = {(n['x'] + dx, n['y'] + dy) for n in plan['npcs']
              for dx in range(-n.get('range_x', 0), n.get('range_x', 0) + 1)
              for dy in range(-n.get('range_y', 0), n.get('range_y', 0) + 1)}
    bindings = {(p['x'], p['y']) for key in ('access_points', 'warp_events',
                'coord_events', 'bg_events', 'scenic_viewpoints')
                for p in plan.get(key, []) if 'x' in p and 'y' in p}
    if changed & (set(lanes) | set(occupied) | set(sea) | set(shore) | actors | bindings):
        raise ValueError('Outer Sunset beach edge: protected cell')
    grass = cards['grass']['tiles']
    if len(grass) != 1 or len(grass[0]) != 1:
        raise ValueError('Outer Sunset beach edge: grass dimensions changed')
    token = chr(0x100 + grass[0][0] - 512)
    if plan['legend'].get(token) != [grass[0][0], False, 3] or any(
            grid[y][x] != token for x, y in changed):
        raise ValueError('Outer Sunset beach edge: expected open grass')
    if plan['legend'].get(SAND) != [0x124, False, 3]:
        raise ValueError('Outer Sunset beach edge: sand changed')
    patches = {point: SAND for point in changed}
    for style, x, y in PLANTS:
        tile = cards[style]['tiles'][0][0]
        char = chr(0x100 + tile - 512)
        if (x, y) not in changed or plan['legend'].get(char) != [tile, False, 3]:
            raise ValueError('Outer Sunset beach edge: invalid plant')
        patches[x, y] = char
    for (x, y), char in patches.items():
        grid[y][x] = char
    plan['sunset_beach_edge'] = dict(cells=len(changed), plantings=[[s, x, y] for s, x, y in PLANTS])
