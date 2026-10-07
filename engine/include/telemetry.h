#ifndef SF_FOUNDATION_TELEMETRY_H
#define SF_FOUNDATION_TELEMETRY_H
#include <stdint.h>

struct FoundationTelemetry
{
    uint32_t magic;
    uint32_t updates;
    uint32_t missed_frames;
    uint32_t peak_cpu_q12;
    uint32_t keys;
    uint32_t step_duration;
    uint32_t step_elapsed;
    uint32_t completed_steps;
    int32_t world_x;
    int32_t world_y;
    uint32_t map;
};

extern "C" volatile FoundationTelemetry foundation_telemetry;
#endif
