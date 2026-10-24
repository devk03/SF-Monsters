"""Expand destinations around authored circulation and stable service bindings."""
from copy import deepcopy
from world_geometry import dimensions, destination_ids
from world_district_layouts import STREETS, circulation, raster_path
from world_tiles import compile_kit
from world_architecture import FORMS
from world_landscape import NATURE
from world_surfaces import DISTRICTS


def expand(plans, manifest):
    if not manifest.get('destination_geometry'):
        return plans
    result = deepcopy(plans)
    kits = {}
    for plan in result:
        name = plan['world_id']
        if name not in destination_ids(manifest):
            continue
        width,height = dimensions(manifest,name)
        profile = plan['tile_profile']
        if profile not in kits:
            kits[profile] = compile_kit(profile=profile)
        cards = kits[profile]['catalog']
        old = plan['rows']
        def token(style,x=0,y=0):
            tiles = cards[style]['tiles']
            return chr(0x100+tiles[y%len(tiles)][x%len(tiles[0])]-512)
        nature = name in NATURE
        ground = 'grove' if nature else 'grass'
        grid = [[token(ground,x,y) for x in range(width)] for y in range(height)]
        directions = [link['direction'] for link in plan['connections'] or []]
        lanes = circulation(name,(width,height),directions)
        walks = {(x+dx,y+dy) for x,y in lanes for dx in range(-2,3)
                 for dy in range(-2,3) if 0<x+dx<width-1 and 0<y+dy<height-1}
        material = DISTRICTS.get(name,('slab_walk',))[0]
        for x,y in walks:
            grid[y][x] = token('grass' if nature else material,x,y)
        for x,y in lanes:
            grid[y][x] = token('paving' if nature else 'asphalt',x,y)
        # Existing service/gym bindings remain in the northwest block. Its old
        # east/south boundary becomes an internal walkway, never a hidden wall.
        for y,row in enumerate(old):
            for x,value in enumerate(row):
                grid[y][x] = token('paving' if nature else material,x,y) if x==31 or y==23 else value
        if nature:
            # Retain every object/landmark binding, but replace the old broad
            # concrete loop with lawn and narrow approaches to its real stops.
            paved=token('paving')
            for y in range(1,24):
                for x in range(1,32):
                    if grid[y][x]==paved:grid[y][x]=token('grass',x,y)
            protected=[(p['x'],p['y']) for p in plan['access_points']]
            protected += [(n['x'],n['y']) for n in plan['npcs']]
            protected += [(p['x'],p['y']) for p in plan.get('scenic_viewpoints',[])]
            approaches=set()
            for point in protected:
                approaches |= raster_path([point,(point[0],12),(32,12)])
            solid={(b['x']+dx,b['y']+dy) for b in plan['town_blocks']
                   for dy in range(b['height']) for dx in range(b['width'])}
            for x,y in approaches:
                if 0<x<32 and 0<y<24 and (x,y) not in solid and grid[y][x] in (token('grass'),paved):
                    grid[y][x]=paved
        occupied = {(x,y) for b in plan['town_blocks'] for y in range(b['y'],b['y']+b['height'])
                    for x in range(b['x'],b['x']+b['width'])}
        def stamp(style,x,y):
            card = cards[style]
            cells = {(x+dx,y+dy) for dy,row in enumerate(card['tiles']) for dx,_ in enumerate(row)}
            if (cells & occupied or any(xx<1 or yy<1 or xx>=width-1 or yy>=height-1
                                       or xx<32 and yy<24 for xx,yy in cells)):
                return False
            if cells & walks:
                return False
            for dy,row in enumerate(card['tiles']):
                for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x100+tile-512)
            occupied.update(cells)
            plan['town_blocks'].append(dict(style=style,x=x,y=y,width=len(card['tiles'][0]),
                height=len(card['tiles']),first_metatile=card['tiles'][0][0]))
            return True
        if nature:
            # Small irregular lawns alternate with complete tree silhouettes.
            # Paths remain three tiles wide; their shoulders are grass, not a
            # giant concrete apron copied from the old compact park loop.
            for cx,cy,radius in [(44,20,6),(68,42,7),(30,48,5),(82,14,4)]:
                for y in range(cy-radius,cy+radius+1):
                    for x in range(cx-radius,cx+radius+1):
                        if (x-cx)**2+(y-cy)**2<radius**2+(x%3)-1 and not(x<32 and y<24):
                            grid[y][x]=token('grass',x,y)
            # Restore trail paint through lawns after their irregular borders.
            for x,y in lanes:
                if not(x<32 and y<24):grid[y][x]=token('paving',x,y)
            for y in range(2,height-4,3):
                for x in range(2,width-4,3):
                    style = 'pine' if (x//3+y//3+len(name))%3 else 'cypress'
                    footprint = cards[style]['tiles']
                    if all(grid[y+dy][x+dx]==token('grove',x+dx,y+dy)
                           for dy,row in enumerate(footprint) for dx,_ in enumerate(row)):
                        stamp(style,x,y)
        else:
            # Continuous frontage along each authored east/west street. A gap
            # is retained at every real intersection and pedestrian shoulder.
            bands = set()
            for line in STREETS[name]:
                for (x0,y0),(x1,y1) in zip(line,line[1:]):
                    if y0==y1:
                        bands.add((min(x0,x1),max(x0,x1),y0-7))
                        bands.add((min(x0,x1),max(x0,x1),y0+5))
            # Residential side lanes occupy block interiors instead of leaving
            # entire green rectangles between the principal street walls.
            phase=sum(map(ord,name))%4
            for top in range(25+phase,height-5,8):
                bands.add((2,width-2,top))
            index = 0
            for left,right,top in sorted(bands,key=lambda b:(b[2],b[0])):
                x = max(1,left)
                while x<min(width-1,right):
                    style = FORMS[(index+len(name))%len(FORMS)]
                    paints = [style,style+'__sage',style+'__slate']
                    style = paints[(index//len(FORMS))%3]
                    if style not in cards:style=paints[0]
                    w = len(cards[style]['tiles'][0])
                    if x+w<=right and stamp(style,x,top):
                        # A neutral threshold strip belongs to each street wall.
                        bottom = top+len(cards[style]['tiles'])
                        for xx in range(x,x+w):
                            if 0<bottom<height-1 and (xx,bottom) not in occupied:
                                grid[bottom][xx]=token(material,xx,bottom)
                        x += w
                        index += 1
                    else:
                        x += 1
        # Seal the true enlarged edge, then reopen only declared route lanes.
        edge = 'grove' if nature else 'edge_hedge'
        for y in range(height):
            for x in range(width):
                if x in (0,width-1) or y in (0,height-1):grid[y][x]=token(edge,x,y)
        for side in directions:
            for delta in (-1,0,1):
                x,y={'left':(0,height//2+delta),'right':(width-1,height//2+delta),
                     'up':(width//2+delta,0),'down':(width//2+delta,height-1)}[side]
                grid[y][x]=token('paving' if nature else material,x,y)
        plan['rows']=[''.join(row) for row in grid]
        plan['water_positions']=[[x,y] for y,row in enumerate(grid) for x,value in enumerate(row) if value in 'WV']
        plan['expanded_design']={'size':[width,height],'circulation':STREETS[name],
            'legacy_service_block':[0,0,31,23], 'status':'authored candidate; visual review pending'}
    return result
