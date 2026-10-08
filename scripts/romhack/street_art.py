"""Original native street textures and adjacency-based SF road rendering."""
import hashlib
import json
from pathlib import Path
import struct

ASSET = 'assets/tiles/sunset-streets'
FIRST_METATILE = 40
# Source tile and clockwise quarter-turns. Native variants use one palette bank.
VARIANTS = ((0, 0), (1, 0), (1, 1), (1, 2), (1, 3),
            (2, 0), (2, 1), (2, 2), (2, 3),
            (3, 0), (3, 1), (3, 2), (3, 3),
            (4, 0), (4, 1), (5, 0), (6, 0), (7, 0))
EDGE_VARIANTS = {0: 0, 1: 1, 2: 2, 4: 3, 8: 4, 9: 5, 3: 6, 6: 7, 12: 8}


def rotate_pixels(pixels, turns):
    if len(pixels) != 256 or turns not in range(4):
        raise ValueError('Street orientation needs a 16x16 native cell and zero to three turns.')
    for _ in range(turns):
        pixels = bytes(pixels[(15 - x) * 16 + y] for y in range(16) for x in range(16))
    return pixels


def encode_streets(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGB')
    native = Image.new('RGB', (64, 32))
    for row in range(2):
        for column in range(4):
            box = (round(column * source.width / 4), round(row * source.height / 2),
                   round((column + 1) * source.width / 4), round((row + 1) * source.height / 2))
            native.paste(source.crop(box).resize((16, 16), Image.Resampling.NEAREST), (column * 16, row * 16))
    palette = native.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in palette[i:i + 3])
                           for i in range(0, 45, 3)]
    indexed = Image.new('P', (64, 32), 0)
    indexed.putpalette([c for color in colors for c in color] + [0] * 720)
    indexed.putdata([min(range(1, 16), key=lambda i: sum((rgb[c] - colors[i][c]) ** 2
                                                      for c in range(3))) for rgb in native.get_flattened_data()])
    indexed.save(directory / 'native-atlas.png', bits=4)
    pixels = b''.join(indexed.crop((column * 16, row * 16, column * 16 + 16, row * 16 + 16)).tobytes()
                      for row in range(2) for column in range(4))
    native_palette = b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c)
                                                 for c in range(3))) for rgb in colors)
    files = {'tiles.indices': pixels, 'street.gbapal': native_palette}
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'source_size': list(source.size), 'native_size': [64, 32], 'palette_bank': 11,
        'source_tiles': ['asphalt', 'north curb', 'outer northwest corner', 'inner northwest corner',
                         'horizontal double yellow', 'crossing paint', 'sidewalk', 'drain'],
        'variants': VARIANTS, 'quality_approval': 'pending',
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    }, indent=2) + '\n')


def load_streets(root):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    files = {name: (directory / name).read_bytes() for name in metadata['files']}
    if any(hashlib.sha256(data).hexdigest() != metadata['files'][name] for name, data in files.items()) or \
       hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest() != metadata['source_sha256']:
        raise ValueError('Regenerate original street resources after changing their source.')
    pixels = files['tiles.indices']
    if len(pixels) != 2048 or not all(1 <= value <= 15 for value in pixels) or len(files['street.gbapal']) != 32:
        raise ValueError('Street art needs eight opaque native tiles and sixteen palette entries.')
    return [rotate_pixels(pixels[index * 256:(index + 1) * 256], turns)
            for index, turns in VARIANTS], files['street.gbapal']


def road_edge_variant(plan, x, y, tokens='P#'):
    rows = plan['rows']
    is_road = lambda nx, ny: 0 <= ny < len(rows) and 0 <= nx < len(rows[0]) and rows[ny][nx] in tokens
    mask = sum(bit for dx, dy, bit in ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8))
               if not is_road(x + dx, y + dy))
    if mask not in EDGE_VARIANTS:
        raise ValueError(f'Unsupported street width/corner at {x},{y}.')
    if mask:
        return EDGE_VARIANTS[mask]
    corners = [index for dx, dy, index in ((-1, -1, 9), (1, -1, 10), (1, 1, 11), (-1, 1, 12))
               if not is_road(x + dx, y + dy)]
    if len(corners) > 1:
        raise ValueError(f'Review a multi-corner street junction at {x},{y}.')
    if corners:
        return corners[0]
    return 0


def road_variant(plan, x, y):
    edge = road_edge_variant(plan, x, y)
    if edge:
        return edge
    if (x, y) in ((10, 8), (10, 24)):
        return 17
    if x in (17, 27) and y in (17, 22):
        return 15
    if y in (17, 22) and x not in (9, 10, 11, 18, 19, 28, 29):
        return 13
    if x == 10 and y not in (16, 17, 18, 21, 22, 23):
        return 14
    return 0


def remap_roads(plan, blocks):
    width = len(plan['rows'][0])
    if len(blocks) != width * len(plan['rows']) * 2:
        raise ValueError('Road block array must match the authored map dimensions.')
    output, counts = bytearray(blocks), {}
    for y, row in enumerate(plan['rows']):
        for x, token in enumerate(row):
            if token != 'P':
                continue
            address = (y * width + x) * 2
            word = struct.unpack_from('<H', blocks, address)[0]
            if word & 0x3ff != 513:
                raise ValueError('Road overlay must start from the authored road ID.')
            variant = road_variant(plan, x, y)
            struct.pack_into('<H', output, address, (word & 0xfc00) | (512 + FIRST_METATILE + variant))
            counts[variant] = counts.get(variant, 0) + 1
    return bytes(output), counts


if __name__ == '__main__':
    encode_streets(Path(__file__).resolve().parents[2])
