# Pinned browser emulator

The acceptance reference uses mGBA 0.10.5. The packaged SDK's July 2026 core
produced different fresh-game HP digits under identical input, so the browser
now builds the same revision as the native capture harness.

Run `python3 scripts/build_web_core.py` with Docker. It pins both mGBA and the
Emscripten image, mirrors the core's compiler definitions, and emits artifacts
and a fingerprint under ignored `.tools/mgba-0105-web`. It runs no clean target.
`scripts/prepare_web.py` verifies the cached or committed artifact hashes and
shim identity before using them; it never falls back to a newer packaged core.

`mgba_0105_shim.c` derives from the upstream wasm-gaming shim at the revision
listed in its header. The adaptations preserve its SDK API while using the
0.10.5 video methods and raw hardware audio callbacks. Its bounded stereo queue
is drained by the existing browser AudioWorklet. All covered code stays MPL-2.0;
the project's original game code does not relicense it.

Native/WebAssembly comparison accepts an optional runtime directory and `audio`
after the battery argument (`-` for no battery). Audio comparison drains every
frame and verifies the complete PCM hash and sample count. Pixel failures remain
failures and write separately named diagnostic frames; no regions are masked.
