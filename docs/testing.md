# Testing SF Mini Monsters

## Main Emerald engine preview

Open https://sf-mini-monsters.devkunjadia03.chatgpt.site and choose **Load .gba or ZIP**.
Supply your local English Emerald ROM matching SHA-256
`a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af`.
Validation, extraction and SF patching happen on your device. No ROM is uploaded.
Version 0.0.8 includes South Park, three original starter candidates and their
original cry candidates, plus Ocean Commute (Sunset) and Fogbank Frenzy (wild battles).
Preview a starter to hear its call; explore Sunset and its encounter grass to
hear the new themes. Wild
creatures, cast art, other music and evolution art still use scaffolding; the full
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
node --experimental-strip-types tests/bps.test.mjs .tools/romhack-baseline/emerald-matching.gba romhack/releases/0.0.8-battle-score-preview/sf-mini-monsters.bps .tools/pokeemerald/sf-engine-probe.gba
node --experimental-strip-types tests/flash-save.test.mjs
```

Baseline bootstrap and subsequent SF rebuilding have reproduced the same ROM
and immutable patch. These checks do not establish SF content or quality parity.
The browser and native acceptance harness use the same pinned mGBA 0.10.5.
`python3 scripts/build_web_core.py` rebuilds the browser artifacts; source and
artifact fingerprints are in `web/public/emulator/core-build.json`.

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
