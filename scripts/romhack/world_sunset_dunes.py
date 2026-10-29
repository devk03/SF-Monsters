"""Replace the v185 beach tree with a small, walkable dune planting.

Call after the Outer Sunset shore/sand pass and before resident placement.
Cards must be sand-backed, walkable metatiles registered in the plan legend.
"""
from collections import deque

TREE = (12, 32)
PLANTS = (('dune_grass_1', 10, 27), ('dune_grass_2', 11, 28),
          ('dune_grass_3', 10, 39), ('dune_grass_1', 11, 40),
          ('dune_grass_2', 10, 56), ('dune_grass_3', 11, 57))
SAND = chr(0x800 + 0x124)


def _reachable(plan, grid, patches, actors):
    start = (16, 10)
    def walkable(point):
        x, y = point
        return point not in actors and not plan['legend'][patches.get(point, grid[y][x])][1]
    if not walkable(start):
        raise ValueError('Outer Sunset dunes: arrival blocked')
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for point in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
            if 0 <= point[0] < 96 and 0 <= point[1] < 64 and point not in seen and walkable(point):
                seen.add(point)
                queue.append(point)
    return seen


def furnish(plan, grid, cards, lanes, occupied, sea, shore):
    """Apply atomically to the expanded v185 shoreline; preserve all bindings."""
    if plan['world_id'] != 'outer_sunset':
        return
    if (plan['tile_profile'] != 'neighborhood' or len(grid) != 64
            or any(len(row) != 96 for row in grid)
            or plan['legend'].get(SAND) != [0x124, False, 3]):
        raise ValueError('Outer Sunset dunes: map or native sand changed')
    blocks = [b for b in plan['town_blocks'] if (b['x'], b['y']) == TREE]
    details = [d for d in plan.get('expanded_details', [])
               if (d['x'], d['y']) == TREE]
    if (len(blocks) != 1 or len(details) != 1
            or blocks[0] != dict(style='street_tree', x=12, y=32, width=2, height=2,
                                  first_metatile=cards['street_tree']['tiles'][0][0])
            or details[0] != dict(name='street_tree', x=12, y=32)):
        raise ValueError('Outer Sunset dunes: original tree identity changed')
    tree = blocks[0]
    tree_cells = {(12+dx, 32+dy) for dy in range(2) for dx in range(2)}
    card = cards['street_tree']
    if len(card['tiles']) != 2 or any(len(row) != 2 for row in card['tiles']):
        raise ValueError('Outer Sunset dunes: tree dimensions changed')
    for dy, row in enumerate(card['tiles']):
        for dx, tile in enumerate(row):
            char = chr(0x100 + tile - 512)
            if grid[32+dy][12+dx] != char or plan['legend'].get(char) != [tile, True, 3]:
                raise ValueError('Outer Sunset dunes: tree art or collision changed')
    plant_cells = {(x,y) for _,x,y in PLANTS}
    changed = tree_cells | plant_cells
    actors = {(n['x']+dx, n['y']+dy) for n in plan['npcs']
              for dx in range(-n.get('range_x',0), n.get('range_x',0)+1)
              for dy in range(-n.get('range_y',0), n.get('range_y',0)+1)}
    bindings = {(p['x'],p['y']) for key in ('access_points','warp_events','coord_events','bg_events','scenic_viewpoints')
                for p in plan.get(key,[]) if 'x' in p and 'y' in p}
    if changed & (set(lanes) | set(sea) | set(shore) | actors | bindings):
        raise ValueError('Outer Sunset dunes: protected route, water, actor or binding')
    if changed & set(occupied) != tree_cells:
        raise ValueError('Outer Sunset dunes: unexpected occupied cells')
    if any(grid[y][x] != SAND for x,y in plant_cells):
        raise ValueError('Outer Sunset dunes: planting ground changed')
    patches = {point:SAND for point in tree_cells}
    for style,x,y in PLANTS:
        plant = cards.get(style)
        if not plant or len(plant['tiles']) != 1 or len(plant['tiles'][0]) != 1:
            raise ValueError('Outer Sunset dunes: missing 1x1 card '+style)
        tile = plant['tiles'][0][0]
        char = chr(0x100 + tile - 512)
        if plan['legend'].get(char) != [tile, False, 3]:
            raise ValueError('Outer Sunset dunes: plant must be walkable '+style)
        patches[x,y] = char
    before = _reachable(plan, grid, {}, actors)
    after = _reachable(plan, grid, patches, actors)
    if not before <= after or not {(8,32),(12,32),(13,33)} <= after:
        raise ValueError('Outer Sunset dunes: beach approach disconnected')
    for (x,y),char in patches.items():
        grid[y][x] = char
    occupied.difference_update(tree_cells)
    plan['town_blocks'].remove(tree)
    plan['expanded_details'].remove(details[0])
    plan['sunset_dunes'] = dict(removed_tree=list(TREE), plantings=[[s,x,y] for s,x,y in PLANTS])
