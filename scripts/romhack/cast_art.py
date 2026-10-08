"""Compile original, data-registered SF cast sprites into native field records."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
from courier_art import opaque_bands, insert_once
from title_art import tiles8
from title_creature import pack4

ASSET = 'assets/characters/cognition-cast'
ORDER = (0, 3, 6, 1, 2, 4, 5, 7, 8)
TAG = 'OBJ_EVENT_PAL_TAG_SF_COGNITION_CAST'


def catalog(root):
    entries = json.loads((root / ASSET / 'cast.json').read_text())['characters']
    for field in ('slug', 'symbol', 'graphics', 'reserved_slot', 'script'):
        values = [entry[field] for entry in entries]
        if len(values) != len(set(values)):
            raise ValueError('Cast registry duplicates ' + field)
    for entry in entries:
        if not re.fullmatch('[a-z]+(?:-[a-z]+)*', entry['slug']):
            raise ValueError('Cast asset names must be safe paths.')
        if not re.fullmatch('OBJ_EVENT_GFX_UNUSED_[A-Z_0-9]+', entry['reserved_slot']):
            raise ValueError('Only explicitly unused native slots may be reserved.')
    return entries


def source_cells(image):
    mask = image.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    rows = opaque_bands(mask, 1)
    if len(rows) != 3:
        raise ValueError('Cast atlas needs three isolated direction rows.')
    boxes = []
    for top, bottom in rows:
        bands = opaque_bands(mask.crop((0, top, mask.width, bottom)), 0)
        if len(bands) != 3:
            raise ValueError('Each cast direction needs idle and two footsteps.')
        boxes.extend((left, top, right, bottom) for left, right in bands)
    return mask, boxes


def native_frames(image, mask, boxes, colors):
    from PIL import Image
    scale = min(15 / max(r-l for l, t, r, b in boxes),
                24 / max(b-t for l, t, r, b in boxes))
    frames = []
    for box in boxes:
        cell, alpha = image.crop(box), mask.crop(box)
        size = (round(cell.width * scale), round(cell.height * scale))
        cell, alpha = (x.resize(size, Image.Resampling.NEAREST) for x in (cell, alpha))
        frame = bytearray(512)
        left, top = (16-cell.width)//2, 30-cell.height
        for y in range(cell.height):
            for x in range(cell.width):
                if alpha.getpixel((x, y)):
                    rgb = cell.getpixel((x, y))[:3]
                    index = min(range(1, 16), key=lambda i:
                                sum((rgb[c]-colors[i][c])**2 for c in range(3)))
                    frame[(top+y)*16+left+x] = index
        frames.append(bytes(frame))
    for row in range(3):
        if len(set(frames[row*3:row*3+3])) != 3:
            raise ValueError('Native idle and alternate footsteps collapsed.')
    return frames, scale


def encode_cast(root):
    from PIL import Image
    directory = root / ASSET
    prepared, pixels = [], []
    for entry in catalog(root):
        image = Image.open(directory / entry['slug'] / 'source.png').convert('RGBA')
        mask, boxes = source_cells(image)
        for box in boxes:
            cell, alpha = image.crop(box), mask.crop(box)
            pixels.extend(rgb[:3] for rgb, a in
                          zip(cell.get_flattened_data(), alpha.get_flattened_data()) if a)
        prepared.append((entry, image, mask, boxes))
    samples = Image.new('RGB', (len(pixels), 1)); samples.putdata(pixels)
    palette = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors = [(0, 0, 0)] + [tuple(round(c*31/255)*255//31 for c in palette[i:i+3])
                            for i in range(0, 45, 3)]
    flat = [c for color in colors for c in color] + [0]*720
    raw_palette = b''.join(struct.pack('<H', sum(round(rgb[c]*31/255) << (5*c)
                                                for c in range(3))) for rgb in colors)
    (directory / 'cast.gbapal').write_bytes(raw_palette)
    receipts = []
    for entry, image, mask, boxes in prepared:
        frames, scale = native_frames(image, mask, boxes, colors)
        selected = [frames[index] for index in ORDER]
        strip = bytes(p for y in range(32) for frame in selected for p in frame[y*16:(y+1)*16])
        raw = pack4(tiles8(strip, 144, 32, 2, 4))
        path = directory / entry['slug']
        native = Image.new('P', (144, 32), 0); native.putpalette(flat); native.putdata(strip)
        native.save(path / 'walk.png', transparency=0, bits=4)
        (path / 'walk.4bpp').write_bytes(raw)
        gallery = Image.new('P', (48, 96), 0); gallery.putpalette(flat)
        for index, frame in enumerate(frames):
            cell = Image.new('P', (16, 32), 0); cell.putpalette(flat); cell.putdata(frame)
            gallery.paste(cell, (index%3*16, index//3*32))
        gallery.save(path / 'native-gallery.png', transparency=0, bits=4)
        receipts.append(dict(entry, source_size=list(image.size), source_cells=boxes,
                             common_scale=scale, files={name: hashlib.sha256((path/name).read_bytes()).hexdigest()
                             for name in ('source.png', 'walk.png', 'walk.4bpp', 'native-gallery.png')}))
    metadata = {'characters': receipts, 'frames_per_character': 9, 'native_order': ORDER,
                'native_frame_size': [16, 32], 'feet_baseline': 30,
                'east_view': 'native horizontal flip of original west frames',
                'palette_tag': '0x1125', 'palette_slot': 'PALSLOT_NPC_SPECIAL',
                'palette_sha256': hashlib.sha256(raw_palette).hexdigest(), 'quality_approval': 'pending'}
    (directory / 'conversion.json').write_text(json.dumps(metadata, indent=2)+'\n')
    return metadata


def apply_cast(root, emerald):
    directory = root / ASSET
    entries = catalog(root)
    metadata = json.loads((directory / 'conversion.json').read_text())
    if [dict((key, e[key]) for key in entries[0]) for e in metadata['characters']] != entries:
        raise ValueError('Cast registry changed after native conversion.')
    if hashlib.sha256((directory/'cast.gbapal').read_bytes()).hexdigest() != metadata['palette_sha256']:
        raise ValueError('Cast palette differs from its receipt.')
    for entry in metadata['characters']:
        for name, digest in entry['files'].items():
            if hashlib.sha256((directory/entry['slug']/name).read_bytes()).hexdigest() != digest:
                raise ValueError('Regenerate native cast after changing asset: '+entry['slug'])
        if len((directory/entry['slug']/'walk.4bpp').read_bytes()) != 9*256:
            raise ValueError('Cast graphics allocation must be nine native frames.')
    paths = ['include/constants/event_objects.h', 'include/graphics.h',
             'src/data/object_events/object_event_graphics.h',
             'src/data/object_events/object_event_pic_tables.h',
             'src/data/object_events/object_event_graphics_info.h',
             'src/data/object_events/object_event_graphics_info_pointers.h',
             'src/event_object_movement.c']
    constants, header, graphics, pictures, info, pointers, movement = ((emerald/p).read_text() for p in paths)
    if TAG in movement or '0x1125' in movement:
        raise ValueError('Dedicated SF cast palette tag is already occupied.')
    palette_dest = 'graphics/object_events/palettes/sf_cognition_cast.gbapal'
    shutil.copy2(directory/'cast.gbapal', emerald/palette_dest)
    graphics += '\nconst u16 gObjectEventPal_SFCognitionCast[] = INCBIN_U16("'+palette_dest+'");\n'
    header += '\nextern const u16 gObjectEventPal_SFCognitionCast[];\n'
    for entry in entries:
        symbol, alias, slot = entry['symbol'], entry['graphics'], entry['reserved_slot']
        constants += '\n#define '+alias+' '+slot+'\n'
        target = 'graphics/object_events/pics/people/sf_'+entry['slug'].replace('-', '_')+'.4bpp'
        shutil.copy2(directory/entry['slug']/'walk.4bpp', emerald/target)
        graphics += 'const u32 gObjectEventPic_'+symbol+'[] = INCBIN_U32("'+target+'");\n'
        pictures += '\nstatic const struct SpriteFrameImage sPicTable_'+symbol+'[] = {\n'
        pictures += ''.join('    overworld_frame(gObjectEventPic_'+symbol+', 2, 4, '+str(i)+'),\n' for i in range(9))+'};\n'
        info += '\nconst struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_'+symbol+' = {\n'
        fields = {'tileTag':'TAG_NONE', 'paletteTag':TAG, 'reflectionPaletteTag':'OBJ_EVENT_PAL_TAG_NONE',
                  'size':'256', 'width':'16', 'height':'32', 'paletteSlot':'PALSLOT_NPC_SPECIAL',
                  'shadowSize':'SHADOW_SIZE_M', 'inanimate':'FALSE', 'disableReflectionPaletteLoad':'FALSE',
                  'tracks':'TRACKS_FOOT', 'oam':'&gObjectEventBaseOam_16x32',
                  'subspriteTables':'sOamTables_16x32', 'anims':'sAnimTable_Standard',
                  'images':'sPicTable_'+symbol, 'affineAnims':'gDummySpriteAffineAnimTable'}
        info += ''.join('    .'+k+' = '+v+',\n' for k,v in fields.items())+'};\n'
        pointers = 'extern const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_'+symbol+';\n'+pointers
        pointers, count = re.subn(r'(\['+slot+r'\]\s*=\s*)&\w+,',
                                 r'\1&gObjectEventGraphicsInfo_'+symbol+',', pointers)
        if count != 1:
            raise ValueError('Reserved cast slot must exist exactly once.')
    movement = insert_once(movement, '#define OBJ_EVENT_PAL_TAG_NONE', '#define '+TAG+' 0x1125\n')
    anchor = 'static const struct SpritePalette sObjectEventSpritePalettes[] = {\n'
    movement = insert_once(movement, anchor, '').replace(anchor, anchor+
                '    {gObjectEventPal_SFCognitionCast, '+TAG+'},\n', 1)
    anchor = 'static const struct PairedPalettes sSpecialObjectReflectionPaletteSets[] = {\n'
    reflection = 'static const u16 sReflectionPaletteTags_SFCognitionCast[] = {\n    '+', '.join([TAG]*4)+',\n};\n\n'
    movement = insert_once(movement, anchor, reflection).replace(anchor, anchor+
                '    {'+TAG+', sReflectionPaletteTags_SFCognitionCast},\n', 1)
    for path, source in zip(paths, (constants, header, graphics, pictures, info, pointers, movement)):
        (emerald/path).write_text(source)
    return paths+[palette_dest]+['graphics/object_events/pics/people/sf_'+e['slug'].replace('-', '_')+'.4bpp' for e in entries]


if __name__ == '__main__':
    encode_cast(Path(__file__).resolve().parents[2])
