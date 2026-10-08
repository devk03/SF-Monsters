"""Convert original coastal terrain and preserve native field collision coordinates."""
import hashlib
import json
from pathlib import Path
import struct
import shutil
from street_art import rotate_pixels
from title_art import tiles8
from title_creature import pack4

ASSET = 'assets/tiles/sunset-terrain'
FIRST_METATILE = 60
PALETTE_BANK = 12
WAVE_TILE_START = 240
WAVE_CELLS = ((2, 3), (10, 11), (14, 15))
# Extra native orientations of the authored northwest railing corner.
VARIANTS = [(index, 0) for index in range(16)] + [(7, turn) for turn in (1, 2, 3)]
TOKENS = set('.WESFG#')


def encode_terrain(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGB')
    native = Image.new('RGB', (64, 64))
    for row in range(4):
        for column in range(4):
            box = (round(column * source.width / 4), round(row * source.height / 4),
                   round((column + 1) * source.width / 4), round((row + 1) * source.height / 4))
            cell = source.crop(box).resize((16, 16), Image.Resampling.NEAREST)
            native.paste(cell, (column * 16, row * 16))
    values = native.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in values[i:i + 3])
                           for i in range(0, 45, 3)]
    indexed = Image.new('P', native.size, 0)
    indexed.putpalette([value for color in colors for value in color] + [0] * 720)
    indexed.putdata([min(range(1, 16), key=lambda i: sum((rgb[c] - colors[i][c]) ** 2
                                                      for c in range(3))) for rgb in native.get_flattened_data()])
    indexed.save(directory / 'native-atlas.png', bits=4)
    cells = [indexed.crop((column * 16, row * 16, column * 16 + 16, row * 16 + 16)).tobytes()
             for row in range(4) for column in range(4)]
    palette = b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c)
                                            for c in range(3))) for rgb in colors)
    waves = b''.join(pack4(tiles8(cells[index], 16, 16, 2, 2))
                     for pair in WAVE_CELLS for index in pair)
    if len({waves[i:i + 256] for i in range(0, 768, 256)}) != 3:
        raise ValueError('All three coastal wave stages must remain distinct at native scale.')
    files = {'tiles.indices': b''.join(cells), 'terrain.gbapal': palette, 'waves.4bpp': waves}
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'source_size': list(source.size), 'native_size': [64, 64], 'palette_bank': PALETTE_BANK,
        'wave_tile_start': WAVE_TILE_START, 'wave_tiles': 8, 'wave_frames': 3,
        'wave_frame_bytes': 256, 'wave_cadence_frames': 16,
        'quality_approval': 'pending', 'files': {
            name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    }, indent=2) + '\n')


def load_terrain(root):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    files = {name: (directory / name).read_bytes() for name in metadata['files']}
    if hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest() != metadata['source_sha256'] or \
       any(hashlib.sha256(data).hexdigest() != metadata['files'][name] for name, data in files.items()):
        raise ValueError('Regenerate coastal terrain after changing its source.')
    pixels = files['tiles.indices']
    if len(pixels) != 4096 or not all(1 <= value <= 15 for value in pixels) or \
       len(files['terrain.gbapal']) != 32 or len(files['waves.4bpp']) != 768:
        raise ValueError('Coastal art needs sixteen opaque cells, one palette and three wave stages.')
    return [rotate_pixels(pixels[index * 256:(index + 1) * 256], turns)
            for index, turns in VARIANTS], files['terrain.gbapal'], files['waves.4bpp']


def terrain_variant(plan, x, y):
    token = plan['rows'][y][x]
    if token == '.':
        return (0, 12, 13)[(x * 17 + y * 11) % 3]
    if token in 'WESG#':
        return {'W': 2, 'E': 3, 'S': 1, 'G': 4, '#': 8}[token]
    if token != 'F':
        raise ValueError('Terrain selector only accepts coastal ground tokens.')
    last_x, last_y = len(plan['rows'][0]) - 1, len(plan['rows']) - 1
    if x == last_x and y == 0:
        return 16  # East edge bends south.
    if x == last_x and y == last_y:
        return 17  # East edge bends north.
    return 6 if x == last_x else 5


