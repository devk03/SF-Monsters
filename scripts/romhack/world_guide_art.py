"""Original, native-resolution SF region relief, compiled to tiled GBA4bpp.

No commercial reference pixels are read. Original generated terrain is converted
to native indices; towns/corridors come from the real world graph. One16color bank.
"""
from PIL import Image

import hashlib
import json
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parents[2] / 'assets/ui/sf-region-relief-v2'
PALETTE = json.loads((DIRECTORY / 'palette.json').read_text())


def terrain():
    proof = json.loads((DIRECTORY / 'conversion.json').read_text())
    data = (DIRECTORY / 'native.indices').read_bytes()
    if hashlib.sha256(data).hexdigest() != proof['native_sha256'] or len(data) != 224*112:
        raise ValueError('Original SF relief differs from its reviewed native conversion')
    image = Image.frombytes('P',(224,112),data)
    image.putpalette([v*255//31 for color in PALETTE for v in color]+[0]*(768-48))
    return image


def tiled_bytes(image):
    width, height = image.size
    if width % 8 or height % 8:
        raise ValueError('Region image must fill complete native tiles')
    out = bytearray()
    for top in range(0, height, 8):
        for left in range(0, width, 8):
            for y in range(8):
                for x in range(0, 8, 2):
                    a, b = image.getpixel((left + x, top + y)), image.getpixel((left + x + 1, top + y))
                    if not 0 <= a < 16 or not 0 <= b < 16:
                        raise ValueError('Region artwork exceeds one native palette bank')
                    out.append(a | b << 4)
    return bytes(out)


def compile_art():
    raw = tiled_bytes(terrain())
    palette = ', '.join('RGB' + str(color).replace(' ', '') for color in PALETTE)
    rows = ['    ' + ','.join(hex(v) for v in raw[n:n + 24]) for n in range(0, len(raw), 24)]
    return ('// Original SF region relief; generated from world_guide_art.py.\n'
            'static const u16 sSFGuidePalette[16] = {' + palette + '};\n'
            'static const u8 sSFGuideRelief[] = {\n' + ',\n'.join(rows) + '\n};\n')
