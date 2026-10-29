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
