/* Bounded stock-core KEYINPUT observer. Never writes guest RAM/registers. */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/core/timing.h>
#include <mgba/internal/arm/arm.h>
#include <mgba/internal/gba/gba.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_FRAMES 120
#define MAX_HOOKS 4096
#define FRAME_CYCLES 280896u
#define MAIN_HELD_RAW 0x030022e8u
#define READ_KEYS_PC 0x080005ecu /* Raw PC inside Thumb LDRH at 080005e8. */

struct Clock { uint32_t previous; uint64_t elapsed; };
struct Hook { uint64_t cycle; unsigned frame, sequence, keys; };
struct Frame {
    uint64_t cycle, set_cycle;
    unsigned sequence, keys, held_raw, hooks;
};
enum EventKind {
    LOOP_START = 1, KEYS_LOADED, KEYS_RETURNED, WRAPPER_ENTRY,
    CALLBACKS_ENTRY, CALLBACK1_ENTER, CALLBACK2_ENTER,
    CALLBACK1_RETURN, CALLBACK2_RETURN, WAIT_ENTER, WAIT_CLEAR, WAIT_RETURN,
    VBLANK_DELIVERED
};
struct Event { uint64_t cycle; unsigned frame, kind, from, to, value; };
struct Profile {
    struct mAVStream stream;
    struct mCore* core;
    struct Clock clock;
    struct Hook hooks[MAX_HOOKS];
    struct Frame frames[MAX_FRAMES];
    unsigned count, frame, sequence, keys, sample_rate;
    uint64_t samples;
    uint64_t instructions, event_drains;
    struct Event events[8192];
    unsigned event_count;
    int step_observe;
    int callback_pending[2];
    FILE* audio;
};

static void log_errors(struct mLogger* logger, int category, enum mLogLevel level,
                       const char* format, va_list args)
{
    (void) logger;
    (void) category;
    if(level & (mLOG_FATAL | mLOG_ERROR))
    {
        vfprintf(stderr, format, args);
        fputc('\n', stderr);
    }
}

static void fail(const char* message)
{
    fprintf(stderr, "%s\n", message);
    exit(2);
}

/* Unsigned subtraction handles signed-boundary and full 32-bit wraps alike.
 * Each sample must be within two guest frames; reset/load starts a new epoch. */
static int advance(struct Clock* clock, uint32_t now)
{
    uint32_t delta = now - clock->previous;
    if(delta > 2 * FRAME_CYCLES) return 0;
    clock->elapsed += delta;
    clock->previous = now;
    return 1;
}

static uint64_t guest_now(struct Profile* profile)
{
    uint32_t now = (uint32_t) mTimingCurrentTime(profile->core->timing);
    if(! advance(&profile->clock, now)) fail("Guest clock discontinuity");
    return profile->clock.elapsed;
}

static int clock_test(void)
{
    const uint32_t vectors[][3] = {
        {0xfffffff0u, 0x10u, 32}, {100, 101, 1}, {42, 42, 0},
        {0x7ffffff0u, 0x80000010u, 32}, {100, 50, UINT32_MAX}
    };
    for(unsigned i = 0; i < sizeof(vectors) / sizeof(*vectors); ++i)
    {
        struct Clock clock = {.previous = vectors[i][0]};
        int valid = advance(&clock, vectors[i][1]);
        if(vectors[i][2] == UINT32_MAX ? valid :
            (! valid || clock.elapsed != vectors[i][2])) return 2;
    }
    puts("Unsigned clock wrap/boundary/discontinuity checks passed");
    return 0;
}

static double wall_now(void)
{
    struct timespec value;
    if(clock_gettime(CLOCK_MONOTONIC, &value)) fail("Monotonic clock unavailable");
    return value.tv_sec + value.tv_nsec / 1e9;
}

static uint32_t next_pc(const struct ARMCore* cpu)
{
    return (uint32_t) cpu->gprs[ARM_PC] - (cpu->executionMode == MODE_THUMB ? 2 : 4);
}

static void event(struct Profile* profile, unsigned kind, unsigned from,
                  unsigned to, unsigned value)
{
    if(profile->event_count == 8192) fail("Instruction event buffer full");
    profile->events[profile->event_count++] = (struct Event) {
        .cycle = guest_now(profile), .frame = profile->frame,
        .kind = kind, .from = from, .to = to, .value = value
    };
}

/* Called only after an actually executed instruction, after pending events were
 * drained before pre-PC sampling. Never infer execution from a pre-IRQ PC. */
