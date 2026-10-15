"""Original service-building candidates matching the connected block's art scale.

These assets are not installed in the normal release producer yet.
"""
import json
from pathlib import Path
import struct
from connected_frontage import COLORS, sha

ASSET = 'assets/tiles/south-park-services-v2'
CARDS = (('warehouse', (89,25,972,703)), ('clinic', (1125,25,2009,703)))


def encode(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory/'source.png').convert('RGBA')
    if source.size != (2098,749):
        raise ValueError('Review service architecture source coordinates.')
    palette = b''.join(struct.pack('<H', sum(rgb[c] << (5*c) for c in range(3)))
                       for rgb in COLORS)
    frames = []
    for name, bounds in CARDS:
        native = source.crop(bounds).resize((112,80), Image.Resampling.NEAREST)
        pixels = bytes(0 if rgba[3] < 128 else min(range(1,16), key=lambda index:
            sum((round(rgba[c]*31/255)-COLORS[index][c])**2 for c in range(3)))
            for rgba in native.get_flattened_data())
        image = Image.new('P',(112,80))
        image.putpalette([c*255//31 for rgb in COLORS for c in rgb]+[0]*720)
        image.putdata(pixels);image.save(directory/(name+'.png'),bits=4,transparency=0)
        frames.append(pixels)
    (directory/'buildings.indices').write_bytes(b''.join(frames))
    (directory/'building-palettes.gbapal').write_bytes(palette*2)
    files = ('warehouse.png','clinic.png','buildings.indices','building-palettes.gbapal')
    references = ('assets/tiles/connected-frontage-v2/native.png',
                  'assets/tiles/south-park-buildings/warehouse.png',
                  'assets/tiles/south-park-buildings/clinic.png')
    metadata = {'source_sha256':sha((directory/'source.png').read_bytes()),
        'prompt_sha256':sha((directory/'prompt.md').read_bytes()),
        'generator':'Built-in imagegen, original architecture',
        'quality_approval':'pending; prototype only; door animation not integrated',
        'native_size':[112,80], 'cards':[{'name':n,'source_bounds':list(b)} for n,b in CARDS],
        'method':'Separate original source bounds; nearest112x80; shared curated RGB55515; alpha128',
        'references':{name:sha((root/name).read_bytes()) for name in references},
        'files':{name:sha((directory/name).read_bytes()) for name in files}}
    (directory/'conversion.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata


def load(root):
    from PIL import Image
    directory = root / ASSET
    info = json.loads((directory/'conversion.json').read_text())
    if info['source_sha256'] != sha((directory/'source.png').read_bytes()) or (
            info['prompt_sha256'] != sha((directory/'prompt.md').read_bytes())):
        raise ValueError('Service architecture source or prompt changed.')
    if info['native_size'] != [112,80] or info['cards'] != [
            {'name':n,'source_bounds':list(b)} for n,b in CARDS]:
        raise ValueError('Service architecture native footprint changed.')
    for name,digest in info['files'].items():
        if sha((directory/name).read_bytes()) != digest:
            raise ValueError('Service architecture resource changed: '+name)
    packed = b''.join(struct.pack('<H',sum(rgb[c] << (5*c) for c in range(3))) for rgb in COLORS)
    if (directory/'building-palettes.gbapal').read_bytes() != packed*2:
        raise ValueError('Service architecture palette differs from the block palette.')
    frames = (directory/'buildings.indices').read_bytes()
    if len(frames) != 112*80*2 or max(frames) > 15:
        raise ValueError('Service architecture indexed allocation changed.')
    result = [frames[:8960],frames[8960:]]
    expected = [c*255//31 for rgb in COLORS for c in rgb]
    for (name,_),pixels in zip(CARDS,result):
        image = Image.open(directory/(name+'.png'))
        if (image.mode,image.size,image.tobytes(),image.getpalette()[:48]) != (
                'P',(112,80),pixels,expected):
            raise ValueError('Service preview differs from consumed indexed data.')
    return result,[packed,packed]


if __name__ == '__main__':
    print(json.dumps(encode(Path(__file__).resolve().parents[2]),indent=2))
