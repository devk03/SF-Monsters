"""Assemble prototype maps from their shared collision source and original atlas."""
from pathlib import Path
import ctypes
import json
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'engine/graphics'
BUILD = ROOT / 'engine/build'
BUILD.mkdir(parents=True, exist_ok=True)
library = BUILD / 'host_content.so'
subprocess.run(['cc', '-shared', '-fPIC', str(ROOT / 'game/content.c'),
                '-o', str(library)], check=True)
tile = ctypes.CDLL(str(library)).game_tile
tile.argtypes = [ctypes.c_uint8, ctypes.c_int, ctypes.c_int]
tile.restype = ctypes.c_uint8
atlas = Image.open(ROOT / 'assets/world-atlas.png').convert('RGBA')


def cell(index, size):
    column, row = index % 4, index // 4
    image = atlas.crop((round(column * atlas.width / 4), round(row * atlas.height / 4),
                        round((column + 1) * atlas.width / 4), round((row + 1) * atlas.height / 4)))
    box = image.getchannel('A').point(lambda value: 255 if value > 90 else 0).getbbox()
    if box:
        image = image.crop(box)
    image.thumbnail(size, Image.Resampling.NEAREST)
    frame = Image.new('RGBA', size)
    frame.alpha_composite(image, ((size[0] - image.width) // 2, size[1] - image.height))
    return frame


terrain = [cell(index, (16, 16)) for index in range(12, 16)]
buildings = [cell(index, (64, 48)) for index in range(8, 12)]
for map_id, name in enumerate(['sunset', 'south_park', 'cognition']):
    canvas = Image.new('RGB', (512, 512), '#102333')
    for y in range(18):
        for x in range(24):
            kind = tile(map_id, x, y)
            graphic = terrain[3 if kind == 2 else 0 if kind == 3 else 1 if kind == 1 else 2]
            canvas.paste(graphic, (x * 16, y * 16), graphic)
    placements = [(0, 13, 3), (1, 18, 4)] if map_id == 0 else [(2, 12, 3), (3, 4, 3)]
    if map_id < 2:
        for graphic, x, y in placements:
            canvas.paste(buildings[graphic], (x * 16, y * 16), buildings[graphic])
    # Quantization and tile packing are build conversion, not source-art cleanup.
    canvas.quantize(colors=128, dither=Image.Dither.NONE).save(OUT / f'{name}.bmp')
    (OUT / f'{name}.json').write_text(json.dumps({
        'type': 'regular_bg', 'bpp_mode': 'bpp_8'
    }, indent=2) + '\n')
print('Packed three provisional 512x512 backgrounds; collision source unchanged.')
