"""Post-packing Outer Sunset court relocation and two joined house fronts.

Call before the shared party-wall pass, with the original court reservation.
This is a source candidate; native, old-save and visual validation are required.
"""
from collections import deque

SCRIPT = 'WBCourt_outer_sunset_1'
OLD_OBJECT = (57, 39)
OLD_REST = (56, 39)
OBJECT = (57, 48)
REST = (57, 49)
PASSAGE = {(x, y) for x in range(55, 58) for y in range(38, 47)}
NEW = (('walkup', 55, 37), ('workshop__slate', 55, 44))


def _one(items, predicate, label):
    matches = [item for item in items if predicate(item)]
    if len(matches) != 1:
        raise ValueError('Outer Sunset court baseline changed: ' + label)
    return matches[0]


def _footprint(block):
    return {(block['x'] + dx, block['y'] + dy)
            for dy in range(block['height']) for dx in range(block['width'])}


def _check_stamp(plan, grid, cards, block):
    card = cards.get(block['style'])
    if (not card or len(card['tiles']) != block['height']
            or any(len(row) != block['width'] for row in card['tiles'])
            or block['first_metatile'] != card['tiles'][0][0]):
        raise ValueError('Outer Sunset baseline stamp identity changed')
    for dy, row in enumerate(card['tiles']):
        for dx, tile in enumerate(row):
            char = chr(0x100 + tile - 512)
            if (grid[block['y'] + dy][block['x'] + dx] != char
                    or plan['legend'].get(char) != [tile, True, 3]):
                raise ValueError('Outer Sunset baseline stamp pixels or collision changed')


def _reachable(plan, grid, patches, actors):
    start = (16, 10)
    def walkable(point):
        x, y = point
        return point not in actors and not plan['legend'][patches.get(point, grid[y][x])][1]
    if not walkable(start):
        raise ValueError('Outer Sunset arrival is blocked')
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for point in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
            if (0 <= point[0] < 96 and 0 <= point[1] < 64
                    and point not in seen and walkable(point)):
                seen.add(point)
                queue.append(point)
    return seen


