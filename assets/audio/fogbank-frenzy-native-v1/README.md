# Fogbank Frenzy — native wild-battle score candidate

An original twenty-four-bar G-minor battle cue at nominal 132 BPM. A/A2/B/A3/C/A4
phrases develop a short rising motif, answer it with descending variations,
open into a quarter-note section, then rebuild through a syncopated bridge.
The final F-sharp leads into the opening G. Seven monophonic MPlay tracks hold
lead, answering pluck, bass, chord pads, kick, snare and hi-hat. A sustained
harmonic lead and native track mix address the first candidate's low level.
A quieter pad
and off-center answer leave space for cries and move effects.

`assets/audio/fogbank-frenzy.json` contains the editable notes, rhythm and mix.
`scripts/romhack/battle_music.py` supplies arrangement and synthesis recipes;
`scripts/romhack/field_music.py` writes MIDI, waveforms and voice declarations.
All notes and samples are original. No commercial melody or recording is copied.

```
python3 scripts/romhack/field_music.py
python3 tests/field_music_test.py
make hack
```

The importer binds only the native wild-battle slot and its voicegroup.
The score's `native_volume` sets its MIDI converter gain, capped at 100 percent;
the original settings for other native songs remain intact.
Trainer/gym/rival/villain/legendary/championship cues still require original
scores. Native conversion compiles synchronized loop jumps for all tracks.
Native/browser output checks support review; they do not approve composition,
instrumentation, mix, loop listening or the complete soundtrack.
Original score/sample assets use CC BY 4.0 attribution, to the extent licensable;
generator/import code is MIT, as with the project's other original contributions.
