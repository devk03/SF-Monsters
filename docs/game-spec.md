# SF Mini Monsters — v1 specification

Status: implementation in progress; this file is the source of truth for scope and progress.
Updated: October 7, 2026.
Repository: https://github.com/devk03/SF-Monsters

## 1. Product

An original, open-source, adult comedy creature RPG set in a compressed San
Francisco. The single-player mechanics should feel familiar to a Pokemon player.
The world, creatures, art, music, dialogue, presentation, and implementation are original.

Required release scope:

- 16 accessible neighborhood hubs, each with a mini-adventure.
- Eight famous-startup gyms placed in verified San Francisco office districts.
  Each has a real-person leader, a product-inspired puzzle, and a distinct battle strategy.
- 150 collectible mini-monster catalog entries, including evolution stages.
- Three starter choices, a recurring rival, and real-person antagonist roles.
- Four championship opponents followed by a champion.
- One legendary mini monster and a dedicated recruitment quest.
- Marina bars and a playable drunk state for the protagonist.
- An optional Tenderloin adventure with a playable high state for the protagonist.
- Optional weird dates, recurring jokes, historical lore, and hidden Easter eggs.
- Real public tech figures and online personalities as the preferred named NPC cast.
- One original GBA ROM, playable in standard GBA emulators and a web player.
- Public source, editable content, documented builds, and open licensing.
- Support for adding approximately 50 researched Twitter personalities after
  the main game is complete, without redesigning the engine or campaign.

Working title: SF Mini Monsters. Title and other names remain provisional.
Main-story target: 8–12 hours; collecting everything and optional quests takes longer.
Reassess this duration after the playable slice rather than cutting requirements to fit it.

## 2. Core mechanics

- Choose one of three original starter monsters.
- Carry up to six monsters; store additional monsters at accessible terminals.
- Each monster equips up to four moves with finite use counts.
- Wild encounters support Fight, Item, Switch, and Run.
- NPC battles support Fight, Item, and Switch; retreat rules are defined separately.
- Weaken wild monsters and use an original capture device to recruit them.
- Capture chance depends on the monster, remaining health, conditions, and device.
- Earn experience, increase levels, learn moves, and evolve monsters.
- Use HP, Attack, Defense, Special Attack, Special Defense, and Speed.
- Support physical, special, and support moves; priority, accuracy, and critical hits.
- Support one or two elemental types, type effectiveness, and matching-type bonuses.
- Support passive abilities, one held item, temporary stat changes, and conditions.
- Initial conditions: poison, burn, paralysis, sleep, freeze, and confusion.
- Provide healing, revival, shops, currency, inventory, storage, and move relearning.
- Defeat trainers, rival encounters, eight gym leaders, four finalists, and a champion.
- Losing returns the player to a recovery point; never deletes monsters or progress.

Proposed initial type set: Tide, Ember, Bloom, Spark, Stone, Alloy, Fog, Gust,
Frost, Echo, Mind, and Shade. Finalize the chart before implementing battle content.
Gym concepts and elemental specialties are separate design decisions.

The battle system is deterministic for a fixed state and random seed.
Balance formulas live in a separate tuning specification and are implemented originally.
Gym teams progress in difficulty and demonstrate distinct strategies.
Ordinary encounters provide enough experience to progress without mandatory grinding.

## 3. Monster catalog

Working name: Mini Monster Field Guide.
Exactly 150 obtainable entries in the complete v1 game.
Each evolution stage is an entry; cosmetic variants are not extra entries.

Each entry contains:

- Stable ID, catalog number, name, and original front/back battle art.
- Type or types, base stats, growth curve, and passive ability options.
- Move progression, evolution rules, capture difficulty, and encounter sources.
- Habitat, rarity, description, and optional local lore or joke.
- Seen/caught tracking, discovered habitats, and evolution relationship display.

Creature inspiration includes wildlife, ocean life, fog, plants, infrastructure,
food, nightlife, and original urban oddities. Creatures should be appealing
characters rather than 150 literal objects with eyes.

