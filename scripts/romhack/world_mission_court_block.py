"""Complete Mission's central street wall and move its shared court notice.

This runs before party-wall art is resolved. It validates all moved bindings,
new building footprints and pedestrian reachability before touching the plan.
"""
from collections import deque

OLD = (51, 40)
OLD_STAND = (50, 40)
OBJECT = (58, 40)
STAND = (58, 41)
NEW = (('flats__slate', 48, 37), ('shophouse__sage', 50, 37))
SCRIPT = 'WBCourt_mission_1'


def one(items, predicate, label):
    matches = [item for item in items if predicate(item)]
    if len(matches) != 1:
        raise ValueError('Mission court baseline changed: ' + label)
    return matches[0]


def footprint(block):
    return {(block['x'] + dx, block['y'] + dy)
            for dy in range(block['height']) for dx in range(block['width'])}


def furnish(plan, grid, cards, token, lanes, walks, occupied, sea, shore):
    if plan['world_id'] != 'mission':
        return
    if plan['tile_profile'] != 'mixed_use' or len(grid) != 64 or any(len(row) != 96 for row in grid):
        raise ValueError('Mission court requires expanded mixed-use map')
    fixture = one(plan['town_blocks'], lambda b: b['style'] == 'flower_box' and (b['x'], b['y']) == OLD, 'fixture')
    event = one(plan['bg_events'], lambda e: e.get('script') == SCRIPT, 'event')
    checkpoint = one(plan['access_points'], lambda a: a.get('name') == 'pedestrian_court_1', 'checkpoint')
    viewpoint = one(plan['scenic_viewpoints'], lambda v: v.get('name') == 'Planted pedestrian court 2', 'viewpoint')
    notice = one(plan['court_notices'], lambda n: n.get('script') == SCRIPT, 'notice')
    extra = one(plan['extra_street_signs'], lambda n: n.get('script') == SCRIPT, 'extra sign')
    court = one(plan['pedestrian_courts'], lambda c: c.get('zone') == 1, 'court')
    if ((fixture['width'], fixture['height']) != (1, 1) or (event['x'], event['y']) != OLD
            or event.get('type') != 'sign' or event.get('elevation') != 0
            or event.get('player_facing_dir') != 'BG_EVENT_PLAYER_FACING_ANY'):
        raise ValueError('Mission court fixture/event changed')
    if ((checkpoint['x'], checkpoint['y']) != OLD_STAND or checkpoint.get('activation') != 'interact'
            or (viewpoint['x'], viewpoint['y']) != OLD_STAND):
        raise ValueError('Mission court standing point changed')
    if notice != extra or (notice['object'], notice['standing']) != (list(OLD), list(OLD_STAND)):
        raise ValueError('Mission court notice changed')
    if court != dict(x=49,top=42,rest=list(OLD_STAND),zone=1,kind='nook',bounds=[49,39,51,41]):
        raise ValueError('Mission court metadata changed')
    oldtile = cards['flower_box']['tiles'][0][0]
    if fixture['first_metatile'] != oldtile or grid[OLD[1]][OLD[0]] != chr(0x100+oldtile-512):
        raise ValueError('Mission court fixture pixels changed')
    neighbors = ((45,37,3,4,'duplex'), (52,37,2,4,'shophouse'))
    for x,y,width,height,family in neighbors:
        block = one(plan['town_blocks'], lambda b: (b['x'],b['y'],b['width'],b['height']) == (x,y,width,height), 'neighbor')
        card = cards[block['style']]
        if card.get('architecture_type') != family or block['first_metatile'] != card['tiles'][0][0]:
            raise ValueError('Mission court neighboring facade changed')
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                if grid[y+dy][x+dx] != chr(0x100+tile-512):
                    raise ValueError('Mission court neighboring pixels changed')
    actors = {(n['x']+dx,n['y']+dy) for n in plan['npcs']
              for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
              for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    bindings = {(e['x'],e['y']) for key in ('access_points','coord_events','bg_events','scenic_viewpoints')
                for e in plan.get(key,[]) if e is not event and e is not checkpoint and e is not viewpoint and 'x' in e and 'y' in e}
    building = {(x,y) for x in range(48,52) for y in range(37,41)}
    newcells = building | {OBJECT}
    prohibited = set(lanes) | set(walks) | set(sea) | set(shore) | actors | bindings
    if newcells & prohibited or newcells & occupied != {OLD} or STAND in actors | bindings | newcells:
        raise ValueError('Mission court conflicts: ' + str(sorted(newcells & prohibited)))
    if any(plan['legend'][grid[y][x]][1] for x,y in newcells - {OLD}):
        raise ValueError('Mission court covers unowned solid ground')
    for block in plan['town_blocks']:
        if block is not fixture and footprint(block) & newcells:
            raise ValueError('Mission court intersects another stamp')
    patches, additions = {}, []
    for style,x,y in NEW + (('flower_box',*OBJECT),):
        card = cards.get(style)
        width,height = (1,1) if style == 'flower_box' else (2,4)
        if not card or not card.get('blocked') or len(card['tiles']) != height or any(len(row) != width for row in card['tiles']):
            raise ValueError('Mission court replacement card changed: '+style)
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                char=chr(0x100+tile-512)
                if plan['legend'].get(char) != [tile,True,3]:
                    raise ValueError('Mission court replacement collision changed')
                patches[x+dx,y+dy] = char
        additions.append(dict(style=style,x=x,y=y,width=width,height=height,first_metatile=card['tiles'][0][0]))
    # Repair exposed strips of grass surrounding the small court and its front.
    # Do not touch road, fixtures, actor envelopes, bindings or existing solids.
    for y in range(41,44):
        for x in range(42,59):
            point=(x,y)
            if point in newcells | occupied | actors | bindings | set(lanes) | set(sea) | set(shore):
                continue
            if grid[y][x] == token('grass',x,y):
                char=token('brick_walk',x,y)
                if plan['legend'].get(char,[None,True,None])[1:] != [False,3]:
                    raise ValueError('Mission court paving collision changed')
                patches[point] = char
    def reachable(changes):
        start=(16,10)
        def open_(p):
            x,y=p
            return p not in actors and not plan['legend'][changes.get(p,grid[y][x])][1]
        if not open_(start): raise ValueError('Mission court arrival blocked')
        seen,queue={start},deque([start])
        while queue:
            x,y=queue.popleft()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0<=p[0]<96 and 0<=p[1]<64 and p not in seen and open_(p):
                    seen.add(p);queue.append(p)
        return seen
    before,after=reachable({}),reachable(patches)
    if not (before-newcells) <= after or not {(58,41),(58,42),(58,43)} <= after:
        raise ValueError('Mission court would strand ground or its sign')
    for (x,y),char in patches.items(): grid[y][x]=char
    occupied.remove(OLD);occupied.update(newcells)
    plan['town_blocks'].remove(fixture);plan['town_blocks'].extend(additions)
    event['x'],event['y']=OBJECT
    checkpoint['x'],checkpoint['y']=STAND
    viewpoint['x'],viewpoint['y']=STAND
    for item in (notice,extra): item['object'],item['standing']=list(OBJECT),list(STAND)
    court.clear();court.update(zone=1,kind='nook',bounds=[57,41,59,43],rest=list(STAND))
    plan['mission_court_block']=dict(old_object=list(OLD),object=list(OBJECT),standing=list(STAND),wall=[48,37,51,40])
