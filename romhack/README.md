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

### Native Mac build

Docker is optional on the verified native Mac path. Install Git, Python 3,
a C/C++ compiler, ARM GNU binutils/preprocessor, libpng and pkg-config. Run
`make setup` to install the project Python/Node dependencies, then:

```sh
.tools/venv/bin/python scripts/romhack/host_toolchain.py
.tools/venv/bin/python scripts/romhack/build_probe.py --backend host --draft
```

The host uses separate `.tools/pokeemerald-host` and compiler work directories.
Its fresh baseline must reproduce the pinned reference exactly before SF content
is applied. Compiler/library hashes, tool versions and the baseline fingerprint
are recorded and rechecked; changing that identity requires inspecting its proof.
Build commands have a ninety-minute limit. The existing Docker checkout, verified
cartridges and failed intermediates are preserved.

A draft keeps its immutable cartridge/ELF, patch and manifest under ignored
`.tools/romhack-drafts`. Omit `--draft` only for a validated versioned release;
the public release folder receives the patch/manifest alone.
`make hack HACK_BACKEND=host` uses the same project Python environment for a
versioned native source build. The default `make hack` backend remains Docker.

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

The overlay includes original Sunset/South Park layouts, the courier quest,
clinic and Cognition gym draft, eighteen creature/call candidates and Sunset/wild-battle
theme candidates. Cast art, tiles and most music remain scaffolding;
this is not the accepted polished slice or complete SF campaign.
Floating IPS is Alcaro's GPL-3.0 tool, pinned at
`ff216a75df0987047a67d7923567dc4482ce07ac`; its source/license stay in the local
checkout. Our browser decoder follows byuu's public-domain BPS format rather
than embedding Floating IPS code.

## Native interface text

`romhack/content/interface-text.json` declares our compact team, summary, guide
and capture labels. After compilation, `interface_text.py` resolves read-only
symbols in the linked ELF and verifies their bytes against the cartridge before
replacing them. Labels must fit their original allocations, including the native
terminator. Addresses, surrounding data and save layouts stay unchanged. Shorter
labels are terminated and padded; repeat application produces identical bytes.
Controls use the pinned engine's character map. Check actual rendered widths too:
allocation safety does not prove that a phrase fits its screen window.

When compilation is unavailable, `python3 scripts/romhack/preview_interface.py
--rom PATH` can make a private interface draft from the explicitly pinned prior
cartridge. It uses the pinned native Flips encoder and verifies reapplication.
Its manifest explicitly leaves full recompilation unverified; do not publish it
as a normal release. The inherited title and other guide graphics still need
original replacements; changing individual labels or the header does not finish branding.

The guide-header wordmark source/native conversion is in `assets/ui/field-guide`.
`interface_graphics.py` maps its ink mask into thirteen central header tiles and
preserves both outer caps and all unrelated raw tiles. A small host adapter uses
the pinned engine tool's LZ77 codec. It verifies lossless decoding and refuses a
compressed replacement larger than its original ELF allocation. Full inherited
sheets and reconstructed cartridges remain in ignored private storage.

Original title lettering is under `assets/ui/title`; run
`.tools/venv/bin/python scripts/romhack/title_art.py` to encode the source atlas.
Its logo sheet uses the native affine layer's 29-pixel horizontal offset; the
subtitle consists of two contiguous 64x32 sprite blocks. `native_resources.py`
checks ELF correspondence and compression/allocation budgets, then writes the
resource batch together. The title palette update preserves the final sixteen
creature/cloud colors. The inherited background creature/footer and title music
still need their scoped replacements and review.

Bayveil's title silhouette is under `assets/ui/title-bayveil`; encode it with
`.tools/venv/bin/python scripts/romhack/title_creature.py`. The scene keeps two
independent eye regions in the animated palette slot and supplies its own
blue/teal backing tiles for cloud blending. Its graphics/map must fit the
original allocations and decode losslessly. This title hint does not implement
Bayveil's battle art, catalog entry, stats or acquisition quest.

