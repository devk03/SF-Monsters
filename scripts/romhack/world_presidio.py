"""A wooded campus/residential transition, separate from Pacific Heights.

Existing street and service geometry owns circulation. Complete native tree
groups occupy unused lawn beyond that campus, never roofs or walking shoulders.
"""
from world_green_routes import TREES


def landscape(plan, grid, lanes, walks, occupied, token):
    if plan['world_id'] != 'presidio':
        return
    plan['metadata']['map_type']='MAP_TYPE_CITY'
    width,height=len(grid[0]),len(grid)
    grass=token('grass')
    for row in TREES:
        for tile in row:
            plan['legend'][chr(0x800+tile)]=[tile,True,3]
    protected=occupied|walks|{(x,y) for y in range(24) for x in range(32)}
    # The campus clearings remain open between attached housing blocks. The
    # western reserve and eastern wooded ridge make this a hybrid destination,
    # rather than another residential grid with a different sign.
    campus={(x,y) for y in range(1,height-1) for x in range(1,width-1)
            if (34<=x<=74 and 1<=y<=10)
            or (36<=x<=74 and 15<=y<=22)
            or (28<=x<=74 and 38<=y<=61)}
    planted=set()
    for y in range(0,height-1,2):
        for x in range(0,width-1,2):
            cells={(x+dx,y+dy) for dy in (0,1) for dx in (0,1)}
            if cells & (protected|campus):continue
            if any(grid[yy][xx]!=grass for xx,yy in cells):continue
            for dy,row in enumerate(TREES):
                for dx,tile in enumerate(row):
                    grid[y+dy][x+dx]=chr(0x800+tile)
            planted|=cells
    from world_forest_edges import finish_forest
    finish_forest(grid,plan['legend'],protected|campus,grass)
    plan['presidio_design']={
        'native_forest_cells':len(planted),
        'campus_clearings':'attached housing and visitor court',
        'walk_connections':['Presidio Greenway','Lyon Steps Walk'],
        'visual_acceptance':'pending actual native review',
    }
