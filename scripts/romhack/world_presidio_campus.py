"""Presidio hall/common candidate with no new art or door/state IDs.

Reserve the plot and two-tile connector BEFORE frontage/furniture packing.
Furnish AFTER packing, before final attachment and resident/forest passes.
The caller supplies campus_hall: a warm7x4 shared-cell catalog alias. Its
front is decorative; the existing visitor-service entry remains at5,8.
"""

BOUNDS = (38, 1, 57, 10)
HALL = (44, 1)
CONNECTOR = (54, 9, 55, 22)
FORECOURT = (42, 5, 52, 8)
TREES = ((39, 2), (39, 5), (55, 2), (55, 5))
BENCHES = ((40, 8), (54, 8))
NOTICE = dict(style='shop_board', x=52, y=6, object=(52, 7), standing=(52, 8),
              script='WBCampus_presidio_Notice',
              text='Presidio common. A public place to sit or meet before a walk. Visitor help is at the northwest neighborhood desk.')


def _rectangle(left, top, right, bottom):
    return {(x, y) for y in range(top, bottom + 1) for x in range(left, right + 1)}


def reserved_cells(identifier):
    if identifier != 'presidio':
        return set()
    return _rectangle(*BOUNDS) | _rectangle(*CONNECTOR)


def _protected(plan, cards):
    cells = _rectangle(0, 0, 31, 23)
    for key in ('access_points', 'coord_events', 'bg_events'):
        for event in plan.get(key, []):
            x, y = event['x'], event['y']
            cells |= _rectangle(x-1, y-1, x+1, y+1)
    for npc in plan.get('npcs', []):
        x, y = npc['x'], npc['y']
        rx, ry = npc.get('range_x', 0), npc.get('range_y', 0)
        cells |= _rectangle(x-rx-1, y-ry-1, x+rx+1, y+ry+1)
    for block in plan.get('town_blocks', []):
        if cards[block['style']].get('architecture_type'):
            x, y, w, h = (block[k] for k in ('x', 'y', 'width', 'height'))
            cells |= _rectangle(x, y+h, x+w-1, y+h+1)
    return cells


def furnish(plan, grid, lanes, walks, occupied, token, cards):
    """Stage the whole composition, check safety/reachability, then commit it.

    Occupied plots, NPC roaming envelopes, existing event approaches and both
    retained frontage rows are refused. Existing road/sidewalk tokens survive.
    """
    if plan['world_id'] != 'presidio':
        return
    reserved = reserved_cells('presidio')
    width, height = len(grid[0]), len(grid)
    if any(not 0 < x < width-1 or not 0 < y < height-1 for x, y in reserved):
        raise ValueError('Presidio campus requires the expanded district bounds')
    hall = cards['campus_hall']['tiles']
    if len(hall) != 4 or any(len(row) != 7 for row in hall):
        raise ValueError('Presidio campus_hall must be the declared7x4 shared-cell alias')
    protected = _protected(plan, cards)
    blocked = {(x,y) for x,y in reserved if plan['legend'][grid[y][x]][1]}
    conflicts = reserved & (occupied | protected | blocked)
    if conflicts:
        raise ValueError('Reserve Presidio campus before frontage/furniture packing: ' + str(sorted(conflicts)[:8]))
    patches, blocks, solid = {}, [], set()

    def floor(cells):
        for x, y in cells - (lanes | walks):
            patches[x, y] = token('stone_walk', x, y)

    def put(style, x, y):
        card = cards[style]
        cells = {(x+dx, y+dy) for dy, row in enumerate(card['tiles']) for dx, _ in enumerate(row)}
        if not cells <= reserved or cells & (occupied | protected | lanes | walks | solid):
            raise ValueError('Presidio campus cannot safely place ' + style + ' at ' + str((x, y)))
        for dy, row in enumerate(card['tiles']):
            for dx, tile in enumerate(row):
                char = chr(0x100 + tile - 512)
                if char not in plan['legend']:
                    raise ValueError('Presidio campus alias references undeclared art')
                patches[x+dx, y+dy] = char
        solid.update(cells)
        blocks.append(dict(style=style, x=x, y=y, width=len(card['tiles'][0]),
                           height=len(card['tiles']), first_metatile=card['tiles'][0][0]))

    # A broad hall threshold and shallow formal court face the retained lawn.
    # The east-side public connector crosses the housing row at a reserved gap.
    floor(_rectangle(*FORECOURT))
    floor(_rectangle(40, 9, 55, 9))
    floor(_rectangle(*CONNECTOR))
    put('campus_hall', *HALL)
    for position in TREES:
        put('street_tree', *position)
    for position in BENCHES:
        put('bench_grass', *position)
    put(NOTICE['style'], NOTICE['x'], NOTICE['y'])
    if not patches.keys() <= reserved:
        raise ValueError('Presidio campus escaped its reservation')

    def walkable(x, y):
        return not plan['legend'][patches.get((x, y), grid[y][x])][1]
    seen = {(x, y) for x, y in lanes if walkable(x, y)}
    pending = list(seen)
    while pending:
        x, y = pending.pop()
        for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and walkable(nx, ny):
                seen.add((nx, ny));pending.append((nx, ny))
    thresholds = _rectangle(HALL[0], HALL[1]+4, HALL[0]+6, HALL[1]+5)
    targets = thresholds | _rectangle(*CONNECTOR) | {NOTICE['standing']}
    targets |= {(x+dx, y+1) for x, y in BENCHES for dx in (0, 1)}
    if not targets <= seen:
        raise ValueError('Presidio campus would strand a hall, bench, notice or connector approach')
    # No mutation occurs above this line. All metadata uses existing script
    # generation conventions and introduces neither a flag nor an entry warp.
    for (x, y), char in patches.items():
        grid[y][x] = char
    occupied.update(solid)
    plan['town_blocks'].extend(blocks)
    plan.setdefault('extra_street_signs', []).append(dict(script=NOTICE['script'], text=NOTICE['text']))
    ox, oy = NOTICE['object']
    sx, sy = NOTICE['standing']
    plan.setdefault('bg_events', []).append(dict(type='sign', x=ox, y=oy, elevation=0,
        player_facing_dir='BG_EVENT_PLAYER_FACING_ANY', script=NOTICE['script']))
    plan['access_points'].append(dict(kind='checkpoint', name='campus_common_notice',
                                     activation='interact', x=sx, y=sy))
    plan.setdefault('scenic_viewpoints', []).extend([
        dict(name='Campus hall forecourt', x=47, y=7),
        dict(name='Campus pedestrian connection', x=54, y=20),
    ])
    plan['presidio_campus'] = dict(bounds=list(BOUNDS), hall=[*HALL, 7, 4],
        forecourt=list(FORECOURT), connector=list(CONNECTOR),
        notice=dict(object=list(NOTICE['object']), standing=list(NOTICE['standing']), script=NOTICE['script']),
        visitor_service_entry=[5, 8], new_art_allocations=0, new_flags=0, new_warps=0,
        visual_acceptance='native review pending')
