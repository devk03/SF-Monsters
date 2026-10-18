"""Compile small return-path masks; Continue needs no flood-fill on GBA stack."""
from collections import deque


def return_mask(plan, stage):
    rows, legend = plan['rows'], plan['legend']
    width, height = len(rows[0]), len(rows)
    occupied = {(x, y) for npc in plan['npcs']
                for x in range(npc['x'] - npc.get('range_x', 0), npc['x'] + npc.get('range_x', 0) + 1)
                for y in range(npc['y'] - npc.get('range_y', 0), npc['y'] + npc.get('range_y', 0) + 1)}
    exits = {(point['x'], point['y']) for point in plan['access_points']
             if point['kind'] in ('room_exit', 'gym_exit')}
    triggers = {(event['x'], event['y']) for event in plan['coord_events']} - exits
    for link in plan['connections'] or []:
        side = link['direction']
        for delta in (-1, 0, 1):
            exits.add({'up': (width // 2 + delta, 0),
                       'down': (width // 2 + delta, height - 1),
                       'left': (0, height // 2 + delta),
                       'right': (width - 1, height // 2 + delta)}[side])
    def allowed(point):
        x, y = point
        if not (0 <= x < width and 0 <= y < height) or point in occupied | triggers:
            return False
        tile, blocked, _ = legend[rows[y][x]]
        return not blocked and (tile != 368 or stage >= 5) and (tile != 179 or stage >= 8)
    reached = {point for point in exits if allowed(point)}
    queue = deque(reached)
    while queue:
        x, y = queue.popleft()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if point not in reached and allowed(point):
                reached.add(point)
                queue.append(point)
    result = bytearray((width * height + 7) // 8)
    for x, y in reached:
        bit = y * width + x
        result[bit // 8] |= 1 << (bit % 8)
    return bytes(result)


def header(plans, spawn):
    start = next(plan for plan in plans if plan['engine_map'] == spawn['map'])
    bit = spawn['y'] * len(start['rows'][0]) + spawn['x']
    if not (return_mask(start, 0)[bit // 8] & 1 << (bit % 8)):
        raise ValueError('Emergency Continue landing needs an ungated path to an exit')
    if any((p['x'],p['y']) == (spawn['x'],spawn['y']) for p in start['coord_events']):
        raise ValueError('Emergency Continue landing cannot be a coordinate trigger')
    lines = ['// Generated from authored collision, movement envelopes and exits.',
             'struct SFResumeArea { u8 group, number, width, height; const u8 *masks[3]; };']
    for index, plan in enumerate(plans):
        for stage in (0, 5, 8):
            data = ','.join(str(byte) for byte in return_mask(plan, stage))
            lines.append(f'static const u8 sSFResumeMask{index}_{stage}[] = {{{data}}};')
    lines.append('static const struct SFResumeArea sSFResumeAreas[] = {')
    for index, plan in enumerate(plans):
        native = plan['native_id']
        masks = ','.join(f'sSFResumeMask{index}_{stage}' for stage in (0, 5, 8))
        lines.append(f'{{MAP_GROUP({native}),MAP_NUM({native}),'
                     f'{len(plan["rows"][0])},{len(plan["rows"])},{{{masks}}}}},')
    lines += ['};', 'static bool8 SFResumeCanReturn(s16 x, s16 y)', '{',
              '    u16 i, bit;',
              '    u8 stage = FlagGet(FLAG_BADGE05_GET) ? (FlagGet(FLAG_BADGE08_GET) ? 2 : 1) : 0;',
              '    for (i = 0; i < ARRAY_COUNT(sSFResumeAreas); i++)', '    {',
              '        const struct SFResumeArea *area = &sSFResumeAreas[i];',
              '        if (area->group != gSaveBlock1Ptr->location.mapGroup',
              '            || area->number != gSaveBlock1Ptr->location.mapNum) continue;',
              '        if (x < 0 || y < 0 || x >= area->width || y >= area->height) return FALSE;',
              '        bit = y * area->width + x;',
              '        return (area->masks[stage][bit / 8] >> (bit % 8)) & 1;',
              '    }', '    return FALSE;', '}',
              'static bool8 SFResumeFallback(void)', '{',
              '    ResetInitialPlayerAvatarState();',
              f'    SetWarpDestination(MAP_GROUP({start["native_id"]}), MAP_NUM({start["native_id"]}),',
              f'                       WARP_ID_NONE, {spawn["x"]}, {spawn["y"]});',
              '    return TRUE;', '}', '']
    return '\n'.join(lines)
