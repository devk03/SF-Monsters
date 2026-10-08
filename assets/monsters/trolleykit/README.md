# TrolleyKit — original wild/gym creature candidate

An Electric/Steel cable stoat with copper cuffs and cable whiskers. It fills the first gym's electric defender role; Static punishes contact and its screens support a team.

Its stable native slot is `MAGNEMITE` so supported older saves retain their species
identity. Content revision 6 replaces the default stock name, stats and presentation;
custom nicknames, experience, held items and existing moves/PP remain intact.
No evolution is enabled until an original target and its acquisition rules are authored.
Gen III mechanics remain in force; Sturdy protects against OHKO moves in this engine.

`source-v1.png` is the built-in imagegen source sheet. `prompt.txt` preserves the
exact generation prompt; `atlas-layout.json` records the actual panels. Distinct
front, entrance and back views and two icon poses are encoded at native sizes.
Battle views share fifteen opaque RGB555 colors. Icons reuse reserved palette
group 3; their color simplification remains a review concern.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/trolleykit/source-v1.png assets/monsters/trolleykit/native-v1 --layout assets/monsters/trolleykit/atlas-layout.json --icon-palette assets/monsters/cindercoy/native-v1/normal.pal
```

The original synthesized cry recipe is in `assets/audio/creature-cries.json`;
`python3 scripts/romhack/creature_audio.py` reproduces its native PCM and audition WAV.
No commercial creature artwork or recorded cry was used as source material.
Original asset licensing follows repository CC BY 4.0 terms, to the extent licensable.
Pixel cleanup, native battle/party review and user art/audio approval remain pending.
Generation and format compliance do not establish Emerald-tier visual quality.
