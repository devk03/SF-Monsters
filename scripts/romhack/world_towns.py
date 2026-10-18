"""Compact authored SF blocks, kept separate from contributor gym interiors."""
from copy import deepcopy
from world_tiles import compile_kit, legend_for, PROFILES

URBAN = {'dogpatch', 'potrero_hill', 'mission', 'castro', 'outer_sunset',
         'marina', 'pacific_heights', 'noe_valley', 'mission_bay',
         'giants_stadium', 'financial_district', 'north_beach', 'treasure_island'}
GREEN_ROUTES = {'route_05','route_06','route_14','route_15'}


def furnish(plans, manifest):
    if not manifest.get('town_finishing'):
        return plans
    kits = {}
    result = deepcopy(plans)
    streets = {r['id'] for r in manifest['routes'] if r['mode']=='walk' and r['id'] not in GREEN_ROUTES}
    for plan in result:
        connector = plan['world_id'] in streets
        if plan['world_id'] not in URBAN and not connector:
            continue
        profile = manifest['town_finishing'].get('profiles',{}).get(plan['world_id'],'neighborhood')
        if profile not in kits: kits[profile] = compile_kit(profile=profile)
        kit = kits[profile]
        grid = [['#' if x in (0, 31) or y in (0, 23) else '.' for x in range(32)] for y in range(24)]
        # Each record has independently checked collision semantics. No roof
        # tile is placed over a walkable building footprint.
        legend = legend_for(kit)
        occupied = set()
        def stamp(name, left, top):
            card = kit['catalog'][name]
            cells = {(left+x,top+y) for y,row in enumerate(card['tiles']) for x,_ in enumerate(row)}
            if card['blocked']:
                if cells & occupied:
                    raise ValueError(f"{plan['world_id']}: {name}@{left},{top} overlaps {sorted(cells & occupied)}")
                occupied.update(cells)
            for dy, row in enumerate(kit['catalog'][name]['tiles']):
                for dx, tile in enumerate(row):
                    grid[top+dy][left+dx] = chr(0x100 + tile-512)
        ground = chr(0x100)
        for y in range(1, 23):
            for x in range(1, 31): grid[y][x] = ground
        from world_surfaces import DISTRICTS
        district = plan['world_id']
        material, accent, character = DISTRICTS.get(district,
            ('slab_walk','stone_walk','compact connecting street'))
        def surface(name, left, top, right, bottom):
            card = kit['catalog'][name]['tiles']
            for y in range(top,bottom+1):
                for x in range(left,right+1):
                    tile=card[(y-top)%len(card)][(x-left)%len(card[0])]
                    grid[y][x]=chr(0x100+tile-512)
        # Sidewalks have an edge and a purpose. Rear gardens replace the broad
        # empty paved aprons; the walking street remains a clear three-tile lane.
        surface('grass',1,1,30,3)
        surface('grass',1,20,30,22)
        surface(material,1,7,30,10)
        surface(material,1,14,30,16)
        surface(accent,1,7,30,7)
        surface('asphalt',1,11,30,13)
        surface('curb_north',1,10,30,10)
        surface('curb_south',1,14,30,14)
        surface('crossing',14,11,18,13)
        for left,right in ((4,6),(14,18)):
            surface('curb_cut',left,10,right,10)
            surface('curb_cut',left,14,right,14)
        # The landmark belongs to the same street wall as the small fronts.
        # Only an actual north connection gets a three-tile side alley.
        gym = next((g for g in manifest['gyms'] if g['area']==district),None)
        landmark = {'industrial':('crane',14,3),'civic':('highrise',15,2),
                    'culture':('theater',14,3),'stadium':('stadium_gate',13,3)}.get(profile)
        if profile=='neighborhood':
            landmark={'mission':('mural',14,5),
                      'pacific_heights':('mansion',14,3)}.get(district)
        extras=[]
        if profile=='neighborhood':
            extras={'outer_sunset':[('surfboards',18,8)],'marina':[('bar_sign',4,9)],
                    'noe_valley':[('book_box',18,8)],
                    'potrero_hill':[('lookout_left',15,4),('lookout_steps',16,4),
                                    ('lookout_right',17,4)]}.get(district,[])
        centerpiece=landmark or (('cream',14,3) if gym else
                    ('pair',14,3) if not connector and district!='potrero_hill' else None)
        center_left,center_right=(15,17)
        if centerpiece:
            center_left=centerpiece[1]
            center_right=center_left+len(kit['catalog'][centerpiece[0]]['tiles'][0])-1
        blocks=[]
        frontage_runs=[]
        planting_pockets=[]
        choices={
            'industrial':('warehouse','brick','coral','cafe'),
            'civic':('brick','cream','clinic','cafe'),
            'stadium':('cafe','cream'),
        }.get(profile,{
            'mission':('cafe','coral','lilac','cream','pair'),
            'marina':('cream','cafe','lilac','pair'),
            'pacific_heights':('cream','lilac','pair','coral','cafe'),
            'noe_valley':('pair','cafe','cream','lilac'),
            'outer_sunset':('pair','coral','cafe','cream'),
            'potrero_hill':('coral','pair','cream','cafe'),
            'north_beach':('cafe','cream','coral','lilac'),
        }.get(district,('coral','cafe','cream','lilac','pair')))
        def record(style,x,y):
            card=kit['catalog'][style]
            stamp(style,x,y)
            blocks.append({'style':style,'x':x,'y':y,
                'width':len(card['tiles'][0]),'height':len(card['tiles']),
                'first_metatile':card['tiles'][0][0]})
        def attach(left,right,bottom,phase):
            # Exact-width packing gives shared walls, not randomly spaced houses.
            # Keep an explicit gap only if the native art cannot fill one tile.
            def fit(remaining, index):
                if remaining==0:return []
                for n in range(len(choices)):
                    style=choices[(index+n)%len(choices)]
                    width=len(kit['catalog'][style]['tiles'][0])
                    if width<=remaining:
                        rest=fit(remaining-width,index+n+1)
                        if rest is not None:return [style]+rest
                return None
            packed=fit(right-left+1,phase)
            if packed is None:
                if left!=right:
                    raise ValueError(f'{district}: unfilled frontage {left}..{right}')
                top,base=(3,7) if bottom==8 else (16,20)
                surface('grass',left,top,right,base)
                planting_pockets.append({'x':left,'top':top,'bottom':base})
                return
            south_top=17 if district=='outer_sunset' and left<5 else 16
            frontage_runs.append({'left':left,'right':right,'y':7 if bottom==8 else south_top})
            for style in packed:
                card=kit['catalog'][style]
                top=south_top if bottom==21 else bottom-len(card['tiles'])
                record(style,left,top)
                left+=len(card['tiles'][0])
        north_spans=[(1,center_left-1),(center_right+1,30)]
        north_link=any(l['direction']=='up' for l in plan['connections'] or [])
        if north_link and not connector:
            north_spans=[piece for left,right in north_spans
                         for piece in ((left,min(right,10)),(max(left,14),right))
                         if piece[0]<=piece[1]]
            surface(material,11,1,13,7)
            surface(material,11,1,17,2)
        # The fixed service trigger must sit directly below the drawn door.
        # Large service cards have a central door; the narrow cafe has its
        # door in its second metatile. Pin that front before packing neighbors.
        doorway=None
        if not connector:
            style='warehouse' if profile=='industrial' else 'clinic' if profile=='civic' else 'cafe'
            door_offset=3 if style in ('warehouse','clinic') else 1
            left=5-door_offset
            card=kit['catalog'][style];right=left+len(card['tiles'][0])-1
            top=8-len(card['tiles'])
            record(style,left,top)
            frontage_runs.append({'left':left,'right':right,'y':7})
            north_spans=[piece for a,b in north_spans
                         for piece in ((a,min(b,left-1)),(max(a,right+1),b))
                         if piece[0]<=piece[1]]
            doorway={'style':style,'x':left,'y':top,'entry':[5,8]}
        for number,(left,right) in enumerate(north_spans):attach(left,right,8,number)
        down_link=any(l['direction']=='down' for l in plan['connections'] or [])
        passage=(15,17) if down_link or district=='dogpatch' or connector else {
            'mission':(9,10),'potrero_hill':(11,12),'castro':(21,22),
            'noe_valley':(14,15)}.get(district,(15,16))
        south_spans=[(1,passage[0]-1),(passage[1]+1,30)]
        for number,(left,right) in enumerate(south_spans):attach(left,right,21,number+2)
        if centerpiece:record(*centerpiece)
        for item in extras:record(*item)
        coastal=district=='outer_sunset'
        if coastal:
            for y in range(9,17):
                for x in range(4):stamp('scenic_sea',x,y)
                stamp('seawall',4,y)
        if connector:
            for link in plan['connections'] or []:
                if link['direction'] in ('up','down'):
                    surface('asphalt',15,1 if link['direction']=='up' else 12,
                            17,13 if link['direction']=='up' else 22)
            plan['route_setting']='city street'
        # Trees sit in contained wells. Utilities follow the curb; furniture
        # gathers beside shops and destinations instead of filling random gaps.
        props=[('lamp',13,8),('lamp',18,8),('meter',6,10),('hydrant',26,10),
               ('bin',6 if coastal else 2,15),('rack',26,15),('bench',6,9),('tree',28,8)]
        if district in ('outer_sunset','noe_valley'):
            props.remove(('lamp',18,8))
        treatments={
            'dogpatch':[('recycling',9,15),('rack',23,10),('lamp',29,14),('bin',30,8)],
            'mission':[('tree',1,8),('tree',19,8),('tree',20,14),('meter',23,10),('lamp',10,14)],
            'marina':[('tree',1,8),('tree',19,8),('bench',19,15),('lamp',10,14),('meter',23,10)],
            'pacific_heights':[('tree',1,8),('tree',19,8),('tree',20,14),('lamp',10,14)],
            'noe_valley':[('tree',1,8),('tree',20,14),('bench',19,9),('recycling',29,15)],
            'outer_sunset':[('tree',20,14),('recycling',29,15),('lamp',10,14)],
            'potrero_hill':[('tree',1,8),('bench',19,9),('lamp',10,14)],
            'castro':[('bench',19,9),('lamp',10,14),('meter',23,10),('recycling',29,15)],
            'north_beach':[('bench',19,9),('tree',1,8),('meter',23,10),('bin',29,15)],
            'mission_bay':[('tree',1,8),('tree',19,8),('tree',20,14),('lamp',10,14)],
            'financial_district':[('tree',1,8),('tree',19,8),('bench',19,15),('lamp',10,14),('rack',23,10)],
            'giants_stadium':[('rack',22,10),('recycling',29,15),('bench',19,15),('lamp',10,14)],
            'treasure_island':[('recycling',9,15),('bin',29,15),('lamp',24,14)],
        }
        props+=treatments.get(district,[('tree',19,8),('meter',23,10)])
        props=[('street_tree' if name=='tree' else name,x,y) for name,x,y in props]
        for name,x,y in props:
            stamp(name,x,y)
        from world_botany import PLANTINGS
        details=[]
        if district in PLANTINGS:
            species=PLANTINGS[district]
            last=(18,15) if district in ('castro','noe_valley','giants_stadium','outer_sunset') else (30,15)
            beds=[(3,8),(10,8),(17,8),(22,8),last]
            for index,(x,y) in enumerate(beds):
                name=species[index%len(species)];record(name,x,y)
                details.append({'name':name,'x':x,'y':y})
            for pocket in planting_pockets:
                name=species[0];x=pocket['x'];y=pocket['bottom']-1
                record(name,x,y);details.append({'name':name,'x':x,'y':y})
            # The street pole is read at its base; shop boards sit beside the
            # service approach. Neither uses a walking trigger or reward flag.
            board=(9,10) if coastal else (3,9)
            for name,x,y in [('wayfinder',11,8),('shop_board',*board)]:
                record(name,x,y);details.append({'name':name,'x':x,'y':y})
            for x in (10,20,29):stamp('curb_drain',x,10)
        plan['street_details']=details
        plan['street_design']={'sidewalk':material,'threshold':accent,'character':character,
            'frontage_runs':frontage_runs,'planting_pockets':planting_pockets,
            'service_doorway':doorway,'south_passage':{'left':passage[0],'right':passage[1],
                'purpose':'connection' if down_link else 'start courtyard' if district=='dogpatch'
                else 'rear residential garden'},
            'furniture':[{'name':n,'x':x,'y':y} for n,x,y in props]}
        # Preserve the exact three-tile inter-map connection interface.
        hedge=chr(0x100+kit['catalog']['edge_hedge']['tiles'][0][0]-512)
        for y in range(24):
            for x in range(32):
                if x in (0,31) or y in (0,23):
                    if not(coastal and x==0 and 9<=y<=16):grid[y][x]=hedge
        for link in plan['connections'] or []:
            for d in (-1,0,1):
                x,y={'left':(0,12+d),'right':(31,12+d),
                     'up':(16+d,0),'down':(16+d,23)}[link['direction']]
                grid[y][x]=ground
        plan['rows']=[''.join(row) for row in grid]
        plan['legend']=legend
        plan['border_tile']=kit['catalog']['edge_hedge']['tiles'][0][0]
        plan['tile_profile']=profile
        plan['tilesets']['secondary']=PROFILES[profile]
        plan['town_blocks']=blocks
        plan['town_props']=sorted({n for n,_,_ in props})
        features=([landmark] if landmark else [])+extras
        plan['landmarks']=[{'name':style,'x':x,'y':y} for style,x,y in features]
        plan['scenic_viewpoints']=[]
        for style,x,y in features:
            card=kit['catalog'][style];w,h=len(card['tiles'][0]),len(card['tiles'])
            if style in ('lookout_left','lookout_right'):continue
            if style=='lookout_steps':point=(16,5)
            elif landmark and style==landmark[0]:point=(16,8)
            else:point=(x+w//2,y+h)
            plan['scenic_viewpoints'].append({'x':point[0],'y':point[1],'name':style})
        if coastal:plan['scenic_viewpoints'].append({'x':5,'y':14,'name':'ocean_beach_overlook'})
    return result
