"""Shared native pixel modules for coherent attached SF frontage candidates.

The existing composer is unchanged until allocation and pixel review accept
this candidate. Attachment changes actual party-wall pixels, never just labels.
"""
from world_architecture import FORMS


def facade(name, closed=('left','right')):
    width=32 if name in ('shophouse','flats') else 48
    height=64
    pixels=bytearray(width*height)
    wall=10 if name in ('workshop','deco','arcade') else 7
    def box(x0,y0,x1,y1,color):
        for y in range(max(0,y0),min(height,y1+1)):
            for x in range(max(0,x0),min(width,x1+1)):pixels[y*width+x]=color
    def window(left,top,*,tall=False,arch=False):
        bottom=top+(23 if tall else 11)
        # Recessed sash, lit outer frame and a shadowed right reveal. These
        # shared pixel modules give every form the same level of detail.
        box(left-1,top-1,left+10,bottom+1,6)
        box(left,top,left+9,bottom,1)
        box(left+1,top+1,left+8,bottom-1,4)
        box(left+2,top+1,left+2,top+3,3)
        box(left,top+5,left+9,top+5,2)
        box(left-1,top-1,left+10,top-1,5)
        box(left-1,top,left-1,bottom,5)
        box(left+9,top+1,left+9,bottom,8)
        box(left-1,bottom+1,left+10,bottom+1,5)
        if arch:
            box(left,top,left,top+2,wall);box(left+9,top,left+9,top+2,wall)
            box(left+1,top,left+8,top,5)
    def door(left):
        box(left-1,47,left+10,61,6)
        box(left,48,left+9,61,1);box(left+1,49,left+8,60,8)
        box(left+2,49,left+7,54,4);box(left+7,56,left+7,56,5)
        box(left+2,57,left+5,59,2)
        box(left+1,49,left+1,60,5)
        box(left-1,47,left+10,47,5);box(left-1,62,left+10,62,12)
    box(0,12,width-1,61,wall)
    # A real roof plane and layered projecting cornice replace the thin flat
    # roof stripe. The same modules join continuously across party walls.
    box(0,1,width-1,11,2);box(0,1,width-1,1,1)
    box(1,2,width-2,2,3);box(1,9,width-2,9,6)
    box(0,10,width-1,10,1);box(0,11,width-1,12,5)
    box(0,13,width-1,14,6);box(0,15,width-1,15,8)
    box(4,2,11,6,1);box(5,2,10,4,6);box(5,2,10,2,3)
    box(0,30,width-1,31,6);box(0,30,width-1,30,5)
    box(0,45,width-1,46,6)
    box(0,60,width-1,61,13);box(0,62,width-1,63,1)
    columns=range(3,width,16)
    if name=='gable':
        box(0,0,width-1,15,0)
        for y in range(1,16):
            half=min(width//2-1,y*2)
            box(width//2-half,y,width//2+half-1,y,2)
            box(width//2-half,y,width//2-half,y,1)
        box(0,15,width-1,16,5)
        for x in columns:window(x,19)
        window(19,35);door(35)
    elif name=='deco':
        box(16,0,31,3,6);box(20,0,27,1,5)
        for x in columns:
            window(x,13,tall=True);box(x-2,9,x-2,43,5)
        door(19)
    elif name=='workshop':
        for x in columns:window(x,16)
        box(3,34,28,59,1);box(4,35,27,59,2)
        for y in range(38,60,4):box(4,y,27,y,13)
        door(35)
    elif name=='arcade':
        for x in columns:window(x,16)
        box(0,32,width-1,36,1);box(1,33,width-2,35,5)
        for x in columns:window(x,48,arch=True)
    elif name=='shophouse':
        for x in columns:window(x,16)
        box(0,33,width-1,37,6);box(0,33,width-1,33,5)
        for x in range(0,width,8):box(x,34,x+3,37,10)
        box(0,38,width-1,38,2)
        window(3,48);door(19)
    elif name=='duplex':
        for x in columns:window(x,16)
        for x in columns:window(x,33)
        door(3);door(35)
        box(23,9,24,61,6)
    elif name=='flats':
        for x in columns:window(x,13,tall=True)
        box(0,39,width-1,41,5);window(3,48);door(19)
    else:
        for x in columns:window(x,16)
        for x in columns:window(x,33)
        window(3,48);window(19,48);door(35)
    # A shared wall loses its exposed outer pier. Roof/cornice and foundation
    # remain continuous; isolated buildings keep finished caps on both sides.
    for side in closed:
        x=0 if side=='left' else width-1
        box(x,8,x,61,1)
        inner=1 if side=='left' else width-2
        box(inner,9,inner,59,5 if side=='left' else 6)
    return width,height,bytes(pixels)


def fronts(profile, *, variants=False):
    if profile in ('residential','nature'):return []
    result=[]
    for name in FORMS:
        width,height,pixels=facade(name)
        result.append((name,width,height,pixels))
        if variants:
            for suffix,closed in [('l',('left',)),('m',()),('r',('right',))]:
                width,height,pixels=facade(name,closed)
                result.append((name+'_'+suffix,width,height,pixels))
    return result
