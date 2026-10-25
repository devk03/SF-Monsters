"""Twin Peaks landform candidate; existing terrain and bindings only.

Grass middle70/71/72 is supported by Route117/123 and MtPyre native stacks;
88/8A are sand-backed alternatives. Shared guards pin their native allocations.
Prepare AFTER native outcrop/protected-cell planning but BEFORE forest packing;
union draft['clear'] into the forest's clear set. Replace the generic Twin Peaks
terraces, not other parks' terraces. Furnish AFTER outcrop drawing and BEFORE
park-stop/flower finishing. All land stays elevation3; this is visual relief,
not a new elevation gate. This module does not build the concept's lower
residential base; the whole-map translation remains unfinished. Native
gameplay/visual approval remains pending.
"""

PEAKS = (
    dict(name='North summit', center=(45, 18), envelope=(35, 12, 55, 30),
         oval=(45, 21, 10, 9),
         rims=((40, 22, 50, 44, 3), (38, 27, 52, 50, 3)),
         route=((45, 18), (44, 18), (44, 25), (50, 25), (50, 30))),
    dict(name='South summit', center=(65, 35), envelope=(56, 28, 78, 48),
         oval=(67, 38, 11, 10),
         rims=((56, 41, 75, 61, 3), (59, 46, 75, 64, 3)),
         route=((65, 35), (61, 35), (61, 44), (64, 44), (64, 49))),
)
SADDLE = ((50, 30), (54, 30), (57, 31), (61, 32), (65, 35))
# Existing generated park-stop objects, standing cells and furniture; protect
# them before add_park_stops has created its metadata. Include final NPC anchors.
STABLE_CELLS = ((16, 7), (16, 10), (43, 16), (43, 17), (63, 34), (63, 35),
                (37, 45), (37, 46), (47, 18), (67, 36))
REST_FOOTPRINTS = ((46, 19, 47, 20), (65, 32, 66, 33), (39, 46, 40, 47))


def _rect(left, top, right, bottom):
    return {(x, y) for y in range(top, bottom+1) for x in range(left, right+1)}


def _path(points):
    """Two walkable columns along each horizontal/vertical/diagonal segment."""
    result = set()
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        steps = max(abs(x1-x0), abs(y1-y0))
        for step in range(steps+1):
            x = round(x0+(x1-x0)*step/max(1, steps))
            y = round(y0+(y1-y0)*step/max(1, steps))
            result |= {(x, y), (x+1, y)}
    return result


def reserved_cells(identifier):
    if identifier != 'twin_peaks':
        return set()
    clear = _path(SADDLE)
    for peak in PEAKS:
        cx, cy, rx, ry = peak['oval']
        left, top, right, bottom = peak['envelope']
        clear |= {(x, y) for y in range(top, bottom+1) for x in range(left, right+1)
                  if (x-cx)**2*ry**2+(y-cy)**2*rx**2 <= rx**2*ry**2}
        clear |= _path(peak['route'])
        for left, y, right, _, depth in peak['rims']:
            clear |= _rect(left, y, right, y+depth-1)
    return clear


def _bindings(plan):
    protected = _rect(0, 0, 31, 23)
    for x, y in STABLE_CELLS:
        protected |= _rect(x-1, y-1, x+1, y+1)
    for bounds in REST_FOOTPRINTS:
        left, top, right, bottom = bounds
        protected |= _rect(left-1, top-1, right+1, bottom+1)
    for key in ('access_points', 'coord_events', 'bg_events'):
        for event in plan.get(key, []):
            x, y = event['x'], event['y']
            protected |= _rect(x-1, y-1, x+1, y+1)
    for npc in plan.get('npcs', []):
        x, y = npc['x'], npc['y']
        rx, ry = npc.get('range_x', 0), npc.get('range_y', 0)
        protected |= _rect(x-rx-1, y-ry-1, x+rx+1, y+ry+1)
    return protected


