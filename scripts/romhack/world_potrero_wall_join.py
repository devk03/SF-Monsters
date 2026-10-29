"""Join Potrero's lower street wall with existing neighborhood art.

Call furnish after generic packing and ground finishing, before the shared
architecture attachment pass and expanded-resident placement. It replaces two
complete detached stamps without changing the earlier frontage selection index.
The v182 receipt is the baseline; this is not native or Save validation.
"""
from copy import deepcopy

OLD = ((24, 39, 3, 4, 'gable__sage'), (50, 39, 2, 4, 'flats__sage'))
NEIGHBORS = ((28, 38, 3, 4, 'gable'), (47, 38, 3, 4, 'arcade__sage'),
             (52, 42, 2, 1, 'bench'))
NEW = ((24, 38, 2, 4, 'shophouse_l'),
       (26, 38, 2, 4, 'flats_m__sage'),
       (50, 38, 2, 4, 'flats_r__sage'))


def _cells(x, y, width, height):
    return {(x + dx, y + dy) for dy in range(height) for dx in range(width)}


def _binding_cells(plan):
    cells = set()
    for key in ('access_points', 'coord_events', 'bg_events', 'scenic_viewpoints'):
        for event in plan.get(key, []):
            cells.add((event['x'], event['y']))
    for npc in plan.get('npcs', []):
        cells |= {(npc['x'] + dx, npc['y'] + dy)
                  for dx in range(-npc.get('range_x', 0), npc.get('range_x', 0) + 1)
                  for dy in range(-npc.get('range_y', 0), npc.get('range_y', 0) + 1)}
    return cells


def _reachable(plan, grid, patches, actors):
    height, width = len(grid), len(grid[0])
    def open_cell(point):
        x, y = point
        return point not in actors and not plan['legend'][patches.get(point, grid[y][x])][1]
    start = (28, 43)
    if not open_cell(start):
        raise ValueError('Potrero wall sidewalk start is blocked')
    seen, pending = {start}, [start]
    while pending:
        x, y = pending.pop()
        for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= p[0] < width and 0 <= p[1] < height and p not in seen and open_cell(p):
                seen.add(p)
                pending.append(p)
    return seen


def furnish(plan, grid, cards, token, lanes, walks, occupied, sea, shore):
    """Validate the complete transaction and commit it atomically in memory."""
    if plan['world_id'] != 'potrero_hill':
        return
    if plan['tile_profile'] != 'mixed_use' or len(grid) != 64 or any(len(row) != 96 for row in grid):
        raise ValueError('Potrero wall requires the expanded mixed-use map')
    def bounds(block):
        return tuple(block[k] for k in ('x', 'y', 'width', 'height'))
    old_cells = set().union(*(_cells(*entry[:4]) for entry in OLD))
    new_cells = set().union(*(_cells(*entry[:4]) for entry in NEW))
    envelope = old_cells | new_cells
    expected = {entry[:4]: entry[4] for entry in OLD + NEIGHBORS}
    found = {}
    retired = set()
    for index, block in enumerate(plan['town_blocks']):
        shape = bounds(block)
        footprint = _cells(*shape)
        if shape in expected:
            if shape in found or block['style'] != expected[shape]:
                raise ValueError('Potrero wall baseline stamp changed: ' + str(shape))
            card = cards.get(block['style'])
            if not card or len(card['tiles']) != shape[3] or any(len(row) != shape[2] for row in card['tiles']):
                raise ValueError('Potrero wall baseline card dimensions changed')
            if block['first_metatile'] != card['tiles'][0][0]:
                raise ValueError('Potrero wall baseline card identity changed')
            for dy, row in enumerate(card['tiles']):
                for dx, tile in enumerate(row):
                    char = chr(0x100 + tile - 512)
                    if grid[shape[1] + dy][shape[0] + dx] != char or plan['legend'].get(char) != [tile, True, 3]:
                        raise ValueError('Potrero wall baseline pixels or collision changed')
            found[shape] = deepcopy(block)
            if shape in {entry[:4] for entry in OLD}:
                retired.add(index)
        elif footprint & envelope:
            raise ValueError('Potrero wall intersects an unowned stamp')
    if set(found) != set(expected) or occupied & envelope != old_cells:
        raise ValueError('Potrero wall missing baseline ownership or contains unowned occupancy')
    bindings = _binding_cells(plan)
    if envelope & bindings or (new_cells - old_cells) & (set(lanes) | set(walks) | set(sea) | set(shore)):
        raise ValueError('Potrero wall would block a protected route or binding')
    for x, y in envelope - old_cells:
        if plan['legend'][grid[y][x]][1]:
            raise ValueError('Potrero wall would cover unowned solid ground')
    before = _reachable(plan, grid, {}, bindings)
    patches, blocks = {}, []
    # Fill only grass in the existing frontage sidewalk. Keep road, event,
    # actor and other occupied cells byte-for-byte unchanged.
    sidewalk = {(x, y) for x in range(24, 52) for y in (42, 43)}
    protected = set(lanes) | set(sea) | set(shore) | bindings | set(occupied)
    for x, y in sidewalk - protected:
        if grid[y][x] != token('grass', x, y):
            continue
        char = token('slab_walk', x, y)
        if plan['legend'].get(char, [None, True, None])[1:] != [False, 3]:
            raise ValueError('Potrero sidewalk tile is not walkable land')
        patches[x, y] = char
    for x, y in old_cells - new_cells:
        char = token('slab_walk', x, y)
        if plan['legend'].get(char, [None, True, None])[1:] != [False, 3]:
            raise ValueError('Potrero sidewalk tile is not walkable land')
        patches[x, y] = char
    for x, y, width, height, style in NEW:
        card = cards.get(style)
        if not card or not card.get('architecture_type') or not card.get('blocked') or len(card['tiles']) != height or any(len(row) != width for row in card['tiles']):
            raise ValueError('Potrero wall card missing or incompatible: ' + style)
        for dy, row in enumerate(card['tiles']):
            for dx, tile in enumerate(row):
                char = chr(0x100 + tile - 512)
                if plan['legend'].get(char) != [tile, True, 3]:
                    raise ValueError('Potrero wall card collision changed: ' + style)
                patches[x + dx, y + dy] = char
        blocks.append(dict(style=style, x=x, y=y, width=width, height=height,
                           first_metatile=card['tiles'][0][0]))
    after = _reachable(plan, grid, patches, bindings)
    if not (before - new_cells) <= after:
        raise ValueError('Potrero wall would strand previously reachable ground')
    # The bench and both rows of the street frontage remain reachable.
    if not {(x, y) for x in range(24, 52) for y in (42, 43)} <= after:
        raise ValueError('Potrero wall sidewalk is not continuously reachable')
    for (x, y), char in patches.items():
        grid[y][x] = char
    occupied.difference_update(old_cells)
    occupied.update(new_cells)
    plan['town_blocks'] = [block for i, block in enumerate(plan['town_blocks']) if i not in retired] + blocks
    plan['potrero_wall_join'] = dict(bounds=[24, 38, 51, 41], old_stamps=2,
                                    new_stamps=3, sidewalk_rows=[42, 43],
                                    limitations=['Native, Save and visual validation pending'])
