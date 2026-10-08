# Tideroar — final BrinePup evolution candidate

BrinePup → Brinebull at level 16 → Tideroar at level 36. Its mature sea-lion
shape, crystalline wave crest and shoulder ridges support Water/Ice identity.
High HP and defenses, special Water/Ice attacks, Protect and Rest offer a
defensive role. Ice Beam is learned at evolution. It remains a sea lion rather
than a tusked walrus or an armored humanoid.

`source-v1.png` contains original generated front/entrance/back views and
separately designed icon poses. `prompt.txt` records the built-in imagegen
prompt. `atlas-layout.json` records the actual panels; unequal-width panels
are transparently padded during native encoding to preserve full flippers,
proportions and ground alignment. Icons use BrinePup's reserved palette group 4.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/tideroar/source-v1.png assets/monsters/tideroar/native-v1 --layout assets/monsters/tideroar/atlas-layout.json --icon-palette assets/monsters/brinepup/native-v1/normal.pal
```

Assets follow the repository's CC BY 4.0 terms, to the extent licensable.
Generated art and format checks do not approve native-size pixel cleanup,
animation or Emerald-tier craft; all remain subject to review.
