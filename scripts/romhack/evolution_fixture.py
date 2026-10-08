"""Private native-script fixtures; never evidence of earned campaign levels."""
import re

FIXTURES = {'cinder-15': ('SPECIES_TORCHIC', 15),
            'ashrunner-35': ('SPECIES_COMBUSKEN', 35),
            'reference-15': ('SPECIES_TORCHIC', 15),
            'reference-35': ('SPECIES_COMBUSKEN', 35)}


def apply_evolution_fixture(engine, name, original):
    species, level = FIXTURES[name]
    path = 'data/maps/LittlerootTown/scripts.inc'
    text = (engine / path).read_text()
    pattern = r'(SF_Starter_Ember::\n.*?)(?=SF_Starter_Tide::)'
    match = re.search(pattern, text, re.S)
    if not match: raise ValueError('Native fixture starter anchor was not found.')
    block = match.group(1)
    block, count = re.subn(r'\tgivemon SPECIES_TORCHIC, 5\n',
                          f'\tgivemon {species}, {level}\n', block)
    if count != 1: raise ValueError('Native fixture gift must have one declaration.')
    text = text[:match.start()] + block + text[match.end():]
    text, count = re.subn(r'\tgiveitem ITEM_POTION, 3\n',
                          '\tgiveitem ITEM_POTION, 3\n\tgiveitem ITEM_RARE_CANDY, 1\n', text)
    if count != 1: raise ValueError('Native fixture supply anchor was not found.')
    if name.startswith('reference-'):
        # Prepare compatible battery data for the actual fixed reference ROM.
        # The subsequent reference capture uses a9dec84d…85af, not this fixture.
        text, count = re.subn(r'\tmsgbox SF_Text_Ready, MSGBOX_DEFAULT\n',
            '\tmsgbox SF_Text_Ready, MSGBOX_DEFAULT\n\twarp MAP_LITTLEROOT_TOWN, 10, 18\n\twaitstate\n', text)
        if count != 1: raise ValueError('Reference battery fixture warp anchor was not found.')
        for native in ['src/data/text/species_names.h', 'src/data/pokemon/species_info.h',
                       'src/data/pokemon/level_up_learnsets.h']:
            (engine / native).write_text(original(native))
    (engine / path).write_text(text)
    return path
