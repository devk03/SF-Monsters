"""Pack original source artwork into hardware-sized BMPs; do not repaint it."""
from pathlib import Path
import hashlib
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'engine/graphics'
OUT.mkdir(parents=True, exist_ok=True)


def indexed_sprite(sheet, name, height):
    opaque = sheet.getchannel('A').point(lambda value: 255 if value >= 192 else 0)
    rgb = sheet.convert('RGB')
    learned = rgb.quantize(colors=15, dither=Image.Dither.NONE)
    palette = [255, 0, 255] + learned.getpalette()[:45] + [0] * 720
    result = Image.new('P', sheet.size)
    result.putpalette(palette)
    pixels = [value + 1 if alpha else 0 for value, alpha in
              zip(learned.get_flattened_data(), opaque.get_flattened_data())]
    result.putdata(pixels)
    assert max(pixels) < 16
    result.save(OUT / f'{name}.bmp')
    (OUT / f'{name}.json').write_text(json.dumps({
        'type': 'sprite', 'height': height, 'bpp_mode': 'bpp_4'
    }, indent=2) + '\n')
    return result


def courier():
    path = ROOT / 'assets/characters/courier-walk-candidate.png'
    image = Image.open(path).convert('RGBA')
    assert image.size == (1024, 1536), 'Update crop metadata for a new source sheet.'
    sheet = Image.new('RGBA', (16, 32 * 12))
    # Fixed crop and baseline across all poses; never trim each frame separately.
    tops = [138, 589, 1037]
    for direction in range(4):
        for pose, top in enumerate(tops):
            left = direction * 256 + 32
            frame = image.crop((left, top, left + 192, top + 393))
            frame = frame.resize((16, 32), Image.Resampling.NEAREST)
            sheet.paste(frame, (0, (direction * 3 + pose) * 32))
    indexed_sprite(sheet, 'courier', 32)
    metadata = ROOT / 'engine/build'
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / 'courier-source.json').write_text(json.dumps({
        'source': str(path.relative_to(ROOT)),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'frames': 12, 'directions': ['down', 'up', 'left', 'right'],
        'poses': ['idle', 'left_step', 'right_step'],
        'review': 'unreviewed; native-size cleanup remains required'
    }, indent=2) + '\n')


def font():
    source = (ROOT / 'assets/font8x8_basic.h').read_text()
    rows = re.findall(r'\{((?:\s*0x[0-9A-Fa-f]+,?){8})\}', source)
    assert len(rows) == 128
    sheet = Image.new('RGBA', (8, 8 * 94))
    for character in range(33, 127):
        values = [int(value, 16) for value in re.findall(r'0x[0-9A-Fa-f]+', rows[character])]
        for y, value in enumerate(values):
            for x in range(8):
                if value & (1 << x):
                    sheet.putpixel((x, (character - 33) * 8 + y), (239, 246, 242, 255))
    indexed_sprite(sheet, 'ui_font', 8)


courier()
font()
print('Packed 12 courier poses and 94 public-domain font glyphs.')
