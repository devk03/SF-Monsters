"""Small native safety hooks, applied to the pinned engine without ROM edits."""
import shutil


def apply_engine_guards(root, engine, original):
    path = 'src/main_menu.c'
    source = original(path)
    anchor = '        switch (gSaveFileStatus)\n'
    if source.count(anchor) != 1:
        raise ValueError('Pinned main-menu save hook changed; review before applying.')
    source = source.replace('#include "event_data.h"',
                            '#include "event_data.h"\n#include "constants/vars.h"')
    source = source.replace('/*\n * Main menu state machine',
                            '#include "sf_save_guard.h"\n\n/*\n * Main menu state machine', 1)
    source = source.replace(anchor, '''        if ((gSaveFileStatus == SAVE_STATUS_OK || gSaveFileStatus == SAVE_STATUS_ERROR)
            && !SFSaveIsSupported())
        {
            CreateMainMenuErrorWindow(sSFUnsupportedSave);
            tMenuType = HAS_NO_SAVED_GAME;
            gTasks[taskId].func = Task_WaitForSaveFileErrorWindow;
        }
        else switch (gSaveFileStatus)
''', 1)
    (engine / path).write_text(source)
    shutil.copy2(root / 'romhack/engine/save_guard.h', engine / 'src/sf_save_guard.h')
    # The added header is inert after the tracked caller is restored to base.
    return [path]