static void transition(struct Profile* profile, unsigned from, unsigned mode,
                       unsigned opcode, unsigned r0, unsigned lr)
{
    const struct ARMCore* cpu = profile->core->cpu;
    unsigned to = next_pc(cpu);
    if(cpu->executionMode == MODE_THUMB)
    {
        for(unsigned slot = 0; slot < 2; ++slot)
            if(profile->callback_pending[slot] && to == 0x0800052a + 10 * slot)
            {
                event(profile, CALLBACK1_RETURN + slot, from, to, 0);
                profile->callback_pending[slot] = 0;
            }
    }
    if(mode != MODE_THUMB) return;
    unsigned kind = 0, expected = 0, destination = 0, value = 0;
    switch(from)
    {
    case 0x0800042c: kind = LOOP_START; expected = 0xf8db; destination = 0x080005e4; break;
    case 0x080005e8:
        kind = KEYS_LOADED; expected = 0x8801; destination = 0x080005ea;
        value = ((unsigned) cpu->gprs[1] ^ 0x3ff) & 0x3ff; break;
    case 0x08000678:
        if(r0 != 0x0800042f) return;
        kind = KEYS_RETURNED; expected = 0x4700; destination = 0x0800042e;
        value = profile->core->rawRead16(profile->core, MAIN_HELD_RAW, -1); break;
    case 0x08000460: kind = WRAPPER_ENTRY; expected = 0xf831; destination = 0x080004c4; break;
    case 0x08000494: kind = WRAPPER_ENTRY; expected = 0xf817; destination = 0x080004c4; break;
    case 0x080004ac: kind = WRAPPER_ENTRY; expected = 0xf80b; destination = 0x080004c4; break;
    case 0x080004d2: kind = CALLBACKS_ENTRY; expected = 0xf824; destination = 0x0800051c; break;
    case 0x082ea358:
        if(lr != 0x0800052b && lr != 0x08000535) return;
        {
            unsigned slot = lr == 0x08000535;
            if(profile->callback_pending[slot]) fail("Overlapping callback span");
            profile->callback_pending[slot] = 1;
            kind = CALLBACK1_ENTER + slot; expected = 0x4700;
            destination = r0 & ~1u; value = r0;
        }
        break;
    case 0x080004bc: kind = WAIT_ENTER; expected = 0xf9f7; destination = 0x080008ac; break;
    case 0x080008b8: kind = WAIT_CLEAR; expected = 0x8390; destination = 0x080008ba; break;
    case 0x080008d2:
        if(r0 != 0x080004bf) return;
        kind = WAIT_RETURN; expected = 0x4700; destination = 0x080004be; break;
    default: return;
    }
    if(opcode != expected || to != destination) fail("Executed observation site changed");
    event(profile, kind, from, to, value);
}

/* Match ARMRun's existing event-drain prefix, then its existing step function.
 * Yield immediately after the event that changes frameCounter: stock runFrame
 * returns there too. Stepping once after that event would overshoot the boundary.
 * This executes the pinned core's emulation; it never substitutes IRQ/timing code. */
static void step_frame(struct Profile* profile)
{
    struct mCore* core = profile->core;
    struct ARMCore* cpu = core->cpu;
    uint32_t frame = core->frameCounter(core);
    uint32_t start = (uint32_t) mTimingCurrentTime(core->timing);
    while(core->frameCounter(core) == frame)
    {
        if((uint32_t) ((uint32_t) mTimingCurrentTime(core->timing) - start) >
           FRAME_CYCLES + 1232) fail("Step frame exceeded stock frame guard");
        while(cpu->cycles >= cpu->nextEvent)
        {
            if(++profile->event_drains > 10000000) fail("Event-drain limit exceeded");
            cpu->irqh.processEvents(cpu);
            if(core->frameCounter(core) != frame) return;
        }
        if(++profile->instructions > 100000000) fail("Instruction limit exceeded");
        if(profile->step_observe)
        {
            unsigned from = next_pc(cpu), mode = cpu->executionMode;
            unsigned opcode = cpu->prefetch[0], r0 = cpu->gprs[0], lr = cpu->gprs[ARM_LR];
            core->step(core);
            transition(profile, from, mode, opcode, r0, lr);
        }
        else core->step(core);
    }
}

static void keys_read(void* context)
{
    struct Profile* profile = context;
    const struct ARMCore* cpu = profile->core->cpu;
    if(cpu->executionMode != MODE_THUMB ||
       (uint32_t) cpu->gprs[ARM_PC] != READ_KEYS_PC) return;
    if(profile->count == MAX_HOOKS) fail("Input event buffer full");
    profile->hooks[profile->count++] = (struct Hook) {
        .cycle = guest_now(profile), .frame = profile->frame,
        .sequence = profile->sequence, .keys = profile->core->getKeys(profile->core)
    };
}

