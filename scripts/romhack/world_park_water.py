"""Original park pond geometry referencing the user's native General terrain.

Collision is solid at ordinary land elevation. Native Surf interaction requires
an elevation mismatch, so this scenery is separate from the real bay routes.
"""
ORIGIN=(66,35)
POND=(
 (0xb0,0xb1,0xb1,0xb2,None,None,None,None),
 (0xb8,0xa1,0xa1,0xba,None,None,None,None),
 (0xb8,0xa1,0xa1,0xc2,0xb1,0xb1,0xb1,0xb2),
 (0xb8,0xa1,0xa1,0xa1,0xa1,0xa1,0xa1,0xba),
 (0xb8,0xa1,0xa1,0xa1,0xa1,0xa1,0xa1,0xba),
 (0xb8,0xa1,0xa1,0xa1,0xa1,0xa1,0xa1,0xba),
 (2,2,2,2,2,2,2,2),
)


def pond_cells(identifier):
    if identifier!='golden_gate_park':return set()
    ox,oy=ORIGIN
    return {(ox+x,oy+y) for y,row in enumerate(POND) for x,n in enumerate(row) if n is not None}


def draw_pond(plan,grid):
    if plan['world_id']!='golden_gate_park':return
    ox,oy=ORIGIN;water=[];bank=[]
    for y,row in enumerate(POND):
        for x,n in enumerate(row):
            if n is None:continue
            char=chr(0x800+n)
            plan['legend'][char]=[n,n!=2,3]
            grid[oy+y][ox+x]=char
            (bank if n==2 else water).append([ox+x,oy+y])
    plan['scenic_pond']={'origin':list(ORIGIN),'water':water,'south_bank':bank,
                         'solid_land_elevation':3,'native_terrain':True}
