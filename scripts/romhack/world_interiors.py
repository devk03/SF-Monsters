"""Small useful neighborhood rooms with independently paired native door scripts."""
import json
from pathlib import Path
from world_tiles import compile_kit, legend_for, PROFILES
from world_people import native_text

def load_details(manifest):
    path = Path(__file__).resolve().parents[2] / 'romhack/world/interior-details.json'
    data = json.loads(path.read_text())
    if data['schema_version'] != 1 or set(data['rooms']) != {r['id'] for r in manifest['interiors']}:
        raise ValueError('Interior details must cover exactly the authored service rooms')
    for detail in data['rooms'].values():
        for field in ('rest', 'shop'):
            value = detail[field]
            if not isinstance(value, str) or not 8 <= len(value) <= 320 or any(c in value for c in '$"\\\n'):
                raise ValueError('Service dialogue needs bounded plain native text')
            native_text(value)
    return data['rooms']


def add_rooms(plans, manifest):
    if not manifest.get('interiors'):
        return plans
    from generate_world import native_id
    kit = compile_kit()
    by_id = {p['world_id']:p for p in plans}
    details = load_details(manifest)
    for room in manifest['interiors']:
        parent = by_id[room['area']]
        legend = legend_for(kit)
        def token(tile): return chr(0x100+tile-512)
        detail = details[room['id']]
        grid = [[token(kit['catalog']['void']['tiles'][0][0])]*16 for _ in range(11)]
        def stamp(name,x,y):
            for dy,row in enumerate(kit['catalog'][name]['tiles']):
                for dx,tile in enumerate(row): grid[y-6+dy][x-8+dx]=token(tile)
        for y in range(8,16):
            for x in range(11,21): stamp('wood_floor',x,y)
        for x in range(10,22):
            stamp('room_wall',x,6);stamp('wall_bottom',x,16)
        for y in range(8,17):
            stamp('wall_side',10,y);stamp('wall_side',21,y)
        stamp('room_wall_left',10,6);stamp('room_wall_right',21,6)
        stamp('room_window',12,6);stamp('room_window',18,6)
        if detail['rug']:
            x,y = detail['rug'];stamp('rug',x+8,y+6)
        stamp('wood_floor',16,15);stamp('room_door_open',16,16)
        protected = {tuple(room[k]) for k in ('arrival','exit')}
        for service in room['services'].values():
            x,y=service['actor']
            protected |= {(x,y),(x,y+1),(x+1,y+1),tuple(service['standing'])}
        occupied = set()
        for name,x,y in detail['props']:
            card = kit['catalog'][name]
            cells = {(x+dx,y+dy) for dy,row in enumerate(card['tiles']) for dx,_ in enumerate(row)}
            if (not card['blocked'] or not cells or cells & (protected | occupied)
                    or any(not 3<=xx<=12 or not 2<=yy<=9 for xx,yy in cells)):
                raise ValueError('Room furniture blocks a fixed service/door or leaves the floor: '+room['id'])
            occupied |= cells
            stamp(name,x+8,y+6)
        for service in room['services'].values():
            x,y=service['actor'];stamp('service_counter',x+8,y+7)
        # Counter/furniture placement must leave both clerks reachable. The
        # validator checks the actual tiles and arrivals, not this recipe alone.
        residents = [{'dialogue':detail[field]} for field in ('rest','shop')]
        rx,ry=room['services']['rest']['actor'];sx,sy=room['services']['shop']['actor']
        tx,ty=room['services']['rest']['standing'];ux,uy=room['services']['shop']['standing']
        npcs=[{'id':1,'x':rx,'y':ry,'graphics':'OBJ_EVENT_GFX_WOMAN_3',
               'script':'WBRoom_'+room['id']+'_Rest'},
              {'id':2,'x':sx,'y':sy,'graphics':'OBJ_EVENT_GFX_MAN_2',
               'script':'WBRoom_'+room['id']+'_Shop'}]
        result = {'world_id':room['id'],'engine_map':room['engine_map'],
                  'native_id':native_id(room['engine_map']),
                  'label':room['label'],'unique_layout':True,'rows':[''.join(row) for row in grid],
                  'legend':legend,'border_tile':613,'tile_profile':'residential',
                  'tilesets':{'primary':manifest['native']['primary_tileset'],'secondary':PROFILES['residential']},
                  'metadata':dict(parent['metadata'],music='MUS_VERDANTURF',weather='WEATHER_SUNNY'),
                  'connections':None,'npcs':npcs,'coord_events':[],
                  'access_points':[{'kind':'checkpoint','x':tx,'y':ty,'activation':'interact','name':'rest_counter'},
                                   {'kind':'checkpoint','x':ux,'y':uy,'activation':'interact','name':'shop_counter'}],'water_positions':[],'script':room['id']+'.inc',
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
