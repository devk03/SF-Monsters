# BinPossum — original early-route creature candidate

A Normal urban opossum that treasures a bottle-cap shield. Pickup/Run Away
and fast physical moves make it an early utility companion.

It occupies stable native slot `ZIGZAGOON` and disables the stock evolution until
an original target is authored. Content revision 7 renames only the old default
nickname and recalculates party stats without replacing moves/PP, experience,
individual variation or held items. Its experience curve is retained so saved
levels do not change. Capture rate, battle experience and six EV yields are
explicitly declared in the original catalog.

`source-v1.png` was created with built-in imagegen; `prompt.txt` stores the exact
prompt. `atlas-layout.json` records separately authored front, entrance, back
and two simplified party-icon views. Battle views share fifteen opaque RGB555
colors and icons map into reserved CinderCoy palette group 3.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/binpossum/source-v1.png assets/monsters/binpossum/native-v1 --layout assets/monsters/binpossum/atlas-layout.json --icon-palette assets/monsters/cindercoy/native-v1/normal.pal
```

Its own harmonic/formant call is authored in `assets/audio/creature-cries.json`;
`python3 scripts/romhack/creature_audio.py` reproduces native PCM and audition WAV.
No commercial artwork or recorded cry was used as a source. Original asset
licensing follows repository CC BY 4.0 terms, to the extent licensable.
Native pixel cleanup, party-palette and battle/animation review remain pending.
A compiled asset or generated sheet does not establish Emerald-tier art/audio.
