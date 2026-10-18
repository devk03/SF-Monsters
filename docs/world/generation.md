# Connected-world development guide

The active October 17 milestone finishes the compact non-gym world beyond its
playable geometry blockout. The imported user plan,
`DEVELOPMENT_AGENT.md`, `docs/game-spec.md` section 15 and `romhack/world/world.json`
define its scope. The published v80 opening is a separate preview.

## World contract

The manifest generates **58 native maps: 18 destinations, 19 route connectors,
eight reserved gym rooms and 13 useful service interiors**. Outdoors stay32×24;
service rooms are16×11. Every connector uses actual walking or native water geometry
and reciprocal map connections. Streets compress distance; they do not claim that
all story stops are adjacent real-world blocks.

| Destination | Purpose / reserved content |
| --- | --- |
| Dogpatch | New game, mentor and starter scene reservation |
| Potrero Hill | First rival encounter reservation |
| Mission | Neighborhood story reservation |
| Castro | Gym 1: Caffeine |
| Outer Sunset | Gym 2: Wellness |
| Golden Gate Park / Richmond | Park exploration and coastal branch |
| Marina | Gym 3: Clout; NIMBY introduction reservation |
| Pacific Heights | Meteorite/legendary introduction revisit |
| Twin Peaks | Gym 4: Hardware; tower approach |
| Noe Valley | Gym 5: Open Source; Surf access |
| Mission Bay | Gym 6: Stealth; island return connection |
| Giants Stadium | Event reservation |
| Financial District | Gym 7: Investor |
| North Beach / Jackson Square | Gym 8: Consumer Agents; late return |
| Treasure Island | Island story checkpoint |
| Sutro Tower | Tower story checkpoint |
| Lands End / Sutro Baths | Crisis checkpoint |
| Angel Island | Landing, Victory Road tunnel switchbacks, rival staging, summit |

Both islands are required. Angel Island is the user's explicit exception to the
earlier SF-only rule. Treasure Island remains a separate destination.

The narrative route visits Pacific Heights again after Twin Peaks for the
meteorite scene; later visits Treasure Island → Sutro Tower → Lands End → returns
to North Beach for the final stamp → crosses to Angel Island. Existing roads and
water routes carry these returns. Core world finishing adds114fictional ambient residents, natural greetings,
bounded walkers,18optional local activities and a native SF map. Contributor
scenes, battles and final puzzles remain reserved.

## Traversal and contributor interfaces

Gym rooms `gym_1` through `gym_8` are stable contributor slots. Their entry tiles
are `(16,7)` in the parent area, arriving at `(16,16)` in the gym. The room's
exit trigger is `(16,20)`, returning to `(16,10)` outside. Arrivals stay separate
from triggers and NPCs. The scientist at `(12,9)` is a temporary access-stamp tool.

Stamps require the prior stamp. Stamp 5 enables native Surf; stamp 8 enables native
Waterfall and additionally requires the Treasure Island → Sutro Tower → Lands End
checkpoint chain. These are explicit development tools, not completed gym battles.
A level-100 loan Marill carries Surf and Waterfall solely for traversal testing.

The current finishing draft uses native save magic `0x5743`, schema1. Older
v81blockouts use `0x5742`; publicv80uses `0x5346`. These identities stay separate.
Do not import a v80 save into this world. The game code remains BPEE for native
Emerald Flash compatibility; browser draft QA uses no production persistence.

## Generation and private build

```sh
.tools/venv/bin/python scripts/romhack/generate_world.py
.tools/venv/bin/python tests/world_contract_test.py
.tools/venv/bin/python scripts/romhack/build_world.py
```

Generated JSON/scripts live in ignored `romhack/content/world-blockout/`.
Edit the manifest or generator, then regenerate; generated files are not a second
authoritative source. Angel Island's landing, tunnel path, rival pocket, summit
and section markers are editable under `league.blockout`.

`districts.json` owns fictional resident dialogue; `discoveries.json` owns local
favors/observations; `core-state.json` reserves their native flags explicitly.
`art-contract.json` independently declares each regional kit allocation. Do not
borrow contributor flags or shift their actor IDs. SF map positions and native
location sections belong to `world.json` under `city_guide`.

The builder uses `.tools/pokeemerald-world-host`, separate from the production
engine. A fresh engine must reproduce the pinned base before overlays. This path
does not run the production art pipeline or deploy to the website. It preserves
the base ROM and writes a version/hash-addressed draft under `.tools/romhack-drafts/`.

Each draft freezes the manifest, generated files, applied native overlays and
compiler identity. Repeated builds add fresh receipts without replacing the first
manifest. Existing differing artifacts cause an error. BPS application must
reproduce the compiled target byte for byte. Full ROMs, saves and reference assets
remain private and ignored.

## Verification layers

- `world_contract.py` independently checks source geometry, references, safe
  arrivals, reciprocal ports, native limits, eight gym slots, nine badge stages,
  actual water cuts and the approved geographic exception. Broken-world fixtures
  exercise failures without importing the generator.
- `world_native_audit.py` reads the compiled cartridge through ELF symbols. It
  checks group/header selection, tileset pointers, every tile/collision/elevation,
  NPC identities/graphics/envelopes, coordinate and background-script bindings,
  all connection records, and exact complete linked art resources. Source audits
  also reject chopped landmark cards and inaccessible viewing points.
- The controller-only probe has no guest-memory write command. It observes
  positions/flags, moves through ordinary controls, activates native HM prompts,
  and exports private evidence with cartridge identity. Finite frame, request and
  wall-clock limits prevent indefinite runs.
- Real older ordinary Saves exercise updated collision, actor-cache refresh on
  still-valid positions, land/Surf mode, completed/pending local activities and
  preserved party, money, chapter variables and Flash. Emulator states alone do
  not establish save compatibility.
- Negative native checks attempt Surf before stamp 5, Waterfall before stamp 8,
  and the final stamp before the crisis checkpoints. Ordinary Save/Continue is
  checked separately from emulator snapshots.
- Browser QA uses the same cartridge in the existing WASM runtime, with isolated
  checkpoints and finite keyboard replays. Performance receipts have narrow
  scope; desktop results do not establish mobile performance or art quality.

Current acceptance results and remaining review gates belong in spec section 15.
No blockout receipt approves the full story, graphics, soundtrack or battles.
GitHub Actions remains manual-only; routine checks run locally.
