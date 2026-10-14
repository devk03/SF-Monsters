# Native input and instruction observation

Run `scripts/quality/profile_native_input.py --help` from the project Python
environment. Supply `--rom`, its matching `--elf`, a controller-only `--state`
with its original `.json` and companion `.sav`, a headerless `--input` CSV and
a new `--name`. Rows contain decimal `keys,duration`; the pilot permits at most
120 frames and rejects opposing direction pairs. Begin with a changed held mask.
All output stays in ignored `.tools/benchmarks`; existing evidence is preserved.

The command verifies pinned native library/source, cartridge and state provenance,
ROM/ELF function bytes and Main key offsets compiled by cartridge agbcc. It compares
all RGBA frames, PCM, final state and Flash against the unchanged capture harness.
Control and observer must be exact; timing observations are rejected otherwise.
Each subprocess is bounded to60 wall seconds, including bootstrap and output IO.

Add `--step` to compare two additional variants: instruction stepping without
observations and stepping with KEYINPUT/transition observations. The step path
uses the existing core event-drain function, samples PC after pending IRQ events
and yields at the same frame-ending event as stock runFrame. It never writes
guest registers or RAM, adds breakpoints or synthesizes game-update counters.

`hooks.csv` timestamps actual KEYINPUT read-hook entry before final instruction
cost. `frames.csv` samples the game's raw held mask at frame end: a changed mask
is an acknowledgement upper bound. Requested masks alone are not acknowledgements.
Time is unsigned-unwrapped mTimingCurrentTime relative to the loaded state;
stock mTimingGlobalTime is unsuitable because this build disables debug clocks.

Step `events.csv` records executed source/destination PCs, kind, value and guest
completion cycle. Kinds1–3 are ReadKeys call/load/return;4–5 are wrapper/callback
dispatcher entries;6–7 are actual callback1/2 dispatches;8–9 are their pending
returns;10–12 are wait entry, VBlank-bit clear completion and wait return.
NULL callback skips cannot create pending callback spans. Initial/final partial
spans require explicit treatment by any downstream analysis.

Kind13 records native VBlank callback delivery and lateness derived from the
already-scheduled Hblank event. Nominal time is delivery minus lateness. Run
`analyze_native_loop.py --capture PATH` on an accepted step capture to pair spans,
retain edge partials and compare work-clear completion against the first nominal
VBlank after each observed loop start. That marker is not a browser paint or a
complete renderer handoff. Event schema1 and exact metadata/trace hashes are
required; source/build inputs must stay unchanged through calibration.

These short native calibrations establish no browser/mobile, input-to-photon,
ten-minute stability, display deadline or human quality gate. Single-pair wall
timings include audio output callbacks and do not establish instrumentation cost.
