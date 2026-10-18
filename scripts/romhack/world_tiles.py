"""Compile the original SF street kit into one bounded native secondary tileset."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRST_TILE = 512
FIRST_METATILE = 512
LAYER_COVERED = 0x1000


def checked(directory, name, receipt):
    data = (directory / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != receipt['files'][name]:
        raise ValueError('Original SF asset changed: ' + str(directory / name))
    return data


def crop(pixels, width, x, y, w, h):
    return bytes(pixels[(y+dy)*width+x+dx] for dy in range(h) for dx in range(w))


def compile_kit(root=ROOT):
    """Two native layers: opaque ground and original transparent architecture."""
    tiles = [bytes(64)]
    tile_ids = {tiles[0]: 0}
    records, attributes, catalog = [], [], {}
    palettes = {}

    def words(pixels, bank):
        result = []
        for y, x in ((0, 0), (0, 8), (8, 0), (8, 8)):
            tile = crop(pixels, 16, x, y, 8, 8)
            if tile not in tile_ids:
                tile_ids[tile] = len(tiles); tiles.append(tile)
            result.append(FIRST_TILE + tile_ids[tile] | bank << 12)
        return result

    def card(name, pixels, width, height, bank, ground, ground_bank, blocked=True):
        if len(pixels) != width*height or width % 16 or height % 16 or max(pixels) > 15:
            raise ValueError('Native SF card dimensions/palette are invalid')
        ids = []
        for y in range(0, height, 16):
            row = []
            for x in range(0, width, 16):
                row.append(FIRST_METATILE + len(records))
                records.append(words(ground, ground_bank) + words(crop(pixels, width, x, y, 16, 16), bank))
                attributes.append(LAYER_COVERED)
            ids.append(row)
        catalog[name] = {'tiles': ids, 'blocked': blocked}

    paving_dir = root / 'assets/tiles/south-park-paving-v1'
    paving_info = json.loads((paving_dir / 'conversion.json').read_text())
    paving = checked(paving_dir, 'paving.indices', paving_info)
    palettes[7] = checked(paving_dir, 'paving.gbapal', paving_info)
    empty = bytes(256)
    card('paving', empty, 16, 16, 7, paving, 7, False)
    # Use existing original asphalt, not a yellow or teal ground replacement.
    street_dir = root / 'assets/tiles/sunset-streets'
    street_info = json.loads((street_dir / 'conversion.json').read_text())
    source = checked(street_dir, 'tiles.indices', street_info)
    palettes[8] = checked(street_dir, 'street.gbapal', street_info)
    asphalt = bytes(source[(y % 4)*64+x] for y in range(16) for x in range(16))
    crossing = crop(source, 64, 16, 16, 16, 16)
    card('asphalt', empty, 16, 16, 8, asphalt, 8, False)
    card('crossing', empty, 16, 16, 8, crossing, 8, False)
    house_dir = root / 'assets/tiles/connected-frontage-v3'
    info = json.loads((house_dir / 'conversion.json').read_text())
    houses = checked(house_dir, 'block.indices', info)
    palettes[6] = checked(house_dir, 'block.gbapal', info)
    # Shared attached fronts keep roofs, walls and stoops together at native scale.
    for name, x, width in [('coral', 0, 48), ('cafe', 48, 32),
                            ('cream', 80, 48), ('lilac', 128, 48)]:
        card(name, crop(houses, 176, x, 0, width, 64), width, 64, 6, paving, 7)
    pair_dir = root / 'assets/tiles/compact-townhouses-v1'
    pair_info = json.loads((pair_dir / 'conversion.json').read_text())
    card('pair', checked(pair_dir, 'pair.indices', pair_info), 64, 64, 6, paving, 7)
    furniture_dir = root / 'assets/tiles/city-furniture-v1'
    furniture_info = json.loads((furniture_dir / 'conversion.json').read_text())
    for item in furniture_info['cards']:
        name = item['name']; raw = (furniture_dir / (name + '.indices')).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['indices_sha256']:
            raise ValueError('Original furniture changed: ' + name)
        w, h = item['size']
        card(name, raw, w, h, 6, paving, 7)
    if len(tiles) > 512 or len(records) > 512:
        raise ValueError('SF world kit exceeds native secondary allocation')
    return {'tiles': tiles, 'records': records, 'attributes': attributes,
            'palettes': palettes, 'catalog': catalog}


def apply_kit(engine, original, kit):
    """Normal compile inputs, never unverified post-link cartridge replacements."""
    from PIL import Image
    directory = 'data/tilesets/secondary/petalburg/'
    files = []
    pixels = bytearray(128*256)
    for index, tile in enumerate(kit['tiles']):
        left, top = index % 16 * 8, index // 16 * 8
        for y in range(8):
            pixels[(top+y)*128+left:(top+y)*128+left+8] = tile[y*8:y*8+8]
    image = Image.new('P', (128, 256)); image.putdata(pixels)
    image.putpalette([v for i in range(256) for v in (i, i, i)])
    image.save(engine / directory / 'tiles.png', bits=4)
    files.append(directory + 'tiles.png')
    for name, data in [('metatiles.bin', b''.join(struct.pack('<8H', *r) for r in kit['records'])),
                       ('metatile_attributes.bin', struct.pack('<'+'H'*len(kit['attributes']), *kit['attributes']))]:
        (engine / directory / name).write_bytes(data); files.append(directory + name)
    for bank, raw in kit['palettes'].items():
        colors = [tuple(((w >> c*5) & 31)*255//31 for c in range(3)) for w in struct.unpack('<16H', raw)]
        relative = directory + f'palettes/{bank:02d}.pal'
        (engine / relative).write_text('JASC-PAL\n0100\n16\n' + '\n'.join(' '.join(map(str, rgb)) for rgb in colors) + '\n')
        files.append(relative)
    path = 'src/data/tilesets/graphics.h'
    source = original(path)
    old = '"-num_tiles 159 -Wnum_tiles"'
    line = next(line for line in source.splitlines() if line.startswith('const u32 gTilesetTiles_Petalburg[]'))
    if old not in line:
        raise ValueError('Pinned secondary tileset allocation changed')
    (engine / path).write_text(source.replace(line, line.replace(old, '"-num_tiles 512 -Wnum_tiles"'), 1))
    files.append(path)
    path = 'src/data/tilesets/headers.h'
    source = original(path)
    (engine / path).write_text(source.replace('.callback = InitTilesetAnim_Petalburg,', '.callback = NULL,', 1))
    files.append(path)
    return files
