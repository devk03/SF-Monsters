"""Explicit isolated native service bench; no campaign or balance evidence."""
import json
import re

MAGIC = 0x5751
FILL_ITEMS = ['POTION','ANTIDOTE','BURN_HEAL','ICE_HEAL','AWAKENING','PARALYZE_HEAL',
              'FULL_RESTORE','MAX_POTION','HYPER_POTION','SUPER_POTION','FULL_HEAL',
              'REVIVE','MAX_REVIVE','FRESH_WATER','SODA_POP','LEMONADE','MOOMOO_MILK',
              'ENERGY_POWDER','ENERGY_ROOT','HEAL_POWDER','REVIVAL_HERB','ETHER',
              'MAX_ETHER','ELIXIR','MAX_ELIXIR','LAVA_COOKIE','BLUE_FLUTE',
              'YELLOW_FLUTE','RED_FLUTE','BLACK_FLUTE']


def apply_fixture(directory, content):
    path = directory / 'dogpatch.inc'
    source = path.read_text()
    source = re.sub(r'(VAR_UNUSED_0x40F8, )\d+', lambda m:m[1]+str(MAGIC), source)
    source = source.replace('    givemon SPECIES_MARILL, 100\n',
                            '    givemon SPECIES_MARILL, 5\n'
                            '    setmonmove 0, 2, MOVE_TAIL_WHIP\n'
                            '    addmoney 10000\n')
    # The ordinary new-game identity branch runs this injected setup once only.
    anchor = '    setmonmove 0, 1, MOVE_WATERFALL\n'
    init = ''.join(f'    setflag FLAG_BADGE{n:02d}_GET\n' for n in range(1,9))
    init += ''.join(f'    setvar VAR_UNUSED_0x40F{n}, 1\n' for n in 'ABC')
    if source.count(anchor) != 1 or source.count('WB_dogpatch_Info::') != 1:
        raise ValueError('Town service bench initialization anchor changed')
    source = source.replace(anchor, anchor+init, 1)
    source = source.replace('WB_dogpatch_Info::','SFTownQA_OriginalInfo::',1)
    source += '''
WB_dogpatch_Info::
    lock
    faceplayer
    compare VAR_UNUSED_0x40FD, 0
    goto_if_eq SFTownQA_Battle
    compare VAR_UNUSED_0x40FD, 1
    goto_if_eq SFTownQA_Fill
    goto SFTownQA_OriginalInfo
SFTownQA_Battle::
    setwildbattle SPECIES_POOCHYENA, 3, ITEM_NONE
    dowildbattle
    setvar VAR_UNUSED_0x40FD, 1
    release
    end
SFTownQA_Fill::
'''
    source += ''.join(f'    additem ITEM_{item}, {99 if item=="POTION" else 1}\n' for item in FILL_ITEMS)
    source += '''    setvar VAR_UNUSED_0x40FD, 2
    msgbox SFTownQA_FullText, MSGBOX_DEFAULT
    release
    end
SFTownQA_FullText::
    .string "QA setup: item pocket filled.\\nUse Toss to free reward space.$"
'''
    path.write_text(source)
    (directory/'content.json').write_text(json.dumps(content,indent=2)+'\n')
    return dict(kind='town-services',save_magic=MAGIC,campaign_evidence=False,
                note='Injected loan level, access flags, money and bag contents; controller-only healing/economy/reward QA')
