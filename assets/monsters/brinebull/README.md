# Brinebull — BrinePup evolution candidate

BrinePup evolves into Brinebull at level 16, then Tideroar at 36. The growing
sea lion keeps blue/mint coloring, external ear nubs and broad flippers; a
wave-shaped crest identifies its family. It stays Water type and learns Bubble
Beam at evolution. Its defenses and support moves provide a different role
from CinderCoy's faster attacking line.

`source-v1.png` contains original generated front/entrance/back views and
separately designed icon poses. The exact built-in imagegen prompt is in
`prompt.txt`, and source panel bounds are in `atlas-layout.json`.
`native-v1` contains 64x64 battle views, two entrance frames, two 32x32 icon
frames and shared RGB555 palettes. Icons use BrinePup's reserved group 4.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/brinebull/source-v1.png assets/monsters/brinebull/native-v1 --layout assets/monsters/brinebull/atlas-layout.json --icon-palette assets/monsters/brinepup/native-v1/normal.pal
```

Assets follow the repository's CC BY 4.0 terms, to the extent licensable.
Generated art and format checks do not approve native-size pixel cleanup,
animation or Emerald-tier craft; all remain subject to review.
