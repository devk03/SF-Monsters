"""Finish native canopy masses with their real lower trunk/grass edge."""
TOP=(0x1d4,0x1d5)
BASE=(0x1e4,0x1e5)


def finish_forest(grid,legend,protected,ground):
    """Overlapping tree rows hide bases; exposed fronts must retain them.

Remove a canopy pair if its real base would block an authored path. Work from
south to north so an exposed row above a removed pair can finish naturally.
"""
    width,height=len(grid[0]),len(grid)
    top=tuple(chr(0x800+n) for n in TOP)
    for n in BASE:legend[chr(0x800+n)]=[n,True,3]
    for y in range(height-4,-1,-2):
        for x in range(0,width-1,2):
            if tuple(grid[y][x:x+2])!=top:continue
            if tuple(grid[y+2][x:x+2])==top:continue
            cells={(x,y+2),(x+1,y+2)}
            if cells & protected or any(grid[yy][xx]!=ground for xx,yy in cells):
                for dy in (0,1):
                    for dx in (0,1):grid[y+dy][x+dx]=ground
            else:
                for dx,n in enumerate(BASE):grid[y+2][x+dx]=chr(0x800+n)
