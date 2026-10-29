"""Original small stone tiles for the ruined coastal bath basins."""


def basin_rim(side, colors, weathered=False):
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
            if weathered and (x,y) in ((3,6),(4,7),(4,8),(11,3),(12,4),(11,12)):
                value=dark
            pixels.append(value)
    return bytes(pixels)


def promenade(colors):
    """A restrained, neutral stone surface without a repeating square grid."""
    dark,shade,light,stone=colors
    flecks={(4,7),(23,3),(15,19),(27,26),(2,29)}
    return bytes(shade if (x,y) in flecks else stone
                 for y in range(32) for x in range(32))
