"""Compile authored SF map layouts into Emerald's native block/event formats."""
import json
import re
import struct
from copy import deepcopy
import shutil
from pathlib import Path


def encode_layout(plan):
    rows, legend = plan['rows'], plan['legend']
    if not rows or not 1 <= len(rows) <= 128:
        raise ValueError('Map height must be 1–128 tiles.')
    width = len(rows[0])
    if not 1 <= width <= 128 or any(len(row) != width for row in rows):
        raise ValueError('Map rows must have one consistent width of 1–128 tiles.')
    if (width + 15) * (len(rows) + 14) > 0x2800:
        raise ValueError('Map and native connection margins exceed the virtual-map buffer.')
    blocks = []
    base = plan.get('tile_grid_base')
    if base is not None and (type(base) is not int or base < 512 or base + width * len(rows) > 1024):
        raise ValueError('Backdrop tiles must fit the native secondary metatile range.')
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            tile, blocked, elevation = legend[token]
            if not (0 <= tile < 1024 and type(blocked) is bool and 0 <= elevation < 16):
                raise ValueError('Invalid native metatile, collision or elevation.')
            blocks.append((base + y * width + x if base is not None else tile) |
                          (0xC00 if blocked else 0) | elevation << 12)
    return width, len(rows), struct.pack('<' + 'H' * len(blocks), *blocks)


def check_position(plan, x, y, *, walkable=True):
    rows = plan['rows']
    if not (0 <= y < len(rows) and 0 <= x < len(rows[0])):
        raise ValueError(f'Event outside map: {x},{y}')
    if walkable and plan['legend'][rows[y][x]][1]:
        raise ValueError(f'Event occupies a blocked tile: {x},{y}')


def event_objects(plan):
    events, positions, identifiers = [], set(), set()
    for index, npc in enumerate(plan.get('npcs', []), 1):
        x, y = npc['x'], npc['y']
        check_position(plan, x, y)
        if (x, y) in positions or npc['id'] in identifiers:
            raise ValueError('NPC positions and local IDs must be unique.')
        positions.add((x, y))
        identifiers.add(npc['id'])
        if not 1 <= npc['id'] <= 255:
            raise ValueError('NPC local ID must fit the native object format.')
        if npc['id'] != index:
            raise ValueError('Append NPC IDs in native event order, starting at one.')
        events.append({
            'local_id': f'LOCALID_SF_{plan.get("engine_map", "TEST").upper()}_{npc["id"]}',
            'graphics_id': npc['graphics'], 'x': x, 'y': y,
            'elevation': plan['legend'][plan['rows'][y][x]][2],
            'movement_type': npc.get('movement', 'MOVEMENT_TYPE_FACE_DOWN'),
            'movement_range_x': npc.get('range_x', 0),
            'movement_range_y': npc.get('range_y', 0),
            'trainer_type': npc.get('trainer_type', 'TRAINER_TYPE_NONE'),
            'trainer_sight_or_berry_tree_id': str(npc.get('sight', 0)),
            'script': npc['script'], 'flag': npc.get('flag', '0')
        })
    if len(events) > 15:
        raise ValueError('A map must reserve one of sixteen active-object slots for the player.')
    return events


def validate_links(plans):
    """Map warps/connections may only reach other authored SF locations."""
    by_id = {plan['native_id']: plan for plan in plans}
    for plan in plans:
        for warp in plan.get('warp_events', []):
            target = by_id.get(warp['dest_map'])
            if target is None:
                raise ValueError('A warp leaves the authored SF map graph.')
            index = int(warp['dest_warp_id'])
            if not 0 <= index < len(target.get('warp_events', [])):
                raise ValueError('A warp targets an absent native arrival slot.')
        for connection in plan.get('connections') or []:
            if connection['map'] not in by_id:
                raise ValueError('A connection leaves the authored SF map graph.')


def recovery_locations(points, plans, native):
    """Replace declared native recovery slots with safe authored SF positions."""
    result = deepcopy(native)
    slots = {location['id']: location for location in result['heal_locations']}
    maps = {plan['native_id']: plan for plan in plans}
    declared = set()
    for point in points:
        identifier = point.get('id')
        if identifier not in slots or identifier in declared:
            raise ValueError('Recovery IDs must name unique existing native slots.')
        plan = maps.get(point.get('map'))
        if plan is None:
            raise ValueError('Recovery must stay inside the authored SF map graph.')
        x, y = point.get('x'), point.get('y')
        if type(x) is not int or type(y) is not int:
            raise ValueError('Recovery coordinates must be integer tiles.')
        check_position(plan, x, y)
        occupied = plan.get('npcs', []) + plan.get('warp_events', [])
        if any((event['x'], event['y']) == (x, y) for event in occupied):
            raise ValueError('Recovery cannot occupy an NPC or warp tile.')
        slots[identifier].update(map=point['map'], x=x, y=y)
        declared.add(identifier)
    return result


