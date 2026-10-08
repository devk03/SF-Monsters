# SF Mini Monsters

A San Francisco creature RPG with public SF content and development tools.

The main build is now an Emerald ROM hack. Players supply their own base
ROM to the website for local patching. The pinned engine baseline reproduces
Emerald exactly; the first SF content overlay is an unreviewed engine proof.
See [the hack workflow](romhack/README.md) and the active spec in section 15.

Status: the current preview includes the Outer Sunset opening, Muni travel,
South Park clinic and Cognition's first gym draft. BrinePup, SproutSlug and
CinderCoy are original starter/call candidates. Ocean Commute and Fogbank Frenzy
are the original Sunset and wild-battle theme candidates. The preview now has
eighteen original creature candidates, original title art/music and six Sunset
rowhouse facades, street textures and coastal ground/wave animation. The first house now has an original
enterable courier studio with an animated doorway: a fog-beacon puzzle, one-time capsule reward, team
rest and an N-Judah history postcard. South Park now has original brick/clinic facades, street paving, park furniture
and animated entrances. Cast art, other interiors and other music still use
placeholders. The full SF campaign and Emerald quality
approval remain outstanding.
CinderCoy now has authored Ashrunner (level 16) and Solhowl (level 36)
evolution candidates, with new views, icon poses, cries and move progression.
BrinePup now has Brinebull (level 16) and Water/Ice Tideroar (level 36)
candidates with their own art, cries and defensive move progression.
SproutSlug now has FernSlug (16) and Grass/Bug Canoptera (36) candidates.
All three authored lines still need pixel cleanup and user quality approval.
The gym/clinic now have furnished interiors, an incident log, a planning board
and a one-time emergency Potion. Older saves reload updated rooms safely.
Cognition now has distinct original field-sprite candidates for Scott Wu,
Walden Yan and Steven Hao, each with native walking poses. Trainer battle
portraits and the other named cast remain unfinished.

[Play online](https://sf-mini-monsters.devkunjadia03.chatgpt.site) ·
[Download the SF patch](https://sf-mini-monsters.devkunjadia03.chatgpt.site/patch/sf-mini-monsters.bps) ·
[Earlier standalone prototype](https://sf-mini-monsters.devkunjadia03.chatgpt.site/prototype)

Load the supported Emerald `.gba` or ZIP to play. ROM bytes stay on your device.
The player can download the patched cartridge for a standard GBA emulator.

## Game scope

- 16 accessible neighborhood hubs, each with a mini-adventure.
- 150 collectible mini-monster entries, including evolution stages.
- Real tech people and recognizable online personalities as the proposed cast.
- Adult SF comedy, playable drunk/high character states, and optional weird dates.
- Eight famous-startup gyms with real-person leaders and sourced geographic placements.
- A four-member championship followed by a champion battle.
- A recurring antagonist, a villain organization, and one legendary mini monster.
- Original SF creatures, artwork, music, dialogue and campaign on Emerald's engine.
- A GBA ROM playable in standard GBA emulators and a browser through WebAssembly.
- Public source, editable content, and documented builds for contributors.

The [v1 specification](docs/game-spec.md) defines the full proposed game.
It includes support for approximately 50 additional researched Twitter personalities
after the main game is complete.
Sourced character candidates and fictional roles are in [cast research](docs/cast-research.md).

## Previous technical milestone

Build Outer Sunset and SoMa with three starter choices, approximately
12 mini monsters, one Cognition gym, one complete courier quest, encounters, recruitment,
turn-based battles, and persistent saving.

Scope, acceptance criteria, and current progress are maintained in
[the canonical specification](docs/game-spec.md#15-active-emerald-parity-goal).
The active goal requires Emerald-tier quality across all eleven audited domains,
with user-approved comparison clips and the complete SF campaign.

Acceptance criteria:

- Finish the quest and gym on the same ROM in mGBA and the browser player.
- Save, close the player, reopen it, and resume progress on both platforms.
- Verify manual save export/import between the supported players.
- Build from documented prerequisites without proprietary game assets.

## Architecture

The main build overlays SF content on a pinned Emerald decompilation and releases
a BPS patch. A player's local base ROM becomes the same patched cartridge used
in native mGBA and the WebAssembly player. Full inherited cartridges stay private.
The earlier freestanding C prototype remains archived and playable at `/prototype`.
The website uses React/Vinext and Sites hosting with optional ChatGPT sign-in.

Maps, encounters, monsters, and dialogue should have editable source data
compiled into the ROM. The browser wrapper supplies touch controls, keyboard
and gamepad input, local persistence, and save import/export.

Guest play is available. Signed-in players get a separate device-local save slot.
There is no database or cloud-save service.

See [build, controls, save transfer, and QA instructions](docs/testing.md).

## Development workflow

Commit coherent changes every 200–300 handwritten code lines when practical,
with smaller completed fixes committed at logical boundaries.

Verify the diff and run checks relevant to the change before committing.
Stage explicit project files. Do not include credentials or unrelated changes.
Commits are authorized; remote publication and PR merges require their own scope.

## Licensing and originality

Original code and documentation are available under the [MIT license](LICENSE).
Original generated sprite atlases are offered under CC BY 4.0 to the extent
licensable; see [asset credits](assets/README.md).
Dependencies and separately licensed assets retain their own licenses.
Track the author, source, and license of contributed assets.

Publish original SF contributions and patches, never full commercial or
reconstructed cartridges. Our license does not relicense Emerald's inherited
engine or assets. Keep full ROMs in ignored local storage.

## Platform references

- [mGBA](https://github.com/mgba-emu/mgba)
- [Candidate WebAssembly wrapper](https://github.com/wasm-gaming/mGBA-wasm)