The original title score is `assets/audio/foglight-overture.json`. Rebuild its
eight-track MIDI with `python3 scripts/romhack/title_music.py`. The title music
overlay verifies our existing waveform bank, links native sequence data and
keeps the song-table/header address stable inside the old title allocation.
Its score/loop and mix checks support a listening review; they do not establish
soundtrack parity or complete the remaining neighborhood/encounter themes.

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
The Sunset plan is the first original layout/event draft. Inherited tiles and
wild species remain placeholders; the full first chapter is unfinished.

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
The three starters have original front/back art, entrance frames, icons and
cry candidates. CinderCoy's authored line evolves into Ashrunner at 16 and
Solhowl at 36, with new art/cry/move candidates. Explicit evolution targets
also bind BrinePup → Brinebull at 16 → Water/Ice Tideroar at 36, with their own
views, icon poses, cries and Bubble Beam/Ice Beam learning.
SproutSlug → FernSlug at 16 → Grass/Bug Canoptera at 36 includes Poison
Powder/Signal Beam learning. All three lines remain unapproved candidates.
Evolution targets
must be authored, acyclic and have increasing level thresholds. Other native
evolution methods remain available in the engine; their original content
authoring rules are unfinished. Pixel cleanup, remaining creature art and user approval
remain required; these are not finished or approved catalog entries.

`scripts/romhack/monster_atlas.py` encodes distinct battle and authored icon
frames into shared native palettes without changing the legacy encoder.
The evolved icons share CinderCoy's reserved group 3. Layouts and exact built-in
imagegen prompts stay beside each source image under `assets/monsters`.

For isolated evolution UI checks, use `build_probe.py --draft --fixture cinder-15`
or `ashrunner-35`. These private cartridges script a starting level and Rare Candy.
`brinepup-15` and `brinebull-35` prepare the corresponding Water-line cases.
`sproutslug-15` and `fernslug-35` prepare the Grass-line cases; reference fixtures
use the matching `reference-sprout-15`/`reference-sprout-35` names.
They never count as earned campaign progression. Fixture publishing is rejected.
`reference-15`/`reference-35` prepare battery inputs for the actual fixed reference
ROM with original names/stats/learnsets and compatible coordinates. Their saved
map view can carry SF tiles, so use them for evolution/menu comparisons only,
not original-world exploration evidence. Capture the reference using a9dec84d…85af.

## Original native audio

`assets/audio/creature-cries.json` declares synthesized starter calls;
`scripts/romhack/creature_audio.py` generates their PCM and native table overlay.
`assets/audio/ocean-commute.json` declares Sunset's sixteen-bar, seven-track
theme. `assets/audio/fogbank-frenzy.json` declares the twenty-four-bar wild-battle
score, with its arrangement/recipes in `scripts/romhack/battle_music.py`.
`scripts/romhack/field_music.py` generates their looped MIDI, eight original
instrument samples per theme and native voicegroups. Explicit `music_scores`
bindings select each context. Generated sources remain public and
editable; `make hack` compiles them with Emerald's MPlay sequencer.
These candidates replace only their declared contexts. Other music and cries
remain scaffolding, and all composition/presentation approvals remain pending.
Run `python3 tests/creature_audio_test.py` and `python3 tests/field_music_test.py`
to check signal/header limits, MIDI loop alignment and voice bounds.

Recovery destinations are authored in `engine-probe.json` under `recovery_points`.
Each record names an existing native healing-slot ID, an authored SF map ID and
walkable integer coordinates. NPC/warp tiles, foreign maps and duplicate slots
are rejected. Both new-game recovery slots must be declared, and every authored
`setrespawn` script must register a declared slot. The South Park clinic uses
32,6, immediately outside its entrance; the two initial slots use Sunset 23,22.
These change recovery data, without converting or deleting existing saves.

Authored SF maps reload their current layouts on Continue rather than overlaying
an older saved view. Reconstruct lasting metatile changes in the map's on-load
script from persistent flags/variables. The gym gate already follows this rule.
Valid saved coordinates are retained; newly blocked positions use the native
same-map warp to a nearby walkable tile, avoiding doors and NPC anchors.

## Original Sunset streets

`assets/tiles/sunset-streets` contains original asphalt, sidewalk, curb/corner,
lane, crossing and drain textures. `street_art.py` builds the native palette and
directional variants, then selects road records from map adjacency. It preserves
the upper collision/elevation bits and existing event coordinates.

The complete house/street sheet is compiled from original indexed art with
256 secondary tiles, including coastal terrain; its compressed allocation comes from the actual source
build. Metatile records use separate house/street palette banks. Normal native
resource guards still verify lossless encoding, ELF correspondence and bounds.
The older road ID aliases the new asphalt for legacy map-view buffers, while
authored SF layouts reload on Continue. Coastal ground/water now use original
art; field-effect sprites and human pixel-art approval remain pending.

This sheet requires normal source compilation. The old pinned-cartridge
`preview_interface.py` path rejects the current world revision; use
`build_probe.py --backend host --draft` for an immutable local candidate.


## Courier apartment

