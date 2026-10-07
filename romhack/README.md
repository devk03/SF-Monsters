# SF Emerald ROM hack

The main game now uses Emerald's actual engine. The user approved this path and
a website that patches a locally supplied Emerald ROM on October 7, 2026.
The complete SF scope and quality gates remain in `docs/game-spec.md` section 15.

Our public repository contains original SF contributions and build/patch tools.
Full commercial and reconstructed cartridges stay under ignored `.tools`.
The release website distributes the patch and emulator; a player's base ROM
is validated and patched locally, without uploading it to a server.

Pinned sources:

- [pret/pokeemerald](https://github.com/pret/pokeemerald), commit
  `731ad5bfd6e6f265508d0efcca0ba42f9dcf5881`.
- [pret/agbcc](https://github.com/pret/agbcc), commit
  `da598c1d918402c42c0c0d7128ba14567f3175e9`.
- Official devkitARM container digest in `romhack/Dockerfile`; host libpng 1.6.39.

Prerequisites: Docker, Git and Python 3. Run
`python3 scripts/romhack/bootstrap.py` to build the original matching baseline.
The result must match SHA-1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7` and the
user-approved SHA-256 in the spec. Build evidence goes to
`.tools/romhack-baseline/build.json`; the local ROM stays beside it.
If an SF overlay was previously built, bootstrap preserves its modified inputs
in ignored storage before restoring the pinned base inputs. Run `make hack`
afterward to rebuild the SF overlay. No source or intermediate files are deleted.

Compiler variants build in separate work directories. Upstream cleanup actions
move temporary files into ignored preservation storage, respecting the project's
no-deletion instruction. Game/compiler C and assembly are not changed for this
adaptation. Failed stages and their logs remain available for inspection.

Exact baseline reproduction, SF patch application and local browser ROM upload
pass. The same cartridge reaches identical native-core/WebAssembly frame output.
Flash slot validation passes; actual campaign-save transfers and the SF campaign
remain outstanding gates.
Renaming stock maps alone does not complete an SF neighborhood adventure.

`make hack` builds the small `engine-probe.json` overlay, creates a BPS delta
with pinned Floating IPS, and independently reapplies it to the validated base.
Repeated builds must reproduce the same patch; changing a published version's
bytes requires a version bump. The public `romhack/releases` folder contains
patches and integrity manifests, never full ROMs.

The engine probe changes the opening dialogue and hometown label. Stock art,
creatures, maps and campaign remain scaffolding; it is not the SF campaign MVP.
Floating IPS is Alcaro's GPL-3.0 tool, pinned at
`ff216a75df0987047a67d7923567dc4482ce07ac`; its source/license stay in the local
checkout. Our browser decoder follows byuu's public-domain BPS format rather
than embedding Floating IPS code.

## Editable SF maps

`scripts/romhack/maps.py` compiles original ASCII layouts into Emerald's native
16-bit map blocks. A map plan specifies rows, a token legend containing metatile
ID/collision/elevation, positioned NPCs, native warp/trigger/sign events, and an
original script file. The build rejects uneven rows, invalid tile packing,
blocked/out-of-bounds event positions, duplicate NPC IDs/positions and object
budget overflow. New-game spawn must be a walkable authored tile.

Stock script symbols remain available for engine linkage; their map-entry
header is replaced by the SF script. Modified engine inputs are recorded under
ignored storage so baseline bootstrap can preserve and restore them later.
Run `python3 tests/romhack_maps_test.py` for format and event-boundary checks.
Inherited tiles are local development scaffolding, not publicly copied assets.

`build_probe.py --draft` keeps immutable iteration patches in ignored storage,
keyed by target hash. Publish with `make hack` after the relevant native checks.
The Sunset plan is the first original layout/event draft. Its inherited art,
species and music are placeholders; the full first chapter is unfinished.

Native captures now export `.sav` battery files beside their `.state` snapshots.
`capture_core.py --battery PATH` tests a cold battery-save boot; `--state PATH`
resumes an emulator snapshot instead. They are mutually exclusive.
Raw snapshots do not contain Flash bytes; the harness restores a matching `.sav`
companion automatically when continuing a recorded snapshot.
`tests/foundation_runtime.cjs ROM INPUT NATIVE_DIRECTORY BATTERY` verifies actual
WebAssembly restore/export and native frame/save equality for a recorded route.

## Original species overlay

`romhack/content/monsters.json` binds original creatures to stable native species
IDs. The importer supplies names, six stats, types, abilities, learnsets, guide
text, front/back coordinates, entrance frames and party-icon palette groups.
Native PNGs must satisfy the dimensions and indexed-color contracts; source art
and conversion notes stay editable under `assets/monsters`. Palette groups 3–5
are shared by original party icons; icons in a group must use that group's colors.

Content revision upgrades run once on Continue and cover party and storage.
Only an exact former default nickname changes; custom names remain. Earned
early moves fill empty slots without removing existing moves. Party stats are
recalculated from unchanged experience, nature, IVs and EVs. Schema/quest/badge
identity stays intact; Flash changes only when the player saves normally.
The current CinderCoy candidate still needs pixel cleanup, original cry and
complete evolution-line art. It is not a finished or approved catalog entry.
