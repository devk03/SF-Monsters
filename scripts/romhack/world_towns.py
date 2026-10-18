"""Compact authored SF blocks, kept separate from contributor gym interiors."""
from copy import deepcopy
from world_tiles import compile_kit, legend_for, PROFILES

URBAN = {'dogpatch', 'potrero_hill', 'mission', 'castro', 'outer_sunset',
         'marina', 'pacific_heights', 'noe_valley', 'mission_bay',
         'giants_stadium', 'financial_district', 'north_beach', 'treasure_island'}
GREEN_ROUTES = {'route_05','route_06','route_14','route_15'}


def furnish(plans, manifest):
    if not manifest.get('town_finishing'):
        return plans
    kits = {}
    result = deepcopy(plans)
    streets = {r['id'] for r in manifest['routes'] if r['mode']=='walk' and r['id'] not in GREEN_ROUTES}
    for plan in result:
        connector = plan['world_id'] in streets
        if plan['world_id'] not in URBAN and not connector:
            continue
        profile = manifest['town_finishing'].get('profiles',{}).get(plan['world_id'],'residential')
        if profile not in kits: kits[profile] = compile_kit(profile=profile)
        kit = kits[profile]
        grid = [['#' if x in (0, 31) or y in (0, 23) else '.' for x in range(32)] for y in range(24)]
        # Each record has independently checked collision semantics. No roof
        # tile is placed over a walkable building footprint.
        legend = legend_for(kit)
        occupied = set()
        def stamp(name, left, top):
            card = kit['catalog'][name]
            cells = {(left+x,top+y) for y,row in enumerate(card['tiles']) for x,_ in enumerate(row)}
            if card['blocked']:
                if cells & occupied:raise ValueError('Street furnishing overlaps an architectural footprint')
                occupied.update(cells)
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
        recipes = {
            'industrial':((1,3,('warehouse','coral')),(20,3,('brick','coral','cafe','coral')),
                          (1,16,('warehouse','coral')),(20,16,('brick','warehouse'))),
            'civic':((1,3,('clinic','cafe')),(20,3,('brick','brick','cream')),
                     (1,16,('brick','cream','cafe')),(20,16,('clinic','cafe'))),
            'residential':((1,4,('coral','cafe','cream','lilac')),
                           (20,4,('lilac','cream','cafe','coral')),
                           (1,17,('pair','cream','coral')),(20,17,('cream','pair','lilac')))}
        recipe = list(recipes.get(profile,recipes['residential']))
        if profile == 'stadium':
            recipe=[(1,4,('cream','cafe','cream')),(21,4,('cream','cafe','cream')),
                    (1,17,('cafe','cream','cafe')),(21,17,('cream','cafe','cream'))]
        # Explicit neighborhood variants keep the shared door/road interface,
        # but avoid repeating the same four facades in the same order citywide.
        variants = {
            'outer_sunset':(('pair','coral','cafe'),('pair','pair','cafe'),('pair','pair','cafe')),
            'pacific_heights':(('cream','lilac','cream'),('lilac','cream','coral'),('cream','lilac','cream')),
            'noe_valley':(('pair','lilac','cafe'),('cream','pair','coral'),('pair','cream','pair')),
            'potrero_hill':(('coral','pair','cream'),('pair','cream','coral'),('cream','pair','lilac')),
            'marina':(('cream','cream','cafe'),('lilac','cream','pair'),('cream','pair','coral'))}
        if plan['world_id'] in variants:
            for index,styles in zip((1,2,3),variants[plan['world_id']]):
                left,top,_ = recipe[index];recipe[index]=(left,top,styles)
        for left, top, styles in recipe:
            x=left
            for style in styles:
                stamp(style,x,top)
                width=len(kit['catalog'][style]['tiles'][0])
                blocks.append({'style':style,'x':x,'y':top,'width':width,'height':len(kit['catalog'][style]['tiles']),
                               'first_metatile':kit['catalog'][style]['tiles'][0][0]})
                x+=width
        # Show a real, reserved gym facade at the existing stable trigger.
        gym = next((g for g in manifest['gyms'] if g['area']==plan['world_id']),None)
        landmark = None
        if profile == 'industrial': landmark=('crane',14,3)
        elif profile == 'civic': landmark=('highrise',15,2)
        elif profile == 'culture': landmark=('theater',14,3)
        elif profile == 'stadium': landmark=('stadium_gate',13,3)
        if landmark: stamp(*landmark)
        elif gym: stamp('cream',15,3)
        elif not connector: stamp('pair',14,3)
        if connector:
            for link in plan['connections'] or []:
                if link['direction'] in ('up','down'):
                    for y in range(1 if link['direction']=='up' else 12,13 if link['direction']=='up' else 23):
                        for x in range(15,18):stamp('asphalt',x,y)
            plan['route_setting']='city street'
        for name,x,y in [('lamp',12 if profile=='stadium' else 13,5),('lamp',18,17),('meter',6,10),
                         ('hydrant',26,10),('bin',2,15),('rack',26,15),
                         ('bench',6,9),('tree',28,8)]:
            stamp(name,x,y)
        # Preserve the exact three-tile inter-map connection interface.
        for link in plan['connections'] or []:
            for d in (-1,0,1):
                x,y={'left':(0,12+d),'right':(31,12+d),
                     'up':(16+d,0),'down':(16+d,23)}[link['direction']]
                grid[y][x]=ground
        plan['rows']=[''.join(row) for row in grid]
        plan['legend']=legend
        plan['tile_profile']=profile
        plan['tilesets']['secondary']=PROFILES[profile]
        plan['town_blocks']=blocks
        plan['town_props']=['lamp','meter','hydrant','bin','rack','bench','tree']
        if landmark:
            plan['landmarks']=[{'name':landmark[0],'x':landmark[1],'y':landmark[2]}]
            style,x,y=landmark;card=kit['catalog'][style]
            blocks.append({'style':style,'x':x,'y':y,'width':len(card['tiles'][0]),
                           'height':len(card['tiles']),'first_metatile':card['tiles'][0][0]})
            plan['scenic_viewpoints']=[{'x':16,'y':8,'name':style}]
    return result
