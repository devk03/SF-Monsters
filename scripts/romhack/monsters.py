"""Apply original creature data and native-format art without changing save IDs."""
from pathlib import Path
import json
import re
import shutil
import struct
from battle_content import constant


def replace_one(source, pattern, value):
    source, count = re.subn(pattern, lambda match: value, source, flags=re.M | re.S)
    if count != 1: raise ValueError('Pinned species anchor changed: ' + pattern)
    return source


def check_monster(mon):
    constant(mon['species'], 'SPECIES_')
    for field in ['old_name', 'name', 'category']:
        # categoryName[12] also stores the native text terminator.
        if not re.fullmatch(r'[A-Z0-9 ]{1,%d}' % (11 if field == 'category' else 10), mon[field]):
            raise ValueError('Creature names must fit the native text fields.')
    if not re.fullmatch(r'[A-Z][A-Za-z]+', mon['symbol']) or not re.fullmatch(r'[a-z_]+', mon['engine_asset_dir']):
        raise ValueError('Unsafe native species symbol or asset path.')
    required = {'baseHP', 'baseAttack', 'baseDefense', 'baseSpeed', 'baseSpAttack', 'baseSpDefense'}
    if set(mon['stats']) != required or any(type(value) is not int or not 1 <= value <= 255 for value in mon['stats'].values()):
        raise ValueError('Creature needs all six valid base stats.')
    for key, prefix in [('types', 'TYPE_'), ('abilities', 'ABILITY_')]:
        if len(mon[key]) != 2: raise ValueError('Native type/ability tables need two entries.')
        for value in mon[key]: constant(value, prefix)
    previous = 0
    for level, move in mon['learnset']:
        if type(level) is not int or not previous <= level <= 100 or level < 1: raise ValueError('Learnset levels must be ordered.')
        previous = level; constant(move, 'MOVE_')
    if not mon['learnset']: raise ValueError('Creature needs a learnset.')
    level, move = mon['migration_move']; constant(move, 'MOVE_')
    if [level, move] not in mon['learnset']: raise ValueError('Migration move must be earned in the learnset.')
    if any(type(mon[key]) is not int or not 1 <= mon[key] <= 65535 for key in ['height', 'weight']): raise ValueError('Invalid field-guide size.')
    if not 3 <= mon['icon_palette'] <= 5: raise ValueError('Original icons use reserved palette groups 3–5.')
    for side in ['front', 'back']:
        width, height, offset = mon['coordinates'][side]
        if any(type(value) is not int for value in [width, height, offset]) or width not in range(8, 65, 8) or height not in range(8, 65, 8) or not 0 <= offset <= 32:
            raise ValueError('Sprite bounds must fit native coordinate packing and ground alignment.')
    if len(mon['description']) != 3 or any(not re.fullmatch(r"[A-Za-z0-9 ,.!'-]{1,38}", line) for line in mon['description']):
        raise ValueError('Field-guide description needs three safe short lines.')
    evolutions = mon.get('evolutions', [])
    if len(evolutions) > 1:
        raise ValueError('Declare one unconditional level evolution per creature.')
    for evolution in evolutions:
        if set(evolution) != {'level', 'species'} or type(evolution['level']) is not int or not 2 <= evolution['level'] <= 100:
            raise ValueError('Level evolution needs a target and a threshold from 2–100.')
        constant(evolution['species'], 'SPECIES_')
        if evolution['species'] == mon['species']:
            raise ValueError('A creature cannot evolve into itself.')


def check_catalog(monsters):
    records = {}
    names, symbols, paths = set(), set(), set()
    for mon in monsters:
        check_monster(mon)
        if mon['species'] in records: raise ValueError('Species IDs must be unique.')
        if mon['name'] in names or mon['symbol'] in symbols or mon['engine_asset_dir'] in paths:
            raise ValueError('Creature names, engine symbols and asset destinations must be unique.')
        names.add(mon['name']); symbols.add(mon['symbol']); paths.add(mon['engine_asset_dir'])
        records[mon['species']] = mon
    for mon in monsters:
        visited, current = set(), mon
        previous_level = 0
        while current.get('evolutions'):
            species = current['species']
            if species in visited: raise ValueError('Evolution lines cannot contain cycles.')
            visited.add(species)
            rule = current['evolutions'][0]
            if rule['species'] not in records:
                raise ValueError('An original evolution must target an authored creature.')
            if rule['level'] <= previous_level:
                raise ValueError('Later evolution thresholds must increase.')
            previous_level = rule['level']
            current = records[rule['species']]


