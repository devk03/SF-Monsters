"""Compile two SF display aliases without changing native classes or shared text."""
from pathlib import Path

GETTER = '''const u8 *GetTrainerClassNameFromId(u16 trainerId)
{
    if (trainerId >= TRAINERS_COUNT)
        trainerId = TRAINER_NONE;
    return gTrainerClassNames[gTrainers[trainerId].trainerClass];
}'''
ALIASED_GETTER = '''const u8 gSFBuilderClassName[] = _("BUILDER");

const u8 *GetTrainerClassNameFromId(u16 trainerId)
{
    if (trainerId >= TRAINERS_COUNT)
        trainerId = TRAINER_NONE;
    if ((trainerId == TRAINER_JOSH || trainerId == TRAINER_TOMMY)
        && gTrainers[trainerId].trainerClass == TRAINER_CLASS_POKEMANIAC)
        return gSFBuilderClassName;
    return gTrainerClassNames[gTrainers[trainerId].trainerClass];
}'''


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('Pinned trainer-class display anchor changed or was already applied.')
    return source.replace(old, new, 1)


def transform(pokemon, battle_message):
    """Preserve every byte outside one getter, two lookups and explicit includes."""
    pokemon = replace_once(pokemon, '#include "constants/trainers.h"\n',
        '#include "constants/trainers.h"\n#include "constants/opponents.h"\n')
    pokemon = replace_once(pokemon, GETTER, ALIASED_GETTER)
    if '#include "pokemon.h"' in battle_message:
        raise ValueError('Review the pinned battle-message include set before applying.')
    battle_message = replace_once(battle_message, '#include "palette.h"\n',
        '#include "palette.h"\n#include "pokemon.h"\n')
    for side in ('A', 'B'):
        battle_message = replace_once(battle_message,
            f'toCpy = gTrainerClassNames[gTrainers[gTrainerBattleOpponent_{side}].trainerClass];',
            f'toCpy = GetTrainerClassNameFromId(gTrainerBattleOpponent_{side});')
    return pokemon, battle_message


def apply_alias(root, engine):
    # Compose after earlier species hooks. Never restore/overwrite their edits.
    paths = ['src/pokemon.c', 'src/battle_message.c']
    sources = [(engine / path).read_text() for path in paths]
    changed = transform(*sources)  # Validate both complete sources before writing either.
    for path, source in zip(paths, changed):
        (engine / path).write_text(source)
    return paths
