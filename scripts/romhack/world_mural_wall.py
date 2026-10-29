"""Original attached masonry backing for the Mission community mural."""


def wall():
    """A 64x32 low-detail brick wall using the existing neighborhood palette.

    The horizontal cap spans the entire card; the ends touch neighboring shop
    walls rather than drawing independent posts or a disconnected panel.
    """
    pixels=[]
    for y in range(32):
        for x in range(64):
            if y in (0,1,31):color=1
            elif y in (2,3):color=4
            elif y in (10,18,26):color=2
            elif (x+(4 if (y//8)%2 else 0))%12==0:color=2
            elif (x,y) in ((7,7),(31,15),(49,22),(18,29)):color=4
            else:color=3
            pixels.append(color)
    return bytes(pixels)