static void video_ended(void* context)
{
    struct Profile* profile = context;
    const struct GBA* gba = profile->core->board;
    int32_t until = mTimingUntil(profile->core->timing, &gba->video.event);
    if(gba->video.vcount != 160 || until < 0 || until > 1008)
        fail("Unexpected VBlank callback scheduling point");
    /* Existing video code schedules Hblank before this callback. Remove event
     * delivery lateness to recover nominal VBlank time; do not call it a paint. */
    event(profile, VBLANK_DELIVERED, 0, gba->video.frameCounter + 1u, 1008 - until);
}

static void audio_rate(struct mAVStream* stream, unsigned rate)
{
    ((struct Profile*) stream)->sample_rate = rate;
}

static void audio_frame(struct mAVStream* stream, int16_t left, int16_t right)
{
    struct Profile* profile = (struct Profile*) stream;
    int16_t samples[] = {left, right};
    if(fwrite(samples, sizeof(samples), 1, profile->audio) != 1) fail("Audio write failed");
    ++profile->samples;
}

static FILE* output(const char* prefix, const char* suffix)
{
    char path[4096];
    if(snprintf(path, sizeof(path), "%s.%s", prefix, suffix) >= (int) sizeof(path))
        fail("Output path too long");
    FILE* file = fopen(path, "wbx");
    if(! file) fail("Output exists or cannot be created; preserve evidence");
    return file;
}

static void* load_bytes(const char* path, size_t size)
{
    FILE* file = fopen(path, "rb");
    void* bytes = malloc(size);
    if(! file || ! bytes || fread(bytes, size, 1, file) != 1 || fgetc(file) != EOF)
        fail("Input length differs from expected native layout");
    fclose(file);
    return bytes;
}

