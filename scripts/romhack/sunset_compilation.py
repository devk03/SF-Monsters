"""Compile complete original Sunset overlays before linking; verify without repair."""
import hashlib
import json
import re
import struct
import subprocess

from bootstrap import EMERALD_REVISION

PREFIX = 'data/tilesets/secondary/petalburg/'
MAP = 'data/layouts/LittlerootTown/map.bin'
HEADER = 'src/data/tilesets/graphics.h'
SYMBOLS = ('gTilesetTiles_Petalburg', 'gTilesetPalettes_Petalburg',
           'gMetatiles_Petalburg', 'gMetatileAttributes_Petalburg',
           'LittlerootTown_Layout_Blockdata')


def pinned(engine, name):
    return subprocess.check_output(['git', 'show', f'{EMERALD_REVISION}:{name}'], cwd=engine)


def native_palette(source):
    rows = source.decode('ascii').splitlines()
    if rows[:3] != ['JASC-PAL', '0100', '16'] or len(rows) != 19:
        raise ValueError('Require the pinned sixteen-color native palette source.')
    colors = [tuple(map(int, row.split())) for row in rows[3:]]
    if any(len(rgb) != 3 or any(not 0 <= c <= 255 for c in rgb) for rgb in colors):
        raise ValueError('Native palette source has invalid RGB channels.')
    # Match the pinned gbagfx WriteGbaPalette downconversion exactly.
    return struct.pack('<16H', *(sum((rgb[c]//8) << (5*c) for c in range(3)) for rgb in colors))


def compose(root, engine, plan=None):
    from house_art import ASSET, compose_tiles, owned_field_attributes, remap_houses
    from house_variants import load_variants, facade_placements
    from street_art import load_streets, remap_roads
    from terrain_art import load_terrain, remap_terrain
    from sunset_density import extend, remap
    from maps import encode_layout
    if plan is None:
        plan = json.loads((root/'romhack/content/sunset.json').read_text())
    directory = root/ASSET
    info = json.loads((directory/'conversion.json').read_text())
    files = {name:(directory/name).read_bytes() for name in info['files']}
    for name, raw in [('source.png', (directory/'source.png').read_bytes()), *files.items()]:
        expected = info['source_sha256'] if name == 'source.png' else info['files'][name]
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Original Sunset house asset changed: '+name)
    records = pinned(engine, PREFIX+'metatiles.bin')
    attrs = pinned(engine, PREFIX+'metatile_attributes.bin')
    if len(records) != 2304 or len(attrs) != 288:
        raise ValueError('Pinned Sunset source allocations changed.')
    palettes = bytearray(b''.join(native_palette(pinned(engine, PREFIX+f'palettes/{i:02}.pal')) for i in range(16)))
    streets, street_pal = load_streets(root)
    terrain, terrain_pal, _ = load_terrain(root)
    facades = load_variants(root)
    graphics, records, unique = compose_tiles(bytes(16384), files['house.4bpp'], records+bytes(800), streets, terrain, facades)
    palettes[320:352] = files['house.gbapal']
    palettes[352:384] = street_pal
    palettes[384:416] = terrain_pal
    for facade in facades:
        bank = facade['bank']; palettes[bank*32:(bank+1)*32] = facade['palette']
    attrs = owned_field_attributes(attrs+bytes(100))
    blocks = encode_layout(plan)[2]
    _, origins = remap_houses(plan, blocks)
    placements = facade_placements(plan, origins, facades)
    blocks, _ = remap_houses(plan, blocks, placements)
    blocks, roads = remap_roads(plan, blocks)
    blocks, ground = remap_terrain(plan, blocks)
    if 'compact_homes' in plan:
        graphics, records, attrs, palettes = extend(root, graphics, records, attrs, bytes(palettes))
        blocks = remap(plan, blocks, root)
        unique = 491
    resources = dict(zip(SYMBOLS, (graphics, bytes(palettes), records, attrs, blocks)))
    receipt = {'origins':origins, 'unique_tiles':unique, 'native_size':[80,80],
        'collision_elevation_preserved':'compact_homes' not in plan,
        'existing_collision_elevation_preserved':True,
        'new_solid_cells':36 if 'compact_homes' in plan else 0,
        'street_variants':roads, 'terrain_variants':ground,
        'secondary_tiles':512, 'enterable_apartment':True,
        'decorative_houses':8 if 'compact_homes' in plan else 5,
        'architectural_variants':[{'name':f['name'], 'first_metatile':f['first'],
            'palette_bank':f['bank'], 'placements':[list(p) for p, first in placements.items() if first == f['first']]} for f in facades],
        'door_animation':'three original stages; native opening/closing timing', 'quality_approval':'pending'}
    return resources, receipt


def prepare(root, engine, original, plan=None):
    from PIL import Image
    from house_art import ASSET
    if plan is None:
        plan = json.loads((root/'romhack/content/sunset.json').read_text())
    resources, _ = compose(root, engine, plan)
    layouts = json.loads((engine/'data/layouts/layouts.json').read_text())['layouts']
    for name in json.loads((root/'romhack/content/engine-probe.json').read_text())['maps']:
        other = json.loads((root/'romhack/content'/name).read_text())
        metadata = json.loads((engine/('data/maps/'+other['engine_map']+'/map.json')).read_text())
        layout = next(item for item in layouts if item['id'] == metadata['layout'])
        if other['engine_map'] != plan['engine_map'] and layout['secondary_tileset'] == 'gTileset_Petalburg':
            raise ValueError('Another active SF map shares the Sunset native sheet.')
    header = original(HEADER)
    old = 'const u32 gTilesetTiles_Petalburg[] = INCGFX_U32("'+PREFIX+'tiles.png", ".4bpp.lz", "-num_tiles 159 -Wnum_tiles");'
    if header.count(old) != 1:
        raise ValueError('Pinned Sunset graphics declaration changed.')
    header = header.replace(old, old.replace('159', '512'), 1)
    pattern = r'const u16 gTilesetPalettes_Petalburg\[\]\[16\] =\n\{.*?\n\};'
    header, count = re.subn(pattern, 'const u16 gTilesetPalettes_Petalburg[][16] = INCBIN_U16("'+PREFIX+'sf-palettes.gbapal");', header, flags=re.S)
    if count != 1:
        raise ValueError('Pinned Sunset palette declaration changed.')
    # Validate everything before writing any native build input. The base header
    # reset remains before the apartment/park appenders in the normal pipeline.
    image = Image.new('P', (128,256), 0)
    image.putpalette(Image.open(root/ASSET/'native-preview.png').getpalette())
    raw = resources[SYMBOLS[0]]
    for tile in range(512):
        for y in range(8):
            for x in range(8):
                byte = raw[tile*32+y*4+x//2]
                image.putpixel((tile%16*8+x,tile//16*8+y), (byte >> (x%2*4)) & 15)
    outputs = {PREFIX+'metatiles.bin':resources[SYMBOLS[2]],
               PREFIX+'metatile_attributes.bin':resources[SYMBOLS[3]], MAP:resources[SYMBOLS[4]],
               PREFIX+'sf-palettes.gbapal':resources[SYMBOLS[1]], HEADER:header.encode()}
    for name, data in outputs.items():
        path = engine/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    path = engine/PREFIX/'tiles.png'
    image.save(path, transparency=0, bits=4)
    # Only tracked inputs belong in the base-restoration manifest. The generated
    # private palette becomes unreferenced when the tracked header is restored.
    return [PREFIX+'tiles.png', HEADER, PREFIX+'metatiles.bin', PREFIX+'metatile_attributes.bin', MAP]


def verify(root, engine, target, *, elf=None, plan=None):
    import sys
    sys.path.insert(0, str(root/'scripts/quality'))
    from check_creature_resources import Cartridge, decode_lz
    expected, receipt = compose(root, engine, plan)
    cart = Cartridge(target, elf or engine/'sf-engine-probe.elf')
    observed = []
    for name, raw in expected.items():
        data = cart.data(name, 2048 if name == SYMBOLS[-1] else None)
        actual = decode_lz(data) if name == SYMBOLS[0] else data
        if actual != raw:
            raise ValueError('Normally compiled Sunset resource differs: '+name)
        observed.append({'symbol':name, 'raw_bytes':len(raw),
                         'raw_sha256':hashlib.sha256(raw).hexdigest()})
    receipt.update(resources=observed, normal_compilation_verified=True,
                   post_link_writes=False)
    return receipt
