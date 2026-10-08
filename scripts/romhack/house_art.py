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
from street_art import load_streets, remap_roads, FIRST_METATILE as FIRST_ROAD
from terrain_art import load_terrain, remap_terrain, FIRST_METATILE as FIRST_TERRAIN, WAVE_TILE_START

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
            if all(plan['rows'][y + dy][x:x + 5].replace('D', 'v') == row for dy, row in enumerate(HOUSE_ROWS)):
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


def compose_tiles(original, owned, metatiles, streets=None, terrain=None):
    count = 256 if terrain is not None else (192 if streets is not None else 159)
    if len(original) != count * 32 or len(owned) != 100 * 32 or len(metatiles) != 144 * 16:
        raise ValueError('Pinned secondary tiles/metatiles allocation changed.')
    # Preserve the actual road quadrants, including flip and palette flags.
    if struct.unpack_from('<8H', metatiles, 16) != (0x2002, 0x2003, 0x2003, 0x2002,
                                                  0x5250, 0x5251, 0x5260, 0x5261):
        raise ValueError('Review secondary road references before changing its tile pool.')
    tiles, mapping, unique = bytearray(len(original)), [], {}
    reserved = ROAD_TILES if streets is None else set()
    if terrain is not None:
        reserved = set(range(WAVE_TILE_START, WAVE_TILE_START + 8))
    for index in reserved:
        tiles[index * 32:index * 32 + 32] = original[index * 32:index * 32 + 32]
    pool = iter(index for index in range(count) if index not in reserved)
    def allocate(tile):
        if tile not in unique:
            try:
                index = next(pool)
            except StopIteration:
                raise ValueError('Original SF tiles exceed their declared secondary tile count.') from None
            unique[tile] = index
            tiles[index * 32:index * 32 + 32] = tile
        return unique[tile]
    for start in range(0, len(owned), 32):
        tile = owned[start:start + 32]
        mapping.append(allocate(tile))
    records = bytearray(metatiles)
    for y in range(5):
        for x in range(5):
            top = y * 20 + x * 2
            quadrants = [0xa200 | mapping[top + delta] for delta in (0, 1, 10, 11)]
            struct.pack_into('<8H', records, (FIRST_METATILE + y * 5 + x) * 16,
                             0x2002, 0x2003, 0x2003, 0x2002, *quadrants)
    if streets is not None:
        if FIRST_ROAD + len(streets) > FIRST_METATILE or any(len(cell) != 256 for cell in streets):
            raise ValueError('Street records overlap houses or have an invalid native cell size.')
        for index, cell in enumerate(streets):
            raw = pack4(tiles8(cell, 16, 16, 2, 2))
            quadrants = [0xb200 | allocate(raw[start:start + 32]) for start in range(0, 128, 32)]
            struct.pack_into('<8H', records, (FIRST_ROAD + index) * 16,
                             0x2002, 0x2003, 0x2003, 0x2002, *quadrants)
        # Older map-view buffers may still contain P=513 until refreshed on resume.
        records[16:32] = records[FIRST_ROAD * 16:(FIRST_ROAD + 1) * 16]
    if terrain is not None:
        if streets is None or len(terrain) != 19 or FIRST_TERRAIN + len(terrain) > FIRST_METATILE:
            raise ValueError('Coastal records need their own range between streets and houses.')
        for index, cell in enumerate(terrain):
            if index in (10, 11, 14, 15):
                continue  # These are animation stages, not static map records.
            raw = pack4(tiles8(cell, 16, 16, 2, 2))
            if index in (2, 3):
                slot = WAVE_TILE_START + (index - 2) * 4
                tiles[slot * 32:(slot + 4) * 32] = raw
                slots = range(slot, slot + 4)
            else:
                slots = [allocate(raw[start:start + 32]) for start in range(0, 128, 32)]
            quadrants = [0xc200 | slot for slot in slots]
            struct.pack_into('<8H', records, (FIRST_TERRAIN + index) * 16,
                             0, 0, 0, 0, *quadrants)
        # Transparent facade margins use original SF lawn rather than inherited grass.
        grass = struct.unpack_from('<4H', records, FIRST_TERRAIN * 16 + 8)
        for index in range(FIRST_METATILE, FIRST_METATILE + 25):
            struct.pack_into('<4H', records, index * 16, *grass)
    return bytes(tiles), bytes(records), len(unique) + (8 if terrain is not None else 0)


