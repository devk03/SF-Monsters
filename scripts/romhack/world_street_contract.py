"""Independent street-wall and drawn-door checks; no map producer imports."""


def check_streets(plan, cells, frontage, profile):
    design=plan.get('street_design')
    if not design:return
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
    doorway=design['service_doorway']
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
