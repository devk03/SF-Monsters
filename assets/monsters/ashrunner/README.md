# Ashrunner — evolved CinderCoy candidate

The middle stage of CinderCoy's line: CinderCoy → Ashrunner at level 16,
then Solhowl at level 36. Its longer legs, sharper muzzle and ember mane keep
the original coyote's rust, cream and charcoal identity. It stays Fire type
and gains Flame Wheel at its evolution level.

`source-v1.png` contains generated front, entrance pose, separate back view and
two separately designed icon poses. `prompt.txt` records the built-in imagegen
prompt and correction; `atlas-layout.json` records the actual source panels.
Native format encoding preserves proportions, uses a shared fifteen-color
RGB555 battle palette and maps authored icons into CinderCoy's reserved group 3.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/ashrunner/source-v1.png assets/monsters/ashrunner/native-v1 --layout assets/monsters/ashrunner/atlas-layout.json --icon-palette assets/monsters/cindercoy/native-v1/normal.pal
```

Source art was made with the built-in imagegen tool. Original asset licensing
follows the repository's CC BY 4.0 terms, to the extent licensable. Native-size
pixel cleanup, animation/battle/evolution review and user quality approval remain
pending. Format compliance and generated images do not prove Emerald-tier craft.
