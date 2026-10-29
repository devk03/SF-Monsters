"""Join both sides of Castro's central block around a relocated court notice.

This post-packing transaction retains the existing road and house assets. It is
an incremental block composition, not a deep-roof or architecture redesign.
"""
from collections import deque

SCRIPT='WBCourt_castro_1'
OLD=(41,39)
OLD_STAND=(40,39)
OBJECT=(44,41)
STAND=(45,41)
NEW=(('duplex__slate',39,37,3,4),('shophouse',38,43,2,4),('flats__sage',40,43,2,4))


def one(items, predicate, what):
    found=[item for item in items if predicate(item)]
    if len(found)!=1: raise ValueError('Castro block baseline changed: '+what)
    return found[0]


def furnish(plan,grid,cards,token,lanes,walks,occupied,sea,shore,passage_cells):
    if plan['world_id']!='castro': return
    if plan['tile_profile']!='culture' or len(grid)!=64 or any(len(row)!=96 for row in grid):
        raise ValueError('Castro block requires the expanded culture map')
    fixture=one(plan['town_blocks'],lambda b:b['style']=='flower_box' and (b['x'],b['y'])==OLD,'fixture')
    event=one(plan['bg_events'],lambda e:e.get('script')==SCRIPT,'event')
    checkpoint=one(plan['access_points'],lambda e:e.get('name')=='pedestrian_court_1','checkpoint')
    viewpoint=one(plan['scenic_viewpoints'],lambda e:e.get('name')=='Planted pedestrian court 2','viewpoint')
    notice=one(plan['court_notices'],lambda e:e.get('script')==SCRIPT,'notice')
    extra=one(plan['extra_street_signs'],lambda e:e.get('script')==SCRIPT,'extra sign')
    court=one(plan['pedestrian_courts'],lambda e:e.get('zone')==1,'court')
    if ((fixture['width'],fixture['height'])!=(1,1) or (event['x'],event['y'])!=OLD
            or event.get('type')!='sign' or event.get('player_facing_dir')!='BG_EVENT_PLAYER_FACING_ANY'
            or (checkpoint['x'],checkpoint['y'])!=OLD_STAND or checkpoint.get('activation')!='interact'
            or (viewpoint['x'],viewpoint['y'])!=OLD_STAND or notice!=extra
            or notice['object']!=list(OLD) or notice['standing']!=list(OLD_STAND)
            or court!=dict(x=39,top=41,rest=list(OLD_STAND),zone=1)):
        raise ValueError('Castro block court bindings changed')
    card=cards['flower_box'];tile=card['tiles'][0][0]
    if fixture['first_metatile']!=tile or grid[OLD[1]][OLD[0]]!=chr(0x100+tile-512):
        raise ValueError('Castro block fixture changed')
    neighbors=((36,37,3,4,'gable'),(42,37,3,4,'workshop'),
               (35,43,3,4,'walkup'),(42,43,3,4,'arcade'))
    for x,y,w,h,family in neighbors:
        b=one(plan['town_blocks'],lambda b:(b['x'],b['y'],b['width'],b['height'])==(x,y,w,h),'neighbor')
        card=cards[b['style']]
        if card.get('architecture_type')!=family or b['first_metatile']!=card['tiles'][0][0]:
            raise ValueError('Castro block neighboring architecture changed')
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                if grid[y+dy][x+dx]!=chr(0x100+tile-512):
                    raise ValueError('Castro block neighboring pixels changed')
    actors={(n['x']+dx,n['y']+dy) for n in plan['npcs']
            for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)
            for dy in range(-n.get('range_y',0),n.get('range_y',0)+1)}
    bindings={(e['x'],e['y']) for key in ('access_points','coord_events','bg_events','warp_events','scenic_viewpoints')
              for e in plan.get(key,[]) if e is not event and e is not checkpoint and e is not viewpoint and 'x' in e and 'y' in e}
    buildings={(x+dx,y+dy) for _,x,y,w,h in NEW for dx in range(w) for dy in range(h)}
    new=buildings|{OBJECT};protected=set(lanes)|set(walks)|set(sea)|set(shore)|actors|bindings
    if new&protected or new&occupied!={OLD} or STAND in (set(lanes)|actors|bindings|new|occupied):
        raise ValueError('Castro block conflicts: '+str((new&protected,new&occupied,STAND in (set(lanes)|actors|bindings|new|occupied))))
    if any(plan['legend'][grid[y][x]][1] for x,y in new-{OLD}):
        raise ValueError('Castro block covers unowned solid ground')
    for b in plan['town_blocks']:
        footprint={(b['x']+dx,b['y']+dy) for dx in range(b['width']) for dy in range(b['height'])}
        if b is not fixture and footprint&new: raise ValueError('Castro block intersects a stamp')
    patches={};additions=[]
    for style,x,y,w,h in NEW+(('flower_box',*OBJECT,1,1),):
        card=cards.get(style)
        if not card or not card.get('blocked') or len(card['tiles'])!=h or any(len(row)!=w for row in card['tiles']):
            raise ValueError('Castro block replacement card changed: '+style)
        for dy,row in enumerate(card['tiles']):
            for dx,tile in enumerate(row):
                char=chr(0x100+tile-512)
                if plan['legend'].get(char)!=[tile,True,3]:raise ValueError('Castro block collision changed')
                patches[x+dx,y+dy]=char
        additions.append(dict(style=style,x=x,y=y,width=w,height=h,first_metatile=card['tiles'][0][0]))
    # Continue the existing district sidewalk immediately in front of each wall.
    for y in (41,47):
        for x in range(38,43):
            point=(x,y)
            if point in protected|occupied|new: continue
            if grid[y][x]==token('grass',x,y):
                char=token('stone_walk',x,y)
                if plan['legend'].get(char,[None,True,None])[1:]!=[False,3]:raise ValueError('Castro paving blocked')
                patches[point]=char
    def reachable(changes):
        start=(16,10)
        def opened(p):
            x,y=p
            return p not in actors and not plan['legend'][changes.get(p,grid[y][x])][1]
        if not opened(start): raise ValueError('Castro block arrival blocked')
        seen,queue={start},deque([start])
        while queue:
            x,y=queue.popleft()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0<=p[0]<96 and 0<=p[1]<64 and p not in seen and opened(p):seen.add(p);queue.append(p)
        return seen
    before,after=reachable({}),reachable(patches)
    if not (before-new)<=after or STAND not in after:
        raise ValueError('Castro block strands ground or court notice')
    if any(p not in after for p in ((45,40),(45,41),(45,42))):
        raise ValueError('Castro court nook approach blocked')
    for (x,y),char in patches.items():grid[y][x]=char
    occupied.remove(OLD);occupied.update(new)
    passage_cells.difference_update({(x,y) for x in range(39,42) for y in range(38,47)})
    plan['town_blocks'].remove(fixture);plan['town_blocks'].extend(additions)
    event['x'],event['y']=OBJECT;checkpoint['x'],checkpoint['y']=STAND;viewpoint['x'],viewpoint['y']=STAND
    for item in (notice,extra):
        item['object'],item['standing']=list(OBJECT),list(STAND)
        item['text']="A quiet corner to catch your breath. The theater is up the street."
    court.clear();court.update(zone=1,kind='nook',bounds=[44,40,46,42],rest=list(STAND))
    plan['castro_block_join']=dict(walls=[[39,37],[38,43]],object=list(OBJECT),standing=list(STAND))
