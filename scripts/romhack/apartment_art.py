"""Compile an original furnished apartment backdrop into a dedicated native tileset."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
from title_art import tiles8
from title_creature import pack4

ASSET = 'assets/tiles/courier-apartment'


def encode_apartment(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGB')
    native = source.resize((176, 160), Image.Resampling.NEAREST)
    values = native.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in values[i:i + 3])
                           for i in range(0, 45, 3)]
    palette = [c for color in colors for c in color] + [0] * 720
    image = Image.new('P', native.size, 0); image.putpalette(palette)
    image.putdata([min(range(1, 16), key=lambda i: sum((rgb[c] - colors[i][c]) ** 2
                                                    for c in range(3))) for rgb in native.get_flattened_data()])
    image.save(directory / 'native-room.png', bits=4)
    raw, records, attributes = bytearray(), bytearray(), bytearray()
    border_color = min(range(1, 16), key=lambda i: sum(colors[i]))
    border_tiles = [0x6200 | tile for tile in range(440, 444)]
    for y in range(10):
        for x in range(11):
            cell = image.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)).tobytes()
            raw.extend(pack4(tiles8(cell, 16, 16, 2, 2)))
            upper = [0x6200 | ((y * 11 + x) * 4 + tile) for tile in range(4)]
            records.extend(struct.pack('<8H', *border_tiles, *upper))
            attributes.extend(struct.pack('<H', 0x65 if (x, y) == (5, 9) else 0))
    raw.extend(bytes([border_color | border_color << 4]) * 128)
    records.extend(struct.pack('<8H', *border_tiles, *border_tiles)); attributes.extend(bytes(2))
    sheet = Image.new('P', (128, 224), 0); sheet.putpalette(palette)
    for tile in range(444):
        for y in range(8):
            for x in range(8):
                byte = raw[tile * 32 + y * 4 + x // 2]
                sheet.putpixel((tile % 16 * 8 + x, tile // 16 * 8 + y), byte >> (x % 2 * 4) & 15)
    sheet.save(directory / 'tiles.png', bits=4)
    native_palette = b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c)
                                                 for c in range(3))) for rgb in colors)
    files = {'tiles.4bpp': bytes(raw), 'metatiles.bin': bytes(records),
             'attributes.bin': bytes(attributes), 'palettes.gbapal': bytes(192) + native_palette + bytes(288)}
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'source_size': list(source.size), 'native_size': [176, 160], 'palette_bank': 6,
        'tile_count': 444, 'metatile_count': 111, 'border_metatile': 622,
        'exit_metatile': 616, 'exit_behavior': 'MB_SOUTH_ARROW_WARP',
        'quality_approval': 'pending', 'files': {
            **{name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
            'tiles.png': hashlib.sha256((directory / 'tiles.png').read_bytes()).hexdigest()}
    }, indent=2) + '\n')


def apply_apartment_art(root, engine, original):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    if hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest() != metadata['source_sha256'] or \
       any(hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest
           for name, digest in metadata['files'].items()):
        raise ValueError('Regenerate apartment resources after changing their source.')
    destination = engine / 'data/tilesets/secondary/sf_courier_home'
    destination.mkdir(parents=True, exist_ok=True)
    for name in ('tiles.png', 'metatiles.bin', 'attributes.bin', 'palettes.gbapal'):
        shutil.copy2(directory / name, destination / name)
    prefix = 'data/tilesets/secondary/sf_courier_home/'
    # Earlier source stages may add declarations to graphics.h; preserve them.
    graphics = engine / 'src/data/tilesets/graphics.h'
    text = graphics.read_text()
    declarations = '\nconst u32 gTilesetTiles_SFCourierHome[] = INCGFX_U32("' + prefix + 'tiles.png", ".4bpp.lz", "-num_tiles 444 -Wnum_tiles");\n'
    declarations += 'const u16 gTilesetPalettes_SFCourierHome[] = INCBIN_U16("' + prefix + 'palettes.gbapal");\n'
    if 'gTilesetTiles_SFCourierHome' in text:
        raise ValueError('Apartment tileset declarations must be reset before rebuilding.')
    graphics.write_text(text + declarations)
    path = 'src/data/tilesets/metatiles.h'
    (engine / path).write_text(original(path) +
        '\nconst u16 gMetatiles_SFCourierHome[] = INCBIN_U16("' + prefix + 'metatiles.bin");\n' +
        'const u16 gMetatileAttributes_SFCourierHome[] = INCBIN_U16("' + prefix + 'attributes.bin");\n')
    headers = 'src/data/tilesets/headers.h'
    (engine / headers).write_text(original(headers) + '''
const struct Tileset gTileset_CourierHome = {
    .isCompressed = TRUE,
    .isSecondary = TRUE,
    .tiles = gTilesetTiles_SFCourierHome,
    .palettes = gTilesetPalettes_SFCourierHome,
    .metatiles = gMetatiles_SFCourierHome,
    .metatileAttributes = gMetatileAttributes_SFCourierHome,
    .callback = NULL,
};
''')
    return ['src/data/tilesets/graphics.h', path, headers]


if __name__ == '__main__':
    encode_apartment(Path(__file__).resolve().parents[2])
