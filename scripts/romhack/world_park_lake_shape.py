"""Golden Gate Park lake geometry using existing General shoreline.

Reserve pond_cells BEFORE forest packing, then call
draw_pond(plan, grid, cards, lanes) BEFORE park stops. This replaces the former
rectangular painter; never run both pond painters.

Original Route104 and FarawayIsland_Interior use staggered C8/CA/D8/DA corners
with D1 between them. These native diagonal joins also form the inward bends;
there is no separate low-bank concave tile. A1 has D1's eight graphics words
and is already protected. Their behavior attributes differ (1010 vs1016);
retain A1 to preserve the existing scenic pond's behavior. Do not mix the tall C0/C2
cliff banks into this low shoreline. No new art, native IDs, VRAM slots, flags,
warps or HM behavior are required. Version-specific native evidence and
remaining visual gates are recorded in docs/game-spec.md section15.1.
"""

ORIGIN = (58, 35)
# Inclusive water spans relative to ORIGIN: two lobes around a north-bank cove.
SPANS = (
    ((3, 6), (12, 14)),
    ((2, 7), (11, 15)),
    ((1, 7), (11, 16)),
    ((0, 17),),
    ((0, 17),),
    ((0, 16),),
    ((1, 15),),
    ((2, 14),),
    ((5, 11),),
)
NATIVE_IDS = frozenset((1, 2, 0xa1, 0xc8, 0xc9, 0xca, 0xd0, 0xd2,
                        0xd8, 0xd9, 0xda))
# Keep every original southern-bank cell and join its west end to the rest glade.
SOUTH_BANK = frozenset((x, 44) for x in range(58, 76))
REST_LINK = frozenset((x, 44) for x in range(55, 58))
STABLE_CELLS = frozenset(((42, 19), (42, 20), (45, 19), (46, 19),
                          (50, 41), (50, 42), (53, 41), (54, 41),
                          (30, 48), (30, 49), (33, 48)))


def _water():
    ox, oy = ORIGIN
    return {(ox+x, oy+y) for y, spans in enumerate(SPANS)
            for left, right in spans for x in range(left, right+1)}


def pond_cells(identifier):
    """Reserve the old rectangle plus its short walking link before trees grow."""
    if identifier != 'golden_gate_park':
        return set()
    return {(x, y) for y in range(35, 45) for x in range(58, 76)} | set(REST_LINK)


def _shore_tiles(water):
    # Cardinal exposed edges determine native bank words. Diagonal-only gaps
    # retain the original maps' staggered corner/fill joints, not tall cliffs.
    edges = {frozenset(): 0xa1,
             frozenset('N'): 0xc9, frozenset('S'): 0xd9,
             frozenset('W'): 0xd0, frozenset('E'): 0xd2,
             frozenset('NW'): 0xc8, frozenset('NE'): 0xca,
             frozenset('SW'): 0xd8, frozenset('SE'): 0xda}
    result = {}
    for x, y in water:
        exposed = frozenset(side for side, dx, dy in
                            (('N', 0, -1), ('S', 0, 1), ('W', -1, 0), ('E', 1, 0))
                            if (x+dx, y+dy) not in water)
        if exposed not in edges:
            raise ValueError('Lake contour needs an unsupported narrow bank at '+str((x, y)))
        result[x, y] = edges[exposed]
    return result


def _bindings(plan):
    keep = set(STABLE_CELLS)
    for key in ('access_points', 'coord_events', 'bg_events'):
        keep |= {(event['x'], event['y']) for event in plan.get(key, [])}
    for npc in plan.get('npcs', []):
        x, y = npc['x'], npc['y']
        rx, ry = npc.get('range_x', 0), npc.get('range_y', 0)
        keep |= {(xx, yy) for yy in range(y-ry, y+ry+1)
                 for xx in range(x-rx, x+rx+1)}
    for block in plan.get('town_blocks', []):
        keep |= {(block['x']+dx, block['y']+dy)
                 for dy in range(block['height']) for dx in range(block['width'])}
    return keep


def draw_pond(plan, grid, cards, lanes):
    """Stage and validate the entire reservation before changing grid/metadata.

    Cards identify only the legacy grass/filler replaced by native_park itself.
    A newly packed native tree, building, binding or existing trail is refused;
    this prevents late painting from cutting canopies or hiding route mistakes.
    Water/banks stay solid at land elevation3, matching the existing scenic pond.
    """
    if plan['world_id'] != 'golden_gate_park':
        return
    reserve = pond_cells(plan['world_id'])
    if reserve & (set(lanes) | _bindings(plan)):
        raise ValueError('Lake reservation overlaps a protected binding or trail')
    water = _water()
    if not water <= reserve:
        raise ValueError('Lake contour exceeds its forest reservation')
    patches = {point: (1, False, 3) for point in reserve-water}
    patches.update({point: (tile, True, 3) for point, tile in _shore_tiles(water).items()})
    # Plain grass keeps the old walking cells without the old rectangle's
    # straight brown lip running across the newly inset southern shore.
    patches.update({point: (1, False, 3) for point in SOUTH_BANK})
    allowed = set(NATIVE_IDS) | {4, 0x124}
    for style in ('grass', 'paving', 'grove', 'pine', 'cypress'):
        allowed |= {tile for row in cards[style]['tiles'] for tile in row}
    for (x, y), record in patches.items():
        if not (0 <= y < len(grid) and 0 <= x < len(grid[y])):
            raise ValueError('Lake reservation exceeds map bounds')
        old = plan['legend'].get(grid[y][x])
        if old is None or old[0] not in allowed:
            raise ValueError('Lake was not reserved before forest packing at '+str((x, y)))
        token = chr(0x800+record[0])
        if token in plan['legend'] and tuple(plan['legend'][token]) != record:
            raise ValueError('Lake native token has incompatible behavior')
    legend = {chr(0x800+n): [n, blocked, elevation]
              for n, blocked, elevation in patches.values()}
    metadata = dict(origin=list(ORIGIN), water=[list(p) for p in sorted(water)],
                    south_bank=[list(p) for p in sorted(SOUTH_BANK)],
                    shore_walk=[list(p) for p in sorted(reserve-water)],
                    rest_link=[list(p) for p in sorted(REST_LINK)],
                    solid_land_elevation=3, native_terrain=True,
                    shape='two lobes and a north-bank cove',
                    native_join_reference='Route104 / SouthernIsland_Interior / FarawayIsland_Interior')
    plan['legend'].update(legend)
    for (x, y), (n, _, _) in patches.items():
        grid[y][x] = chr(0x800+n)
    plan['scenic_pond'] = metadata
