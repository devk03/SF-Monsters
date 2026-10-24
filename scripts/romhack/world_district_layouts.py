"""Authored large-district circulation, in native metatile coordinates.

Each polyline is an actual connected walking/street spine, not a diagram edge
or teleport. Building parcels are fitted around these lanes by the town pass.
The northwest service block keeps existing contributor and save coordinates.
"""

STREETS = {
    'dogpatch': [[(16,12),(84,12),(84,50),(46,50),(46,32),(16,32),(16,12)],
                 [(46,12),(46,50)],[(66,12),(66,50)]],
    'potrero_hill': [[(16,12),(40,12),(40,26),(76,26),(76,46),(24,46)],
                    [(24,46),(24,58),(88,58)],[(56,26),(56,46)]],
    'mission': [[(16,12),(86,12),(86,52),(16,52),(16,32),(86,32)],
                [(38,12),(38,52)],[(62,12),(62,52)]],
    'castro': [[(16,12),(48,12),(48,50),(22,50),(22,32),(82,32)],
               [(48,50),(82,50),(82,20)],[(64,32),(64,12)]],
    'outer_sunset': [[(16,12),(84,12),(84,52),(16,52),(16,12)],
                     [(16,32),(84,32)],[(40,12),(40,52)],[(64,12),(64,52)]],
    'marina': [[(16,12),(84,12),(84,54),(16,54),(16,12)],
               [(36,12),(36,38),(84,38)],[(60,12),(60,38)]],
    'pacific_heights': [[(16,12),(44,12),(44,30),(82,30),(82,54),(20,54)],
                        [(20,54),(20,34),(44,34)],[(62,30),(62,54)]],
    'noe_valley': [[(16,12),(78,12),(78,48),(22,48),(22,32),(78,32)],
                   [(42,12),(42,48)],[(58,32),(58,56)]],
    'mission_bay': [[(16,12),(80,12),(80,52),(40,52),(40,12)],
                    [(40,32),(80,32)],[(60,12),(60,52)],[(80,42),(90,42)]],
    'giants_stadium': [[(16,12),(42,12),(42,50),(84,50),(84,28),(42,28)],
                       [(16,12),(16,50),(42,50)],[(64,50),(64,58)]],
    'financial_district': [[(16,12),(86,12),(86,54),(16,54),(16,12)],
                           [(16,32),(86,32)],[(36,12),(36,54)],[(60,12),(60,54)]],
    'north_beach': [[(16,12),(48,12),(48,32),(82,32),(82,52),(22,52),(22,32),(48,32)],
                    [(66,32),(66,12)],[(48,32),(48,52)]],
    'treasure_island': [[(16,12),(80,12),(80,52),(16,52),(16,12)],
                        [(16,30),(58,30),(58,52)],[(80,30),(90,30)]],
    'golden_gate_park': [[(16,12),(36,18),(48,34),(72,28),(86,42),(66,54),(40,48),(16,32),(16,12)],
                         [(48,34),(40,48)],[(72,28),(78,12)]],
    'twin_peaks': [[(16,12),(38,20),(60,12),(80,24),(62,38),(82,52),(44,54),(26,38),(38,20)],
                   [(26,38),(62,38)]],
    'sutro_tower': [[(16,12),(38,16),(30,32),(54,42),(76,30),(84,48),(54,56),(30,48),(30,32)],
                    [(54,42),(54,20),(70,12)]],
    'lands_end': [[(16,12),(38,18),(48,30),(70,24),(84,38),(72,54),(48,48),(26,56),(16,36),(16,12)],
                  [(48,30),(48,48)]],
    'angel_island': [[(16,12),(38,12),(72,20),(46,30),(80,40),(50,52),(24,44),(38,32),(16,22)],
                     [(24,44),(20,58),(70,58),(80,40)]],
}


PARK_PORTS={
 'golden_gate_park':{'down':[(48,63),(50,58),(42,50)],
                    'up':[(48,0),(52,6),(66,10),(78,12)],
                    'left':[(0,32),(8,30),(16,32)]},
 'twin_peaks':{'up':[(48,0),(52,5),(60,12)],
               'right':[(95,32),(88,34),(80,40),(82,52)],
               'left':[(0,32),(10,34),(18,42),(26,38)]},
 'sutro_tower':{'right':[(95,32),(90,35),(84,48)],
                'left':[(0,32),(10,30),(20,32),(30,32)]},
 'lands_end':{'right':[(95,32),(90,29),(84,38)]},
 'angel_island':{'down':[(48,63),(40,59),(20,58)]},
}


def raster_path(points, radius=1):
    """Connected integer line raster with a walkable native-width corridor."""
    result = set()
    for (x0,y0),(x1,y1) in zip(points,points[1:]):
        count = max(abs(x1-x0),abs(y1-y0))
        for step in range(count+1):
            x = round(x0+(x1-x0)*step/max(1,count))
            y = round(y0+(y1-y0)*step/max(1,count))
            for dy in range(-radius,radius+1):
                for dx in range(-radius,radius+1):
                    result.add((x+dx,y+dy))
    return result


def circulation(identifier, size, directions):
    width,height = size
    if size != (96,64):
        raise ValueError('Authored district circulation currently requires96x64')
    lines = STREETS[identifier]
    cells = set().union(*(raster_path(line) for line in lines))
    if identifier in PARK_PORTS:
        cells|=raster_path([(16,12),(32,12),lines[0][1]])
        for side in directions:cells|=raster_path(PARK_PORTS[identifier][side])
        return {(x,y) for x,y in cells if 0<=x<width and 0<=y<height}
    # Route spurs meet a shared central junction without moving stable services.
    junction = (48,32)
    cells |= raster_path([(16,12),(32,12),(32,32),junction])
    for side in directions:
        edge = {'up':(width//2,0),'down':(width//2,height-1),
                'left':(0,height//2),'right':(width-1,height//2)}[side]
        cells |= raster_path([junction,edge])
    return {(x,y) for x,y in cells if 0<=x<width and 0<=y<height}
