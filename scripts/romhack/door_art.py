"""Compile original rowhouse door frames into the inherited native animation table."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
from title_art import tiles8
from title_creature import pack4

ASSET = 'assets/tiles/sunset-door'
FRAME_SIZE = (16, 32)
METATILE = 635


def native_frames(frames):
    if len(frames) != 3 or any(len(frame) != 512 for frame in frames):
        raise ValueError('Door animation needs three 16x32 frames.')
    if any(any(pixel > 15 for pixel in frame) or not any(frame) for frame in frames):
        raise ValueError('Door frames must contain visible four-bit pixels.')
    if len(set(frames)) != 3:
        raise ValueError('Opening stages must remain distinct at native size.')
    # Each native animation offset selects eight tiles: top then bottom metatile.
    return b''.join(pack4(tiles8(frame, 16, 32, 2, 4)) for frame in frames)


def encode_door(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    # Keep three equal columns aligned; do not separately crop or center poses.
    if source.width % 3:
        raise ValueError('Review equal frame boundaries before converting the door sheet.')
    palette_data = (root / 'assets/tiles/sunset-rowhouse/house.gbapal').read_bytes()
    colors = [tuple(((word >> (5 * c)) & 31) * 255 // 31 for c in range(3))
              for word in struct.unpack('<16H', palette_data)]
    palette = [value for color in colors for value in color] + [0] * 720
    sheet = Image.new('P', (48, 32), 0); sheet.putpalette(palette)
    frames = []
    for index in range(3):
        width = source.width // 3
        image = source.crop((index * width, 0, (index + 1) * width, source.height))
        image = image.resize(FRAME_SIZE, Image.Resampling.NEAREST)
        pixels = bytes(0 if rgba[3] < 128 else min(range(1, 16),
            key=lambda i: sum((rgba[c] - colors[i][c]) ** 2 for c in range(3)))
            for rgba in image.get_flattened_data())
        frame = Image.new('P', FRAME_SIZE, 0); frame.putpalette(palette); frame.putdata(pixels)
        sheet.paste(frame, (index * 16, 0)); frames.append(pixels)
    encoded = native_frames(frames)
    sheet.save(directory / 'frames.png', bits=4, transparency=0)
    (directory / 'frames.4bpp').write_bytes(encoded)
    metadata = {'native_frame_size': list(FRAME_SIZE), 'frames': 3,
                'metatile': METATILE, 'palette_bank': 10,
                'source_sha256': hashlib.sha256((directory / 'source.png').read_bytes()).hexdigest(),
                'palette_sha256': hashlib.sha256(palette_data).hexdigest(),
                'frame_offsets': [0, 256, 512], 'animation_timing': 'inherited native table',
                'quality_approval': 'pending', 'files': {
                    name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                    for name in ('frames.png', 'frames.4bpp')}}
    (directory / 'conversion.json').write_text(json.dumps(metadata, indent=2) + '\n')


def apply_door_art(root, engine, original):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    for path, digest in [(directory / 'source.png', metadata['source_sha256']),
        (root / 'assets/tiles/sunset-rowhouse/house.gbapal', metadata['palette_sha256']),
        *[(directory / name, digest) for name, digest in metadata['files'].items()]]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Regenerate door frames after changing art or the house palette.')
    if (directory / 'frames.4bpp').stat().st_size != 768:
        raise ValueError('Native door animation must contain three 256-byte stages.')
    destination = engine / 'graphics/door_anims/sf_rowhouse.png'
    shutil.copy2(directory / 'frames.png', destination)
    path = 'src/field_door.c'
    source = original(path)
    anchor = 'static const struct DoorGraphics sDoorAnimGraphicsTable[] =\n{\n'
    if source.count(anchor) != 1:
        raise ValueError('Pinned native door table changed; inspect before integrating.')
    declaration = '''static const u8 sSFDoorTiles[] = INCGFX_U8("graphics/door_anims/sf_rowhouse.png", ".4bpp", "-mwidth 2 -mheight 4");
static const u8 sSFDoorPalettes[] = {10, 10, 10, 10, 10, 10, 10, 10};

'''
    source = source.replace(anchor, declaration + anchor +
        '    {635, DOOR_SOUND_NORMAL, 1, sSFDoorTiles, sSFDoorPalettes},\n')
    (engine / path).write_text(source)
    camera_path = 'src/field_camera.c'
    camera = original(camera_path)
    draw_anchor = '        DrawMetatile(METATILE_LAYER_TYPE_COVERED, tiles, offset);'
    if camera.count(draw_anchor) != 1:
        raise ValueError('Pinned door drawing hook changed; inspect before integrating.')
    camera = camera.replace('#include "text.h"',
                            '#include "text.h"\n#include "constants/maps.h"')
    camera = camera.replace(draw_anchor, '''        // The SF facade occupies the top background, above the native fog.
        // Put its animated replacement on that same layer, without changing timing.
        if ((gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_LITTLEROOT_TOWN)
          && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_LITTLEROOT_TOWN)
          && (MapGridGetMetatileIdAt(x, y) == 630 || MapGridGetMetatileIdAt(x, y) == 635))
         || (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_OLDALE_TOWN)
          && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_OLDALE_TOWN)
          && (MapGridGetMetatileIdAt(x, y) == 576 || MapGridGetMetatileIdAt(x, y) == 583
           || MapGridGetMetatileIdAt(x, y) == 611 || MapGridGetMetatileIdAt(x, y) == 618)))
        {
            u16 sfTiles[8];
            const u16 *sfGround = gMapHeader.mapLayout->secondaryTileset->metatiles
                + (gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_OLDALE_TOWN) ? 19 : 60)
                * NUM_TILES_PER_METATILE;
            int i;
            for (i = 0; i < 4; i++)
            {
                sfTiles[i] = sfGround[i + 4];
                sfTiles[i + 4] = tiles[i];
            }
            DrawMetatile(METATILE_LAYER_TYPE_NORMAL, sfTiles, offset);
        }
        else
            DrawMetatile(METATILE_LAYER_TYPE_COVERED, tiles, offset);''')
    (engine / camera_path).write_text(camera)
    return [path, camera_path]


if __name__ == '__main__':
    encode_door(Path(__file__).resolve().parents[2])
