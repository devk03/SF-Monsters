"""Place original street-wall cards in an isolated, unanimated primary tileset."""
import struct
import json
from park_art import facade_cells, tile_orientations
from park_frontage import load
from title_art import tiles8
from title_creature import pack4
from park_paving import load_paving_palette
from sidewalk_thresholds import load as load_thresholds
from connected_frontage import load as load_connected
from city_furniture import load as load_furniture
from city_dressing import strip as strip_dressing
from park_density import strip as strip_density
from compact_townhouses import load as load_compact

# token, name, left, top, width, height, first native metatile
PLACEMENTS = (('W', 'brick', 2, 1, 3, 5, 1),
              ('X', 'sage', 2, 12, 3, 5, 16),
              ('Y', 'sandstone', 2, 20, 3, 5, 31),
              ('Z', 'coffee', 21, 2, 2, 4, 46))
APRON_CARDS = (('brick',54),('sage',57),('bay',60),('coffee',63))
METATILE_COUNT = 120


def connected_tile(plan,x,y):
    if plan.get('tilesets',{}).get('primary')!='gTileset_SFParkFrontage':
        return None
    if not (18<=x<29 and 2<=y<7):
        return None
    rows=('abcZZabcabc','defZZdefdef','ghfZZghfghf','ijfZZijfijf','P'*11)
    if plan['rows'][y][18:29] != rows[y-2]:
        raise ValueError('Connected frontage must retain its existing map footprint.')
    token=plan['rows'][y][x]
    expected=[699,False,3] if y==6 else [plan['legend'][token][0],True,0]
    if plan['legend'][token] != expected:
        raise ValueError('Connected frontage must preserve blocked walls and walkable elevation3 approach.')
    return 65+(y-2)*11+x-18


def infill_tile(plan, x, y):
    token = plan['rows'][y][x]
    for marker, _, left, top, width, height, first in PLACEMENTS:
        if token == marker and left <= x < left + width and top <= y < top + height:
            return first + (y - top) * width + x - left
    raise ValueError('Original infill token is outside its declared footprint.')


def previous_plan(plan):
    """Remove precisely this infill for pinned historical-map comparisons."""
    result = strip_dressing(strip_density(plan))
    result['tilesets'].pop('primary')
    for token, _, left, top, width, height, _ in PLACEMENTS:
        result['legend'].pop(token)
        for y in range(top, top + height):
            row = result['rows'][y]
            if row[left:left+width] != token * width:
                raise ValueError('Infill footprint differs from its declared rectangle.')
            result['rows'][y] = row[:left] + 'P' * width + row[left+width:]
    return result


