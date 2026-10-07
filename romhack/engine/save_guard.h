// Native Continue uses the same persistent identity as the browser importer.
// Refusing continuation does not erase, convert or write the loaded Flash.
static const u8 sSFUnsupportedSave[] = _(
    "This save belongs to another game\n"
    "or an unsupported SF version.\p"
    "Your save has not been changed.\n"
    "Keep a backup before starting anew.");

static bool8 SFSaveIsSupported(void)
{
    return VarGet(VAR_UNUSED_0x40F8) == 0x5346
        && VarGet(VAR_UNUSED_0x40F9) == 1;
}
