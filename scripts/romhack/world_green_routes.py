"""Authored SF woodland passages using native Emerald terrain references.

Composition study: Route102 and Petalburg Woods use tree masses, grass clearings
and optional encounter pockets. No original route geometry is copied here.
"""
from world_district_layouts import raster_path

TREES=((0x1d4,0x1d5),(0x1dc,0x1dd))
PATHS={
 'route_19':([(4,12),(9,12),(9,6),(20,6),(20,15),(27,15),(27,12)],(8,19)),
 'route_20':([(4,12),(9,12),(9,18),(19,18),(19,8),(27,8),(27,12)],(24,19)),
 'route_05':([(8,4),(8,10),(18,10),(18,18),(26,18),(26,12),(16,12)],(5,18)),
 'route_06':([(5,8),(12,8),(12,18),(24,18),(24,12),(16,12)],(24,5)),
 'route_14':([(4,16),(10,16),(10,6),(22,6),(22,12),(16,12)],(24,19)),
 'route_15':([(7,5),(7,15),(20,15),(20,7),(26,7),(26,12),(16,12)],(8,20)),
 'route_02_mid':([(5,6),(14,6),(14,16),(25,16),(25,12),(16,12)],(6,19)),
 'route_05_mid':([(5,17),(13,17),(13,8),(24,8),(24,12),(16,12)],(24,19)),
 'route_06_mid':([(6,5),(22,5),(22,11),(10,11),(10,18),(16,18),(16,12)],(26,19)),
 'route_08_mid':([(6,18),(6,9),(18,9),(18,4),(26,4),(26,12),(16,12)],(24,19)),
 'route_09_mid':([(5,5),(12,5),(12,17),(24,17),(24,12),(16,12)],(25,5)),
 'route_10_mid':([(6,7),(23,7),(23,18),(12,18),(12,12),(16,12)],(6,19)),
 'route_14_mid':([(5,6),(5,16),(14,16),(14,7),(25,7),(25,12),(16,12)],(24,19)),
 'route_15_mid':([(6,17),(22,17),(22,6),(12,6),(12,12),(16,12)],(5,5)),
}


def furnish_green_route(plan,kit):
    name=plan['world_id'];width,height=32,24
    line,pocket=PATHS[name]
    main=raster_path(line)
    ports=[]
    for link in plan['connections'] or []:
        side=link['direction']
        edge={'left':(0,12),'right':(31,12),'up':(16,0),'down':(16,23)}[side]
        nearest=min(main,key=lambda p:(abs(p[0]-edge[0])+abs(p[1]-edge[1]),p[1],p[0]))
        elbow=(nearest[0],edge[1]) if side in ('left','right') else (edge[0],nearest[1])
        main|=raster_path([edge,elbow,nearest]);ports.append(side)
    px,py=pocket
    nearest=min(line,key=lambda p:abs(p[0]-px)+abs(p[1]-py))
    branch=raster_path([nearest,(px,nearest[1]),pocket],radius=0)
    glade={(x,y) for y in range(py-3,py+4) for x in range(px-4,px+5)
           if (x-px)**2/16+(y-py)**2/9<=1}
    clear=main|branch|glade
    grid=[['.']*width for _ in range(height)]
    legend=dict(plan['legend'])
    for identifier in (0x1d4,0x1d5,0x1dc,0x1dd):
        legend[chr(0x800+identifier)]=[identifier,True,3]
    legend['G']=[13,False,3]  # Optional native tall-grass encounter patches.
    legend['F']=[4,False,3]  # Original animated field flowers, not a painted prop.
    for y in range(0,height,2):
        for x in range(0,width,2):
            footprint={(x+dx,y+dy) for dx in (0,1) for dy in (0,1)}
            if footprint & clear:continue
            for dy,row in enumerate(TREES):
                for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x800+tile)
    from world_forest_edges import finish_forest
    finish_forest(grid,legend,clear,'.')
    # Reserve the rest stop before encounter planting. It must fit wholly
    # inside a reachable side clearing, with an unobstructed approach below it.
    bench=kit['catalog']['bench_grass']['tiles']
    rest=None
    for x,y in sorted(glade,key=lambda p:(abs(p[0]-px)+abs(p[1]-(py+1)),p[1],p[0])):
        cells={(x+dx,y+dy) for dy,row in enumerate(bench) for dx,_ in enumerate(row)}
        approach={(xx,y+len(bench)) for xx in range(x,x+len(bench[0]))}
        if cells & (main|branch):continue
        if not cells|approach<=glade:continue
        if any(not 1<xx<width-2 or not 1<yy<height-2 or grid[yy][xx]!='.' for xx,yy in cells|approach):continue
        rest=(x,y,cells|approach);break
    if rest is None:raise ValueError(name+': side clearing has no complete rest stop')
    # Compact asymmetric patches, not an outline following every canopy edge.
    encounters=[]
    for x,y in sorted(glade):
        if not 1<x<width-2 or not 1<y<height-2:continue
        if (x,y) in main|branch|rest[2]:continue
        if x>px or y>py or (x-px)**2+(y-py)**2>10:continue
        if grid[y][x]=='.':
            grid[y][x]='G';encounters.append([x,y])
    for cx,cy in ((line[1][0]-2,line[1][1]-1),(line[-2][0]+2,line[-2][1]+1)):
        for dx,dy in ((0,0),(1,0),(0,1)):
            x,y=cx+dx,cy+dy
            if 2<x<width-3 and 2<y<height-3 and grid[y][x]=='.':grid[y][x]='F'
    # Seal everything except the exact three-tile connection contract.
    for y in range(height):
        for x in range(width):
            if x in (0,width-1) or y in (0,height-1):
                grid[y][x]=chr(0x800+TREES[y%2][x%2])
    for side in ports:
        for delta in (-1,0,1):
            x,y={'left':(0,12+delta),'right':(31,12+delta),
                 'up':(16+delta,0),'down':(16+delta,23)}[side]
            grid[y][x]='.'
    # One quiet rest stop belongs to the optional clearing. It does not turn
    # the whole route into a concrete plaza or block the through-path.
    x,y,_=rest
    for dy,row in enumerate(bench):
        for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x100+tile-512)
    blocks=[dict(style='bench_grass',x=x,y=y,width=len(bench[0]),height=len(bench),first_metatile=bench[0][0])]
    plan.update(rows=[''.join(row) for row in grid],legend=legend,water_positions=[],
                town_blocks=blocks,scenic_viewpoints=[],route_setting='woodland grass trail',
                encounter_positions=encounters,
                border_metatiles=[0x1d4,0x1d5,0x1dc,0x1dd],
                green_route_design={'spine':line,'side_clearing':list(pocket),'native_forest':True})
    plan['metadata']['map_type']='MAP_TYPE_ROUTE'
    return plan
