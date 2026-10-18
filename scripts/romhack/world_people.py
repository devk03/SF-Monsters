"""Authored ambient town life, separate from reserved contributor mission hooks."""
import json
import textwrap
from pathlib import Path
from world_towns import URBAN

ROOT = Path(__file__).resolve().parents[2]
POSITIONS = [(4,8),(25,8),(8,15),(23,15),(3,21),(27,21),(10,9),(21,9)]
GRAPHICS = ['MAN_1','WOMAN_1','BOY_1','WOMAN_2','OLD_MAN','GIRL_1','WOMAN_3','MAN_2']
REVISIT_BADGE = {'dogpatch':1,'potrero_hill':1,'mission':1,'castro':1,
                 'outer_sunset':2,'golden_gate_park':2,'marina':3,
                 'pacific_heights':4,'twin_peaks':4,'noe_valley':5,
                 'mission_bay':6,'giants_stadium':6,'financial_district':7,
                 'north_beach':8,'treasure_island':5,'sutro_tower':5,
                 'lands_end':8,'angel_island':8}


def load_people():
    data = json.loads((ROOT / 'romhack/world/districts.json').read_text())
    if data['schema_version'] != 1 or set(data['areas']) != set(REVISIT_BADGE):
        raise ValueError('Town dialogue must cover every approved destination')
    for identifier, area in data['areas'].items():
        expected = 8 if identifier in URBAN else 2
        if len(area['residents']) != expected:
            raise ValueError('Core resident allocation changed: ' + identifier)
        for person in area['residents']:
            for field in ('dialogue', 'revisit'):
                value = person[field]
                if value is not None and (not isinstance(value,str) or not 8 <= len(value) <= 320
                                          or any(c in value for c in '$"\\\n')):
                    raise ValueError('Native conversation needs bounded plain text')
    return data['areas']


def populate(plans, manifest):
    if not manifest.get('town_finishing'):
        return plans
    areas = load_people()
    for plan in plans:
        identifier = plan['world_id']
        if identifier not in areas:
            continue
        residents = areas[identifier]['residents']
        # Core count is stable before contributors receive their native IDs.
        used = {(n['x'],n['y']) for n in plan['npcs']}
        reserved = {(p['x'],p['y']) for p in plan['access_points']}
        for index, person in enumerate(residents):
            if identifier in URBAN:
                x,y = POSITIONS[index]
            else:
                candidates = [(x,y) for y in range(6,21) for x in range(8,25)
                              if (x,y) not in used | reserved and
                              all(not plan['legend'][plan['rows'][yy][xx]][1]
                                  for xx,yy in ((x,y),(x-1,y),(x+1,y),(x,y-1),(x,y+1)))]
                if not candidates: raise ValueError('Nature resident has no safe pocket')
                x,y = min(candidates,key=lambda p:abs(p[0]-(10+index*11))+abs(p[1]-17))
            used.add((x,y))
            npc = {'id':len(plan['npcs'])+1,'x':x,'y':y,
                   'graphics':'OBJ_EVENT_GFX_'+GRAPHICS[index],
                   'script':f'WBTown_{identifier}_{index}', 'role':person['role']}
            if identifier in URBAN and index < 2:
                npc.update(movement='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT',range_x=1,range_y=0)
            plan['npcs'].append(npc)
        plan['ambient_residents'] = residents
        plan['district_character'] = areas[identifier]['character']
    return plans


def native_text(value):
    lines = textwrap.wrap(value, width=28, break_long_words=False)
    if any(len(line)>28 for line in lines): raise ValueError('Native dialogue word exceeds textbox width')
    pages = [r'\n'.join(lines[i:i+2]) for i in range(0,len(lines),2)]
    return r'\p'.join(pages)+'$'


def scripts(plan):
    identifier = plan['world_id']
    result = []
    for index, person in enumerate(plan.get('ambient_residents', [])):
        prefix = f'WBTown_{identifier}_{index}'
        result += [prefix+'::','    lock','    faceplayer']
        if person['revisit']:
            badge = REVISIT_BADGE[identifier]
            result += [f'    goto_if_set FLAG_BADGE{badge:02d}_GET, {prefix}_Revisit']
        result += [f'    msgbox {prefix}_Text, MSGBOX_DEFAULT',prefix+'_Service::']
        if identifier in URBAN and index == 6:
            result += ['    special HealPlayerParty','    playfanfare MUS_HEAL','    waitfanfare']
        if identifier in URBAN and index == 7:
            result += [f'    pokemart {prefix}_Items']
        result += ['    release','    end',prefix+'_Text::',
                   '    .string "'+native_text(person['dialogue'])+'"']
        if person['revisit']:
            result += [prefix+'_Revisit::',f'    msgbox {prefix}_Later, MSGBOX_DEFAULT',
                       f'    goto {prefix}_Service',prefix+'_Later::',
                       '    .string "'+native_text(person['revisit'])+'"']
        if identifier in URBAN and index == 7:
            result += ['    .align 2',prefix+'_Items::','    .2byte ITEM_POTION',
                       '    .2byte ITEM_ANTIDOTE','    .2byte ITEM_REPEL','    pokemartlistend']
    return '\n'.join(result)+'\n'
