"""Plan native-primary restoration for a map transition; no engine mutation.

The caller supplies actual destination native slots, the previous scene's
overwritten slots, destination-owned slots, and pristine native8x8 tiles.
This prototype does not change allocation or claim that its plan fits VBlank.
"""
from world_shared_primary import validate_tile


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
