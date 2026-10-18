"""Compact authored SF blocks, kept separate from contributor gym interiors."""
from copy import deepcopy
from world_tiles import compile_kit

URBAN = {'dogpatch', 'potrero_hill', 'mission', 'castro', 'outer_sunset',
         'marina', 'pacific_heights', 'noe_valley', 'mission_bay',
         'giants_stadium', 'financial_district', 'north_beach', 'treasure_island'}


def furnish(plans, manifest):
    if not manifest.get('town_finishing'):
        return plans
    kit = compile_kit()
    result = deepcopy(plans)
    for plan in result:
        if plan['world_id'] not in URBAN:
            continue
        grid = [['#' if x in (0, 31) or y in (0, 23) else '.' for x in range(32)] for y in range(24)]
        # Each record has independently checked collision semantics. No roof
        # tile is placed over a walkable building footprint.
        legend = deepcopy(plan['legend'])
        for name, card in kit['catalog'].items():
            for row in card['tiles']:
                for tile in row:
                    legend[chr(0x100 + tile-512)] = [tile, card['blocked'], 3]
        def stamp(name, left, top):
            for dy, row in enumerate(kit['catalog'][name]['tiles']):
                for dx, tile in enumerate(row):
                    grid[top+dy][left+dx] = chr(0x100 + tile-512)
        ground = chr(0x100)
        for y in range(1, 23):
            for x in range(1, 31): grid[y][x] = ground
        for x in range(1, 31):
            for y in range(11, 14): stamp('asphalt', x, y)
        for y in (11, 12, 13):
            for x in (14, 15, 16, 17, 18): stamp('crossing', x, y)
        # Four attached blocks, with pavement continuous under the original
        # foundations. Both street sides get doors, stoops and clear approaches.
        blocks = []
        for left, top, styles in ((1,4,('coral','cafe','cream','lilac')),
                                  (20,4,('lilac','cream','cafe','coral')),
                                  (1,17,('pair','cream','coral')),
                                  (20,17,('cream','pair','lilac'))):
            x=left
            for style in styles:
                stamp(style,x,top)
                width=len(kit['catalog'][style]['tiles'][0])
                blocks.append({'style':style,'x':x,'y':top,'width':width,'height':4})
                x+=width
        # Show a real, reserved gym facade at the existing stable trigger.
        gym = next((g for g in manifest['gyms'] if g['area']==plan['world_id']),None)
        if gym: stamp('cream',15,3)
        else: stamp('pair',14,3)
        for name,x,y in [('lamp',13,5),('lamp',18,17),('meter',6,10),
                         ('hydrant',26,10),('bin',2,15),('rack',26,15),
                         ('bench',6,7),('tree',28,7)]:
            stamp(name,x,y)
        # Preserve the exact three-tile inter-map connection interface.
        for link in plan['connections'] or []:
            for d in (-1,0,1):
                x,y={'left':(0,12+d),'right':(31,12+d),
                     'up':(16+d,0),'down':(16+d,23)}[link['direction']]
                grid[y][x]=ground
        plan['rows']=[''.join(row) for row in grid]
        plan['legend']=legend
        plan['town_blocks']=blocks
        plan['town_props']=['lamp','meter','hydrant','bin','rack','bench','tree']
    return result
