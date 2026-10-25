"""Native Emerald cliff faces and ordinary stairs for SF ridge destinations.

The stairs are the General AF/CF pair used on Route112. They introduce no HM,
warp, encounter or persistent-state requirement. Real route lanes stay open.
"""
from world_district_layouts import raster_path

CHOICES = {'twin_peaks':(0,1), 'sutro_tower':(0,2),
           'lands_end':(0,2), 'angel_island':(1,2)}


def compose(identifier, glades, lanes, protected, clear):
    result=[]
    for index in CHOICES.get(identifier,()):
        cx,cy,rx,ry=glades[index]
        left,right,top=cx-rx,cx+rx,cy+ry+1
        stairs={(x,y) for y in range(cy,top+4) for x in (cx,cx+1)}
        if stairs & protected:
            continue
        foot=(cx,top+3)
        nearest=min(lanes,key=lambda p:(abs(p[0]-foot[0])+abs(p[1]-foot[1]),p[1],p[0]))
        approach=raster_path([foot,nearest],radius=0)
        clear |= stairs|approach
        face={(x,y) for y in (top,top+1) for x in range(left,right+1)}
        clear |= face  # Keep complete tree silhouettes outside the rocky rim.
        # Existing paths form deliberate breaks in a natural ridge. Never
        # convert a mandatory trail or an event standing tile into a wall.
        solid=face-(lanes|protected|stairs|approach)
        result.append(dict(center=[cx,cy],bounds=[left,top,right,top+1],
                           solid=solid,stairs=stairs & face))
    return result


def draw(plan,grid,terraces):
    legend=plan['legend']
    for terrace in terraces:
        left,top,right,_=terrace['bounds']
        for x,y in terrace['solid']:
            tile=((0x68 if x==left else 0x6a if x==right else 0x69)
                  if y==top else (0x78 if x==left else 0x7a if x==right else 0x79))
            char=chr(0x800+tile);legend[char]=[tile,True,3];grid[y][x]=char
        cx=terrace['center'][0]
        for x,y in terrace['stairs']:
            tile=0xaf if x==cx else 0xcf
            char=chr(0x800+tile);legend[char]=[tile,False,3];grid[y][x]=char
    if terraces:
        plan['native_terraces']=[dict(center=t['center'],bounds=t['bounds'],
            stairs=[list(p) for p in sorted(t['stairs'])],solid_cells=len(t['solid'])) for t in terraces]
