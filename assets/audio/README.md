# Original creature-call candidates

`creature-cries.json` contains the editable synthesis recipes. No recordings,
commercial samples or stock creature cries are used to make these calls.
`scripts/romhack/creature_audio.py` combines voiced harmonic partials, formant
resonances, filtered breath noise and shaped envelopes. Reproduce with:

```
python3 scripts/romhack/creature_audio.py
python3 tests/creature_audio_test.py
```

`cries-v1/` contains mono listening WAVs and the native signed 8-bit PCM with
WaveData headers. Each uses 10,512 samples/second, no loop and silent endpoints.
The importer binds these sources to the stable development slots' normal and
reverse cry voices, using uncompressed Direct Sound entries. Previewing a
starter now auditions its call in the actual game.

- CinderCoy: two rough, falling barks with breath and upper vocal resonances.
- BrinePup: two rounded lower honks with a rising second onset.
- SproutSlug: three short, higher wet trills.

These are unreviewed candidates. The native decoder and audible signal checks
do not establish character, mix or Emerald-tier quality. The original music
contexts, remaining creature calls and user listening reviews stay required.
To the extent licensable, the original recipes and sample assets use CC BY 4.0,
attributed to SF Mini Monsters contributors; generation/import code is MIT.
