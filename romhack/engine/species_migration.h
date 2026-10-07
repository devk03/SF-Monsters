#include "data.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "string_util.h"
#include "constants/vars.h"
#include "constants/moves.h"

struct SFSpeciesUpgrade
{
    u16 species;
    u8 oldName[POKEMON_NAME_LENGTH + 1];
    u8 moveLevel;
    u16 earlyMove;
};
static const struct SFSpeciesUpgrade sSFSpeciesUpgrades[] = {
    // SF_SPECIES_RECORDS
};

static bool8 SFUpgradeBoxMon(struct BoxPokemon *mon)
{
    u16 species = GetBoxMonData(mon, MON_DATA_SPECIES, NULL);
    u8 nickname[POKEMON_NAME_LENGTH + 1];
    u8 entry, slot, empty = MAX_MON_MOVES;
    for (entry = 0; entry < ARRAY_COUNT(sSFSpeciesUpgrades); entry++)
    {
        const struct SFSpeciesUpgrade *upgrade = &sSFSpeciesUpgrades[entry];
        if (species != upgrade->species || GetBoxMonData(mon, MON_DATA_IS_EGG, NULL))
            continue;
        GetBoxMonData(mon, MON_DATA_NICKNAME, nickname);
        if (StringCompare(nickname, upgrade->oldName) == 0)
            SetBoxMonData(mon, MON_DATA_NICKNAME, gSpeciesNames[species]);
        // Add an earned move only to an empty slot. Preserve every existing move.
        for (slot = 0; slot < MAX_MON_MOVES; slot++)
        {
            u16 move = GetBoxMonData(mon, MON_DATA_MOVE1 + slot, NULL);
            if (move == upgrade->earlyMove)
                return TRUE;
            if (move == MOVE_NONE && empty == MAX_MON_MOVES)
                empty = slot;
        }
        if (empty < MAX_MON_MOVES && GetLevelFromBoxMonExp(mon) >= upgrade->moveLevel)
        {
            SetBoxMonData(mon, MON_DATA_MOVE1 + empty, &upgrade->earlyMove);
            SetBoxMonData(mon, MON_DATA_PP1 + empty, &gBattleMoves[upgrade->earlyMove].pp);
        }
        return TRUE;
    }
    return FALSE;
}

static void SFUpgradeSpeciesContent(void)
{
    u8 member, box, slot;
    if (VarGet(VAR_UNUSED_0x40FA) >= SF_SPECIES_CONTENT_REVISION)
        return;
    for (member = 0; member < gPlayerPartyCount; member++)
        if (SFUpgradeBoxMon(&gPlayerParty[member].box))
            CalculateMonStats(&gPlayerParty[member]);
    for (box = 0; box < TOTAL_BOXES_COUNT; box++)
        for (slot = 0; slot < IN_BOX_COUNT; slot++)
            SFUpgradeBoxMon(GetBoxedMonPtr(box, slot));
    VarSet(VAR_UNUSED_0x40FA, SF_SPECIES_CONTENT_REVISION);
}
