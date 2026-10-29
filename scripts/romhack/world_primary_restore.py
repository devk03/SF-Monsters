"""Plan native-primary restoration for a map transition; no engine mutation.

The caller supplies actual destination native slots, the previous scene's
overwritten slots, destination-owned slots, and pristine native8x8 tiles.
This prototype does not change allocation or claim that its plan fits VBlank.
"""
from world_shared_primary import validate_tile
import struct


def visible_native_slots(plan, by_native, kits, general_records):
    """Gather native primary graphics visible on this map and clipped margins.

    Include the implicit renderer background and native grass used beneath
    composite cards. This is an input planner, not a runtime allocation change.
    """
    from world_seams import margin_points
    native_words=set()
    def split_ids(area, identifiers):
        kit=kits[area.get('tile_profile','residential')]
        for identifier in identifiers:
            if identifier>=512:
                for word in kit['records'][identifier-512]:
                    if (word&1023)<512 and word>>12<6:native_words.add(word&1023)
        return {i for i in identifiers if i<512}
    def native_ids(area, points):
        return split_ids(area,{area['legend'][area['rows'][y][x]][0] for x,y in points})
    points=((x,y) for y,row in enumerate(plan['rows']) for x in range(len(row)))
    ids=native_ids(plan,points)
    ids |= split_ids(plan,set(plan.get('border_metatiles',[plan.get('border_tile',11)])))
    if kits[plan.get('tile_profile','residential')].get('uses_native_grass'):ids.add(1)
    for link in plan.get('connections') or []:
        neighbor=by_native[link['map']]
        ids |= native_ids(neighbor,margin_points(neighbor,link['direction'],plan,link['offset']))
        if kits[neighbor.get('tile_profile','residential')].get('uses_native_grass'):ids.add(1)
    slots={20} | native_words  # The field renderer draws implicit background word 0x3014.
    for identifier in ids:
        if len(general_records) < (identifier+1)*16:
            raise ValueError('Missing native primary metatile record')
        for word in struct.unpack_from('<8H',general_records,identifier*16):
            slot=word&1023
            if slot>=512:raise ValueError('Native metatile references secondary graphics')
            slots.add(slot)
    return slots


def restoration(previous_slots, destination_native, destination_owned, native_tiles):
    previous, native, owned = map(set, (previous_slots, destination_native, destination_owned))
    if any(type(slot) is not int or not 0 <= slot < 512 for slot in previous | native | owned):
        raise ValueError('Expected primary graphics slots in range 0..511')
    if native & owned:
        raise ValueError('Destination native and owned graphics collide')
    needed = sorted(previous & native)
    missing = set(needed) - native_tiles.keys()
    if missing:
        raise ValueError('Missing pristine native graphics for restoration')
    return [(slot, validate_tile(native_tiles[slot])) for slot in needed]


def destination_restoration(destination_native, destination_owned, native_tiles):
    """Restore all visible native graphics, independent of transition history.

    A slot overwritten two maps ago can still be stale when the immediately
    preceding map never touched it. A runtime that tracks only the last map's
    writes is therefore insufficient. Animation and VBlank timing remain for the
    engine integration to prove; this helper is only a conservative plan.
    """
    native=set(destination_native)
    return restoration(native,native,destination_owned,native_tiles)


def borrowed_restoration(destination_native, destination_owned, native_tiles,
                         potentially_overwritten, borrowed_slots):
    """Limit restoration to a proven set of borrowable native slots.

    Every destination-native slot that any scene can overwrite must belong to
    borrowed_slots. The caller must include own AND foreign seam allocations
    in potentially_overwritten, across the entire world. Animation and DMA
    timing are outside this pure planner's scope.
    """
    native, overwritten, borrowed = map(set, (destination_native, potentially_overwritten, borrowed_slots))
    if any(type(slot) is not int or not 0 <= slot < 512 for slot in overwritten):
        raise ValueError('Expected primary graphics slots in range 0..511')
    if (native & overwritten) - borrowed:
        raise ValueError('A destination-native slot can be overwritten outside the borrowed set')
    return restoration(borrowed,native,destination_owned,native_tiles)


