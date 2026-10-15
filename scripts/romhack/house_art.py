"""Original Sunset facade conversion and safe native tile allocation."""
import hashlib
import json
from pathlib import Path
import struct
from maps import encode_layout
from title_art import tiles8
from title_creature import pack4
from street_art import FIRST_METATILE as FIRST_ROAD
from terrain_art import FIRST_METATILE as FIRST_TERRAIN, WAVE_TILE_START

ASSET = 'assets/tiles/sunset-rowhouse'
STEMS = ('gTilesetTiles_Petalburg', 'gTilesetPalettes_Petalburg',
         'gMetatiles_Petalburg', 'gMetatileAttributes_Petalburg')
HOUSE_ROWS = ('abbbe', 'fgggh', 'ijjjk', 'lmnor', 'stuvw')
ROAD_TILES = {80, 81, 96, 97}
FIRST_METATILE = 100


def encode_house(root, asset=ASSET, palette_bank=10):
    # Only crop, nearest resampling, RGB555 quantization and native serialization.
    from PIL import Image
    directory = root / asset
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
        'visible_size': list(size), 'palette_bank': palette_bank, 'quality_approval': 'pending',
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    }, indent=2) + '\n')


def remap_houses(plan, original, placements=None):
    width, height, expected = encode_layout(plan)
    if (width, height) != (32, 32) or original != expected:
        raise ValueError('Sunset block data no longer matches its authored map.')
    output, origins = bytearray(original), []
    for y in range(height - 4):
        for x in range(width - 4):
            if all(plan['rows'][y + dy][x:x + 5].replace('D', 'v') == row for dy, row in enumerate(HOUSE_ROWS)):
                origins.append([x, y])
                first = (placements or {}).get((x, y), FIRST_METATILE)
                for dy in range(5):
                    for dx in range(5):
                        address = ((y + dy) * width + x + dx) * 2
                        word = struct.unpack_from('<H', original, address)[0]
                        struct.pack_into('<H', output, address, (word & 0xfc00) |
                                         (512 + first + dy * 5 + dx))
    if len(origins) != 6:
        raise ValueError('Review facade footprints when changing the Sunset layout.')
    if set(placements or {}) - {tuple(origin) for origin in origins}:
        raise ValueError('Variant placement must match an actual facade footprint.')
    return bytes(output), origins


def compose_tiles(original, owned, metatiles, streets=None, terrain=None, variants=None):
    count = 512 if variants else (256 if terrain is not None else (192 if streets is not None else 159))
    records_count = 194 if variants else 144
    if len(original) != count * 32 or len(owned) != 100 * 32 or len(metatiles) != records_count * 16:
        raise ValueError('Pinned secondary tiles/metatiles allocation changed.')
    # Preserve the actual road quadrants, including flip and palette flags.
    if struct.unpack_from('<8H', metatiles, 16) != (0x2002, 0x2003, 0x2003, 0x2002,
                                                  0x5250, 0x5251, 0x5260, 0x5261):
        raise ValueError('Review secondary road references before changing its tile pool.')
    tiles, unique = bytearray(len(original)), {}
    reserved = ROAD_TILES if streets is None else set()
    if terrain is not None:
        reserved = set(range(WAVE_TILE_START, WAVE_TILE_START + 8))
    if variants:
        reserved |= set(range(504, 512))  # Native animated-door scratch tiles.
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
    records = bytearray(metatiles)
    facades = [{'first': FIRST_METATILE, 'bank': 10, 'graphics': owned}, *(variants or [])]
    occupied = set()
    for facade in facades:
        first, bank, raw = facade['first'], facade['bank'], facade['graphics']
        if len(raw) != 3200 or not 100 <= first <= records_count - 25 or bank not in (6, 7, 10):
            raise ValueError('Invalid native facade allocation or palette bank.')
        slots = set(range(first, first + 25))
        if occupied & slots:
            raise ValueError('Facade metatile allocations overlap.')
        occupied |= slots
        mapping = [allocate(raw[start:start + 32]) for start in range(0, len(raw), 32)]
        for y in range(5):
            for x in range(5):
                top = y * 20 + x * 2
                quadrants = [(bank << 12) | 0x200 | mapping[top + delta] for delta in (0, 1, 10, 11)]
                struct.pack_into('<8H', records, (first + y * 5 + x) * 16,
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
        for facade in facades:
            for index in range(facade['first'], facade['first'] + 25):
                struct.pack_into('<4H', records, index * 16, *grass)
    return bytes(tiles), bytes(records), len(unique) + (8 if terrain is not None else 0)


def prepare_sunset_tiles(root, emerald, original):
    from sunset_compilation import prepare
    return prepare(root, emerald, original)


def owned_field_attributes(original):
    if len(original) not in (288, 388):
        raise ValueError('Native secondary attributes need144 or194 sixteen-bit records.')
    attributes = bytearray(original)
    # Walkable ground belongs below elevation-three field sprites, on BG2.
    for index in range(FIRST_ROAD, FIRST_ROAD + 18):
        struct.pack_into('<H', attributes, index * 2, 0x1000)
    for index in range(FIRST_TERRAIN, FIRST_TERRAIN + 19):
        struct.pack_into('<H', attributes, index * 2, 0x1000)
    for index, behavior in ((1, 0x21), (2, 0x15), (4, 0x02)):
        struct.pack_into('<H', attributes, (FIRST_TERRAIN + index) * 2, 0x1000 | behavior)
    # Upper walls stay foreground; the blocked front edge belongs behind actors
    # standing immediately south. Their 32px sprites extend into the row above.
    attributes[FIRST_METATILE * 2:(FIRST_METATILE + 25) * 2] = bytes(50)
    for index in range(FIRST_METATILE + 20, FIRST_METATILE + 25):
        struct.pack_into('<H', attributes, index * 2, 0x1000)
    struct.pack_into('<H', attributes, 123 * 2, 0x1069)
    if len(original) == 388:
        for first in (144, 169):
            for index in range(25):
                struct.pack_into('<H', attributes, (first + index) * 2, 0x1000 if index >= 20 else 0)
    return bytes(attributes)


def apply_house_art(root, emerald, target):
    from sunset_compilation import verify
    return verify(root, emerald, target)


if __name__ == '__main__':
    encode_house(Path(__file__).resolve().parents[2])
