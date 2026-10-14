/* Controlled native function fixtures: this intentionally writes test RAM and CPU
 * registers. It never produces campaign/progression or controller-only evidence.
 * The Python owner verifies ROM/state/ELF identity before invoking this helper.
 * Inputs can write only GBA RAM; ROM files and battery saves are never exported.
 */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/internal/arm/arm.h>
#include <mgba/internal/arm/isa-inlines.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int ram(unsigned address, unsigned length)
{
    return length && ((address >= 0x02000000 && address < 0x02040000
                       && length <= 0x02040000 - address)
        || (address >= 0x03000000 && address < 0x03008000
                       && length <= 0x03008000 - address));
}

static void fixture_log(struct mLogger *logger, int category, enum mLogLevel level,
                        const char *format, va_list args)
{
    (void)logger; (void)category;
    if (level & (mLOG_FATAL | mLOG_ERROR))
    {
        vfprintf(stderr, format, args);
        fputc('\n', stderr);
        if (level & mLOG_FATAL) exit(4);
    }
}

int main(int argc, char **argv)
{
    if (argc != 3) return 2;
    struct mLogger logger = {.log = fixture_log};
    mLogSetDefaultLogger(&logger);
    struct mCore *core = mCoreFind(argv[1]);
    if (!core || core->platform(core) != mPLATFORM_GBA || !core->init(core)) return 2;
    mCoreConfigInit(&core->config, NULL);
    mCoreConfigSetDefaultIntValue(&core->config, "skipBios", 1);
    mCoreConfigSetDefaultIntValue(&core->config, "logLevel", 0);
    mCoreLoadConfig(core);
    color_t pixels[240 * 160];
    core->setVideoBuffer(core, pixels, 240);
    if (!mCoreLoadFile(core, argv[1])) return 2;
    core->reset(core);
    core->runFrame(core);
    FILE *f = fopen(argv[2], "rb");
    void *state = malloc(core->stateSize(core));
    if (!f || !state || fseek(f, 0, SEEK_END) || ftell(f) != (long)core->stateSize(core)) return 2;
    rewind(f);
    if (fread(state, core->stateSize(core), 1, f) != 1) return 2;
    fclose(f);
    if (!core->loadState(core, state)) return 2;
    char line[8192], command[16], bytes[4096];
    unsigned address, count;
    while (fgets(line, sizeof(line), stdin))
    {
        if (sscanf(line, "%15s", command) != 1) continue;
        if (!strcmp(command, "reset"))
        {
            if (!core->loadState(core, state)) return 2;
        }
        else if (!strcmp(command, "write"))
        {
            if (sscanf(line, "%15s %x %4095s", command, &address, bytes) != 3) return 2;
            count = (unsigned)strlen(bytes) / 2;
            if (strlen(bytes) % 2 || !ram(address, count)) return 2;
            for (unsigned i = 0; i < count; ++i)
            {
                unsigned byte;
                if (sscanf(bytes + i * 2, "%2x", &byte) != 1) return 2;
                core->busWrite8(core, address + i, byte);
            }
        }
        else if (!strcmp(command, "call"))
        {
            unsigned args[8];
            if (sscanf(line, "%15s %x %x %x %x %x %x %x %x %x", command,
                &address, args, args+1, args+2, args+3, args+4, args+5, args+6, args+7) != 10) return 2;
            if (address < 0x08000000 || address >= 0x0a000000) return 2;
            struct ARMCore *cpu = core->cpu;
            _ARMSetMode(cpu, MODE_THUMB);
            cpu->halted = 0;
            cpu->cpsr.i = 1;
            cpu->cpsr.f = 1;
            cpu->gprs[ARM_SP] = 0x03007e00;
            cpu->gprs[ARM_LR] = 0x03007f01;
            core->busWrite16(core, 0x03007f00, 0xe7fe);
            for (unsigned i = 0; i < 4; ++i)
            {
                cpu->gprs[i] = args[i];
                core->busWrite32(core, 0x03007e00 + i * 4, args[i+4]);
            }
            cpu->gprs[ARM_PC] = address & ~1u;
            cpu->cycles += ThumbWritePC(cpu);
            unsigned steps;
            for (steps = 0; steps < 2000000 && (unsigned)cpu->gprs[ARM_PC] != 0x03007f02; ++steps)
                core->step(core);
            if (steps == 2000000) {fprintf(stderr, "Function return timeout at %08x\n", (unsigned)cpu->gprs[ARM_PC]); return 3;}
            printf("return %08x steps %u\n", (unsigned)cpu->gprs[0], steps);
        }
        else if (!strcmp(command, "read"))
        {
            if (sscanf(line, "%15s %x %x", command, &address, &count) != 3 || !ram(address, count)) return 2;
            for (unsigned i = 0; i < count; ++i) printf("%02x", core->busRead8(core, address + i));
            putchar('\n');
        }
        else return 2;
    }
    free(state);
    mCoreConfigDeinit(&core->config);
    core->deinit(core);
    return 0;
}
