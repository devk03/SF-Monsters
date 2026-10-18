"""Independent street-wall and drawn-door checks; no map producer imports."""

# Deliberate landmark setbacks in the reviewed 32-wide street section. Every
# other cell must be architecture, an actual port alley or a bounded planting
# strip; shortening a producer's declared run cannot make a missing house pass.
CENTERS={'dogpatch':(14,17),'potrero_hill':(15,17),'mission':(14,17),
         'castro':(14,18),'outer_sunset':(14,16),'marina':(14,16),
         'pacific_heights':(14,17),'noe_valley':(14,16),'mission_bay':(15,17),
         'giants_stadium':(13,18),'financial_district':(15,17),
         'north_beach':(14,18),'treasure_island':(14,17)}


def check_streets(plan, cells, frontage, profile):
    design=plan.get('street_design')
    if not design:
        raise ValueError('Authored urban district is missing its street design')
    claimed=set()
    for run in design['frontage_runs']:
        left,right,y=run['left'],run['right'],run['y']
        allowed_y=(7,16,17) if plan['world_id']=='outer_sunset' else (7,16)
        if not 1<=left<=right<=30 or y not in allowed_y:
            raise ValueError('Invalid declared street frontage')
        points={(x,y) for x in range(left,right+1)}
        if points & claimed or not points<=frontage:
            raise ValueError(f"{plan['world_id']}: street wall gap or overlapping runs at {left}..{right},{y}")
        claimed.update(points)
    if len(claimed)<48:
        raise ValueError('Urban street walls cover less than 48 of 60 frontage cells')
    identifier=plan['world_id']
    if identifier in CENTERS:
        a,b=CENTERS[identifier]
        north=set(range(1,31))-set(range(a,b+1))
        up=any(link['direction']=='up' for link in plan['connections'] or [])
        if up:north-=set(range(11,14))
        # The central-door service cards need one narrow planting strip at
        # the west boundary. A north alley can leave one additional strip.
        if identifier in ('dogpatch','treasure_island','mission_bay','financial_district'):
            north.discard(1)
        if up and a==15:north.discard(14)
        down=any(link['direction']=='down' for link in plan['connections'] or [])
        passage=(15,17) if down or identifier=='dogpatch' else {
            'mission':(9,10),'potrero_hill':(11,12),'castro':(21,22),
            'noe_valley':(14,15)}.get(identifier,(15,16))
        expected={(x,7) for x in north}
        expected|={(x,17 if identifier=='outer_sunset' and x<=14 else 16)
                   for x in range(1,31) if not passage[0]<=x<=passage[1]}
        if claimed!=expected:
            raise ValueError('Street wall coverage differs from required district frontage')
    doorway=design['service_doorway']
    entries=[p for p in plan.get('access_points',[]) if p['kind']=='room_entry']
    if identifier in CENTERS and (not doorway or len(entries)!=1):
        raise ValueError('Urban service door is missing its actual room entrance')
    if doorway:
        offsets={'warehouse':3,'clinic':3,'cafe':1}
        style=doorway['style'];spec=profile['cards'][style]
        if style not in offsets or doorway['entry']!=[5,8]:
            raise ValueError('Service doorway changed its shared-world binding')
        block=next((b for b in plan['town_blocks'] if
                    (b['style'],b['x'],b['y'])==(style,doorway['x'],doorway['y'])),None)
        if (not block or doorway['x']+offsets[style]!=5
                or doorway['y']+spec['height']!=8 or cells[5,8][1]):
            raise ValueError('Service trigger does not meet the drawn facade doorway')
        if entries and [entries[0]['x'],entries[0]['y']]!=doorway['entry']:
            raise ValueError('Drawn service doorway differs from the actual room entry')
    for entry in plan.get('access_points',[]):
        if entry['kind']!='gym_entry':continue
        offsets={'cream':2,'highrise':1,'theater':2}
        matches=[b for b in plan['town_blocks'] if b['style'] in offsets
                 and b['x']+offsets[b['style']]==entry['x']
                 and b['y']+b['height']==entry['y']]
        if len(matches)!=1:
            raise ValueError('Gym entry does not meet its drawn facade doorway')
    passage=design['south_passage']
    left,right=passage['left'],passage['right']
    if not 1<=left<=right<=30 or not 2<=right-left+1<=3:
        raise ValueError('Street passage is not a bounded alley')
    down=any(link['direction']=='down' for link in plan['connections'] or [])
    if (passage['purpose']=='connection')!=down:
        raise ValueError('Street passage mislabels an actual map connection')
    if passage['purpose'] not in ('connection','start courtyard','rear residential garden'):
        raise ValueError('Street wall opening has no named destination')
    if any(cells[x,y][1] for x in range(left,right+1) for y in range(16,23)):
        raise ValueError('Street passage is blocked before its destination')
