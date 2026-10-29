"""Recompose the central North Beach street walls around a reading nook.

The two existing short rows become connected fronts, including the offset shop.
This does not add deeper roof art or claim completion of the neighborhood.
"""
from collections import deque

SCRIPT = 'WBCourt_north_beach_1'
OLD = (32, 40)
OLD_STAND = (31, 40)
OBJECT = (44, 41)
STAND = (45, 41)
NEW = (('flats__sage', 29, 37, 2, 4), ('shophouse__slate', 31, 37, 2, 4),
       ('shophouse__sage', 28, 44, 2, 4), ('walkup__slate', 30, 44, 3, 4))


def one(items, predicate, label):
    matches = [item for item in items if predicate(item)]
    if len(matches) != 1:
        raise ValueError('North Beach central block baseline changed: ' + label)
    return matches[0]


def footprint(block):
    return {(block['x'] + dx, block['y'] + dy)
            for dx in range(block['width']) for dy in range(block['height'])}


def furnish(plan, grid, cards, token, lanes, walks, occupied, sea, shore, passage_cells):
    if plan['world_id'] != 'north_beach':
        return
    if plan['tile_profile'] != 'culture' or len(grid) != 64 or any(len(row) != 96 for row in grid):
        raise ValueError('North Beach central block requires expanded culture map')
    fixture = one(plan['town_blocks'], lambda b: b['style'] == 'flower_box' and (b['x'], b['y']) == OLD, 'fixture')
    offset = one(plan['town_blocks'], lambda b: (b['x'], b['y'], b['width'], b['height']) == (42,45,3,4), 'offset shop')
    event = one(plan['bg_events'], lambda e: e.get('script') == SCRIPT, 'event')
    checkpoint = one(plan['access_points'], lambda e: e.get('name') == 'pedestrian_court_1', 'checkpoint')
    viewpoint = one(plan['scenic_viewpoints'], lambda e: e.get('name') == 'Planted pedestrian court 2', 'viewpoint')
    notice = one(plan['court_notices'], lambda e: e.get('script') == SCRIPT, 'notice')
    extra = one(plan['extra_street_signs'], lambda e: e.get('script') == SCRIPT, 'extra sign')
    court = one(plan['pedestrian_courts'], lambda e: e.get('zone') == 1, 'court')
    if ((fixture['width'], fixture['height']) != (1,1) or (event['x'], event['y']) != OLD
            or event.get('type') != 'sign' or event.get('player_facing_dir') != 'BG_EVENT_PLAYER_FACING_ANY'
            or (checkpoint['x'], checkpoint['y']) != OLD_STAND or checkpoint.get('activation') != 'interact'
            or (viewpoint['x'], viewpoint['y']) != OLD_STAND or notice != extra
            or notice['object'] != list(OLD) or notice['standing'] != list(OLD_STAND)
            or court != dict(x=30,top=42,rest=list(OLD_STAND),zone=1)):
        raise ValueError('North Beach central block court bindings changed')
    neighbors = ((26,37,3,4,'arcade'),(33,37,2,4,'shophouse'),
                 (26,44,2,4,'flats'),(33,44,3,4,'gable'),(39,44,3,4,'workshop'))
    for x,y,w,h,family in neighbors + ((42,45,3,4,'arcade'),):
        block = one(plan['town_blocks'], lambda b: (b['x'],b['y'],b['width'],b['height']) == (x,y,w,h), 'neighbor')
        card = cards[block['style']]
        if (card.get('architecture_type') != family or block['first_metatile'] != card['tiles'][0][0]
                or len(card['tiles']) != h or any(len(row) != w for row in card['tiles'])):
            raise ValueError('North Beach central block neighbor identity changed')
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                char = chr(0x100+tile-512)
                if grid[y+dy][x+dx] != char or plan['legend'].get(char) != [tile,True,3]:
                    raise ValueError('North Beach central block neighbor pixels changed')
    tile = cards['flower_box']['tiles'][0][0]
    if fixture['first_metatile'] != tile or grid[OLD[1]][OLD[0]] != chr(0x100+tile-512):
        raise ValueError('North Beach central block fixture changed')
    actors = {(n['x']+dx,n['y']+dy) for n in plan['npcs']
              for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
              for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    bindings = {(e['x'],e['y']) for key in ('access_points','coord_events','bg_events','warp_events','scenic_viewpoints')
                for e in plan.get(key,[]) if e is not event and e is not checkpoint and e is not viewpoint and 'x' in e and 'y' in e}
    added = {(x+dx,y+dy) for _,x,y,w,h in NEW for dx in range(w) for dy in range(h)}
    old_shop = footprint(offset)
    new_shop = {(x,y) for x in range(42,45) for y in range(44,48)}
    new = added | new_shop | {OBJECT}
    protected = set(lanes) | set(walks) | set(sea) | set(shore) | actors | bindings
    if new & protected or new & occupied != ({OLD} | (new_shop & old_shop)):
        raise ValueError('North Beach central block conflicts with protected or occupied cells')
    if STAND in set(lanes) | set(sea) | set(shore) | actors | bindings | occupied | new:
        raise ValueError('North Beach central block notice approach blocked')
    if any(plan['legend'][grid[y][x]][1] for x,y in new - {OLD} - old_shop):
        raise ValueError('North Beach central block covers unowned solid ground')
    for b in plan['town_blocks']:
        if b is not fixture and b is not offset and footprint(b) & new:
            raise ValueError('North Beach central block intersects another stamp')
    patches, additions = {}, []
    for x,y in old_shop - new_shop:
        char = token('brick_walk',x,y)
        if plan['legend'].get(char,[None,True,None])[1:] != [False,3]:
            raise ValueError('North Beach central block sidewalk blocked')
        patches[x,y] = char
    items = NEW + ((offset['style'],42,44,3,4),('flower_box',*OBJECT,1,1))
    for style,x,y,w,h in items:
        card = cards.get(style)
        if not card or not card.get('blocked') or len(card['tiles']) != h or any(len(row) != w for row in card['tiles']):
            raise ValueError('North Beach central block replacement card changed: '+style)
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                char = chr(0x100+tile-512)
                if plan['legend'].get(char) != [tile,True,3]:
                    raise ValueError('North Beach central block collision changed')
                patches[x+dx,y+dy] = char
        additions.append(dict(style=style,x=x,y=y,width=w,height=h,first_metatile=card['tiles'][0][0]))
    def reachable(changes):
        start=(16,10)
        def opened(point):
            x,y=point
            return point not in actors and not plan['legend'][changes.get(point,grid[y][x])][1]
        if not opened(start):
            raise ValueError('North Beach central block arrival blocked')
        seen, queue = {start}, deque([start])
        while queue:
            x,y=queue.popleft()
            for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0<=point[0]<96 and 0<=point[1]<64 and point not in seen and opened(point):
                    seen.add(point);queue.append(point)
        return seen
    before,after=reachable({}),reachable(patches)
    if not (before-new) <= after or STAND not in after:
        raise ValueError('North Beach central block strands ground or notice')
    for (x,y),char in patches.items():
        grid[y][x]=char
    occupied.difference_update(old_shop | {OLD});occupied.update(new)
    passage_cells.difference_update({(x,y) for x in range(30,33) for y in range(39,48)})
    plan['town_blocks'].remove(fixture);plan['town_blocks'].remove(offset);plan['town_blocks'].extend(additions)
    event['x'],event['y']=OBJECT;checkpoint['x'],checkpoint['y']=STAND;viewpoint['x'],viewpoint['y']=STAND
    for item in (notice,extra):
        item['object'],item['standing']=list(OBJECT),list(STAND)
        item['text']='Bring your own book. Leave the good light for the plants.'
    court.clear();court.update(zone=1,kind='nook',bounds=[44,41,46,43],rest=list(STAND))
    plan['north_beach_central_block']=dict(walls=[[29,37],[28,44]],object=list(OBJECT),standing=list(STAND))
