"""Install one SF geographic layout across native map graphics and habitat UI."""
import json
import re
import shutil
from city_map_art import ASSET, make_map
from title_art import tiles8
from title_creature import pack4


def replace(source, before, after):
    if source.count(before) != 1:
        raise ValueError('Pinned SF map anchor changed: ' + before)
    return source.replace(before, after, 1)


def prepare_player_icon(root, destination):
    from PIL import Image
    source = root / 'assets/characters/courier-native'
    image = Image.open(source / 'walk.png').crop((0, 4, 16, 20))
    if image.mode != 'P' or max(image.tobytes()) > 15:
        raise ValueError('Original courier head must retain native four-bit indices.')
    image.save(destination / 'player.png', transparency=0, bits=4)
    raw = pack4(tiles8(image.tobytes(), 16, 16, 2, 2))
    if len(raw) != 128:
        raise ValueError('Region player head must occupy sixteen-square native pixels.')
    (destination / 'player.4bpp').write_bytes(raw)
    shutil.copyfile(source / 'courier.gbapal', destination / 'player.gbapal')


def apply_city_map(content, root, engine, original):
    image, atlas, regular, affine, palette, hubs, _ = make_map(root)
    asset = root / ASSET
    expected = {'guide-map.bin': regular, 'region-map.bin': affine, 'palette.gbapal': palette}
    for name, data in expected.items():
        if (asset / name).read_bytes() != data:
            raise ValueError('Rebuild stale SF map asset: ' + name)
    from PIL import Image
    if Image.open(asset / 'tiles.png').tobytes() != atlas.tobytes():
        raise ValueError('Rebuild stale SF map atlas.')
    destination = engine / 'graphics/sf_city_map'
    destination.mkdir(parents=True, exist_ok=True)
    for name in (*expected, 'tiles.png'):
        shutil.copyfile(asset / name, destination / name)
    prepare_player_icon(root, destination)
    sections_path = 'src/data/region_map/region_map_sections.json'
    sections = json.loads((engine / sections_path).read_text())
    for hub in hubs:
        section = next(s for s in sections['map_sections'] if s['id'] == hub['section'])
        section.update({key: hub[key] for key in ('name', 'x', 'y', 'width', 'height')})
    (engine / sections_path).write_text(json.dumps(sections, indent=2) + '\n')
    grid = [['MAPSEC_NONE'] * 28 for _ in range(15)]
    for hub in hubs:
        grid[hub['y']][hub['x']] = hub['section']
    layout_path = 'src/data/region_map/region_map_layout.h'
    (engine / layout_path).write_text(
        'static const mapsec_u8_t sRegionMap_MapSectionLayout[MAP_HEIGHT][MAP_WIDTH] = {\n'
        + '\n'.join('    {' + ', '.join(row) + '},' for row in grid) + '\n};\n')
    # Derive both whitelists from the existing campaign source, never the stock graph.
    parents, authored_ids = [], set()
    for name in content['maps']:
        plan = json.loads((root / 'romhack/content' / name).read_text())
        metadata = json.loads(original('data/maps/' + plan['engine_map'] + '/map.json'))
        metadata.update(plan.get('metadata', {}))
        identifier, section = metadata['id'], metadata['region_map_section']
        if section not in {hub['section'] for hub in hubs}:
            raise ValueError('An authored map has no SF geographic parent.')
        parents.append((identifier, section))
        authored_ids.add(identifier)
    battles = json.loads((root / 'romhack/content' / content['battle_content']).read_text())
    encounters = [row['map'] for row in battles['encounters']]
    if not encounters or len(set(encounters)) != len(encounters) or not set(encounters) <= authored_ids:
        raise ValueError('SF habitat whitelist must contain unique authored encounter maps.')
    for identifier in authored_ids:
        if not re.fullmatch(r'MAP_[A-Z0-9_]+', identifier):
            raise ValueError('Invalid authored map constant.')
    (engine / 'src/sf_habitat_maps.h').write_text(
        'static const u8 sSFHabitatMapIds[][2] = {\n' + '\n'.join(
            '    {MAP_GROUP(%s), MAP_NUM(%s)},' % (identifier, identifier)
            for identifier in encounters) + '\n};\n')
    (engine / 'src/sf_city_map_parents.h').write_text(
        'static const u8 sSFRegionMapParents[][3] = {\n' + '\n'.join(
            '    {MAP_GROUP(%s), MAP_NUM(%s), %s},' % (identifier, identifier, section)
            for identifier, section in parents) + '\n};\n')
    path = 'src/region_map.c'
    source = original(path)
    source = replace(source, '"graphics/pokenav/region_map/map.pal", ".gbapal"',
                     '"graphics/sf_city_map/palette.gbapal", ""')
    # Raw native palette bytes, rather than treating a binary .gbapal as JASC text.
    source = replace(source, 'INCGFX_U16("graphics/sf_city_map/palette.gbapal", "")',
                     'INCBIN_U16("graphics/sf_city_map/palette.gbapal")')
    source = replace(source, '"graphics/pokenav/region_map/map.png"', '"graphics/sf_city_map/tiles.png"')
    source = replace(source, '"graphics/pokenav/region_map/map.bin"', '"graphics/sf_city_map/region-map.bin"')
    for name in ('brendan', 'may'):
        source = replace(source,
            f'INCGFX_U16("graphics/pokenav/region_map/{name}_icon.png", ".gbapal")',
            'INCBIN_U16("graphics/sf_city_map/player.gbapal")')
        source = replace(source,
            f'INCGFX_U8("graphics/pokenav/region_map/{name}_icon.png", ".4bpp")',
            'INCBIN_U8("graphics/sf_city_map/player.4bpp")')
    source = replace(source, 'static void InitMapBasedOnPlayerLocation(void)\n{',
                     '#include "sf_region_map_parent.h"\n\nstatic void InitMapBasedOnPlayerLocation(void)\n{')
    anchor = '    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_SS_TIDAL_CORRIDOR)\n'
    source = replace(source, anchor, '    if (SFInitRegionMapPlayer())\n        return;\n\n' + anchor)
    (engine / path).write_text(source)
    restored = [sections_path, layout_path, path]
    path = 'src/pokedex_area_region_map.c'
    source = original(path)
    source = replace(source, 'INCGFX_U16("graphics/pokedex/region_map.pal", ".gbapal")',
                     'INCBIN_U16("graphics/sf_city_map/palette.gbapal")')
    source = replace(source, '"graphics/pokedex/region_map.png"', '"graphics/sf_city_map/tiles.png"')
    source = replace(source, '"graphics/pokedex/region_map.bin"', '"graphics/sf_city_map/guide-map.bin"')
    (engine / path).write_text(source)
    restored.append(path)
    path = 'src/pokedex_area_screen.c'
    source = replace(original(path), 'static void FindMapsWithMon(u16 species)\n{',
        '#include "sf_habitat_map.h"\n\nstatic void UNUSED SFUnusedLegacyFindMapsWithMon(u16 species)\n{')
    (engine / path).write_text(source)
    restored.append(path)
    for source, target in [('habitat_map.h', 'sf_habitat_map.h'), ('region_map_parent.h', 'sf_region_map_parent.h')]:
        shutil.copyfile(root / 'romhack/engine' / source, engine / 'src' / target)
    return restored
