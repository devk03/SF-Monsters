"""Small useful neighborhood rooms with independently paired native door scripts."""
from copy import deepcopy
from world_tiles import compile_kit
from world_people import native_text, load_people

PROPS = {
 'workshop':[('desk',11,12),('shelf',19,7),('rack',11,15)],
 'library':[('shelf',11,8),('shelf',19,8),('desk',15,12)],
 'studio':[('desk',11,11),('desk',18,11),('indoor_plant',20,8)],
 'cafe':[('desk',11,11),('desk',18,11),('shelf',19,7)],
 'rest':[('bed',11,8),('bed',19,8),('indoor_plant',20,14)],
 'bar':[('desk',11,11),('desk',13,11),('desk',18,11),('shelf',19,7)],
 'home':[('bed',11,8),('shelf',19,7),('indoor_plant',20,14)]}


def add_rooms(plans, manifest):
    if not manifest.get('interiors'):
        return plans
    from generate_world import native_id
    kit = compile_kit()
    by_id = {p['world_id']:p for p in plans}
    people = load_people()
    for room in manifest['interiors']:
        parent = by_id[room['area']]
        legend = deepcopy(parent['legend'])
        def token(tile): return chr(0x100+tile-512)
        grid = [[token(613)]*16 for _ in range(11)]
        def stamp(name,x,y):
            for dy,row in enumerate(kit['catalog'][name]['tiles']):
                for dx,tile in enumerate(row): grid[y-6+dy][x-8+dx]=token(tile)
        for y in range(8,16):
            for x in range(11,21): stamp('wood_floor',x,y)
        for x in range(10,22):
            stamp('wall_top',x,6);stamp('wall_low',x,7)
            stamp('wall_bottom',x,16)
        for y in range(8,17):
            stamp('wall_side',10,y);stamp('wall_side',21,y)
        stamp('wall_span',10,6)
        stamp('rug',15,12);stamp('threshold',16,15);stamp('door_frame',16,16)
        for name,x,y in PROPS[room['style']]:
            if name != 'desk': stamp(name,x,y)
        stamp('desk',13,12);stamp('desk',18,12)
        # Counter/furniture placement must leave both clerks reachable. The
        # validator checks the actual tiles and arrivals, not this recipe alone.
        residents = people[room['area']]['residents'][-2:]
        npcs=[{'id':1,'x':5,'y':5,'graphics':'OBJ_EVENT_GFX_WOMAN_3',
               'script':'WBRoom_'+room['id']+'_Rest'},
              {'id':2,'x':10,'y':5,'graphics':'OBJ_EVENT_GFX_MAN_2',
               'script':'WBRoom_'+room['id']+'_Shop'}]
        result = {'world_id':room['id'],'engine_map':room['engine_map'],
                  'native_id':native_id(room['engine_map']),
                  'label':room['label'],'unique_layout':True,'rows':[''.join(row) for row in grid],
                  'legend':legend,'border_tile':613,'tilesets':deepcopy(parent['tilesets']),
                  'metadata':dict(parent['metadata'],music='MUS_VERDANTURF',weather='WEATHER_SUNNY'),
                  'connections':None,'npcs':npcs,'coord_events':[],
                  'access_points':[{'kind':'checkpoint','x':5,'y':7,'activation':'interact'},
                                   {'kind':'checkpoint','x':10,'y':7,'activation':'interact'}],'water_positions':[],'script':room['id']+'.inc',
                  'room':room,'service_dialogue':residents}
        for plan,kind,point,target in (
                (parent,'room_entry',room['entry'],room['id']),
                (parent,'arrival',room['outside_arrival'],room['id']),
                (result,'room_exit',room['exit'],room['area']),
                (result,'arrival',room['arrival'],room['area'])):
            x,y=point
            plan['access_points'].append({'kind':kind,'x':x,'y':y,'activation':'walk','target_id':target})
            if kind.startswith('room_'):
                script='WBRoom_'+room['id']+('_Enter' if kind=='room_entry' else '_Exit')
                plan['coord_events'].append({'type':'trigger','x':x,'y':y,'elevation':3,
                     'var':'VAR_TEMP_0','var_value':'0','script':script})
        plans.append(result)
    return plans


def extra_scripts(plan, manifest):
    result=[]
    room=plan.get('room')
    rooms=[room] if room else [r for r in manifest.get('interiors',[]) if r['area']==plan['world_id']]
    for spec in rooms:
        label='WBRoom_'+spec['id']
        target=spec['area'] if room else spec['id']
        records=manifest['areas']+manifest['interiors']
        engine=next(r['engine_map'] for r in records if r['id']==target)
        from generate_world import native_id
        x,y=spec['outside_arrival'] if room else spec['arrival']
        result += [label+('_Exit' if room else '_Enter')+'::',
                   f'    warp {native_id(engine)}, {x}, {y}','    waitstate','    end']
    if room:
        label='WBRoom_'+room['id']
        for index,service in enumerate(('Rest','Shop')):
            result += [label+'_'+service+'::','    lock','    faceplayer',
                       f'    msgbox {label}_{service}Text, MSGBOX_DEFAULT']
            result += (['    special HealPlayerParty','    playfanfare MUS_HEAL','    waitfanfare']
                       if service=='Rest' else [f'    pokemart {label}_Items'])
            result += ['    release','    end',label+'_'+service+'Text::',
                       '    .string "'+native_text(plan['service_dialogue'][index]['dialogue'])+'"']
        result += ['    .align 2',label+'_Items::','    .2byte ITEM_POTION',
                   '    .2byte ITEM_ANTIDOTE','    .2byte ITEM_REPEL','    pokemartlistend']
    return '\n'.join(result)+'\n'
