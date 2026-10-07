"""Compile authored SF map layouts into Emerald's native block/event formats."""
import json
import re
import struct
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
    for row in rows:
        for token in row:
            tile, blocked, elevation = legend[token]
            if not (0 <= tile < 1024 and type(blocked) is bool and 0 <= elevation < 16):
                raise ValueError('Invalid native metatile, collision or elevation.')
            blocks.append(tile | (0xC00 if blocked else 0) | elevation << 12)
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


def apply_maps(content, root, engine, original):
    plans = content.get('maps', [])
    if not plans:
        return []
    layouts_path = 'data/layouts/layouts.json'
    layouts = json.loads(original(layouts_path))
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
        blocks_path = layout['blockdata_filepath']
        (engine / blocks_path).write_bytes(blocks)
        restored.extend([map_path, blocks_path])
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
        # Defeat recovery must return to the same SF hub, never a stock house.
        path = 'src/data/heal_locations.json'
        healing = json.loads(original(path))
        for location in healing['heal_locations'][:2]:
            location.update(map='MAP_' + spawn['id'], x=spawn['x'], y=spawn['y'])
        (engine / path).write_text(json.dumps(healing, indent=2) + '\n')
        restored.append(path)
    return restored
