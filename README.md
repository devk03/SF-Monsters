# SF Mini Monsters

An original, open-source creature RPG set in a compressed San Francisco.

Status: concept and planning. No playable ROM or browser build exists yet.
The project name is provisional and has not been cleared for release.

## Game scope

- 16 accessible neighborhood hubs, each with a mini-adventure.
- 150 collectible mini-monster entries, including evolution stages.
- Real tech people and recognizable online personalities as the proposed cast.
- Adult SF comedy, playable drunk/high character states, and optional weird dates.
- Eight famous-startup gyms with real-person leaders, one at every second campaign stop.
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

Build Outer Sunset and Inner Sunset with three starter choices, approximately
12 mini monsters, one gym, one complete quest, encounters, recruitment,
turn-based battles, and persistent saving.

Scope, acceptance criteria, and current progress are maintained in
[the canonical specification](docs/game-spec.md#14-active-mvp-objective-and-progress).

Acceptance criteria:

- Finish the quest and gym on the same ROM in mGBA and the browser player.
- Save, close the player, reopen it, and resume progress on both platforms.
- Verify manual save export/import between the supported players.
- Build from documented prerequisites without proprietary game assets.

## Proposed architecture

Original content and C++ game code compile into a GBA ROM using Butano.
The browser player runs that ROM in a WebAssembly GBA emulator.
The emulator choice remains subject to compatibility and licensing checks.

Maps, encounters, monsters, and dialogue should have editable source data
compiled into the ROM. The browser wrapper supplies touch controls, keyboard
and gamepad input, local persistence, and save import/export.

No account system or backend is required for the first release.

## Development workflow

Commit frequently, keeping each commit coherent and reviewable.

Verify the diff and run checks relevant to the change before committing.
Stage explicit project files. Do not include credentials or unrelated changes.
Commits are authorized; remote publication and PR merges require their own scope.

## Licensing and originality

Original code and documentation are available under the [MIT license](LICENSE).
CC BY 4.0 is proposed for future original art and music; no game assets exist yet.
Dependencies and separately licensed assets retain their own licenses.
Track the author, source, and license of contributed assets.

Use original implementation and creative expression. Do not include commercial
game ROMs, copied sprites, music, scripts, logos, or proprietary BIOS files.
Review the name, branding, and distinctive mechanics before public release.

## Platform references

- [Butano](https://github.com/GValiente/butano)
- [Delta ROM importing](https://faq.deltaemulator.com/getting-started/importing-games)
- [mGBA](https://github.com/mgba-emu/mgba)
- [Candidate WebAssembly wrapper](https://github.com/wasm-gaming/mGBA-wasm)
