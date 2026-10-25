"""Three short Richmond frontages along the park's northern/eastern edge.

Prepare before native forest packing; furnish after its complete-tree pass.
Existing route words, landmarks, park stops and lake retain their bindings.
Facades are scenery: no door, contributor state or service is inferred.
"""

GROUPS = (
    (80,4,('shophouse_l','walkup_m__sage','duplex_m','flats_m__sage','shophouse_r')),
    (82,12,('gable_l','deco_m__sage','flats_m','shophouse_r__sage')),
    (84,20,('workshop_l','arcade_m__sage','flats_r')),
)
BOUNDS = ((78,3,93,10),(80,11,93,18),(82,19,93,26))
FRONTAGES = ((80,8,91,9),(82,16,91,17),(84,24,91,25))
RETURN = {(92,28),(93,28),(91,29),(92,29),(90,30),(91,30)}
VIEWPOINTS = ((86,9),(86,17),(88,25),(92,28))
RESIDENTS = (
    (78,8,'Park walker','OBJ_EVENT_GFX_WOMAN_1',(79,8),
     "I came in for a ten-minute walk. That was an hour ago."),
    (80,18,'Richmond neighbor','OBJ_EVENT_GFX_MAN_1',(81,18),
     "Everyone says they live by the park. This time I can actually point to it."),
)


def rectangle(left,top,right,bottom):
    return {(x,y) for y in range(top,bottom+1) for x in range(left,right+1)}


def reserved_cells(identifier):
    if identifier!='golden_gate_park':return set()
    return (set().union(*(rectangle(*bounds) for bounds in BOUNDS))
            | rectangle(92,8,93,28) | rectangle(78,16,83,17) | RETURN)


def prepare(plan,lanes,protected,cards):
    if plan['world_id']!='golden_gate_park':return None
    if plan['tile_profile']!='park_edge':
        raise ValueError('Richmond edge needs the declared park/housing profile')
    clear=reserved_cells(plan['world_id']);keep=set(protected)
    # The three existing park-stop glades are not housing parcels.
    for cx,cy,rx,ry in ((44,20,6,4),(52,42,4,4),(32,49,5,4)):
        keep|={(x,y) for y in range(cy-ry,cy+ry+1) for x in range(cx-rx,cx+rx+1)
               if (x-cx)**2*ry**2+(y-cy)**2*rx**2<=rx**2*ry**2}
    for key in ('access_points','coord_events','bg_events','scenic_viewpoints'):
        for event in plan.get(key,[]):
            keep|=rectangle(event['x']-1,event['y']-1,event['x']+1,event['y']+1)
    for npc in plan['npcs']:
        x,y=npc['x'],npc['y'];rx,ry=npc.get('range_x',0),npc.get('range_y',0)
        keep|=rectangle(x-rx-1,y-ry-1,x+rx+1,y+ry+1)
    if clear&keep:raise ValueError('Richmond reservation overlaps a protected park binding')
    fronts=set().union(*(rectangle(*bounds) for bounds in FRONTAGES))
    blocks=[]
    for left,top,styles in GROUPS:
        x=left
        for style in styles:
            card=cards[style];w,h=len(card['tiles'][0]),len(card['tiles'])
            cells=rectangle(x,top,x+w-1,top+h-1)
            if h!=4 or cells&(keep|lanes|fronts) or not cells<=clear:
                raise ValueError('Richmond facade obstructs a protected path or leaves its plot')
            blocks.append(dict(style=style,x=x,y=top,width=w,height=h,
                               first_metatile=card['tiles'][0][0]));x+=w
    if fronts&set(lanes):raise ValueError('Richmond frontage would replace an existing trail')
    solid=set().union(*(rectangle(b['x'],b['y'],b['x']+b['width']-1,b['y']+3) for b in blocks))
    actors={(x,y) for x,y,*_ in RESIDENTS}
    if actors&(solid|fronts|set(lanes)) or not actors<=clear:
        raise ValueError('Richmond residents obstruct a frontage or original route')
    return dict(clear=clear,protected=keep,lanes=set(lanes),fronts=fronts,blocks=blocks)


