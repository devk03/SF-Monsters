# Team Refresh

Original two-bar recovery cue: a bright, syncopated bell melody over a
four-chord cadence, with bass and soft keys. Its 192 ticks at 192 BPM give
2.5 seconds of nominal playback; final notes end at tick 180, leaving room
for release before the existing 160-frame clinic service gate completes.

This is a one-shot MIDI, with no loop markers. It uses a dedicated sf_heal
voicegroup, leaving the shared native fanfare instrument bank unchanged.
All four instrument waves are synthesized locally; no recordings, commercial
samples or inherited melodies are used. Score/waves: CC BY 4.0, SF Mini
Monsters contributors. Code: MIT.

Reproduce with `python3 scripts/romhack/field_music.py`. The native importer
changes only MUS_HEAL's MIDI/configuration binding, appends the independent
voicegroup, and preserves the engine's service duration. Actual playback,
transition quality and a human comparison review remain required.