Provide three starter evolution lines. Unchosen starters become obtainable later.
All 150 entries are attainable in one release without trading, limited-time events,
paid content, or restarting. Branching evolutions remain collectable through
additional encounters or repeatable sources.

Bayveil is the proposed legendary: a tiny floating fog manta with kelp-like
whiskers and lighthouse eyes. Show early hints, tie it to habitat restoration,
and provide a dedicated late-game quest. An unsuccessful encounter can be retried.

## 4. City map

Keep the ocean west, bay east, northwest parkland, and recognizable street/hill
relationships. Compress distances and block counts for playability.
Neighborhoods are town hubs; parks, beaches, tunnels, and stairways are routes/dungeons.
Campaign order is not a claim of literal neighborhood adjacency.

| Order | Hub | Mini-adventure | Gym leader and concept |
| --- | --- | --- | --- |
| 1 | Outer Sunset | Select a starter and rescue a surf courier lost in an Ocean Beach fog bank | — |
| 2 | Inner Sunset | Restore a greenhouse and investigate Golden Gate Park machinery | — |
| 3 | Haight-Ashbury | Follow conflicting concert flyers to a secret performance | — |
| 4 | Castro | Restore the lights for a neighborhood celebration | — |
| 5 | Mission | Recover mural pigments and follow a painted monster's clues | — |
| 6 | Dogpatch | Restore an industrial workshop with inventive monsters | — |
| 7 | SoMa | Investigate an escaped startup demo and the antagonist's first installation | Cognition (MVP); other SoMa gyms subject to sourced layout |
| 8 | Tenderloin | Find a missing musician, with an optional surreal high-state route | — |
| 9 | Fillmore | Recover a jazz ensemble's instruments before its show | — |
| 10 | Japantown | Recover festival supplies through lantern and gallery puzzles | — |
| 11 | Richmond District | Follow archival clues through Lands End to Sutro Baths | — |
| 12 | Presidio | Trace signals through woodland and Fort Point | — |
| 13 | Marina | Solve The Case of the Missing Quarter-Zip across Chestnut Street bars | — |
| 14 | Russian Hill | Restore cable-car machinery and navigate foggy stairways | — |
| 15 | North Beach | Decode a poet's notebook while following an unhelpful parrot | — |
| 16 | Chinatown | Restore a community festival and expose the final antagonist relay | — |