def furnish(plan,grid,draft,token,cards,occupied):
    if plan['world_id']!='golden_gate_park':return
    if draft is None:raise ValueError('Reserve Richmond before native forest packing')
    clear=draft['clear'];keep=draft['protected']|draft['lanes'];patches={};solid=set()
    for x,y in draft['fronts']|rectangle(92,8,93,28):
        if (x,y) not in keep:patches[x,y]=token('stone_walk',x,y)
    # Short park links use actual native worn ground, not a broad urban slab.
    for x,y in rectangle(78,16,83,17)|RETURN:
        if (x,y) not in keep:patches[x,y]=chr(0x800+0x124)
    for block in draft['blocks']:
        x,y,w,h=(block[k] for k in ('x','y','width','height'))
        cells=rectangle(x,y,x+w-1,y+h-1)
        if cells&(occupied|keep|solid):raise ValueError('Richmond home overlaps an existing object')
        for dy,row in enumerate(cards[block['style']]['tiles']):
            for dx,tile in enumerate(row):patches[x+dx,y+dy]=chr(0x100+tile-512)
        solid|=cells
    if not patches.keys()<=clear:raise ValueError('Richmond painting leaves its reservation')
    width,height=len(grid[0]),len(grid)
    for (x,y),char in patches.items():
        if not 0<x<width-1 or not 0<y<height-1 or char not in plan['legend']:
            raise ValueError('Richmond references undeclared art or leaves the map')
        if plan['legend'][grid[y][x]][1]:
            raise ValueError('Reserve Richmond before drawing forest or other scenery')
    actors={(x,y) for x,y,*_ in RESIDENTS}
    existing={(n['x']+dx,n['y']+dy) for n in plan['npcs']
              for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
              for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    def walkable(point):
        x,y=point
        return point not in actors|existing and not plan['legend'][patches.get(point,grid[y][x])][1]
    start=(42,20)  # Actual Garden court standing tile, not disconnected lane seeds.
    seen={start};pending=[start]
    while pending:
        x,y=pending.pop()
        for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            xx,yy=point
            if 0<=xx<width and 0<=yy<height and point not in seen and walkable(point):
                seen.add(point);pending.append(point)
    targets=draft['fronts']|rectangle(92,8,93,28)|rectangle(78,16,83,17)|RETURN|set(VIEWPOINTS)
    targets|={standing for _,_,_,_,standing,_ in RESIDENTS}
    if not targets<=seen:raise ValueError('Richmond edge strands a frontage, resident or park return')
    # The full candidate passes before any grid, object or script is mutated.
    for (x,y),char in patches.items():grid[y][x]=char
    occupied|=solid;plan['town_blocks'].extend(draft['blocks'])
    for index,(x,y,role,graphics,standing,text) in enumerate(RESIDENTS):
        label='WBRichmond_Neighbor_'+str(index)
        identifier=max(n['id'] for n in plan['npcs'])+1
        plan['npcs'].append(dict(id=identifier,x=x,y=y,role=role,graphics=graphics,script=label))
        plan.setdefault('extra_street_signs',[]).append(dict(script=label,text=text,npc=True))
        plan['access_points'].append(dict(kind='checkpoint',name='richmond_neighbor_'+str(index),
            activation='interact',x=standing[0],y=standing[1]))
    plan.setdefault('scenic_viewpoints',[]).extend(
        dict(name='Richmond park edge '+str(index+1),x=x,y=y) for index,(x,y) in enumerate(VIEWPOINTS))
    plan['richmond_edge']=dict(homes=len(draft['blocks']),residents=len(RESIDENTS),
        cleared_cells=len(clear),bounds=[list(b) for b in BOUNDS],
        frontage_rows=[list(b) for b in FRONTAGES],original_trails_preserved=True,
        new_warps=0,new_flags=0,visual_acceptance='human review pending')
