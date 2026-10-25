"""Whole-stamp industrial replacement beside Dogpatch's planted passage.

Run after ordinary packing/ground, before final attachment and residents.
Do not exclude these plots from packing: later frontage indices must stay put.
New fronts are scenery; the original Repair Counter and court keep their state.
"""
from copy import deepcopy

OLD = {(50,37,3,4):'gable',(53,37,3,4):'deco',(60,37,3,4):'duplex',
       (50,43,3,4):'arcade',(53,43,2,4):'flats',(55,43,2,4):'shophouse',
       (52,36,1,1):'shrub'}
NEW = (('warehouse',50,36,7,5),('workshop',60,37,3,4),('garage_hall',50,43,6,4))
ACTORS = ((12,9,0),(60,27,1),(79,30,1),(54,47,0),(24,47,0),
          (74,53,0),(38,29,0),(79,14,0),(50,34,0))
VIEWS = ((53,41),(53,48),(46,42),(58,41))


def rect(x,y,w,h):
    return {(x+dx,y+dy) for dy in range(h) for dx in range(w)}


def transaction_cells():
    return set().union(*(rect(*b) for b in OLD),*(rect(*n[1:]) for n in NEW))


def prepare(plan,grid,cards,lanes,walks,occupied,sea,shore):
    if plan['world_id']!='dogpatch':return None
    if plan['tile_profile']!='industrial' or len(grid)!=64 or any(len(r)!=96 for r in grid):
        raise ValueError('Dogpatch works require the expanded industrial map')
    cells=transaction_cells();retired={}
    for index,block in enumerate(plan['town_blocks']):
        bounds=tuple(block[k] for k in ('x','y','width','height'))
        footprint=rect(*bounds)
        if not footprint&cells:continue
        if not footprint<=cells:raise ValueError('Dogpatch works would crop an existing stamp')
        family=cards[block['style']].get('architecture_type',block['style'])
        if bounds not in OLD or family!=OLD[bounds]:
            raise ValueError('Dogpatch works overlaps an unexpected facade or prop')
        if any(tuple(b[k] for k in ('x','y','width','height'))==bounds for b in retired.values()):
            raise ValueError('Dogpatch works contains duplicate stamp ownership')
        retired[index]=deepcopy(block)
    if {tuple(b[k] for k in ('x','y','width','height')) for b in retired.values()}!=set(OLD):
        raise ValueError('Dogpatch works frozen whole-stamp footprints are missing')
    old_solid=set().union(*(rect(*b) for b in OLD))
    keep=rect(0,0,32,24)
    for key in ('access_points','coord_events','bg_events'):
        keep|={(e['x'],e['y']) for e in plan.get(key,[])}
    actors={(x+dx,y) for x,y,rx in ACTORS for dx in range(-rx,rx+1)}
    actors|={(n['x']+dx,n['y']+dy) for n in plan['npcs']
             for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
             for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    keep|=actors
    # Preserve the entire planted court, not just its notice/standing cell.
    keep|=rect(57,39,3,9)
    if cells&(keep|set(lanes)|set(walks)|set(sea)|set(shore)):
        raise ValueError('Dogpatch works overlaps a path, court, resident or protected binding')
    if set(occupied)&cells!=old_solid:
        raise ValueError('Dogpatch works contains unowned or missing occupancy')
    for x,y in cells:
        if plan['legend'][grid[y][x]][1] != ((x,y) in old_solid):
            raise ValueError('Dogpatch works old collision/terrain has changed')
    return dict(cells=cells,retired=retired,old_solid=old_solid,actors=actors,
        lanes=set(lanes),walks=set(walks),sea=set(sea),shore=set(shore),
        old_grid={(x,y):grid[y][x] for x,y in cells})


def furnish(plan,grid,cards,token,occupied,draft):
    if plan['world_id']!='dogpatch':return
    if draft is None:raise ValueError('Prepare the complete Dogpatch replacement first')
    fresh=prepare(plan,grid,cards,draft['lanes'],draft['walks'],occupied,draft['sea'],draft['shore'])
    if fresh!=draft:raise ValueError('Dogpatch transaction changed after preparation')
    patches={point:token('slab_walk',*point) for point in fresh['cells']};solid=set();blocks=[]
    if any(plan['legend'].get(c,[None,True,None])[1:] != [False,3] for c in patches.values()):
        raise ValueError('Dogpatch service verge must remain ordinary walkable ground')
    for style,x,y,w,h in NEW:
        card=cards.get(style)
        if not card or len(card['tiles'])!=h or any(len(row)!=w for row in card['tiles']):
            raise ValueError('Dogpatch industrial card dimensions changed: '+style)
        if not card.get('blocked') or card.get('closed_edges')!=['left','right']:
            raise ValueError('Dogpatch industrial fronts need solid complete exterior caps')
        footprint=rect(x,y,w,h)
        if not footprint<=fresh['cells'] or footprint&solid:
            raise ValueError('Dogpatch industrial stamp leaves or overlaps its transaction')
        for dy,row in enumerate(card['tiles']):
            for dx,n in enumerate(row):
                char=chr(0x100+n-512)
                if plan['legend'].get(char)!=[n,True,3]:
                    raise ValueError('Dogpatch industrial art has incompatible collision/elevation')
                patches[x+dx,y+dy]=char
        solid|=footprint
        blocks.append(dict(style=style,x=x,y=y,width=w,height=h,first_metatile=card['tiles'][0][0]))
    width,height=len(grid[0]),len(grid)
    def walkable(point):
        x,y=point
        return point not in fresh['actors'] and not plan['legend'][patches.get(point,grid[y][x])][1]
    start=(46,34);seen={start};pending=[start]
    while pending:
        x,y=pending.pop()
        for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            xx,yy=point
            if 0<=xx<width and 0<=yy<height and point not in seen and walkable(point):
                seen.add(point);pending.append(point)
    targets=set(VIEWS)|{(58,40),(54,48)}
    for _,x,y,w,h in NEW:
        targets|=rect(x,y+h,w,2)-fresh['actors']
    if not targets<=seen:raise ValueError('Dogpatch works strands a frontage, court or resident approach')
    # Entire candidate is validated before grid/occupancy/metadata mutation.
    for (x,y),char in patches.items():grid[y][x]=char
    occupied.difference_update(fresh['old_solid']);occupied.update(solid)
    plan['town_blocks']=[b for i,b in enumerate(plan['town_blocks']) if i not in fresh['retired']]+blocks
    plan.setdefault('scenic_viewpoints',[]).extend(dict(name='Dogpatch working block '+str(i+1),x=x,y=y)
        for i,(x,y) in enumerate(VIEWS))
    plan['dogpatch_works']=dict(transaction_cells=len(fresh['cells']),old_stamps=7,new_buildings=3,
        court_preserved=[57,39,59,47],old_solid_cells=len(fresh['old_solid']),new_solid_cells=len(solid),
        new_flags=0,new_warps=0,visual_acceptance='human review pending')
