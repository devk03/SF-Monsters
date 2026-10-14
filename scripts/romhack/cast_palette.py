"""Share a native NPC palette without silently recoloring existing cast art."""
import hashlib
import json
import struct


def palette_colors(raw):
    if len(raw) != 32:
        raise ValueError('Cast palette must contain sixteen RGB555 colors.')
    words = struct.unpack('<16H', raw)
    if words[0] != 0 or any(word > 0x7fff for word in words):
        raise ValueError('Cast palette needs transparent index0 and native RGB555.')
    return [tuple(((word >> (5*c)) & 31)*255//31 for c in range(3)) for word in words]


def cast_palette(directory, pixels):
    policy = directory/'palette-policy.json'
    if policy.exists():
        raw_policy = policy.read_bytes()
        document = json.loads(raw_policy)
        if not isinstance(document, dict) or set(document) != {'format', 'intent', 'colors_rgb5'} or \
           type(document['format']) is not int or document['format'] != 1 or \
           not isinstance(document['intent'], str) or not document['intent'].strip():
            raise ValueError('Cast palette policy needs its format and intent.')
        colors = document['colors_rgb5']
        if not isinstance(colors, list) or len(colors) != 16 or any(
            not isinstance(color, list) or len(color) != 3 or any(
                type(value) is not int or not 0 <= value <= 31 for value in color)
            for color in colors):
            raise ValueError('Cast palette policy needs sixteen RGB5 triples.')
        raw = b''.join(struct.pack('<H', sum(value << (5*c)
                        for c, value in enumerate(color))) for color in colors)
        return palette_colors(raw), raw, hashlib.sha256(raw_policy).hexdigest()
    from PIL import Image
    samples = Image.new('RGB', (len(pixels), 1)); samples.putdata(pixels)
    palette = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c*31/255)*255//31 for c in palette[i:i+3])
                            for i in range(0, 45, 3)]
    raw = b''.join(struct.pack('<H', sum(round(rgb[c]*31/255) << (5*c)
                                        for c in range(3))) for rgb in colors)
    return colors, raw, None


def quantization_palette(directory, shared):
    path = directory/'quantization-palette.gbapal'
    raw = path.read_bytes() if path.exists() else shared
    return palette_colors(raw), raw


def preserve_used_colors(frames, source, shared):
    palette_colors(source); palette_colors(shared)
    used = {index for frame in frames for index in frame if index}
    if any(index > 15 or source[index*2:index*2+2] != shared[index*2:index*2+2]
           for index in used):
        raise ValueError('Shared cast palette would recolor an existing native pose.')
