"""Read linked cartridge tables independently of the world map encoder."""
import json
import re
import struct
import subprocess


def audit_native(rom_path, elf_path, plans, engine):
    rom = rom_path.read_bytes()
    symbols = {}
    for line in subprocess.check_output(
            ['arm-none-eabi-nm', '--defined-only', str(elf_path)], text=True).splitlines():
        fields = line.split()
        if len(fields) == 3:
            symbols[fields[2]] = int(fields[0], 16)

    def read(address, fmt):
        offset = address - 0x08000000
        size = struct.calcsize('<' + fmt)
        if not 0 <= offset <= len(rom) - size:
            raise ValueError('Compiled table points outside cartridge.')
        return struct.unpack_from('<' + fmt, rom, offset)

    def constants(name):
        source = (engine / 'include/constants' / name).read_text()
        return {key:int(value,0) for key,value in re.findall(
            r'^#define\s+(\w+)\s+(0x[0-9A-Fa-f]+|[0-9]+)\b',source,re.MULTILINE)}
    motions = constants('event_object_movement.h')
    graphics = constants('event_objects.h')
    flag_values = constants('flags.h')
    unique_layouts = set()
    groups = json.loads((engine / 'data/maps/map_groups.json').read_text())
    ids = {name: (g, n) for g, group in enumerate(groups['group_order'])
           for n, name in enumerate(groups[group])}
    native_to_name = {plan['native_id']: plan['engine_map'] for plan in plans}
    directions = {'down': 1, 'up': 2, 'left': 3, 'right': 4}
    errors, tiles, connections, objects, coords = [], 0, 0, 0, 0
    for plan in plans:
        name = plan['engine_map']
        group, number = ids[name]
        group_ptr, = read(symbols['gMapGroups'] + group * 4, 'I')
        header_ptr, = read(group_ptr + number * 4, 'I')
        if header_ptr != symbols[name]:
            errors.append(name + ': native group table selects a different header')
        layout, events, scripts, conn = read(symbols[name], '4I')
        if plan.get('unique_layout'):
            if layout in unique_layouts:
                errors.append(name + ': authored maps share a native layout')
            unique_layouts.add(layout)
        width, height, border, blocks = read(layout, '4I')
        primary, secondary = read(layout + 16, '2I')
        if (primary, secondary) != tuple(symbols[plan['tilesets'][role]]
                                         for role in ('primary', 'secondary')):
            errors.append(name + ': compiled tileset pointers differ')
        # Original SF secondary cards have normal ground behavior and use the
        # bottom/middle layers. Roof collision comes from the authored map;
        # no custom card may secretly become a ledge, door or overhead bridge.
        used = {tile for row in plan['rows'] for tile, _, _ in
                (plan['legend'][token] for token in row) if tile >= 512}
        if used:
            attrs, = read(secondary + 16, 'I')
            for tile in used:
                behavior, = read(attrs + (tile-512)*2, 'H')
                if behavior != (0x1080 if tile in (607,608) else 0x1000):
                    errors.append(name + ': SF tile has unexpected behavior/layer')
        if (width, height) != (len(plan['rows'][0]), len(plan['rows'])):
            errors.append(name + ': compiled dimensions differ')
        actual = read(blocks, str(width * height) + 'H')
        expected = tuple(tile | (0xC00 if blocked else 0) | elevation << 12
                         for row in plan['rows'] for tile, blocked, elevation in
                         (plan['legend'][token] for token in row))
        if actual != expected:
            errors.append(name + ': compiled tile/collision/elevation differs')
        tiles += len(expected)
        counts = read(events, '4B')
        if counts != (len(plan['npcs']), 0, len(plan['coord_events']), 0):
            errors.append(name + ': compiled event counts differ')
        obj_ptr, _, coord_ptr, _ = read(events + 4, '4I')
        for i, npc in enumerate(plan['npcs']):
            x, y = read(obj_ptr + i * 24 + 4, '2h')
            script, = read(obj_ptr + i * 24 + 16, 'I')
            if (x, y, script) != (npc['x'], npc['y'], symbols[npc['script']]):
                errors.append(name + ': compiled NPC position/script differs')
            elevation,movement,ranges = read(obj_ptr + i*24 + 8,'3B')
            gfx, = read(obj_ptr + i*24 + 1,'B')
            expected_motion = motions[npc.get('movement','MOVEMENT_TYPE_FACE_DOWN')]
            expected_ranges = npc.get('range_x',0) | npc.get('range_y',0)<<4
            if (gfx,movement,ranges,elevation) != (graphics[npc['graphics']],expected_motion,
                    expected_ranges,plan['legend'][plan['rows'][npc['y']][npc['x']]][2]):
                errors.append(name + ': compiled actor graphics/movement/envelope differs')
            local_id, = read(obj_ptr + i*24,'B')
            visibility, = read(obj_ptr + i*24 + 20,'H')
            flag = npc.get('flag','0')
            expected_flag = flag_values[flag] if flag in flag_values else int(str(flag),0)
            if (local_id,visibility)!=(npc['id'],expected_flag):
                errors.append(name + ': compiled actor identity/visibility differs')
            objects += 1
        for i, event in enumerate(plan['coord_events']):
            x, y = read(coord_ptr + i * 16, '2h')
            elevation, = read(coord_ptr + i * 16 + 4, 'B')
            variable, value = read(coord_ptr + i * 16 + 6, '2H')
            script, = read(coord_ptr + i * 16 + 12, 'I')
            if (x, y, script) != (event['x'], event['y'], symbols[event['script']]):
                errors.append(name + ': compiled coordinate trigger differs')
            if (elevation, variable, value) != (event['elevation'], 0x4000, 0):
                errors.append(name + ': native trigger elevation/condition differs')
            coords += 1
        expected_links = plan['connections'] or []
        count, pointer = read(conn, '2I') if conn else (0, 0)
        if count != len(expected_links):
            errors.append(name + ': compiled connection count differs')
        for i, link in enumerate(expected_links):
            direction, offset, group, number = read(pointer + i * 12, 'B3xi2B')
            target = native_to_name[link['map']]
            if (direction, offset, group, number) != (
                    directions[link['direction']], link['offset'], *ids[target]):
                errors.append(name + ': compiled connection destination differs')
            connections += 1
        if scripts != symbols[name + '_MapScripts']:
            errors.append(name + ': inherited stock map script active')
    return {'passed': not errors, 'errors': errors,
            'counts': {'maps': len(plans), 'tiles': tiles, 'connections': connections,
                       'npcs': objects, 'coord_events': coords},
            'scope': 'linked layout/event/connection integrity; not controller traversal'}
