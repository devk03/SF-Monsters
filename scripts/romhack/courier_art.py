"""Author native courier locomotion and isolate its palette from other field art."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from title_art import tiles8
from title_creature import pack4

ASSET = 'assets/characters/courier-native'
ORDER = ((0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 1), (2, 2))


def opaque_bands(mask, axis):
    bands = []
    for index in range(mask.size[axis]):
        box = (index, 0, index + 1, mask.height) if axis == 0 else (0, index, mask.width, index + 1)
        if mask.crop(box).getbbox():
            if not bands or index > bands[-1][1]:
                bands.append([index, index + 1])
            else:
                bands[-1][1] = index + 1
    return bands


def native_strip(frames, mode):
    if len(frames) != 18 or mode not in ('walk', 'run') or any(len(frame) != 512 for frame in frames):
        raise ValueError('Courier atlas needs eighteen 16x32 frames and a locomotion mode.')
    offset = 0 if mode == 'walk' else 3
    selected = [frames[row * 6 + column + offset] for row, column in ORDER]
    if any(not any(frame) or any(pixel > 15 for pixel in frame) for frame in selected):
        raise ValueError('Every native courier frame must contain visible four-bit pixels.')
    for idle, left, right in ((0, 3, 4), (1, 5, 6), (2, 7, 8)):
        if len({selected[idle], selected[left], selected[right]}) != 3:
            raise ValueError('Idle and both footsteps must remain distinct at native scale.')
    pixels = bytes(pixel for y in range(32) for frame in selected for pixel in frame[y * 16:(y + 1) * 16])
    return pixels, pack4(tiles8(pixels, 144, 32, 2, 4))


def encode_courier(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    mask = source.getchannel('A').point(lambda alpha: 255 if alpha >= 128 else 0)
    rows = opaque_bands(mask, 1)
    if len(rows) != 3:
        raise ValueError('Review courier row isolation before conversion.')
    cells = []
    for top, bottom in rows:
        columns = opaque_bands(mask.crop((0, top, mask.width, bottom)), 0)
        if len(columns) != 6:
            raise ValueError('Every courier direction needs six isolated source poses.')
        cells.extend((left, top, right, bottom) for left, right in columns)
    # One common scale and row baseline preserve authored stepping and head proportions.
    scale = min(15 / max(right - left for left, _, right, _ in cells),
                24 / max(bottom - top for _, top, _, bottom in cells))
    sized = []
    visible = []
    for box in cells:
        cell, alpha = source.crop(box), mask.crop(box)
        size = (round(cell.width * scale), round(cell.height * scale))
        cell, alpha = (image.resize(size, Image.Resampling.NEAREST) for image in (cell, alpha))
        sized.append((cell, alpha))
        visible.extend(rgb[:3] for rgb, a in zip(cell.get_flattened_data(), alpha.get_flattened_data()) if a)
    samples = Image.new('RGB', (len(visible), 1)); samples.putdata(visible)
    palette = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in palette[i:i + 3])
                           for i in range(0, 45, 3)]
    flat_palette = [c for color in colors for c in color] + [0] * 720
    frames = []
    gallery = Image.new('P', (96, 96), 0); gallery.putpalette(flat_palette)
    for index, (cell, alpha) in enumerate(sized):
        frame = Image.new('P', (16, 32), 0); frame.putpalette(flat_palette)
        left, top = (16 - cell.width) // 2, 30 - cell.height
        for y in range(cell.height):
            for x in range(cell.width):
                if alpha.getpixel((x, y)):
                    rgb = cell.getpixel((x, y))[:3]
                    color = min(range(1, 16), key=lambda i: sum((rgb[c] - colors[i][c]) ** 2 for c in range(3)))
                    frame.putpixel((left + x, top + y), color)
        frames.append(bytes(frame.get_flattened_data()))
        gallery.paste(frame, (index % 6 * 16, index // 6 * 32))
    gallery.save(directory / 'native-gallery.png', transparency=0, bits=4)
    files = {}
    for mode in ('walk', 'run'):
        pixels, raw = native_strip(frames, mode)
        image = Image.new('P', (144, 32), 0); image.putpalette(flat_palette); image.putdata(pixels)
        image.save(directory / (mode + '.png'), transparency=0, bits=4)
        path = directory / (mode + '.4bpp'); path.write_bytes(raw)
        files[path.name] = hashlib.sha256(raw).hexdigest()
        files[mode + '.png'] = hashlib.sha256((directory / (mode + '.png')).read_bytes()).hexdigest()
    import struct
    native_palette = b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c)
                                                 for c in range(3))) for rgb in colors)
    (directory / 'courier.gbapal').write_bytes(native_palette)
    files['courier.gbapal'] = hashlib.sha256(native_palette).hexdigest()
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'source_size': list(source.size), 'source_cells': cells, 'common_scale': scale,
        'native_frame_size': [16, 32], 'feet_baseline': 30, 'native_order': ORDER,
        'east_view': 'native horizontal flip of authored west frames',
        'shared_gender_design': True, 'frames': 18, 'palette_tag': '0x1124',
        'quality_approval': 'pending', 'files': files
    }, indent=2) + '\n')


def insert_once(source, anchor, extra):
    if source.count(anchor) != 1:
        raise ValueError('Pinned courier source anchor changed.')
    return source.replace(anchor, extra + anchor, 1)


def palette_info(source):
    for name in ('BrendanNormal', 'MayNormal', 'RivalBrendanNormal', 'RivalMayNormal'):
        pattern = r'(const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_' + name + r' = \{)(.*?)(\n\};)'
        def change(match):
            record, count = re.subn(r'(\.paletteTag = )OBJ_EVENT_PAL_TAG_(?:BRENDAN|MAY),',
                                    r'\1OBJ_EVENT_PAL_TAG_SF_COURIER,', match[2])
            if count != 1:
                raise ValueError('Courier normal view must have one original palette tag.')
            return match[1] + record + match[3]
        source, count = re.subn(pattern, change, source, flags=re.S)
        if count != 1:
            raise ValueError('Missing native normal-view palette record: ' + name)
    return source


def apply_courier(root, emerald, original):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    digests = dict(metadata['files'], **{'source.png': metadata['source_sha256']})
    if any(hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest for name, digest in digests.items()):
        raise ValueError('Regenerate native courier assets after changing source or conversion.')
    restored = []
    for person in ('brendan', 'may'):
        for mode, name in (('walk', 'walking'), ('run', 'running')):
            path = f'graphics/object_events/pics/people/{person}/{name}.png'
            shutil.copy2(directory / (mode + '.png'), emerald / path); restored.append(path)
    palette_path = emerald / 'graphics/object_events/palettes/sf_courier.gbapal'
    shutil.copy2(directory / 'courier.gbapal', palette_path)
    gfx = 'src/data/object_events/object_event_graphics.h'
    header = 'include/graphics.h'
    info = 'src/data/object_events/object_event_graphics_info.h'
    movement = 'src/event_object_movement.c'
    (emerald / gfx).write_text(original(gfx) + '\nconst u16 gObjectEventPal_SFCourier[] = INCBIN_U16("graphics/object_events/palettes/sf_courier.gbapal");\n')
    (emerald / header).write_text(insert_once(original(header), '// overworld', 'extern const u16 gObjectEventPal_SFCourier[];\n\n'))
    (emerald / info).write_text(palette_info(original(info)))
    source = original(movement)
    if '0x1124' in source:
        raise ValueError('Dedicated courier palette tag is already occupied.')
    source = insert_once(source, '#define OBJ_EVENT_PAL_TAG_NONE', '#define OBJ_EVENT_PAL_TAG_SF_COURIER 0x1124\n')
    source = insert_once(source, 'static const struct SpritePalette sObjectEventSpritePalettes[] = {\n', '')
    source = source.replace('static const struct SpritePalette sObjectEventSpritePalettes[] = {\n',
                            'static const struct SpritePalette sObjectEventSpritePalettes[] = {\n    {gObjectEventPal_SFCourier, OBJ_EVENT_PAL_TAG_SF_COURIER},\n', 1)
    source = insert_once(source, 'static const u16 sReflectionPaletteTags_Brendan[]',
        'static const u16 sReflectionPaletteTags_SFCourier[] = {\n    OBJ_EVENT_PAL_TAG_SF_COURIER, OBJ_EVENT_PAL_TAG_SF_COURIER,\n    OBJ_EVENT_PAL_TAG_SF_COURIER, OBJ_EVENT_PAL_TAG_SF_COURIER,\n};\n\n')
    for table in ('sPlayerReflectionPaletteSets', 'sSpecialObjectReflectionPaletteSets'):
        anchor = 'static const struct PairedPalettes ' + table + '[] = {\n'
        source = insert_once(source, anchor, '').replace(anchor, anchor +
            '    {OBJ_EVENT_PAL_TAG_SF_COURIER, sReflectionPaletteTags_SFCourier},\n', 1)
    (emerald / movement).write_text(source)
    return restored + [gfx, header, info, movement]


if __name__ == '__main__':
    encode_courier(Path(__file__).resolve().parents[2])
