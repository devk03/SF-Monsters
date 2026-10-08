# Canoptera — final SproutSlug evolution candidate

SproutSlug → FernSlug at 16 → Canoptera at 36. The garden finally takes flight:
veined leaf wings, a soft green abdomen, cream chest and blossom preserve its
family identity. Grass/Bug gives special Grass attacks and physical Bug coverage
under native Gen III rules. Signal Beam is learned at evolution; Leech Seed,
status moves, recovery and Light Screen provide support choices.

`source-v1.png` contains generated front/entrance/back views and separately
designed icon poses. `prompt.txt` records the exact built-in imagegen prompt;
`atlas-layout.json` records panels that preserve the complete wing tips.
Native assets use fifteen opaque RGB555 colors and SproutSlug's reserved icon
palette group 5. Unequal panels are padded transparently without stretching.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/canoptera/source-v1.png assets/monsters/canoptera/native-v1 --layout assets/monsters/canoptera/atlas-layout.json --icon-palette assets/monsters/sproutslug/native-v1/normal.pal
```

Original asset licensing follows the repository's CC BY 4.0 terms, to the
extent licensable. Native-size cleanup, art/animation review and user quality
approval remain pending; format checks do not prove Emerald-tier craft.