def validate_recovery_scripts(script, points):
    declared = {point['id'] for point in points}
    for identifier in re.findall(r'^\s*setrespawn\s+(\w+)\s*$', script, re.MULTILINE):
        if identifier not in declared:
            raise ValueError('An SF script registers an unauthored recovery slot.')


def apply_maps(content, root, engine, original):
    plans = content.get('maps', [])
    if not plans:
        return []
    layouts_path = 'data/layouts/layouts.json'
    layouts = json.loads(original(layouts_path))
    linked = []
    for reference in plans:
        plan = json.loads((root / 'romhack/content' / reference).read_text())
        plan['native_id'] = json.loads(original(f'data/maps/{plan["engine_map"]}/map.json'))['id']
        linked.append(plan)
    validate_links(linked)
    authored = '\n        || '.join(
        '(gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(%s)\n'
        '         && gSaveBlock1Ptr->location.mapNum == MAP_NUM(%s))'
        % (plan['native_id'], plan['native_id']) for plan in linked)
    (engine / 'src/sf_authored_maps.h').write_text(
        '#ifndef SF_AUTHORED_MAPS_H\n#define SF_AUTHORED_MAPS_H\n'
        '#include "constants/maps.h"\n'
        'static inline bool8 SFMapUsesAuthoredLayout(void)\n{\n'
        '    return ' + authored + ';\n}\n#endif\n')
    points = content.get('recovery_points', [])
    healing_path = 'src/data/heal_locations.json'
    healing = json.loads(original(healing_path))
    if 'spawn' in content:
        defaults = {location['id'] for location in healing['heal_locations'][:2]}
        if not defaults <= {point['id'] for point in points}:
            raise ValueError('Declare both native new-game recovery slots in SF content.')
    healing = recovery_locations(points, linked, healing)
    restored = [layouts_path]
    ids, aliases = set(), {}
    for reference in plans:
        source = (root / 'romhack/content' / reference).resolve()
        source.relative_to((root / 'romhack/content').resolve())
        plan = json.loads(source.read_text())
        width, height, blocks = encode_layout(plan)
        name = plan['engine_map']
        if not re.fullmatch(r'[A-Za-z0-9_]+', name) or name in ids:
            raise ValueError('Engine map names must be valid and unique.')
        ids.add(name)
        map_path = f'data/maps/{name}/map.json'
        metadata = json.loads(original(map_path))
        for index, event in enumerate(metadata['object_events'], 1):
            if 'local_id' in event:
                aliases[event['local_id']] = index
        layout = next(item for item in layouts['layouts'] if item['id'] == metadata['layout'])
        layout.update(width=width, height=height)
        for role, tileset in plan.get('tilesets', {}).items():
            if role not in ['primary', 'secondary'] or not re.fullmatch(r'gTileset_[A-Za-z0-9]+', tileset):
                raise ValueError('Tileset role/name is invalid.')
            layout[role + '_tileset'] = tileset
        blocks_path = layout['blockdata_filepath']
        (engine / blocks_path).write_bytes(blocks)
        restored.extend([map_path, blocks_path])
        if 'border_tile' in plan:
            tile = plan['border_tile']
            if type(tile) is not int or not 0 <= tile < 1024:
                raise ValueError('Border metatile must fit the native map word.')
            border_path = layout['border_filepath']
            (engine / border_path).write_bytes(struct.pack('<4H', *([tile | 0x3c00] * 4)))
            restored.append(border_path)
        for field in ['warp_events', 'coord_events', 'bg_events']:
            metadata[field] = plan.get(field, [])
            for event in metadata[field]:
                check_position(plan, event['x'], event['y'], walkable=field != 'bg_events')
        metadata['connections'] = plan.get('connections')
        metadata['object_events'] = event_objects(plan)
        metadata.update(plan.get('metadata', {}))
        (engine / map_path).write_text(json.dumps(metadata, indent=2) + '\n')
        script_path = f'data/maps/{name}/scripts.inc'
        script_source = (source.parent / plan['script']).resolve()
        script_source.relative_to((root / 'romhack/content').resolve())
        script = script_source.read_text()
        validate_recovery_scripts(script, points)
        for text in re.findall(r'\.string "(.*?)"', script):
            if not text.endswith('$') or '$' in text[:-1]:
                raise ValueError('SF text must have one final $ terminator; spell out currency.')
        symbol = name + '_MapScripts::'
        if script.count(symbol) != 1:
            raise ValueError('SF script must define exactly one native map-script header.')
        # Keep external stock script symbols available without running their map header.
        inherited = original(script_path).replace(symbol, 'SF_Stock_' + symbol, 1)
        (engine / script_path).write_text(inherited + '\n' + script)
        restored.append(script_path)
    (engine / layouts_path).write_text(json.dumps(layouts, indent=2) + '\n')
    # Inherited scripts/C still reference old local IDs even when unreachable.
    path = 'include/constants/event_objects.h'
    compatibility = '\n'.join(f'#ifndef {name}\n#define {name} {value}\n#endif'
                              for name, value in sorted(aliases.items()))
    (engine / path).write_text(original(path) + '\n' + compatibility + '\n')
    restored.append(path)
    (engine / healing_path).write_text(json.dumps(healing, indent=2) + '\n')
    restored.append(healing_path)
    if 'spawn' in content:
        spawn = content['spawn']
        plan = next(json.loads((root / 'romhack/content' / p).read_text())
                    for p in plans if json.loads((root / 'romhack/content' / p).read_text())['engine_map'] == spawn['map'])
        check_position(plan, spawn['x'], spawn['y'])
        path = 'src/new_game.c'
        before = 'SetWarpDestination(MAP_GROUP(MAP_INSIDE_OF_TRUCK), MAP_NUM(MAP_INSIDE_OF_TRUCK), WARP_ID_NONE, -1, -1);'
        after = (f'SetWarpDestination(MAP_GROUP(MAP_{spawn["id"]}), MAP_NUM(MAP_{spawn["id"]}), '
                 f'WARP_ID_NONE, {spawn["x"]}, {spawn["y"]});')
        source = original(path)
        if source.count(before) != 1:
            raise ValueError('Pinned new-game spawn anchor changed.')
        (engine / path).write_text(source.replace(before, after))
        restored.append(path)
        path = 'src/overworld.c'
        source = original(path)
        before = 'gFieldCallback = ExecuteTruckSequence;'
        if source.count(before) != 1:
            raise ValueError('Pinned new-game field callback changed.')
        (engine / path).write_text(source.replace(before, 'gFieldCallback = NULL;'))
        restored.append(path)
    # SF map state is rebuilt by its on-load scripts, including the gym gate.
    # A cached view from an older patch must not paint over a new layout.
    path = 'src/fieldmap.c'
    source = original(path)
    source = source.replace('#include "fieldmap.h"',
                            '#include "fieldmap.h"\n#include "sf_authored_maps.h"', 1)
    if source.count('    LoadSavedMapView();') != 1:
        raise ValueError('Pinned saved-map-view hook changed.')
    (engine / path).write_text(source.replace('    LoadSavedMapView();',
        '    if (!SFMapUsesAuthoredLayout())\n        LoadSavedMapView();', 1))
    restored.append(path)
    shutil.copy2(root / 'romhack/engine/map_resume.h', engine / 'src/sf_map_resume.h')
    path = 'src/overworld.c'
    source = (engine / path).read_text()
    anchor = 'void CB2_ContinueSavedGame(void)'
    if source.count(anchor) != 1 or source.count('    if (UseContinueGameWarp() == TRUE)') != 1:
        raise ValueError('Pinned saved-position hook changed.')
    source = source.replace(anchor, '#include "sf_map_resume.h"\n\n' + anchor, 1)
    source = source.replace('    if (UseContinueGameWarp() == TRUE)',
        '    if (SFMapResumeWarpIfNeeded())\n'
        '    {\n        WarpIntoMap();\n        TryPutTodaysRivalTrainerOnAir();\n'
        '        SetMainCallback2(CB2_LoadMap);\n    }\n'
        '    else if (UseContinueGameWarp() == TRUE)', 1)
    (engine / path).write_text(source)
    if path not in restored:
        restored.append(path)
    return restored
