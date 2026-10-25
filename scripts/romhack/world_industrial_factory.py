"""Original native-pixel industrial front using the existing warehouse palette.

A sawtooth north-light roof and wide loading bays distinguish working blocks
from Victorian homes. Dimensions stay112x80; index0 is transparent. This is
code-authored pixel art, with no resized image or extracted game bitmap.
"""


def factory():
    width,height=112,80
    pixels=bytearray(width*height)
    def dot(x,y,c):
        if 0<=x<width and 0<=y<height:pixels[y*width+x]=c
    def box(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):dot(x,y,c)
    # Solid brick shell, stone footing and restrained mortar courses.
    box(4,26,107,75,7)
    for y in (43,59,67):
        for x in range(8,105):dot(x,y,9)
    box(4,28,5,74,8);box(6,29,6,73,10)
    box(106,28,107,75,8)
    box(2,74,109,76,12);box(2,77,109,78,13);box(3,79,108,79,1)
    # Three complete sawtooth bays. Roof planes are flat color clusters; their
    # narrow right faces carry the north-light glazing and dark steel mullions.
    for start in (4,38,72):
        for dx in range(34):
            top=26-dx*18//28 if dx<=28 else 11
            for y in range(top,29):dot(start+dx,y,1 if y<top+2 else 2)
            dot(start+dx,top+2,3)
        box(start+25,16,start+29,25,1)
        box(start+26,17,start+28,24,4)
        box(start+26,17,start+26,19,3)
        box(start+25,21,start+29,21,1)
        box(start+31,12,start+33,28,1)
        box(start+31,12,start+31,26,13)
    box(2,28,109,29,1);box(3,30,108,30,3)
    box(4,31,107,32,8)
    # Repeated clerestory windows read as a working hall rather than home bays.
    for x in (10,44,78):
        box(x-2,35,x+25,45,8)
        box(x,36,x+23,44,1);box(x+1,37,x+22,43,4)
        box(x+2,37,x+4,38,3)
        for mullion in (x+8,x+16):box(mullion,36,mullion,44,1)
        box(x,40,x+23,40,1)
        box(x-1,45,x+24,45,10)
    # A small painted sign uses a legible3x5 native-pixel alphabet.
    box(42,27,70,36,1);box(43,28,69,35,5)
    font={'W':('10001','10001','10101','10101','01010'),
          'O':('111','101','101','101','111'),
          'R':('110','101','110','101','101'),
          'K':('101','110','100','110','101'),
          'S':('111','100','111','001','111')}
    cursor=46
    for letter in 'WORKS':
        for y,row in enumerate(font[letter]):
            for x,v in enumerate(row):
                if v=='1':dot(cursor+x,29+y,1)
        cursor+=len(font[letter][0])+1
    # A steel lintel ties the bays together; brick piers remain visible.
    box(7,47,104,49,1);box(8,47,103,47,3)
    # One closed roller door, with broad quiet slats and a recessed lower edge.
    box(9,50,48,73,8);box(11,50,46,73,1)
    box(13,51,44,72,13)
    for y in range(52,72,4):box(13,y,44,y,12)
    box(13,51,14,71,3);box(13,72,44,73,1)
    # A half-closed loading shutter and cargo block the scenic opening. The
    # separate closed personnel door is not a new service/warp affordance.
    box(54,50,92,73,8);box(56,50,90,73,1)
    box(58,52,88,71,1);box(58,52,88,58,13)
    box(58,53,88,53,12);box(58,57,88,57,12);box(58,59,88,60,1)
    box(60,60,74,72,9);box(61,61,73,71,6)
    box(61,61,73,62,10);box(74,62,76,73,9)
    for step in range(11):dot(62+step,61+step,9)
    box(60,72,76,73,9);box(61,72,74,72,10)
    box(95,50,105,73,8);box(97,51,103,73,1)
    box(98,53,102,71,13);box(98,53,102,58,4)
    box(98,53,98,57,3);dot(102,65,5)
    # Shallow concrete loading thresholds connect physically to the sidewalk.
    box(10,74,47,75,3);box(55,74,91,75,3);box(96,74,104,75,3)
    return width,height,bytes(pixels)


def factory_block():
    """A deep roof/body mass, not stacked miniature facade strips."""
    width,height=112,112
    pixels=bytearray(width*height)
    def box(x0,y0,x1,y1,color):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):pixels[y*width+x]=color
    box(4,7,107,63,1);box(6,9,105,61,2)
    # Quiet zinc roof planes with complete parapet caps and two low vents.
    for y in (10,28,46):
        box(7,y,104,y,3);box(7,y+1,104,y+1,1)
    for x in (26,54,82):box(x,12,x,60,1)
    for x,y in ((19,18),(75,39)):
        box(x+2,y+3,x+15,y+10,1);box(x,y,x+12,y+7,13)
        box(x,y,x+12,y+1,3);box(x+1,y+3,x+11,y+3,1)
    box(3,59,108,62,1);box(4,59,107,59,3)
    # Retain the existing native-pixel clerestory/loading facade at full size.
    _,_,front=factory()
    for y in range(31,80):
        pixels[(y+32)*width:(y+33)*width]=front[y*width:(y+1)*width]
    return width,height,bytes(pixels)


def dock_surfaces():
    """Original timber deck/piling art in the existing warehouse palette."""
    deck=bytes(9 if y%5==4 else 10 if y%5==0 else
               1 if (x,y) in ((2,2),(13,7),(2,12)) else 6
               for y in range(16) for x in range(16))
    rail=bytearray(deck)
    for y in range(16):
        for x in range(16):
            if y in (3,4,5):rail[y*16+x]=9 if y==5 else 10
            if x in (2,3,12,13) and 1<=y<=11:rail[y*16+x]=9
    return deck,bytes(rail)


def deep_walkup():
    """A narrow corner building with a real rear roof plane, native pixels."""
    from world_rich_facades import facade
    w,h,front=facade('walkup')
    pixels=bytearray(w*96)
    for y in range(4,48):
        for x in range(3,w-3):
            pixels[y*w+x]=1 if x in (3,w-4) or y==4 else 3 if y==5 else 2
    for y in (19,35):
        for x in range(5,w-5):pixels[y*w+x]=1
    for y in range(9,15):
        for x in range(31,39):pixels[y*w+x]=3 if y==9 else 13
    pixels[48*w:]=front[16*w:]
    return w,96,bytes(pixels)
