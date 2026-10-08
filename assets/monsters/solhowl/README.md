# Solhowl — final CinderCoy evolution candidate

CinderCoy → Ashrunner at level 16 → Solhowl at level 36. The mature coyote's
charcoal saddle, ember mane and arcing tail preserve its family identity.
Fire/Dark uses special attacks for both native Gen III types; strong special
attack and speed, physical priority/Slash coverage and Roar/Sunny Day give it
several roles. Crunch is learned at its evolution level.

`source-v1.png` contains generated front, entrance pose, separate back view and
two separately designed icon poses. `prompt.txt` records the built-in imagegen
prompt; `atlas-layout.json` records the actual source panels. Native format
encoding preserves proportions, uses a shared fifteen-color RGB555 battle
palette and maps authored icons into CinderCoy's reserved group 3.

```
.tools/venv/bin/python scripts/romhack/monster_atlas.py assets/monsters/solhowl/source-v1.png assets/monsters/solhowl/native-v1 --layout assets/monsters/solhowl/atlas-layout.json --icon-palette assets/monsters/cindercoy/native-v1/normal.pal
```

Source art was made with the built-in imagegen tool. Original asset licensing
follows the repository's CC BY 4.0 terms, to the extent licensable. Native-size
pixel cleanup, animation/battle/evolution review and user quality approval remain
pending. Format compliance and generated images do not prove Emerald-tier craft.
