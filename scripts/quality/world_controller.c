/* Finite controller-only world probe. Observations never write guest memory. */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void quiet(struct mLogger* logger, int category, enum mLogLevel level,
                  const char* format, va_list args)
{
    (void) logger; (void) category;
    if(level & (mLOG_FATAL | mLOG_ERROR)) vfprintf(stderr, format, args);
}

int main(int argc, char** argv)
{
    if(argc < 2 || argc > 4) return 2;
    setvbuf(stdout, NULL, _IOLBF, 0);
    struct mLogger logger = {.log = quiet};
    mLogSetDefaultLogger(&logger);
    struct mCore* core = mCoreFind(argv[1]);
    if(! core || ! core->init(core)) return 2;
    mCoreConfigInit(&core->config, NULL);
    mCoreConfigSetDefaultIntValue(&core->config, "logLevel", 0);
    mCoreConfigSetDefaultIntValue(&core->config, "skipBios", 1);
    mCoreLoadConfig(core);
    color_t pixels[240 * 160];
    core->setVideoBuffer(core, pixels, 240);
    if(! mCoreLoadFile(core, argv[1])) return 2;
    if(argc > 2 && strcmp(argv[2], "-"))
    {
        FILE* file = fopen(argv[2], "rb");
        unsigned char battery[131072];
        if(! file || fread(battery, sizeof(battery), 1, file) != 1 ||
           ! core->savedataRestore(core, battery, sizeof(battery), false)) return 2;
        fclose(file);
    }
    core->reset(core); core->runFrame(core);
    if(argc > 3 && strcmp(argv[3], "-"))
    {
        FILE* file = fopen(argv[3], "rb");
        void* state = malloc(core->stateSize(core));
        if(! file || ! state || fread(state, core->stateSize(core), 1, file) != 1 ||
           ! core->loadState(core, state)) return 2;
        fclose(file); free(state);
    }
    char line[8192], command[32], path[4096];
    unsigned keys, frames, address, length, total = 0;
    for(unsigned requests = 0; requests < 50000 && fgets(line, sizeof(line), stdin); ++requests)
    {
        if(sscanf(line, "%31s", command) != 1) return 2;
        if(! strcmp(command, "step"))
        {
            if(sscanf(line, "%*s %u %u", &keys, &frames) != 2 || keys > 1023 ||
               ! frames || frames > 36000 || total + frames > 200000) return 2;
            core->setKeys(core, keys);
            for(unsigned i = 0; i < frames; ++i) core->runFrame(core);
            total += frames; printf("ok %u\n", total);
        }
        else if(! strcmp(command, "read"))
        {
            if(sscanf(line, "%*s %x %u", &address, &length) != 2 || length > 1024) return 2;
            for(unsigned i = 0; i < length; ++i) printf("%02x", core->busRead8(core, address + i));
            puts("");
        }
        else if(! strcmp(command, "frame"))
        {
            if(sscanf(line, "%*s %4095s", path) != 1) return 2;
            FILE* file = fopen(path, "wbx");
            if(! file || fwrite(pixels, sizeof(pixels), 1, file) != 1) return 2;
            fclose(file); puts("ok");
        }
        else if(! strcmp(command, "state") || ! strcmp(command, "battery"))
        {
            if(sscanf(line, "%*s %4095s", path) != 1) return 2;
            void* bytes = NULL;
            size_t size;
            if(! strcmp(command, "state"))
            {
                size = core->stateSize(core); bytes = malloc(size);
                if(! bytes || ! core->saveState(core, bytes)) return 2;
            }
            else size = core->savedataClone(core, &bytes);
            FILE* file = fopen(path, "wbx");
            if(! file || ! bytes || ! size || fwrite(bytes, size, 1, file) != 1) return 2;
            fclose(file); free(bytes); puts("ok");
        }
        else return 2;
    }
    core->deinit(core);
    return 0;
}
