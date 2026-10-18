# A working contributor battle interface

This example explains the interface; it is not the finished Caffeine gym or an
approved balance/cast decision. Keep your actual contribution inside its assigned
folder. The project supplies the world, prerequisite guards, completion tracking
and badge grant.

In `romhack/modules/gym_1/module.json`, set status to `draft` and add this trainer:

```json
{
  "id": "TRAINER_ROXANNE_1",
  "name": "EXAMPLE",
  "class": "TRAINER_CLASS_LEADER",
  "portrait": "TRAINER_PIC_HIKER",
  "party": [
    {"species": "SPECIES_ZIGZAGOON", "level": 2, "moves": ["MOVE_TACKLE"]}
  ]
}
```

This native slot name is an allocation, not the character's visible identity.
It uses inherited development assets in the private ROM; original character/art
work and final Mini Monster rosters are separate production tasks.

Replace the package's content.inc with:

```asm
SFMod_gym_1_Run::
    checktrainerflag TRAINER_ROXANNE_1
    goto_if_eq SFMod_gym_1_Won
    trainerbattle_single TRAINER_ROXANNE_1, SFMod_gym_1_Intro, SFMod_gym_1_Defeat, SFMod_gym_1_Won
SFMod_gym_1_Won::
    sfmodule_return 1
SFMod_gym_1_Intro::
    .string "Example contributor battle.$"
SFMod_gym_1_Defeat::
    .string "The module can finish now.$"
```

The **fourth argument** is the explicit victory continuation. An ordinary stock
trainer encounter without that callback can end after battle without reaching
the module's reward path. The loader rejects that form. `sfmodule_return 1` is
lowered into a jump to the core's completion path, so it does not depend on a
call stack surviving a native battle. Use `sfmodule_return 0` to decline/cancel.
Use native `return` only in an internal subroutine with a matching local call.

The core clears the result before entry, checks existing world prerequisites,
rechecks them before granting any output (including direct contributor NPC entry),
and records the module's separate completion flag before its fixed output. Old
blockout badge stamps do not mark this new content complete. A revisit can read
the allocated completion flag or trainer flag; authors must define their revisit
experience. Persistent puzzle flags are available separately.

## Fresh-game playtest

With the documented native Mac toolchain installed, run:

```sh
make module-check MODULE=gym_1
make module-playtest MODULE=gym_1 SCENARIO=ready
make module-preview
```

Open `.tools/pokeemerald-world-host/sf-module-playtest.gba` in mGBA and start a
**new game**. You arrive in the assigned room with a traversal loan and the
required incoming state. No owner's private save is needed. Talk to the scientist.
The builder creates an ignored BPS/cartridge/ELF and frozen receipt; it bootstraps
the pinned patch encoder if missing.

Other scenarios use the same command with:

| Scenario | Purpose |
| --- | --- |
| `locked` | Omits incoming prerequisites; gyms/missions with prerequisites stay locked |
| `completed` | Sets the module's completion and fixed output for revisit testing |
| `weak-party` | Supplies a level-1 loan for real battle loss/retry testing |

Gym 1 has no incoming badge requirement, so `locked` does not invent one. A weak
party does not guarantee a loss against every roster; play the actual encounter.
The sample is deliberately trivial and is not a campaign difficulty test.

QA saves use magic `0x4D51`, distinct from normal world drafts (`0x5742`) and v80
(`0x5346`). Keep them separate. These scenarios inject prerequisites for testing
and are marked **not campaign progression evidence**. `make world-draft` builds
normal geography/progression instead.

The same generated ROM is used for native and web testing. `make module-preview`
opens a finite localhost-only player; click Start test and choose NEW GAME.
It uses the repo's WASM emulator without production accounts or save persistence.
No owner's private checkpoint is required. Use `PYTHON=python3` on native make
commands if the optional project venv is absent. A public contributor
preview uploader for arbitrary module patches is not yet provided; do not replace
the public v80 patch to demonstrate a PR. The other private WASM/browser QA
harnesses can also inspect these builds; see `scripts/quality/README.md`.
Include reproducible ROM/patch hashes and evidence; never attach full ROMs or saves.
