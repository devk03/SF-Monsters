"""Compact attached homes below Twin Peaks, with preserved native hill trails.

Reserve before forest packing, furnish after summit drawing. Existing trails,
objects, gym bindings and summit stairs retain their coordinates and surfaces.
"""
from world_district_layouts import raster_path

LOTS = (
    (8,48,('shophouse','walkup__sage','flats','duplex__slate','deco')),
    (40,56,('gable','arcade__sage','workshop__slate','flats')),
    (58,56,('deco__slate','walkup','duplex__sage','shophouse')),
    (76,56,('arcade','workshop__sage','gable__slate','deco')),
)
RECTS = ((6,47,24,55),(38,55,90,62))
LINKS = (((15,53),(26,53),(35,46)),((54,54),(54,61)),((72,53),(72,61)))
NEIGHBORS = (
    (54,60,'Homeowner','OBJ_EVENT_GFX_WOMAN_2',
     "It's quiet here until someone decides these stairs count as a shortcut."),
    (73,60,'Dog walker','OBJ_EVENT_GFX_MAN_3',
     "I'm walking the dog. He's apparently training for something."),
)


def rectangle(left,top,right,bottom):
    return {(x,y) for y in range(top,bottom+1) for x in range(left,right+1)}


def prepare(plan, lanes, protected, cards):
    if plan['world_id']!='twin_peaks':return None
    if plan['tile_profile']!='ridge_town':
        raise ValueError('Ridge homes require the declared hybrid art profile')
    clear=set().union(*(rectangle(*bounds) for bounds in RECTS))
    paths=set().union(*(raster_path(line,radius=1) for line in LINKS))
    clear|=paths
    keep=set(protected)
    for key in ('access_points','coord_events','bg_events'):
        for event in plan.get(key,[]):
            keep|=rectangle(event['x']-1,event['y']-1,event['x']+1,event['y']+1)
    blocks=[]
    for left,top,styles in LOTS:
        x=left
        for style in styles:
            card=cards[style];w,h=len(card['tiles'][0]),len(card['tiles'])
            cells=rectangle(x,top,x+w-1,top+h-1)
            if not cells<=clear or cells&(keep|lanes):
                raise ValueError('Ridge home overlaps an existing trail/binding: '+str((style,x,top)))
            blocks.append(dict(style=style,x=x,y=top,width=w,height=h,
                               first_metatile=card['tiles'][0][0]))
            x+=w
    return dict(clear=clear,paths=paths,protected=keep,lanes=set(lanes),blocks=blocks)


def furnish(plan,grid,draft,token,cards,occupied):
    if plan['world_id']!='twin_peaks':return
    if draft is None:raise ValueError('Reserve ridge homes before forest packing')
    patches={};solid=set();fronts=set();keep=draft['protected']|draft['lanes']
    def floor(cells,style):
        for x,y in cells-keep:patches[x,y]=token(style,x,y)
    # Keep the forest reservation walkable, but do not pave its entire width.
    # Narrow pedestrian links emerge through grass verges; the residential
    # fronts have a distinct sidewalk/curb above a single quiet road row.
    # These are existing lower-layer surfaces, not new solids or allocations.
    links=set().union(*(raster_path(line,radius=0) for line in LINKS))
    floor(links,'stone_walk')
    for left,right,sidewalk in ((6,24,52),(38,90,60)):
        floor(rectangle(left,sidewalk,right,sidewalk),
              'curb_north')
        floor(rectangle(left,sidewalk+1,right,sidewalk+1),'asphalt')
    # Pedestrian curb cuts connect each hill approach without a repeated ramp
    # pattern along every house. The native collision/elevation stays unchanged.
    for x,y in ((24,52),(54,60),(72,60)):
        floor({(x,y)},'curb_cut')
    blocks=list(draft['blocks'])
    for block in blocks:
        x,y,w,h=(block[k] for k in ('x','y','width','height'))
        cells=rectangle(x,y,x+w-1,y+h-1)
        if cells&occupied:raise ValueError('Ridge home overlaps an existing object')
        for dy,row in enumerate(cards[block['style']]['tiles']):
            for dx,tile in enumerate(row):patches[x+dx,y+dy]=chr(0x100+tile-512)
        solid|=cells
        approach=rectangle(x,y+h,x+w-1,y+h+1)
        fronts|=approach
        # The first frontage row is the sidewalk; the second is the street.
        # Avoid repainting either over the deliberately connected curb above.
    # Small useful places face the homes; the original park stops remain above.
    for style,x,y in (('street_tree',22,48),('bench',22,54),('flower_box',22,52)):
        card=cards[style];w,h=len(card['tiles'][0]),len(card['tiles'])
        cells=rectangle(x,y,x+w-1,y+h-1)
        if not cells<=draft['clear'] or cells&(keep|solid|occupied|fronts):
            raise ValueError('Ridge furniture obstructs a home or walking approach')
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):patches[x+dx,y+dy]=chr(0x100+tile-512)
        solid|=cells
        blocks.append(dict(style=style,x=x,y=y,width=w,height=h,first_metatile=card['tiles'][0][0]))
    width,height=len(grid[0]),len(grid)
    if not patches.keys()<=draft['clear']:
        raise ValueError('Ridge composition leaves its pre-forest reservation')
    for (x,y),char in patches.items():
        if not 0<x<width-1 or not 0<y<height-1 or char not in plan['legend']:
            raise ValueError('Ridge composition leaves the map or declared art')
        if plan['legend'][grid[y][x]][1]:
            raise ValueError('Reserve ridge homes before drawing forest or cliffs')
    actors={(x,y) for x,y,*_ in NEIGHBORS}
    def walkable(x,y):
        return (x,y) not in actors and not plan['legend'][patches.get((x,y),grid[y][x])][1]
    seen={p for p in draft['lanes'] if walkable(*p)};pending=list(seen)
    while pending:
        x,y=pending.pop()
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=nx<width and 0<=ny<height and (nx,ny) not in seen and walkable(nx,ny):
                seen.add((nx,ny));pending.append((nx,ny))
    targets=fronts|{(15,53),(54,61),(73,61),(86,61)}
    if not targets<=seen:raise ValueError('Ridge homes or residents have no safe walking return')
    # Nothing is mutated before the complete candidate passes its checks.
    for (x,y),char in patches.items():grid[y][x]=char
    occupied|=solid;plan['town_blocks'].extend(blocks)
    for index,(x,y,role,graphics,text) in enumerate(NEIGHBORS):
        label='WBRidge_Neighbor_'+str(index)
        identifier=max(n['id'] for n in plan['npcs'])+1
        plan['npcs'].append(dict(id=identifier,x=x,y=y,role=role,graphics=graphics,script=label))
        plan.setdefault('extra_street_signs',[]).append(dict(script=label,text=text,npc=True))
        plan['access_points'].append(dict(kind='checkpoint',name='ridge_neighbor_'+str(index),
                                         activation='interact',x=x,y=y+1))
    plan.setdefault('scenic_viewpoints',[]).extend([
        dict(name='West hillside homes',x=15,y=53),
        dict(name='Lower ridge street',x=54,y=61),
        dict(name='Eastern ridge homes',x=86,y=61)])
    plan['ridge_neighborhood']=dict(homes=len(draft['blocks']),neighbors=len(NEIGHBORS),
        bounds=[list(r) for r in RECTS],existing_trails_preserved=True,
        street_materials='narrow stone links, grass verges, curb and asphalt',
        visual_acceptance='native review pending')
