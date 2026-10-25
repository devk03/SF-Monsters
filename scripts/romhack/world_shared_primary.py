"""Safe original SF art allocation in reusable native primary VRAM slots.

No engine mutations and no fallback over reservations. Caller supplies the
actual General metatile records and ALL existing seam slots. Output graphics
use indexed4bpp pixels; their metatile words retain the caller's palette bank.
The connection atlas loads these slots on every applicable map entry and
allocates foreign seams after all live own-art slots are reserved.
"""

REQUIRED_METATILES = frozenset((1,2,3,4,11,13,14,22,161,176,177,178,179,184,186,
    194,198,368,464,465,466,468,469,472,473,474,476,477,480,481,482,484,485,
    0x68,0x69,0x6a,0x6b,0x6c,0x70,0x71,0x72,0x73,0x78,0x79,0x7a,0x7b,0xaf,0xcf,0xc8,0xc9,0xca,0xd0,0xd2,0xd8,0xd9,0xda,0x124))
FIXED_RESERVED = frozenset(range(16)) | {20} | frozenset(range(432,512))
# Only slot IDs and a hash of pinned General records are distributed here,
# never extracted reference graphics. apply_seams rechecks actual native uses.
PINNED_GENERAL_HASH = 'ea8d123548ac5ceb12fe2c454bf6d6da1ff487e667769012b43f194b3a23d2f2'
PINNED_RESERVED = FIXED_RESERVED | frozenset((16, 17, 22, 25, 30, 32, 33, 41, 65, 66, 67, 68, 70, 71, 72, 73, 80, 81, 82, 83, 84, 85, 86, 96, 97, 98, 99, 100, 101, 102, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 124, 127, 128, 129, 130, 131, 132, 133, 134, 140, 143, 144, 145, 146, 147, 148, 149, 150, 151, 159, 166, 174, 175, 184, 185, 204, 205, 211, 249, 250, 253, 254, 264, 265, 266, 269, 270, 280, 281, 282, 285, 286, 297, 298, 301, 302, 309, 310, 325, 326, 384, 385, 400, 401, 416, 417, 418, 419, 420, 421))


def validate_general(raw):
    import hashlib
    if hashlib.sha256(b''.join(raw[i*16:i*16+16] for i in sorted(REQUIRED_METATILES))).hexdigest() != PINNED_GENERAL_HASH:
        raise ValueError('Pinned General terrain reservation records changed')


def pack_graphics(tiles, records):
    """Resolve compiler-only graphic handles before any16bit packing.

    Stable profile-owned overflow slots precede per-map foreign seam allocation.
    All slots are independently checked against actual terrain during building.
    """
    pool = sorted(set(range(432))-PINNED_RESERVED)
    overflow = max(0,len(tiles)-512)
    if overflow > len(pool):
        raise ValueError('Own SF art exceeds secondary plus safe primary graphics')
    primary = dict(zip(pool,tiles[512:]))
    resolved = []
    for record in records:
        row = []
        for word in record:
            if word & 0x10000000:
                index = (word >> 16) & 0xfff
                if index >= len(tiles):raise ValueError('Invalid logical SF graphic')
                slot = 512+index if index<512 else pool[index-512]
                word = slot | (word & 0xfc00)
            if not 0 <= word <= 0xffff:raise ValueError('Unresolved SF graphic handle')
            row.append(word)
        resolved.append(row)
    return tiles[:512],primary,resolved


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
