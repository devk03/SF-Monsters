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
        if name=='dogpatch':
            from world_dogpatch_district import compose
            authored=compose(plan,cards)
            plan.clear();plan.update(authored)
            continue
        old = plan['rows']
        def token(style,x=0,y=0):
            tiles = cards[style]['tiles']
            return chr(0x100+tiles[y%len(tiles)][x%len(tiles[0])]-512)
        nature = name in NATURE
        ground = 'grove' if nature else 'grass'
        grid = [[token(ground,x,y) for x in range(width)] for y in range(height)]
        directions = [link['direction'] for link in plan['connections'] or []]
        lanes = circulation(name,(width,height),directions)
        from world_coast import shoreline
        sea,shore=shoreline(name,width,height,lanes)
        walks = {(x+dx,y+dy) for x,y in lanes for dx in range(-2,3)
                 for dy in range(-2,3) if 0<x+dx<width-1 and 0<y+dy<height-1}
        material = DISTRICTS.get(name,('slab_walk',))[0]
        for x,y in walks:
            grid[y][x] = token('grass' if nature else material,x,y)
        for x,y in lanes:
            grid[y][x] = token('paving' if nature else 'asphalt',x,y)
        if not nature:
            for x,y in walks-lanes:
                if (x,y+1) in lanes and (x,y-1) not in lanes:
                    grid[y][x]=token('curb_north',x,y)
                elif (x,y-1) in lanes and (x,y+1) not in lanes:
                    grid[y][x]=token('curb_south',x,y)
            horizontals=[];verticals=[]
            for line in STREETS[name]:
                for (x0,y0),(x1,y1) in zip(line,line[1:]):
                    if y0==y1:horizontals.append((min(x0,x1),max(x0,x1),y0))
                    if x0==x1:verticals.append((x0,min(y0,y1),max(y0,y1)))
            crossings={(x,y) for left,right,y in horizontals for x,top,bottom in verticals
                       if left<=x<=right and top<=y<=bottom}
            for cx,cy in crossings:
                for y in range(cy-1,cy+2):
                    for x in range(cx-1,cx+2):
                        if (x,y) in lanes:grid[y][x]=token('crossing',x,y)
                for y in (cy-2,cy+2):
                    for x in range(cx-1,cx+2):
                        if (x,y) in walks-lanes:grid[y][x]=token('curb_cut',x,y)
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
        from world_parcels import reserved_cells,furnish_parcel
        parcel_cells=reserved_cells(name) if not nature else set()
        from world_concept_places import reserved_cells as place_cells, furnish as furnish_place
        if not nature:parcel_cells|=place_cells(name)
        from world_north_beach_frontage import reserved_cells as north_frontage_cells
        if not nature:parcel_cells|=north_frontage_cells(name,cards)
        from world_town_relief import reserved_cells as relief_cells, furnish as furnish_relief
        if not nature:parcel_cells|=relief_cells(name)
        from world_presidio_campus import reserved_cells as campus_cells, furnish as furnish_campus
        if not nature:parcel_cells|=campus_cells(name)
        passage_cells=set()
        front_approaches=set()
        def stamp(style,x,y,*,shoulder=False,parcel=False,passage=False):
            card = cards[style]
            cells = {(x+dx,y+dy) for dy,row in enumerate(card['tiles']) for dx,_ in enumerate(row)}
            if (cells & occupied or any(xx<1 or yy<1 or xx>=width-1 or yy>=height-1
                                       or xx<32 and yy<24 for xx,yy in cells)):
                return False
            if not parcel and cells & parcel_cells:return False
            if not passage and cells & passage_cells:return False
            if cells & (sea|shore):return False
            if cells & front_approaches:return False
            if cells & (lanes if shoulder else walks):
                return False
            frontage=set()
            if card.get('architecture_type'):
                base=y+len(card['tiles'])
                frontage={(xx,yy) for xx in range(x,x+len(card['tiles'][0])) for yy in (base,base+1)}
                if frontage & (occupied|sea|shore) or base+1>=height-1:return False
                if not parcel and frontage & parcel_cells:return False
            for dy,row in enumerate(card['tiles']):
                for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x100+tile-512)
            occupied.update(cells)
            front_approaches.update(frontage)
            plan['town_blocks'].append(dict(style=style,x=x,y=y,width=len(card['tiles'][0]),
                height=len(card['tiles']),first_metatile=card['tiles'][0][0]))
            return True
        if nature:
            from world_native_parks import native_park
            native_park(plan,grid,lanes,walks,occupied,sea,shore,token,cards,approaches)
        else:
            # Continuous frontage along each authored east/west street. A gap
            # is retained at every real intersection and pedestrian shoulder.
            bands = set()
            for line in STREETS[name]:
                for (x0,y0),(x1,y1) in zip(line,line[1:]):
                    if y0==y1:
                        bands.add((min(x0,x1),max(x0,x1),y0-7))
                        bands.add((min(x0,x1),max(x0,x1),y0+5))
            road_frontages=set(bands)
            # Residential side lanes occupy block interiors instead of leaving
            # entire green rectangles between the principal street walls.
            phase=sum(map(ord,name))%4
            for top in range(25+phase,height-5,8):
                bands.add((2,width-2,top))
            # Fill the unprogrammed block interiors with small housing courts.
            # Keep two real walking tiles below every frontage; this adds land
            # use rather than decorating a giant empty lawn with random props.
            for top in range(5+phase,height-6,7):
                bands.add((2,width-2,top))
            from world_pedestrian_courts import propose,furnish
            courts=propose(name,bands,width,height,occupied|parcel_cells|sea|shore,walks,lanes)
            passage_cells=set().union(*(p['cells'] for p in courts)) if courts else set()
            furnish(plan,grid,courts,stamp,token,material)
            from world_concept_blocks import frontage_bands, mark_composition
            authored = frontage_bands(name)
            if authored is not None:
                bands = authored|road_frontages
                mark_composition(plan)
            index = 0
            for left,right,top in sorted(bands,key=lambda b:(b[2],b[0])):
                # This infill is a new independent block. Its eight buildings
                # must not advance the established selection rhythm for every
                # later Potrero street or change unrelated saved positions.
                independent = name=='potrero_hill' and (left,right,top)==(4,29,24)
                previous_index = index
                x = max(1,left)
                while x<min(width-1,right):
                    from world_frontage_identity import frontage
                    style=frontage(name,index,x,top,cards)
                    w = len(cards[style]['tiles'][0])
                    if x+w<=right and stamp(style,x,top):
                        # A neutral threshold strip belongs to each street wall.
                        bottom = top+len(cards[style]['tiles'])
                        for yy in (bottom,bottom+1):
                            for xx in range(x,x+w):
                                if 0<yy<height-1 and (xx,yy) not in occupied|lanes:
                                    grid[yy][xx]=token(material,xx,yy)
                        x += w
                        index += 1
                    else:
                        x += 1
                if independent:index = previous_index
            # Fixtures follow the outside sidewalk edge, leaving the inner
            # curb strip clear. No tree, pole or bench may occupy road cells.
            from world_botany import PLANTINGS
            species=PLANTINGS[name]
            motifs={'industrial':('lamp','recycling','rack','street_tree'),
                    'civic':('lamp','street_tree','bench','bin'),
                    'culture':('street_tree','lamp','bench','street_tree'),
                    'stadium':('rack','lamp','street_tree','bin')}.get(profile,
                    ('street_tree','lamp','bench','street_tree'))
            fixtures=[]
            for left,right,y in horizontals:
                for x in range(left+6,right-3,11):
                    fixtures.extend([(x,y-4),(x+4,y+3)])
            for x,top,bottom in verticals:
                for y in range(top+7,bottom-3,13):
                    fixtures.extend([(x-4,y),(x+3,y+4)])
            for index,(x,y) in enumerate(dict.fromkeys(fixtures)):
                style=motifs[(index+len(name))%len(motifs)]
                if stamp(style,x,y,shoulder=True):
                    plan.setdefault('expanded_details',[]).append({'name':style,'x':x,'y':y})
                plant=species[index%len(species)]
                if stamp(plant,x+3,y,shoulder=True):
                    plan.setdefault('expanded_details',[]).append({'name':plant,'x':x+3,'y':y})
            # Additional readable directions belong where the new blocks meet,
            # with a free standing tile and no persistent-state reservation.
            for index,(tx,ty) in enumerate(((44,30),(76,48))):
                for x,y in sorted(walks-lanes,key=lambda p:(abs(p[0]-tx)+abs(p[1]-ty),p[1],p[0])):
                    if x<32 and y<26:continue
                    if (x,y) in sea|shore:continue
                    if (x,y) in occupied:continue
                    if not stamp('wayfinder',x,y-2,shoulder=True):continue
                    label=f'WBStreet_{name}_expanded_{index}'
                    original=next(s['text'] for s in plan['street_signs'] if s['style']==('wayfinder' if index==0 else 'shop_board'))
                    text=original if index==0 else original+' Neighborhood services are in the northwest block.'
                    plan.setdefault('extra_street_signs',[]).append(dict(script=label,text=text))
                    plan.setdefault('bg_events',[]).append(dict(type='sign',x=x,y=y-1,elevation=0,
                        player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=label))
                    plan['access_points'].append(dict(kind='checkpoint',name='district_wayfinder',
                        activation='interact',x=x,y=y))
                    break
        if not nature:furnish_parcel(plan,grid,cards,stamp,token)
        if not nature:furnish_place(plan,grid,cards,stamp,token,lanes)
        if not nature:furnish_relief(plan,grid,lanes,walks,occupied,token,cards)
        if not nature:furnish_campus(plan,grid,lanes,walks,occupied,token,cards)
        if name=='north_beach':
            from world_north_beach_frontage import furnish as furnish_north_frontage
            furnish_north_frontage(stamp,grid,token,lanes,cards)
        if not nature:
            from world_concept_blocks import furnish_ground
            furnish_ground(plan,grid,stamp,token)
            from world_presidio import landscape as presidio_landscape
            presidio_landscape(plan,grid,lanes,walks,occupied,token)
            from world_marina_venues import prepare as prepare_venues, furnish as furnish_venues
            venue_draft=prepare_venues(plan,grid,cards,lanes,walks,occupied,sea,shore)
            furnish_venues(plan,grid,cards,token,occupied,venue_draft)
            from world_dogpatch_works import prepare as prepare_works, furnish as furnish_works
            works_draft=prepare_works(plan,grid,cards,lanes,walks,occupied,sea,shore)
            furnish_works(plan,grid,cards,token,occupied,works_draft)
        # Match real party-wall art to the final neighboring footprints. An end
        # cap is drawn only where the building actually exposes that side.
        architecture=[b for b in plan['town_blocks'] if cards[b['style']].get('architecture_type')]
        for block in architecture:
            family=cards[block['style']].get('architecture_type')
            if family not in FORMS:continue
            def joined(side):
                edge=block['x'] if side=='left' else block['x']+block['width']
                return any(other is not block and
                    (other['x']+other['width'] if side=='left' else other['x'])==edge
                    and other['y']<=block['y'] and other['y']+other['height']>=block['y']+block['height']
                    for other in architecture)
            left,right=joined('left'),joined('right')
            suffix='_m' if left and right else '_r' if left else '_l' if right else ''
            paint='__'+block['style'].split('__')[1] if '__' in block['style'] else ''
            style=family+suffix+paint
            card=cards[style]
            for dy,row in enumerate(card['tiles']):
                for dx,tile in enumerate(row):grid[block['y']+dy][block['x']+dx]=chr(0x100+tile-512)
            block['style']=style;block['first_metatile']=card['tiles'][0][0]
        # Seal the true enlarged edge, then reopen only declared route lanes.
        edge = 'grove' if nature else 'edge_hedge'
        for y in range(height):
            for x in range(width):
                if x in (0,width-1) or y in (0,height-1):
                    if not nature:grid[y][x]=token(edge,x,y)
                    elif not plan['legend'][grid[y][x]][1]:
                        # Keep complete tree silhouettes already generated at
                        # the edge. Seal leftover half-width shoulders with
                        # native opaque foliage, not a chopped canopy row.
                        leaf=chr(0x800+198);plan['legend'][leaf]=[198,True,3]
                        grid[y][x]=leaf
        for side in directions:
            for delta in (-1,0,1):
                x,y={'left':(0,height//2+delta),'right':(width-1,height//2+delta),
                     'up':(width//2+delta,0),'down':(width//2+delta,height-1)}[side]
                grid[y][x]=token('grass' if nature else material,x,y)
        # Scenic water stays solid: traversal still occurs only through the
        # declared Surf connectors. Landward seawalls and actual piers make
        # these full districts read as coast/islands rather than hedge boxes.
        for x,y in sea:grid[y][x]=token('scenic_sea',x,y)
        for x,y in shore:
            if (x,y) not in occupied:grid[y][x]=token('seawall',x,y)
        if name=='outer_sunset':
            # A narrow walkable beach replaces the inland-facing concrete wall.
            # Native sand is land, while the existing scenic water remains solid.
            # Keep route lanes, fixtures and the legacy service block unchanged.
            sand=chr(0x800+0x124);plan['legend'][sand]=[0x124,False,3]
            for x,y in sea:
                if y>=9:
                    kind='sunset_surf' if (x+1,y) not in sea else 'sunset_ocean'
                    grid[y][x]=token(kind+('_alt' if (x+y)%2 else ''))
            for y in range(24,height-1):
                for x in range(1,12+(y//6)%2):
                    if (x,y) in sea|lanes|occupied:continue
                    if (x,y) in shore or grid[y][x]==token('grass',x,y):
                        grid[y][x]=sand
        if name=='angel_island':
            # The former compact map's east shore is now inland. Remove only
            # those obsolete sea/wall cells, retaining landmarks and actors.
            for y in range(1,23):
                for x in range(27,32):
                    if (x,y) not in occupied and grid[y][x] in (token('scenic_sea'),token('seawall')):
                        grid[y][x]=token('grass',x,y)
        # Keep local IDs and scripts stable while letting the expanded district
        # feel inhabited beyond its original service block. Reserve every real
        # interaction approach and the complete horizontal wandering envelope.
        reserved={(p['x'],p['y']) for p in plan['access_points']}
        reserved|={(p['x'],p['y']) for p in plan['coord_events']}
        residents=[n for n in plan['npcs'] if n['script'].startswith('WBTown_')]
        anchors=[(42,14),(80,30),(54,48),(24,48),(74,52),(38,32),(82,14),(48,34)]
        resident_space=walks-lanes
        if plan.get('parcel_resident_anchor'):
            anchors[0]=tuple(plan['parcel_resident_anchor'])
            resident_space|=parcel_cells
        if nature:
            meadows=plan['native_park_design']['meadows']
            anchors=[(cx+2,cy+1) for cx,cy,_,_ in meadows]
            resident_space={(x,y) for cx,cy,rx,ry in meadows
                for y in range(cy-ry,cy+ry+1) for x in range(cx-rx,cx+rx+1)
                if (x-cx)**2*ry**2+(y-cy)**2*rx**2<=rx**2*ry**2}
        for index,npc in enumerate(residents):
            others={(n['x']+dx,n['y']) for n in plan['npcs'] if n is not npc
                    for dx in range(-n.get('range_x',0),n.get('range_x',0)+1)}
            rx=npc.get('range_x',0)
            candidates=[]
            for x,y in resident_space:
                envelope={(x+dx,y) for dx in range(-rx,rx+1)}
                if x<32 and y<24 or envelope & (others|reserved):continue
                if not nature and any((x+dx,y+dy) in lanes for dx,dy in ((-1,0),(1,0),(0,-1),(0,1))):continue
                if all(0<xx<width-1 and 0<yy<height-1
                       and not plan['legend'][grid[yy][xx]][1] for xx,yy in envelope):
                    candidates.append((x,y))
            if not candidates:raise ValueError(name+': no safe expanded resident position')
            tx,ty=anchors[index%len(anchors)]
            npc['x'],npc['y']=min(candidates,key=lambda p:(abs(p[0]-tx)+abs(p[1]-ty),p[1],p[0]))
        plan['rows']=[''.join(row) for row in grid]
        plan['water_positions']=[[x,y] for y,row in enumerate(grid) for x,value in enumerate(row) if value in 'WV']
        plan['expanded_design']={'size':[width,height],'circulation':STREETS[name],
            'legacy_service_block':[0,0,31,23], 'status':'authored candidate; visual review pending'}
    return result
