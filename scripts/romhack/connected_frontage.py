"""Convert one connected architectural scene at its final native pixel scale.

This is a visual experiment, not the installed South Park resource producer.
The fixed split keeps all walls inside the existing blocked four-row footprint.
"""
import hashlib
import json
from pathlib import Path
import struct

SIZE = (176, 80)
REVISIONS = {
    'v1': ('source-candidate-b.png', 'prompt-candidate-b.md',
           (1859,846), (67,20,1792,805), 726),
    'v2': ('source.png', 'prompt.md', (1860,846), (0,1,1860,636), 636),
    'v3': ('source.png', 'prompt.md', (1859,846), (2,2,1858,637), 637),
}
COLORS = ((0,0,0), (5,7,10), (12,13,16), (17,17,19), (8,11,15),
          (29,26,20), (22,18,14), (25,14,11), (18,9,8), (18,10,7),
          (28,22,14), (20,17,22), (20,20,20), (14,14,14), (9,14,4), (11,8,9))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def specification(root, revision):
    if revision not in REVISIONS:
        raise ValueError('Unknown connected frontage revision.')
    return root / ('assets/tiles/connected-frontage-'+revision), REVISIONS[revision]


def encode(root, revision='v1'):
    from PIL import Image
    directory, (source_name, prompt_name, size, bounds, ground_y) = specification(root, revision)
    source = Image.open(directory / source_name).convert('RGBA')
    if source.size != size:
        raise ValueError('Review source coordinates for a new generated candidate.')
    left, top, right, bottom = bounds
    native = Image.new('RGBA', SIZE)
    # Keep architecture coupled across the whole block. Discard generated ground:
    # the native sidewalk underlay supplies the approach without a pasted panel.
    zone = source.crop((left, top, right, ground_y))
    native.paste(zone.resize((176, 64), Image.Resampling.NEAREST), (0, 0))
    colors = COLORS
    pixels = bytes(0 if rgba[3] < 128 else min(range(1, 16), key=lambda index:
        sum((round(rgba[c]*31/255)-colors[index][c])**2 for c in range(3)))
        for rgba in native.get_flattened_data())
    image = Image.new('P', SIZE)
    image.putpalette([c*255//31 for rgb in colors for c in rgb] + [0]*720)
    image.putdata(pixels)
    image.save(directory / 'native.png', bits=4, transparency=0)
    packed = b''.join(struct.pack('<H', sum(rgb[c] << (5*c) for c in range(3)))
                      for rgb in colors)
    (directory / 'block.indices').write_bytes(pixels)
    (directory / 'block.gbapal').write_bytes(packed)
    files = ('native.png', 'block.indices', 'block.gbapal')
    info = {'source_sha256': sha((directory/source_name).read_bytes()),
            'prompt_sha256': sha((directory/prompt_name).read_bytes()),
            'generator': 'Built-in imagegen, original connected architecture',
            'quality_approval': 'pending; prototype only', 'size': list(SIZE),
            'source_bounds': list(bounds), 'source_ground_y': ground_y,
            'method': 'Whole-width architecture crop; nearest176x64; fixed RGB55515; alpha128; transparent approach',
            'blocked_rows': [0,64], 'walkable_rows': [64,80],
            'files': {name: sha((directory/name).read_bytes()) for name in files}}
    (directory/'conversion.json').write_text(json.dumps(info, indent=2)+'\n')
    return info


def load(root, revision='v1'):
    from PIL import Image
    directory, (source_name, prompt_name, size, bounds, ground_y) = specification(root, revision)
    info = json.loads((directory/'conversion.json').read_text())
    if info['source_sha256'] != sha((directory/source_name).read_bytes()):
        raise ValueError('Connected frontage source changed.')
    if info['prompt_sha256'] != sha((directory/prompt_name).read_bytes()):
        raise ValueError('Connected frontage prompt provenance changed.')
    if (info['size'], info['source_bounds'], info['source_ground_y']) != (
            list(SIZE), list(bounds), ground_y):
        raise ValueError('Review native footprint and source split together.')
    for name in ('native.png', 'block.indices', 'block.gbapal'):
        if sha((directory/name).read_bytes()) != info['files'][name]:
            raise ValueError('Connected frontage native resource changed: '+name)
    pixels = (directory/'block.indices').read_bytes()
    palette = (directory/'block.gbapal').read_bytes()
    image = Image.open(directory/'native.png')
    if len(pixels) != 176*80 or max(pixels) > 15 or len(palette) != 32 or (
            image.mode, image.size, image.tobytes()) != ('P', SIZE, pixels):
        raise ValueError('Connected frontage exceeds its native indexed footprint.')
    words = struct.unpack('<16H', palette)
    expected = [((w >> (5*c)) & 31)*255//31 for w in words for c in range(3)]
    fixed_words = tuple(sum(rgb[c] << (5*c) for c in range(3)) for rgb in COLORS)
    if words != fixed_words or image.getpalette()[:48] != expected:
        raise ValueError('Connected frontage preview and native palette differ.')
    if any(pixels[176*64:]):
        raise ValueError('Generated pavement must not cover the native sidewalk.')
    return pixels, palette


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', choices=tuple(REVISIONS), default='v1')
    args = parser.parse_args()
    print(json.dumps(encode(Path(__file__).resolve().parents[2], args.revision), indent=2))
