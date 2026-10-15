"""Original South Park infill artwork, isolated from existing secondary resources."""
import hashlib
import json
from pathlib import Path
import struct
from courier_art import opaque_bands

ASSET = 'assets/tiles/south-park-frontage-v1'
STYLES = (('brick', 48, 80, 0), ('sage', 48, 80, 1),
          ('sandstone', 48, 80, 2), ('coffee', 32, 64, 3))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(root):
    """Crop separate original cards and serialize nearest-sampled RGB555 pixels."""
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    mask = source.getchannel('A').point(lambda alpha: 255 if alpha >= 128 else 0)
    bands = opaque_bands(mask, 0)
    if len(bands) != len(STYLES):
        raise ValueError('Frontage sheet needs four completely separated buildings.')
    cards = []
    for (name, width, height, bank), (left, right) in zip(STYLES, bands):
        bounds = mask.crop((left, 0, right, source.height)).getbbox()
        bounds = (left + bounds[0], bounds[1], left + bounds[2], bounds[3])
        card = source.crop(bounds).resize((width, height), Image.Resampling.NEAREST)
        visible = [rgba[:3] for rgba in card.get_flattened_data() if rgba[3] >= 128]
        samples = Image.new('RGB', (len(visible), 1)); samples.putdata(visible)
        palette = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
        colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) for c in palette[i:i + 3])
                               for i in range(0, 45, 3)]
        pixels = bytes(0 if rgba[3] < 128 else min(range(1, 16), key=lambda index:
            sum((round(rgba[c] * 31 / 255) - colors[index][c]) ** 2 for c in range(3)))
            for rgba in card.get_flattened_data())
        native = Image.new('P', (width, height), 0)
        native.putpalette([value * 255 // 31 for color in colors for value in color] + [0] * 720)
        native.putdata(pixels)
        native.save(directory / (name + '.png'), bits=4, transparency=0)
        packed_palette = b''.join(struct.pack('<H', sum(rgb[c] << (5*c) for c in range(3)))
                                  for rgb in colors)
        (directory / (name + '.indices')).write_bytes(pixels)
        (directory / (name + '.gbapal')).write_bytes(packed_palette)
        names = [name + suffix for suffix in ('.png', '.indices', '.gbapal')]
        cards.append({'name': name, 'size': [width, height], 'bank': bank,
                      'source_bounds': list(bounds), 'files': {
                          filename: digest((directory / filename).read_bytes()) for filename in names}})
    info = {'source_sha256': digest((directory / 'source.png').read_bytes()),
            'prompt_sha256': digest((directory / 'prompt.md').read_bytes()),
            'source_size': list(source.size), 'alpha_threshold': 128,
            'method': 'Separate alpha bands; nearest native resize; RGB555 median-cut15; transparent0',
            'generator': 'Built-in imagegen; original designs; no commercial source image',
            'quality_approval': 'pending', 'cards': cards}
    (directory / 'conversion.json').write_text(json.dumps(info, indent=2) + '\n')
    return info


def load(root):
    """Verify every consumed source, palette, index buffer and preview together."""
    from PIL import Image
    directory = root / ASSET
    info = json.loads((directory / 'conversion.json').read_text())
    if info['source_sha256'] != digest((directory / 'source.png').read_bytes()) or \
       info['prompt_sha256'] != digest((directory / 'prompt.md').read_bytes()):
        raise ValueError('Regenerate frontage resources after source/prompt changes.')
    if len(info['cards']) != len(STYLES) or info['alpha_threshold'] != 128:
        raise ValueError('Frontage conversion contract changed.')
    result = []
    for card, (name, width, height, bank) in zip(info['cards'], STYLES):
        if (card['name'], card['size'], card['bank']) != (name, [width, height], bank):
            raise ValueError('Frontage card order, dimensions or palette bank changed.')
        expected = {name + suffix for suffix in ('.png', '.indices', '.gbapal')}
        if set(card['files']) != expected:
            raise ValueError('Frontage card must declare all three native resources.')
        for filename in expected:
            if digest((directory / filename).read_bytes()) != card['files'][filename]:
                raise ValueError('Frontage resource changed: ' + filename)
        pixels = (directory / (name + '.indices')).read_bytes()
        palette = (directory / (name + '.gbapal')).read_bytes()
        image = Image.open(directory / (name + '.png'))
        if len(pixels) != width * height or max(pixels) > 15 or len(palette) != 32:
            raise ValueError('Frontage dimensions/color indices exceed native limits.')
        if image.mode != 'P' or image.size != (width, height) or image.tobytes() != pixels:
            raise ValueError('Frontage preview differs from consumed native pixels.')
        words = struct.unpack('<16H', palette)
        if words[0] != 0 or any(word > 0x7fff for word in words):
            raise ValueError('Frontage palette must be RGB555 with transparent entry0.')
        flat = image.getpalette()[:48]
        expected_flat = [((word >> (5*c)) & 31) * 255 // 31 for word in words for c in range(3)]
        if flat != expected_flat:
            raise ValueError('Frontage preview palette differs from the native palette.')
        if any(sum(value != 0 for value in pixels[y*width:(y+1)*width]) < width//2
               for y in range(height - 16, height)):
            raise ValueError('Frontage foundation must have a substantial opaque footprint.')
        result.append({'name': name, 'width': width, 'height': height, 'bank': bank,
                       'pixels': pixels, 'palette': palette})
    return result


if __name__ == '__main__':
    encode(Path(__file__).resolve().parents[2])
