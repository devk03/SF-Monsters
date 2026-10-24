"""Native forest masses around authored park circulation and stable landmarks."""
from world_green_routes import TREES
from world_district_layouts import raster_path

# Each reserve has a different sequence of enclosed meadow destinations.
GLADES={
 'golden_gate_park':((44,20,6,4),(64,42,8,6),(32,49,5,4)),
 'twin_peaks':((45,18,6,4),(65,35,6,4),(38,48,5,4)),
 'sutro_tower':((40,18,4,4),(68,43,5,4),(82,18,3,3)),
 'lands_end':((12,36,4,3),(63,40,5,4),(31,48,4,3)),
 'angel_island':((12,30,4,3),(67,38,6,4),(43,49,4,3)),
}


def native_park(plan,grid,lanes,walks,occupied,sea,shore,token,cards,legacy_approaches):
    """Keep complete trees and small meadows; never paint over service objects."""
    width,height=len(grid[0]),len(grid)
    legend=plan['legend']
    for row in TREES:
        for identifier in row:legend[chr(0x800+identifier)]=[identifier,True,3]
    flower=chr(0x804);legend[flower]=[4,False,3]
    grass=token('grass')
    clear=set(lanes)|legacy_approaches
    for cx,cy,rx,ry in GLADES[plan['world_id']]:
        nearest=min(lanes,key=lambda p:(abs(p[0]-cx)+abs(p[1]-cy),p[1],p[0]))
        clear|=raster_path([(cx,cy),nearest],radius=0)
        clear|={(x,y) for y in range(cy-ry,cy+ry+1) for x in range(cx-rx,cx+rx+1)
                if (x-cx)**2*ry**2+(y-cy)**2*rx**2<=rx**2*ry**2}
    # Preserve real landmarks, furniture and event bindings, not the former
    # rectangular hedge maze. Rebuild its filler as part of the same forest.
    filler={chr(0x100+n-512) for style in ('grove','pine','cypress')
            for row in cards[style]['tiles'] for n in row}
    grasslike=filler|{grass,token('paving')}
    legacy_keep={(x,y) for y in range(24) for x in range(32)
                 if grid[y][x] not in grasslike
                 and not(plan['world_id']=='angel_island' and x>=27)}
    from world_park_water import pond_cells,draw_pond
    pond=pond_cells(plan['world_id'])
    if pond & (occupied|lanes|legacy_keep):raise ValueError('Park pond overlaps a protected binding or trail')
    protected=occupied|sea|shore|legacy_keep|pond
    for event in plan.get('coord_events',[])+plan.get('bg_events',[]):
        point=(event['x'],event['y'])
        nearest=min(lanes,key=lambda p:(abs(p[0]-point[0])+abs(p[1]-point[1]),p[1],p[0]))
        clear|=raster_path([point,nearest])
    for y in range(height):
        for x in range(width):
            if (x,y) not in protected:grid[y][x]=grass
    for y in range(0,height,2):
        for x in range(0,width,2):
            cells={(x+dx,y+dy) for dy in (0,1) for dx in (0,1)}
            if cells & (clear|protected):continue
            for dy,row in enumerate(TREES):
                for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x800+tile)
    from world_forest_edges import finish_forest
    finish_forest(grid,legend,clear|protected,grass)
    draw_pond(plan,grid)
    from world_park_stops import add_park_stops
    add_park_stops(plan,grid,cards,GLADES[plan['world_id']],lanes,protected)
    # Small coherent flower groups identify meadow edges without a tiled lawn.
    for cx,cy,rx,ry in GLADES[plan['world_id']]:
        for dx,dy in ((-2,-1),(-1,-1),(-2,0),(2,1),(3,1)):
            x,y=cx+dx,cy+dy
            if grid[y][x]==grass and (x,y) not in lanes:grid[y][x]=flower
    # Native border follows the same canopy; exact ports are reopened below.
    plan['border_metatiles']=[tile for row in TREES for tile in row]
    plan['native_park_design']={'meadows':[list(g) for g in GLADES[plan['world_id']]],
                               'native_forest':True,'legacy_bindings_preserved':True,'legacy_filler_rebuilt':True}
