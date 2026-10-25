"""Small original pixel motifs for planted SF sidewalks; no resampled artwork."""
import struct


def palette(original):
    colors=list(struct.unpack('<16H',original))
    for index,rgb in enumerate(((5,10,5),(9,15,7),(15,21,11),(28,14,11),
                                (22,16,24),(29,24,11),(13,10,8)),9):
        colors[index]=sum(v<<(c*5) for c,v in enumerate(rgb))
    return struct.pack('<16H',*colors)


def cards():
    result=[]
    for kind in ('succulent','tuft','shrub','flower_box','lavender','daisies','shop_board','wayfinder'):
        height=32 if kind=='wayfinder' else 16
        p=bytearray(16*height)
        def dot(x,y,c):
            if 0<=x<16 and 0<=y<height:p[y*16+x]=c
        def box(x0,y0,x1,y1,c):
            for y in range(y0,y1+1):
                for x in range(x0,x1+1):dot(x,y,c)
        def line(x0,y0,x1,y1,c):
            n=max(abs(x1-x0),abs(y1-y0),1)
            for i in range(n+1):dot(round(x0+(x1-x0)*i/n),round(y0+(y1-y0)*i/n),c)
        if kind in ('wayfinder','shop_board'):
            if kind=='wayfinder':
                box(7,3,8,29,6);box(6,29,10,30,5)
                box(1,3,14,8,9);box(2,4,13,7,10)
                line(3,5,10,5,1);line(9,4,11,5,1);line(9,6,11,5,1)
                box(2,10,13,15,9);box(3,11,12,14,10)
                line(5,12,11,12,1);line(5,11,3,12,1);line(5,13,3,12,1)
            else:
                line(3,2,1,14,6);line(12,2,14,14,6)
                box(3,2,12,12,6);box(4,3,11,11,7)
                box(5,5,9,8,1);dot(10,5,1);dot(10,7,1)
                line(5,10,10,10,3)
        else:
            box(2,12,13,14,5);box(2,11,13,11,8)
            box(3,12,12,13,4);box(4,10,11,10,15)
            if kind=='succulent':
                for x,y in ((3,6),(5,3),(8,1),(11,3),(13,6),(12,9),(4,9)):
                    line(8,10,x,y,9);line(8,9,x,y,10)
                line(8,9,8,3,11);line(8,9,12,6,11)
            elif kind=='shrub':
                for y in range(3,11):
                    for x in range(2,14):
                        if ((x-7.5)/6)**2+((y-7)/4.5)**2<=1:
                            dot(x,y,9 if y>8 else 11 if (x+y)%7==0 else 10)
            elif kind=='flower_box':
                box(2,7,13,10,9)
                for x,y,c in ((3,5,12),(7,6,14),(11,4,12)):
                    line(x,y+1,x,9,10)
                    for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):dot(x+dx,y+dy,c)
                    dot(x,y,1)
            elif kind=='tuft':
                for x,y in ((2,4),(5,2),(8,1),(11,2),(14,5)):
                    line(8,10,x,y,9);line(8,9,x,y,11 if x<8 else 10)
            else:
                for x,y in ((4,5),(8,2),(12,4)):
                    line(x,10,x,y,10);line(x,8,x-2,6,11)
                    color=13 if kind=='lavender' else 1
                    if kind=='lavender':
                        box(x-1,y,x+1,y+2,color);dot(x,y-1,13)
                    else:
                        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):dot(x+dx,y+dy,color)
                        dot(x,y,14)
        result.append((kind,16,height,bytes(p)))
    return result


# Distinct combinations and planting rhythms, not a claim that each species is
# exclusive to one real neighborhood. Quiet ground remains the walking surface.
PLANTINGS={
 'presidio':('shrub','lavender','tuft'),
    'dogpatch':('succulent','tuft','shrub'),
    'potrero_hill':('lavender','succulent','daisies'),
    'mission':('flower_box','succulent','tuft'),
    'castro':('flower_box','lavender','daisies'),
    'outer_sunset':('tuft','succulent','daisies'),
    'marina':('shrub','flower_box','tuft'),
    'pacific_heights':('shrub','lavender','flower_box'),
    'noe_valley':('daisies','lavender','shrub'),
    'mission_bay':('tuft','shrub','lavender'),
    'giants_stadium':('flower_box','tuft','succulent'),
    'financial_district':('shrub','tuft','succulent'),
    'north_beach':('lavender','flower_box','shrub'),
    'treasure_island':('tuft','daisies','succulent'),
}