def remap_terrain(plan, blocks):
    width = len(plan['rows'][0])
    if len(blocks) != width * len(plan['rows']) * 2:
        raise ValueError('Coastal block data must match the authored map.')
    output, counts = bytearray(blocks), {}
    for y, row in enumerate(plan['rows']):
        for x, token in enumerate(row):
            if token not in TOKENS:
                continue
            offset = (y * width + x) * 2
            word = struct.unpack_from('<H', blocks, offset)[0]
            if word & 0x3ff != plan['legend'][token][0]:
                raise ValueError('Terrain overlay must start from authored native IDs.')
            variant = terrain_variant(plan, x, y)
            struct.pack_into('<H', output, offset, (word & 0xfc00) | (512 + FIRST_METATILE + variant))
            counts[variant] = counts.get(variant, 0) + 1
    return bytes(output), counts


def apply_coastal_animation(root, engine, original):
    # Eight reserved secondary tiles are isolated from static-art deduplication.
    _, _, waves = load_terrain(root)
    destination = engine / 'data/tilesets/secondary/petalburg/sf_coast_waves.4bpp'
    destination.write_bytes(waves)
    path = 'src/tileset_anims.c'
    source = original(path)
    anchor = '''void InitTilesetAnim_Petalburg(void)
{
    sSecondaryTilesetAnimCounter = 0;
    sSecondaryTilesetAnimCounterMax = sPrimaryTilesetAnimCounterMax;
    sSecondaryTilesetAnimCallback = NULL;
}'''
    if source.count(anchor) != 1:
        raise ValueError('Pinned secondary animation initializer changed; inspect before integrating.')
    replacement = '''static const u16 sSFCoastalWaves[] = INCBIN_U16("data/tilesets/secondary/petalburg/sf_coast_waves.4bpp");

static void TilesetAnim_SFCoast(u16 timer)
{
    if (timer % 16 == 0)
        AppendTilesetAnimToBuffer(sSFCoastalWaves + (timer / 16) * 128,
            (u16 *)(BG_VRAM + TILE_OFFSET_4BPP(NUM_TILES_IN_PRIMARY + 240)), 8 * TILE_SIZE_4BPP);
}

void InitTilesetAnim_Petalburg(void)
{
    sSecondaryTilesetAnimCounter = 0;
    sSecondaryTilesetAnimCounterMax = 48;
    sSecondaryTilesetAnimCallback = TilesetAnim_SFCoast;
}'''
    (engine / path).write_text(source.replace(anchor, replacement))
    # Extend only the displayed camera margin, preserving physical map borders.
    camera_path = 'src/field_camera.c'
    camera = (engine / camera_path).read_text()  # Keep the earlier doorway hook.
    marker = '    u16 metatileId = MapGridGetMetatileIdAt(x, y);\n    const u16 *metatiles;'
    draw = 'DrawMetatile(MapGridGetMetatileLayerTypeAt(x, y), metatiles + metatileId * NUM_TILES_PER_METATILE, offset);'
    if camera.count(marker) != 1 or camera.count(draw) != 1:
        raise ValueError('Pinned camera margin hook changed; inspect before integrating.')
    camera = camera.replace('#include "constants/maps.h"',
                            '#include "constants/maps.h"\n#include "sf_coastal_border.h"')
    camera = camera.replace(marker, marker + '''
    u8 layerType = MapGridGetMetatileLayerTypeAt(x, y);
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_LITTLEROOT_TOWN)
     && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_LITTLEROOT_TOWN))
    {
        int sfBorder = SFCoastalBorderGraphic(x, y, mapLayout->width, mapLayout->height);
        if (sfBorder >= 0)
        {
            metatileId = sfBorder;
            layerType = METATILE_LAYER_TYPE_NORMAL;
        }
    }''')
    camera = camera.replace(draw, 'DrawMetatile(layerType, metatiles + metatileId * NUM_TILES_PER_METATILE, offset);')
    (engine / camera_path).write_text(camera)
    shutil.copy2(root / 'romhack/engine/coastal_border.h', engine / 'src/sf_coastal_border.h')
    return [path, camera_path]


if __name__ == '__main__':
    encode_terrain(Path(__file__).resolve().parents[2])
