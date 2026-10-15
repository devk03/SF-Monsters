"""Convert one original paving master without changing the shared street art."""
import hashlib
import json
from pathlib import Path
import struct

ASSET = 'assets/tiles/south-park-paving-v1'
PALETTE_SHA = 'c9056768a5543b99f664e5a21ae2aa609f84391b2dcd006f3c133fdb5c1c2b13'
FILES = ('master8.indices', 'paving.indices', 'paving.png')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def palette(root):
    raw = (root / 'assets/tiles/sunset-streets/street.gbapal').read_bytes()
    if len(raw) != 32 or sha(raw) != PALETTE_SHA:
        raise ValueError('Keep the original sixteen-color street palette unchanged.')
    return [tuple(((word >> (5*c)) & 31)*255//31 for c in range(3))
            for word in struct.unpack('<16H', raw)]


def repeated(master):
    if len(master) != 64 or set(master) != {1, 2} or master.count(1) < 48:
        raise ValueError('Use a bright opaque eight-pixel master with restrained joints.')
    return bytes(master[(y % 8)*8+x % 8] for y in range(16) for x in range(16))


def encode_paving(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGB')
    if source.width != source.height or not 8 <= source.width <= 8192:
        raise ValueError('Require one square, edge-to-edge original texture source.')
    colors = palette(root)
    samples = [source.getpixel(((2*x+1)*source.width//16,
                                (2*y+1)*source.height//16))
               for y in range(8) for x in range(8)]
    master = bytes(min((1, 2), key=lambda i: sum((rgb[c]-colors[i][c])**2
                                               for c in range(3))) for rgb in samples)
    pixels = repeated(master)
    image = Image.new('P', (16, 16))
    image.putpalette([c for color in colors for c in color] + [0]*720)
    image.putdata(pixels)
    image.save(directory / 'paving.png', bits=4)
    (directory / 'master8.indices').write_bytes(master)
    (directory / 'paving.indices').write_bytes(pixels)
    metadata = {'source_sha256': sha((directory/'source.png').read_bytes()),
        'prompt_sha256': sha((directory/'prompt.md').read_bytes()),
        'source_size': list(source.size), 'native_size': [16, 16],
        'method': 'eight-by-eight center samples; nearest original colors1/2; repeat2x2',
        'street_palette_sha256': PALETTE_SHA, 'quality_approval': 'pending',
        'files': {name: sha((directory/name).read_bytes()) for name in FILES}}
    (directory/'conversion.json').write_text(json.dumps(metadata, indent=2)+'\n')
    return pixels


def load_paving(root):
    from PIL import Image
    directory = root / ASSET
    metadata = json.loads((directory/'conversion.json').read_text())
    if metadata.get('native_size') != [16, 16] or set(metadata.get('files', {})) != set(FILES) or \
       metadata.get('street_palette_sha256') != PALETTE_SHA:
        raise ValueError('Require the declared native paving resources and unchanged palette.')
    for name, expected in {'source.png': metadata['source_sha256'],
                           'prompt.md': metadata['prompt_sha256'],
                           **metadata['files']}.items():
        if sha((directory/name).read_bytes()) != expected:
            raise ValueError('Regenerate the original paving resources: '+name)
    master = (directory/'master8.indices').read_bytes()
    pixels = (directory/'paving.indices').read_bytes()
    if pixels != repeated(master):
        raise ValueError('The sixteen-pixel cell must repeat its exact eight-pixel master.')
    with Image.open(directory/'paving.png') as image:
        if image.mode != 'P' or image.size != (16, 16) or image.tobytes() != pixels or \
           image.getpalette()[:48] != [c for color in palette(root) for c in color]:
            raise ValueError('Native paving PNG, indices and palette disagree.')
    return pixels


if __name__ == '__main__':
    encode_paving(Path(__file__).resolve().parents[2])
