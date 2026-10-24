"""Small native worn-grass patches, with complete original terrain edges."""
WORN=((0x1d0,0x1d1,0x1d2),(0x1d8,0x1d9,0x1da),(0x1e0,0x1e1,0x1e2))
WORN_IDS={n for row in WORN for n in row}


def worn_patch(grid,legend,grass,target,excluded=()):
    """A bounded softened trail patch; never replace trees, props or flowers."""
    for n in WORN_IDS:legend[chr(0x800+n)]=[n,False,3]
    width,height=len(grid[0]),len(grid)
    candidates=sorted(((x,y) for y in range(2,height-4) for x in range(2,width-4)),
                      key=lambda p:(abs(p[0]+2-target[0])+abs(p[1]+1-target[1]),p[1],p[0]))
    excluded=set(excluded)
    for x,y in candidates:
        cells={(x+dx,y+dy) for dy in range(3) for dx in range(5)}
        if cells & excluded or any(grid[yy][xx]!=grass for xx,yy in cells):continue
        for dy in range(3):
            for dx in range(5):
                tile=WORN[dy][0 if dx==0 else 2 if dx==4 else 1]
                grid[y+dy][x+dx]=chr(0x800+tile)
        return [x,y,5,3]
    return None
