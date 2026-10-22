"""Original native SF fronts: flat walkups, shop awnings and industrial lofts."""
import struct


def paint_palette(original, scheme):
    colors=list(struct.unpack('<16H',original))
    paints={
        'sage':{5:(29,28,24),6:(18,19,16),7:(18,23,17),8:(10,15,11),
                9:(14,18,14),10:(25,28,23),11:(15,20,22)},
        'slate':{5:(28,28,27),6:(17,18,20),7:(17,21,25),8:(9,12,17),
                 9:(13,17,22),10:(23,25,28),11:(20,22,19)},
    }
    for i,rgb in paints[scheme].items():colors[i]=sum(v<<(c*5) for c,v in enumerate(rgb))
    return struct.pack('<16H',*colors)


# Forms describe architecture, never a paint name. Repeated window/cornice
# modules align to native 8px boundaries so eight forms fit a GBA street kit.
FORMS = ('walkup', 'shophouse', 'workshop', 'gable', 'deco',
         'flats', 'arcade', 'duplex')


def fronts(profile):
    if profile in ('residential', 'nature'):
        return []
    result=[]
    for name in FORMS:
        width=32 if name in ('shophouse','flats') else 48
        height=64;p=bytearray(width*height)
        def box(x0,y0,x1,y1,c):
            for y in range(max(0,y0),min(height,y1+1)):
                for x in range(max(0,x0),min(width,x1+1)):p[y*width+x]=c
        def window(x,y,w=8,h=10):
            box(x-1,y-1,x+w,y+h,6);box(x,y,x+w-1,y+h-1,1)
            box(x+1,y+1,x+w-2,y+h-2,4)
            box(x+2,y+1,x+2,y+3,3)
            box(x,y+5,x+w-1,y+5,2)
            box(x-1,y+h,x+w,y+h,5)
            box(x-1,y-1,x+w,y-1,5);box(x-1,y,x-1,y+h-1,3)
        def door(x):
            box(x-1,47,x+8,61,6);box(x,48,x+7,60,1)
            box(x+1,49,x+6,53,4);box(x+1,56,x+6,59,8)
            box(x-2,62,x+9,62,12);box(x+5,55,x+5,55,5)
            box(x-2,45,x+9,46,5);box(x+8,48,x+9,61,2)
        wall=10 if name in ('workshop','deco','arcade') else 7
        box(1,5,width-2,61,wall)
        box(0,5,0,61,1);box(width-1,5,width-1,61,1)
        box(1,5,2,61,6);box(width-3,5,width-2,61,6)
        box(0,3,width-1,5,1);box(1,3,width-2,3,5)
        box(3,6,width-4,8,6);box(3,6,width-4,6,3)
        box(3,9,3,57,5);box(width-4,9,width-4,57,8)
        box(2,0,width-3,2,2);box(4,0,width-5,0,3)
        box(1,58,width-2,61,13);box(1,58,width-2,58,3)
        box(0,62,width-1,63,1);box(1,62,width-2,62,12)
        if name=='workshop':
            # Steel loft windows and a wide loading shutter.
            for x in (4,20,36):window(x,12,8,14)
            box(3,29,width-4,31,6)
            box(4,39,27,60,1);box(5,40,26,59,2)
            for y in range(42,60,4):box(5,y,26,y,13)
            door(36);box(6,0,14,2,1);box(7,0,13,1,3)
        elif name=='gable':
            # A visible pitched roof and attic distinguish the cottage.
            box(0,0,width-1,15,0)
            for y in range(2,16):
                half=min(23,(y-2)*2)
                box(23-half,y,24+half,y,2)
                box(23-half,y,24-half,y,1)
                box(23+half,y,24+half,y,1)
            box(0,15,width-1,16,5);window(20,7,8,7)
            for y in (20,24,40,44):box(4,y,width-5,y,6)
            for x in (4,20,36):window(x,28)
            window(4,48);door(36)
        elif name=='deco':
            # Stepped parapet, three vertical ribs, tall recessed windows.
            box(16,0,31,3,6);box(20,0,27,1,5)
            for x in (4,20,36):
                window(x,12,8,24);box(x-2,8,x-2,40,5)
            box(3,41,width-4,44,6);door(20)
        elif name=='arcade':
            # Three shallow arches over a shop gallery, sign band above.
            for x in (4,20,36):window(x,12)
            box(3,28,width-4,33,1);box(4,29,width-5,32,5)
            for x in (9,13,18,23,27,32,36):box(x,30,x+1,31,6)
            for x in (4,20,36):
                window(x,44,8,14)
                box(x-1,41,x+8,43,6);box(x+1,39,x+6,40,6)
                box(x+1,42,x+6,43,4)
            door(20)
        elif name=='duplex':
            # Paired entries, central party wall and two symmetric flats.
            for x in (4,36):
                box(x-2,10,x+10,40,6);box(x-2,10,x+9,10,5)
                box(x-2,11,x-1,38,5);box(x+9,11,x+10,39,8)
                window(x,12);window(x,28);door(x)
                box(x-3,40,x+11,41,5)
            box(22,6,25,61,6);box(23,7,24,57,5)
        else:
            for y in (12,28):
                for x in range(4,width-4,16):window(x,y)
            if name=='shophouse':
                box(1,40,width-2,43,1)
                for x in range(2,width-2):
                    box(x,41,x,46,5 if x//4%2 else 7)
                window(4,49,8,10);door(20)
            elif name=='flats':
                # Recessed porch and a wide stone belt, no shop awning.
                box(2,40,width-3,42,6);window(4,48);door(20)
                box(17,44,29,46,5);box(17,47,17,61,6)
            else:
                # Brick walkup: sash rows and the external fire escape.
                box(2,40,width-3,42,6);window(4,48);door(36)
                for y in (10,26,44):
                    for x in (13,29):box(x,y,x+2,y,6)
                for y in (23,39):
                    box(17,y,31,y,1);box(17,y-2,17,y,1)
                    box(31,y-2,31,y,1)
                for y in range(24,39):p[y*width+23+(y%4)//2]=2
        result.append((name,width,height,bytes(p)))
    return result
