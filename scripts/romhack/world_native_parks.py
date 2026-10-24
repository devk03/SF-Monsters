"""Native forest masses around authored park circulation and stable landmarks."""
from world_green_routes import TREES
from world_district_layouts import raster_path

# Each reserve has a different sequence of enclosed meadow destinations.
GLADES={
 'golden_gate_park':((44,20,6,4),(66,40,7,5),(32,49,5,4)),
 'twin_peaks':((45,18,4,3),(65,35,5,3),(38,48,4,3)),
 'sutro_tower':((40,18,4,4),(68,43,5,4),(82,18,3,3)),
 'lands_end':((42,18,5,3),(63,40,4,3),(31,48,4,3)),
 'angel_island':((44,18,5,4),(67,38,5,3),(43,49,4,3)),
}


def native_park(plan,grid,lanes,walks,occupied,sea,shore,token):
    """Keep complete trees and small meadows; never paint over service objects."""
    width,height=len(grid[0]),len(grid)
    legend=plan['legend']
    for row in TREES:
        for identifier in row:legend[chr(0x800+identifier)]=[identifier,True,3]
    flower=chr(0x804);legend[flower]=[4,False,3]
    grass=token('grass')
    clear=set(lanes)
    for cx,cy,rx,ry in GLADES[plan['world_id']]:
        nearest=min(lanes,key=lambda p:(abs(p[0]-cx)+abs(p[1]-cy),p[1],p[0]))
        clear|=raster_path([(cx,cy),nearest],radius=0)
        clear|={(x,y) for y in range(cy-ry,cy+ry+1) for x in range(cx-rx,cx+rx+1)
                if (x-cx)**2*ry**2+(y-cy)**2*rx**2<=rx**2*ry**2}
    # The original service quarter is kept intact during this expansion pass.
    # Its old white approach paint becomes grass, preserving collision and stops.
    protected=occupied|sea|shore
    paving=token('paving')
    for y in range(height):
        for x in range(width):
            if (x,y) in protected:continue
            if x<32 and y<24:
                if grid[y][x]==paving:grid[y][x]=grass
            else:grid[y][x]=grass
    for y in range(0,height,2):
        for x in range(0,width,2):
            cells={(x+dx,y+dy) for dy in (0,1) for dx in (0,1)}
            if cells & (clear|protected):continue
            if any(xx<32 and yy<24 for xx,yy in cells):continue
            for dy,row in enumerate(TREES):
                for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x800+tile)
    # Small coherent flower groups identify meadow edges without a tiled lawn.
    for cx,cy,rx,ry in GLADES[plan['world_id']]:
        for dx,dy in ((-2,-1),(-1,-1),(-2,0),(2,1),(3,1)):
            x,y=cx+dx,cy+dy
            if grid[y][x]==grass and (x,y) not in lanes:grid[y][x]=flower
    from world_trail_ground import worn_patch
    plan['worn_trail_patch']=worn_patch(grid,legend,grass,(48,32),protected)
    # Native border follows the same canopy; exact ports are reopened below.
    plan['border_metatiles']=[tile for row in TREES for tile in row]
    plan['native_park_design']={'meadows':[list(g) for g in GLADES[plan['world_id']]],
                               'native_forest':True,'legacy_quarter_preserved':True}
