# Testing SF Mini Monsters

## Main Emerald engine preview

Open https://sf-mini-monsters.devkunjadia03.chatgpt.site and choose **Load .gba or ZIP**.
Supply your local English Emerald ROM matching SHA-256
`a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af`.
Validation, extraction and SF patching happen on your device. No ROM is uploaded.
Version 0.0.17 includes South Park, eighteen original creature-presentation
candidates, plus Ocean Commute (Sunset) and Fogbank Frenzy (wild battles).
Preview a starter to hear its call; explore Sunset and its encounter grass to
hear the new themes. The wild-battle mix has been raised to within 1 dB of the
measured Emerald reference. This is a mix check, not soundtrack approval. Wild
cast art, tiles and other music still use scaffolding. The opening encounter and
gym roster has original art and cry candidates, still awaiting pixel cleanup and
user review. CinderCoy evolves into Ashrunner at level 16, then Solhowl at 36.
The new forms include original art, icon poses, cries and species-specific moves.
BrinePup also evolves into Brinebull at 16 and Water/Ice Tideroar at 36,
learning Bubble Beam and Ice Beam at those thresholds.
SproutSlug evolves into FernSlug at 16 and Grass/Bug Canoptera at 36,
learning Poison Powder and Signal Beam at evolution. All three lines remain
art/animation candidates, with native-size cleanup and user review outstanding.
Private level/Rare Candy fixtures validate the evolution UI; they do not prove
earned campaign progression or balance. The South Park clinic now registers
recovery immediately outside its entrance.
After a blackout, confirm team HP is restored and relay progress remains. The full
campaign and all quality approvals remain unfinished.

Choose a companion from the three capsules near Karpathy, recover the sensor
north along Ocean Beach, then return it to Roon. Karpathy heals the team for free.
After returning the sensor, talk to Jonathan at Judah to ride Muni. In SoMa,
Cognition is near Third Street, northwest of the park. The clinic to its east
offers healing, supplies and storage. Deliver the sensor to Scott, stabilize
blue INPUT before green OUTPUT, then cross the gate for his gym battle.
Gym victory/rewards and three-starter balance still need release play checks.

Guest play works without an account. Optional ChatGPT sign-in has a separate
device-local save slot. Complete **Save** inside the game before using **Save
backup**. Emerald backups are 128 KiB Flash battery saves, distinct from the
earlier prototype's 32 KiB SRAM saves. Import rejects incompatible backups.
SF schema 1 backups carry a campaign marker. Ordinary Emerald backups and
unsupported SF schemas are rejected; older engine-preview/browser namespaces
are preserved separately. The full campaign save-transfer gate remains pending.

After loading the ROM, use **Download patched GBA** for native mGBA. Keep its
`.sav` beside the cartridge with the same basename and close the emulator before
replacing a battery-save file. Emulator savestates are not portable battery saves.

Build the matching baseline with `python3 scripts/romhack/bootstrap.py`, then
run `make hack`. See [the pinned build workflow](../romhack/README.md).
Check patch integrity and Flash-slot validation with:

```sh
node --experimental-strip-types tests/bps.test.mjs .tools/romhack-baseline/emerald-matching.gba romhack/releases/0.0.17-slice-roster-preview/sf-mini-monsters.bps .tools/browser-review/production-downloaded-v17.gba
node --experimental-strip-types tests/flash-save.test.mjs
```

Baseline bootstrap and subsequent SF rebuilding have reproduced the same ROM
and immutable patch. These checks do not establish SF content or quality parity.
The browser and native acceptance harness use the same pinned mGBA 0.10.5.
`python3 scripts/build_web_core.py` rebuilds the browser artifacts; source and
artifact fingerprints are in `web/public/emulator/core-build.json`.

### Controller captures without Docker

Use the pinned native mGBA core directly on the development Mac when Docker is
unavailable. This creates a separate host library, records its fingerprint and
preserves generated cleanup targets. It does not replace or restart Docker jobs.
Install CMake in the project venv if it is absent (`cmake==3.31.10` was used for
the current Mac evidence). Keep full cartridges, inputs and recordings in `.tools`.

```sh
python3 scripts/quality/capture_core.py --backend host --setup \
  --rom .tools/browser-review/production-downloaded-v17.gba \
  --input .tools/benchmarks/sunset-battery-continue.csv \
  --battery .tools/benchmarks/slice-roster-wasm-caught-saved/capture.sav \
  --name my-native-resume --trace-only
```

Omit `--setup` after the host core is built. Omit `--trace-only` to record video;
raw video needs about 9 MiB per game second. Losslessly compress a completed
recording with `python3 scripts/quality/frame_storage.py .tools/benchmarks/NAME`,
then encode it with `python3 scripts/quality/encode_core_capture.py` and that path.
Always choose a new name; existing evidence is preserved. `--state` requires its
original controller-only metadata and restores the companion battery before the
snapshot. A different cartridge/core revision is rejected.

The Docker-independent browser-core harness is
`node scripts/quality/capture_web_core.cjs`, with the same ROM/input/name and
state-or-battery arguments. Its optional `--video` writes compressed frames.
That Node harness proves cartridge behavior, not real browser input latency,
playback quality or sign-in. Native and WASM recordings remain separately labeled.
Routine verification runs locally; GitHub Actions is manual-only.