def prepare_sunset_tiles(root, emerald, original):
    from PIL import Image
    variants, _ = load_streets(root)
    terrain, _, _ = load_terrain(root)
    records = (emerald / 'data/tilesets/secondary/petalburg/metatiles.bin').read_bytes()
    graphics, _, unique = compose_tiles(bytes(256 * 32), (root / ASSET / 'house.4bpp').read_bytes(), records, variants, terrain)
    # Indexed PNG is a native build input. RGB palette selection is in metatiles.
    image = Image.new('P', (128, 128), 0)
    image.putpalette(Image.open(root / ASSET / 'native-preview.png').getpalette())
    for tile in range(256):
        for y in range(8):
            for x in range(8):
                byte = graphics[tile * 32 + y * 4 + x // 2]
                image.putpixel((tile % 16 * 8 + x, tile // 16 * 8 + y), (byte >> ((x % 2) * 4)) & 15)
    path = 'data/tilesets/secondary/petalburg/tiles.png'
    image.save(emerald / path, transparency=0, bits=4)
    header = 'src/data/tilesets/graphics.h'
    source = original(header)
    line = 'const u32 gTilesetTiles_Petalburg[] = INCGFX_U32("data/tilesets/secondary/petalburg/tiles.png", ".4bpp.lz", "-num_tiles 159 -Wnum_tiles");'
    if source.count(line) != 1:
        raise ValueError('Pinned native tileset compilation declaration changed.')
    (emerald / header).write_text(source.replace(line, line.replace('159', '256'), 1))
    if unique > 256:
        raise ValueError('Original SF sheet exceeds the native tile allocation.')
    return [path, header]


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
    # The complete owned sheet receives its allocation through normal compilation.
    from interface_text import symbols_from_nm
    slots = symbols_from_nm(subprocess.check_output(['arm-none-eabi-nm', '-S', '--defined-only',
        str(elf)], text=True), {STEMS[0]})
    packed.write_bytes(read(STEMS[0], slots[STEMS[0]][1]))
    subprocess.run([str(codec), 'decode', str(packed), str(raw)], check=True)
    streets, street_palette = load_streets(root)
    terrain, terrain_palette, _ = load_terrain(root)
    graphics, records, unique = compose_tiles(raw.read_bytes(), files['house.4bpp'], read(STEMS[2], 2304), streets, terrain)
    palette, attributes = bytearray(read(STEMS[1], 512)), bytearray(read(STEMS[3], 288))
    if len(files['house.gbapal']) != 32:
        raise ValueError('House palette must contain exactly sixteen native colors.')
    palette[320:352] = files['house.gbapal']
    palette[352:384] = street_palette
    palette[384:416] = terrain_palette
    attributes[FIRST_METATILE * 2:(FIRST_METATILE + 25) * 2] = bytes(50)
    attributes[123 * 2:124 * 2] = struct.pack('<H', 0x69)  # Native animated door; original SF frames.
    for index in range(FIRST_ROAD, FIRST_ROAD + len(streets)):
        attributes[index * 2:index * 2 + 2] = attributes[2:4]
    # Normal ground/rail/sign cells; sand footprints, ocean and encounters stay native.
    attributes[FIRST_TERRAIN * 2:(FIRST_TERRAIN + 19) * 2] = bytes(38)
    for index, behavior in ((1, 0x21), (2, 0x15), (4, 0x02)):
        struct.pack_into('<H', attributes, (FIRST_TERRAIN + index) * 2, behavior)
    offset, capacity = bounded_span(addresses, 'LittlerootTown_Layout_Blockdata', 'LittlerootTown_Layout')
    plan = json.loads((root / 'romhack/content/sunset.json').read_text())
    house_tokens = set(''.join(HOUSE_ROWS)) | {'D'}
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
    blocks, road_counts = remap_roads(plan, blocks)
    blocks, terrain_counts = remap_terrain(plan, blocks)
    resources = [{'symbol': name, 'data': data, 'compressed': index == 0}
                 for index, (name, data) in enumerate(zip(STEMS, (graphics, bytes(palette), records, bytes(attributes))))]
    resources.append({'symbol': 'LittlerootTown_Layout_Blockdata',
                      'end_symbol': 'LittlerootTown_Layout', 'data': blocks})
    return {'resources': apply_resources(root, emerald, target, resources), 'origins': origins,
            'unique_tiles': unique, 'native_size': [80, 80], 'collision_elevation_preserved': True,
            'street_variants': road_counts, 'terrain_variants': terrain_counts, 'secondary_tiles': 256,
            'enterable_apartment': True, 'decorative_houses': 5,
            'door_animation': 'three original stages; native opening/closing timing', 'quality_approval': 'pending'}


if __name__ == '__main__':
    encode_house(Path(__file__).resolve().parents[2])
