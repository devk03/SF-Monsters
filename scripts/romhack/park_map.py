"""Compile the authored SF park into its own original secondary tileset."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
from park_art import load_buildings, facade_cells, pack_park_cells
from street_art import load_streets, rotate_pixels, road_edge_variant
from terrain_art import load_terrain
from maps import encode_layout
from house_variants import load_variants
from park_signs import sign_cells
from seed_door_art import load as load_seed_door
from park_infill import infill_tile, connected_tile, apply as apply_infill
from park_paving import load_paving
from service_architecture import load as load_services
from service_door_art import load as load_service_doors
from city_dressing import tile as dressing_tile
from park_density import tile as density_tile

# Existing service doors retain their metatile IDs and recovery coordinates.
FACADES = ((10, 1, 7, 5, 40), (29, 1, 7, 5, 75),
           (18, 2, 3, 4, 110), (11, 20, 3, 4, 110), (23, 2, 3, 4, 122),
           (26, 2, 3, 4, 136),
           (11, 13, 3, 4, 110), (14, 13, 3, 4, 122), (14, 20, 3, 4, 122))


def prune_unused_terrain(cells, plan):
    """Keep IDs stable; reclaim graphics only from unreferenced terrain cells.

    South Park has no tileset animation callback or terrain-changing scripts.
    Animated service doors occupy facade IDs71/106 and separate reserved VRAM.
    All street, furniture and architectural cells remain untouched.
    """
    used = {park_tile(plan, x, y) - 512
            for y, row in enumerate(plan['rows']) for x in range(len(row))}
    used.add(plan['border_tile'] - 512)
    result = list(cells)
    for index in range(20, 39):
        if index not in used:
            result[index] = (bytes(256), cells[index][1])
    return result


def park_resources(root):
    from PIL import Image
    streets, street_palette = load_streets(root)
    # Park-only pixels use isolated primary palette4; street palette6 stays intact.
    streets[16] = load_paving(root)
    terrain, terrain_palette, _ = load_terrain(root)
    furniture_root = root / 'assets/tiles/south-park-furniture'
    metadata = json.loads((furniture_root / 'conversion.json').read_text())
    furniture = (furniture_root / 'furniture.indices').read_bytes()
    if len(furniture) != 768 or hashlib.sha256(furniture).hexdigest() != metadata['indices_sha256'] or \
       hashlib.sha256((furniture_root / 'source.png').read_bytes()).hexdigest() != metadata['source_sha256'] or \
       hashlib.sha256(terrain_palette).hexdigest() != metadata['palette_sha256']:
        raise ValueError('Regenerate the original park furnishings after changes.')
    terrain[8], terrain[9] = furniture[512:], furniture[256:512]
    frames, building_palettes = load_services(root,'v3')
    cells = [(cell, 4 if index in (16,19) else 6) for index,cell in
             enumerate(streets + [rotate_pixels(streets[15], 1), streets[16]])]
    flags = [0x1000] * 20
    cells += [(cell, 7) for cell in terrain]; flags += [0x1000] * 19
    flags[24] = 0x1002  # Tall grass keeps native encounter behavior.
    cells.append((furniture[:256], 7)); flags.append(0x1000)
    for frame, bank in zip(frames, (8, 9)):
        cells += facade_cells(frame, 112, 80, bank); flags += [0] * 35
    for first in (68, 103):
        flags[first:first + 7] = [0x1000] * 7
    flags[71] = flags[106] = 0x1069  # Original frames use native animated door behavior.
    doors=load_service_doors(root)
    for name,upper,lower,bank in (('warehouse',64,71,8),('clinic',99,106,9)):
        # The exact closed animation frame also supplies the static facade.
        cells[upper],cells[lower]=facade_cells(doors[name][0],16,32,bank)
    annex = Image.open(root / 'assets/tiles/sunset-rowhouse/native-preview.png').resize(
        (48, 64), Image.Resampling.NEAREST).tobytes()
    cells += facade_cells(annex, 48, 64, 10); flags += [0] * 12
    flags[119:122] = [0x1000] * 3
    variants = {variant['name']: variant for variant in load_variants(root)}
    butter = Image.open(root / 'assets/tiles/sunset-rowhouse-butter/native-preview.png').resize(
        (48, 64), Image.Resampling.NEAREST).tobytes()
    cells += facade_cells(butter, 48, 64, 11); flags += [0] * 12
    flags[131:134] = [0x1000] * 3
    plan = json.loads((root / 'romhack/content/south-park.json').read_text())
    cells = prune_unused_terrain(cells, plan)
    cells += sign_cells(); flags += [0x1000, 0x1000]
    lavender = Image.open(root / 'assets/tiles/sunset-rowhouse-lavender/native-preview.png').resize(
        (48, 64), Image.Resampling.NEAREST).tobytes()
    cells += facade_cells(lavender, 48, 64, 12); flags += [0]*9 + [0x1000]*3
    # A dedicated centered entrance leaves the original facade records intact.
    door = load_seed_door(root)
    upper, lower = facade_cells(door['frames'][0], 16, 32, 11)
    cells.append(lower); flags.append(0x1069)  # Native animated door, global660.
    cells.append(upper); flags.append(0)       # Blocked upper facade, global661.
    raw, records, attributes = pack_park_cells(cells, flags, reuse_flips=True)
    if len(raw) // 32 > 504:
        raise ValueError('Park art must reserve the last eight secondary tiles for native doors.')
    # Alpha around facades reveals our own sidewalk, not inherited scenery.
    records = bytearray(records)
    sidewalk = records[19 * 16 + 8:20 * 16]
    for index in range(40, len(cells)):
        records[index * 16:index * 16 + 8] = sidewalk
    palettes = bytearray(512)
    for bank, data in zip((6, 7, 8, 9, 10, 11, 12), (street_palette, terrain_palette,
                                           *building_palettes,
                                           (root / 'assets/tiles/sunset-rowhouse/house.gbapal').read_bytes(),
                                           variants['butter']['palette'],
                                           variants['lavender']['palette'])):
        palettes[bank * 32:(bank + 1) * 32] = data
    return raw, bytes(records), attributes, bytes(palettes)


def park_tile(plan, x, y):
    housing=density_tile(plan,x,y)
    if housing is not None:
        return housing
    furnishing=dressing_tile(plan,x,y)
    if furnishing is not None:
        return furnishing
    connected=connected_tile(plan,x,y)
    if connected is not None:
        return connected
    token = plan['rows'][y][x]
    if token in 'WXYZ':
        return infill_tile(plan, x, y)
    if token == 'R':
        edge = road_edge_variant(plan, x, y, tokens='R')
        if edge:
            return 512 + edge
        if y in (9, 28) and x != 7:
            return 525  # Horizontal center stripe.
        if x == 7 and y not in (8, 9, 10, 27, 28, 29):
            return 526  # Vertical center stripe.
        return 512
    if token in 'Qq':
        return 660 if token == 'Q' else 661
    if token == 'P':
        return 531
    if token == '.':
        return 532 + (0, 12, 13)[(x * 17 + y * 11) % 3]
    if token in 'GB#T':
        if token == '#' and (x, y) in ((10, 6), (29, 6)):
            return 646 if x == 10 else 647
        return {'G': 536, 'B': 551, '#': 540, 'T': 541}[token]
    if token == 'F':
        last_x, last_y = len(plan['rows'][0]) - 1, len(plan['rows']) - 1
        corner = {(0, 0): 7, (last_x, 0): 16, (last_x, last_y): 17, (0, last_y): 18}
        return 532 + corner.get((x, y), 6 if x in (0, last_x) else 5)
    for left, top, width, height, first in FACADES:
        if left <= x < left + width and top <= y < top + height:
            return 512 + first + (y - top) * width + x - left
    raise ValueError(f'Unmapped South Park token {token} at {x},{y}.')


def apply_park_map(root, engine):
    from PIL import Image
    plan = json.loads((root / 'romhack/content/south-park.json').read_text())
    raw, records, attributes, palettes = park_resources(root)
    directory = engine / 'data/tilesets/secondary/sf_south_park'
    directory.mkdir(parents=True, exist_ok=True)
    count = len(raw) // 32
    image = Image.new('P', (128, ((count + 15) // 16) * 8), 0)
    image.putpalette(Image.open(root / 'assets/tiles/sunset-streets/native-atlas.png').getpalette())
    for tile in range(count):
        for y in range(8):
            for x in range(8):
                value = raw[tile * 32 + y * 4 + x // 2] >> (x % 2 * 4) & 15
                image.putpixel((tile % 16 * 8 + x, tile // 16 * 8 + y), value)
    image.save(directory / 'tiles.png', transparency=0, bits=4)
    for name, data in (('metatiles.bin', records), ('attributes.bin', attributes), ('palettes.gbapal', palettes)):
        (directory / name).write_bytes(data)
    prefix = 'data/tilesets/secondary/sf_south_park/'
    additions = {
        'src/data/tilesets/graphics.h': f'\nconst u32 gTilesetTiles_SFSouthPark[] = INCGFX_U32("{prefix}tiles.png", ".4bpp.lz", "-num_tiles {count} -Wnum_tiles");\nconst u16 gTilesetPalettes_SFSouthPark[] = INCBIN_U16("{prefix}palettes.gbapal");\n',
        'src/data/tilesets/metatiles.h': f'\nconst u16 gMetatiles_SFSouthPark[] = INCBIN_U16("{prefix}metatiles.bin");\nconst u16 gMetatileAttributes_SFSouthPark[] = INCBIN_U16("{prefix}attributes.bin");\n',
        'src/data/tilesets/headers.h': '''
const struct Tileset gTileset_SFSouthPark = {
    .isCompressed = TRUE, .isSecondary = TRUE,
    .tiles = gTilesetTiles_SFSouthPark,
    .palettes = (const u16 (*)[16])gTilesetPalettes_SFSouthPark,
    .metatiles = gMetatiles_SFSouthPark,
    .metatileAttributes = gMetatileAttributes_SFSouthPark, .callback = NULL,
};
'''}
    for path, addition in additions.items():
        source = (engine / path).read_text()
        if 'gTilesetTiles_SFSouthPark' in source or 'gMetatiles_SFSouthPark' in source:
            raise ValueError('Reset SF source declarations before rebuilding South Park.')
        (engine / path).write_text(source + addition)
    width, height, blocks = encode_layout(plan); data = bytearray(blocks)
    for y in range(height):
        for x in range(width):
            offset = (y * width + x) * 2; word = struct.unpack_from('<H', data, offset)[0]
            struct.pack_into('<H', data, offset, word & 0xfc00 | park_tile(plan, x, y))
    (engine / 'data/layouts/OldaleTown/map.bin').write_bytes(data)
    return list(additions) + apply_infill(root, engine, records)
