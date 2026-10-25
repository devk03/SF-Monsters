"""Authored Dogpatch blocks, working yards and timber quay; no generic packing.

The service core and progression bindings remain; outside-core geography is
composed as a district. Return a fully checked copy, never a partial mutation.
"""
from copy import deepcopy
from collections import deque
from world_district_layouts import raster_path
from world_architecture import FORMS

ROWS = (
    (41,1,('workshop','walkup__sage','duplex','deco__sage','gable')),
    (44,6,('workshop','walkup__sage','duplex','deco')),
    (38,18,('arcade','workshop__sage','deco','walkup__sage','duplex')),
    (38,25,('arcade','workshop','duplex__sage','deco')),
    (2,25,('workshop','walkup__sage','duplex','deco')),
    (20,25,('gable__sage','arcade','workshop','walkup')),
    (2,44,('workshop','workshop__sage','arcade','walkup','duplex','deco')),
    (38,44,('workshop','flats__sage','shophouse','workshop__sage','deco')),
    (5,55,('duplex__sage','deco','arcade__sage')),
    (20,55,('walkup__sage','duplex','deco__sage','gable')),
    (38,55,('workshop','walkup__sage','arcade','duplex','deco__sage','gable')),
)
BUILDINGS = (
    ('corner_walkup',38,1),('corner_walkup_sage',53,18),
    ('corner_walkup',2,53),
    ('native_loft',58,3),('workshop',70,5),
    ('native_loft',58,18),('workshop',67,19),('workshop__sage',70,19),
    ('native_loft',2,35),('factory_sage',11,35),('factory',20,35),
    ('factory',38,35),('factory_sage',46,35),('native_loft',59,36),
    ('garage_hall',22,44),('garage_hall',59,44),('workshop',66,44),
)
# Scripts, local IDs and resident order are stable, positions follow actual use.
RESIDENTS = ((55,27),(69,26),(65,57),(81,45),(25,60),(51,23),(39,42),(56,10))
AMBIENT = (
    (37,16,'Courier','OBJ_EVENT_GFX_MAN_2',0,1,
     "I'm picking up, not delivering. They still handed me three bags."),
    (43,10,'Coffee break','OBJ_EVENT_GFX_WOMAN_4',0,0,
     "I said I'd be back in five minutes. That was before I found this bench."),
    (80,25,'Quay walker','OBJ_EVENT_GFX_WOMAN_1',0,1,
     "The wind's fine until you try to unfold a receipt."),
    (90,21,'Deck hand','OBJ_EVENT_GFX_MAN_5',0,0,
     "Other pier for the pickup. This one's for loading. Happens all day."),
    (68,58,'Garden neighbor','OBJ_EVENT_GFX_WOMAN_2',0,0,
     "We water these in shifts. Everyone remembers their shift after it rains."),
    (52,29,'Studio assistant','OBJ_EVENT_GFX_MAN_3',0,0,
     "If you're here for the ceramics, go round the side. The big door's stuck again."),
)
VIEWS = ((35,32,'West entry'),(47,10,'Mixed-use street'),
         (56,26,'Studio service aisle'),(18,43,'West loading yard'),
         (56,42,'Main working court'),(79,29,'Quay approach'),
         (91,22,'North timber pier'),(90,42,'South timber pier'),
         (66,59,'Waterfront pocket'))


def rect(x,y,w,h):return {(xx,yy) for yy in range(y,y+h) for xx in range(x,x+w)}


