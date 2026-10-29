"""Join the southern Mission studio frontage without disturbing its court."""
from collections import deque

NEW = (('shophouse', 48, 44), ('flats__sage', 50, 44))
NEIGHBORS = ((45, 44, 3, 4, 'duplex'), (52, 44, 2, 4, 'shophouse'))


def furnish(plan, grid, cards, token, lanes, walks, occupied, sea, shore):
    if plan['world_id'] != 'mission':
        return
    if plan['tile_profile'] != 'mixed_use' or len(grid) != 64 or any(len(row) != 96 for row in grid):
        raise ValueError('Mission wall requires expanded mixed-use map')
    cells = {(x, y) for x in range(48, 52) for y in range(44, 48)}
    actors = {(n['x'] + dx, n['y'] + dy) for n in plan['npcs']
              for dx in range(-n.get('range_x', 0), n.get('range_x', 0) + 1)
              for dy in range(-n.get('range_y', 0), n.get('range_y', 0) + 1)}
    bindings = {(e['x'], e['y']) for key in ('access_points', 'coord_events', 'bg_events', 'scenic_viewpoints')
                for e in plan.get(key, []) if 'x' in e and 'y' in e}
    if cells & (set(lanes) | set(walks) | set(occupied) | set(sea) | set(shore) | actors | bindings):
        raise ValueError('Mission wall intersects a protected cell')
    if any(plan['legend'][grid[y][x]][1] for x, y in cells):
        raise ValueError('Mission wall covers unowned solid ground')
    courts = [c for c in plan['pedestrian_courts'] if c.get('zone') == 1]
    if courts != [dict(x=49, top=42, rest=[50, 40], zone=1)]:
        raise ValueError('Mission court baseline changed')
    for x, y, width, height, family in NEIGHBORS:
        matches = [b for b in plan['town_blocks'] if (b['x'], b['y'], b['width'], b['height']) == (x, y, width, height)]
        if len(matches) != 1 or cards[matches[0]['style']].get('architecture_type') != family:
            raise ValueError('Mission wall neighboring frontage changed')
        card = cards[matches[0]['style']]
        for dy, row in enumerate(card['tiles']):
            for dx, tile in enumerate(row):
                if grid[y + dy][x + dx] != chr(0x100 + tile - 512):
                    raise ValueError('Mission wall neighboring pixels changed')
    patches, additions = {}, []
    for x in range(48,52):
        if grid[48][x] != token('grass',x,48):
            raise ValueError('Mission wall sidewalk baseline changed')
        char = token('brick_walk',x,48)
        if plan['legend'].get(char, [None, True, None])[1:] != [False,3]:
            raise ValueError('Mission wall sidewalk is not walkable')
        patches[x,48] = char
    for style, x, y in NEW:
        card = cards.get(style)
        if not card or not card.get('architecture_type') or not card.get('blocked') or len(card['tiles']) != 4 or any(len(row) != 2 for row in card['tiles']):
            raise ValueError('Mission wall card changed: ' + style)
        for dy, row in enumerate(card['tiles']):
            for dx, tile in enumerate(row):
                char = chr(0x100 + tile - 512)
                if plan['legend'].get(char) != [tile, True, 3]:
                    raise ValueError('Mission wall collision changed')
                patches[x + dx, y + dy] = char
        additions.append(dict(style=style, x=x, y=y, width=2, height=4, first_metatile=card['tiles'][0][0]))
    def reachable(patches):
        start = (16, 10)
        def open_(p):
            x, y = p
            return p not in actors and not plan['legend'][patches.get(p, grid[y][x])][1]
        if not open_(start):
            raise ValueError('Mission wall arrival blocked')
        seen, pending = {start}, deque([start])
        while pending:
            x, y = pending.popleft()
            for p in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
                if 0 <= p[0] < 96 and 0 <= p[1] < 64 and p not in seen and open_(p):
                    seen.add(p); pending.append(p)
        return seen
    before, after = reachable({}), reachable(patches)
    if not (before - cells) <= after or (50,40) not in after:
        raise ValueError('Mission wall would strand ground or court access')
    for (x, y), char in patches.items():
        grid[y][x] = char
    occupied.update(cells)
    plan['town_blocks'].extend(additions)
    courts[0].update(kind='nook', bounds=[49,39,51,41])
    plan['mission_south_wall'] = dict(bounds=[48,44,51,47], court=[50,40])
