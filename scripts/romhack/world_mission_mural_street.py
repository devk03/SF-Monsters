"""Align the Mission mural street into one continuous commercial frontage.

The existing mural and sidewalk viewpoints stay fixed. Four detached shops are
moved as complete stamps, leaving their former southern row as brick sidewalk.
"""
from collections import deque

OLD = ((16,25,3,4,'workshop'), (19,25,3,4,'arcade'),
       (22,25,3,4,'walkup'), (25,25,2,4,'flats'))
NEW_X = (15,18,21,24)


def cells(x,y,w,h):
    return {(x+dx,y+dy) for dx in range(w) for dy in range(h)}


def furnish(plan, grid, cards, token, lanes, walks, occupied, sea, shore):
    if plan['world_id'] != 'mission':
        return
    if plan['tile_profile'] != 'mixed_use' or len(grid)!=64 or any(len(row)!=96 for row in grid):
        raise ValueError('Mission mural street requires expanded mixed-use map')
    blocks=[]
    for x,y,w,h,family in OLD:
        matches=[b for b in plan['town_blocks'] if (b['x'],b['y'],b['width'],b['height'])==(x,y,w,h)]
        if len(matches)!=1:
            raise ValueError('Mission mural street baseline stamp missing')
        b=matches[0];card=cards[b['style']]
        if card.get('architecture_type')!=family or b['first_metatile']!=card['tiles'][0][0]:
            raise ValueError('Mission mural street baseline architecture changed')
        if len(card['tiles'])!=h or any(len(row)!=w for row in card['tiles']):
            raise ValueError('Mission mural street baseline dimensions changed')
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                char=chr(0x100+tile-512)
                if grid[y+dy][x+dx]!=char or plan['legend'].get(char)!=[tile,True,3]:
                    raise ValueError('Mission mural street baseline pixels changed')
        blocks.append(b)
    mural=[b for b in plan['town_blocks'] if b['style']=='mission_sun_mural' and (b['x'],b['y'])==(9,26)]
    shop=[b for b in plan['town_blocks'] if (b['x'],b['y'],b['width'],b['height'])==(13,24,2,4)]
    viewpoint=[v for v in plan.get('scenic_viewpoints',[]) if v.get('name')=='Sun mural street']
    if len(mural)!=1 or len(shop)!=1 or len(viewpoint)!=1 or (viewpoint[0]['x'],viewpoint[0]['y'])!=(10,29):
        raise ValueError('Mission mural or neighboring shop changed')
    old=set().union(*(cells(*entry[:4]) for entry in OLD))
    new=set().union(*(cells(x,24,entry[2],entry[3]) for x,entry in zip(NEW_X,OLD)))
    actors={(n['x']+dx,n['y']+dy) for n in plan['npcs']
            for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
            for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    bindings={(e['x'],e['y']) for key in ('access_points','coord_events','bg_events','warp_events','scenic_viewpoints')
              for e in plan.get(key,[]) if 'x' in e and 'y' in e}
    protected=set(lanes)|set(sea)|set(shore)|actors|bindings
    if new & (protected|set(walks)) or (new & occupied)!=new & old:
        raise ValueError('Mission mural street conflicts with protected cells')
    for x,y in new-old:
        if plan['legend'][grid[y][x]][1]:
            raise ValueError('Mission mural street covers unowned solid ground')
    patches={}
    sidewalk = {(x,28) for x in range(15,27)}
    if sidewalk & protected or (sidewalk & occupied)-old:
        raise ValueError('Mission mural sidewalk conflicts with a protected cell')
    for x,y in (old-new)|sidewalk:
        char=token('brick_walk',x,y)
        if plan['legend'].get(char,[None,True,None])[1:]!=[False,3]:
            raise ValueError('Mission mural sidewalk is not walkable')
        patches[x,y]=char
    additions=[]
    for nx,block in zip(NEW_X,blocks):
        card=cards[block['style']]
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                patches[nx+dx,24+dy]=chr(0x100+tile-512)
        additions.append(dict(style=block['style'],x=nx,y=24,width=block['width'],height=block['height'],first_metatile=card['tiles'][0][0]))
    def reach(changes):
        start=(16,10)
        def isopen(p):
            x,y=p
            return p not in actors and not plan['legend'][changes.get(p,grid[y][x])][1]
        if not isopen(start): raise ValueError('Mission mural arrival is blocked')
        seen,queue={start},deque([start])
        while queue:
            x,y=queue.popleft()
            for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0<=point[0]<96 and 0<=point[1]<64 and point not in seen and isopen(point):
                    seen.add(point);queue.append(point)
        return seen
    before,after=reach({}),reach(patches)
    if not (before-new)<=after or (10,29) not in after:
        raise ValueError('Mission mural street would strand ground or mural viewpoint')
    for (x,y),char in patches.items():grid[y][x]=char
    occupied.difference_update(old);occupied.update(new)
    for b in blocks:plan['town_blocks'].remove(b)
    plan['town_blocks'].extend(additions)
    plan['mission_mural_street']=dict(bounds=[4,24,25,27],mural=[9,26],view=[10,29])
