"""Original South Park facade conversion and bounded native tileset packing."""
import hashlib
import json
from pathlib import Path
import struct
from street_art import load_streets, rotate_pixels, road_edge_variant
from terrain_art import load_terrain
from title_art import tiles8
from title_creature import pack4

ASSET = 'assets/tiles/south-park-buildings'


def encode_buildings(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    frames, palettes = [], []
    for index, name in enumerate(('warehouse', 'clinic')):
        box = (round(index * source.width / 2), 0, round((index + 1) * source.width / 2), source.height)
        cell = source.crop(box).resize((112, 80), Image.Resampling.NEAREST)
        visible = [rgb[:3] for rgb in cell.get_flattened_data() if rgb[3] >= 128]
        if not visible:
            raise ValueError('Both SF facades must have visible architecture.')
        samples = Image.new('RGB', (len(visible), 1)); samples.putdata(visible)
        values = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
        colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in values[i:i + 3])
                               for i in range(0, 45, 3)]
        image = Image.new('P', (112, 80), 0)
        image.putpalette([c for color in colors for c in color] + [0] * 720)
        pixels = bytes(0 if rgba[3] < 128 else min(range(1, 16),
            key=lambda i: sum((rgba[c] - colors[i][c]) ** 2 for c in range(3)))
            for rgba in cell.get_flattened_data())
        image.putdata(pixels); image.save(directory / (name + '.png'), transparency=0, bits=4)
        frames.append(pixels)
        palettes.append(b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c)
                                                      for c in range(3))) for rgb in colors))
    files = {'buildings.indices': b''.join(frames), 'building-palettes.gbapal': b''.join(palettes)}
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'native_frame_size': [112, 80], 'frames': 2, 'palette_banks': [8, 9],
        'quality_approval': 'pending', 'files': {
            name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    }, indent=2) + '\n')


def load_buildings(root):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    files = {name: (directory / name).read_bytes() for name in metadata['files']}
    if hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest() != metadata['source_sha256'] or \
       any(hashlib.sha256(data).hexdigest() != metadata['files'][name] for name, data in files.items()):
        raise ValueError('Regenerate SF institutional facades after changing art.')
    data, palettes = files['buildings.indices'], files['building-palettes.gbapal']
    if len(data) != 17920 or len(palettes) != 64 or max(data) > 15:
        raise ValueError('Two 112x80 four-bit facades and two native palettes are required.')
    return [data[:8960], data[8960:]], [palettes[:32], palettes[32:]]


def pack_park_cells(cells, attributes):
    """Every cell chooses a palette; ground uses BG2 and architecture uses BG1."""
    if len(cells) != len(attributes) or len(cells) > 512:
        raise ValueError('Native cell/attribute allocations must agree and fit a tileset.')
    raw, records, pool = bytearray(), bytearray(), {}
    for pixels, bank in cells:
        if len(pixels) != 256 or max(pixels) > 15 or bank not in range(6, 13):
            raise ValueError('Park cells need 16x16 four-bit pixels and a secondary palette bank.')
        encoded = pack4(tiles8(pixels, 16, 16, 2, 2))
        quadrants = []
        for offset in range(0, 128, 32):
            tile = encoded[offset:offset + 32]
            if tile not in pool:
                if len(pool) == 512:
                    raise ValueError('Original South Park art exceeds secondary VRAM capacity.')
                pool[tile] = len(pool); raw.extend(tile)
            quadrants.append((bank << 12) | (512 + pool[tile]))
        records.extend(struct.pack('<8H', 0, 0, 0, 0, *quadrants))
    return bytes(raw), bytes(records), struct.pack('<' + 'H' * len(attributes), *attributes)


def facade_cells(pixels, width, height, bank):
    if len(pixels) != width * height or width % 16 or height % 16:
        raise ValueError('Facade dimensions must match native metatile boundaries.')
    return [(b''.join(pixels[y * width + x:y * width + x + 16]
                      for y in range(top, top + 16)), bank)
            for top in range(0, height, 16) for x in range(0, width, 16)]


def encode_furniture(root):
    from PIL import Image
    directory = root / 'assets/tiles/south-park-furniture'
    source = Image.open(directory / 'source.png').convert('RGB')
    palette_bytes = (root / 'assets/tiles/sunset-terrain/terrain.gbapal').read_bytes()
    colors = [tuple(((word >> (5 * c)) & 31) * 255 // 31 for c in range(3))
              for word in struct.unpack('<16H', palette_bytes)]
    native = Image.new('P', (48, 16), 0)
    native.putpalette([value for color in colors for value in color] + [0] * 720)
    cells = []
    for index in range(3):
        image = source.crop((round(index * source.width / 3), 0,
                             round((index + 1) * source.width / 3), source.height))
        image = image.resize((16, 16), Image.Resampling.NEAREST)
        pixels = bytes(min(range(1, 16), key=lambda i: sum((rgb[c] - colors[i][c]) ** 2
                                                        for c in range(3))) for rgb in image.get_flattened_data())
        cell = Image.new('P', (16, 16), 0); cell.putpalette(native.getpalette()); cell.putdata(pixels)
        native.paste(cell, (index * 16, 0)); cells.append(pixels)
    native.save(directory / 'native-atlas.png', bits=4)
    data = b''.join(cells); (directory / 'furniture.indices').write_bytes(data)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'palette_sha256': hashlib.sha256(palette_bytes).hexdigest(),
        'native_cells': ['bench', 'planter', 'information board'], 'palette_bank': 7,
        'indices_sha256': hashlib.sha256(data).hexdigest(), 'quality_approval': 'pending'
    }, indent=2) + '\n')


if __name__ == '__main__':
    encode_buildings(Path(__file__).resolve().parents[2])
    encode_furniture(Path(__file__).resolve().parents[2])
