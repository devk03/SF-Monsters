/* Controller-only native mGBA capture. Output stays in ignored local benchmarks. */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

struct Capture
{
    struct mAVStream stream;
    FILE* audio;
    unsigned rate;
    unsigned long samples;
};

static void audio_rate(struct mAVStream* stream, unsigned rate)
{
    ((struct Capture*) stream)->rate = rate;
}

static void audio_frame(struct mAVStream* stream, int16_t left, int16_t right)
{
    struct Capture* capture = (struct Capture*) stream;
    int16_t sample[] = {left, right};
    if(fwrite(sample, sizeof(sample), 1, capture->audio) != 1) exit(2);
    ++capture->samples;
}

static FILE* output(const char* prefix, const char* extension)
{
    char path[4096];
    if(snprintf(path, sizeof(path), "%s.%s", prefix, extension) >= (int) sizeof(path)) exit(2);
    FILE* file = fopen(path, "wbx");
    if(! file) { perror(path); exit(2); }
    return file;
}

int main(int argc, char** argv)
{
    if(argc < 4 || argc > 7)
    {
        fprintf(stderr, "Usage: core_capture ROM PREFIX INPUT_CSV [STATE|-] [TELEMETRY_HEX] [trace]\n");
        return 2;
    }
    struct mLogger logger = {.log = log_errors};
    mLogSetDefaultLogger(&logger);
    struct mCore* core = mCoreFind(argv[1]);
    if(! core || ! core->init(core)) return 2;
    mCoreConfigInit(&core->config, NULL);
    mCoreConfigSetDefaultIntValue(&core->config, "logLevel", 0);
    mCoreConfigSetDefaultIntValue(&core->config, "skipBios", 1);
    mCoreLoadConfig(core);
    color_t pixels[240 * 160];
    unsigned width, height;
    core->desiredVideoDimensions(core, &width, &height);
    if(width != 240 || height != 160 || sizeof(color_t) != 4) return 2;
    core->setVideoBuffer(core, pixels, 240);
    if(! mCoreLoadFile(core, argv[1])) return 2;
    core->reset(core);
    core->runFrame(core); /* Align to a complete video frame before recording. */
    if(argc > 4 && strcmp(argv[4], "-"))
    {
        FILE* state_file = fopen(argv[4], "rb");
        void* state = malloc(core->stateSize(core));
        if(! state_file || ! state ||
           fread(state, core->stateSize(core), 1, state_file) != 1 ||
           ! core->loadState(core, state)) return 2;
        fclose(state_file);
        free(state);
    }
    FILE* sequence = fopen(argv[3], "r");
    if(! sequence) return 2;
    FILE* video = argc > 6 && ! strcmp(argv[6], "trace") ? NULL : output(argv[2], "rgba");
    FILE* trace = output(argv[2], "csv");
    struct Capture capture = {.audio = output(argv[2], "pcm")};
    capture.stream.audioRateChanged = audio_rate;
    capture.stream.postAudioFrame = audio_frame;
    core->setAVStream(core, &capture.stream);
    uint32_t telemetry = argc > 5 ? strtoul(argv[5], NULL, 16) : 0;
    fprintf(trace, "frame,keys,bg0_x,bg0_y,bg1_x,bg1_y,updates,missed,cpu_q12,x,y,steps,map\n");
    unsigned mask, frames;
    unsigned long total = 0;
    while(fscanf(sequence, "%u,%u", &mask, &frames) == 2)
    {
        if(mask >= 1024 || ! frames || frames > 36000 || total + frames > 600000) return 2;
        core->setKeys(core, mask);
        for(unsigned frame = 0; frame < frames; ++frame)
        {
            core->runFrame(core);
            if(video && fwrite(pixels, sizeof(pixels), 1, video) != 1) return 2;
            fprintf(trace, "%u,%u,%u,%u,%u,%u,%u,%u,%u,%d,%d,%u,%u\n",
                core->frameCounter(core), mask,
                core->rawRead16(core, 0x04000010, -1), core->rawRead16(core, 0x04000012, -1),
                core->rawRead16(core, 0x04000014, -1), core->rawRead16(core, 0x04000016, -1),
                telemetry ? core->busRead32(core, telemetry + 4) : 0,
                telemetry ? core->busRead32(core, telemetry + 8) : 0,
                telemetry ? core->busRead32(core, telemetry + 12) : 0,
                telemetry ? core->busRead32(core, telemetry + 32) : 0,
                telemetry ? core->busRead32(core, telemetry + 36) : 0,
                telemetry ? core->busRead32(core, telemetry + 28) : 0,
                telemetry ? core->busRead32(core, telemetry + 40) : 0);
        }
        total += frames;
    }
    if(! feof(sequence) || ! total || ! capture.rate) return 2;
    if(telemetry && core->busRead32(core, telemetry) != 0x53464654)
    {
        fprintf(stderr, "Foundation telemetry signature mismatch\n");
        return 2;
    }
    FILE* metadata = output(argv[2], "json");
    fprintf(metadata, "{\"frames\":%lu,\"frequency\":%d,\"frame_cycles\":%d,"
        "\"sample_rate\":%u,\"audio_samples\":%lu,\"width\":240,\"height\":160}\n",
        total, core->frequency(core), core->frameCycles(core), capture.rate, capture.samples);
    FILE* state_file = output(argv[2], "state");
    void* state = malloc(core->stateSize(core));
    if(! state || ! core->saveState(core, state) ||
       fwrite(state, core->stateSize(core), 1, state_file) != 1) return 2;
    free(state);
    fclose(state_file);
    fclose(metadata);
    if(video) fclose(video);
    FILE* still = output(argv[2], "final.rgba");
    if(fwrite(pixels, sizeof(pixels), 1, still) != 1) return 2;
    fclose(still);
    fclose(trace);
    fclose(sequence);
    fclose(capture.audio);
    core->deinit(core);
    return 0;
}
