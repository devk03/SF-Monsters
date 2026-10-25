"""Marina venue corridor, replacing complete existing facade stamps.

Two-phase integration in world_expansion AFTER ordinary packing/ground finishing
and BEFORE final architecture attachment and resident placement:
    draft = prepare(plan, grid, cards, lanes, walks, occupied, sea, shore)
    furnish(plan, grid, cards, token, occupied, draft)
Do NOT exclude reserved_cells from ordinary packing: skipping the eleven old
stamps would shift the shared frontage index and change unrelated blocks.
Prepare reserves a complete replacement transaction without mutation; furnish
revalidates it and commits only after all footprints/approaches pass.

Frozen v126 receipt c7037d17b1a041c29696d1d6e7cb6447 supplies the old footprints.
No new art/profile/ID/palette, resident, flag, service or warp is introduced.
Cafe/bar facades are scenery; the actual Corner Bar entry remains at5,8.
Version-specific native evidence and remaining visual gates are recorded in
docs/game-spec.md section15.1.
"""
from copy import deepcopy

# (x,y,width,height), exactly the complete v126 north-row stamps. Graphics and
# current edge variants are resolved from the live catalog, never copied here.
OLD_FRONTAGES = ((52,5,3,4), (55,5,2,4), (57,5,2,4), (59,5,3,4),
                 (62,5,3,4), (65,5,3,4), (68,5,3,4), (71,5,3,4),
                 (74,5,2,4), (76,5,3,4), (79,5,3,4))
FACADES = (('arcade_l',52,5,3,4), ('cafe',55,5,2,4),
           ('shophouse_m__sage',57,5,2,4), ('arcade_m',59,5,3,4),
           ('shophouse_m__sage',62,5,2,4), ('flats_r__sage',64,5,2,4),
           ('arcade_l__slate',70,5,3,4), ('cafe',73,5,2,4),
           ('shophouse_m__sage',75,5,2,4), ('shophouse_m__slate',77,5,2,4),
           ('deco_r__slate',79,5,3,4))
PROPS = (('bench',66,4,2,1), ('shop_board',66,6,1,1),
         ('bar_sign',66,7,1,2), ('bar_sign',82,7,1,2),
         ('street_tree',82,4,2,2), ('bench',85,4,2,1),
         ('rack',85,7,2,1), ('lamp',87,6,1,2))
VIEWPOINTS = (('Marina west venue frontage',60,10),
              ('Marina harbor passage',68,4),
              ('Marina east venue frontage',78,10),
              ('Marina harbor pocket',88,4))
# Final actor envelopes, before expanded residents have been positioned by the
# caller. Actual current actors/events are protected independently as well.
ACTORS = ((12,9,0), (42,15,1), (81,29,1), (51,48,0), (24,51,0),
          (74,51,0), (39,29,0), (80,15,0), (51,34,0))


def _rect(x, y, width, height):
    return {(x+dx,y+dy) for dy in range(height) for dx in range(width)}


def reserved_cells(identifier):
    """Transaction envelope, NOT a pre-packing exclusion (see module contract)."""
    if identifier != 'marina':
        return set()
    return set().union(*(_rect(*b) for b in OLD_FRONTAGES)) | _rect(52,4,30,1) | _rect(82,4,8,5)


def _through():
    return _rect(52,9,38,2) | _rect(68,4,2,7) | _rect(88,4,2,7)


def _bindings(plan, retired):
    keep = _rect(0,0,32,24)
    for key in ('access_points','coord_events','bg_events'):
        for event in plan.get(key, []):
            keep |= _rect(event['x']-1,event['y']-1,3,3)
    envelopes = [(x,y,rx,0) for x,y,rx in ACTORS]
    envelopes += [(n['x'],n['y'],n.get('range_x',0),n.get('range_y',0))
                  for n in plan.get('npcs', [])]
    for x,y,rx,ry in envelopes:
        keep |= _rect(x-rx-1,y-ry-1,2*rx+3,2*ry+3)
    for index, block in enumerate(plan['town_blocks']):
        if index in retired:
            continue
        x,y,w,h = (block[k] for k in ('x','y','width','height'))
        keep |= _rect(x,y,w,h)
    return keep


def prepare(plan, grid, cards, lanes, walks, occupied, sea, shore):
    """Read-only reservation of exactly eleven whole stamps; refuse drift."""
    if plan['world_id'] != 'marina':
        return None
    if plan['tile_profile'] != 'neighborhood' or len(grid) != 64 or any(len(row) != 96 for row in grid):
        raise ValueError('Marina venues require the expanded neighborhood map/profile')
    cells = reserved_cells('marina')
    expected = set(OLD_FRONTAGES)
    retired = {}
    for index, block in enumerate(plan['town_blocks']):
        bounds = tuple(block[k] for k in ('x','y','width','height'))
        footprint = _rect(*bounds)
        if not footprint & cells:
            continue
        if not footprint <= cells:
            raise ValueError('Marina replacement would crop an existing stamp')
        card = cards.get(block['style'], {})
        if bounds not in expected or not card.get('architecture_type'):
            raise ValueError('Marina replacement overlaps an unexpected building/prop')
        if bounds in [tuple(b[k] for k in ('x','y','width','height')) for b in retired.values()]:
            raise ValueError('Marina replacement has duplicate facade ownership')
        retired[index] = deepcopy(block)
    actual = {tuple(b[k] for k in ('x','y','width','height')) for b in retired.values()}
    if actual != expected:
        raise ValueError('Marina frozen whole-facade footprints changed or are missing')
    old_solid = set().union(*(_rect(*b) for b in actual))
    keep = _bindings(plan, retired)
    if cells & (keep | set(lanes) | set(sea) | set(shore)):
        raise ValueError('Marina replacement overlaps a binding, road or harbor wall')
    if (set(occupied) & cells) != old_solid:
        raise ValueError('Marina replacement contains unowned/missing occupancy')
    for x,y in cells-old_solid:
        if plan['legend'][grid[y][x]][1]:
            raise ValueError('Marina harbor pocket contains unowned solid terrain')
    for x,y in old_solid:
        if not plan['legend'][grid[y][x]][1]:
            raise ValueError('Marina original facade collision changed')
    return dict(cells=cells, retired=retired, old_solid=old_solid,
                lanes=set(lanes), walks=set(walks), sea=set(sea), shore=set(shore),
                old_grid={(x,y):grid[y][x] for x,y in cells})