def png_palette(path, expected_size):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack_from('>II', data, 16) != expected_size or data[25] != 3:
        raise ValueError('Creature art must be native-size indexed PNG.')
    offset, palette, transparency = 8, None, None
    while offset < len(data):
        length = struct.unpack_from('>I', data, offset)[0]; kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        if kind == b'PLTE': palette = payload
        if kind == b'tRNS': transparency = payload
        offset += length + 12
    if palette is None or len(palette) != 48 or transparency != b'\x00':
        raise ValueError('Art must share sixteen colors with transparent index zero.')
    return palette


def apply_monsters(content, root, engine, original):
    if 'monster_content' not in content: return []
    reference = (root / 'romhack/content' / content['monster_content']).resolve()
    reference.relative_to(root / 'romhack/content')
    data = json.loads(reference.read_text()); changed, source, records, identifiers = [], {}, [], set()
    if not data['monsters'] or type(data['content_revision']) is not int or not 1 <= data['content_revision'] <= 65535:
        raise ValueError('Species content needs entries and a valid persistent revision.')
    check_catalog(data['monsters'])
    icon_palettes, icon_paths = {}, {}
    for group, reference in data['icon_palettes'].items():
        if group not in ['3', '4', '5']: raise ValueError('Original icon palette group is not reserved.')
        palette_source = (root / reference).resolve(); palette_source.relative_to(root / 'assets')
        lines = palette_source.read_text().splitlines()
        if lines[:3] != ['JASC-PAL', '0100', '16'] or len(lines) != 19:
            raise ValueError('Icon palette needs sixteen JASC colors.')
        icon_palettes[int(group)] = bytes(int(channel) for line in lines[3:] for channel in line.split())
        if len(icon_palettes[int(group)]) != 48: raise ValueError('Icon colors need three channels each.')
        icon_paths[int(group)] = f'graphics/pokemon/icon_palettes/sf_icon_palette_{group}.pal'
        shutil.copy2(palette_source, engine / icon_paths[int(group)])

    def edit(path, pattern, value):
        source[path] = replace_one(source.get(path, original(path)), pattern, value)

    for mon in data['monsters']:
        check_monster(mon); species, symbol = mon['species'], mon['symbol']
        if species in identifiers: raise ValueError('Species IDs must be unique.')
        identifiers.add(species)
        art = (root / mon['art']).resolve(); art.relative_to(root / 'assets/monsters')
        destination = 'graphics/pokemon/' + mon['engine_asset_dir']
        palettes = []
        for name, size in [('front', (64, 64)), ('anim_front', (64, 128)), ('back', (64, 64))]:
            palettes.append(png_palette(art / (name + '.png'), size))
        if any(palette != palettes[0] for palette in palettes): raise ValueError('Creature views must share a palette.')
        if png_palette(art / 'icon.png', (32, 64)) != icon_palettes.get(mon['icon_palette']):
            raise ValueError('Party icon does not match its shared native palette group.')
        for name in ['front.png', 'anim_front.png', 'back.png', 'icon.png', 'normal.pal', 'shiny.pal']:
            path = destination + '/' + name; shutil.copy2(art / name, engine / path); changed.append(path)
        edit('src/data/text/species_names.h', rf'\[{species}\] = _\("[^"]*"\)', f'[{species}] = _("{mon["name"]}")')
        path = 'src/data/pokemon/species_info.h'
        info = source.get(path, original(path))
        pattern = rf'^    \[{species}\] =\n    \{{.*?^    \}},'
        match = re.search(pattern, info, re.M | re.S)
        if not match: raise ValueError('Unknown pinned species ID.')
        record = match.group()
        for field, value in mon['stats'].items(): record = replace_one(record, rf'\.{field}\s*=\s*\d+', f'.{field} = {value}')
        for field in ['types', 'abilities']: record = replace_one(record, rf'\.{field}\s*=\s*\{{[^}}]*\}}', '.%s = {%s}' % (field, ', '.join(mon[field])))
        edit(path, pattern, record)
        if 'evolutions' in mon:
            path = 'src/data/pokemon/evolution.h'
            value = source.get(path, original(path))
            rules = ', '.join('{EVO_LEVEL, %d, %s}' % (rule['level'], rule['species'])
                              for rule in mon['evolutions']) or '{0}'
            record = f'    [{species}] = {{{rules}}},'
            pattern = rf'^    \[{species}\]\s*=\s*\{{\{{.*?\}}\}},'
            if re.search(pattern, value, re.M | re.S):
                source[path] = replace_one(value, pattern, record)
            else:
                source[path] = replace_one(value, r'\n\};\s*\Z', '\n' + record + '\n};\n')
        moves = ',\n'.join(f'    LEVEL_UP_MOVE({level}, {move})' for level, move in mon['learnset'])
        edit('src/data/pokemon/level_up_learnsets.h', rf'static const u16 s{symbol}LevelUpLearnset\[\] = \{{.*?\n\}};',
             f'static const u16 s{symbol}LevelUpLearnset[] = {{\n{moves},\n    LEVEL_UP_END\n}};')
        for side in ['front', 'back']:
            width, height, offset = mon['coordinates'][side]
            edit(f'src/data/pokemon_graphics/{side}_pic_coordinates.h', rf'\[{species}\]\s*=\s*\{{[^}}]*\}}',
                 f'[{species}] = {{ .size = MON_COORDS_SIZE({width}, {height}), .y_offset = {offset} }}')
        edit('src/data/pokemon_graphics/front_pic_anims.h', rf'static const union AnimCmd sAnim_{symbol}_1\[\] =\n\{{.*?\n\}};',
             f'static const union AnimCmd sAnim_{symbol}_1[] = {{\n    ANIMCMD_FRAME(0, 12),\n    ANIMCMD_FRAME(1, 6),\n    ANIMCMD_FRAME(0, 10),\n    ANIMCMD_END,\n}};')
        edit('src/pokemon_icon.c', rf'\[{species}\] = \d+,', f'[{species}] = {mon["icon_palette"]},')
        text = '\n'.join('    "' + line + ('\\n' if index < 2 else '') + '"' for index, line in enumerate(mon['description']))
        edit('src/data/pokemon/pokedex_text.h', rf'const u8 g{symbol}PokedexText\[\] = _\(.*?\);', f'const u8 g{symbol}PokedexText[] = _(\n{text});')
        path = 'src/data/pokemon/pokedex_entries.h'; dex = species.replace('SPECIES_', 'NATIONAL_DEX_')
        pattern = rf'^    \[{dex}\] =\n    \{{.*?^    \}},'; match = re.search(pattern, original(path), re.M | re.S)
        record = replace_one(match.group(), r'\.categoryName = _\("[^"]*"\)', f'.categoryName = _("{mon["category"]}")')
        for field in ['height', 'weight']: record = replace_one(record, rf'\.{field} = \d+', f'.{field} = {mon[field]}')
        edit(path, pattern, record)
        level, move = mon['migration_move']; records.append(f'    {{{species}, _("{mon["old_name"]}"), {level}, {move}}},')
    # Three original icon groups occupy the engine's already-reserved tags.
    fallback = next(iter(icon_paths.values()))
    addition = '\n'.join('    INCGFX_U16("%s", ".gbapal"),' % icon_paths.get(group, fallback) for group in range(3, 6))
    edit('src/graphics.c', r'(const u16 gMonIconPalettes\[\]\[16\] =\n\{.*?)(\n\};)',
         re.search(r'const u16 gMonIconPalettes\[\]\[16\] =\n\{.*?(?=\n\};)', original('src/graphics.c'), re.S).group() + '\n' + addition + '\n};')
    for path, value in source.items(): (engine / path).write_text(value); changed.append(path)
    migration = (root / 'romhack/engine/species_migration.h').read_text().replace('    // SF_SPECIES_RECORDS', '\n'.join(records))
    (engine / 'src/sf_species_migration.h').write_text('#define SF_SPECIES_CONTENT_REVISION %d\n' % data['content_revision'] + migration)
    path = 'src/overworld.c'; value = (engine / path).read_text()
    value = replace_one(value, r'void CB2_ContinueSavedGame\(void\)\n\{\n    u8 trainerHillMapId;',
                        '#include "sf_species_migration.h"\n\nvoid CB2_ContinueSavedGame(void)\n{\n    u8 trainerHillMapId;\n    SFUpgradeSpeciesContent();')
    (engine / path).write_text(value); changed.append(path)
    return changed
