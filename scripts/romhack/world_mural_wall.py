"""Original attached masonry backing for the Mission community mural."""


def wall():
    """A 64x32 low-detail brick wall using the existing neighborhood palette.

    The horizontal cap spans the entire card; the ends touch neighboring shop
    walls rather than drawing independent posts or a disconnected panel.
    """
    pixels=[]
    for y in range(32):
        for x in range(64):
            # A shallow capped parapet is legible at actual GBA scale and
            # meets the neighboring rooflines without detached end posts.
            if y in (0,6,31):color=1
            elif y in (1,2):color=9
            elif y==3:color=2
            elif y==4:color=4
            elif y==5:color=2
            elif x in (0,63):color=2
            elif y in (10,18,26):color=2
            elif (x+(4 if (y//8)%2 else 0))%12==0:color=2
            elif (x,y) in ((7,7),(31,15),(49,22),(18,29)):color=4
            else:color=3
            pixels.append(color)
    return bytes(pixels)