def resources(root, secondary_records, *, furniture=True, density=True):
    """Use primary0..511 for new pixels; underlay references existing sidewalk."""
    if len(secondary_records) != 150 * 16:
        raise ValueError('Review the pinned secondary metatile allocation.')
    sidewalk = secondary_records[19*16+8:20*16]
    if any(word >> 12 != 4 or not 512 <= (word & 1023) < 1016
           for word in struct.unpack('<4H', sidewalk)):
        raise ValueError('Primary facade underlay must use the existing secondary sidewalk.')
    cards = {card['name']: card for card in load(root)}
    raw = bytearray(32)  # A real transparent primary tile0; never inherited scenery.
    pool = {bytes(32): (0, 0)}
    records = bytearray(sidewalk + bytes(8))
    attributes = bytearray(struct.pack('<H', 0x1000))
    palettes = bytearray(512)
    palettes[4*32:5*32] = load_paving_palette(root)
    def append_cell(pixels,bank,attribute):
        encoded = pack4(tiles8(pixels,16,16,2,2));words=[]
        for offset in range(0,128,32):
            tile=encoded[offset:offset+32]
            if tile not in pool:
                index=len(raw)//32
                if index>=512:raise ValueError('Original primary frontage exceeds512 resident tiles.')
                raw.extend(tile)
                for oriented,bits in tile_orientations(tile):pool.setdefault(oriented,(index,bits))
            index,bits=pool[tile];words.append((bank<<12)|bits|index)
        records.extend(sidewalk+struct.pack('<4H',*words))
        attributes.extend(struct.pack('<H',attribute))
    for _, name, _, _, width, height, first in PLACEMENTS:
        card = cards[name]
        if (card['width'], card['height']) != (width*16, height*16) or \
           len(records)//16 != first or card['bank'] not in range(4):
            raise ValueError('Primary card dimensions, bank or metatile ordering changed.')
        bank = card['bank'];palettes[bank*32:(bank+1)*32] = card['palette']
        for cell_index, (pixels, _) in enumerate(facade_cells(
                card['pixels'], card['width'], card['height'], bank)):
            # Match existing facade priority: front foundation behind the hero.
            append_cell(pixels,bank,0x1000 if cell_index//width==height-1 else 0)
    thresholds=load_thresholds(root)
    for name,first in APRON_CARDS:
        card=thresholds[name]
        if len(records)//16!=first or card['bank']!=5:
            raise ValueError('Threshold records must append after existing frontage.')
        palettes[160:192]=card['palette']
        # The cafe's door is on the right; mirror the whole ground detail,
        # preserving its source art and the renderer's native tile flips.
        pixels=card['pixels']
        if name=='coffee':
            pixels=b''.join(pixels[y*card['width']:(y+1)*card['width']][::-1] for y in range(16))
        for pixels,bank in facade_cells(pixels,card['width'],16,5):
            append_cell(pixels,bank,0x1000)
    # Retain the old original-art prefix for independent preservation checks.
    # Its detached apron records are unused by the map. One complete connected
    # scene supplies architecture; transparent approach pixels reveal paving.
    pixels,palette=load_connected(root,'v3')
    palettes[160:192]=palette
    for index,(cell,bank) in enumerate(facade_cells(pixels,176,80,5)):
        append_cell(cell,bank,0x1000 if index//11>=3 else 0)
    if len(records) != METATILE_COUNT*16 or len(attributes) != METATILE_COUNT*2:
        raise ValueError('Original primary frontage table allocation changed.')
    plan = json.loads((root/'romhack/content/south-park.json').read_text())
    if furniture and 'city_furniture' in plan:
        strip_dressing(plan)  # Validate the entire declared footprint, not only used cells.
        for card in load_furniture(root):
            width,height = card['width'],card['height']
            for index,(cell,bank) in enumerate(facade_cells(card['pixels'],width,height,5)):
                append_cell(cell,bank,0x1000 if index//(width//16)==height//16-1 else 0)
        if len(records)!=135*16 or len(attributes)!=135*2:
            raise ValueError('City furniture must append exactly15 metatiles.')
    if density and 'street_blocks' in plan:
        strip_density(plan)
        if len(records)!=135*16:
            raise ValueError('Compact housing must append after all existing furniture.')
        pixels,palette=load_compact(root)
        if palettes[160:192]!=palette:
            raise ValueError('Compact housing must preserve the accepted street palette.')
        for index,(cell,bank) in enumerate(facade_cells(pixels,64,64,5)):
            append_cell(cell,bank,0x1000 if index//4==3 else 0)
        if len(raw)!=511*32 or len(records)!=151*16 or len(attributes)!=151*2:
            raise ValueError('Review the compact housing resident allocation.')
    return bytes(raw), bytes(records), bytes(attributes), bytes(palettes)


def apply(root, engine, secondary_records):
    from PIL import Image
    raw, records, attributes, palettes = resources(root, secondary_records)
    prefix = 'data/tilesets/primary/sf_south_park_frontage/'
    directory = engine / prefix;directory.mkdir(parents=True, exist_ok=True)
    count = len(raw)//32
    image = Image.new('P', (128, ((count+15)//16)*8), 0)
    image.putpalette([c for i in range(16) for c in (i*17,)*3] + [0]*720)
    for tile in range(count):
        for y in range(8):
            for x in range(8):
                image.putpixel((tile%16*8+x,tile//16*8+y),
                    raw[tile*32+y*4+x//2] >> (x%2*4) & 15)
    image.save(directory / 'tiles.png', transparency=0, bits=4)
    for filename, data in (('metatiles.bin',records),('attributes.bin',attributes),
                            ('palettes.gbapal',palettes)):
        (directory / filename).write_bytes(data)
    declarations = {
        'src/data/tilesets/graphics.h':
            f'\nconst u32 gTilesetTiles_SFParkFrontage[] = INCGFX_U32("{prefix}tiles.png", ".4bpp.lz", "-num_tiles {count} -Wnum_tiles");\n'
            f'const u16 gTilesetPalettes_SFParkFrontage[] = INCBIN_U16("{prefix}palettes.gbapal");\n',
        'src/data/tilesets/metatiles.h':
            f'\nconst u16 gMetatiles_SFParkFrontage[] = INCBIN_U16("{prefix}metatiles.bin");\n'
            f'const u16 gMetatileAttributes_SFParkFrontage[] = INCBIN_U16("{prefix}attributes.bin");\n',
        'src/data/tilesets/headers.h': '''
const struct Tileset gTileset_SFParkFrontage = {
    .isCompressed = TRUE, .isSecondary = FALSE,
    .tiles = gTilesetTiles_SFParkFrontage,
    .palettes = (const u16 (*)[16])gTilesetPalettes_SFParkFrontage,
    .metatiles = gMetatiles_SFParkFrontage,
    .metatileAttributes = gMetatileAttributes_SFParkFrontage, .callback = NULL,
};
'''}
    for filename, declaration in declarations.items():
        path = engine / filename;source = path.read_text()
        if 'SFParkFrontage' in source:
            raise ValueError('Reset native declarations before installing primary frontage.')
        path.write_text(source + declaration)
    return list(declarations)
