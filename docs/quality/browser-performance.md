# Reproducible browser measurements

The browser probe records requested/executed/video frames, discarded pacing debt,
canvas submissions, input pipeline stages and actual audio-sink counters. It is
off until `startDiagnostics` is called and stops after its finite window.

Use a controller-only native capture from the same verified cartridge, retaining
its `.state`, `.sav` and `.json` companions. Start one private session:

```sh
.tools/venv/bin/python scripts/quality/serve_web_performance.py \
  --rom /absolute/path/target.gba --state /absolute/path/capture.state \
  --name fresh-session-name --port 18766 --seconds 1800
```

The server binds127.0.0.1 only, freezes exact frontend/runtime bytes, checks the
native snapshot header/ROM/core identity and preserves evidence under ignored
`.tools/benchmarks/fresh-session-name`. Existing names fail. Its lifetime is at
most3600seconds; no recurring job starts. Full cartridges stay local.

Open the printed address in the declared browser. Load the checkpoint, let audio
settle, and keep the page visible for a10-second,2-minute or10-minute window.
The optional four-direction loop sends ordinary scripted DOM keyboard events.
Record the actual scene and host; that loop does not detect or prove a scene.
Use Finish local QA afterward, close the test tab and stop the server when done.

Audit a saved report against its preserved runtime, not whatever source is newer:

```sh
.tools/venv/bin/python scripts/quality/audit_web_performance.py \
  --report .tools/benchmarks/fresh-session-name/report-UUID.json
```

The audit preserves its own source and rejects mismatched runtime bytes, wrong
audio epochs, inconsistent frame totals, regressing/invalid final audio counts
and malformed percentiles. `receipt_well_formed` validates evidence structure;
nonzero drops/underruns remain reported failures, not a passing gate.

Input timestamps begin at the DOM handler/API dispatch. `dispatchToFrameMs` ends
after the next completed emulation batch; `dispatchToSubmitMs` ends at canvas
submission. Neither proves guest consumption, physical-key time or screen paint.
At120Hz, many callbacks execute no guest frame, so per-rAF median work can be0.
Actual video counters are not counts of game updates or callback completions.

The final audio ACK includes its own rendered-frame interval/output sample rate.
Compare that interval with the main window and preserve any discrepancy. Zero
starvation does not imply zero loss: a full sink drops incoming source samples.
For example, the recorded600second IAB run has0starvation but469829dropped source
frames and592.864audio-clock seconds; it fails audio continuity. Cause remains open.

Three10-minute scene regimes, native/Chromium/Safari/physical-phone coverage,
matched diagnostics-off/on overhead, guest-update/render deadlines, actual
input-to-visible response and listening for transition/loop clicks remain separate
acceptance work. Do not promote a short field observation into those gates.


New diagnostic windows also bracket AudioContext.currentTime reads with two
performance.now readings at start and close. The auditor reports the context-time
change and the wall-clock read interval separately from worklet output frames.
These are quantized context-clock observations, not hardware/speaker timestamps.
A discrepancy is retained as evidence; it does not select a cause or adjust pitch
or pacing. Historical receipts without start anchors remain explicitly unavailable
for this comparison. The anchor calls run only when diagnostics start/close.


The new sink candidate accumulates40ms of source-rate PCM once before initial
playback and after an explicit playback reset. This deliberately adds audio delay
(plus chunk/quantum alignment); guest execution, video pacing and interpolation
ratio remain unchanged. It never reprimes after starvation. A durable playback
flag separates initial warmup from all later underruns, across diagnostic epochs
and source-rate changes. No-PCM output stays visible as warmup/playbackStarted=false,
not a continuity pass. This cushion does not correct a sustained audio-clock deficit.
Actual browser long-run/transition checks and listening approval remain required.
