"""Original small stone tiles for the ruined coastal bath basins."""


def basin_rim(side, colors):
    """Return an opaque16x16 joined masonry rim in the existing gray palette.

    Horizontal and vertical sides have matching cap and shadow widths; four
    rotated corner pieces finish the perimeter instead of exposing cut ends.
    """
    if side not in ('north','south','west','east','nw','ne','sw','se'):
        raise ValueError('Unknown basin rim side')
    dark,shade,light,stone=colors
    pixels=[]
    for y in range(16):
        for x in range(16):
            # Offset the stone courses so neighboring tiles do not form a
            # continuous harsh grid. Every edge meets its adjoining tile.
            joint=(y in (5,11) or (x+(4 if 6<=y<=11 else 0))%8==0)
            value=shade if joint else stone
            if y==0:value=light
            if y>=14:value=dark if y==15 else shade
            if side in ('west','nw','sw') and x<2:value=dark if x==0 else shade
            if side in ('east','ne','se') and x>=14:value=dark if x==15 else shade
            if side in ('south','sw','se') and y==0:value=shade
            # Sparse broken-stone flecks, identical at matching boundaries.
            if (x,y) in ((3,3),(12,8),(5,13)):value=light
            pixels.append(value)
    return bytes(pixels)
