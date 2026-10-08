# Park Bench Break

Original clinic candidate: a 32-bar, 104 BPM instrumental with a relaxed
offbeat accompaniment. The flute opens after a short rest; a second phrase
climbs, the bridge changes harmony and drops percussion, then the first
theme returns with a quiet cadence. Loop duration is about 73.85 seconds.

Flute and bass use original additive waveforms. Seventh-chord piano voices,
a damped plucked string, soft kick, brush and shaker are synthesized locally.
There are no imported recordings, commercial samples or copied melodies.
Seven monophonic native tracks limit the arrangement's simultaneous voices.

The JSON is the editable score. Run `python3 scripts/romhack/field_music.py`
to reproduce its MIDI, instrument waves and native voicegroup. It replaces
the `MUS_BIRCH_LAB` binding used by the SF clinic. Healing still uses the
inherited fanfare; that context needs its own original composition.

This is an unreviewed composition/arrangement candidate. Loop and decoding
checks do not certify musical quality, mix or Emerald parity.
Original score/waves: CC BY 4.0, SF Mini Monsters contributors. Code: MIT.

Revision 2 keeps the v40 MIDI notes, tempo and mix. The flute now has a breath
attack and longer moving sustain; bass has a pluck attack before its loop.
Piano uses a fading tine strike, and guitar uses pitched damped partials with
a short pick transient. All voices remain synthesized from original code.
The importer supports native loop-start offsets so attacks play once per note.
Revision 1 assets stay preserved; reproduce that generation from commit
0898f0838e34b715e4ec0ff374de9f67c851a9c2. Current CLI writes native-v2.
The user's v40 clinic music score is 2/4. Revision 2 is unreviewed.