def furnish(plan, grid, cards, lanes, walks, occupied, sea, shore, passage_cells):
    """Atomically relocate court bindings and join two fronts after packing.

    All arguments are the live expansion-stage structures. The caller must pass
    the complete original passage reservation and run the normal attachment pass.
    """
    if plan['world_id'] != 'outer_sunset':
        return
    if (plan['tile_profile'] != 'neighborhood' or len(grid) != 64
            or any(len(row) != 96 for row in grid)):
        raise ValueError('Outer Sunset join requires its expanded neighborhood map')
    fixture = _one(plan['town_blocks'], lambda b: b['style'] == 'flower_box'
                   and (b['x'], b['y']) == OLD_OBJECT, 'flower box')
    bench = _one(plan['town_blocks'], lambda b: b['style'] == 'bench'
                 and (b['x'], b['y'], b['width'], b['height']) == (55, 48, 2, 1), 'bench')
    event = _one(plan['bg_events'], lambda e: e.get('script') == SCRIPT, 'event')
    checkpoint = _one(plan['access_points'], lambda e: e.get('name') == 'pedestrian_court_1', 'checkpoint')
    viewpoint = _one(plan['scenic_viewpoints'], lambda e: e.get('name') == 'Planted pedestrian court 2', 'viewpoint')
    notice = _one(plan['court_notices'], lambda e: e.get('script') == SCRIPT, 'notice')
    extra = _one(plan['extra_street_signs'], lambda e: e.get('script') == SCRIPT, 'extra sign')
    court = _one(plan['pedestrian_courts'], lambda e: e.get('zone') == 1, 'court')
    if (fixture['width'], fixture['height']) != (1, 1) or (event.get('x'), event.get('y')) != OLD_OBJECT or event.get('type') != 'sign' or event.get('player_facing_dir') != 'BG_EVENT_PLAYER_FACING_ANY' or event.get('elevation') != 0:
        raise ValueError('Outer Sunset court event semantics changed')
    if (checkpoint.get('x'), checkpoint.get('y')) != OLD_REST or checkpoint.get('activation') != 'interact' or (viewpoint.get('x'), viewpoint.get('y')) != OLD_REST:
        raise ValueError('Outer Sunset court checkpoint changed')
    if (notice.get('object'), notice.get('standing')) != (list(OLD_OBJECT), list(OLD_REST)) or notice != extra or not notice.get('text'):
        raise ValueError('Outer Sunset court notice changed')
    if court != dict(x=55, top=41, rest=list(OLD_REST), zone=1) or not PASSAGE <= passage_cells:
        raise ValueError('Outer Sunset court reservation changed')
    _check_stamp(plan, grid, cards, fixture)
    _check_stamp(plan, grid, cards, bench)
    neighbors = []
    for x, y, family in ((52,37,'duplex'), (58,37,'gable'), (52,44,'duplex'), (58,44,'gable')):
        block = _one(plan['town_blocks'], lambda b: (b['x'], b['y'], b['width'], b['height']) == (x,y,3,4), 'neighbor')
        if cards[block['style']].get('architecture_type') != family:
            raise ValueError('Outer Sunset neighboring house changed')
        _check_stamp(plan, grid, cards, block)
        neighbors.append(block)
    actors = {(n['x'] + dx, n['y'] + dy) for n in plan['npcs']
              for dx in range(-n.get('range_x', 0), n.get('range_x', 0)+1)
              for dy in range(-n.get('range_y', 0), n.get('range_y', 0)+1)}
    bindings = {(e['x'], e['y']) for key in ('access_points','coord_events','bg_events','scenic_viewpoints')
                for e in plan.get(key, []) if e is not event and e is not checkpoint and e is not viewpoint}
    new_cells = {(x,y) for _,left,top in NEW for x in range(left,left+3) for y in range(top,top+4)} | {OBJECT}
    if (new_cells & (set(lanes) | set(walks) | set(sea) | set(shore) | actors | bindings)
            or (new_cells & set(occupied)) != {OLD_OBJECT} or REST in actors | bindings | new_cells):
        raise ValueError('Outer Sunset join conflicts with a protected cell')
    if any(plan['legend'][grid[y][x]][1] for x,y in new_cells - {OLD_OBJECT}):
        raise ValueError('Outer Sunset join would cover unowned solid ground')
    background = {
        37: (550,550,550), 38: (586,585,586), 39: (588,587,None),
        40: (586,585,586), 44: (586,585,586), 45: (588,587,588),
        46: (586,585,586), 47: (550,550,550),
    }
    for y, row in background.items():
        for x, tile in zip(range(55,58), row):
            if tile is not None and plan['legend'].get(grid[y][x]) != [tile,False,3]:
                raise ValueError('Outer Sunset original court ground changed')
    if plan['legend'].get(grid[48][57]) != [550,False,3]:
        raise ValueError('Outer Sunset nook ground changed')
    for block in plan['town_blocks']:
        if block is not fixture and _footprint(block) & new_cells:
            raise ValueError('Outer Sunset join intersects another stamp')
    patches, additions = {}, []
    for style, x, y in NEW + (('flower_box', *OBJECT),):
        card = cards.get(style)
        width, height = (1, 1) if style == 'flower_box' else (3, 4)
        if (not card or not card.get('blocked') or len(card['tiles']) != height
                or any(len(row) != width for row in card['tiles'])
                or (style != 'flower_box' and not card.get('architecture_type'))):
            raise ValueError('Outer Sunset replacement card changed: ' + style)
        for dy, row in enumerate(card['tiles']):
            for dx, tile in enumerate(row):
                char = chr(0x100 + tile - 512)
                if plan['legend'].get(char) != [tile, True, 3]:
                    raise ValueError('Outer Sunset replacement collision changed')
                patches[x+dx,y+dy] = char
        additions.append(dict(style=style,x=x,y=y,width=width,height=height,first_metatile=card['tiles'][0][0]))
    before = _reachable(plan, grid, {}, actors)
    after = _reachable(plan, grid, patches, actors)
    if not (before - new_cells) <= after:
        raise ValueError('Outer Sunset join strands previously reachable ground')
    # A three-cell open approach reaches the sign from the south; the rectangle
    # includes the unchanged curb/road and does not authorize painting it.
    if not {(57,49), (57,50), (57,51), (58,49), (55,41), (57,42)} <= after:
        raise ValueError('Outer Sunset court or inner walk is inaccessible')
    for point, char in patches.items():
        grid[point[1]][point[0]] = char
    occupied.remove(OLD_OBJECT)
    occupied.update(new_cells)
    passage_cells.difference_update(PASSAGE)
    plan['town_blocks'].remove(fixture)
    plan['town_blocks'].extend(additions)
    event['x'],event['y'] = OBJECT
    checkpoint['x'],checkpoint['y'] = REST
    viewpoint['x'],viewpoint['y'] = REST
    for item in (notice, extra):
        item['object'],item['standing'] = list(OBJECT),list(REST)
    court.clear()
    court.update(zone=1, kind='nook', bounds=[56,49,58,51], rest=list(REST))
    plan['outer_sunset_join'] = dict(old_object=list(OLD_OBJECT), object=list(OBJECT),
                                    standing=list(REST), walls=[[55,37],[55,44]])
