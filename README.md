# SF Mini Monsters

An original, open-source creature RPG set in a compressed San Francisco.

Status: playable MVP. Explore Outer Sunset and SoMa, recruit 12 original monsters,
and complete the courier quest and Cognition gym on the same GBA cartridge.
All playable locations are inside San Francisco.

[Play online](https://sf-mini-monsters.devkunjadia03.chatgpt.site) ·
[Download the GBA ROM](https://sf-mini-monsters.devkunjadia03.chatgpt.site/game/sf-mini-monsters.gba)

## Game scope

- 16 accessible neighborhood hubs, each with a mini-adventure.
- 150 collectible mini-monster entries, including evolution stages.
- Real tech people and recognizable online personalities as the proposed cast.
- Adult SF comedy, playable drunk/high character states, and optional weird dates.
- Eight famous-startup gyms with real-person leaders and sourced geographic placements.
- A four-member championship followed by a champion battle.
- A recurring antagonist, a villain organization, and one legendary mini monster.
- Original creatures, artwork, music, dialogue, interface, and game code.
- A GBA ROM playable in standard GBA emulators and a browser through WebAssembly.
- Public source, editable content, and documented builds for contributors.

The [v1 specification](docs/game-spec.md) defines the full proposed game.
It includes support for approximately 50 additional researched Twitter personalities
after the main game is complete.
Sourced character candidates and fictional roles are in [cast research](docs/cast-research.md).

## First playable milestone

Build Outer Sunset and SoMa with three starter choices, approximately
12 mini monsters, one Cognition gym, one complete courier quest, encounters, recruitment,
turn-based battles, and persistent saving.

Scope, acceptance criteria, and current progress are maintained in
[the canonical specification](docs/game-spec.md#14-active-mvp-objective-and-progress).

Acceptance criteria:

- Finish the quest and gym on the same ROM in mGBA and the browser player.
- Save, close the player, reopen it, and resume progress on both platforms.
- Verify manual save export/import between the supported players.
- Build from documented prerequisites without proprietary game assets.

## Architecture

Freestanding C and original assets compile into a GBA ROM using GCC for ARM.
The browser runs that ROM in mGBA through WebAssembly.
The website uses React/Vinext and Sites hosting with optional ChatGPT sign-in.

Maps, encounters, monsters, and dialogue should have editable source data
compiled into the ROM. The browser wrapper supplies touch controls, keyboard
and gamepad input, local persistence, and save import/export.

Guest play is available. Signed-in players get a separate device-local save slot.
There is no database or cloud-save service.

See [build, controls, save transfer, and QA instructions](docs/testing.md).

## Development workflow

Commit frequently, keeping each commit coherent and reviewable.

Verify the diff and run checks relevant to the change before committing.
Stage explicit project files. Do not include credentials or unrelated changes.
Commits are authorized; remote publication and PR merges require their own scope.

## Licensing and originality

Original code and documentation are available under the [MIT license](LICENSE).
Original generated sprite atlases are offered under CC BY 4.0 to the extent
licensable; see [asset credits](assets/README.md).
Dependencies and separately licensed assets retain their own licenses.
Track the author, source, and license of contributed assets.

Use original implementation and creative expression. Do not include commercial
game ROMs, copied sprites, music, scripts, logos, or proprietary BIOS files.
Review the name, branding, and distinctive mechanics before public release.

## Platform references

- [mGBA](https://github.com/mgba-emu/mgba)
- [Candidate WebAssembly wrapper](https://github.com/wasm-gaming/mGBA-wasm)
