"""Encode our four-pose courier throw atlas and isolate its battle-back palette."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
from title_art import tiles8
from title_creature import pack4
from courier_art import opaque_bands

ASSET = 'assets/characters/courier-battle-v1'
# Pinned engine waits on frame3; throw animation advances0,1,2 before retreat.
FRAME_ORDER = (1, 2, 3, 0)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode_courier_battle(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    alpha = source.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    bands = opaque_bands(alpha, 0)
    if len(bands) != 4:
        raise ValueError('Courier throw source needs four horizontally separated figures.')
    boxes, anchors = [], []
    for left, right in bands:
        mask = alpha.crop((left, 0, right, source.height))
        bounds = mask.getbbox()
        waist = mask.crop((0, bounds[3] - 4, mask.width, bounds[3])).getbbox()
        boxes.append((left, bounds[1], right, bounds[3]))
        anchors.append(((waist[0] + waist[2]) / 2, bounds[3] - bounds[1]))
    # Waist center/bottom anchors avoid arm-dependent recentering between poses.
    max_left = max(x for x, _ in anchors)
    max_right = max(box[2] - box[0] - x for box, (x, _) in zip(boxes, anchors))
    canvas = (math.ceil(max_left + max_right), max(y for _, y in anchors))
    scale = min(60 / canvas[0], 60 / canvas[1])
    size = (round(canvas[0] * scale), round(canvas[1] * scale))
    cells, masks = [], []
    for box, (x, y) in zip(boxes, anchors):
        cell = Image.new('RGBA', canvas)
        cell.paste(source.crop(box), (round(max_left - x), canvas[1] - y))
        cells.append(cell.resize(size, Image.Resampling.NEAREST))
        masks.append(cell.getchannel('A').point(lambda a: 255 if a >= 128 else 0).resize(size, Image.Resampling.NEAREST))
    samples = [rgb[:3] for cell, mask in zip(cells, masks)
               for rgb, alpha in zip(cell.get_flattened_data(), mask.get_flattened_data()) if alpha]
    strip = Image.new('RGB', (len(samples), 1)); strip.putdata(samples)
    palette = strip.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in palette[i:i + 3])
                           for i in range(0, 45, 3)]
    flat = [c for color in colors for c in color] + [0] * 720
    atlas = Image.new('P', (64, 256), 0); atlas.putpalette(flat)
    frames = []
    for index, (cell, mask) in enumerate(zip(cells, masks)):
        frame = Image.new('P', (64, 64), 0); frame.putpalette(flat)
        left, top = (64 - size[0]) // 2, 64 - size[1]
        for y in range(size[1]):
            for x in range(size[0]):
                if mask.getpixel((x, y)):
                    rgb = cell.getpixel((x, y))[:3]
                    color = min(range(1, 16), key=lambda n: sum((rgb[c] - colors[n][c]) ** 2 for c in range(3)))
                    frame.putpixel((left + x, top + y), color)
        frames.append(frame.tobytes())
    if len(set(frames)) != 4 or any(not any(frame) for frame in frames):
        raise ValueError('All four native throw poses must be visible and distinct.')
    atlas.putdata(b''.join(frames[index] for index in FRAME_ORDER))
    atlas.save(directory / 'back.png', transparency=0, bits=4)
    raw = pack4(tiles8(atlas.tobytes(), 64, 256, 8, 8))
    (directory / 'back.4bpp').write_bytes(raw)
    native_palette = b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c)
                                                   for c in range(3))) for rgb in colors)
    (directory / 'back.gbapal').write_bytes(native_palette)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': digest(directory / 'source.png'), 'source_size': list(source.size),
        'source_layout': 'four separated horizontal figures, left to right',
        'source_cells': boxes, 'waist_anchors': anchors, 'shared_canvas': canvas,
        'common_scale': scale, 'native_frame_size': [64, 64], 'frames': 4,
        'native_frame_order': FRAME_ORDER, 'idle_native_frame': 3,
        'native_layout': 'four vertical frames', 'waist_baseline': 64,
        'shared_gender_design': True, 'quality_approval': 'pending',
        'files': {name: digest(directory / name) for name in ('back.png', 'back.4bpp', 'back.gbapal')}
    }, indent=2) + '\n')


def apply_courier_battle(root, engine, original):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    for name, expected in dict(metadata['files'], **{'source.png': metadata['source_sha256']}).items():
        if digest(directory / name) != expected:
            raise ValueError('Regenerate courier battle assets after changing ' + name)
    if (directory / 'back.4bpp').stat().st_size != 8192 or (directory / 'back.gbapal').stat().st_size != 32:
        raise ValueError('Courier battle art needs four64x64 four-bit frames and16 colors.')
    destination = 'graphics/trainers/back_pics/sf_courier.png'
    shutil.copy2(directory / 'back.png', engine / destination)
    graphics, header, table = ('src/data/graphics/trainers.h', 'include/graphics.h',
                               'src/data/trainer_graphics/back_pic_tables.h')
    # Earlier overlays reset/extend these shared headers. Preserve Scott/field additions.
    source = (engine / graphics).read_text()
    for person in ('brendan', 'may'):
        anchor = 'graphics/trainers/back_pics/' + person + '.png'
        if source.count(anchor) != 1:
            raise ValueError('Pinned player back-picture declaration changed.')
        source = source.replace(anchor, destination)
    source += '\nconst u32 gTrainerBackPalette_SFCourier[] = INCGFX_U32("' + destination + '", ".gbapal.lz");\n'
    (engine / graphics).write_text(source)
    (engine / header).write_text((engine / header).read_text() + '\nextern const u32 gTrainerBackPalette_SFCourier[];\n')
    source = original(table)
    for name in ('BRENDAN', 'MAY'):
        anchor = 'TRAINER_BACK_PAL(' + name + ', gTrainerPalette_' + name.title() + ')'
        if source.count(anchor) != 1:
            raise ValueError('Pinned player back-palette entry changed.')
        source = source.replace(anchor, 'TRAINER_BACK_PAL(' + name + ', gTrainerBackPalette_SFCourier)')
    (engine / table).write_text(source)
    return [destination, graphics, header, table]


if __name__ == '__main__':
    encode_courier_battle(Path(__file__).resolve().parents[2])
