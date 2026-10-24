"""Whole-district shore masks; piers preserve the declared route approaches."""


def shoreline(identifier,width,height,lanes):
    def water(x,y):
        if identifier=='lands_end':return x<6+(y//9)%3
        if identifier=='angel_island':return x<5+(y//11)%2 or x>=width-5-(y//13)%2
        if identifier=='outer_sunset':
            return (y>=24 and x<7+(y//12)%2) or (9<=y<=16 and x<4)
        if identifier=='treasure_island':
            return (x<6 or x>=width-6 or y<5 or y>=height-6) and not(x<32 and y<24)
        return False
    sea={(x,y) for y in range(height) for x in range(width) if water(x,y)}-lanes
    wall={(x+dx,y+dy) for x,y in sea for dx,dy in ((-1,0),(1,0),(0,-1),(0,1))
          if 0<x+dx<width-1 and 0<y+dy<height-1 and (x+dx,y+dy) not in sea|lanes}
    # Existing northwest service buildings retain their entry contracts.
    # Lands End/Angel Island already have authored western shores there.
    if identifier in ('treasure_island','outer_sunset'):
        wall={p for p in wall if not(p[0]<32 and p[1]<24)}
    return sea,wall
