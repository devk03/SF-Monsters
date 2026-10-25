"""Pure prototype planner for own-art/foreign-seam shared primary VRAM slots.

No engine mutations and no fallback over reservations. Caller supplies the
actual General metatile records and ALL existing seam slots. Output graphics
use indexed4bpp pixels; their metatile words retain the caller's palette bank.
Parent integration must load these slots on every applicable map entry and
allocate future seams from the returned remaining_pool (one allocator only).
"""

REQUIRED_METATILES = frozenset((1,2,3,4,11,13,14,22,161,176,177,178,179,184,186,
    194,198,368,464,465,466,468,469,472,473,474,476,477,480,481,482,484,485,
    0x68,0x69,0x6a,0x6b,0x6c,0x70,0x71,0x73,0x78,0x79,0x7b,0xaf,0xcf))
FIXED_RESERVED = frozenset(range(16)) | {20} | frozenset(range(432,512))


def validate_tile(tile):
    tile = bytes(tile)
    if len(tile) != 64 or any(v > 15 for v in tile):
        raise ValueError('A shared graphic must be one64pixel indexed4bpp tile')
    return tile


def reflect(tile, flags):
    return bytes(tile[(7-y if flags & 0x800 else y)*8+(7-x if flags & 0x400 else x)]
                 for y in range(8) for x in range(8))


def canonical_tile(tile):
    tile = validate_tile(tile)
    return min((reflect(tile, flags), flags) for flags in (0,0x400,0x800,0xc00))


def reservations(primary_records):
    """Accept {metatile_id: eight actual linked tile words}; require full coverage.

    Additional supplied terrain IDs are reserved too. This deliberately refuses
    to guess whether undeclared native primary graphics are safe to overwrite.
    """
    missing = REQUIRED_METATILES - primary_records.keys()
    if missing:
        raise ValueError('Missing protected General metatiles: '+str(sorted(missing)))
    slots = set(FIXED_RESERVED)
    for identifier, words in primary_records.items():
        if not isinstance(identifier, int) or not 0 <= identifier < 512:
            raise ValueError('Expected a native primary metatile ID')
        if len(words) != 8 or any(type(w) is not int or not 0 <= w <= 0xffff for w in words):
            raise ValueError('Expected eight native16bit tile words')
        for word in words:
            slot = word & 1023
            if slot >= 512:
                raise ValueError('Protected General record unexpectedly uses secondary graphics')
            slots.add(slot)
    return slots


def plan_shared_primary(primary_records, tiles, *, seam_slots, seam_headroom=0):
    """Return stable graphic placement and per-input word references.

    seam_slots is mandatory, even when explicitly empty. seam_headroom reserves
    additional free slots for seams that have not been packed yet. References
    are tile-ID|flip only; the caller adds its own palette bits without altering
    pixel indices. This planner does not allocate palettes or metatile IDs.
    """
    reserved = reservations(primary_records)
    seams = set(seam_slots)
    if any(type(i) is not int or not 0 <= i < 432 for i in seams):
        raise ValueError('Existing seam slot is outside reusable primary space')
    if seams & reserved:
        raise ValueError('Existing seam slots collide with protected native graphics')
    if type(seam_headroom) is not int or seam_headroom < 0:
        raise ValueError('Seam headroom must be a nonnegative integer')
    pool = sorted(set(range(432))-reserved-seams)
    refs = [canonical_tile(tile) for tile in tiles]
    # Pixel ordering, not Python hash/set iteration or call order, determines
    # ownership. The returned references still follow the input tile order.
    graphics = sorted({canonical for canonical, _ in refs})
    unique = {tile:index for index,tile in enumerate(graphics)}
    if len(unique)+seam_headroom > len(pool):
        raise ValueError(f'Shared own art needs{len(unique)}slots plus{seam_headroom}seam reserve; only{len(pool)}available')
    used = pool[:len(unique)]
    return dict(protected_metatile_ids=sorted(primary_records),
                reserved_slots=sorted(reserved), seam_slots=sorted(seams),
                used_slots=used, graphics=graphics,
                references=[used[unique[tile]] | flags for tile,flags in refs],
                remaining_pool=pool[len(unique):], seam_headroom=seam_headroom,
                palette_locks={3: 'Preserve native implicit0x3014 entries; planner never edits palettes'},
                scope='Prototype only; exact source records and live loading require independent integration audits')