def prepare(plan, lanes, protected):
    """Return pure forest reservations and a staged two-tier route per summit."""
    if plan['world_id'] != 'twin_peaks':
        return None
    keep = set(protected) | _bindings(plan)
    trail = _path(SADDLE)
    clear = reserved_cells('twin_peaks')
    faces, stairs, rims = {}, {}, []
    for peak in PEAKS:
        route = _path(peak['route'])
        trail |= route
        for left, top, right, stair, depth in peak['rims']:
            bottom = top+depth-1
            step_cells = _rect(stair, top, stair+1, bottom)
            if step_cells & keep:
                raise ValueError(peak['name']+': stairs overlap protected cells '+str(sorted(step_cells & keep)))
            # Native route lanes stay intact and provide additional open breaks.
            # Stair words may replace only the new switchback, never old lanes.
            if step_cells & lanes:
                raise ValueError('Twin summit stairs overlap an existing route lane')
            columns = [x for x in range(left, right+1)
                       if not ({(x, y) for y in range(top, bottom+1)} & (keep | lanes | route | _path(SADDLE)))]
            runs = []
            for x in columns:
                if not runs or x != runs[-1][-1]+1:
                    runs.append([])
                runs[-1].append(x)
            for run in runs:
                if len(run) < 3:
                    continue
                for x in run:
                    faces[x, top] = 0x68 if x == run[0] else 0x6a if x == run[-1] else 0x69
                    for y in range(top+1,bottom):
                        faces[x, y] = 0x70 if x == run[0] else 0x72 if x == run[-1] else 0x71
                    faces[x, bottom] = 0x78 if x == run[0] else 0x7a if x == run[-1] else 0x79
            for x, y in step_cells:
                stairs[x, y] = 0xaf if x == stair else 0xcf
            rims.append(dict(name=peak['name'], bounds=[left, top, right, bottom],
                             stair=[stair, top], upper=[stair, top-1], lower=[stair, bottom+1]))
    if faces.keys() & stairs.keys() or not (faces.keys() | stairs.keys() | trail) <= clear:
        raise ValueError('Twin summit terrain exceeds its forest reservation')
    return dict(clear=clear, faces=faces, stairs=stairs, trail=trail,
                protected=keep, lanes=set(lanes), rims=rims)


def furnish(plan, grid, draft, token):
    """Apply the prepared landform atomically, without moving objects/events.

    Refuse packed canopies/old cliffs rather than cutting a tree or covering an
    unreviewed scene. Native normal-land words are the only changed resources.
    """
    if plan['world_id'] != 'twin_peaks':
        return
    if draft is None:
        raise ValueError('Prepare Twin Peaks before forest packing')
    keep = draft['protected'] | _bindings(plan)
    patches, legend = {}, {}
    for point in draft['trail'] - (keep | draft['lanes']):
        patches[point] = (0x124, False)
    patches.update({point:(tile, True) for point, tile in draft['faces'].items()})
    patches.update({point:(tile, False) for point, tile in draft['stairs'].items()})
    width, height = len(grid[0]), len(grid)
    for (x, y), (tile, blocked) in patches.items():
        if not 0 < x < width-1 or not 0 < y < height-1:
            raise ValueError('Twin summit terrain leaves the map')
        if (x, y) in keep | draft['lanes']:
            raise ValueError('Twin summit terrain changes a binding or existing route')
        if plan['legend'][grid[y][x]][1]:
            raise ValueError('Reserve Twin Peaks before forest/old-terrace drawing')
        char = chr(0x800+tile)
        entry = [tile, blocked, 3]
        if char in plan['legend'] and plan['legend'][char] != entry:
            raise ValueError('Conflicting native Twin Peaks terrain legend')
        legend[char] = entry
    # Every summit, stair head/foot and existing stop must have a walking return.
    def walkable(x, y):
        if (x, y) in patches:
            return not patches[x, y][1]
        return not plan['legend'][grid[y][x]][1]
    seen = {(x, y) for x, y in draft['lanes'] if walkable(x, y)}
    pending = list(seen)
    while pending:
        x, y = pending.pop()
        for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and walkable(nx, ny):
                seen.add((nx, ny));pending.append((nx, ny))
    targets = {peak['center'] for peak in PEAKS} | {(43,17), (63,35), (37,46), (16,7), (16,10)}
    targets |= {(r[key][0]+dx,r[key][1]) for r in draft['rims']
                for key in ('upper', 'lower') for dx in (0,1)}
    if not targets <= seen:
        raise ValueError('Twin summit proposal strands a lookout, stair or existing binding')
    plan['legend'].update(legend)
    for (x, y), (tile, _) in patches.items():
        grid[y][x] = chr(0x800+tile)
    plan['twin_summits'] = dict(
        peaks=[dict(name=p['name'], center=list(p['center']), envelope=list(p['envelope'])) for p in PEAKS],
        saddle=[list(p) for p in SADDLE], rims=draft['rims'], exposed_cells=len(draft['clear']),
        integration_requires=dict(native_classifications=[0x70,0x71,0x72],
                                  primary_reservation_ids=[0x72], primary_graphics_slots=[100,101,116,117]),
        elevation=3, new_art_allocations=0, new_flags=0, new_warps=0,
        limitations=['Ordinary elevation3; no new height/progression mechanics',
                     'Lower residential/urban-edge concept area remains absent'],
        visual_acceptance='native review pending')
    plan.setdefault('scenic_viewpoints', []).extend([
        dict(name='Exposed north summit', x=45, y=18),
        dict(name='Summit saddle', x=54, y=30),
        dict(name='Exposed south summit', x=65, y=35),
    ])
