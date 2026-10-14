"""Check final linked SF map bytes, geographic entries and native whitelists."""
import hashlib
import json
import re
import struct
from city_map_art import make_map
from interface_text import encode, encoding_table


def audit_city_map(rom, elf, root, engine):
    from check_creature_resources import Cartridge, decode_lz
    from PIL import Image
    from title_art import tiles8
    from title_creature import pack4
    cartridge = Cartridge(rom, elf)
    _, atlas, regular, affine, palette, hubs, _ = make_map(root)
    raw_tiles = b''.join(atlas.crop((x, y, x + 8, y + 8)).tobytes()
                         for y in range(0, 120, 8) for x in range(0, 128, 8))
    courier = root / 'assets/characters/courier-native'
    face = Image.open(courier / 'walk.png').crop((0, 4, 16, 20))
    head = pack4(tiles8(face.tobytes(), 16, 16, 2, 2))
    head_palette = (courier / 'courier.gbapal').read_bytes()
    resources = [
        ('sRegionMapBg_Pal', palette, False),
        ('sRegionMapBg_GfxLZ', raw_tiles[:233 * 64], True),
        ('sRegionMapBg_TilemapLZ', affine, True),
        ('sPokedexAreaMap_Pal', palette, False),
        ('sPokedexAreaMap_Gfx', raw_tiles[:232 * 64], True),
        ('sPokedexAreaMap_Tilemap', regular, True),
        ('sRegionMapPlayerIcon_BrendanGfx', head, False),
        ('sRegionMapPlayerIcon_MayGfx', head, False),
        ('sRegionMapPlayerIcon_BrendanPal', head_palette, False),
        ('sRegionMapPlayerIcon_MayPal', head_palette, False)
    ]
    checks = []
    def compare(name, expected, actual):
        checks.append({'name': name, 'passed': actual == expected,
                       'expected_sha256': hashlib.sha256(expected).hexdigest(),
                       'actual_sha256': hashlib.sha256(actual).hexdigest(), 'bytes': len(actual)})
    def resource(name, expected, compressed=False):
        try:
            actual = cartridge.data(name)
            compare(name, expected, decode_lz(actual) if compressed else actual)
        except ValueError as error:
            checks.append({'name': name, 'passed': False, 'error': str(error)})
    for name, expected, compressed in resources:
        resource(name, expected, compressed)
    section_names = re.findall(r'^\s*(MAPSEC_[A-Z0-9_]+),?\s*$',
        (engine / 'include/constants/region_map_sections.h').read_text(), re.MULTILINE)
    sections = {name: i for i, name in enumerate(section_names)}
    if sections.get('MAPSEC_LITTLEROOT_TOWN') != 0 or sections.get('MAPSEC_OLDALE_TOWN') != 1:
        raise ValueError('Pinned SF region identifiers changed.')
    grid = bytearray([sections['MAPSEC_NONE']] * 420)
    entries = cartridge.data('gRegionMapEntries')
    table = encoding_table(engine / 'charmap.txt')
    for hub in hubs:
        section = sections[hub['section']]
        grid[hub['y'] * 28 + hub['x']] = section
        entry = entries[section * 8:section * 8 + 8]
        if len(entry) != 8:
            raise ValueError('SF entry falls outside native section table.')
        compare(hub['section'] + ':rectangle', bytes(hub[k] for k in ('x', 'y', 'width', 'height')), entry[:4])
        address = struct.unpack_from('<I', entry, 4)[0] - 0x08000000
        text = encode(hub['name'], table)
        if not 0 <= address <= len(cartridge.rom) - len(text):
            raise ValueError('SF region label pointer leaves the cartridge.')
        compare(hub['section'] + ':label', text, cartridge.rom[address:address + len(text)])
    resource('sRegionMap_MapSectionLayout', bytes(grid))
    map_constants = (engine / 'include/constants/map_groups.h').read_text()
    native_ids = {name: (int(group), int(number)) for name, number, group in re.findall(
        r'(MAP_[A-Z0-9_]+)\s*=\s*\((\d+) \| \((\d+) << 8\)\)', map_constants)}
    content = json.loads((root / 'romhack/content/engine-probe.json').read_text())
    battles = json.loads((root / 'romhack/content' / content['battle_content']).read_text())
    whitelist = bytes(v for row in battles['encounters'] for v in native_ids[row['map']])
    resource('sSFHabitatMapIds', whitelist)
    parents = bytearray()
    for name in content['maps']:
        plan = json.loads((root / 'romhack/content' / name).read_text())
        metadata = json.loads((engine / 'data/maps' / plan['engine_map'] / 'map.json').read_text())
        parents.extend((*native_ids[metadata['id']], sections[metadata['region_map_section']]))
    resource('sSFRegionMapParents', bytes(parents))
    return {'passed': all(c['passed'] for c in checks),
            'counts': {'total': len(checks), 'matched': sum(c['passed'] for c in checks)},
            'checks': checks, 'rom_sha256': hashlib.sha256(cartridge.rom).hexdigest(),
            'quality_approval': 'pending',
            'scope': 'Compiled SF background/head/grid/entry/whitelist integration; not art, save, behavior or performance acceptance'}