def relocate_owned_records(records, owned_graphics, native_slots, forbidden_secondary=()):
    """Plan lossless per-map relocation of conflicting owned primary tiles.

    `records` must cover every map cell, border and same-profile connection
    margin. Reserve foreign seam/animation slots in `forbidden_secondary`.
    The returned record overrides and graphics are a prototype: the engine
    must load them atomically and restore destination native pixels separately.
    """
    forbidden=set(forbidden_secondary);native=set(native_slots)
    if any(type(i) is not int or not 512<=i<1024 for i in forbidden):
        raise ValueError('Invalid secondary graphics reservation')
    if any(type(i) is not int or not 0<=i<512 for i in native):
        raise ValueError('Invalid native primary graphics reservation')
    words=[word for row in records.values() for word in row]
    if any(len(row)!=8 for row in records.values()) or any(type(w) is not int or not 0<=w<=65535 for w in words):
        raise ValueError('Expected native eight-word metatile records')
    own={w&1023 for w in words if (w&1023)<512 and w>>12>=6}
    missing=own-owned_graphics.keys()
    if missing:raise ValueError('Missing owned primary graphics')
    conflict=sorted(own & native)
    used={w&1023 for w in words if (w&1023)>=512}
    free=sorted(set(range(512,1024))-used-forbidden)
    if len(conflict)>len(free):raise ValueError('Insufficient unused secondary graphics slots')
    mapping=dict(zip(conflict,free))
    graphics={mapping[slot]:validate_tile(owned_graphics[slot]) for slot in conflict}
    revised={identifier:[(w&~1023)|mapping[w&1023]
                         if (w&1023) in mapping and w>>12>=6 else w for w in row]
             for identifier,row in records.items()}
    return dict(mapping=mapping,graphics=graphics,records=revised)


def relocate_atlas(atlas, kit, own_ids, native_slots):
    """Produce an isolated atlas with own and foreign conflicts relocated.

    `own_ids` must include the map, borders, and same-profile margins. This
    does not restore native graphics or schedule DMA; do not publish its output
    until those engine operations and actual transitions have been verified.
    """
    from copy import deepcopy
    own_ids=set(own_ids)
    # A foreign metatile may deduplicate to an otherwise-unused host record.
    # Its mapping still renders that record, so it needs the same override.
    for neighbor in atlas.get('neighbors',[]):
        for identifier in neighbor['used']:
            if identifier>=512:
                mapped=neighbor['mapping'][identifier-512]
                if 512<=mapped<512+len(kit['records']):own_ids.add(mapped)
    if any(type(i) is not int or not 512<=i<512+len(kit['records']) for i in own_ids):
        raise ValueError('Invalid owned metatile identifier')
    if len(atlas['record_ids'])!=len(atlas['records']) or len(atlas['attributes'])!=len(atlas['records']):
        raise ValueError('Foreign atlas record metadata does not match')
    if len(set(atlas['record_ids']))!=len(atlas['record_ids']) or own_ids & set(atlas['record_ids']):
        raise ValueError('Own and foreign atlas identifiers overlap')
    if len(atlas['tile_slots'])!=len(atlas['tiles']) or len(set(atlas['tile_slots']))!=len(atlas['tile_slots']):
        raise ValueError('Atlas graphics allocation is invalid')
    records={('own',i):kit['records'][i-512] for i in own_ids}
    records.update({('foreign',i):r for i,r in enumerate(atlas['records'])})
    all_graphics=dict(zip(atlas['tile_slots'],atlas['tiles']))
    primary={i:v for i,v in all_graphics.items() if i<512}
    secondary={i for i in all_graphics if i>=512}
    plan=relocate_owned_records(records,primary,native_slots,secondary)
    result=deepcopy(atlas)
    result['records']=[plan['records'][('foreign',i)] for i in range(len(atlas['records']))]
    for identifier in sorted(own_ids):
        row=plan['records'][('own',identifier)]
        if row != kit['records'][identifier-512]:
            result['record_ids'].append(identifier)
            result['records'].append(row)
            result['attributes'].append(kit['attributes'][identifier-512])
    for old,new in plan['mapping'].items():
        del all_graphics[old]
        all_graphics[new]=plan['graphics'][new]
    result['tile_slots']=sorted(all_graphics)
    result['tiles']=[all_graphics[i] for i in result['tile_slots']]
    result['own_primary_slots']=[i for i in atlas['own_primary_slots'] if i not in plan['mapping']]
    return result,plan['mapping']
