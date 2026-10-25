"""District destinations whose land use must survive residential packing.

These are small playable public spaces, not contributor gym or mission content.
Reservations precede housing and court placement; every visible prop must fit.
"""
RECTS={
    'dogpatch':(20,37,42,47),
    'treasure_island':(62,35,75,48),
    'giants_stadium':(52,33,80,46),
    'financial_district':(40,17,56,28),
    'mission_bay':(64,17,76,28),
    'mission':(66,37,82,48),
}
EXTRA_RECTS={'dogpatch':((3,24,13,28),(3,37,13,43))}


def reserved_cells(identifier):
    if identifier not in RECTS:return set()
    return {(x,y) for left,top,right,bottom in (RECTS[identifier],*EXTRA_RECTS.get(identifier,()))
            for y in range(top,bottom+1) for x in range(left,right+1)}


def furnish(plan,grid,cards,stamp,token,lanes):
    identifier=plan['world_id']
    if identifier not in RECTS:return
    left,top,right,bottom=RECTS[identifier]
    def put(style,x,y):
        if not stamp(style,x,y,shoulder=True,parcel=True):
            raise ValueError(identifier+': concept place cannot fit '+style+' at '+str((x,y)))
    def paint(style,x0,y0,x1,y1):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                if (x,y) not in lanes:grid[y][x]=token(style,x,y)
    if identifier=='dogpatch':
        for a,b,c,d in EXTRA_RECTS[identifier]:paint('slab_walk',a,b,c,d)
        put('warehouse',4,24);put('warehouse',4,37)
        paint('slab_walk',left,top,right,bottom)
        put('warehouse',20,37);put('warehouse',30,37);put('crane',38,36)
        paint('dark_walk',20,44,42,44)
        put('bench',20,45);put('recycling',27,45);put('rack',35,45)
        title='Working warehouse yard';point=(26,43)
        obj=(40,45);standing=(40,46)
        note='Working yard. Deliveries use the marked lane. The little repair shops are across the street; this is where the large broken things go.'
    elif identifier=='treasure_island':
        paint('slab_walk',left,top,right,bottom)
        put('warehouse',63,35);put('warehouse',68,43);put('crane',71,35)
        paint('dark_walk',62,41,75,42)
        put('recycling',63,44);put('bench',63,46)
        title='Island ferry workshop yard';point=(70,41)
        obj=(65,44);standing=(65,45)
        note='Island workshop yard. The ferry path is east. Please leave the loading lane open, even if you are only stopping for a minute.'
    elif identifier=='giants_stadium':
        paint('grass',left,top,right,bottom)
        # A walkable infield gives the ballpark a real footprint, rather than
        # representing the entire stadium with one small decorative gate.
        # General124 is native sand with ordinary footprint behavior21; it is
        # collision-free land, not an encounter or a progression trigger.
        sand=chr(0x800+0x124);plan['legend'][sand]=[0x124,False,3]
        for y in range(35,45):
            for x in range(58,75):
                if abs(x-66)+abs(y-40)<=6:grid[y][x]=sand
        paint('brick_walk',left,45,right,46)
        for x in (54,58,62,72,76):put('bench',x,33)
        for x in (54,78):put('street_tree',x,39)
        put('lamp',52,43);put('lamp',80,43)
        title='Ballpark field and fan walk';point=(66,44)
        note='A neighborhood practice field. The next argument about the lineup starts on the bench. Please keep the path clear.'
        obj=(76,44);standing=(76,45)
    elif identifier in ('financial_district','mission_bay'):
        paint('stone_walk',left,top,right,bottom)
        towers=(40,44,50,54) if identifier=='financial_district' else (64,68,72)
        height=8 if identifier=='financial_district' else 5
        for index,x in enumerate(towers):
            style=('highrise_tall' if index in (0,2) else 'highrise_medium') if height==8 else 'highrise'
            put(style,x,top+height-len(cards[style]['tiles']))
        paint('slab_walk',left,top+height,right,top+height+1)
        for x in (left,right-1):put('street_tree',x,top+height+2)
        put('bench',left+5,top+height+2)
        put('flower_box',left+(8 if identifier=='mission_bay' else 11),top+height+2)
        title='Office canyon lunch court' if identifier=='financial_district' else 'Research campus court'
        point=(left+6,top+height+1);obj=(left+12,top+height+2);standing=(left+12,top+height+3)
        if identifier=='mission_bay':obj=(73,25);standing=(73,26)
        note=('Public lunch court. You can eat here even if you do not work in any of these buildings.'
              if identifier=='financial_district' else
              'Research campus court. A good place to sit between appointments. Please leave the bicycle entrance clear.')
    else:
        paint('grass',left,top,right,bottom)
        paint('brick_walk',left,42,right,43)
        paint('brick_walk',73,top,74,bottom)
        for x in (67,70,77,80):
            for y in (38,40,45,47):put('flower_box' if y%2 else 'shrub',x,y)
        put('street_tree',71,44);put('bench',76,44)
        title='Community garden crossing';point=(74,43)
        obj=(79,44);standing=(79,45)
        note='Neighbors share this garden. The gate stays open. Please ask before picking anything; someone has been waiting for those tomatoes.'
    put('shop_board',*obj)
    label='WBPlace_'+identifier
    plan.setdefault('extra_street_signs',[]).append(dict(script=label,text=note))
    plan.setdefault('bg_events',[]).append(dict(type='sign',x=obj[0],y=obj[1],elevation=0,
        player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=label))
    plan['access_points'].append(dict(kind='checkpoint',name='concept_place',activation='interact',x=standing[0],y=standing[1]))
    plan.setdefault('scenic_viewpoints',[]).append(dict(name=title,x=point[0],y=point[1]))
    plan['concept_place']=dict(name=title,bounds=list(RECTS[identifier]),notice=label)
    if identifier in EXTRA_RECTS:
        plan['concept_place']['secondary_bounds']=[list(r) for r in EXTRA_RECTS[identifier]]
