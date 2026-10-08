# PierPeep — original first-slice creature candidate

A Water/Flying harbor pelican with a broad pouch beak and slate wings. It
combines ranged water damage with flight and later stockpile/recovery utility.

Stable native slot `WINGULL` retains its experience curve and save identity.
Catch rate, battle experience and six EV yields are explicitly authored in
`romhack/content/monsters.json`. Content revision 8 upgrades only default stock
names and earned moves into empty slots. Existing moves/PP, experience, personal
variation and held items remain intact. No stock evolution remains enabled;
an original target must be authored before this creature evolves.

`source-v1.png` was created with built-in imagegen. `prompt.txt` stores the exact
prompt and `atlas-layout.json` records actual source panels. Front, entrance and
separate rear views share fifteen opaque RGB555 colors. Two simplified icon
poses map into reserved original palette group 4; color cleanup remains pending.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/pierpeep/source-v1.png assets/monsters/pierpeep/native-v1 --layout assets/monsters/pierpeep/atlas-layout.json --icon-palette assets/monsters/brinepup/native-v1/normal.pal
```

Its original harmonic/formant cry is authored in `assets/audio/creature-cries.json`;
`python3 scripts/romhack/creature_audio.py` reproduces native PCM and audition WAV.
No commercial creature art or recorded cry was used as a source. Original asset
licensing follows repository CC BY 4.0 terms, to the extent licensable.
Pixel/outline cleanup and native battle/party art/audio review remain pending.
Generated or compiled assets do not establish Emerald-tier craft or user approval.
