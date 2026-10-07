# Comparison evidence

Reference ROMs, states, raw frames, audio and recordings stay under ignored
`.tools/benchmarks`. Never add them to Git or the public website. Preparation
verifies the specific user-supplied Emerald SHA-256 from the game specification.

`prepare_capture.py` prepares native GUI Lua controller routes. Scroll-register
reads use the emulator's memory-domain view because these GBA registers are
write-only through the ordinary bus. Frame-only encodes remain diagnostics.

`capture_core.py` provides a second native mGBA 0.10.5 capture path that avoids
GUI codec/resolution presets. It builds the pinned official core with the same
SDK container as the foundation and emits 240x160 raw frames, synchronized PCM,
controller traces, final stills, metadata and a continuation state. It never
writes game memory. State continuation checks the original cartridge hash.

Example: `python3 scripts/quality/capture_core.py --setup --rom
engine/sf-foundation.gba --input .tools/benchmarks/route.csv --name walking-001`.
Input CSV contains `controller_bit_mask,frames` per line with no header. Add
`--telemetry HEX_ADDRESS` from the foundation ELF symbol table to count actual
game updates. `--trace-only` avoids writing large video files for long traces.
Every benchmark name is unique; existing evidence is never overwritten.

This Linux ARM64 core provides emulated behavior and CPU-budget evidence.
Normal-speed encoded playback can support presentation comparisons. It does
not prove interactive Mac GUI behavior, browser latency, or physical-phone
performance. Those checks remain separate release gates. Unreviewed clips and
generated assets never acquire an automatic parity score.

`encode_core_capture.py DIRECTORY` checks native frame/audio byte counts and
clock agreement before encoding at the cartridge's native frame rate. It marks
clips outside 30–60 seconds as diagnostics and reports whether the signal is
audible. Capture initializes mixer volume explicitly; earlier silent captures
are invalid for soundtrack comparison. A clip still needs scenario matching,
equal listening levels and user approval before it contributes to parity.
