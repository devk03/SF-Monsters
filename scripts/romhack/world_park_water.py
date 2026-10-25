"""Original park pond geometry referencing the user's native General terrain.

Collision is solid at ordinary land elevation. Native Surf interaction requires
an elevation mismatch, so this scenery is separate from the real bay routes.
"""
ORIGIN=(58,35)
# General's low shoreline family supplies all four joined banks, including
# the southern corners. The former pond ended abruptly against a grass row.
POND=(
 (0xc8,)+(0xc9,)*16+(0xca,),
 *((0xd0,)+(0xa1,)*16+(0xd2,) for _ in range(7)),
 (0xd8,)+(0xd9,)*16+(0xda,),
 (2,)*18,
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
