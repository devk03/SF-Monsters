"""Original trainer teams and encounters compiled into the pinned native engine."""
import json
import re


def constant(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(prefix + r'[A-Z0-9_]+', value):
        raise ValueError(f'Expected a native {prefix} identifier.')
    return value


def trainer_record(team):
    identifier = constant(team['id'], 'TRAINER_')
    name = team['name']
    if not re.fullmatch(r'[A-Z0-9 ]{1,12}', name):
        raise ValueError('Trainer names must fit twelve native characters.')
    if not 1 <= len(team['party']) <= 6:
        raise ValueError('Trainer parties must contain one to six members.')
    members = []
    for mon in team['party']:
        if not 1 <= mon['level'] <= 100 or not 0 <= mon.get('iv', 80) <= 255:
            raise ValueError('Trainer level/IV value is outside the native range.')
        moves = mon['moves']
        if not 1 <= len(moves) <= 4:
            raise ValueError('Each trainer member needs one to four moves.')
        moves = [constant(move, 'MOVE_') for move in moves] + ['MOVE_NONE'] * (4 - len(moves))
        species = constant(mon['species'], 'SPECIES_')
        held = constant(mon.get('item', 'ITEM_NONE'), 'ITEM_')
        members.append('    {.iv = %d, .lvl = %d, .species = %s, .heldItem = %s, .moves = {%s}}'
                       % (mon.get('iv', 80), mon['level'], species, held, ', '.join(moves)))
    party = 'sParty_SF_' + identifier
    declaration = ('static const struct TrainerMonItemCustomMoves ' + party + '[] = {\n'
                   + ',\n'.join(members) + '\n};\n')
    items = [constant(item, 'ITEM_') for item in team.get('items', [])]
    if len(items) > 4:
        raise ValueError('A trainer can carry at most four battle items.')
    items += ['ITEM_NONE'] * (4 - len(items))
    record = ('    [%s] =\n    {\n' % identifier
              + '        .trainerClass = %s,\n' % constant(team['class'], 'TRAINER_CLASS_')
              + '        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_MALE,\n'
              + '        .trainerPic = %s,\n' % constant(team['portrait'], 'TRAINER_PIC_')
              + '        .trainerName = _("%s"),\n' % name
              + '        .items = {%s},\n' % ', '.join(items)
              + '        .doubleBattle = FALSE,\n'
              + '        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,\n'
              + '        .party = ITEM_CUSTOM_MOVES(%s),\n    },' % party)
    return identifier, declaration, record


def apply_battles(content, root, engine, original):
    if 'battle_content' not in content:
        return []
    path = (root / 'romhack/content' / content['battle_content']).resolve()
    path.relative_to((root / 'romhack/content').resolve())
    data = json.loads(path.read_text())
    trainers_path, parties_path = 'src/data/trainers.h', 'src/data/trainer_parties.h'
    trainers, parties = original(trainers_path), original(parties_path)
    identifiers = set()
    for team in data.get('trainers', []):
        identifier, declaration, record = trainer_record(team)
        if identifier in identifiers:
            raise ValueError('Trainer IDs must be unique.')
        identifiers.add(identifier)
        pattern = rf'(?m)^    \[{re.escape(identifier)}\] =\n    \{{.*?^    \}},'
        trainers, count = re.subn(pattern, lambda match: record, trainers, flags=re.S)
        if count != 1:
            raise ValueError(f'Expected one pinned trainer slot: {identifier}')
        parties += '\n' + declaration
    (engine / trainers_path).write_text(trainers)
    (engine / parties_path).write_text(parties)
    encounters_path = 'src/data/wild_encounters.json'
    wild = json.loads(original(encounters_path))
    group = next(group for group in wild['wild_encounter_groups'] if group['for_maps'])
    identifiers = set()
    for encounter in data.get('encounters', []):
        map_id = constant(encounter['map'], 'MAP_')
        if map_id in identifiers:
            raise ValueError('Encounter map IDs must be unique.')
        identifiers.add(map_id)
        mons = encounter['land_mons']['mons']
        if len(mons) != 12 or not 1 <= encounter['land_mons']['encounter_rate'] <= 100:
            raise ValueError('Land encounters need twelve native probability slots and a valid rate.')
        for mon in mons:
            constant(mon['species'], 'SPECIES_')
            if not 1 <= mon['min_level'] <= mon['max_level'] <= 100:
                raise ValueError('Encounter levels are invalid.')
        group['encounters'] = [entry for entry in group['encounters'] if entry['map'] != map_id]
        group['encounters'].append(encounter)
    (engine / encounters_path).write_text(json.dumps(wild, indent=2) + '\n')
    return [trainers_path, parties_path, encounters_path]
