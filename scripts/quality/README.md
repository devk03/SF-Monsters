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

The `--backend host` path uses the pinned native mGBA library on the development
Mac. Fast `runFrame` captures preserve guest behavior; they do not measure
real-time host deadlines or speaker continuity. The foundation's `SFFT`
telemetry address is not an Emerald instrumentation hook. Do not supply an
unrelated address to obtain apparent game-update counts.

`encode_core_capture.py DIRECTORY` checks native frame/audio byte counts and
clock agreement before encoding at the cartridge's native frame rate. It marks
clips outside 30–60 seconds as diagnostics and reports whether the signal is
audible. Capture initializes mixer volume explicitly; earlier silent captures
are invalid for soundtrack comparison. A clip still needs scenario matching,
equal listening levels and user approval before it contributes to parity.

## Private browser field diagnostics

`serve_web_performance.py` freezes one exact cartridge, its controller-only
native snapshot metadata and companion Flash, browser runtime, page, replay
helper and observation helper. It serves only on localhost and expires after
a specified finite lifetime of at most one hour. It does not use public saves
or accounts. Stop the emulator with **Finish local QA**, close the owned QA
tab and stop the server when the check finishes.

For the pinned v75 South Park checkpoint, `data/quality/park-active-field.csv`
defines a 598.652-second route. Its JSON descriptor pins the cartridge and input
hash, start/corridor, native expected endpoint and explicit 600-second browser
window. Another ROM or starting position requires independently checked inputs;
do not reuse the descriptor merely because the map looks similar. Start from
the original snapshot, let audio settle, then select **Measure supplied route**.
Each loaded session permits one route attempt, including an aborted attempt.
Use a fresh session for a retry. Avoid concurrent builds, captures or test suites.

The preserved browser report includes bounded mapped keyboard events, trusted
and repeat markers, window focus/blur, and long tasks when the browser supports
them. Overflow is explicit. These observations help investigate extra inputs
and scheduling stalls; they do not identify SDK mask changes or prove causation.

Run `audit_web_performance.py --report PATH` for receipt integrity, exact frozen
source/runtime bytes, dispatch timing and final audio accounting. Then run
`audit_active_field.py --report PATH` for the separately declared field criteria.
A well-formed report can still fail the field check through an incomplete route,
extra input, discarded frames or audio loss. Neither result proves guest update
deadlines, physical input/paint timing, Safari/mobile behavior, listening quality
or full performance acceptance. Inspect actual field motion separately.

Audits write new source copies and hash-bearing JSON receipts beside the report.
Existing receipts are never overwritten. Preserve failed attempts alongside any
later repeat; a clean repeat alone does not establish a causal fix.
