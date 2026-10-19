# World-only browser speed

Load `/emulator/world-entry.js` as a module. It exposes:

- `window.sfWorldMonstersLoad(config)`: the existing SDK load configuration and
  engine methods, plus `getSpeed(): 1 | 2` and `setSpeed(1 | 2): 1 | 2`.
- `window.sfWorldMonstersExtract(bytes)`: the existing local `.gba`/ZIP extractor.

Pass the world-specific `storageNamespace` and `persist: null` when the player
owns battery persistence. This entry does not assign the Sunset loader globals.
The existing `/emulator/entry.js`, SDK, core, worklet and capture ABI are unchanged.

Every new engine starts at 1×. If the UI keeps a selected speed while loading a
new ROM/engine, call `setSpeed(selectedSpeed)` on that engine before `start()`.
Reset, reboot, battery import and state loading retain the current engine's speed.
Unsupported values throw `RangeError` before changing anything. Speed changes do
not advance or reset the guest, flush PCM, write Flash, or persist a preference.
The `speed` event reports `{type: 'speed', speed: 1 | 2}` when the value changes.

At 2×, guest frames run twice as fast and the unchanged worklet consumes source
PCM at twice the native rate. Sound therefore becomes faster and higher pitched;
this is not pitch-preserving time stretching. Native source-rate changes are
still detected. The per-tick frame cap scales from 5 to 10. Returning to 1×
restores normal timing, with no catch-up against time spent at the previous rate.
Changing speed ends an active diagnostic window with reason `speed-change`; that
window cannot pass the existing uninterrupted-duration acceptance gate.

`world.sdk.js` is a generated derivative of the SHA-pinned original SDK. Review
changes in `scripts/quality/generate_world_runtime.py`; regenerate with
`python3 -B scripts/quality/generate_world_runtime.py` and verify using `--check`.
The generator refuses an unexpected source SDK instead of changing the pinned
runtime or silently absorbing unrelated behavior.

Validation:

```sh
python3 -B scripts/quality/generate_world_runtime.py --check
node --test tests/world_speed_test.mjs
SF_WORLD_SPEED_ROM=/absolute/private/world.gba node --test tests/world_speed_test.mjs
```

The regular tests load the actual SDK with a fake core and execute the unchanged
AudioWorklet source. They compare 1× frame/PCM/battery behavior against the original
SDK, exercise 2× playback at both GBA source rates, and cover validation, toggles,
pause/resume, reset/reboot/import and new-instance defaults. The optional private
cartridge check runs the pinned WASM core and compares guest frame count, final
video and battery at 1× versus half-duration 2×; it also checks that toggling leaves
serialized core state identical. No ROM or private save is included in the tests.
These checks do not establish foreground browser, speaker or full-route acceptance.