## Archived standalone prototype

The following walkthrough/checks apply only to `/prototype`, the original
freestanding cartridge. Its saves and mechanics are separate from the main hack.

### Play

The MVP uses one original cartridge on both platforms. All playable areas are
inside San Francisco: Outer Sunset, SoMa/South Park, and the Cognition Lab interior.

On the website, play as a guest or use Sign in with ChatGPT for a separate local
save slot. Account saves remain on this browser/device; there is no cloud sync.
Use **Save backup** before changing devices or clearing browser storage.

Download `sf-mini-monsters.gba` and open it in a standard GBA emulator. mGBA is
our reference ([default controls](https://github.com/mgba-emu/mgba#controls)). No commercial base ROM or external BIOS is required.

Keyboard in the browser: arrows move, X/A confirms, Z/B cancels, Enter opens the
menu. The on-screen controls work with touch. Native emulator key bindings may
differ (mGBA defaults: X = A, Z = B).

## Walkthrough

1. Press A, read Karpathy's introduction, and choose a companion with left/right.
2. Walk northwest to Ocean Beach. Interact with the glowing parcel around (4,3).
3. Find Roon around (6,9) and speak to him. The journal records the next objective.
4. Walk southeast to the Muni stop at (18,13); interact to travel to SoMa.
5. Enter the Cognition door around (14,6). Speak to Scott Wu near (11,2).
6. Repair relay A at (5,6), then relay B at (17,10). Return to Scott.
7. Train your lead to about level 8, or build a balanced party. Heal at the clinic
   and restock potions at Jonathan's shop.
8. Defeat his three-monster team to earn the Build Badge and finish this chapter.

Explore grass and sand for wild encounters. Weaken a monster, select Capsule,
then press A to recruit it. Six companions fit in the active party; additional
captures go into storage. Start opens team/storage, catalog, journal, save, and bag.
Karpathy and the SoMa clinic heal for free. Potions heal the team outside battle.
The SoMa shop sells capsules. Defeats return you to the neighborhood clinic and
retain quest progress.

## Save transfer

The game automatically writes versioned, checksummed cartridge SRAM after world
and dialogue actions. The browser copies valid saves to local storage periodically.
Its Import save control checks format and integrity before replacing progress.

Use Save backup to export a 32 KiB `.sav`. In mGBA, put it beside the ROM with the
same basename (`sf-mini-monsters.gba` and `sf-mini-monsters.sav`) before loading.
Close the emulator before replacing its battery-save file. Export the emulator's
battery save and use Import save on the website to return to browser play.
Emulator savestates (`.ss0`, `.state`, etc.) are not portable battery saves.

## Build and checks

Prerequisites: Node 22.13+, Python 3.12+, Clang, and `arm-none-eabi-gcc`/binutils.
Install the ARM toolchain using Homebrew on macOS or the distribution packages
on Linux. Then run:

```sh
make setup
make rom
make check
make web
cd web
npm run dev
```

`make check` covers all starter choices, corruption rejection, native/browser save
layout, quest gates, 12-entry recruitment, team/storage, gym completion, defeat
recovery, and reachability of required map locations. It also executes the actual
WebAssembly cartridge to verify boot, controller input, SRAM restore, resume, and
export. CI rebuilds the cartridge and website and uploads the GBA artifact.

For native emulator acceptance, run `make native-qa`. It prepares a fresh ROM
basename and Lua script under `build/native-qa`. Open that ROM in mGBA, then use
Tools → Scripting → File → Load script to load the matching Lua file. The script
plays through the quest with controller inputs and reports the gym result in the
console. It reads game state for navigation; it never writes stats or progress.
Each run uses a new basename so existing player saves are preserved.

For manual QA, finish the route, recruit a wild monster, switch the lead, heal,
save/reopen, and export/import on both targets. Test the site at 320, 375, 414,
768, and desktop widths. Check pause, mute, touch buttons, keyboard controls,
public guest access, and sign-in redirects.

## Known MVP limits

This chapter has two neighborhoods, one gym, and 12 monsters. The complete
16-hub city, eight gyms, 150 monsters, Elite Four, legendary quest, Marina bars,
Tenderloin character effects, dates, and expanded Twitter cast remain in the
canonical specification. Current characters have fictional dialogue and roles.

The first gym's earned Fire route is now functionally verified. Practice with
Walden and Steven, rest at the clinic between battles, buy supplies, stabilize
blue INPUT before green OUTPUT, and challenge Scott. The tested route used
physical attacks against Steven's Wingull, Fire attacks against Grass opponents,
and healing before low HP became fatal. It earned level 11 and learned Leer.
After victory, confirm one Build Badge and one Reflect disk, then leave/re-enter
and talk to Scott: the reward must not duplicate and the battle must not restart.
Save and Continue to check that the badge, party, items and gym progress survive.
This is one verified route; other starter/team strategies and normal-player
pacing still need testing, and this does not certify the finished SF campaign.

The office and clinic now have furnished work/waiting/service areas. Read the
team board near the office entrance and the incident log upstairs; the log changes
after the badge. The coffee shelf offers one emergency Potion. Repeated visits
must not grant another. Older saves reload the new layouts; a valid position stays
unchanged, while a position covered by new furniture moves to nearby safe floor.
These layouts still use inherited tile and cast art, with quality review pending.
