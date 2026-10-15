"""Compile original, data-registered SF cast sprites into native field records."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
from courier_art import opaque_bands, insert_once
from title_art import tiles8
from title_creature import pack4
from cast_cleanup import apply_cleanup
from cast_palette import cast_palette, quantization_palette, preserve_used_colors

ASSET = 'assets/characters/cognition-cast'
ORDER = (0, 3, 6, 1, 2, 4, 5, 7, 8)
TAG = 'OBJ_EVENT_PAL_TAG_SF_COGNITION_CAST'
GROUPS = ((ASSET, 'SFCognitionCast', TAG, '0x1125'),
          ('assets/characters/south-park-cast', 'SFSouthParkCast',
           'OBJ_EVENT_PAL_TAG_SF_SOUTH_PARK_CAST', '0x1126'),
          ('assets/characters/sunset-cast', 'SFSunsetCast',
           'OBJ_EVENT_PAL_TAG_SF_SUNSET_CAST', '0x1127'))
# The six unused doll slots are occupied. Reuse reviewed stock appearances for
# their explicit SF owners; keep the static table and native dynamic IDs stable.
# Each replacement is restricted to its named existing SF owner.
AUTHORED_REPLACEMENTS = {'OBJ_EVENT_GFX_GENTLEMAN': ('south-park.json', 'SF_GarryTan'),
                         'OBJ_EVENT_GFX_MAN_3': ('south-park.json', 'SF_DylanField'),
                         'OBJ_EVENT_GFX_SCIENTIST_1': ('sunset.json', 'SF_Karpathy'),
                         'OBJ_EVENT_GFX_PROF_BIRCH': ('sunset.json', 'SF_Naval')}


def catalog(root, asset=ASSET):
    entries = json.loads((root / asset / 'cast.json').read_text())['characters']
    for field in ('slug', 'symbol', 'graphics', 'reserved_slot', 'script'):
        values = [entry[field] for entry in entries]
        if len(values) != len(set(values)):
            raise ValueError('Cast registry duplicates ' + field)
    for entry in entries:
        if not re.fullmatch('[a-z]+(?:-[a-z]+)*', entry['slug']):
            raise ValueError('Cast asset names must be safe paths.')
        slot = entry['reserved_slot']
        if not re.fullmatch('OBJ_EVENT_GFX_UNUSED_[A-Z_0-9]+', slot) and \
           AUTHORED_REPLACEMENTS.get(slot) != (entry['map'], entry['script']):
            raise ValueError('Reserve an unused slot or its reviewed authored SF appearance.')
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


def encode_cast(root, asset=ASSET, palette_tag='0x1125'):
    from PIL import Image
    directory = root / asset
    prepared, pixels = [], []
    for entry in catalog(root, asset):
        image = Image.open(directory / entry['slug'] / 'source.png').convert('RGBA')
        mask, boxes = source_cells(image)
        for box in boxes:
            cell, alpha = image.crop(box), mask.crop(box)
            pixels.extend(rgb[:3] for rgb, a in
                          zip(cell.get_flattened_data(), alpha.get_flattened_data()) if a)
        prepared.append((entry, image, mask, boxes))
    colors, raw_palette, policy_hash = cast_palette(directory, pixels)
    flat = [c for color in colors for c in color] + [0]*720
    (directory / 'cast.gbapal').write_bytes(raw_palette)
    receipts = []
    for entry, image, mask, boxes in prepared:
        path = directory / entry['slug']
        source_colors, source_palette = quantization_palette(path, raw_palette)
        frames, scale = native_frames(image, mask, boxes, source_colors)
        cleanup = path / 'native-cleanup.json'
        if cleanup.exists():
            frames = apply_cleanup(frames, json.loads(cleanup.read_text()),
                                   (path/'source.png').read_bytes(), source_palette)
        preserve_used_colors(frames, source_palette, raw_palette)
        selected = [frames[index] for index in ORDER]
        strip = bytes(p for y in range(32) for frame in selected for p in frame[y*16:(y+1)*16])
        raw = pack4(tiles8(strip, 144, 32, 2, 4))
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
                             for name in ('source.png', 'walk.png', 'walk.4bpp', 'native-gallery.png')
                             + (('native-cleanup.json',) if cleanup.exists() else ())
                             + (('quantization-palette.gbapal',) if
                                (path/'quantization-palette.gbapal').exists() else ())}))
    metadata = {'characters': receipts, 'frames_per_character': 9, 'native_order': ORDER,
                'native_frame_size': [16, 32], 'feet_baseline': 30,
                'east_view': 'native horizontal flip of original west frames',
                'palette_tag': palette_tag, 'palette_slot': 'PALSLOT_NPC_SPECIAL',
                'palette_sha256': hashlib.sha256(raw_palette).hexdigest(), 'quality_approval': 'pending'}
    if policy_hash:
        metadata['palette_policy_sha256'] = policy_hash
    (directory / 'conversion.json').write_text(json.dumps(metadata, indent=2)+'\n')
    return metadata


def verified_cast(root, asset):
    directory = root / asset
    entries = catalog(root, asset)
    metadata = json.loads((directory / 'conversion.json').read_text())
    if [dict((key, e[key]) for key in entries[0]) for e in metadata['characters']] != entries:
        raise ValueError('Cast registry changed after native conversion.')
    if hashlib.sha256((directory/'cast.gbapal').read_bytes()).hexdigest() != metadata['palette_sha256']:
        raise ValueError('Cast palette differs from its receipt.')
    policy = directory/'palette-policy.json'
    if policy.exists() != ('palette_policy_sha256' in metadata) or (policy.exists() and
       hashlib.sha256(policy.read_bytes()).hexdigest() != metadata['palette_policy_sha256']):
        raise ValueError('Regenerate cast after changing its shared palette policy.')
    for entry in metadata['characters']:
        for name in ('native-cleanup.json', 'quantization-palette.gbapal'):
            if (directory/entry['slug']/name).exists() != (name in entry['files']):
                raise ValueError('Regenerate cast after adding/removing '+name+': '+entry['slug'])
        for name, digest in entry['files'].items():
            if hashlib.sha256((directory/entry['slug']/name).read_bytes()).hexdigest() != digest:
                raise ValueError('Regenerate native cast after changing asset: '+entry['slug'])
        if len((directory/entry['slug']/'walk.4bpp').read_bytes()) != 9*256:
            raise ValueError('Cast graphics allocation must be nine native frames.')
    return entries, metadata


def registered_groups(root):
    groups = [(asset, symbol, tag, value, *verified_cast(root, asset))
              for asset, symbol, tag, value in GROUPS]
    for field in ('slug', 'symbol', 'graphics', 'reserved_slot', 'script'):
        values = [entry[field] for *_, entries, metadata in groups for entry in entries]
        if len(values) != len(set(values)):
            raise ValueError('Cast groups collide on '+field)
    map_palettes = {}
    for asset, symbol, tag, value, entries, metadata in groups:
        for entry in entries:
            if entry['map'] in map_palettes and map_palettes[entry['map']] != value:
                raise ValueError('Named cast on one map must share its special palette group.')
            map_palettes[entry['map']] = value
    for asset, symbol, tag, value, entries, metadata in groups:
        if metadata['palette_tag'] != value:
            raise ValueError('Cast group palette tag differs from its receipt.')
        for entry in entries:
            plan = json.loads((root/'romhack/content'/entry['map']).read_text())
            owners = [npc for npc in plan['npcs'] if npc['script']==entry['script']]
            if len(owners)!=1 or owners[0]['graphics']!=entry['graphics']:
                raise ValueError('Cast event must use its registered graphics: '+entry['slug'])
            if entry['reserved_slot'] in AUTHORED_REPLACEMENTS:
                for path in (root/'romhack/content').glob('*.json'):
                    for npc in json.loads(path.read_text()).get('npcs', []):
                        if npc.get('graphics') == entry['reserved_slot']:
                            raise ValueError('Stock cast appearance still has another authored owner.')
    return groups


def audit_compiled_cast(rom, elf, root, graphics_header):
    """Verify original cast pixels and actual native slot/frame/palette bindings."""
    sys.path.insert(0, str(root/'scripts/quality'))
    from check_creature_resources import Cartridge
    receipt = {'passed': False, 'checks': [], 'errors': [],
               'scope': 'Compiled field cast integration; no likeness/animation/save approval'}
    try:
        cart = Cartridge(rom, elf)
        constants = {name:int(value) for name,value in re.findall(
            r'^#define (OBJ_EVENT_GFX_\w+)\s+(\d+)\s*$', graphics_header.read_text(), re.M)}
        table = cart.data('gObjectEventGraphicsInfoPointers')

        def check(label, expected, actual):
            receipt['checks'].append({'label':label, 'matches':expected == actual,
                'expected_sha256':hashlib.sha256(expected).hexdigest(),
                'actual_sha256':hashlib.sha256(actual).hexdigest()})

        check('static_table_bytes', struct.pack('<I', 239*4), struct.pack('<I', len(table)))
        for asset, palette_symbol, tag, tag_value, entries, metadata in registered_groups(root):
            directory = root/asset
            check(palette_symbol+':palette', (directory/'cast.gbapal').read_bytes(),
                  cart.data('gObjectEventPal_'+palette_symbol))
            for entry in entries:
                symbol = entry['symbol']; picture = 'gObjectEventPic_'+symbol
                frame_table = 'sPicTable_'+symbol; info_name = 'gObjectEventGraphicsInfo_'+symbol
                check(symbol+':graphics', (directory/entry['slug']/'walk.4bpp').read_bytes(),
                      cart.data(picture))
                expected = b''.join(struct.pack('<IHH', cart.symbols[picture][0]+i*256, 256, 0)
                                    for i in range(9))
                check(symbol+':nine_frames', expected, cart.data(frame_table))
                slot = constants[entry['reserved_slot']]
                check(symbol+':slot', struct.pack('<I', cart.symbols[info_name][0]),
                      table[slot*4:slot*4+4])
                info = cart.data(info_name)
                if len(info) != 36:
                    raise ValueError('Field graphics info must retain its native 36-byte ABI.')
                expected = struct.pack('<HHhhBI', int(tag_value,16), 256, 16, 32, 10,
                                       cart.symbols[frame_table][0])
                check(symbol+':display', expected,
                      info[2:4]+info[6:12]+bytes([info[12]&15])+info[28:32])
        receipt['inputs'] = {str(path.resolve()):hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in (rom, elf, graphics_header, Path(__file__))}
        receipt['passed'] = bool(receipt['checks']) and all(row['matches'] for row in receipt['checks'])
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        receipt['errors'].append(str(error))
    receipt['counts'] = {'total':len(receipt['checks']),
                         'matched':sum(row['matches'] for row in receipt['checks'])}
    return receipt


def apply_cast(root, emerald, original):
    groups = registered_groups(root)
    paths = ['include/constants/event_objects.h', 'include/graphics.h',
             'src/data/object_events/object_event_graphics.h',
             'src/data/object_events/object_event_pic_tables.h',
             'src/data/object_events/object_event_graphics_info.h',
             'src/data/object_events/object_event_graphics_info_pointers.h',
             'src/event_object_movement.c']
    constants, header, graphics, pictures, info, pointers, movement = ((emerald/p).read_text() for p in paths)
    # These two headers have no earlier overlay owner. Rebuild them from the
    # pinned source; other headers must retain the courier/map additions.
    pictures, pointers = original(paths[3]), original(paths[5])
    generated = []
    for asset, palette_symbol, tag, tag_value, entries, metadata in groups:
        directory = root / asset
        if tag in movement or tag_value in movement:
            raise ValueError('Dedicated SF cast palette tag is already occupied.')
        palette_dest = 'graphics/object_events/palettes/sf_'+Path(asset).name.replace('-', '_')+'.gbapal'
        shutil.copy2(directory/'cast.gbapal', emerald/palette_dest)
        graphics += '\nconst u16 gObjectEventPal_'+palette_symbol+'[] = INCBIN_U16("'+palette_dest+'");\n'
        header += '\nextern const u16 gObjectEventPal_'+palette_symbol+'[];\n'
        for entry in entries:
            symbol, alias, slot = entry['symbol'], entry['graphics'], entry['reserved_slot']
            constants += '\n#define '+alias+' '+slot+'\n'
            target = 'graphics/object_events/pics/people/sf_'+entry['slug'].replace('-', '_')+'.4bpp'
            shutil.copy2(directory/entry['slug']/'walk.4bpp', emerald/target)
            graphics += 'const u32 gObjectEventPic_'+symbol+'[] = INCBIN_U32("'+target+'");\n'
            pictures += '\nstatic const struct SpriteFrameImage sPicTable_'+symbol+'[] = {\n'
            pictures += ''.join('    overworld_frame(gObjectEventPic_'+symbol+', 2, 4, '+str(i)+'),\n' for i in range(9))+'};\n'
            info += '\nconst struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_'+symbol+' = {\n'
            fields = {'tileTag':'TAG_NONE', 'paletteTag':tag, 'reflectionPaletteTag':'OBJ_EVENT_PAL_TAG_NONE',
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
        movement = insert_once(movement, '#define OBJ_EVENT_PAL_TAG_NONE', '#define '+tag+' '+tag_value+'\n')
        anchor = 'static const struct SpritePalette sObjectEventSpritePalettes[] = {\n'
        movement = insert_once(movement, anchor, '').replace(anchor, anchor+
                    '    {gObjectEventPal_'+palette_symbol+', '+tag+'},\n', 1)
        anchor = 'static const struct PairedPalettes sSpecialObjectReflectionPaletteSets[] = {\n'
        reflection = 'static const u16 sReflectionPaletteTags_'+palette_symbol+'[] = {\n    '+', '.join([tag]*4)+',\n};\n\n'
        movement = insert_once(movement, anchor, reflection).replace(anchor, anchor+
                    '    {'+tag+', sReflectionPaletteTags_'+palette_symbol+'},\n', 1)
        generated += [palette_dest]+['graphics/object_events/pics/people/sf_'+e['slug'].replace('-', '_')+'.4bpp' for e in entries]
    for path, source in zip(paths, (constants, header, graphics, pictures, info, pointers, movement)):
        (emerald/path).write_text(source)
    aliases = [entry['graphics'] for *_, entries, metadata in groups for entry in entries]
    predicate = '#include "constants/event_objects.h"\n\n'
    predicate += 'static bool8 SFIsNamedCastGraphics(u8 id)\n{\n    switch (id)\n    {\n'
    predicate += ''.join('    case '+alias+':\n' for alias in aliases)
    predicate += '        return TRUE;\n    default:\n        return FALSE;\n    }\n}\n\n'
    (emerald/'src/sf_cast_resume.h').write_text(predicate+(root/'romhack/engine/cast_resume.h').read_text())
    path = 'src/overworld.c'
    source = (emerald/path).read_text()
    source = insert_once(source,'void CB2_ContinueSavedGame(void)', '#include "sf_cast_resume.h"\n\n')
    anchor = '        LoadSaveblockObjEventScripts();\n\n    UnfreezeObjectEvents();'
    if source.count(anchor)!=1:
        raise ValueError('Pinned named-cast resume hook changed.')
    source = source.replace(anchor,'        LoadSaveblockObjEventScripts();\n\n'
                            '    SFResumeNamedCastGraphics();\n    UnfreezeObjectEvents();',1)
    (emerald/path).write_text(source)
    paths.append(path)
    return paths+generated


if __name__ == '__main__':
    for asset, symbol, tag, value in GROUPS:
        encode_cast(Path(__file__).resolve().parents[2], asset, value)
