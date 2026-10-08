# FernSlug — SproutSlug evolution candidate

SproutSlug → FernSlug at level 16 → Canoptera at 36. The middle-stage slug
keeps its expressive eyestalks, curled tail and cream blossom, with a fuller
fern mantle and folded leaf-like wing buds. Grass typing, defensive stats and
Leech Seed/status/recovery moves support a different role from the other lines.
Poison Powder is learned at evolution.

`source-v1.png` contains generated front/entrance/back views and separately
designed icon poses. `prompt.txt` records the exact built-in imagegen prompt;
`atlas-layout.json` records the actual panels. Native encoding preserves
proportions and ground alignment, uses fifteen opaque RGB555 colors and maps
icons into SproutSlug's reserved palette group 5.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/fernslug/source-v1.png assets/monsters/fernslug/native-v1 --layout assets/monsters/fernslug/atlas-layout.json --icon-palette assets/monsters/sproutslug/native-v1/normal.pal
```

Original asset licensing follows the repository's CC BY 4.0 terms, to the
extent licensable. Native-size cleanup, art/animation review and user quality
approval remain pending; format checks do not prove Emerald-tier craft.