int main(int argc, char** argv)
{
    if(argc == 2 && ! strcmp(argv[1], "--clock-test")) return clock_test();
    if(argc != 7 || (strcmp(argv[6], "control") && strcmp(argv[6], "observe") &&
        strcmp(argv[6], "step-control") && strcmp(argv[6], "step-observe")))
        fail("Usage: native_input_profile ROM STATE BATTERY INPUT_CSV PREFIX control|observe|step-control|step-observe");
    struct mLogger logger = {.log = log_errors};
    mLogSetDefaultLogger(&logger);
    struct mCore* core = mCoreFind(argv[1]);
    if(! core || ! core->init(core)) fail("Core initialization failed");
    mCoreConfigInit(&core->config, NULL);
    mCoreConfigSetDefaultIntValue(&core->config, "logLevel", 0);
    mCoreConfigSetDefaultIntValue(&core->config, "skipBios", 1);
    mCoreConfigSetDefaultIntValue(&core->config, "volume", 256);
    mCoreLoadConfig(core);
    color_t pixels[240 * 160];
    unsigned width, height;
    core->desiredVideoDimensions(core, &width, &height);
    if(width != 240 || height != 160 || sizeof(color_t) != 4 ||
       core->frameCycles(core) != FRAME_CYCLES || core->frequency(core) != 16777216)
        fail("Unexpected native video/clock configuration");
    core->setVideoBuffer(core, pixels, 240);
    if(! mCoreLoadFile(core, argv[1])) fail("ROM load failed");
    core->reset(core);
    core->runFrame(core);
    void* bytes = load_bytes(argv[3], 131072);
    if(! core->savedataRestore(core, bytes, 131072, false)) fail("Flash restore failed");
    free(bytes);
    core->reset(core);
    core->runFrame(core);
    bytes = load_bytes(argv[2], core->stateSize(core));
    if(! core->loadState(core, bytes)) fail("State load failed");
    free(bytes);
    if(core->rawRead16(core, 0x080005e8, -1) != 0x8801 ||
       core->rawRead32(core, 0x08000620, -1) != 0x04000130 ||
       core->rawRead32(core, 0x08000628, -1) != 0x030022c0)
        fail("ReadKeys observation sites differ from validated immutable ROM");
    struct Profile profile = {.core = core, .audio = output(argv[5], "pcm")};
    unsigned initial_held = core->rawRead16(core, MAIN_HELD_RAW, -1);
    profile.clock.previous = (uint32_t) mTimingCurrentTime(core->timing);
    profile.stream.audioRateChanged = audio_rate;
    profile.stream.postAudioFrame = audio_frame;
    core->setAVStream(core, &profile.stream);
    struct mCoreCallbacks callbacks = {.context = &profile, .keysRead = keys_read,
                                      .videoFrameEnded = video_ended};
    int observe = ! strcmp(argv[6], "observe") || ! strcmp(argv[6], "step-observe");
    int stepping = ! strncmp(argv[6], "step-", 5);
    profile.step_observe = stepping && observe;
    if(observe) core->addCoreCallbacks(core, &callbacks);
    FILE* input = fopen(argv[4], "r");
    if(! input) fail("Input sequence unavailable");
    FILE* video = output(argv[5], "rgba");
    unsigned keys, duration;
    uint64_t set_cycle = 0;
    double start = wall_now(), emulation_seconds = 0;
    int parsed;
    while((parsed = fscanf(input, "%u,%u", &keys, &duration)) == 2)
    {
        if(keys > 1023 || (keys & 0x30) == 0x30 || (keys & 0xc0) == 0xc0 ||
           ! duration || duration > MAX_FRAMES - profile.frame)
            fail("Input exceeds bounded pilot or contains opposing directions");
        if(! profile.sequence || keys != profile.keys)
        {
            ++profile.sequence;
            profile.keys = keys;
            set_cycle = guest_now(&profile);
        }
        core->setKeys(core, keys);
        for(unsigned i = 0; i < duration; ++i)
        {
            if(wall_now() - start > 60) fail("Pilot wall-time limit exceeded");
            uint32_t before_frame = core->frameCounter(core);
            double before = wall_now();
            if(stepping) step_frame(&profile);
            else core->runFrame(core);
            emulation_seconds += wall_now() - before;
            if((uint32_t) (core->frameCounter(core) - before_frame) != 1)
                fail("Stock frame call did not advance exactly one video frame");
            profile.frames[profile.frame] = (struct Frame) {
                .cycle = guest_now(&profile), .set_cycle = set_cycle,
                .sequence = profile.sequence, .keys = keys,
                .held_raw = core->rawRead16(core, MAIN_HELD_RAW, -1),
                .hooks = profile.count
            };
            ++profile.frame;
            if(fwrite(pixels, sizeof(pixels), 1, video) != 1) fail("Video write failed");
        }
    }
    if(parsed != EOF || ! feof(input) || ! profile.frame || ! profile.sample_rate)
        fail("Incomplete pilot");
    fclose(input);
    fclose(video);
    fclose(profile.audio);
    FILE* frames = output(argv[5], "frames.csv");
    fprintf(frames, "frame,sequence,keys,set_cycle,end_cycle,held_raw,cumulative_hooks\n");
    for(unsigned i = 0; i < profile.frame; ++i)
    {
        const struct Frame* frame = &profile.frames[i];
        fprintf(frames, "%u,%u,%u,%" PRIu64 ",%" PRIu64 ",%u,%u\n", i,
            frame->sequence, frame->keys, frame->set_cycle, frame->cycle,
            frame->held_raw, frame->hooks);
    }
    fclose(frames);
    FILE* hooks = output(argv[5], "hooks.csv");
    fprintf(hooks, "frame,sequence,keys,hook_entry_cycle\n");
    for(unsigned i = 0; i < profile.count; ++i)
    {
        const struct Hook* hook = &profile.hooks[i];
        fprintf(hooks, "%u,%u,%u,%" PRIu64 "\n", hook->frame,
            hook->sequence, hook->keys, hook->cycle);
    }
    fclose(hooks);
    FILE* events = output(argv[5], "events.csv");
    fprintf(events, "frame,kind,from,to,value,completion_cycle\n");
    for(unsigned i = 0; i < profile.event_count; ++i)
    {
        const struct Event* item = &profile.events[i];
        fprintf(events, "%u,%u,%u,%u,%u,%" PRIu64 "\n", item->frame,
            item->kind, item->from, item->to, item->value, item->cycle);
    }
    fclose(events);
    bytes = malloc(core->stateSize(core));
    if(! bytes || ! core->saveState(core, bytes)) fail("Final state capture failed");
    FILE* state = output(argv[5], "state");
    if(fwrite(bytes, core->stateSize(core), 1, state) != 1) fail("State write failed");
    fclose(state);
    free(bytes);
    size_t length = core->savedataClone(core, &bytes);
    FILE* save = output(argv[5], "sav");
    if(length != 131072 || ! bytes || fwrite(bytes, length, 1, save) != 1)
        fail("Final Flash capture failed");
    fclose(save);
    free(bytes);
    FILE* result = output(argv[5], "json");
    fprintf(result, "{\"event_schema\":1,\"frames\":%u,\"hooks\":%u,\"sample_rate\":%u,"
        "\"audio_samples\":%" PRIu64 ",\"guest_cycles\":%" PRIu64 ","
        "\"emulation_wall_seconds\":%.9f,\"initial_held_raw\":%u,\"observe\":%s,"
        "\"stepping\":%s,\"instructions\":%" PRIu64 ",\"event_drains\":%" PRIu64 "}\n",
        profile.frame, profile.count, profile.sample_rate, profile.samples,
        profile.clock.elapsed, emulation_seconds, initial_held, observe ? "true" : "false",
        stepping ? "true" : "false", profile.instructions, profile.event_drains);
    fclose(result);
    core->deinit(core);
    return 0;
}