Gym identity is the startup; the leader is a real person associated with it.
The previous evenly spaced assignments in the table are milestone proposals,
not final geography. The latest instruction requires realistic startup locations,
so the every-other-neighborhood rule is superseded. Eight gyms may cluster.
Use [Silicon Valley Map](https://www.siliconvalleymap.org/) as a spatial reference,
then verify each current office district independently before implementing it.
Do not confuse mailing/registered addresses, historical offices, or planned leases
with occupied current offices. Record evidence and uncertainty in [startup gyms](startup-gyms.md).

For the MVP, Outer Sunset and SoMa are the two playable neighborhoods,
connected by an explicit Muni transit interaction. The first gym is Cognition
in the SoMa/South Park area. Remove the Foster City excursion and Replit gym.
Replit can appear as an online reference, but not as a falsely located SF office.
Replace its gym slot with an SF company such as Notion, subject to location verification.

Each gym has original pixel-art interiors, employee trainers, a product-inspired
puzzle, a leader battle, and a company-themed badge. Karpathy, Dylan Field,
Danielle Fong, Justine Moore, Naval, Garry Tan, and Jonathan Liu serve other
substantive cast roles. Sam is champion; Dario is an elite opponent.

Tenderloin replaces Bernal Heights in the earlier hub list; Bernal is expansion scope.

Golden Gate Park links Sunset, Haight, and Richmond. Presidio links Richmond
and Marina. Use walking routes and explicit transit for longer connections.
Unlock return routes and transit shortcuts as the player progresses.
The Ferry Building is a route destination; the championship island is a dungeon.
Neither adds a seventeenth neighborhood hub.

Each hub requires a main adventure, local encounters, a hidden discovery,
recurring NPC interactions, and at least one later revisit interaction.
Provide accessible healing and storage services throughout the campaign.

## 5. Story

The player is an adult local courier. Roon has dropped a damaged prototype
near Ocean Beach. Karpathy supplies a companion mini monster so the player can
recover it safely. Bringing it back reveals that it belongs to a citywide
monster-habitat system; delivery to Scott Wu's Cognition lab in SoMa provides
the next concrete destination.

MVP sequence: meet Karpathy, choose a starter, recover the prototype, return to
Roon, take Muni to SoMa, deliver it to Scott, repair the lab's safety relays,
and pass his gym challenge. Scott identifies evidence of an external overclock
signal. The first badge and a clear investigation lead conclude the MVP.
Optional exploration, capture, healing, and roster management fit around this route.

In the full campaign, the fictional Overclock Collective has repurposed the
habitat system to accelerate every monster's evolution simultaneously. Beff
leads its experimental faction; Marc's fictional funding apparatus supplies
its infrastructure. The system damages SF microclimates and awakens Bayveil.
Each neighborhood adventure exposes or repairs a different part of this system.
Gym leaders test the player's readiness and help recover access to its relays.

Roon is a recurring rival with his own investigation. His cryptic posts first
confuse the player, then reveal that he has pieces of the same mystery. Balaji's
fictional Treasure Island district is a side arc connected to competing ideas
about who should control the habitat network. Sam is the championship opponent,
not the same character as the central story villain.

Acts:

1. Hubs 1–4: learn the systems, meet the rival, and discover the first symptoms.
2. Hubs 5–8: expose the installations and confront the first major antagonist operation.
3. Hubs 9–12: discover historical/habitat connections and organize a counterplan.
4. Hubs 13–16: resolve the rival arc, earn the final badges, and stop the main scheme.
5. Championship and postgame: finish the league, pursue Bayveil, and revisit the city.

The ClearSky/Arden/Patch pitch and anonymous Bay Council cast are superseded.
Real names/public personas inspire the cast; dialogue and fantastical actions are fictional.

## 6. Championship and postgame

Eight badges unlock a ferry to a championship venue on Treasure Island within San Francisco.
Fight four consecutive specialists, with a defined recovery/item policy, then a champion.

| Opponent | Proposed battle identity |
| --- | --- |
| Ilya Sutskever | Small, difficult predictive team |
| Dario Amodei | Shields, safeguards, and counterplay |
| Eliezer Yudkowsky | Containment, traps, and constrained choices |
| Sarah Guo | Team coherence and combinations |
| Sam Altman, champion | Visible compute resource and strength that scales during battle |

Unique boss mechanics must remain readable and beatable with ordinary obtainable teams.
Postgame includes Bayveil's quest, rematches, outstanding dates/side quests,
rare monster collection, hidden jokes, and the Treasure Island network-state district challenge.

## 7. Marina, intoxication, and dates

Marina bars: The Quarter Zip, Liquidity Lounge, and The Last Round are fictional venues.
The player can order drinks, become drunk, and continue playing the game.
The quarter-zip mystery includes mistaken identities, competitive trivia,
a product-market-fit bouncer, and a monster nesting in a karaoke speaker.

Tenderloin includes an optional high-character sequence with altered descriptions,
perceived objects, unusual conversations, and an alternate mystery route.
The neighborhood also contains ordinary community life, businesses, music, and residents.

Character state supports sober, drunk, high, and combined states if both effects overlap.
Both intoxication effects have explicit duration/recovery rules using in-game time.
Save their state. Rest or choosing a recovery interaction returns the character to sober.
Main-story progress remains possible sober; intoxication can reveal optional content.

Keep movement, battle decisions, menu labels, and saving usable.
Visual wobble/color effects are optional and reducible independently of story state.
Do not implement involuntary menu choices, irreversible item loss, or progression softlocks.
The player's state does not imply anything about real cast members' actual substance use.

Dates are optional branching adventures with adult characters, choices to leave,
awkward conversations, callbacks, and cosmetic/item/quest rewards.
Proposed scenarios: a pitch-deck date, a wearable-obsessed date, a relationship org
chart, confident wrong directions, and a monster revealing embarrassing information.
Final casting and dialogue are researched separately; these are invented scenarios.
Jonathan's public dating/scheduling projects can inspire a date-assistance quest.
No date outcome blocks gym progression or obtaining the full monster catalog.

## 8. Comedy, lore, and real-person cast

Aim for real public SF/Bay tech figures and recognizable online personalities
for every named interactable human NPC. Use recurring characters across hubs
rather than inventing filler identities to reach a quota.
Build the main game using the core cast; the initial cast shortlist and startup-leader additions are in
[cast research](cast-research.md). Specific role assignments remain proposed.

Recurring candidates include Aella, Nikita Bier, Mike Solana, Dwarkesh Patel,
Visakan, and Patrick McKenzie. Cast visitors as visitors where appropriate.
Use public pseudonyms without deanonymizing people.

Support ambient conversations, signs, inspectable objects, hidden rooms,
a fictional offline social feed, state-dependent dialogue, and cross-city callbacks.
Write original jokes based on public themes rather than copying tweets or article dialogue.
Do not invent biographical allegations; fantastical game roles are distinct from real conduct.

The Overheard SF article inspires conversational comedy; the supplied Noahpinion
excerpt inspires contrasting tech eras and subcultures. The excerpt is incomplete,
so do not treat the later era headings as researched full accounts.

Historical hooks: Golden Gate Park's sand dunes, Sutro Baths' tidal engineering,
the 1915 exposition, and cable-car invention/preservation. Research factual
historical dialogue and distinguish it from the fictional adventure.
Sources are linked in the reference section.

## 9. Adding approximately 50 Twitter personalities later

The main game must be complete without this extra cast. Build expansion
support now, then research and add the user-selected names after completion.

Each added character needs a research record containing:

- Stable character ID, canonical public name/handle, and verified identity source.
- Public SF/Bay connection, visitor status, or explicit fictional placement.
- At least three supporting public posts, essays, or interviews where available.
- Public persona themes, running jokes, and source dates/links.
- Proposed location, role, original dialogue, quest/battle content, and callbacks.
- Portrait/asset provenance and implementation/release status.
- Clear uncertainty notes when a claimed identity or meme cannot be verified.

Never invent evidence to satisfy the source count. Keep unresolved entries in the backlog.
The cast data references the research record, but citations stay in contributor docs,
not in ordinary game dialogue.

Separate character identity from service roles, dialogue, teams, and map spawn slots.
A future character can become a shopkeeper, quest giver, rival, or optional boss
through content data rather than bespoke engine code.

Use persistent stable IDs for characters, monsters, items, maps, and quests.
Append new identifiers; do not reuse removed identifiers or store array positions as identity.
Version the save format, initialize new quest state predictably, and preserve existing progress.
Reserve map spawn opportunities and a tested content budget for the extra 50 characters.
Adding them must not require replaying the campaign or increasing the 150-monster target.

GBA expansions ship as rebuilt ROMs with compatible saves. The browser uses
matching versioned ROM/player releases. Do not promise live downloadable scripts
inside the GBA game. Existing saves must have an explicit upgrade/import path.

## 10. Art, audio, and interface

Use original tile-based pixel art and a GBA-readable interface.
Required assets: city tilesets, interiors, character sprites/portraits, monster
front/back sprites, battle effects, icons, UI, music, and sound effects.
Keep art direction consistent across neighborhoods and future cast additions.

Menus: team, inventory, field guide, city map, quest journal, save, and settings.
Offer readable text, adjustable text speed, clear battle cues, and reduced visual effects.
Support D-pad plus GBA buttons, with corresponding touch, keyboard, and gamepad mapping.
An original city map and simple quest journal help players track return visits.

## 11. Technical architecture and saves

Implemented MVP architecture: freestanding C compiled with GCC for ARM into one
original GBA ROM. The website runs the same cartridge using mGBA WebAssembly.
Native mGBA boot and WebAssembly execution have been demonstrated.

Keep maps, dialogue, quests, monsters, encounters, moves, and teams in editable
source data compiled into ROM assets/tables. Validate IDs, references, resource
limits, and unobtainable content as part of the build.

Stay within GBA display, palette, sprite, memory, and cartridge constraints.
Stream/load map sections as needed; avoid assuming browser resources exist on the GBA.
Reserve performance and ROM space for later cast expansion based on measured builds.

Use in-game time for schedules and effect duration so behavior matches across players.
Store team, storage, inventory, currency, badges, catalog progress, location,
quest flags, character states, and persistent encounter data.

Provide versioned saves with integrity checks and a recoverable previous save.
Verify actual emulator battery-save formats before promising transfer compatibility.
Unsupported/newer save versions must produce a clear error instead of corrupting progress.
Browser saves persist locally and support explicit backup/export/import.
Keep manual saving available; browser storage is not treated as a permanent backup.

All playable locations must be inside San Francisco city limits, including championship
and side-antagonist zones. No Peninsula, Foster City, Oakland, or other-city excursions.

No backend or database is required for v1. No cloud account is required to play.

## 12. Open source and distribution

Public repository: https://github.com/devk03/SF-Monsters
Original code/documentation: MIT, as adopted in the repository.
Original generated raster art: CC BY 4.0 to the extent licensable; asset notices
record source and licensing.
Dependencies and separately licensed material keep their own notices/licenses.

Include editable source assets, content formats, contributor guide, and build instructions.
Builds must not require commercial ROMs, copied proprietary assets, or proprietary BIOS files.
Keep branding and presentation original and review the release identity.

Website requirements: Play, Download GBA, Fork source, controls, save backup/import,
release version, and credits. Serve the ROM and WebAssembly player as static assets.
Choose the hosting provider during release preparation; verify its emulator requirements.
Publish versioned downloadable ROMs and matching browser builds.

## 13. Delivery and acceptance

1. Design baseline: finalize core battle rules/type chart, map links, cast roles,
   monster roster structure, content formats, and the first quest scripts.
2. Platform slice: Outer Sunset/SoMa, three starter choices, about 12 monsters,
   one gym, exploration, capture, battles, healing/storage, and saves.
3. Comedy slice: one playable Marina drunk sequence, one Tenderloin high sequence,
   one weird date, and conditional dialogue/Easter eggs.
4. Complete campaign: all 16 hubs, eight gyms, 150 entries, antagonist/rival arcs,
   legendary quest, championship, and postgame.
5. Release preparation: balance, compatibility, asset/source licensing, builds,
   contributor docs, and deployment.
6. After the main game: research and add approximately 50 user-selected Twitter heads.

Required verification:

- Finish the platform slice on the same ROM in mGBA and the browser WebAssembly player.
- Complete the campaign and all eight gyms without a progression softlock.
- Verify all 150 catalog entries are obtainable in one playthrough/release.
- Validate battle resolution, capture, evolution, and important quest branches.
- Save, close, reopen, and resume on both platforms; verify backup/import round trips.
- Test intoxication recovery, date exits, and readable reduced-effects mode.
- Load an older save after adding cast/quests and verify prior progress survives.
- Demonstrate a sample character addition through content data without engine changes.
- Reproduce the ROM and web build from documented prerequisites in a clean checkout.

Commit frequently at coherent checkpoints and verify relevant changes.
Database migrations and PR merges require the user's permission.

Outside v1: online multiplayer, trading, breeding, cloud accounts, live social
feeds, native platform-specific apps, and neighborhoods beyond the 16 listed hubs.

The release is complete when the full campaign and catalog are playable on both
targets, optional comedy systems work, and a contributor can fork and build it.
The extra 50-person expansion is a subsequent milestone, not a release blocker.

## 14. Active MVP objective and progress

Always read this specification before planning or implementing the next task.
Resolve scope conflicts in favor of the latest user instruction and update this file.
Record completed work, verification evidence, blockers, and the next checkpoint here.
Do not mark a milestone complete until its acceptance criteria have been verified.

### Objective

Deliver a publicly accessible, testable MVP with two neighborhoods, 12 original
collectible mini monsters, one Cognition startup gym in SoMa, exploration and dialogue,
turn-based battles, capture, team/storage management, and persistent saving.
Build an actual GBA ROM with the feel of a classic ROM-hack adventure and run
the same ROM on the website through WebAssembly. Original-ROM implementation is
the default while the user clarifies whether a specific existing base ROM is intended.
Verify the ROM in a standard GBA emulator, using mGBA as the reference target.
The website supports real sign-in and device-local saves with backup/import.
Commit coherent checkpoints around 500–700 changed lines when it makes sense.
The full 150-entry game and later 50-person cast expansion remain subsequent scope.

### Acceptance checklist

- [x] Two neighborhoods and a complete courier quest are implemented; quest gates and required locations pass checks.
- [x] Three starter choices and recruitment of all 12 entries pass core checks.
- [x] Capture, battles, healing, team switching, storage, and defeat recovery pass core checks.
- [x] The Cognition gym can be challenged and defeated (core checks and browser battle through the Build Badge).
- [x] Native/browser format and actual WebAssembly SRAM restore/resume/export pass automated checks.
- [x] A completed native mGBA battery save imports into browser play, preserving
  the Build Badge and level-8 Brinepup.
- [ ] Downloaded browser backup is tested in a regular external browser (in-app
  download event automation times out).
- [x] The actual GBA ROM boots and accepts input in native mGBA.
- [x] The browser boots the same ROM through WebAssembly; starter selection and keyboard input verified.
- [x] Desktop keyboard and on-screen controls, small-screen layout, and browser gym completion are verified.
- [x] Public deployment succeeds; real ChatGPT sign-in integration and protected-route redirects are implemented.
- [ ] A complete production sign-in session is verified.
- [x] Core, map reachability, browser save, WebAssembly execution, TypeScript, and production build checks pass; docs/testing.md provides instructions.

### Current progress

Completed preparation:

- Public GitHub repository and consolidated specification committed.
- Startup gym identities and real-person casting research recorded.
- Public website deployed: https://sf-mini-monsters.devkunjadia03.chatgpt.site
  (Sites version 3, deployment succeeded 2026-10-07).
- Web framework starter and dependencies installed locally.
- GBA compiler installed locally.
- Two original raster sprite atlases integrated; palette and sprite conversion is reproducible.

Implemented and verified:

- Browser interface, emulator execution, controls, and native cartridge behavior.
- Original GBA ROM built successfully (67,820 bytes), with indexed pixel art,
  scrolling maps, menus, battles, and dual-bank cartridge saves.
- Browser battery saves validate native records, wait for actual SRAM allocation,
  verify imported bytes, and support local persistence and portable export.
- Core logic implemented: starter choice, encounters, capture, team/storage,
  courier quest, relay gates, and the three-monster Cognition gym battle.
- Browser player uses a single-threaded mGBA WebAssembly core with same-origin
  assets and no cross-origin isolation requirement.
- All-SF geography supersedes the Foster City excursion. The first gym is
  Cognition in SoMa; Outer Sunset connects to it through Muni.
- The courier/prototype quest now provides a coherent MVP story and completion point.

Next checkpoint:

- Compile and boot the ROM, then integrate the same ROM into the web player.

Verification evidence:

- Specification checked for exactly 16 hubs and eight alternating gym stops.
- Native C checks pass with AddressSanitizer and UndefinedBehaviorSanitizer:
  all three starters, save round trip/corruption rejection, quest order, all 12
  catalog entries, storage swaps, gym completion, and recovery after defeat.
- Native mGBA 0.10.5 boots the cartridge and advances the opening dialogue.
- Browser mGBA boots the same ROM; keyboard advances the opening and starter
  selection, and the website reports the first caught entry.
- Native-generated .sav fixture passes browser decoding, checksum rejection,
  dual-bank ordering, and backup encoding tests.
- Full browser quest, responsive controls, sign-in, and deployment remain to verify.

Blockers requiring user input: none currently.
Database migrations and PR merges still require explicit permission.

## References

- [Cast sources and limitations](cast-research.md)
- [Overheard SF article](https://www.sfgate.com/sf-culture/article/The-story-behind-Overheard-SF-Instagram-16768301.php)
- User-supplied excerpt: Noah Smith, Four eras of San Francisco tech culture,
  September 25, 2026. The attachment is not redistributed in this repository.
- [Golden Gate Park history](https://recpark.sf.gov/1119/History-of-Golden-Gate-Park)
- [Sutro Baths history](https://www.nps.gov/goga/learn/historyculture/sutro-baths.htm)
- [1915 exposition](https://www.nps.gov/prsf/learn/historyculture/1915-panama-pacific-international-exposition.htm)
- [Cable-car history](https://www.sfmta.com/getting-around/muni/cable-cars/cable-car-history)
- [Butano](https://github.com/GValiente/butano)
- [Delta ROM importing](https://faq.deltaemulator.com/getting-started/importing-games)
- [mGBA](https://github.com/mgba-emu/mgba)
- [Candidate WebAssembly wrapper](https://github.com/wasm-gaming/mGBA-wasm)

Latest verification checkpoint (2026-10-07):

- `make rom check` passes on the compiled 67,820-byte cartridge.
- Actual WebAssembly execution resumes a native save, accepts movement, preserves
  currency and quest flags, and writes the next valid cartridge save bank.
- Raster rendering optimized to keep short controller taps responsive.
- Browser play visibly resumes in Cognition Lab and starts Scott Wu's gym battle.
- No database is used or migrated. Source and assets remain publicly forkable.
- Browser gym battle completed manually, awarding the Build Badge and updating the
  website quest panel. Progress survives reload.
- Responsive checks at requested 320/375/414/768/1100 viewport settings show no
  horizontal overflow. Small-screen on-screen confirm works.
- Native mGBA loads a portable 32 KiB fixture and displays Continue Delivery.
- Download event capture times out in the in-app test browser. A persistent
  Download save link is provided; byte-level WebAssembly export/import passes.
- Native controller-script playthrough and native-to-browser save transfer now
  pass (see final acceptance below). Production account sign-in and external
  browser download behavior remain hands-on QA items.

Release checkpoint:

- Public Site version 2 is deployed with the final save-download fallback and
  battle-command selection fix.
- Clean Ubuntu build and all checks pass in GitHub Actions:
  https://github.com/devk03/SF-Monsters/actions/runs/37596174090
- GCC versions produce different ROM sizes (macOS GCC 16: 67,820 bytes;
  Ubuntu toolchain: 67,372 bytes). Both execute the cartridge checks successfully.
- The earlier clean-checkout failure was fixed by tracking required web/build
  helpers while ignoring only the root cartridge build output.

Final native acceptance (2026-10-07):

- A fresh cartridge completes starter selection, parcel recovery, Roon's delivery
  instructions, Muni, both neighborhoods, Scott's diagnosis, both safety relays,
  healing/resupply, and the gym through native mGBA controller scripting.
- The test writes controller keys only. It reads state for navigation and never
  writes stats, levels, quest flags, or other game memory. It exercises recovery,
  ordinary training battles, the free clinic, and the capsule/potion shop.
- Native result: flags 127, 460 coins, level-8 Brinepup, Build Badge earned.
- Importing that actual 32 KiB native save into the browser succeeds. The browser
  Team/Storage screen displays Brinepup level 8 with 52 HP, preserving the badge.
- `make native-qa` prepares isolated ROM/script files for repeatable acceptance.
- MVP implementation is delivered for user testing. Full campaign milestones in
  section 13 remain future work; production account login and normal-browser
  backup download should be included in the user's first testing pass.

Final handoff:

- Public Site version 3 deployed successfully at the same Play URL.
- Final code checkpoint: 8d8c171. Its clean build/check workflow passes:
  https://github.com/devk03/SF-Monsters/actions/runs/37598110919
- Native and browser screenshots are saved locally under .tools/qa for review.
- All playable game maps and future story destinations stay inside SF city limits.
- MVP delivery is complete; user acceptance testing can now begin.