The first Sunset rowhouse opens into the courier's studio. `apartment.json`
provides native collision and reciprocal warps; `apartment.inc` stores the
optional beacon puzzle in reserved `VAR_GIFT_UNUSED_3` (`0x40E0`). States 0/1/2/3
mean unread observation / observed fog / reward pending / reward claimed.
Do not reuse this variable for other gifts. A full capsule pocket preserves
state 2; collecting the reward sets 3. Rest heals the party without changing
the declared recovery destination. Badge-dependent return dialogue changes
only after the first gym is won.

`assets/tiles/courier-apartment/source.png` and its prompt document the original
room artwork. `apartment_art.py` converts it to an eleven-column native scene,
444 tiles, 111 metatiles and palette bank 6. Covered-layer attributes keep the
opaque backdrop below the player; metatile 616 is the south-arrow exit.
The build compiles a separate secondary tileset. `tile_grid_base` assigns each
cell its scene record while retaining map collision/elevation. Native asset
tests protect the layer, capacity and exit. The initial exterior door uses a
native fade; authored door opening frames and human art approval remain pending.


## Rowhouse doorway animation

`assets/tiles/sunset-door` contains the original three-stage sheet and its prompt.
`door_art.py` uses the existing house palette, keeps frame columns aligned and
serializes three groups of eight tiles at offsets 0/256/512. It registers the
768-byte payload in the native door table for metatile 635. The two animated
facade cells use the same top-background layer as their closed artwork, keeping
fog lighting consistent. The drawing hook is limited to Sunset and these
cells; other doors and native opening/closing timing retain their behavior.

Run `python3 tests/door_art_test.py` for native allocation checks. Source art,
matched comparison evidence and human approvals are recorded in spec section 15.


## Coastal terrain

`assets/tiles/sunset-terrain` contains the original 4x4 atlas, prompt, native
cells, palette and three ocean/surf stages. `terrain_art.py` remaps ground
records while retaining collision/elevation and event positions. The shared
secondary sheet reserves slots 240–247 for animated tiles, so even identical
static pixels cannot alias mutable water graphics. Palette bank 12 is separate
from streets (11) and houses (10). Native DMA updates eight tiles each sixteen
frames; the loop is 48 frames.

The camera's Sunset-only padding selector continues the coast west of the map;
it changes displayed graphics, not physical boundaries or map connections.
`coastal_border_test.c` and native gameplay evidence cover its edges. Sand uses
the native sand behavior, water uses ocean behavior, and encounter grass keeps
the native tall-grass behavior. Field-effect art and human approval remain open.


## South Park streets and entrances

`park_map.py` compiles a standalone `gTileset_SFSouthPark` secondary tileset
from original streets, terrain, facades and park furniture. Its 469 tiles,
122 metatiles and five palette banks leave native door animation slots free.
Ground uses the covered layer below actors; warehouse/clinic foundations block
walking except at reciprocal native door warps. Older saves on newly blocked
foundations relocate through the same-map recovery guard.

Editable source images, native derivatives and exact generation prompts are in
`assets/tiles/south-park-buildings`, `south-park-furniture` and `south-park-doors`.
`park_doors.py` packs six original 16x32 frames and registers metatiles 583/618
with the existing native animation timing. Transparent margins reveal our
sidewalk. Gym/clinic interiors still need original art and user review.

Run `.tools/venv/bin/python tests/park_art_test.py` for native resource, layer,
door and gameplay reachability checks. Controller recordings and approval
status are documented in spec section 15; passing checks is not art approval.


## Cognition office candidate

`office_art.py` compiles the original sixteen-card atlas in
`assets/tiles/cognition-office` into a standalone secondary tileset. The native
source has 319 tiles, 81 metatiles and palette banks 6–9. Its floor stays beneath
actors. Record 2 preserves the scripted gate-open floor (0x202); record 1
retains the south-arrow exit behavior. The existing room collision/elevation
bits, NPCs, warps and event coordinates are preserved.

The incident log now appears on a server terminal, the team plan on a
whiteboard, and the coffee reward on its counter. The source, prompt, native
atlas, indexed cards and palette are editable; resized candidates still need
pixel cleanup and user review. Native old-save resume and exit/return evidence
are in spec section 15. Public release preparation remains separate.


The current bright candidate uses source-bright-v2.png and v3 native derivatives.
The original source and one-bank/v2 derivatives remain preserved. Four banks
separate floors/walls, furniture, vegetation and relay/whiteboard colors while
sharing ground/outline colors. The four workstation corners now use different
arrangements: storage, desk, whiteboard and server equipment. Walking assets,
animation timing, room collision/elevation and event coordinates are unchanged.
The user's earlier review requested brighter art and less repetition and gave
positive animation feedback; no 4/4 approval was inferred.
