"""Original architectural variants share the existing Sunset collision footprints."""
import hashlib
import json
import struct
from pathlib import Path
from house_art import encode_house

STYLES = (
    ('butter', 'assets/tiles/sunset-rowhouse-butter', 144, 13),
    ('lavender', 'assets/tiles/sunset-rowhouse-lavender', 169, 14),
)
METATILE_COUNT = 194
TILE_COUNT = 512
# Keep the enterable apartment at13,4 on its existing animated facade.
PLACEMENTS = {(19, 4): 'butter', (13, 25): 'butter',
              (19, 10): 'lavender', (19, 25): 'lavender'}


def encode_variants(root):
    for _, asset, _, bank in STYLES:
        encode_house(root, asset, bank)
        directory = root / asset
        path = directory / 'conversion.json'
        metadata = json.loads(path.read_text())
        metadata['files']['native-preview.png'] = hashlib.sha256(
            (directory / 'native-preview.png').read_bytes()).hexdigest()
        path.write_text(json.dumps(metadata, indent=2) + '\n')


def load_variants(root):
    variants = []
    for name, asset, first, bank in STYLES:
        directory = root / asset
        metadata = json.loads((directory / 'conversion.json').read_text())
        expected = {'house.4bpp', 'house.gbapal', 'native-preview.png'}
        if set(metadata['files']) != expected or metadata['palette_bank'] != bank:
            raise ValueError('Variant must declare its consumed native files and palette bank.')
        for filename, digest in [('source.png', metadata['source_sha256']),
                                  *metadata['files'].items()]:
            if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != digest:
                raise ValueError('Regenerate original facade variant after asset changes.')
        graphics = (directory / 'house.4bpp').read_bytes()
        palette = (directory / 'house.gbapal').read_bytes()
        if len(graphics) != 3200 or len(palette) != 32:
            raise ValueError('Variant needs one80x80 four-bit facade and16 native colors.')
        if any(word > 0x7fff for word in struct.unpack('<16H', palette)):
            raise ValueError('Facade palette exceeds native RGB555.')
        variants.append({'name': name, 'first': first, 'bank': bank,
                         'graphics': graphics, 'palette': palette})
    return variants


def facade_placements(plan, origins, variants):
    names = {variant['name']: variant['first'] for variant in variants}
    available = {tuple(origin) for origin in origins}
    warps = {(warp['x'], warp['y']) for warp in plan.get('warp_events', [])}
    result = {}
    for origin, name in PLACEMENTS.items():
        if origin not in available or name not in names:
            raise ValueError('Review facade placements when changing the residential layout.')
        x, y = origin
        if any(x <= wx < x + 5 and y <= wy < y + 5 for wx, wy in warps):
            raise ValueError('Decorative variants cannot replace an animated enterable facade.')
        result[origin] = names[name]
    return result


if __name__ == '__main__':
    encode_variants(Path(__file__).resolve().parents[2])
