"""Authored compact green spaces and connectors with the same stable route ports."""
from copy import deepcopy
from world_tiles import compile_kit, legend_for, PROFILES

NATURE={'golden_gate_park','twin_peaks','sutro_tower','lands_end','angel_island'}


def landscape(plans, manifest):
    if not manifest.get('town_finishing'):return plans
    result=deepcopy(plans);kit=compile_kit(profile='nature');cards=kit['catalog']
    from generate_world import records
    from world_towns import GREEN_ROUTES
    routes={r['id']:r for r in records(manifest)[1]}
    for plan in result:
        name=plan['world_id'];route=routes.get(name)
        if name not in NATURE and not route:continue
        if route and route['mode']=='walk' and name not in GREEN_ROUTES and route.get('setting')!='green':continue
        old=plan['rows'];grid=[list(row) for row in old]
        token=lambda name:chr(0x100+cards[name]['tiles'][0][0]-512)
        def fill(x0,y0,x1,y1,name):
            for y in range(max(1,y0),min(22,y1)+1):
                for x in range(max(1,x0),min(30,x1)+1):grid[y][x]=token(name)
        def stamp(name,x,y):
            rows=cards[name]['tiles']
            if any(not 0<y+dy<23 or not 0<x+dx<31 for dy,row in enumerate(rows) for dx,_ in enumerate(row)):
                raise ValueError('Landscape card leaves its bounded map')
            for dy,row in enumerate(rows):
                for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x100+tile-512)
        # Preserve the island's switchbacks and named section approaches. Other
        # parks use a legible loop with short landmark pockets, not a huge plaza.
        for y in range(1,23):
            for x in range(1,31):
                grid[y][x]=token(('grass' if name=='angel_island' else 'paving') if old[y][x]=='.' else 'grove')
        if name=='angel_island':
            points=manifest['league']['blockout']['tunnel_path']
            for (x0,y0),(x1,y1) in zip(points,points[1:]):
                fill(min(x0,x1)-1,min(y0,y1)-1,max(x0,x1)+1,max(y0,y1)+1,'paving')
            fill(15,20,17,22,'paving');fill(14,6,18,9,'paving')
        if route and route['mode']!='walk':
            # A real bay crossing, with short dry piers and no walkable bypass.
            for y in range(1,23):
                for x in range(1,31):grid[y][x]='V' if route['mode']=='waterfall' and y==12 else 'W'
            for link in plan['connections'] or []:
                side=link['direction']
                bounds={'left':(1,11,5,13),'right':(26,11,30,13),
                        'up':(15,1,17,4),'down':(15,19,17,22)}[side]
                fill(*bounds,'paving')
        if name in NATURE and name!='angel_island':
            fill(1,1,30,22,'grove')
            for link in plan['connections'] or []:
                side=link['direction']
                if side in ('left','right'):fill(1 if side=='left' else 15,11,17 if side=='left' else 30,13,'paving')
                else:fill(15,1 if side=='up' else 11,17,13 if side=='up' else 22,'paving')
            fill(5,6,26,8,'paving');fill(5,17,26,19,'paving')
            fill(5,6,7,19,'paving');fill(24,6,26,19,'paving')
            fill(10,8,18,11,'paving');fill(11,10,13,18,'paving')
            # Small lawn pockets soften the trail without making walls invisible.
            fill(8,14,11,16,'grass');fill(19,9,23,11,'grass')
            fill(19,14,23,16,'grass');fill(9,20,13,21,'grass')
        landmarks=[]
        if name=='golden_gate_park':
            stamp('windmill',5,2);stamp('conservatory',22,3)
            landmarks=[('windmill',5,2),('conservatory',22,3)]
        elif name=='sutro_tower':
            stamp('sutro_tower',15,1);landmarks=[('sutro_tower',15,1)]
        elif name=='lands_end':
            stamp('bath_ruins',20,4);landmarks=[('bath_ruins',20,4)]
            # The accessible coastal overlook is a compact clearing along the
            # loop, with ruins above it; no fake walkable sea is painted here.
            fill(20,6,27,9,'paving')
        elif name=='twin_peaks':
            # The reserved hardware gym sits above the central trail.
            fill(14,6,18,8,'paving');fill(20,4,27,8,'paving')
            stamp('bench',21,4);stamp('bench',25,4)
            landmarks=[('ridge_lookout',20,4)]
        elif name=='angel_island':
            stamp('conservatory',14,3);stamp('rocks',18,6)
            landmarks=[('conservatory',14,3),('rocks',18,6)]
        if name in NATURE:
            # Furniture stays outside the central info/door approaches. Choose
            # only wholly free patches so a prop never cuts a trail in half.
            for prop,x,y in [('bench',9,18),('bin',23,18),('lamp',18,9)]:
                rows=cards[prop]['tiles']
                points=[(x+dx,y+dy) for dy,row in enumerate(rows) for dx,_ in enumerate(row)]
                if all(grid[yy][xx] in (token('paving'),token('grass')) for xx,yy in points):
                    stamp(prop+'_grass' if all(grid[yy][xx]==token('grass') for xx,yy in points) else prop,x,y)
        else:
            # Dense bordering greenery frames the narrow connecting street;
            # benches and lamps add a pause without bloating route dimensions.
            for prop,x,y in [('bench',9,10),('lamp',21,9)]:
                points=[(x+dx,y+dy) for dy,row in enumerate(cards[prop]['tiles']) for dx,_ in enumerate(row)]
                if all(old[yy][xx]=='#' for xx,yy in points):stamp(prop,x,y)
        if name in ('lands_end','angel_island'):
            for y in range(1,23):
                for x in (1,2,3):grid[y][x]=token('scenic_sea')
                grid[y][4]=token('seawall')
                if name=='angel_island':
                    for x in (28,29,30):grid[y][x]=token('scenic_sea')
                    grid[y][27]=token('seawall')
        # Larger complete silhouettes break up the small canopy fill. Native
        # footprints remain solid and only replace wholly blocked grove cells.
        for y in range(1,21,3):
            for x in range(1,29,3):
                prop='pine' if (x//3+y//3)%2 else 'cypress'
                rows=cards[prop]['tiles']
                points=[(x+dx,y+dy) for dy,row in enumerate(rows) for dx,_ in enumerate(row)]
                if all(0<yy<23 and 0<xx<31 and grid[yy][xx]==token('grove') for xx,yy in points):stamp(prop,x,y)
        # Sealed map boundaries use the same forest fill as the interior, not
        # arbitrary stock building fragments. Connected seams reopen below.
        for y in range(24):
            for x in range(32):
                if x in (0,31) or y in (0,23):
                    sea=(name in ('lands_end','angel_island') and x==0) or (name=='angel_island' and x==31)
                    grid[y][x]=token('scenic_sea' if sea else 'grove')
        # Native seam ports remain exactly three tiles wide and flush with the
        # neighboring map. Seal every other edge, including decorative corners.
        for link in plan['connections'] or []:
            for delta in (-1,0,1):
                x,y={'left':(0,12+delta),'right':(31,12+delta),
                     'up':(16+delta,0),'down':(16+delta,23)}[link['direction']]
                grid[y][x]=token('paving')
        plan.update(rows=[''.join(row) for row in grid],legend=legend_for(kit),tile_profile='nature')
        plan['border_tile']=cards['grove']['tiles'][0][0]
        plan['water_positions']=[[x,y] for y,row in enumerate(grid) for x,value in enumerate(row) if value in 'WV']
        plan['tilesets']['secondary']=PROFILES['nature']
        plan['landmarks']=[{'name':item,'x':x,'y':y} for item,x,y in landmarks]
        plan['town_blocks']=[];plan['scenic_viewpoints']=[]
        for item,x,y in landmarks:
            if item not in cards:
                plan['scenic_viewpoints'].append({'name':item,'x':x,'y':y+2});continue
            card=cards[item];w,h=len(card['tiles'][0]),len(card['tiles'])
            plan['town_blocks'].append({'style':item,'x':x,'y':y,'width':w,'height':h,
                                       'first_metatile':card['tiles'][0][0]})
            plan['scenic_viewpoints'].append({'name':item,'x':x+w//2,'y':y+h})
        if route and route['mode']=='walk':
            from world_green_routes import furnish_green_route
            furnish_green_route(plan,kit)
    return result
