"""Authored district parcels interrupt the generic frontage bands with local use."""
RECTS={'dogpatch':(50,17,62,30),'mission':(42,17,58,28)}


def reserved_cells(identifier):
    if identifier not in RECTS:return set()
    left,top,right,bottom=RECTS[identifier]
    return {(x,y) for y in range(top,bottom+1) for x in range(left,right+1)}


def furnish_parcel(plan,grid,cards,stamp,token):
    identifier=plan['world_id']
    if identifier not in RECTS:return
    cells=reserved_cells(identifier)
    for x,y in cells:grid[y][x]=token('slab_walk' if identifier=='dogpatch' else 'brick_walk',x,y)
    def put(style,x,y,shoulder=False):
        if not stamp(style,x,y,shoulder=shoulder,parcel=True):
            raise ValueError(identifier+': authored parcel cannot place '+style+' at '+str((x,y)))
    if identifier=='dogpatch':
        # Workshops share walls; the open east side is a genuine two-tile entry.
        for x in (50,53,56):put('workshop',x,17)
        put('shophouse',59,17);put('flats',61,17)
        for x in (50,53,56):put('workshop',x,25)
        for y in (23,24):
            for x in range(50,63):grid[y][x]=token('dark_walk',x,y)
        put('recycling',61,23);put('shop_board',61,25)
        notice=dict(style='parcel_notice',object=[61,25],standing=[61,26],
            text='Workshop court. Deliveries use the side passage. Please leave enough room for an actual bicycle, not just the idea of one.')
        plan['parcel_resident_anchor']=[60,27]
        title='Workshop and loading court'
    else:
        # A shorter mural wall makes a real break in the roofline. Tall neighbors
        # receive finished exposed caps through the normal attachment pass.
        for style,x,y in [('shophouse',42,17),('arcade',44,17),('mural',47,19),
                          ('walkup',51,17),('duplex',54,17),
                          ('arcade__sage',42,25),('duplex__slate',45,25),
                          ('walkup__slate',48,25),('shophouse__slate',51,25),
                          ('workshop__slate',53,25),('gable__slate',56,25)]:put(style,x,y)
        put('street_tree',41,23,True);put('lamp',58,19,True)
        put('flower_box',44,23);put('bench',48,23);put('flower_box',54,23)
        notice=dict(style='parcel_notice',object=[48,20],standing=[48,21],
            text='Community wall. Ask at the studio before adding paint. The bench is for sitting, not storing your entire project.')
        plan['parcel_resident_anchor']=[52,23]
        title='Mural and community court'
    label='WBParcel_'+identifier
    notice['script']=label
    plan.setdefault('extra_street_signs',[]).append(notice)
    plan['parcel_notices']=[notice]
    x,y=notice['object'];sx,sy=notice['standing']
    plan.setdefault('bg_events',[]).append(dict(type='sign',x=x,y=y,elevation=0,
        player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=label))
    plan['access_points'].append(dict(kind='checkpoint',name='parcel_notice',activation='interact',x=sx,y=sy))
    plan.setdefault('scenic_viewpoints',[]).append(dict(name=title,x=sx,y=sy))
    plan['authored_parcel']={'name':title,'bounds':list(RECTS[identifier]),'resident_index':0}
