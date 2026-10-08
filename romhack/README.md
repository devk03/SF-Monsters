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

The overlay includes original Sunset/South Park layouts, the courier quest,
clinic and Cognition gym draft, three starter/call candidates and Sunset/wild-battle
theme candidates. Other creatures, cast art, tiles and music remain scaffolding;
this is not the accepted polished slice or complete SF campaign.
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
views, icon poses, cries and Bubble Beam/Ice Beam learning. Evolution targets
must be authored, acyclic and have increasing level thresholds. Other native
evolution methods remain available in the engine; their original content
authoring rules are unfinished. Pixel cleanup, other evolution-line art and user approval
remain required; these are not finished or approved catalog entries.

`scripts/romhack/monster_atlas.py` encodes distinct battle and authored icon
frames into shared native palettes without changing the legacy encoder.
The evolved icons share CinderCoy's reserved group 3. Layouts and exact built-in
imagegen prompts stay beside each source image under `assets/monsters`.

For isolated evolution UI checks, use `build_probe.py --draft --fixture cinder-15`
or `ashrunner-35`. These private cartridges script a starting level and Rare Candy.
`brinepup-15` and `brinebull-35` prepare the corresponding Water-line cases.
they never count as earned campaign progression. Fixture publishing is rejected.
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
