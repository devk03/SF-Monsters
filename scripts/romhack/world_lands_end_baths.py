"""Small Sutro Baths courtyard beside the coastal trail.

Reserve the full footprint before packing the forest. Original stone rim tiles
and existing ruined masonry form solid scenic pools at land elevation.
"""
from collections import deque

RESERVE={(x,y) for y in range(24,34) for x in range(9,36)}
POOLS=({(x,y) for y in range(26,32) for x in range(20,26)},
       {(x,y) for y in range(27,31) for x in range(28,34)})
RUINS=((20,24),)
ROCKS=((30,24),)


def prepare(plan, lanes, protected):
    if plan['world_id']!='lands_end':return None
    reserve=RESERVE-(set(lanes)|set(protected))
    if (set().union(*POOLS) | {(x+dx,y+dy) for x,y in RUINS for dx in range(4) for dy in range(2)}) - reserve:
        raise ValueError('Sutro Baths landmark overlaps a route or protected area')
    for key in ('access_points','bg_events','coord_events','npcs'):
        for event in plan.get(key,[]):
            if (event['x'],event['y']) in RESERVE:
                raise ValueError('Sutro Baths reservation covers an existing event')
    return reserve


def furnish(plan, grid, cards, token, reserve):
    if plan['world_id']!='lands_end':return
    if not reserve or not reserve<=RESERVE:raise ValueError('Reserve Sutro Baths before forest packing')
    patches={point:token('paving' if point[1]==32 or (point[1] in (25,26,31,32) and point[0]>=19) or point[0] in (19,26,27,34) else 'grass') for point in reserve}
    legend={}
    for pool in POOLS:
        for x,y in pool:
            north=(x,y-1) not in pool;south=(x,y+1) not in pool
            west=(x-1,y) not in pool;east=(x+1,y) not in pool
            side=('n' if north else 's' if south else '')+('w' if west else 'e' if east else '')
            side={'n':'north','s':'south','w':'west','e':'east'}.get(side,side)
            patches[x,y]=token('baths_rim_'+side if side else 'scenic_sea')
    rows=cards['bath_ruins']['tiles']
    blocks=[]
    for style,x,y in [('bath_ruins',x,y) for x,y in RUINS]+[('rocks',x,y) for x,y in ROCKS]:
        rows=cards[style]['tiles']
        cells={(x+dx,y+dy) for dy,row in enumerate(rows) for dx,_ in enumerate(row)}
        if not cells<=reserve or cells & set().union(*POOLS):
            raise ValueError('Sutro Baths masonry overlaps a pool or leaves its court')
        for dy,row in enumerate(rows):
            for dx,identifier in enumerate(row):patches[x+dx,y+dy]=chr(0x100+identifier-512)
        blocks.append(dict(style=style,x=x,y=y,width=len(rows[0]),height=len(rows),first_metatile=rows[0][0]))
    for x,y in patches:
        if plan['legend'][grid[y][x]][1]:
            raise ValueError('Sutro Baths would cut a packed tree or existing obstacle')
    def reachable(after):
        start=(12,10);seen={start};queue=deque([start])
        while queue:
            x,y=queue.popleft()
            for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
                nx,ny=x+dx,y+dy
                if not (0<=ny<len(grid) and 0<=nx<len(grid[ny])) or (nx,ny) in seen:continue
                char=patches.get((nx,ny),grid[ny][nx]) if after else grid[ny][nx]
                if not legend.get(char,plan['legend'].get(char))[1]:
                    seen.add((nx,ny));queue.append((nx,ny))
        return seen
    before,after=reachable(False),reachable(True)
    if not (before-set(patches))<=after or not (reserve-set().union(*POOLS)-
            {(b['x']+dx,b['y']+dy) for b in blocks for dy in range(b['height']) for dx in range(b['width'])})<=after:
        raise ValueError('Sutro Baths disconnects a previously reachable path or its courtyard')
    plan['legend'].update(legend)
    for (x,y),char in patches.items():grid[y][x]=char
    plan['town_blocks'].extend(blocks)
    plan['sutro_baths_court']={'bounds':[9,24,35,33],
        'pools':[sorted(map(list,pool)) for pool in POOLS],
        'entrance':[17,32],'scope':'scenic ruined pools; water remains solid'}
    plan.setdefault('scenic_viewpoints',[]).append(dict(name='Sutro Baths courtyard',x=19,y=32))
