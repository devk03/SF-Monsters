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


def fronts(profile):
    names={'industrial':('workshop',),'civic':('walkup',),
           'culture':('shophouse','walkup'),'stadium':('shophouse','walkup'),
           'mixed_use':('walkup','shophouse','workshop')}.get(profile,())
    result=[]
    for name in names:
        width=32 if name=='shophouse' else 48
        height=64;p=bytearray(width*height)
        def box(x0,y0,x1,y1,c):
            for y in range(y0,y1+1):
                for x in range(x0,x1+1):p[y*width+x]=c
        def window(x,y,w=8,h=11):
            box(x-1,y-1,x+w,y+h,6);box(x,y,x+w-1,y+h-1,1)
            box(x+1,y+1,x+w-2,y+h-2,4)
            box(x+2,y+1,x+2,y+3,3)
            box(x,y+5,x+w-1,y+5,2)
            box(x-1,y+h,x+w,y+h,5)
        # A continuous outside pier finishes either exposed end. Shared trim,
        # glass and roof shades keep the new forms in the existing street kit.
        wall=9 if name=='walkup' else 10 if name=='shophouse' else 10
        box(1,5,width-2,59,wall);box(0,5,0,61,1);box(width-1,5,width-1,61,1)
        box(1,5,2,58,6);box(width-3,5,width-2,58,6)
        box(0,3,width-1,5,1);box(1,3,width-2,3,5)
        box(2,0,width-3,2,2);box(4,0,width-5,0,3)
        box(1,58,width-2,61,13);box(1,58,width-2,58,3)
        box(0,62,width-1,63,1);box(1,62,width-2,62,12)
        if name=='walkup':
            # Brick Edwardian: three narrow windows, horizontal stone lintels
            # and an external fire stair rather than a Victorian bay.
            for y in (8,25):
                for x in (6,20,34):window(x,y,7,11)
            for y in (22,39):box(2,y,width-3,y,6)
            window(7,44,12,12)
            box(30,43,40,60,6);box(32,45,38,60,1)
            box(33,46,37,51,4);box(33,54,37,58,8)
            box(27,60,43,61,3);box(25,62,45,62,12)
            for y in range(16,41,8):
                box(18,y,30,y,1);box(18,y-2,18,y,1);box(30,y-2,30,y,1)
            for y in range(18,38):p[y*width+23+(y%4)//2]=2
        elif name=='shophouse':
            # Two upper sash windows over a recessed shop and striped awning.
            for y in (9,25):
                for x in (5,19):window(x,y,7,10)
            box(2,39,width-3,42,1);box(3,40,width-4,41,5)
            for x in range(1,width-1):
                color=7 if (x//4)%2 else 5
                box(x,43,x,46,color)
                if (x//4)%2:box(x,47,x,48,8)
            box(3,49,20,59,1);box(4,50,19,57,4);box(11,50,11,58,2)
            box(23,49,28,61,1);box(24,50,27,54,4);box(24,56,27,60,8)
        else:
            # Loft/workshop: broad steel grids, loading door, roof ventilator.
            box(6,0,14,2,1);box(7,0,13,1,3)
            for x in (6,26):
                window(x,11,15,16)
                box(x+7,11,x+7,26,2);box(x,21,x+14,21,2)
            box(2,32,width-3,34,1);box(2,32,width-3,32,3)
            box(5,39,30,60,1);box(6,40,29,59,2)
            for y in range(42,60,4):box(6,y,29,y,13)
            box(35,40,42,60,1);box(36,41,41,48,4)
            box(36,51,41,59,8)
        result.append((name,width,height,bytes(p)))
    return result
