"""Explicit private fresh-game test bench, never campaign progression evidence."""
import json
import re

MAGIC = 0x4D51


def apply_playtest(directory, content, modules, identifier, scenario):
    module = modules[identifier]
    if module['meta']['status'] == 'stub':
        raise ValueError('Set the assigned module to draft before requesting its playtest')
    contract = module['contract']
    target = json.loads((directory / (contract['world_id'] + '.json')).read_text())
    point = (16, 16)
    if target['legend'][target['rows'][point[1]][point[0]]][1] or any(
            (n['x'], n['y']) == point for n in target['npcs']):
        raise ValueError('Module QA arrival (16,16) must remain free and walkable')
    content['spawn'] = dict(map=target['engine_map'], id=target['native_id'][4:], x=16, y=16)
    for recovery in content['recovery_points']:
        recovery.update(map=target['native_id'], x=16, y=16)
    init = ['    compare VAR_UNUSED_0x40F8, ' + str(MAGIC),
            '    goto_if_eq SFModuleQA_Ready',
            '    setvar VAR_UNUSED_0x40F8, ' + str(MAGIC),
            '    setvar VAR_UNUSED_0x40F9, 1', '    setflag FLAG_SYS_POKEMON_GET',
            '    setflag FLAG_SYS_B_DASH',
            '    givemon SPECIES_MARILL, ' + ('1' if scenario == 'weak-party' else '100'),
            '    setmonmove 0, 0, MOVE_SURF', '    setmonmove 0, 1, MOVE_WATERFALL',
            '    setrespawn HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F']
    if scenario != 'locked':
        for badge in range(1, contract['requires_badge'] + 1):
            init.append(f'    setflag FLAG_BADGE{badge:02d}_GET')
        if contract.get('requires_checkpoint'):
            # Preserve the chronological prerequisites in this fixture only.
            keys = ['VAR_UNUSED_0x40FA', 'VAR_UNUSED_0x40FB', 'VAR_UNUSED_0x40FC']
            for variable in keys[:keys.index(contract['requires_checkpoint']) + 1]:
                init.append('    setvar ' + variable + ', 1')
    if scenario == 'completed':
        init.append('    setflag ' + contract['completion_flag'])
        if contract['kind'] == 'gym':
            init.append(f'    setflag FLAG_BADGE{contract["grants_badge"]:02d}_GET')
        elif contract.get('grants_checkpoint'):
            init.append('    setvar ' + contract['grants_checkpoint'] + ', 1')
        for trainer in contract['trainer_slots']:
            init.append('    settrainerflag ' + trainer)
    init += ['SFModuleQA_Ready::']
    path = directory / target['script']
    source = path.read_text()
    anchor = '    setvar VAR_REPEL_STEP_COUNT, 250\n'
    if source.count(anchor) != 1:
        raise ValueError('Native test-bench initialization anchor changed')
    path.write_text(source.replace(anchor, anchor + '\n'.join(init) + '\n', 1))
    # Returning to Dogpatch must retain the QA identity, not grant a second loan.
    path = directory / 'dogpatch.inc'
    source = re.sub(r'(VAR_UNUSED_0x40F8, )\d+',
                    lambda m: m[1] + str(MAGIC), path.read_text())
    path.write_text(source)
    (directory / 'content.json').write_text(json.dumps(content, indent=2) + '\n')
    return {'kind': 'module-playtest', 'module': identifier, 'scenario': scenario,
            'campaign_evidence': False, 'save_magic': MAGIC,
            'note': 'Fresh-game QA prerequisites are injected; use separate saves.'}
