"""Original institutional opening frames, registered with native door timing."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
from door_art import native_frames

ASSET = 'assets/tiles/south-park-doors'


def encode_park_doors(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    palette_data = (root / 'assets/tiles/south-park-buildings/building-palettes.gbapal').read_bytes()
    payloads = {}
    for row, name in enumerate(('warehouse', 'clinic')):
        palette = palette_data[row * 32:(row + 1) * 32]
        colors = [tuple(((word >> (5 * c)) & 31) * 255 // 31 for c in range(3))
                  for word in struct.unpack('<16H', palette)]
        sheet = Image.new('P', (48, 32), 0)
        sheet.putpalette([value for color in colors for value in color] + [0] * 720)
        frames = []
        for column in range(3):
            image = source.crop((round(column * source.width / 3), round(row * source.height / 2),
                                 round((column + 1) * source.width / 3), round((row + 1) * source.height / 2)))
            image = image.resize((16, 32), Image.Resampling.NEAREST)
            pixels = bytes(0 if rgba[3] < 128 else min(range(1, 16),
                key=lambda i: sum((rgba[c] - colors[i][c]) ** 2 for c in range(3)))
                for rgba in image.get_flattened_data())
            frame = Image.new('P', (16, 32), 0); frame.putpalette(sheet.getpalette()); frame.putdata(pixels)
            sheet.paste(frame, (column * 16, 0)); frames.append(pixels)
        sheet.save(directory / (name + '.png'), transparency=0, bits=4)
        payloads[name + '.4bpp'] = native_frames(frames)
    for name, data in payloads.items():
        (directory / name).write_bytes(data)
    files = list(payloads) + ['warehouse.png', 'clinic.png']
    (directory / 'conversion.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
        'palette_sha256': hashlib.sha256(palette_data).hexdigest(),
        'frame_size': [16, 32], 'frames_per_door': 3, 'palette_banks': [8, 9],
        'door_metatiles': [583, 618], 'native_timing': 'unchanged', 'quality_approval': 'pending',
        'files': {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in files}
    }, indent=2) + '\n')


def apply_park_doors(root, engine):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    if hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest() != metadata['source_sha256'] or \
       hashlib.sha256((root / 'assets/tiles/south-park-buildings/building-palettes.gbapal').read_bytes()).hexdigest() != metadata['palette_sha256'] or \
       any(hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest
           for name, digest in metadata['files'].items()):
        raise ValueError('Regenerate institutional door frames after art or palette changes.')
    for name in ('warehouse', 'clinic'):
        if (directory / (name + '.4bpp')).stat().st_size != 768:
            raise ValueError('Each native institutional door needs three 256-byte stages.')
        shutil.copy2(directory / (name + '.png'), engine / ('graphics/door_anims/sf_park_' + name + '.png'))
    path = 'src/field_door.c'; source = (engine / path).read_text()
    anchor = 'static const struct DoorGraphics sDoorAnimGraphicsTable[] =\n{\n'
    if source.count(anchor) != 1:
        raise ValueError('Review the native door registration point before rebuilding.')
    declaration = '''static const u8 sSFParkWarehouseDoor[] = INCGFX_U8("graphics/door_anims/sf_park_warehouse.png", ".4bpp", "-mwidth 2 -mheight 4");
static const u8 sSFParkClinicDoor[] = INCGFX_U8("graphics/door_anims/sf_park_clinic.png", ".4bpp", "-mwidth 2 -mheight 4");
static const u8 sSFParkWarehousePalette[] = {8,8,8,8,8,8,8,8};
static const u8 sSFParkClinicPalette[] = {9,9,9,9,9,9,9,9};

'''
    source = source.replace(anchor, declaration + anchor +
        '    {583, DOOR_SOUND_NORMAL, 1, sSFParkWarehouseDoor, sSFParkWarehousePalette},\n' +
        '    {618, DOOR_SOUND_NORMAL, 1, sSFParkClinicDoor, sSFParkClinicPalette},\n')
    (engine / path).write_text(source)
    return [path]


if __name__ == '__main__':
    encode_park_doors(Path(__file__).resolve().parents[2])
