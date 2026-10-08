"""Original Sunset facade tiles; mixed inherited sheets never leave private builds."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import uuid
from maps import encode_layout
from native_resources import apply_resources, named_addresses, bounded_span
from title_art import tiles8
from title_creature import pack4

ASSET = 'assets/tiles/sunset-rowhouse'
STEMS = ('gTilesetTiles_Petalburg', 'gTilesetPalettes_Petalburg',
         'gMetatiles_Petalburg', 'gMetatileAttributes_Petalburg')
HOUSE_ROWS = ('abbbe', 'fgggh', 'ijjjk', 'lmnor', 'stuvw')
ROAD_TILES = {80, 81, 96, 97}
FIRST_METATILE = 100


def encode_house(root):
    # Only crop, nearest resampling, RGB555 quantization and native serialization.
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    mask = source.getchannel('A').point(lambda alpha: 255 if alpha >= 128 else 0)
    bounds = mask.getbbox()
    if not bounds:
        raise ValueError('Rowhouse source must have visible architecture.')
    cell, mask = source.crop(bounds), mask.crop(bounds)
    scale = min(78 / cell.width, 78 / cell.height)
    size = (round(cell.width * scale), round(cell.height * scale))
    cell, mask = (image.resize(size, Image.Resampling.NEAREST) for image in (cell, mask))
    visible = [rgb[:3] for rgb, alpha in zip(cell.get_flattened_data(), mask.get_flattened_data()) if alpha]
    samples = Image.new('RGB', (len(visible), 1)); samples.putdata(visible)
    palette = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in palette[i:i + 3])
                           for i in range(0, 45, 3)]
    image = Image.new('P', (80, 80), 0)
    image.putpalette([c for color in colors for c in color] + [0] * 720)
    left, top = ((80 - dimension) // 2 for dimension in size)
    for y in range(size[1]):
        for x in range(size[0]):
            if mask.getpixel((x, y)):
                rgb = cell.getpixel((x, y))[:3]
                index = min(range(1, 16), key=lambda i: sum((rgb[c] - colors[i][c]) ** 2 for c in range(3)))
                image.putpixel((x + left, y + top), index)
    image.save(directory / 'native-preview.png', transparency=0, bits=4)
    graphics = pack4(tiles8(bytes(image.get_flattened_data()), 80, 80, 10, 10))
    palette = b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c)
                                           for c in range(3))) for rgb in colors)
    files = {'house.4bpp': graphics, 'house.gbapal': palette}
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_size': list(source.size), 'alpha_bounds': list(bounds), 'native_size': [80, 80],
        'visible_size': list(size), 'palette_bank': 10, 'quality_approval': 'pending',
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    }, indent=2) + '\n')


def remap_houses(plan, original):
    width, height, expected = encode_layout(plan)
    if (width, height) != (32, 32) or original != expected:
        raise ValueError('Sunset block data no longer matches its authored map.')
    output, origins = bytearray(original), []
    for y in range(height - 4):
        for x in range(width - 4):
            if all(plan['rows'][y + dy][x:x + 5] == row for dy, row in enumerate(HOUSE_ROWS)):
                origins.append([x, y])
                for dy in range(5):
                    for dx in range(5):
                        address = ((y + dy) * width + x + dx) * 2
                        word = struct.unpack_from('<H', original, address)[0]
                        struct.pack_into('<H', output, address, (word & 0xfc00) |
                                         (512 + FIRST_METATILE + dy * 5 + dx))
    if len(origins) != 6:
        raise ValueError('Review facade footprints when changing the Sunset layout.')
    return bytes(output), origins


def compose_tiles(original, owned, metatiles):
    if len(original) != 159 * 32 or len(owned) != 100 * 32 or len(metatiles) != 144 * 16:
        raise ValueError('Pinned secondary tiles/metatiles allocation changed.')
    # Preserve the actual road quadrants, including flip and palette flags.
    if struct.unpack_from('<8H', metatiles, 16) != (0x2002, 0x2003, 0x2003, 0x2002,
                                                  0x5250, 0x5251, 0x5260, 0x5261):
        raise ValueError('Review secondary road references before changing its tile pool.')
    tiles, mapping, unique = bytearray(len(original)), [], {}
    for index in ROAD_TILES:
        tiles[index * 32:index * 32 + 32] = original[index * 32:index * 32 + 32]
    pool = iter(index for index in range(159) if index not in ROAD_TILES)
    for start in range(0, len(owned), 32):
        tile = owned[start:start + 32]
        if tile not in unique:
            index = next(pool)
            unique[tile] = index
            tiles[index * 32:index * 32 + 32] = tile
        mapping.append(unique[tile])
    records = bytearray(metatiles)
    for y in range(5):
        for x in range(5):
            top = y * 20 + x * 2
            quadrants = [0xa200 | mapping[top + delta] for delta in (0, 1, 10, 11)]
            struct.pack_into('<8H', records, (FIRST_METATILE + y * 5 + x) * 16,
                             0x2002, 0x2003, 0x2003, 0x2002, *quadrants)
    return bytes(tiles), bytes(records), len(unique)


def apply_house_art(root, emerald, target):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    files = {name: (directory / name).read_bytes() for name in metadata['files']}
    if any(hashlib.sha256(data).hexdigest() != metadata['files'][name] for name, data in files.items()) or \
       hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest() != metadata['source_sha256']:
        raise ValueError('Regenerate native house assets after changing their source.')
    work = root / '.tools' / ('house-art-' + uuid.uuid4().hex)
    work.mkdir()
    elf = emerald / 'sf-engine-probe.elf'
    names = set(STEMS) | {'gTileset_Petalburg', 'gTileset_General', 'LittlerootTown_Layout',
                         'LittlerootTown_Layout_Blockdata'}
    addresses = named_addresses(elf, names)
    linked_path, codec = work / 'linked.bin', work / 'native-lz'
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', str(elf), str(linked_path)], check=True)
    linked = linked_path.read_bytes()
    layout = addresses['LittlerootTown_Layout'] - 0x08000000
    if struct.unpack_from('<6I', linked, layout)[0:2] != (32, 32) or \
       struct.unpack_from('<6I', linked, layout)[3:] != (addresses['LittlerootTown_Layout_Blockdata'],
           addresses['gTileset_General'], addresses['gTileset_Petalburg']):
        raise ValueError('Sunset must use the declared 32x32 layout and tilesets.')
    source = emerald / 'tools/gbagfx'
    subprocess.run(['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(source),
        str(root / 'scripts/romhack/native_lz.c'), str(source / 'lz.c'), '-o', str(codec)], check=True)
    # Native tables are adjacent; validate capacities again through apply_resources.
    read = lambda name, size: linked[addresses[name] - 0x08000000:addresses[name] - 0x08000000 + size]
    packed, raw = work / 'original.lz', work / 'original.4bpp'
    packed.write_bytes(read(STEMS[0], 2300))
    subprocess.run([str(codec), 'decode', str(packed), str(raw)], check=True)
    graphics, records, unique = compose_tiles(raw.read_bytes(), files['house.4bpp'], read(STEMS[2], 2304))
    palette, attributes = bytearray(read(STEMS[1], 512)), bytearray(read(STEMS[3], 288))
    if len(files['house.gbapal']) != 32:
        raise ValueError('House palette must contain exactly sixteen native colors.')
    palette[320:352] = files['house.gbapal']
    attributes[FIRST_METATILE * 2:(FIRST_METATILE + 25) * 2] = bytes(50)
    offset, capacity = bounded_span(addresses, 'LittlerootTown_Layout_Blockdata', 'LittlerootTown_Layout')
    plan = json.loads((root / 'romhack/content/sunset.json').read_text())
    house_tokens = set(''.join(HOUSE_ROWS))
    if any(tile >= 512 and token not in house_tokens | {'P'}
           for token, (tile, _, _) in plan['legend'].items()):
        raise ValueError('Review all Sunset secondary references before replacing unused tiles.')
    layouts = json.loads((emerald / 'data/layouts/layouts.json').read_text())['layouts']
    for name in json.loads((root / 'romhack/content/engine-probe.json').read_text())['maps']:
        other = json.loads((root / 'romhack/content' / name).read_text())
        layout = next(entry for entry in layouts if entry['name'] == other['engine_map'] + '_Layout')
        if other['engine_map'] != plan['engine_map'] and layout['secondary_tileset'] == 'gTileset_Petalburg':
            raise ValueError('A second active SF map shares the facade tileset; review its references.')
    blocks, origins = remap_houses(plan, linked[offset:offset + capacity])
    resources = [{'symbol': name, 'data': data, 'compressed': index == 0}
                 for index, (name, data) in enumerate(zip(STEMS, (graphics, bytes(palette), records, bytes(attributes))))]
    resources.append({'symbol': 'LittlerootTown_Layout_Blockdata',
                      'end_symbol': 'LittlerootTown_Layout', 'data': blocks})
    return {'resources': apply_resources(root, emerald, target, resources), 'origins': origins,
            'unique_tiles': unique, 'native_size': [80, 80], 'collision_elevation_preserved': True,
            'interiors_implemented': False, 'quality_approval': 'pending'}


if __name__ == '__main__':
    encode_house(Path(__file__).resolve().parents[2])
