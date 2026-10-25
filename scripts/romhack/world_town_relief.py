"""Potrero Hill relief candidate using reserved General terrain only.

Call reserved_cells BEFORE packing buildings, frontage, courts and furniture.
Call furnish AFTER those passes, with the same lane/sidewalk/occupied sets.
The reservations deliberately replace decorative housing rows with upper
lookout courts; this must never be painted over an already-packed facade.
No room, gym, event, state, road or northwest service binding is introduced.
"""

# Each court sits behind a two-row native retaining face. The two terraces
# descend at different heights; stairs connect useful seating to real streets.
TERRACES = (
    dict(name='Upper hill lookout', bounds=(60, 15, 73, 22), stairs=66,
         landing=24, benches=((61, 18), (70, 18)), path_y=19,
         trees=((60, 15), (72, 15))),
    dict(name='Eastern stair garden', bounds=(82, 18, 92, 24), stairs=86,
         landing=28, benches=((82, 20), (90, 20)), path_y=21,
         trees=((82, 18), (91, 18))),
)


def _rectangle(left, top, right, bottom):
    return {(x, y) for y in range(top, bottom + 1) for x in range(left, right + 1)}


def reserved_cells(identifier):
    if identifier != 'potrero_hill':
        return set()
    result = set()
    for terrace in TERRACES:
        left, top, right, bottom = terrace['bounds']
        result |= _rectangle(left, top, right, bottom)
        x = terrace['stairs']
        result |= _rectangle(x, bottom + 1, x + 1, terrace['landing'])
    return result


def _bindings(plan):
    """Protect event standing space and complete authored NPC roaming ranges."""
    result = {(x, y) for y in range(24) for x in range(32)}
    for key in ('access_points', 'coord_events', 'bg_events'):
        for event in plan.get(key, []):
            x, y = event['x'], event['y']
            result |= _rectangle(x - 1, y - 1, x + 1, y + 1)
    for npc in plan.get('npcs', []):
        x, y = npc['x'], npc['y']
        rx, ry = npc.get('range_x', 0), npc.get('range_y', 0)
        result |= _rectangle(x - rx - 1, y - ry - 1, x + rx + 1, y + ry + 1)
    return result


