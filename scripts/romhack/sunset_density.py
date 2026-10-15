"""Add three compact homes on empty Sunset lots; preserve roads and legacy art."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct

from connected_frontage import load as load_frontage
from park_paving import load_paving, load_paving_palette
from title_art import tiles8
from title_creature import pack4

BASE = 'assets/tiles/sunset-density-v1/baseline-v79'
PARCELS = ((28, 4, 194), (28, 10, 206), (28, 25, 218))
TOKENS = {'C': [706, True, 0], 'p': [742, False, 3]}
METATILES = 231


def sha(data):
    return hashlib.sha256(data).hexdigest()


def footprint():
    cells = {}
    for left, top, first in PARCELS:
        for y in range(4):
            for x in range(3):
                cells[left+x, top+y] = (512+first+y*3+x, 'C')
        for x in range(3):
            cells[left+x, top+4] = (742, 'p')
    return cells


def strip(plan, root):
    if 'compact_homes' not in plan:
        if TOKENS.keys() & plan['legend'].keys():
            raise ValueError('Unregistered Sunset compact-home tokens.')
        return deepcopy(plan)
    original = json.loads((root/BASE/'source-plan.json').read_text())
    result = deepcopy(plan)
    if result.pop('compact_homes') != [list(p) for p in PARCELS] or any(
            result['legend'].get(t) != v for t, v in TOKENS.items()):
        raise ValueError('Sunset density declarations or collision changed.')
    cells = footprint()
    for y, row in enumerate(result['rows']):
        output = list(row)
        for x, token in enumerate(row):
            if (x, y) in cells:
                if token != cells[x, y][1]:
                    raise ValueError('Sunset compact-home footprint changed.')
                output[x] = original['rows'][y][x]
            elif token in TOKENS:
                raise ValueError('Sunset compact-home token escaped its parcel.')
        result['rows'][y] = ''.join(output)
    for token in TOKENS:
        result['legend'].pop(token)
    if result != original:
        raise ValueError('Sunset density changed another map field.')
    return result


def decorate(plan, root):
    if plan != json.loads((root/BASE/'source-plan.json').read_text()):
        raise ValueError('Sunset density must extend the frozen authored map.')
    result = deepcopy(plan)
    for (x, y), (_, token) in footprint().items():
        if plan['rows'][y][x] != '.':
            raise ValueError('Compact homes may replace only empty Sunset lawn.')
        row = result['rows'][y]
        result['rows'][y] = row[:x]+token+row[x+1:]
    result['legend'].update(deepcopy(TOKENS))
    result['compact_homes'] = [list(p) for p in PARCELS]
    if strip(result, root) != plan:
        raise ValueError('Compact homes must preserve existing map fields.')
    return result


def remap(plan, blocks, root):
    strip(plan, root)
    if len(blocks) != 2048:
        raise ValueError('Sunset density requires a32x32 map.')
    output = bytearray(blocks)
    for (x, y), (record, token) in footprint().items():
        offset = (y*32+x)*2
        before = struct.unpack_from('<H', blocks, offset)[0]
        tile, solid, elevation = TOKENS[token]
        expected = tile | (int(solid)*0xc00) | (elevation << 12)
        if before != expected:
            raise ValueError('Sunset density must follow the authored native layout.')
        struct.pack_into('<H', output, offset, record | (before & 0xfc00))
    return bytes(output)


def extend(root, graphics, records, attributes, palettes):
    """Append only to the free pool, keeping waves and door-cache slots separate."""
    receipt = json.loads((root/BASE/'receipt.json').read_text())
    if (len(graphics), len(records), len(attributes), len(palettes)) != (16384, 3104, 388, 512):
        raise ValueError('Sunset density requires the exact old native allocations.')
    for raw, expected in ((graphics, receipt['files']['secondary.4bpp']['sha256']),
                          (records, receipt['full_metatiles_sha256']),
                          (attributes, receipt['full_attributes_sha256']),
                          (palettes, receipt['full_palettes_sha256'])):
        if sha(raw) != expected:
            raise ValueError('Sunset density cannot replace changed legacy resources.')
    source, palette = load_frontage(root, 'v3')
    homes = [b''.join(source[y*176+left:y*176+left+48]
                     for y in range(64)) for left in (0, 80)]
    paving = load_paving(root)
    raw = bytearray(graphics)
    metas = bytearray(records+bytes(37*16))
    attrs = bytearray(attributes+bytes(37*2))
    # Existing zero tail is free storage, never a deduplication candidate.
    unique = {}
    for index in range(401):
        if index not in range(240, 248):
            unique.setdefault(graphics[index*32:index*32+32], index)
    next_slot = 401

    def allocate(tile):
        nonlocal next_slot
        if tile not in unique:
            if next_slot >= 504:
                raise ValueError('Sunset homes exceed the pool before the door cache.')
            unique[tile] = next_slot
            raw[next_slot*32:(next_slot+1)*32] = tile
            next_slot += 1
        return unique[tile]

    def words(pixels, width, height, bank):
        packed = pack4(tiles8(pixels, width, height, width//8, height//8))
        return [(bank << 12) | 512 | allocate(packed[i:i+32])
                for i in range(0, len(packed), 32)]

    ground = words(paving, 16, 16, 9)
    blank = 0x8200 | allocate(bytes(32))
    struct.pack_into('<8H', metas, 230*16, *ground, *([blank]*4))
    struct.pack_into('<H', attrs, 230*2, 0x1000)
    for first, pixels in zip((194, 206), homes):
        native = words(pixels, 48, 64, 8)
        for y in range(4):
            for x in range(3):
                start = y*12+x*2
                quadrants = [native[start+d] for d in (0, 1, 6, 7)]
                struct.pack_into('<8H', metas, (first+y*3+x)*16, *ground, *quadrants)
                struct.pack_into('<H', attrs, (first+y*3+x)*2, 0x1000 if y == 3 else 0)
    for y in range(4):
        for x in range(3):
            source_words = struct.unpack_from('<8H', metas, (194+y*3+2-x)*16)
            flipped = [source_words[4+d] ^ 0x400 for d in (1, 0, 3, 2)]
            struct.pack_into('<8H', metas, (218+y*3+x)*16, *ground, *flipped)
            struct.pack_into('<H', attrs, (218+y*3+x)*2, 0x1000 if y == 3 else 0)
    if next_slot != 491 or raw[491*32:] != bytes(21*32):
        raise ValueError('Review the new art budget and native cache reservation.')
    pal = bytearray(palettes)
    pal[8*32:9*32] = palette
    pal[9*32:10*32] = load_paving_palette(root)
    return bytes(raw), bytes(metas), bytes(attrs), bytes(pal)
