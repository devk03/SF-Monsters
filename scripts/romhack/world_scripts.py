"""Native blockout events: labels, safe gym warps and explicit access stamps."""


def text(label, lines):
    return label + '::\n    .string "' + r'\n'.join(lines) + '$"\n'


def map_script(manifest, plan):
    identifier = plan['world_id']
    prefix = 'WB_' + identifier
    start = identifier == manifest['start']['area']
    gym = next((g for g in manifest['gyms'] if g['id'] == identifier), None)
    entry = next((g for g in manifest['gyms'] if g['area'] == identifier), None)
    lines = [plan['engine_map'] + '_MapScripts::',
             '    map_script MAP_SCRIPT_ON_TRANSITION, ' + prefix + '_Load',
             '    .byte 0', '', prefix + '_Load::',
             '    setvar VAR_REPEL_STEP_COUNT, 250']
    if start:
        lines += ['    compare VAR_UNUSED_0x40F8, ' + str(manifest['native']['save_magic']),
                  '    goto_if_eq ' + prefix + '_Ready',
                  '    setvar VAR_UNUSED_0x40F8, ' + str(manifest['native']['save_magic']),
                  '    setvar VAR_UNUSED_0x40F9, 1',
                  '    setflag FLAG_SYS_POKEMON_GET', '    setflag FLAG_SYS_B_DASH',
                  '    givemon SPECIES_MARILL, 100',
                  '    setmonmove 0, 0, MOVE_SURF',
                  '    setmonmove 0, 1, MOVE_WATERFALL',
                  '    setrespawn HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F',
                  prefix + '_Ready::']
    lines += ['    end', '', prefix + '_Info::', '    lock', '    faceplayer']
    messages = []
    if gym:
        n = gym['badge']
        if n > 1:
            lines += [f'    checkflag FLAG_BADGE{n-1:02d}_GET',
                      '    goto_if_unset ' + prefix + '_Locked']
        if n == 8:
            lines += ['    compare VAR_UNUSED_0x40FC, 1',
                      '    goto_if_ne ' + prefix + '_Locked']
        lines += [f'    setflag FLAG_BADGE{n:02d}_GET',
                  '    msgbox ' + prefix + '_Text, MSGBOX_DEFAULT']
        messages += [text(prefix + '_Text', [f'Gym {n}: ' + gym['theme'].replace('_', ' '),
                                            'BLOCKOUT ACCESS STAMP.',
                                            'No leader battle is built yet.'])]
        if n > 1:
            lines += ['    release', '    end', prefix + '_Locked::',
                      '    msgbox ' + prefix + '_Wait, MSGBOX_DEFAULT']
            messages += [text(prefix + '_Wait', ['Return after the prior stamp.',
                                                 'Final stamp also needs the',
                                                 'island, tower and coast checks.'])]
    elif identifier == 'treasure_island':
        lines += ['    setvar VAR_UNUSED_0x40FA, 1',
                  '    msgbox ' + prefix + '_Text, MSGBOX_DEFAULT']
        messages += [text(prefix + '_Text', ['Treasure Island checkpoint.',
                                            'Next: Sutro Tower, then',
                                            'Lands End. Return paths stay open.'])]
    elif identifier in ('sutro_tower', 'lands_end'):
        required = 'VAR_UNUSED_0x40FA' if identifier == 'sutro_tower' else 'VAR_UNUSED_0x40FB'
        granted = 'VAR_UNUSED_0x40FB' if identifier == 'sutro_tower' else 'VAR_UNUSED_0x40FC'
        lines += [f'    compare {required}, 1', '    goto_if_ne ' + prefix + '_Wait',
                  f'    setvar {granted}, 1',
                  '    msgbox ' + prefix + '_Text, MSGBOX_DEFAULT',
                  '    release', '    end', prefix + '_Wait::',
                  '    msgbox ' + prefix + '_WaitText, MSGBOX_DEFAULT']
        messages += [text(prefix + '_Text', [plan['label'], 'Story checkpoint recorded.',
                                            'Scene and quest remain placeholders.']),
                     text(prefix + '_WaitText', ['Visit the prior story checkpoint.',
                                                'Treasure Island, Sutro Tower,',
                                                'then Lands End.'])]
    else:
        # Keep native textbox lines readable at the standard 240-pixel display.
        words, rows, row = plan['label'].split(), [], ''
        for word in words:
            if len(row + word) > 28:
                rows.append(row.rstrip())
                row = ''
            row += word + ' '
        rows.append(row.rstrip())
        lines += ['    msgbox ' + prefix + '_Text, MSGBOX_DEFAULT']
        messages += [text(prefix + '_Text', rows + ['WORLD BLOCKOUT - draft geometry.',
                                                   'Routes and gym entries are live.'])]
    lines += ['    release', '    end']
    if entry:
        from generate_world import native_id
        lines += ['', prefix + '_Enter::',
                  f'    warp {native_id(entry["engine_map"])}, 16, 16',
                  '    waitstate', '    end']
    if gym:
        from generate_world import native_id
        area = next(a for a in manifest['areas'] if a['id'] == gym['area'])
        lines += ['', prefix + '_Exit::',
                  f'    warp {native_id(area["engine_map"])}, 16, 10',
                  '    waitstate', '    end']
    return '\n'.join(lines) + '\n\n' + '\n'.join(messages)