def compose(source,cards):
    p=deepcopy(source);width,height=96,64
    if p['world_id']!='dogpatch' or len(p['rows'])!=24:
        raise ValueError('Compose Dogpatch directly from its unfurnished32x24 service core')
    def token(style,x=0,y=0):
        rows=cards[style]['tiles'];return chr(0x100+rows[y%len(rows)][x%len(rows[0])]-512)
    grid=[[token('slab_walk',x,y) for x in range(width)] for y in range(height)]
    core=rect(0,0,32,24)
    for y,row in enumerate(p['rows']):
        for x,char in enumerate(row):
            grid[y][x]=token('slab_walk',x,y) if x==31 or y==23 else char
    blocks=list(p['town_blocks']);occupied=set().union(*(rect(b['x'],b['y'],b['width'],b['height']) for b in blocks))
    roads=set()
    def fill(cells,style):
        for x,y in cells-core:
            if 0<=x<width and 0<=y<height:grid[y][x]=token(style,x,y)
    def road(line):
        cells=raster_path(line,radius=1);roads.update(cells)
        fill(cells,'asphalt')
        for (x0,y0),(x1,y1) in zip(line,line[1:]):
            if y0==y1:
                fill({(x,y0-2) for x in range(min(x0,x1),max(x0,x1)+1)},'curb_north')
                fill({(x,y0+2) for x in range(min(x0,x1),max(x0,x1)+1)},'curb_south')
    lines=(((35,1),(35,60)),((75,1),(75,60)),((32,12),(75,12)),
           ((0,32),(75,32)),((0,50),(75,50)))
    for line in lines:road(line)
    # Curb bands must stop at intersections, never stripe across a through road.
    fill(roads,'asphalt')
    for x in (35,75):fill(rect(x-1,31,3,3),'crossing')
    # Hard work courts are contained between actual buildings. Green is one
    # deliberate public pocket, not a collar around every pasted facade.
    fill(rect(10,40,20,8),'dark_walk');fill(rect(38,40,35,8),'dark_walk')
    fill(rect(58,25,15,4),'dark_walk');fill(rect(58,55,15,6),'grass')
    fill(rect(64,53,2,8),'stone_walk');fill(rect(58,59,22,2),'stone_walk')
    for y in range(height):
        for x in range(width):
            if x>=84 or y>=62:grid[y][x]=token('scenic_sea',x,y)
    fill(rect(78,1,6,61),'stone_walk')
    fill(rect(83,1,1,61),'seawall')
    fill(rect(1,61,83,1),'seawall')
    for x,y,w,h in ((84,20,10,4),(84,40,9,4)):
        fill(rect(x,y,w,h),'dock_deck')
        fill(rect(83,y,1,h),'dock_deck')
    # Rest/promenade surfacing must not erase the actual road beneath it.
    fill(roads,'asphalt')
    for x in (35,75):fill(rect(x-1,31,3,3),'crossing')
    fill(rect(74,59,3,1),'crossing')
    # Actors are placed before scenery so every footprint respects the complete
    # roaming envelope and interaction standing cell, not just the actor pixel.
    residents=[n for n in p['npcs'] if n['script'].startswith('WBTown_')]
    if len(residents)!=len(RESIDENTS):raise ValueError('Dogpatch resident contract changed')
    for npc,(x,y) in zip(residents,RESIDENTS):npc.update(x=x,y=y)
    for index,(x,y,role,graphics,rx,ry,dialogue) in enumerate(AMBIENT):
        label='WBAmbient_dogpatch_'+str(index)
        movement=('MOVEMENT_TYPE_WANDER_UP_AND_DOWN' if ry else
                  'MOVEMENT_TYPE_FACE_DOWN')
        p['npcs'].append(dict(id=len(p['npcs'])+1,x=x,y=y,role=role,
            graphics=graphics,script=label,movement=movement,range_x=rx,range_y=ry))
        p.setdefault('extra_street_signs',[]).append(dict(script=label,text=dialogue,npc=True))
    actors={(n['x']+dx,n['y']+dy) for n in p['npcs']
            for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
            for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    keep={(e['x'],e['y']) for key in ('access_points','coord_events') for e in p.get(key,[])}
    approaches=set()
    def put(style,x,y):
        card=cards[style];w,h=len(card['tiles'][0]),len(card['tiles']);cells=rect(x,y,w,h)
        if cells&(core|occupied|roads|actors|keep|approaches) or any(not 0<xx<95 or not 0<yy<62 for xx,yy in cells):
            raise ValueError('Dogpatch authored footprint conflict: '+str((style,x,y)))
        if any(p['legend'][grid[yy][xx]][1] for xx,yy in cells):
            raise ValueError('Dogpatch footprint replaces water/edge: '+str((style,x,y)))
        if card.get('architecture_type'):
            front=rect(x,y+h,w,1)
            if front&(occupied|actors) or any(yy>=62 for _,yy in front):
                raise ValueError('Dogpatch facade has no clear threshold: '+str((style,x,y)))
            approaches.update(front)
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x100+tile-512)
        occupied.update(cells)
        blocks.append(dict(style=style,x=x,y=y,width=w,height=h,first_metatile=card['tiles'][0][0]))
    for x,y,styles in ROWS:
        for style in styles:
            put(style,x,y);x+=len(cards[style]['tiles'][0])
    for style,x,y in BUILDINGS:put(style,x,y)
    # Deliberate fixtures: street corners, yard loading edges and a planted
    # waterfront rest. Two clear quay columns remain continuous beside docks.
    for style,x,y in (
        ('lamp',33,17),('rack',39,15),('street_tree',54,15),
        ('street_tree',41,7),('bench',41,9),('flower_box',43,9),
        ('street_tree',50,25),('flower_box',52,27),
        ('recycling',12,42),('rack',28,42),('bin',52,41),
        ('lamp',73,35),('lamp',77,54),('crane',79,15),('crane',79,35),
        ('bench',59,56),('street_tree',70,55),('flower_box',60,59),
        ('succulent',71,58),('shrub',69,59)):
        put(style,x,y)
    for x,y,w in ((84,20,10),(84,23,10),(84,40,9),(84,43,9)):
        for xx in range(x,x+w):put('dock_rail',xx,y)
    for x,y in ((93,21),(93,22),(92,41),(92,42)):put('dock_rail',x,y)
    def notice(script,name,obj,standing,text):
        x,y=obj;put('shop_board',x,y)
        p.setdefault('bg_events',[]).append(dict(type='sign',x=x,y=y,elevation=0,player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=script))
        p['access_points'].append(dict(kind='checkpoint',name=name,activation='interact',x=standing[0],y=standing[1]))
        p.setdefault('extra_street_signs',[]).append(dict(script=script,text=text))
    for args in (
        ('WBCourt_dogpatch_0','pedestrian_court_0',(56,8),(57,8),'Studio passage. Upstairs neighbors, downstairs workshops. Please keep the delivery gap open.'),
        ('WBCourt_dogpatch_1','pedestrian_court_1',(57,44),(56,44),'Loading court. The paint on the floor is not a parking reservation.'),
        ('WBParcel_dogpatch','parcel_notice',(57,26),(56,26),'Repair and pottery studios. Deliveries use this narrow aisle; the main street is not a loading bay.'),
        ('WBPlace_dogpatch','concept_place',(17,43),(18,43),'Working yard. The cranes are on the quay. Please do not leave your bicycle in the loading mouth.'),
        ('WBStreet_dogpatch_expanded_0','district_wayfinder',(37,29),(37,30),'West: the neighborhood route. East: working yards and the waterfront. Repair Counter is in the northwest block.'),
        ('WBStreet_dogpatch_expanded_1','district_wayfinder',(78,47),(79,47),'Quay walk. Timber piers lead east; the planted rest is south. Delivery access stays clear.')):
        notice(*args)
    # Complete party walls are selected from actual final neighboring masses.
    architecture=[b for b in blocks if cards[b['style']].get('architecture_type')]
    for b in architecture:
        family=cards[b['style']]['architecture_type']
        if family not in FORMS:continue
        joined=[]
        for side in ('left','right'):
            edge=b['x'] if side=='left' else b['x']+b['width']
            joined.append(any(o is not b and (o['x']+o['width'] if side=='left' else o['x'])==edge and o['y']<=b['y'] and o['y']+o['height']>=b['y']+b['height'] for o in architecture))
        left,right=joined;suffix='_m' if left and right else '_r' if left else '_l' if right else ''
        paint='__'+b['style'].split('__')[1] if '__' in b['style'] else ''
        style=family+suffix+paint
        for dy,row in enumerate(cards[style]['tiles']):
            for dx,tile in enumerate(row):grid[b['y']+dy][b['x']+dx]=chr(0x100+tile-512)
        b.update(style=style,first_metatile=cards[style]['tiles'][0][0])
    for y in range(height):
        for x in range(width):
            if (x in (0,95) or y in (0,63)) and x<84 and y<62:grid[y][x]=token('edge_hedge',x,y)
    for y in (31,32,33):grid[y][0]=token('slab_walk',0,y)
    # One real source. Every legal standing cell, not merely selected targets,
    # must connect to it; isolated walkable islands are unsafe for older Saves.
    free={(x,y) for y,row in enumerate(grid) for x,c in enumerate(row) if not p['legend'][c][1] and (x,y) not in actors}
    seen={(16,16)};queue=deque(seen)
    while queue:
        x,y=queue.popleft()
        for q in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if q in free and q not in seen:seen.add(q);queue.append(q)
    if (free-seen)-core:raise ValueError('Dogpatch has isolated new legal ground: '+str(sorted((free-seen)-core)[:8]))
    targets={(a['x'],a['y']) for a in p['access_points']}|approaches
    targets-=actors
    if not targets<=seen:raise ValueError('Dogpatch loses a service, notice or frontage approach')
    p.update(rows=[''.join(r) for r in grid],town_blocks=blocks,water_positions=[],
             scenic_viewpoints=[dict(name=n,x=x,y=y) for x,y,n in VIEWS]+p.get('scenic_viewpoints',[]),
             expanded_design=dict(size=[96,64],circulation=[list(line) for line in lines],legacy_service_block=[0,0,31,23],status='whole-district authored candidate; native/human review pending'),
             authored_dogpatch=dict(revision=1,land_use=['mixed-use blocks','studio aisle','working yards','quay','timber piers','one planted rest'],generic_frontage_packing=False,new_flags=0,new_warps=0))
    p['border_tile']=cards['scenic_sea']['tiles'][0][0]
    p['border_metatiles']=[p['border_tile']]*4
    return p