def furnish(plan, grid, lanes, walks, occupied, token, cards):
    """Validate the whole candidate before changing a grid or its metadata.

    Main roads/sidewalks stay byte-identical. A real path through a ridge leaves
    a fully capped break. Existing roofs/fixtures cause a clear refusal, rather
    than being cut or partially hidden. All stairs remain ordinary elevation3.
    """
    if plan['world_id'] != 'potrero_hill':
        return
    reserved = reserved_cells(plan['world_id'])
    width, height = len(grid[0]), len(grid)
    if any(not 0 < x < width - 1 or not 0 < y < height - 1 for x, y in reserved):
        raise ValueError('Potrero relief requires the expanded district bounds')
    protected = _bindings(plan)
    # Retained house fronts keep both walking threshold rows, even when those
    # thresholds are local mews rather than members of the main sidewalk set.
    for block in plan.get('town_blocks', []):
        if not cards[block['style']].get('architecture_type'):
            continue
        x, y, w, h = (block[k] for k in ('x', 'y', 'width', 'height'))
        protected |= _rectangle(x, y + h, x + w - 1, y + h + 1)
    conflicts = reserved & (occupied | protected)
    if conflicts:
        raise ValueError('Reserve Potrero relief before building/frontage packing: ' + str(sorted(conflicts)[:8]))
    patches, legend, blocks, records, viewpoints = {}, {}, [], [], []

    def floor(x, y):
        if (x, y) not in lanes | walks:
            patches[x, y] = token('stone_walk', x, y)

    def terrain(x, y, tile, blocked):
        char = chr(0x800 + tile)
        entry = [tile, blocked, 3]
        if char in plan['legend'] and plan['legend'][char] != entry:
            raise ValueError('Conflicting native Potrero terrain legend')
        legend[char] = entry
        patches[x, y] = char

    def fixture(style, x, y):
        card = cards[style]
        cells = {(x + dx, y + dy) for dy, row in enumerate(card['tiles'])
                 for dx, _ in enumerate(row)}
        if not cells <= reserved or cells & (occupied | protected | lanes | walks):
            raise ValueError('Potrero relief fixture conflicts with a walking approach')
        for dy, row in enumerate(card['tiles']):
            for dx, tile in enumerate(row):
                patches[x + dx, y + dy] = chr(0x100 + tile - 512)
        blocks.append(dict(style=style, x=x, y=y, width=len(card['tiles'][0]),
                           height=len(card['tiles']), first_metatile=card['tiles'][0][0]))

    for terrace in TERRACES:
        left, top, right, bottom = terrace['bounds']
        stair = terrace['stairs']
        face_top = bottom - 1
        stairs = _rectangle(stair, face_top, stair + 1, bottom)
        if stairs & (lanes | walks):
            raise ValueError('Potrero relief stairs would repaint a main sidewalk')
        for y in range(top, terrace['landing'] + 1):
            for x in (stair, stair + 1):
                floor(x, y)
        for x in range(left, right + 1):
            floor(x, terrace['path_y'])
        for x, y in terrace['benches']:
            fixture('bench_grass', x, y)
        for x, y in terrace['trees']:
            fixture('street_tree', x, y)
        # Split at real crossing paths and the stairs. Recompute BOTH end caps
        # for every remaining run, so a path never cuts a cliff in mid-cell.
        columns = [x for x in range(left, right + 1) if x not in (stair, stair + 1)
                   and not ({(x, face_top), (x, bottom)} & (lanes | walks))]
        runs = []
        for x in columns:
            if not runs or x != runs[-1][-1] + 1:
                runs.append([])
            runs[-1].append(x)
        solid = set()
        for run in runs:
            if len(run) < 2:
                continue  # A one-cell broken cap cannot depict a complete face.
            for x in run:
                terrain(x, face_top, 0x68 if x == run[0] else 0x6a if x == run[-1] else 0x69, True)
                terrain(x, bottom, 0x78 if x == run[0] else 0x7a if x == run[-1] else 0x79, True)
                solid |= {(x, face_top), (x, bottom)}
        for x, y in stairs:
            terrain(x, y, 0xaf if x == stair else 0xcf, False)
        viewpoints.append(dict(name=terrace['name'], x=stair, y=terrace['path_y']))
        records.append(dict(name=terrace['name'], bounds=list(terrace['bounds']),
                            stairs=[list(p) for p in sorted(stairs)],
                            solid=[list(p) for p in sorted(solid)],
                            return_to_sidewalk=[stair, terrace['landing']]))
    if not patches.keys() <= reserved:
        raise ValueError('Potrero relief extends beyond its pre-packing reservation')
    # Independently flood the proposed collision result from the existing roads.
    # Every bench approach, upper court and lower stair landing must return.
    def walkable(x, y):
        char = patches.get((x, y), grid[y][x])
        return not (legend.get(char) or plan['legend'][char])[1]
    seen = {(x, y) for x, y in lanes if walkable(x, y)}
    pending = list(seen)
    while pending:
        x, y = pending.pop()
        for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and walkable(nx, ny):
                seen.add((nx, ny));pending.append((nx, ny))
    targets = {(v['x'], v['y']) for v in viewpoints}
    targets |= {(x, y + 1) for t in TERRACES for x, y in t['benches']}
    targets |= {tuple(r['return_to_sidewalk']) for r in records}
    if not targets <= seen:
        raise ValueError('Potrero relief would create a stranded court or stair landing')
    plan['legend'].update(legend)
    for (x, y), char in patches.items():
        grid[y][x] = char
    plan['town_blocks'].extend(blocks)
    occupied.update((b['x'] + dx, b['y'] + dy) for b in blocks
                    for dy in range(b['height']) for dx in range(b['width']))
    occupied.update(tuple(p) for r in records for p in r['solid'])
    plan.setdefault('scenic_viewpoints', []).extend(viewpoints)
    plan['town_relief'] = dict(terraces=records, native_metatiles=[0x68,0x69,0x6a,0x78,0x79,0x7a,0xaf,0xcf],
                               elevation=3, visual_acceptance='native review pending')