def furnish(plan, grid, cards, token, occupied, draft):
    """Atomically replace full facades and furnish two reachable harbor pockets."""
    if plan['world_id'] != 'marina':
        return
    if draft is None:
        raise ValueError('Prepare the complete Marina replacement transaction first')
    fresh = prepare(plan, grid, cards, draft['lanes'], draft['walks'], occupied,
                    draft['sea'], draft['shore'])
    if fresh != draft:
        raise ValueError('Marina replacement transaction changed after preparation')
    cells = fresh['cells']
    patches = {(x,y):token('grass',x,y) for x,y in cells}
    # Two narrow approaches, not a whole new slab-paved block or fake pier.
    for x,y in _rect(68,4,2,5) | _rect(88,4,2,5):
        patches[x,y] = token('brick_walk',x,y)
    if any(plan['legend'].get(char, [None,True,None])[1:] != [False,3] for char in patches.values()):
        raise ValueError('Marina ground must remain ordinary walkable land')
    solid, blocks = set(), []
    for style,x,y,width,height in FACADES+PROPS:
        card = cards.get(style)
        if card is None or len(card['tiles']) != height or any(len(row) != width for row in card['tiles']):
            raise ValueError('Marina card dimensions changed: '+style)
        if not card.get('blocked'):
            raise ValueError('Marina facade/prop collision changed: '+style)
        footprint = _rect(x,y,width,height)
        if not footprint <= cells or footprint & (solid | fresh['lanes'] | fresh['walks'] | _through()):
            raise ValueError('Marina venue or prop obstructs a retained approach: '+style)
        for dy,row in enumerate(card['tiles']):
            for dx,n in enumerate(row):
                char = chr(0x100+n-512)
                if char not in plan['legend'] or plan['legend'][char] != [n,True,3]:
                    raise ValueError('Marina references undeclared/incompatible art: '+style)
                patches[x+dx,y+dy] = char
        solid |= footprint
        blocks.append(dict(style=style,x=x,y=y,width=width,height=height,
                           first_metatile=card['tiles'][0][0]))
    for char in patches.values():
        if char not in plan['legend']:
            raise ValueError('Marina references undeclared ground art')
    actor_cells = {(x+dx,y) for x,y,rx in ACTORS for dx in range(-rx,rx+1)}
    actor_cells |= {(n['x']+dx,n['y']+dy) for n in plan.get('npcs', [])
                    for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
                    for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    def walkable(point):
        x,y = point
        if point in fresh['sea'] | fresh['shore'] | actor_cells:
            return False
        return not plan['legend'][patches.get(point,grid[y][x])][1]
    # Start on the actual existing street, not every disconnected lane at once.
    start = (60,12)
    seen, pending = {start}, [start]
    while pending:
        x,y = pending.pop()
        for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            xx,yy = point
            if 0 <= xx < 96 and 0 <= yy < 64 and point not in seen and walkable(point):
                seen.add(point);pending.append(point)
    targets = _through() | {(66,5),(67,5),(67,6),(85,5),(86,5),(85,8),(86,8)}
    targets |= {(x,y) for _,x,y in VIEWPOINTS}
    if not targets <= seen:
        raise ValueError('Marina venue thresholds, benches or harbor approaches have no safe return')
    # No writes above this line. Original scripts, actors, event/access arrays,
    # service/gym/discovery state and all outside occupied cells are retained.
    for (x,y),char in patches.items():
        grid[y][x] = char
    occupied.difference_update(fresh['old_solid'])
    occupied.update(solid)
    plan['town_blocks'] = [b for i,b in enumerate(plan['town_blocks']) if i not in fresh['retired']] + blocks
    plan.setdefault('scenic_viewpoints', []).extend(
        dict(name=name,x=x,y=y) for name,x,y in VIEWPOINTS)
    plan['marina_venues'] = dict(bounds=[52,4,89,8],whole_facades_replaced=11,
        facade_count=11,front_sidewalk=[52,9,89,10],harbor_passage=[68,4,69,10],
        east_harbor_approach=[88,4,89,10],corner_bar_entry=[5,8],
        viewpoint_cells=[[x,y] for _,x,y in VIEWPOINTS],new_art=0,new_flags=0,new_warps=0,
        limitations=['No boats, docks, palms, patio tables or clubhouse asset',
                     'New cafe/bar facades are scenery; existing Corner Bar provides services',
                     'Native gameplay and human visual acceptance pending'])
