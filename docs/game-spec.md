# SF Mini Monsters — v1 specification

Status: technical prototype shipped; Emerald quality parity is NOT achieved.
Section 15 is the active goal and overrides the earlier prototype completion criteria.
This file is the source of truth for scope, acceptance, and progress.
Updated: October 14, 2026.
Repository: https://github.com/devk03/SF-Monsters

## 1. Product

An adult comedy creature RPG set in a compressed San Francisco, built as an
Emerald ROM hack. Our SF content and tools are open source; inherited commercial
engine/assets retain their rights. Section 15 defines the approved architecture.

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
- One locally patched GBA ROM, playable in standard GBA emulators and a web player.
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
Emerald's Gen III rules are the engine baseline; SF tuning lives in editable data.
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

Main architecture: pinned pret/pokeemerald plus our editable SF overlay, compiled
locally and released as a BPS patch. The website patches a player-supplied ROM
locally and runs that cartridge using mGBA WebAssembly. The earlier freestanding
C implementation is archived at `/prototype`.

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
Players supply the validated base ROM locally. Full commercial and reconstructed
cartridges stay out of Git and public hosting. Publish our original changes and
patches; keep SF branding distinct and record inherited material separately.

Website requirements: local ROM upload/patch/play, local patched-GBA download,
Fork source, controls, save backup/import, release version, and credits.
Serve versioned patches and the WebAssembly player through Sites hosting.

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

## 14. Previous technical prototype and progress (superseded)

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
Current workflow: commit coherent changes every 200–300 handwritten code lines.
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

- See section 15. The earlier compile/boot/deploy checkpoint is complete, but
  it did not establish Emerald quality parity.

Verification evidence:

- Specification defines 16 hubs and eight startup gyms. Real office geography
  supersedes alternating gym placement.
- Native C checks pass with AddressSanitizer and UndefinedBehaviorSanitizer:
  all three starters, save round trip/corruption rejection, quest order, all 12
  catalog entries, storage swaps, gym completion, and recovery after defeat.
- Native mGBA 0.10.5 boots the cartridge and advances the opening dialogue.
- Browser mGBA boots the same ROM; keyboard advances the opening and starter
  selection, and the website reports the first caught entry.
- Native-generated .sav fixture passes browser decoding, checksum rejection,
  dual-bank ordering, and backup encoding tests.
- Later checkpoints below record browser, native, and deployment verification.
  Production account sign-in and normal-browser downloads remain manual QA items.

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

## 15. Active Emerald parity goal

This section supersedes the technical-prototype acceptance bar in section 14.
The user requires Emerald-tier quality in every audited area, within the existing
SF game scope. The user approves matched comparison clips at each review gate.
Commit coherent changes every 200–300 handwritten code lines when practical;
smaller completed fixes are valid checkpoints. Generated output is counted separately.
Do not pad code, churn formatting, or leave a broken intermediate build to meet
the line quota. Scope, tests, screenshots/clips and progress updates travel with
the coherent checkpoint they substantiate.

Current checkpoint — October 15, 2026, 04:00 UTC:

- Goal active; stop October 15 at 18:00 Pacific. Public v75 / Site 66 is live.
  Native release source f85c8906; website source ab096cf5. Human approvals 0/11.
- Fixed stale Make caches that had retained inherited creature graphics. Final
  ROM independently matches all 108 authored visual/palette resources, 90 table
  bindings, 18 icon selectors, three shared palettes and 18 original cry controls.
  The compiled checker now blocks BPS creation on a mismatch. Pixel quality and
  animation acceptance remain pending; integration alone does not satisfy parity.
- Actual native cold Continue, party icons and gym battle, plus Chrome battle /
  party controls, show the authored assets. Matched v57/v58/v59 native controller
  routes produce byte-identical ordinary Flash saves at counter 4.
- 711 independently specified mechanics cases / 57 doubles pass at the v56
  baseline; five controlled turn profiles now pass separately (four full living,
  one partial KO boundary); broad full-turn/type/catalog gates remain open. Ten save round trips cover
  one first-badge checkpoint, not 50 distinct campaign checkpoints.
- Earlier scoped browser smokes passed, but the first active-walking600second
  Chrome v75 run FAILS:16discarded frames,13738audio underrun outputframes and
 334input observations vs310planned. Complete route/foreground/report integrity
  do not override that failure. The instrumented repeat also fails
  (9discarded frames/8330underruns), with exactly310planned inputs and no
  unexpected DOM events. No fix or performance acceptance claimed. Physical response, native deadlines,
  Safari/phone, other workload classes and listening remain open.
- Full 16-neighborhood / eight-gym / 150-monster campaign remains unfinished.
  First-slice approval is required before campaign expansion.
- TrolleyKit is grounded: one ROM byte changes from v58; other 411 elevation
  entries remain identical. Fresh native and Chrome battle views pass this fix.
- South Park discovery bench has a continuous sidewalk landing; five tile IDs
  change, with every other ROM byte unchanged. Actual native/browser interaction
  passes; human art review remains pending. Safari smoke was rejected as hidden.
- Original Naval intro figure is integrated and visible in native/browser play.
  Matched new-game/name flow and existing-save Continue preserve full save blocks.
  Only796 bytes inside the intro graphics/palette allocations change from v60.
- Original Naval field sprite now survives older-save Continue, ordinary Save and
  reload. Native comparisons preserve all gameplay state; actual Chrome older-save
  Continue shows the new figure without leaving the map. Human art approval pending.
- Native JOURNAL now shows current chapter objective from existing state and
  location, preserves Save row, returns cleanly to menu/field, and survives ordinary
  C7 save/reload. Human interface acceptance and the complete SF map remain open.
- South Park now has an enterable seed room in the denser western frontage.
  Native/browser notes and return, indoor Save/coldContinue and map parent pass.
  No new reward/quest flag; centered native door animation passes technical
  entry/exit and old-save checks. Human art review remains open.
- Guide AREA now uses a geographic SF map and original courier marker. Actual
  two/one/no-wild-habitat scenarios and five player-parent contexts pass native
  checks; Chrome displays it and returns to the Guide. Art approval remains open.
- JOURNAL SELECT now opens SF MAP before starter/Guide unlock; A/B returns to
  the native menu. Browser controls and no-starter native access are verified.
- Original Garry field art survives old-save Continue, native Save and cold reload.
  Prior eight custom cast sprites remain byte-exact; human art approval pending.
- Original Jonathan now appears at both Muni stops with existing map palettes.
  Both old-save Continue/resave/reload paths, native two-way journey and actual
  browser route/manual outbound trip pass; art/likeness approval stays pending.
- Original Dylan field art now walks/talks in native and browser play; all nine
  prior cast sprites and shared palettes remain exact. Human review is pending.
- Lower-west South Park frontage has an adjacent butter house. All12 newly
  blocked old-save positions safely reload/resave; native front/side/roof pushes
  remain outside buildings, and browser route passes scoped checks.
- All three Cognition trainers have original portrait candidates. Compiled26
  checks, actual native/browser entrances and two ordinary loss/save/coldContinue
  branches pass their technical scopes. Human paired art reviews remain pending.
- Current alignment exchange03:58UTC,next04:28UTC. Root owns performance
  diagnostics, builds/publication and canonical spec; peer owns only source text
  for three existing Sunset starter prompts. No builds/captures during the
  running measurement. Existing map/save/turn evidence remains scoped below.

### 15.1 Objective and completion rule

Current user-requested stop: **October 15, 2026, 6 PM America/Los_Angeles**
(October 16, 01:00 UTC). Keep working through intermediate commits, fixes, reviews
and deployments until that mark; do not treat a completed subtask as the end of
the full goal. At the deadline stop new implementation/build/deployment work,
record honest remaining gates, make the final coherent commit/push, and pause.
A fixed-date one-time stop reminder is active; no indefinite monitor is authorized.

Alignment requirement (explicitly requested October 14): check in with the
**🧱 SFM Audit Monsters Alignment** chat (ID
01a13900-5c2c-7973-bea7-389deda8a5ab) at least every **30 minutes of elapsed
active work**. Read its latest result/status, exchange current priorities and
acceptance evidence, resolve disagreements against this spec, and record the
last/next check-in below. Work with that chat on implementation, reviews,
reference capture or testing as useful. Coordinate file ownership and engine
builds before parallel mutations. Each dispatched task/monitor remains finite
and under two hours; no recurring GitHub Actions. These check-ins support the
full acceptance goal and must not become a substitute for implementation.

Architecture revision approved by the user on October 7, 2026: use an Emerald
ROM hack. The user explicitly accepts a public website that asks players to load
their own Emerald ROM and applies the SF patch locally. This supersedes the
standalone-homebrew/instant-play distribution approach for the main build.

Deliver the complete SF Mini Monsters campaign on an Emerald-based GBA ROM and
the public WebAssembly website, with Emerald-tier audio, sprites, movement, maps,
battles, monster depth, NPC events, interface, story, and balance. Every playable
location remains inside San Francisco city limits. Keep source publicly forkable.

Preserve Emerald's actual movement, camera, sprites/animation infrastructure,
menus, battle engine, scripting and sound engine as the baseline. On opening the
game, the player should immediately recognize the Gen III creature-RPG format.
New SF art must match its native pixel scale, palette discipline, perspective,
proportions and animation conventions. The former standalone renderer is an
archived experiment, not the main path to parity.

Publish our SF changes, asset sources, build tools and a versioned patch. Keep
commercial ROMs and reconstructed full Emerald-derived ROMs out of Git and
public hosting. The browser validates and patches the player's local base ROM
without uploading it; players may download their resulting cartridge for mGBA.
The project's open-source license covers our original contributions, not the
inherited commercial engine/assets. Patch distribution does not relicense them.

Completion requires ALL of these, independently:

1. All 11 quality domains below receive a user-approved final score of 4/4.
2. The entire existing SF release scope is implemented and validated.
3. All mechanics, performance, save, campaign, and release gates pass.
4. The user approves the final comparison-clip suite and complete playable build.

A passing build, an attractive title screen, or a polished first gym cannot
substitute for those conditions. Partial slice approval never means the full
campaign or all 150 monsters have achieved parity.

Parity means equivalent craft, responsiveness, depth, and polish for the agreed
SF experience, now built on Emerald's engine. Hoenn locations and the stock
campaign are development scaffolding and must be replaced before SF content is
counted complete. Our 150 Mini Monsters, SF cast, neighborhood story and distinct
branding remain required. The user chose quality within the existing SF scope: breeding,
contests, link trading, multiplayer, and a copy of every Battle Frontier facility
are not added to this goal. The later approximately 50-person cast expansion
remains subsequent scope. The existing legendary/rematch/side-quest postgame stays.

### 15.2 Fixed reference and comparison method

Reference supplied by the user: Pokemon - Emerald Version (USA, Europe).gba.
ROM header: POKEMON EMER; game code BPEE; size 16,777,216 bytes.
SHA-256: a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af.
The archive/header/hash have been inspected. Native benchmark captures and paired
clips are recorded below; the complete comparison suite remains unfinished.

Use this ROM locally as the reference, with mGBA 0.10.5 at normal emulation speed.
Keep commercial ROM data and reference assets out of the repository and deployment.
Ship original assets and code or dependencies with appropriate redistribution rights.
The approved reference ROM is now also the validated patch input. Contributors
and players supply it locally; public builds/releases contain our patch and tools.

Compare matching situations, not identical geographic layouts: town walking,
route exploration, interior entry, dialogue, wild battle, trainer/gym battle,
attack/status feedback, capture, evolution, party/storage, and story events.
Use 30–60-second paired clips at 240x160 with equal nearest-neighbor display scale,
normal gameplay speed, and sound. Also inspect still sprites at native pixel size.
Audio comparisons use matched listening levels and at least three consecutive loops.
Label each clip with build commit, reference identity, emulator/runtime, and scenario.

Each review records the user's score, specific remaining gaps, and clip evidence
in this specification. Unreviewed work is marked unreviewed, never inferred as 4/4.
Frame measurements and functional checks support the review; they do not replace
human judgment of melody, pixel art, animation, map composition, or writing.

### 15.3 Quality scale and scorecard

Score each domain against the matched Emerald reference:

- 0: absent, or the required experience cannot be exercised.
- 1: prototype; major visual, audio, interaction, or mechanical gaps.
- 2: functional and recognizable, with obvious deficiencies against the reference.
- 3: polished, but specific reference-level gaps still remain.
- 4: user approves Emerald-tier quality in the agreed scope; all domain gates pass.

An average is not an acceptance criterion. A 4 in art cannot compensate for a 1
in audio. Report the 11 scores individually and the number at approved parity.
Within a checkpoint, improve the lowest-scoring domain first; then resolve its
remaining failed checks. Keep previously approved checks passing. Record regressions.

| Domain | Mandatory evidence for final 4/4 |
| --- | --- |
| World design | All 16 hubs have a distinctive landmark, main adventure, optional discovery, enterable spaces, and return interaction. Routes/shortcuts form the approved SF map. User approves traversal and exploration clips from all 16 hubs; larger empty maps do not count as progress. |
| Movement/camera | Four-direction idle/walk/run animation with alternating footsteps; continuous tile interpolation and camera scrolling; coherent collisions, turns, doors, running and planned traversal modes. Movement timing matches the selected Emerald reference mode within one emulated frame. No snapping between tiles during ordinary movement. |
| Pixel art | All 150 monsters have separately authored readable front/back sprites, party icons, and entrance animation. All shipped tilesets, named cast sprites, leader portraits, and UI share an approved pixel-art direction. Each human locomotion set includes all four directions and stepping frames. Native-size and in-game reviews pass; resized generated art alone is insufficient. |
| Battle presentation | Wild/trainer/gym/double battles include transitions, deployment, animated HP/experience, move effects, status feedback, capture throw/shakes/outcomes, fainting, switching, victory, evolution and move-learning sequences. Every shipped move has appropriate animated feedback and sound; static text-only attacks fail. |
| Battle mechanics | Complete six-stat calculation, speed/priority order, accuracy/evasion, criticals, STAB, dual types, physical/special rules, stat stages, statuses, abilities, held items, weather, switching, items, capture, and doubles. All reference fixtures and approved SF chart tests pass; trainer decisions demonstrate their advertised strategies. |
| Monster depth | 150 obtainable entries, three complete starter evolution lines, species-specific learnsets, move learning/relearning, growth curves, individual stat variation, abilities, habitats and evolution rules. Every final form has an identifiable battle role and multiple viable move choices; one global four-move set fails. |
| NPCs/events | Interaction respects position and facing; roaming NPCs, trainer sight lines, scripted movement, story triggers, and state-dependent dialogue work. Each hub contains both ambient activity and consequential events. No invisible large-region interaction substitutes for approaching a person/object. |
| Interface | Party/summary/moves, organized storage, inventory/held items, field guide, city map, journal, save and settings are complete. Adjustable text pacing, cursor navigation, help, confirmations and battle messages are readable and consistent on GBA and web. All core menu workflows pass without clipping or ambiguous input. |
| Audio | Every declared music context has an original developed looping composition/arrangement: all 16 hub identities, wild/trainer/gym/rival/villain/championship/legendary encounters, evolution, victory, title and credits. All 150 creatures have identifiable cries; UI, moves and field interactions have appropriate effects. User approves composition/arrangement, instrumentation, mix and transitions. Beeps or track count alone do not establish parity. |
| Story/SF identity | Sixteen coherent neighborhood adventures, recurring rival and villains, eight credible startup gyms, championship and legendary arcs, researched lore, Marina bars/drunk play, Tenderloin high-state play, dates and discoverable jokes. User approves scene pacing, cast writing and SF recognizability; labels on generic maps fail. |
| Campaign/balance | All eight gyms, Elite Four, champion, legendary and scoped postgame are playable. Three fresh runs with different starters complete without cheats or progression softlocks. Each gym has at least three obtainable team/strategy solutions that do not require repetitive mandatory grinding. User approves progression and encounter pacing. |

### 15.4 Functional and measurable gates

Mechanics:

- Establish Gen III battle behavior as the baseline, including its type-based
  physical/special distinction. Finalize the original SF type chart and mapping.
- Include nature/IV/EV-style stat variation with explicit rules and growth data.
- At least 300 independently derived reference cases pass 100%, including at
  least 50 doubles cases. Every required mechanic has basic, boundary, and
  interaction cases; repeating a simple attack hundreds of times does not qualify.
- Where state, mapped rules and random draws are equivalent, turn order, damage,
  accuracy, statuses, resource consumption and resulting state match the reference.
  Document intentional content differences before evaluating them.
- Validate every ordered pair in the approved type chart, every evolution rule,
  every move/ability/item reference, and all 150 encounter/acquisition paths.
- The initial four universal moves are replaced with species-specific progression
  and a move catalog covering damage, status, recovery, control, weather and
  multi-target strategies. Final catalog approval requires breadth and usefulness,
  not a minimum number of renamed duplicates.

Performance and input:

- Run at the GBA's native emulation speed. Baseline measurements are collected
  before choosing a renderer, animation scheduler or sound architecture.
- At least 99% of required game update/render deadlines are met in each of three
  10-minute traces: field traversal, mixed battles, and menus/story events.
  Count game updates, not merely an emulator's displayed frame-rate counter.
- Unblocked controller input is consumed within two game frames. Walking/running
  tile duration differs from the matched reference by no more than one frame.
- Web input-to-visible-response p95 is at most 100 ms on the declared devices.
- Record OS, browser, device, emulator/core version and test route before measuring.
  Reference matrix: native mGBA on the development Mac; web Chromium and Safari
  on that Mac; one physical mobile browser/device selected for the release.
- No audio-buffer underruns or unintended loop/transition clicks in those traces.
- Test 320/375/414/768/1440 CSS widths and both phone orientations with no horizontal
  overflow or blocked controls. Viewport simulation does not prove phone performance.

Saves, progression, and release:

- Ten consecutive native-to-web-to-native battery-save round trips preserve all
  monsters, moves, items, money, badges, quest flags, locations and settings.
- Resume from at least 50 distinct campaign save checkpoints, including before
  and after gyms, branching comedy events, legendary encounters and championship.
- Corrupt/truncated/unsupported saves are rejected safely. A documented upgrade
  path preserves supported older SF saves; migration evidence is required.
- Zero unresolved crashes, data-loss bugs, progression softlocks, or broken
  required content references. The entire 150-entry catalog is obtainable in
  one release without trading, restarting or event-only downloads.
- Main-story target stays 8–12 hours for a first-time player. Validate pacing
  through normal play, not emulator turbo or artificial travel/dialogue padding.
- Both the same ROM in native mGBA and the web player complete the campaign.
  Public guest play, real sign-in, independent local save slots and actual
  downloadable/importable backups pass hands-on release checks.
- Clean GitHub builds pass; versioned patch, website, editable SF assets and
  contributor instructions reproduce from a clean checkout plus the documented
  local base-ROM requirement. The patched cartridge runs identically in native
  mGBA and the browser. A sample additional cast member
  can be added through data without engine changes, preserving an older save.

### 15.5 Hill-climbing checkpoints

A. Reference and Emerald foundation: verify a pinned Emerald build against the
   supplied ROM, collect the benchmark set and preserve inherited engine behavior.
   Produce a small SF content patch, verify exact patch application locally, and
   run the same patched cartridge in mGBA and the browser. Establish the native
   art/audio conventions, battle coverage and SF type mapping before expansion.

B. First polished slice: Outer Sunset/Ocean Beach, the Muni connection, a detailed
   South Park block, and Cognition's gym. Include 12 fully presented monsters,
   three starters, species-specific moves, NPC events, interiors, music, battle
   effects, complete menus and save transfer. Target a meaningful 20–30-minute
   first-play experience. The user approves matched clips for each applicable
   domain before campaign expansion; this is a slice gate, not project completion.

C. Complete systems: remaining battle interactions/doubles, growth/evolution,
   full content tools, storage, traversal, events, audio coverage and interfaces.
   Mechanics/performance/save gates pass without presentation regressions.

D. Campaign expansion: implement the 16 hubs, eight gyms, 150 entries and story
   in small batches. Each new hub satisfies its map/event/quest/asset/music gates
   before it is counted complete. Repeat the approved comparison protocol.

E. Final acceptance: full normal-speed playthroughs, collection validation,
   three-starter balance checks, native/web save and deployment checks, and
   user approval of the final 11-domain comparison suite.

Each implementation checkpoint records in this file: build commit, affected
criteria, prior/current approved scores, functional checks passed/required,
clip/evidence references, regressions, and the next weakest domain. Repeatedly
improving an easy high-scoring domain while leaving a weak one untouched is not
progress toward final parity. Do not lower a target to fit the existing code.

### 15.6 Baseline and current state

Current snapshot (October 15, 2026,04:00UTC; historical checkpoint details follow):

| Item | Authoritative current status |
| --- | --- |
| Execution | Continue full-spec work through intermediate releases until October15,6PM Pacific. Only the user or that deadline stops work. Fixed-date stop reminder active. App goal card is active as confirmed October14,00:58 Pacific; this spec supplies the current exact deadline. |
| Active stage | B: polish Sunset/South Park/Cognition before campaign expansion. Full section 15.1 scope stays required. |
| Human-approved full domains | 0/11. Title-art, courier-walking and doorway subset reviews are pending. |
| Public build | 0.0.75-park-paving-preview; target47909520ff1e419cdab4286c9e4507d2c35c66e83ae8703084721164dc3d0938; Site66. User-liked fine paving grid now neutral light gray, isolated primarybank4; road/building/Sunset colors unchanged. Full decoded-delta audit, three native door/cache returns, ordinary saves/coldContinue and Chrome clinic roundtrip pass. Human0/11; grid preference is not a domain score. |
| Latest local source build | v75 normal build from committed f85c8906 reproduces immutable47909520. Existing compiled gates/infill22+nestedpaving153 and full local checks pass. All1280 Park map words unchanged. Every primary/secondary resident tile and loaded palette bank restored after three interiors; matched C8→C9 saves/coldContinue preserve declared data. Manifest dirty marker retained for untracked release/PDF, no clean-checkout credit. |
| Content implemented so far | Sunset opening and courier apartment adventure, Muni, South Park, clinic and first Cognition gym draft; eighteen creature candidates and three starter lines. Complete 16-hub/8-gym/150-entry campaign remains unfinished. |
| Relevant functional evidence | Actual first-badge Firev45, Waterv48 and Grassv49 controller routes; earned batteries cold-load on later native/WASM builds. These establish first-badge viability, not complete campaigns or pacing. |
| Reference movement evidence | Courier candidate's first unblocked four-direction rectangle: sixteen frames/tile, zero difference against the reference. Full movement/performance/input gate remains open. |
| Public QA | Site41 public IAB patches/exports exact v51. Site42 source/core in isolated localhost IAB completed ten consecutive desktop native→browser→native save cycles, independently sealed; populated party/storage/resources preserved. Fresh public auth/isolation, Safari/mobile, browser performance/audio, fresh-session durability and50 campaign checkpoints remain open. |
| Remaining system gates | 711 independent native scenarios pass,57 doubles: all289 native type pairs,55 capture outcomes,8 delivery chains,10 move scripts,21 residual-phase and34 item-effect scenarios. Actual bag/Dex/save integration, SF species mappings, move-end/full-turn/faint resolution and coverage review prevent mechanics acceptance. Performance, save and full campaign gates stay outstanding. |
| Active performance issue | First v75 active600sec Chrome run: complete310row route, zero hidden ticks, but16discarded frame debt,13738underrun outputframes (~0.3115sec),334input observations vs310planned. Strict qualifier fails. Instrumented repeat also fails9debt/8330underruns, with exactly310inputs and no unexpected DOM/focus/longtask entries. No pacing fix yet. Earlier clean idle/short observations do not supersede this failure. |
| Next work | Diagnose active-field stalls/input contamination, then complete truthful starter-choice information and native/browser checks. Continue Stage B art/audio/interface polish and matched review; no campaign expansion before approval. Ten desktop save cycles remain one checkpoint;50 campaign checkpoints and full campaigns stay open. |

- Goal definition and reviewer preference are established. Reference capture
  tooling and the experimental hardware foundation have started.
- Approved Emerald-parity domains: 0/11. This is an approval count, not a claim
  that the prototype has no working functionality.
- Main build: actual Emerald engine, authored Outer Sunset opening, South Park
  travel, clinic and Cognition gym draft. Original SF creatures, cast art and music remain
  required. The earlier two-map/one-gym/12-monster prototype is archived.
- Quality-complete hubs/gyms/monsters: unreviewed. Earlier technical checks do
  not certify final content or visual/audio quality.
- Reference clip suite, measured timings and 300-case mechanics suite: pending.
- Next checkpoint: additional starter/team strategies, original wild creatures,
  map/cast/audio/interface polish and first-slice comparison reviews. The earned
  Fire route now verifies the first gym victory, reward, re-entry and save.
- Public preview: version 0.0.26 includes eighteen original creature/call candidates,
  original Sunset/wild/title themes, title/guide art, Sunset rowhouses/streets and courier locomotion,
  Sunset/Muni/South Park, the clinic,
  all three authored evolution lines and Cognition's gym draft. This is not the
  accepted polished slice or complete campaign.
- Reviewer: the user, through approval of matched comparison clips.
- Scope preference: Emerald-tier quality within existing SF scope; do not add
  breeding, contests or a full Battle Frontier clone as hidden requirements.
- Ask before database migrations and PR merges. Request concrete clip reviews
  at the stated gates. Resolve changes to scope/platform/originality with the user;
  ordinary engine and implementation choices remain autonomous.
- Never mark the goal complete while any required gate or review is outstanding.

First-slice checkpoint — South Park and Cognition draft:

- Authored a two-way Muni connection from the completed Sunset quest to the
  South Park block, a clinic with healing/shop/storage, park lore/discovery,
  and Cognition's sensor delivery, ordered relay puzzle and first gym roster.
  All authored map warps/connections stay within the SF map set.
- Native mGBA controller-only evidence under .tools/benchmarks/cognition-*:
  an existing schema-1 Sunset battery resumes, rides Muni, enters the gym,
  delivers the sensor (stage 1), rejects green-first (still stage 1), activates
  blue (stage 2), activates green (stage 3), crosses the opened gate and enters
  the actual SCOTT WU trainer battle. No gameplay RAM writes are used.
- Native compilation and exact BPS reapplication pass. The latest draft target
  is 088b5793cb077084b2c9fe0711f8007cb0adece248d2334f06ba72d0a3d3d3ab.
  Full cartridges remain ignored/private. Format, save, patch, archived-engine
  and TypeScript checks pass. Cross-runtime checks for this draft remain next.
- Nine wild stock species plus three stock starters exercise native habitats
  and team mechanics; they do not count as finished original Mini Monsters.
  Stock portraits, tiles and soundtrack are unreviewed scaffolding. The large
  interiors need furniture, composition, readable relays and SF art direction.
- Gym victory/reward/re-entry, clinic workflows, return travel, encounters and
  three-starter balance still need native play checks. This draft is not yet
  the public website release and earns no domain approval (still 0/11).

First-slice checkpoint — native save compatibility:

- Added a native main-menu guard using the same SF identity/schema as the web
  importer. Unsupported saves show an explanation and omit Continue. Their
  Flash contents are not erased, rewritten or silently converted.
- Real schema-1 Sunset battery: a 16,551-frame route through Muni, delivery,
  both relays, the opened gate and Scott's battle produces identical final RGB
  and Flash bytes in native mGBA and WebAssembly. Evidence:
  .tools/benchmarks/cognition-supported-save-guard.
- Independently modified, checksum-valid schema-2 and unmarked battery copies
  are rejected by the native menu with byte-identical exported backups. The
  schema-2 refusal also matches WebAssembly after 2,456 frames. Evidence:
  .tools/benchmarks/sf-native-*-guard-menu and sf-native-guard-no-continue.
- A controller-only gym loss returns to the registered Sunset healing location
  without granting a badge; relay stage 3 survives. Actual victory, clinic
  respawn registration and first-chapter balance remain unvalidated. These are
  compatibility checks, not the required ten complete-campaign round trips.
- New guarded target SHA-256:
  6698a2df771b0a8a6115e4e12018b4749b451d9bff7503fc67ac39624c4cbca2.
  Original art/audio and the clip reviews still block first-slice acceptance.
- Clinic follow-up: native controller play registers the SoMa respawn warp,
  restores the starter to 19/19 HP, purchases one ball (five to six; 200 coins
  deducted), and opens the actual Move Monsters box interface. Evidence:
  .tools/benchmarks/cognition-clinic-{heal,buy,box}. Full storage transfer and
  clinic blackout/re-entry checks remain outstanding.
- Restoring the pinned baseline after the native guard still reproduces exact
  Emerald; reapplying the overlay reproduces guarded target 6698a2df...cbca2.
- Original CinderCoy front/entrance/back source candidate is stored at
  assets/monsters/cindercoy/source-v1.png with its prompt and remaining cleanup
  requirements. It is not integrated or quality-approved; finished-monster and
  domain approval counts do not increase.
- CinderCoy now has reproducible native-format candidates: 64x64 front/back,
  two entrance frames, two icon frames and shared RGB555-compatible palettes.
  The independent asset contract check passes dimensions, transparent index
  zero, the 15-color opaque budget and cross-view palette identity. This is
  technical conversion, not deliberate pixel cleanup or art approval. Next:
  integrate the original species data/art into actual battles and menus.

First-slice checkpoint — original CinderCoy in the native engine:

- A data-driven species importer now supplies original names, six base stats,
  abilities, learnsets, field-guide text, front/back art, entrance frames and
  shared party-icon palettes. Native species IDs remain stable across saves.
- CinderCoy replaces the Torchic development slot with original coyote art and
  data. New starters learn Ember at level 5; older SF starters can gain it in an
  empty slot. Native controller play displays its back sprite in Scott's battle,
  executes a super-effective Ember, and displays the separately drawn front
  sprite in the summary interface. These are unreviewed presentation candidates.
- The one-time content upgrade covers party/storage, renames exact stock default
  names and preserves custom names. A checksum-valid SPICY nickname fixture
  remains SPICY. Read-only comparisons of the actual decoded party preserve
  personality/OT, experience, held items, EVs, IVs, origin and ability selection.
  Scratch/Growl and their PP stay unchanged; Ember fills the third slot at 25 PP.
- A 17,527-frame route from the actual earlier Sunset save produces identical
  final RGB/Flash in native mGBA and WebAssembly. The compiled patch reapplies
  byte-for-byte and repeats at target SHA-256
  20fe36c2e9af7b5b62bd093696536394339acaf1b4482b419276175b7f472f9a.
  Evidence: .tools/benchmarks/cindercoy-{first-battle,ember,custom-summary}.
- Creature-record bounds and native art contracts pass, along with the existing
  regression checks. Pixel cleanup, a distinct original cry, evolution-line art,
  SF type labels/chart, remaining eleven slice creatures and user clip review
  remain outstanding. No finished-monster or parity approval count increases.

First-slice checkpoint — all three original starter candidates:

- BrinePup and SproutSlug join CinderCoy with original source sheets, separate
  native front/back art, entrance poses, party icons, six-stat records, abilities,
  species-specific learnsets and guide descriptions. Palette groups 3–5 now
  contain the three original icon palettes. Source prompts and reproducible
  conversions are stored with each creature under assets/monsters.
- Starter interaction previews the actual front sprite and uses the original
  creature name. Controller-only fresh games select each starter at level 5,
  reach quest stage 2, receive exactly one party member and resume movement.
  Their initial moves are respectively Tackle/Growl/Water Gun,
  Pound/Leer/Absorb, and Scratch/Growl/Ember. Each party icon renders in its
  intended palette. Declining CinderCoy leaves no party member, preserves quest
  stage 1 and all three choices, closes the preview and releases movement.
- Evidence: .tools/benchmarks/{brinepup,sproutslug,cindercoy}-{preview-aligned,
  starter-accepted,party-icon} and cindercoy-starter-declined. Latest private
  draft target: 04ecdf09659cf6c0b42de858b14b9aba59c7774ff3fc2e34e0e129fbb62f0b07.
- Content revision 2 extends the existing upgrade table without reordering
  native species IDs. These three integrated candidates are not three finished
  evolution lines or approved monsters. Cries, evolution art, deliberate pixel
  cleanup, nine remaining slice creatures and matched clip approval are pending.
  Approved parity domains remain 0/11; the public Site still serves 0.0.4.

First-slice checkpoint — updated public preview:

- Site version 6 deployed successfully on October 7, 2026 at
  https://sf-mini-monsters.devkunjadia03.chatgpt.site with patch version
  0.0.5-cognition-preview. Site source commit:
  cc0f3da70bde2d3c9cf3d648c7dce018ac3276f4.
- The 586,024-byte BPS patch and integrity manifest are public. Archive inspection
  confirms no full Emerald-derived cartridge is hosted; the 67,820-byte original
  homebrew prototype remains separately available. The browser decoder matches
  native patch application byte-for-byte. Website type checking/build and the
  existing regression suite pass. The player describes the actual current route
  and explicitly labels the unfinished campaign and placeholder assets.
- Both current native and browser save guards preserve schema-1 compatibility;
  original species content upgrades preserve stable IDs and earned progress.
  Full campaign transfers, gym victory/rewards/balance, hands-on production
  sign-in, Safari/physical-mobile performance, original audio/evolutions and
  matched comparison approval remain outstanding. All 11 domains remain
  unapproved; publication is preview availability, not goal completion.
- Follow-up fresh-game replay check does not pass: the BrinePup party screen
  differs by 56 RGB pixels, entirely within the HP digits (native 21/21,
  WebAssembly 20/20). The frames, creature art, name and interface otherwise
  agree. Preserve this failed evidence; do not mask the digits or infer a pass.
  Evidence: .tools/benchmarks/brinepup-fresh-native-web, with separate timestamped
  WASM diagnostic frames. Native Emerald seeds new-game randomness from timer 1;
  startup timer/RNG alignment is the next investigation. The earlier
  battery-seeded 17,527-frame comparison remains a separate passing check.

First-slice checkpoint — pinned browser core and audio equivalence:

- The browser core now builds mGBA 0.10.5 at the same revision as the native
  reference harness. The previous packaged core used a newer upstream revision.
  A public shim adaptation preserves the SDK interface and drains raw hardware
  audio through a bounded queue. Source, immutable compiler image and artifact
  hashes are recorded; clean preparation never substitutes the newer core.
- The previously failing 10,842-frame fresh BrinePup route now matches every
  final RGB pixel, including HP digits, without masking or forcing random draws.
  Original failure frames remain preserved as evidence.
- The new 7,076-frame starter-cry route matches final RGB and all 7,764,140 raw
  stereo sample pairs. A 3,494-frame cold restore from the actual older Sunset
  battery likewise matches RGB, all 3,833,788 stereo pairs and exported Flash.
  Evidence: brinepup-original-cry-preview and pinned-core-battery-summary under
  .tools/benchmarks. These sample hashes verify emulated output, not browser
  AudioWorklet playback, underruns, physical-device latency or listening quality.
- Existing save/patch/asset/cartridge and TypeScript regression checks pass with
  the pinned core. The public Site runtime update remains to be deployed.
  All eleven quality approvals and the full campaign gates remain outstanding.

First-slice checkpoint — original starter calls:

- Added editable harmonic/formant synthesis recipes for CinderCoy's falling
  barks, BrinePup's lower honks and SproutSlug's three wet trills. Source WAVs
  and native signed PCM are original, with no commercial recordings/samples.
  Normal/reverse cry entries use these sources; starter preview also plays them.
- WaveData header/payload bounds, deterministic generation, silent endpoints,
  amplitude limits and audible energy checks pass. The actual BrinePup native
  preview executes with the same graphics/audio stream in WebAssembly as noted
  above. Listening quality and the other two native audition recordings remain
  to be reviewed. A passing sample hash does not earn audio parity approval.
- Private draft 0.0.6-starter-audio-preview target:
  d1b7a24a04ae4a046fbafb231a115e4ade0343daea92aca51c32901e18f1bd18.
  Public patch remains 0.0.5. Original neighborhood/battle music, remaining
  creature cries, evolution art, nine slice creatures and clip reviews remain
  required. This is three call candidates, not a completed soundtrack.
- Follow-up: CinderCoy and SproutSlug native audition routes are also recorded.
  Their 6,952/7,076 frames match every final RGB pixel and every raw stereo
  sample pair (7,628,080/7,764,140 respectively) in the pinned browser core.
  Evidence: cindercoy-original-cry-preview and sproutslug-original-cry-preview
  under .tools/benchmarks. This completes three functional call auditions,
  while composition, character and mix approval remain unreviewed.

First-slice checkpoint — public original-call preview:

- Public Site version 7 deployed successfully with 0.0.6-starter-audio-preview
  and the pinned mGBA 0.10.5 browser core. Site source commit:
  5228a3d789e2e71cccd486900c9426eae2d73be9. URL remains
  https://sf-mini-monsters.devkunjadia03.chatgpt.site.
- Archive validation confirms the 595,880-byte patch, the pinned-core fingerprint
  and no hosted full Emerald-derived cartridge. Browser BPS decoding reproduces
  the compiled target exactly; website build and the regression suite pass.
- The observed fresh-game HP discrepancy is resolved in the checked replay,
  with original failure evidence retained. Three native call-preview routes
  and an actual older-SF-battery restore match final pixels and every raw audio
  sample under the same core revision. These are bounded checks, not all release
  performance traces, campaign save transfers or user quality approval.
- Next weakest content area: original neighborhood/battle soundtrack, followed
  by remaining slice monsters/evolution art and map/cast polish. Real browser
  AudioWorklet/Safari/mobile checks, comparison clips, gym victory/balance,
  full 16-hub/eight-gym/150-entry campaign and all 11 approvals remain open.

First-slice checkpoint — original native Sunset score candidate:

- Ocean Commute now uses native MPlay sequencing: sixteen bars at nominal
  108 BPM, A/A2/B/A3 melodic development, answering pluck, root/fifth bass,
  major/minor chord pads and kick/brush/hat rhythm. Seven tracks use eight
  originally synthesized instrument samples. Score, mix, MIDI and wave sources
  are editable under assets/audio; no commercial melody/sample is copied.
- Native MIDI conversion compiles synchronized loop jumps for all seven tracks.
  Independent MIDI checks confirm monophonic tracks, program bounds, closed
  notes and a shared 1,536-tick loop. Instrument headers and payload bounds pass.
  The draft patch reapplies byte-for-byte at target
  8914865e5b0ef3335790ccc26533d1ec9f3f43761404b2bcca30e65e46c3240c.
- Actual native capture resumes an older Sunset battery and records more than
  three consecutive field loops. Local listening artifact:
  .tools/audio-review/ocean-commute-native-three-loops.wav. Evidence:
  .tools/benchmarks/ocean-commute-native-three-loops. Composition, instrument
  character, mix and loop/transition listening review remain unapproved.
- One neighborhood theme candidate is not soundtrack completion. Remaining
  fifteen hub identities, encounter/fanfare/title/credits contexts, original
  monster/evolution/cast/map work and all release/approval gates remain required.
- The 9,964-frame loop capture matches final RGB, all 10,932,996 raw stereo
  pairs and exported Flash in WebAssembly. Matched 40.18-second native A/V
  listening clips are prepared for Ocean Commute and Emerald's calm town cue.
  They use the same native size/speed, with the reference attenuated 4.06 dB
  to match the candidate's measured -25.31 LUFS. Only constant gain is applied;
  dynamics are not compressed to hide mix differences. Reference scene is the
  house using the same Littleroot cue, so this comparison judges music direction
  rather than outdoor map art. The reference's nominal loop is 53.33 seconds;
  both longer listening artifacts cover three consecutive loop periods.
- Local review files: .tools/audio-review/{sunset,emerald}-level-matched.mp4,
  ocean-commute-native-three-loops.wav and emerald-town-native-three-loops.wav.
  The user has been asked for one-theme direction feedback. No final audio
  score or first-slice approval is inferred from the pending response.
- Public Site version 8 deployed successfully with 0.0.7-sunset-score-preview
  at https://sf-mini-monsters.devkunjadia03.chatgpt.site. Its 607,553-byte BPS
  patch validates against the approved base and reconstructs the verified
  target byte-for-byte. Site source e503469376523d5eec18bb841e511d65318d8a7b;
  deployment appgdep_6ac6d9c643488191b6124a6e19a7f964.
  TypeScript and the packaged production build pass. Archive inspection finds
  the patch and the earlier original homebrew cartridge, with no inherited
  full ROM. Public access is preserved. Hands-on browser playback, Safari/mobile
  performance and actual sign-in/backup checks remain pending.
- Controller-only native play enters a random Sunset grass encounter, sends
  CinderCoy, escapes through RUN and returns to the field. Read-only MPlay
  inspection confirms the original field cue, native wild-battle cue and
  original field cue again; the battle outcome is RAN. No stats, flags or
  random values are written by the harness.
- The full cold-battery route repeats that sequence under native mGBA 0.10.5
  and the matching WebAssembly core: 27,142 frames, identical final RGB,
  all 29,781,556 raw stereo pairs and exported Flash bytes. Evidence:
  .tools/benchmarks/ocean-commute-field-battle-roundtrip; source 94de2cc,
  target 8914865e5b0ef3335790ccc26533d1ec9f3f43761404b2bcca30e65e46c3240c.
  This checks one music transition and battery route, not ten cross-platform
  campaign round trips, real browser AudioWorklet behavior or performance gates.
- Existing clean GitHub checks pass for 94de2cc:
  https://github.com/devk03/SF-Monsters/actions/runs/37704305361.
  That workflow builds the archived homebrew plus current host/content/web
  checks; it does not certify a clean Emerald hack rebuild or the SF campaign.
  Approved parity remains 0/11. Next: original encounter/neighborhood music,
  remaining slice monsters/evolution art and map/cast polish, while the theme
  direction review is pending.

First-slice checkpoint — original wild-battle score candidate:

- Fogbank Frenzy adds an original twenty-four-bar wild-battle cue at nominal
  132 BPM, with six related phrases, contrasting rhythmic sections, answering
  pluck, syncopated bass, chord pads and developed percussion. Seven native
  tracks use eight original synthesized samples. Editable notes and recipes
  live in assets/audio/fogbank-frenzy.json and scripts/romhack/battle_music.py.
- The importer now supports explicit, unique field/wild song bindings and
  keeps each instrument bank separate. Every generated Ocean Commute MIDI,
  sample and voice source remains byte-identical to the preceding checkpoint.
  Independent MIDI checks pass for both loop lengths, monophonic tracks,
  closed notes and program/header bounds; the native draft compiles and its
  patch reapplies byte-for-byte. Native listening/transition/browser evidence
  and user review are still pending at this checkpoint. No quality score changes.
- Native play on target d685ef1cde893130fe17180bd9a7e120702231924f8a483328c436721c003119
  reaches a random wild encounter with CinderCoy, remains in the battle menu
  for over three loop periods, then escapes and resumes Ocean Commute. Read-only
  MPlay/song-header inspection confirms the intended cue at each boundary.
  Listening source: .tools/audio-review/fogbank-frenzy-native-three-loops.wav;
  native 40.18-second A/V clip: .tools/benchmarks/fogbank-frenzy-review-40s/review.mp4.
- The cold-battery field/battle/loop route matches native and WebAssembly final
  RGB, exported Flash and all 37,528,144 raw stereo pairs across 34,202 frames.
  Evidence: .tools/benchmarks/fogbank-frenzy-battle-loop, source f13d9db.
  This is a bounded core/audio check; real browser performance/AudioWorklet,
  campaign save-transfer gates and user musical/presentation judgment remain open.
- Public Site version 9 deployed successfully with 0.0.8-battle-score-preview
  at https://sf-mini-monsters.devkunjadia03.chatgpt.site. The 617,864-byte patch
  reapplies exactly to the approved base. Site source
  edad77b7c06558aacce63df8df05c7b4abeb708c; deployment
  appgdep_6ac6dcc22af481919bedfb448d92f707. TypeScript, production packaging and
  the current host/content checks pass. Archive inspection excludes inherited
  full ROMs. The fixed Emerald battle reference and matched-volume review remain
  in preparation. Two music candidates do not complete the soundtrack; 0/11
  approved parity domains and all remaining SF scope/gates are unchanged.

First-slice audio comparison — measured battle-mix revision:

- The supplied reference cartridge now reaches its original rescue battle
  through controller-only clock, household, rival and route play. Native Torchic
  versus Zigzagoon provides the fixed-reference wild-battle cue and menu scenario.
  No reference game memory is changed, and reference ROM/audio/art stays private.
- Both native A/V clips run 40.18 seconds at 240x160 and normal speed. Initial
  Fogbank Frenzy measures -27.85 LUFS against the reference's -17.80 LUFS:
  a 10.05 dB level gap, recorded before further mix work. The 0.0.9 candidate
  uses a sustained original harmonic lead, stronger individual track mix and
  explicit native converter volume. It measures -16.87 LUFS, a 0.93 dB gap,
  with -8.05 dBTP and 1.60 LU loudness range in the compared battle-menu clip.
- Native capture on target
  0d3669cc8eee271876e25f76b5e9f2daff31c7599d9570d7781fc1fb4da3c2d6
  records 34,202 frames and 37,528,144 stereo pairs, peak 19,392, with zero
  saturated signed-16-bit samples. This is signal evidence, not composition
  approval or proof of every sound-effect combination/device. Loop/header checks,
  current regression checks and unchanged Sunset source fingerprints pass.
- Original wild-cue MIDI has a nominal 39.18-second loop after its introduction.
  The reference and SF longer listening files each cover at least three loop
  periods. The full fixed-reference clip suite and all domain approvals remain
  unfinished. Browser/core comparison, public 0.0.9 deployment and matched-level
  user direction review are the next checks for this revision.
- Matching WebAssembly execution now passes for all 34,202 frames, final RGB,
  exported Flash and all 37,528,144 raw stereo pairs. Native RUN returns to
  the original Sunset cue with outcome RAN. No saturated samples occur in
  this route; this does not certify every sound-effect combination or device.
- Matched-level review files are .tools/audio-review/fogbank-mix-level-matched.mp4
  and emerald-wild-mix-reference.mp4. Both retain native timing and dynamics;
  only a constant 0.93 dB attenuation is applied to the SF clip. Longer files
  fogbank-mix-three-loops.wav and emerald-wild-native-three-loops.wav cover at
  least three consecutive loop periods. Earlier quieter captures are preserved
  separately. Reference identity remains the supplied a9dec84d…85af ROM.
- The user has been asked for the battle cue's direction. No response, score,
  final soundtrack approval or first-slice acceptance is inferred while pending.
  Code/mix checkpoint 56af8c3. After this audio check, remaining slice monsters,
  evolution art, map/cast polish and gym victory/balance are the next content
  priorities; browser performance, full reference fixtures, saves and all release
  gates remain required before acceptance or campaign expansion.
- Public Site version 10 deployed successfully with 0.0.9-battle-mix-preview
  at https://sf-mini-monsters.devkunjadia03.chatgpt.site. Site source
  77b169e116dcd78a2f93068fed9a79f58e108771; deployment
  appgdep_6ac6e2799bdc8191b92d74de22d62e3e. The 615,007-byte immutable patch
  reapplies byte-for-byte to the approved base. Source opening, TypeScript,
  production packaging and archive inspection pass; no inherited full ROM is
  included, and public access is preserved. Existing GitHub checks pass for
  56af8c3: https://github.com/devk03/SF-Monsters/actions/runs/37707174159.
  These checks do not replace clean Emerald rebuild, hands-on sign-in/backup,
  actual browser/device performance or user approval. Approved parity is 0/11.

First-slice creature authoring checkpoint — evolution and icon contracts:

- Original level-evolution declarations now validate authored targets, unique
  native identities/assets, increasing thresholds and cycle-free lines. They
  compile into the existing native evolution table without changing species IDs.
  Other native evolution methods remain engine features; the original authoring
  schema currently covers unconditional level rules only.
- A native atlas encoder accepts separate battle views and separately authored
  icon frames, preserves aspect/ground alignment, and maps icons into their
  family's shared palette. The legacy three-view encoder remains unchanged.
  Independent output checks distinguish blue authored icons from red battle
  views and verify alternate frames, native PNG bounds and palette identity.
- CinderCoy's evolved art is in preparation. This infrastructure checkpoint
  does not count evolved creatures, prove an in-game evolution, or approve art.
  Starter-line data, original evolved cries, native/browser evidence and user
  review remain required. Approved parity stays 0/11.

First-slice creature checkpoint — authored CinderCoy evolution candidates:

- CinderCoy → Ashrunner at level 16 → Solhowl at level 36 is explicitly authored
  on stable native Torchic/Combusken/Blaziken IDs. Ashrunner is a faster Fire
  coyote with Flame Wheel at evolution; Solhowl becomes Fire/Dark with strong
  special attack/speed, Crunch at evolution and physical/support options.
  Species-specific learnsets, six-stat data, guide descriptions and distinct
  original bark/howl recipes are compiled through the native engine.
- Two new source atlases, back views, entrance poses and separately authored
  icon poses are saved under assets/monsters/{ashrunner,solhowl}, including the
  exact built-in imagegen prompts and encoding layouts. Native assets use
  fifteen opaque RGB555 colors; icons share CinderCoy's reserved palette group.
  Native-size cleanup and user art approval remain pending. This adds candidates,
  not two quality-complete monsters or three approved starter lines.
- Content revision 3 retains species IDs and the existing earned-progress upgrade
  behavior. A native compiler warning exposed twelve-character category labels
  overflowing their terminator space; the authoring limit is corrected to eleven
  and the boundary is covered. Native draft compilation and BPS round-trip pass.
- Private native-script fixtures prepare level-15/35 creatures and Rare Candy
  for evolution UI tests. Their build command requires --draft and manifests
  explicitly exclude campaign-progress evidence. Reference-compatible fixtures
  restore original name/stat/learnset data and a safe shared map position for
  battery setup; subsequent reference captures must use the actual a9dec84d…85af
  cartridge. These setups never count as earned campaign levels or balance runs.
  Native evolutions, move-learning, older-save/browser evidence, deployment and
  matched reference clips remain next. Approved parity stays 0/11.
- Native main-ROM fixtures now complete both evolutions, default-name updates
  and stat recalculation: level-16 Ashrunner at 47/47 HP and level-36 Solhowl
  at 103/103 HP in the recorded specimens. Flame Wheel replaces Leer through
  the actual move-forgetting UI; decoded/checksummed party data confirms
  Ember/Quick Attack/Flame Wheel/Bite with PP 25/30/25/25. These results test
  authored content on prepared levels, not normal campaign pacing.
- Each cold-battery evolution route matches final RGB, exported Flash and all
  7,366,936 raw stereo pairs across 6,714 native/WebAssembly frames. The actual
  older level-5 Sunset save resumes at unchanged level 5, 13/19 HP and quest 4;
  content revision advances to 3. Its 9,964-frame route also matches final RGB,
  Flash and all 10,932,996 raw stereo pairs. Captures live under .tools/benchmarks/
  {cinder-evolution15-main-full,ashrunner-evolution35-main-full,cinder-line-older-save-resume}.
- Public Site version 11 deployed successfully with the normal
  0.0.10-cinder-evolution-preview patch at
  https://sf-mini-monsters.devkunjadia03.chatgpt.site. Source
  811ef2a6ed152487c3331a3d08506e9723f7efe9; deployment
  appgdep_6ac6eeb833c48191adebc2a076a6336c. Its 632,272-byte patch reapplies
  exactly to target 5b54d6d8143319624b948a523a91b40a792997fbe33ea7a7357ac684629b5f5b.
  TypeScript/build/packaging pass. Archive inspection excludes full inherited
  ROMs and fixture patches; public access stays unchanged. GitHub checks pass
  for f19bebe: https://github.com/devk03/SF-Monsters/actions/runs/37710128830.
- Reference evolution captures use the actual a9dec84d…85af cartridge with
  prepared original-stat/name/learnset battery fixtures. Saved map views can
  carry SF tiles, so these fixtures are restricted to evolution/menu comparisons,
  not original-world or campaign evidence. The original Torchic's level-16 Peck
  prompt is declined before aligning the evolution scene; that learnset
  difference does not count as an animation-timing regression. Matched clips,
  native pixel review and user approval remain pending; parity stays 0/11.
- Solhowl's actual move-forgetting UI replaces Roar with Crunch. Decoded and
  checksummed party data confirms level 36, species 282 and
  Crunch/Slash/Flamethrower/Agility with PP 15/20/15/30. The first evolution
  similarly confirms species 281 and its authored Flame Wheel progression.
- Four 40.18-second native clips now pair both SF evolution stages with the
  supplied Emerald cartridge, all at 240x160, normal speed and zero measured
  A/V skew. Paths: .tools/benchmarks/{cinder-evolution15-animation-40s,
  ashrunner-evolution35-animation-40s,emerald-evolution15-aligned-40s,
  emerald-evolution35-aligned-40s}/review.mp4. The earlier reference capture
  stopped at Peck learning and is not used as an evolution comparison.
- The user has been asked for this line's art direction, with the prepared-level
  limitation explicit. Pending feedback does not approve pixel cleanup, back
  sprites, all 150 monsters, campaign balance or a whole quality domain.
  Next content priorities are the other starter lines, remaining first-slice
  creatures, map/cast polish and native gym victory/balance. All 16 hubs/eight
  gyms/150 entries, systems/performance/save gates and 11 final approvals remain.

First-slice creature checkpoint — BrinePup evolution candidates:

- BrinePup → Brinebull at level 16 → Tideroar at level 36 is authored on the
  stable Mudkip/Marshtomp/Swampert native IDs. Brinebull stays Water and learns
  Bubble Beam at evolution; Tideroar becomes Water/Ice and learns Ice Beam.
  High HP/defenses, special attacks and Protect/Rest give this line a distinct
  defensive role from the faster CinderCoy line. Stats, learnsets, guide text,
  original honk/roar recipes and explicit evolution rules are authored in data.
- Source atlases, separate back views, entrance poses and authored icon poses
  are saved under assets/monsters/{brinebull,tideroar}, with exact built-in
  imagegen prompts and panel layouts. Icons share BrinePup's reserved group 4.
  Unequal atlas panels can be padded transparently without stretching or cutting
  a wide flipper; an independent output test protects the outer tip and ground
  alignment. Native-size cleanup and art approval remain pending.
- Content revision 4 preserves stable save identities. Native draft compilation,
  BPS round-trip and content/atlas/cry checks pass. Private prepared-level and
  original-reference battery fixtures are added with the same publication guard;
  they do not count as campaign progress. Native evolution/move learning,
  older-save/browser evidence, matched clips and public deployment remain next.
  Seven original creature candidates are not seven quality-complete monsters;
  the SproutSlug line, slice wild creatures and full scope remain outstanding.
  Approved parity stays 0/11.

BrinePup line validation checkpoint:

- Main-ROM prepared fixtures complete both evolutions with normal native UI:
  level-16 Brinebull at 47/47 HP and level-36 Tideroar at 118/118 HP in the
  recorded specimens, with default-name updates and stat recalculation.
  Bubble Beam replaces Defense Curl, yielding Water Gun/Mud-Slap/Bubble Beam/
  Bite with PP 25/10/20/25. Ice Beam replaces Aurora Beam, yielding Bubble Beam/
  Protect/Ice Beam/Rest with PP 20/10/10/10. Decoded party checksums and stable
  species 284/285 confirm the actual changes; these are not earned-level runs.
- Both cold-battery routes match final RGB, exported Flash and all 7,366,936
  raw stereo pairs across 6,714 native/WebAssembly frames. The actual older
  Sunset save also resumes at unchanged level 5, 13/19 HP and quest 4, upgrades
  content revision to 4 and matches RGB/Flash/all 10,932,996 stereo pairs over
  9,964 frames. Evidence lives under .tools/benchmarks/{brine-evolution15-main-full,
  brine-evolution35-main-full,brine-line-older-save-resume}.
- Native 40.18-second SF clips are captured at 240x160 and normal speed under
  .tools/benchmarks/{brine-evolution15-animation-40s,brine-evolution35-animation-40s}.
  Matching fixed-reference Mudkip/Marshtomp evolution captures use prepared
  original-stat/name/learnset batteries and the actual a9dec84d…85af cartridge;
  saved-map-view carryover excludes these fixtures from original-world evidence.
  Clip encoding, reference inspection, user review and public 0.0.11 deployment
  are the remaining handoff steps. No quality-domain approval is inferred.
- Four paired clips now encode both BrinePup evolution stages and their actual
  Emerald counterparts at 40.18 seconds, native 240x160, normal speed and zero
  measured A/V skew. Final reference frames show Marshtomp/Swampert with their
  original names, confirming evolution rather than a stopped move prompt.
  Paths: .tools/benchmarks/{brine-evolution15-animation-40s,
  brine-evolution35-animation-40s,emerald-brine15-animation-40s,
  emerald-brine35-animation-40s}/review.mp4. The user has been asked for this
  line's direction; no answer or quality approval is inferred while pending.
- Public Site version 12 deployed successfully with normal
  0.0.11-brine-evolution-preview at https://sf-mini-monsters.devkunjadia03.chatgpt.site.
  Site source 02b62faeadae7d3486e448c7006eea6ed98b65e8; deployment
  appgdep_6ac6f22a447c81918c6ebe36cd273c64. The 646,141-byte patch reconstructs
  target 1a1a758ed3c6a633ef04c1b2d7fec4f0eee8ae6598fd65c4a37542cb7d301184.
  TypeScript, production packaging, host/content checks and archive inspection
  pass. Neither inherited full ROMs nor private fixture patches are included;
  public access is preserved. Existing GitHub checks pass for 5a98d04:
  https://github.com/devk03/SF-Monsters/actions/runs/37712708545.
- Art cleanup/back-view review, all three original starter lines, remaining
  slice creatures, map/cast polish and native gym victory/balance remain open.
  Browser/device performance, all reference mechanics cases, campaign saves,
  the complete 16-hub/eight-gym/150-entry scope and 11 final approvals remain
  required. Seven candidates and two integrated lines do not satisfy those gates.

First-slice creature checkpoint — SproutSlug evolution candidates:

- SproutSlug → FernSlug at level 16 → Canoptera at 36 is explicitly authored
  on stable Treecko/Grovyle/Sceptile IDs. FernSlug stays Grass and learns Poison
  Powder at evolution; Canoptera becomes Grass/Bug and learns Signal Beam.
  Native Gen III special Grass damage, physical Bug coverage and Leech Seed,
  status, recovery and screens provide a support role distinct from the other
  starter lines. Six-stat data, learnsets, guide text and original trill recipes
  are authored in editable files.
- Original front/entrance/back candidates and separately designed icon poses
  are saved under assets/monsters/{fernslug,canoptera}, with exact built-in
  imagegen prompts and encoding layouts. The existing atlas encoder preserves
  wing tips/proportions and maps icons into SproutSlug's reserved group 5.
  Native dimensions, shared palettes, evolution graph and cry bounds pass;
  the draft compiles and its BPS patch reapplies exactly.
- Content revision 5 preserves stable IDs. Private level-15/35 and original
  reference battery fixtures are covered by the existing publication guard;
  they are not campaign-progress evidence. Actual native evolutions, move
  learning, older-save/browser checks, comparison clips and deployment remain
  the next checks for this candidate. All three authored lines are not three
  approved lines, and nine candidates are not nine quality-complete monsters.
  Native-size cleanup, slice wild creatures, gym balance and the full scope
  remain required. Approved parity stays 0/11.

Approved architecture change — Emerald ROM hack:

- User direction: the result should immediately look and feel like Pokémon's
  Gen III game, including sprite presentation. The user approved Emerald hacking
  and local-ROM upload on the public website.
- Main path: pinned pret/pokeemerald build, SF source/data changes, local ROM
  reconstruction, patch release, and client-side validation/patching/play.
- The standalone Butano candidate is archived. Its native/WASM controller route
  matched final RGB pixels across 2280 frames; this remains experimental evidence
  and earns no quality approval for the new main path.
- All eleven domain approvals and the complete SF content/performance/save gates
  remain outstanding. Inheriting the engine does not complete SF maps or story.
- Next checkpoint: reproduce Emerald, then demonstrate an actual SF content
  change inside that engine. Do not publicly host the supplied or rebuilt ROM.

Emerald foundation checkpoint — matching reproduction:

- Pinned pret/pokeemerald 731ad5bfd6e6f265508d0efcca0ba42f9dcf5881 and
  pret/agbcc da598c1d918402c42c0c0d7128ba14567f3175e9 build a byte-identical
  16,777,216-byte Emerald cartridge. SHA-1 matches f3ae088181bf583e55daf962a92bb46f4f1d07b7;
  SHA-256 matches the approved user-supplied ROM. Local evidence:
  .tools/romhack-baseline/build.json. The ROM is ignored and unpublished.
- Build/compiler cleanup actions preserve temporary files under ignored storage.
  No cleanup deletion command is executed. The game/compiler C and assembly
  remain unchanged for baseline reproduction.
- This proves the engine foundation can exactly preserve the reference.
  It does not grant any SF content or final quality approvals. Next: original
  SF source/data overlay, verified patch application, then local browser playback.

Emerald foundation checkpoint — SF source overlay:

- Version 0.0.2-engine-probe introduces original SF opening dialogue and the
  Outer Sunset hometown label inside the actual Emerald engine. It remains an
  unreviewed engine proof with stock visuals, creatures, maps and story scaffolding.
  Finished SF hubs/gyms/monsters do not increase from these substitutions.
- The public artifact is a 226,361-byte BPS patch plus its integrity manifest.
  Applying it to the approved base reproduces the compiled 16 MiB cartridge
  byte-for-byte. Repeating the build reproduces the identical patch.
- Target SHA-256: 4121e399fdbebe109a508cc28c1d696ea101418193504f1a55e9d0300d0ed052.
  Full cartridges remain local/ignored. Actual first-slice maps, original cast
  art, Mini Monster replacements, SF events and browser upload remain required.

- The browser BPS decoder reproduces the real compiled SF probe byte-for-byte,
  matching native Floating IPS. Independent ASCII fixtures exercise all four
  patch commands, backward offsets and overlapping target copies. Corrupt patches,
  wrong input, invalid bounds and output checksum mismatches are rejected; the
  supplied ROM bytes remain unchanged. These are patch-format checks, not battle
  cases or presentation approvals. Website upload/play integration is next.

Emerald foundation checkpoint — local ROM player:

- Version 0.0.3-engine-probe preserves cartridge code BPEE for standard mGBA
  RTC, Flash and idle-loop compatibility while retaining the SF display title.
  The verified target hash is 32e256b0371bc00004fba7c58a7ea775bcce3356fcb985dfbe7a71ba3c267f87.
- The same patched cartridge produces identical final RGB pixels after a
  1096-frame native-core/WebAssembly controller route.
- Local browser QA loads the user-supplied ZIP, validates/extracts it, patches it
  without sending ROM bytes to the server, and displays Welcome to SAN FRANCISCO.
  Wrong-ROM rejection preserves the running cartridge. Chromium downloads the
  actual 16 MiB result with the exact verified target hash. Automated download
  event monitoring timed out, but the resulting file was verified on disk.
- Measured CSS widths 320/375/414/768/1440 have no horizontal overflow in the
  checked player. Desktop/mobile screenshots are in ignored .tools/qa.
  These are simulated viewports; physical-phone performance is still pending.
- Emerald Flash support validates complete rotating slots and checksums, chooses
  the latest intact counter (including wraparound), and rejects invalid backups.
  Existing prototype SRAM behavior still passes its tests; the earlier game and
  its local save namespace remain available through /prototype.
- The full SF campaign, actual campaign-save round trips/resume checkpoints,
  Mac GUI/Safari/physical mobile checks, sign-in QA and all eleven user approvals
  remain outstanding. No domain approval changed.

Emerald foundation checkpoint — public player deployment:

- Public Site version 4 deployed successfully on October 7, 2026 at
  https://sf-mini-monsters.devkunjadia03.chatgpt.site.
  Pushed Site source: 585833d9eefbcb6440c3069fd35f16cca5e29360.
- Deployment archive inspection confirmed that the main build contains the
  226,353-byte patch, with no full Emerald-derived cartridge. The only hosted
  `.gba` is the earlier 67,820-byte original prototype at `/prototype`.
- Repeating baseline bootstrap after applying the SF overlay preserves modified
  inputs, restores the pinned base and reproduces the exact original ROM again.
  Reapplying the overlay reproduces the immutable 0.0.3 patch; its browser-decoded
  output again matches the compiled target byte-for-byte.
- Public sign-in hands-on QA remains pending. This is a deployed engine preview,
  not a completed SF campaign. All eleven domain approvals remain outstanding.
- Next weakest domain: actual SF world/story content. Replace the stock opening
  with the Outer Sunset/Ocean Beach adventure before expanding neighborhoods.

Emerald foundation checkpoint — editable native maps:

- The source overlay can now compile authored ASCII layouts and native NPC,
  warp, coordinate-trigger and sign events. It validates format boundaries,
  event placement, object identity/budget and a walkable new-game spawn.
- Native bit-packing and invalid event/layout fixtures pass. The existing
  engine-preview cartridge and patch remain identical with this tooling added.
- Stock script linkage is retained while new map-entry scripts replace the
  corresponding inherited entry points. Bootstrap records/restores all modified
  inputs. No new neighborhood is counted complete from tools alone.
- Next: authored Outer Sunset block and its first in-engine quest events.

Native battery-save tooling checkpoint:

- The capture harness exports actual emulator battery saves and can cold-boot
  from them. It keeps emulator savestates and portable battery saves distinct.
- In the local Sunset draft, in-game Save produces a valid 128 KiB Flash file
  at counter 1. Cold boot resumes its acquired starter and inventory.
- Native → WebAssembly → native retains byte-identical battery data and matches
  the resumed final RGB after the same 2464-frame controller route. Evidence:
  .tools/benchmarks/sunset-real-battery-comparison and sunset-native-returned-from-wasm.
- This is one foundation pilot, not the ten full-campaign round trips or fifty
  checkpoint acceptance gate. Full campaign, device matrix and reviews remain.

First authored SF opening — local Sunset preview:

- A 32x32 Outer Sunset block replaces the stock hometown, with a western ocean,
  beach, street grid, house blocks and Judah/Great Highway sign. Fresh games start
  here directly; the stock truck/clock opening is bypassed.
- Karpathy offers three native starter choices and supplies, and heals the team.
  Roon's sensor is guarded by a native wild battle. Winning or capturing permits
  recovery; returning it grants 500 coins and directions toward Cognition.
  Naval/Jonathan have original ambient dialogue. Art, species and music are stock
  placeholders; this is not a quality-complete hub or the 20–30-minute slice.
- Controller-only native play verifies selection, inventory, battle, sensor
  recovery and delivery (quest stage 4, 3500 coins). It caught and fixed a
  redundant post-battle wait before any publication. The final fresh-town
  controller route matches native/WebAssembly RGB across 5972 frames.
- Map validation now covers the native connection-buffer limit, fifteen NPC
  slots plus the player, event placement and native local-ID/header linkage.
  Text validation rejects premature string terminators.
- Iteration patches stay in ignored draft storage until release. Bootstrap can
  restore all overlay inputs. No inherited full ROM is published.
- Native save schema uses reserved vars F8/F9; the browser rejects ordinary
  Emerald/unsupported SF saves and keeps earlier namespaces separate. Native
  refusal of unsupported schemas remains a release gate to implement.
- All eleven approved scores remain unchanged at 0/11. Next: finish the opening
  save/browser checks, publish this preview, then build South Park/Cognition,
  original Mini Monsters, SF art/music and the comparison suite.

Sunset player release checkpoint:

- Version 0.0.4-sunset-preview ships a 494,189-byte verified BPS patch. Target
  SHA-256: 2bf3ce822a56ff0c95dc3a9d271a3587a8ba469033179c4ce5a3b8c44602adf1.
- Native Save after delivery produces a valid SF schema 1 Flash backup at counter
  2. Cold native/browser resume matches final RGB and exported battery bytes after
  the same 2464-frame route. A raw emulator snapshot resumes with its paired Flash
  contents; snapshots alone do not embed battery data.
- Local browser QA imports that actual completed-quest save, continues at the
  saved beach location and prepares a valid backup. An unmarked Emerald-format
  backup is rejected while the current game remains playable. Browser slots use
  emerald:v2; prototype and earlier preview namespaces remain separate.
- Core/prototype regressions, BPS integrity, Flash format/SF schema, native map
  boundaries and TypeScript pass. The pushed Site production build passes.
- Public Site version 5 deployed successfully at the Play URL on October 7, 2026.
  Site source: 59f0536cebb1386d39f5e5a2ffea51c248015168. Archive inspection confirms
  no full inherited cartridge; the earlier original prototype remains /prototype.
- Production sign-in, Mac GUI/Safari/physical-phone performance, campaign checks
  and the complete comparison suite remain pending. This is an opening preview,
  not the completed MVP slice or full campaign; approved domains remain 0/11.

Native first-gym content tools checkpoint:

- Authored trainer teams can now replace pinned trainer slots, including native
  portraits/classes, individual moves, held items and battle items. Editable land
  encounter tables use the engine's twelve probability slots. They remain native
  battle data, rather than a replacement simplified combat system.
- Content limits and native identifier/name constraints pass checks. Map travel
  validation rejects foreign map destinations and absent arrival slots; themes
  can select native tilesets without changing the renderer.
- Cognition's occupied South Park office and separate expansion lease have been
  rechecked. South Park's oval form is sourced in startup-gyms.md.
- These are tools/research, not a completed gym or quality approval. Scores remain
  0/11; next is actual Muni/South Park and the Cognition challenge.

Reference sources for benchmark construction:

- [Emerald battle presentation and doubles](https://www.pokemon.co.jp/game/gba/emerald/battle.html)
- [mGBA scripting API](https://mgba.io/docs/scripting.html)
- [Gen III battle calculation reference](https://github.com/pret/pokeemerald/blob/master/src/pokemon.c)

Foundation checkpoint A — reference tooling:

- Native capture preparation now verifies the approved BPEE SHA-256 and isolates
  ROMs, saves, clips, and frame traces under ignored .tools/benchmarks.
- Native mGBA controller harness records frame numbers, controller state, and
  background scroll registers; all gameplay writes are controller input only.
- Frame-only encodes are explicitly diagnostics. Scored excerpts must come from
  synchronized native 240x160 audio/video and last 30–60 seconds.
- A new courier walking-sheet candidate was generated for asset-pipeline testing;
  it is unreviewed and does not establish pixel-art parity.
- Butano 21.9.0 (a9426cf21b8b6372e4f43678464345a1bf4594de) and pinned devkitARM
  Docker image sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5
  are being evaluated for hardware backgrounds/sprites and streaming music.
- The current production prototype remains at 0/11 approved quality domains.

Foundation checkpoint A — native graphics candidate:

- The pinned Butano/devkitARM build produces a genuine GBA SFMM cartridge.
  The initial build has four-direction interpolated walk/run, alternating
  footstep poses, and a twelve-frame 16x32 original courier sheet.
- Build and indexed-asset dimensions/palette checks pass. Walking/running use
  provisional 16/8-frame tile durations; these are not yet certified timings.
- Reproducible entry point: make foundation, after the documented pinned setup.
  This isolated candidate does not replace the public game or its saves.
- Native GUI checks are pending after emulator window automation became
  unavailable. The first reference recording was rejected: 1080x720 output
  despite native-resolution presets being shown. It is diagnostic only.
- No quality-domain score or approval changed. Map composition, music, core
  integration, measured walking baseline, and valid comparison clips remain next.

- The hardware candidate now scrolls the three provisional maps with camera
  clamping and collision data shared with game/content.c. SELECT map cycling is
  a foundation debug shortcut, not a campaign transition or new finished hub.
- A 760-frame controller route through native mGBA 0.10.5's Linux ARM64 core
  completed 28 tile steps and both map changes with zero missed game updates.
  Peak recorded game CPU budget was 1552/4096 (37.9%). This short foundation
  trace does not pass the three ten-minute release traces or Mac/web device gates.
- Capture instrumentation found that ordinary bus reads of write-only GBA
  background scroll registers returned open-bus data. The harness now uses the
  emulator's raw memory view; earlier scroll-register traces are invalid.

Foundation checkpoint A — audio and synchronized capture:

- Ocean Commute is an original four-voice AABA tracker candidate at 108 BPM,
  using synthesized instruments and percussion. It streams during traversal.
  Its source, notes and instrument recipes are editable and publicly included.
  It is one unreviewed draft, not soundtrack parity or sixteen completed themes.
- A capture-volume initialization bug was found through zero-amplitude checks
  and corrected. Re-recorded SF/reference signals peak at 9408/10848 respectively
  in signed 16-bit PCM. Earlier silent captures are invalid for audio review.
- Native-core video and audio clocks agree within 0.031 ms in the checked route.
  Encodes retain the GBA's native frame rate and 240x160 dimensions; duration,
  byte counts, audible signal and dirty-source metadata are recorded explicitly.
- The reference opening has reached the player's house through controller-only
  input. The walking baseline and matched reference/SF clip review are pending.
- Approved quality domains remain 0/11. Next: measured walking reference,
  browser foundation checks, and full first-slice integration/design work.

SproutSlug line validation and public release checkpoint:

- The normal main ROM evolves prepared specimens into level-16 FernSlug at
  47/47 HP and level-36 Canoptera at 108/108 HP. Default names update and native
  stats recalculate. The actual move-forgetting UI replaces Absorb with Poison
  Powder, yielding Poison Powder/Stun Spore/Leech Seed/Mega Drain and PP
  35/30/10/10. Signal Beam replaces Silver Wind, yielding Poison Powder/Signal
  Beam/Synthesis/Giga Drain and PP 35/15/5/5. Checksummed party decoding confirms
  stable species 278/279. These are evolution fixtures, not earned-level runs.
- Both 6,714-frame cold-battery routes match final RGB, exported Flash and all
  7,366,936 raw stereo pairs between native mGBA and WebAssembly. The actual
  older Sunset save resumes at unchanged level 5, 13/19 HP and quest 4, advances
  content revision to 5, and matches RGB/Flash/all 10,932,996 raw stereo pairs
  over 9,964 frames. Evidence: .tools/benchmarks/{sprout-evolution15-main-full,
  sprout-evolution35-main-full,sprout-line-older-save-resume}.
- Four matched 40.18-second clips capture both SF evolution stages and their
  actual Emerald counterparts at native 240x160, normal speed and zero measured
  A/V skew. Reference captures use the supplied a9dec84d…85af ROM and prepared
  original-name/stat/learnset batteries; final frames show Grovyle/Sceptile.
  The level-16 Pursuit prompt is declined before alignment. The earlier capture
  stopped at learning and is excluded. Saved-map-view carryover restricts these
  reference fixtures to evolution/menu evidence, not original-world comparisons.
  Clips: .tools/benchmarks/{sprout-evolution15-animation-40s,
  sprout-evolution35-animation-40s,emerald-sprout15-aligned-40s,
  emerald-sprout35-aligned-40s}/review.mp4. The user has been asked for direction;
  no pending response counts as approval.
- Public Site version 13 deployed successfully with the normal
  0.0.12-starter-lines-preview at https://sf-mini-monsters.devkunjadia03.chatgpt.site.
  Site source 5edd7477f7b55bb69fee9ac8a3a33d5395324ddf; deployment
  appgdep_6ac6f5afee6081919b9a9da0621326c8. Its 665,289-byte BPS reconstructs
  target eadd7196b8b7d2006d424e78ab55924cc6fb02cb91bf2e64421922ca04de495a.
  TypeScript/build, native content checks, BPS round-trip and archive inspection
  pass. The native host package contains 84 files; no full inherited ROM or
  private fixture patch is included. Public access remains unchanged.
  GitHub checks pass for 70a952b:
  https://github.com/devk03/SF-Monsters/actions/runs/37713787191.
- Three integrated lines and nine original candidates remain unapproved art.
  Pixel/back-view cleanup, remaining first-slice wild creatures, map/cast polish
  and actual first-gym victory/three-starter balance are next. Complete campaign,
  300 mechanics cases, device/audio/input gates, save/campaign runs and all 11
  final quality approvals remain required. Approved parity stays 0/11.

First-gym earned-route probe on the published starter-line ROM:

- The older, actually earned Sunset battery enters Scott's battle through Muni,
  delivery and ordered relays on the current eadd7196…495a target. Its single
  CinderCoy begins at level 5 and 13/19 HP, with three Potions, and skips both
  practice trainers, the clinic and recruitment. No prepared levels or RAM
  writes are used. Evidence: .tools/benchmarks/starter-lines-cognition-*.
- Ember defeats the opening level-6 Magnemite and CinderCoy earns level 7.
  Potion use restores HP through the native party interface. This minimal route
  then loses to level-7 Lotad after two Potions and a switch to Scratch; it does
  not reach Ralts or grant a badge. Move PP/HP are checked from party data.
- Controller-only blackout returns to the registered Sunset healing location.
  Gym relay stage remains 3; badge and defeated-gym flags remain false. Earned
  level 7 persists and HP is restored. The final capture is
  .tools/benchmarks/starter-lines-cognition-earned-route-loss. This is a single
  underprepared route, not evidence that all strategies fail or that the gym is
  balanced. No difficulty changes are inferred from this one result.
- Next: test the clinic, both optional practice trainers and recruited team
  routes with each starter, then actual victory/reward/re-entry and save resume.
  The release commit 594d630 also passes GitHub checks:
  https://github.com/devk03/SF-Monsters/actions/runs/37714577998.

First-gym preparation and clinic recovery regression:

- Controller-only play on the published eadd7196…495a ROM visits the South Park
  clinic, restores CinderCoy from 13/19 to 19/19 HP and all move PP, delivers the
  sensor and starts Walden's practice battle. An initial navigation capture
  instead entered wild grass and is excluded from healing evidence; subsequent
  corrected captures explicitly verify position, party checksum, HP and PP.
  Evidence: .tools/benchmarks/cognition-prepared-route-*.
- A separate intentional non-offensive battle probe reproduces a clinic
  blackout at South Park 6,17, far from its entrance at 32,5. It restores HP/PP,
  retains relay stage 1 and grants neither a badge nor gym victory. Evidence:
  .tools/benchmarks/cognition-clinic-blackout-before. This negative recovery test
  does not count as a normal balance attempt or campaign run.
- Recovery destinations are now explicitly authored in content: Sunset's two
  default native slots stay at 23,22; the registered clinic slot moves to 32,6,
  outside its entrance. The native map compiler rejects non-SF maps, unknown or
  duplicate slots, invalid/blocked/NPC/warp coordinates and script registrations
  without an authored recovery slot. Focused map/recovery tests pass, including
  the actual clinic destination and preservation of unrelated pinned data.
- Native rebuild, after-fix blackout/save checks, WebAssembly equivalence and
  publication remain pending for this source checkpoint. The public website
  still serves 0.0.12. Gym victory, practice/team balance, art cleanup and every
  final parity gate remain outstanding; approved quality domains stay 0/11.

Clinic recovery validation and public release checkpoint:

- Rebuilt the normal 0.0.13 cartridge and verified exact BPS reapplication.
  Native controller-only play now recovers at South Park 32,6, directly outside
  the clinic, instead of the reproduced old 6,17. Level 5, 19/19 HP, restored
  move PP and relay stage 1 are checked; badge/gym-victory flags stay false.
- The full 59,999-frame clinic/delivery/intentional-blackout route matches final
  RGB, exported Flash and all 65,833,900 raw stereo pairs in native mGBA and
  WebAssembly. Evidence: .tools/benchmarks/cognition-clinic-blackout-after-full.
  Its duration and intentional idle/test inputs do not certify story pacing,
  game-update deadlines, browser input latency or AudioWorklet/device performance.
- The recovered checkpoint is saved through the actual native menu. Its 128 KiB
  battery passes the website's SF validator at save counter 3. Cold Continue
  resumes the field at 32,6 with unchanged party and relay progress. That
  2,464-frame route matches RGB/Flash/all 2,703,624 stereo pairs in WebAssembly.
  Evidence: .tools/benchmarks/cognition-clinic-recovery-{saved,cold-resume}.
  The earlier shortened Continue attempt stayed at the title screen and is
  excluded; loaded RAM alone was insufficient evidence of gameplay resume.
- Public Site version 14 deployed successfully with normal
  0.0.13-clinic-recovery-preview at https://sf-mini-monsters.devkunjadia03.chatgpt.site.
  Site source 7f8a7e5ff1c419f66c2a08e7e6e380e83bcf6ee8; deployment
  appgdep_6ac6fca79db88191bec90f09ff7b8908. Its 665,298-byte patch reconstructs
  target c264be15b5ecc3279f447e4ecd0b9bba085017eea3b4b4f09893732407221b4b.
  TypeScript, production build, archive inspection and the source checks pass.
  The native package contains 84 files, with no full inherited ROM or private
  fixture patch. Public access remains unchanged. GitHub source checks:
  https://github.com/devk03/SF-Monsters/actions/runs/37715984319 (dff49e5).

First-gym preparation checkpoint — earned practice victory:

- On the earlier 0.0.12 main ROM, the healed level-5 CinderCoy defeats Walden's
  Zigzagoon/Seedot through actual native battles, using Ember and no Potions.
  It earns level 7 and finishes at 13/23 HP with move PP 35/40/21. This is normal
  earned progress from the older Sunset battery, not scripted levels or RAM
  edits. Evidence: .tools/benchmarks/cognition-prepared-route-walden-*.
- Native Save creates a portable earned checkpoint at Cognition 4,13, relay
  stage 1, with Walden's trainer-defeat flag set and no gym badge. The new
  0.0.13 cartridge resumes that older battery with the same level, HP, moves,
  PP, location and flags. Its cold route also matches native/WebAssembly final
  RGB, exported Flash and all 2,703,624 stereo pairs across 2,464 frames.
  Evidence: .tools/benchmarks/{cognition-earned-walden-saved,
  cognition-earned-walden-new-version-resume}. Both batteries pass SF validation.
- Next: heal/build the team, Steven's practice battle, Scott's actual victory,
  rewards/re-entry and three-starter strategy checks. These early checkpoints
  do not pass ten complete-scope save round trips, fifty campaign checkpoints,
  full campaign runs or any quality-domain approval. Art/map/audio/story polish,
  the complete SF scope and all final gates remain required. Parity stays 0/11.

First-gym validation checkpoint — earned Fire route:

- The normal 0.0.13 ROM completes Steven's practice battle from the earned
  level-7 Walden checkpoint, using Scratch against Wingull and Ember against
  Shroomish, with two Potions. CinderCoy earns level 9; Quick Attack fills its
  fourth slot through normal level-8 learning. Clinic healing restores HP/PP.
  The first solo attempt without recovery loses and is retained as a negative
  diagnostic, not a victory or balanced-route claim.
- A cold 33,744-frame replay of the successful route, starting from the actual
  earned battery without intermediate savestates, matches final RGB, exported
  Flash and all 37,025,604 raw stereo pairs between native mGBA and WebAssembly.
  Evidence: .tools/benchmarks/cognition-steven-earned-full.
- Supplies are bought through the native shop: three Potions cost 900 coins,
  taking money from 4,100 to 3,200 and the Potion count from one to four. Both
  relays are restored in order before entering Scott's actual leader battle.
- The level-9 CinderCoy defeats Scott's Magnemite/Lotad/Ralts using Ember and
  two Potions, earns level 11, and replaces Scratch with Leer through the actual
  move-forgetting UI. Final moves are Leer/Growl/Ember/Quick Attack with PP
  30/40/17/30; party checksum, HP 21/31 and move IDs 43/45/52/98 are verified.
  Some exploratory filenames say bite; the authored level-11 move and actual
  UI/data are Leer. Bite is authored at level 14. No Bite learning is claimed.
- Native victory awards 800 coins, the Build Badge and one Reflect disk (TM33,
  item 321). Gym stage becomes 4; badge, defeated-gym and reward flags are set.
  Money ends at 4,000 with two Potions remaining. Exit/re-entry restores the
  open gate and Scott's station. Talking again starts no rematch and leaves
  money, party, progress and the single Reflect disk unchanged.
- A complete cold replay from the earned Walden battery reaches the same badge
  and reward without intermediate savestates or scripted level/item gifts.
  Its 77,908 frames match native/WebAssembly final RGB, exported Flash and all
  85,484,552 raw stereo pairs. Evidence:
  .tools/benchmarks/{cognition-earned-first-badge-full,cognition-earned-scott-reentry}.
  The automated route includes deliberate waiting/dialogue inputs; its duration
  does not pass the normal-player pacing, input-latency or deadline gates.
- Native Save records the post-badge state at save counter 4. The battery passes
  the web SF validator and cold Continue resumes Cognition 8,4 with level 11,
  21/31 HP, all moves/PP, money/items, badge and gym/reward flags preserved.
  Evidence: .tools/benchmarks/cognition-earned-first-badge-{saved,resume}.
  Its 2,464-frame cold resume also matches native/WebAssembly final RGB,
  exported Flash and all 2,703,624 raw stereo pairs. Reflect remains quantity
  one and its reward flag remains set. This is an early campaign checkpoint,
  not the required ten complete-scope round trips or fifty campaign resumes.
- This proves one Fire-starter route from an existing earned Sunset/practice
  checkpoint, not three fresh full-campaign runs, all seeds or the required
  three team/strategy solutions per gym. Native Mac GUI/Safari/mobile, all 300
  mechanics cases, complete-scope saves, original slice art/audio/story/interface
  polish and the full 16-hub/eight-gym/150-entry campaign remain required.
  Approved quality domains stay 0/11. Latest existing release checks pass:
  https://github.com/devk03/SF-Monsters/actions/runs/37717333483 (bc008be).

First-slice interior upgrade foundation:

- The empty gym/clinic layouts are being composed into work, waiting and service
  areas while retaining their dimensions, main corridors and event identities.
  Native saved views would otherwise paint older cached tiles over updated rooms.
- The authored-map compiler now generates a native SF-map predicate. Continue
  reloads these layouts from content and reconstructs persistent terrain through
  on-load scripts, including Cognition's already-earned open gate. Unauthored
  maps retain the engine's ordinary cached-view behavior.
- A native position resolver keeps valid saved positions unchanged. If revised
  terrain blocks an older position, it selects a nearby walkable tile, avoids
  NPC/door anchors and uses the native same-map warp. It does not rewrite party,
  inventory, money or quest state. Coordinates outside a smaller map are clamped
  before bounded searching. This adds no save-schema or database change.
- Host C tests exercise the production resolver with sanitizers: valid positions,
  moved-NPC anchors, new collision, equally near NPC/warp exclusions, map bounds,
  foreign maps, no safe tile and unrelated state preservation. Native compilation
  and exact draft BPS round-trip pass. New room composition, actual older-save
  resume/rendering and cross-runtime verification remain next; public 0.0.13 is
  unchanged. This does not approve map art or any quality domain (still 0/11).

First-slice interior composition checkpoint:

- Cognition now has workstations, bookshelves, seating, a planning board and a
  coffee/supply nook around its preserved relay, trainer and leader routes.
  The clinic gains waiting seats, books/supplies, floor accents and a counter,
  retaining healing, shop, storage, notes and exit access. Dimensions and stable
  event identities are unchanged. These use inherited lab tiles as composition
  scaffolding; original tile/cast art and user map approval remain outstanding.
- Optional office objects add a team-planning hint, a flag-dependent incident log
  and one emergency Potion at the coffee shelf. The log changes from the unknown
  Sunset pulse to the Mission/Overclock lead after the badge. Native interaction
  gives exactly one Potion, sets its persistent flag and does not repeat the
  gift. This adds exploration/return interaction within the existing first slice.
- Route checks cover all required clinic interactions, trainer/relay approaches,
  the closed gate's barrier and access to the leader/log after opening. Focused
  and full source checks, native compilation and draft BPS round-trip pass.
- Native old-save tests preserve the earned post-badge position 8,4 and all party,
  moves/PP, money/items and flags, while showing the new layout immediately.
  An authentic 0.0.13 save made at the future bookshelf's tile 1,5 relocates to
  safe floor 3,5, with the same progress/resources. Both 2,464-frame routes match
  native/WebAssembly RGB/Flash/all 2,703,624 stereo pairs. The full 77,908-frame
  earned Fire route also retains its victory/reward and matches RGB/Flash/all
  85,484,552 stereo pairs on the new layout.
  Evidence: .tools/benchmarks/interiors-final-{valid-resume,blocked-resume,earned-gym}.
- An early draft used a bench-edge tile as floor; native visual inspection caught
  the repeating object detail and it was replaced before release. Final draft
  target: 234969b126fabde5068cd010d9f6eab91b0b9d8f94b21ff47994857bd34a1de7.
  Clinic workflows, final normal-patch publication and review clips remain next.
  Public 0.0.13 is still current at this source checkpoint. All 11 final quality
  approvals, original wild creatures, broader systems and full campaign remain.

Interior release and interaction validation checkpoint:

- Native interaction reads the post-badge incident log, collects one emergency
  Potion (two to three; flag 0x043 set), then confirms repeated interaction
  grants no additional item. Evidence: .tools/benchmarks/interiors-{incident-log-after,
  coffee-first,coffee-collected,coffee-repeat}. The office planning/return content
  remains inside the existing first slice, not a new completed neighborhood.
- Updated-clinic controller play heals the earned level-11 party from 21/31 to
  31/31 HP and restores PP, opens Patrick's actual purchase list/prices, and
  reaches the native PC menu. Evidence: .tools/benchmarks/interiors-clinic-
  {healed,shop,storage}. Opening these menus proves access; complete storage
  transfer, every inventory workflow and the final interface gate remain open.
- Public Site version 15 deployed successfully with the normal
  0.0.14-interiors-preview patch at https://sf-mini-monsters.devkunjadia03.chatgpt.site.
  Site source 74e600c55eed00dbb7cbab1e10eb075c50be7014; deployment
  appgdep_6ac71acb8e948191a49d4de987624622. The 676,294-byte patch reconstructs
  target 234969b126fabde5068cd010d9f6eab91b0b9d8f94b21ff47994857bd34a1de7.
  Native rebuild/BPS checks, TypeScript, production packaging and archive
  inspection pass. The native package has 84 files; full inherited cartridges
  and private setup fixtures remain excluded. Public access is unchanged.
  Source checks pass for 2710910:
  https://github.com/devk03/SF-Monsters/actions/runs/37727021369.
- Composition and compatibility have improved, but inherited tile/cast art,
  original wild creatures, original indoor/trainer/gym music, native-size art
  cleanup, comparison reviews and other starter/team strategies remain. The full
  16-hub/eight-gym/150-entry game, all system/performance/save/campaign gates
  and 11 final user quality approvals remain required. Approved parity stays 0/11.

Original gym-creature integration checkpoint:

- TrolleyKit (Electric/Steel cable stoat), PuddlePrig (Water/Grass reed frog) and
  HushMoth (Psychic blanket-wing moth) replace the first gym's three stock species.
  Each has original source art/prompt, separate native front/back/entrance art,
  two icon poses, an original synthesized call, six stats, abilities, a distinct
  learnset and guide text. Twelve original creature candidates are now integrated;
  six other slice species still use inherited creature presentation.
- Content revision 6 retains stable species IDs and existing save schema. These
  three species have no evolution until original targets are authored. Stock gym
  moves/items are preserved; new base stats and abilities are intentional content
  differences, so the earlier gym replay is not assumed to remain balanced.
- Source/content/audio checks and native draft compilation/BPS reapplication pass.
  Private 0.0.15-wild-preview target:
  9c681bba8f241abe6e2e6aacae3b82cd1205633b8ecd093f39439e1c83670f82.
  Native glyph/palette/battle checks, earned-route balance and native/WebAssembly
  evidence are next. The public release remains 0.0.14 pending those checks.
- Art was generated with built-in imagegen and encoded to native formats; deliberate
  pixel cleanup and art/audio approval remain pending. Reused icon palettes can
  simplify intended colors. This does not increase finished-monster counts or any
  of the 11 quality approvals. Full campaign, remaining systems and review gates
  remain required by section 15.1.

Original gym roster — gameplay and compatibility evidence:

- Controller-only native play from the real earned Walden checkpoint completes
  Steven, buys supplies and defeats Scott's TrolleyKit/PuddlePrig/HushMoth roster.
  CinderCoy finishes at level 11, 23/31 HP, with Leer/Growl/Ember/Quick Attack;
  two Potions and 4,000 money remain. Build Badge, gym victory/stage 4 and reward
  flags are earned through battle. This is one Fire strategy from an earned save,
  not three fresh campaigns or all starter/team balance solutions.
- The full 77,908-frame route matches final RGB, exported Flash and all 85,484,552
  raw stereo sample pairs in native mGBA 0.10.5 and pinned WebAssembly. A separate
  2,464-frame cold resume of the actual older post-badge battery preserves its
  position 8,4, 21/31 HP, moves/PP, items, money and flags; it matches RGB/Flash
  and all 2,703,624 stereo pairs. Evidence: .tools/benchmarks/original-gym-
  {earned-route,old-save-resume}. Real browser latency/playback remains unproven.
- Native battle captures show all three original fronts, names and calls through
  the actual gym encounter. Separate back/icon files satisfy encoding contracts;
  captured originals still need outline/pixel cleanup and icon-palette review.
  Evidence: original-gym-{trolleykit-settled,puddleprig-presentation,hushmoth-revealed}.
- Normal 0.0.15-wild-preview BPS is 703,494 bytes, SHA-256
  3694981fc659417334795e7e4cfb4c69d39bc49d2432cafe4335afd197d1892e.
  Native Flips and the browser decoder reproduce the compiled target exactly.
  Source/content/audio checks and Site typecheck/production build pass.
  All 11 quality approvals remain pending.

- Public Site version 16 deployed successfully with 0.0.15-wild-preview at
  https://sf-mini-monsters.devkunjadia03.chatgpt.site. Site source commit
  1d28c4b03e9f6e23b7372e671f1ad01f1c17c261; deployment
  appgdep_6ac7200d40288191800967c357d4fd5b. Archive inspection verifies the
  current normal patch and excludes inherited full ROMs and private fixtures.
  The hosting service reports 84 packaged files; raw inspection counts 85
  non-AppleDouble entries. No final parity or full-campaign approval is implied.
- Next weakest areas: deliberate native pixel cleanup, six remaining slice
  creature presentations, original cast/tiles/indoor and trainer music, alternate
  starter/team strategies and matched user comparison clips. The full section
  15 objective stays active; publishing this preview is not completion.

Early-route original creature/progression authoring checkpoint:

- BinPossum (Normal urban opossum) and PinePip (Grass pinecone hedgehog) replace
  Walden's stock team and their existing Sunset/South Park encounters. Both have
  original source sheets/prompts, separate front/back/entrance views, two icons,
  synthesized cries, stats, abilities, learnsets and guide text. Fourteen original
  candidates are integrated; four other slice species still need original art.
- Every authored creature now explicitly declares its catch rate, experience
  reward, six EV yields and growth curve. Existing values are retained for the
  prior twelve entries. Authoring rejects overflowing native fields, malformed
  effort rewards and changes to a stable slot's experience curve; this prevents
  saved EXP from silently turning into a different level. These contracts do
  not establish 300 independent battle-mechanics cases or complete growth QA.
- Revision 7 preserves stable IDs/schema, default-name upgrades and earned move
  insertion. BinPossum/PinePip do not evolve until original targets are authored.
  Native draft compilation/BPS round-trip and required source checks pass.
  Draft target: 57b04945a9e6d79ad910c8defe4ab55a1f5ac181b4284a3f55f45c7fe94c2793.
- Native battle/balance and older-save evidence are next. Both art candidates
  still need pixel/outline cleanup and user art/audio review. Public 0.0.15 is
  unchanged at this checkpoint; all 11 final quality approvals remain pending.

Complete first-slice creature-presentation candidates:

- NightSkunk, PierPeep, HillChirp and Mycelimp replace the remaining four stock
  encounter species, including Steven's trainer roster. Every first-slice
  species now has an original name, separately authored front/back/entrance views,
  two party-icon poses, an original cry, stats, abilities, progression data,
  learnset and guide description. Eighteen original entries comprise twelve
  base/slice species and six starter evolution stages. This is not 150 entries
  or eighteen approved/finished monsters; pixel and palette cleanup remains.
- Revision 8 keeps the existing IDs/schema and supported-save growth curves.
  Stock wild evolution targets remain disabled until original targets exist.
  All original art sources/prompts and native encodings are public contributions.
  Native draft compilation/BPS reapplication and required source checks pass.
  Draft target: 11f315ea2f5c3191d067360e58465d4b2db96ff719fd0d3e5fe0d5726806e176.
- The preceding two-creature draft verifies the earned level-5 Fire route through
  Walden with no Potions, ending level 7, 13/23 HP and Ember PP 21. Its 35,285-frame
  cold replay matches RGB/Flash/all 38,716,464 stereo pairs in native/WebAssembly.
  Native frames show BinPossum/PinePip fronts and names. Older badge save resume
  also preserves its earned state and matches all 2,703,624 stereo pairs.
  Evidence: scouts-{earned-walden-route,old-save-resume,binpossum-presentation,
  pinepip-presentation}. These checks do not certify balance of the new final roster.
- Next: final-roster earned trainer/gym replay, actual capture/party presentation,
  broader art/audio/interface/cast polish and matched comparison clips. Public
  0.0.15 remains current until validation; all 11 final approvals remain pending.

Final opening-roster gameplay/release checkpoint:

- Native final-roster play again defeats Walden from the actual level-5 Sunset
  battery without Potions, ending level 7 and 13/23 HP. Its 35,285-frame cold
  route matches RGB/Flash/all 38,716,464 stereo sample pairs in WebAssembly.
- The earlier fixed Steven/gym input replay fails and remains preserved under
  slice-roster-earned-gym. PierPeep faints after three Scratch attacks, moving
  the old Potion input into the level-up UI; Mycelimp then defeats the unhealed
  party. This is not masked or counted as a pass. Reading the actual command
  menu, using one Potion against Mycelimp and two Embers earns Steven's victory
  and level 9. No game stats, flags, experience or random draws are forced.
- The corrected continuous cold route heals/restocks normally, defeats Scott,
  earns the badge/rewards and returns to Cognition 8,4. It ends level 11, 4/31 HP,
  Leer/Growl/Ember/Quick Attack, three Potions and 4,000 money. All 71,038 frames
  execute in native/WebAssembly with identical final RGB/Flash and all 77,946,444
  stereo pairs. Evidence: slice-roster-earned-gym-cold and the preserved
  slice-roster-steven-* steps. This remains one earned Fire strategy, not the
  required three fresh campaigns or all starter/team/seed balance solutions.
- Source checks pass for 08a69bc:
  https://github.com/devk03/SF-Monsters/actions/runs/37730067469. Native compilation,
  Flips/browser BPS round-trip, Site typecheck/build and archive inspection pass.
  Normal 0.0.17 BPS: 740,811 bytes; SHA-256
  13c3339184c911bd03e4c228c94c3c03421ec0bb240cf2f91257a67c5ebed64b.
- Public Site version 17 deployed successfully at
  https://sf-mini-monsters.devkunjadia03.chatgpt.site. Site source
  03c48fecd77e13888d63fdd76f5ba669375bd40f; deployment
  appgdep_6ac7252533f08191b52ab4293fbca7d3. Its 84-file native package excludes
  inherited full ROMs and fixtures; raw non-AppleDouble inspection counts 85.
- Original front/back/entrance/icon/cry candidates now cover the opening roster.
  Native pixel cleanup, actual capture/party review, cast/tiles/music/interfaces,
  additional starter strategies and user comparison reviews remain open. All
  11 final approvals and the full 16-hub/eight-gym/150-entry campaign remain required.

Capture-storage recovery checkpoint:

- The host ran out of disk space while recording the actual wild BinPossum
  capture attempt. Failed partial evidence is retained, not counted as a pass.
  The first two bag-navigation checkpoints are intact; the subsequent ball-pocket
  recording did not finish. A trace-only retry is still waiting on its live
  Docker compilation process (sf-capture-0fb9f08e83), not assumed completed.
- Added lossless gzip storage for raw native frames and streaming support in the
  clip encoder. Compression verifies the entire decoded byte count/SHA before
  replacing a raw file and retains a recovery receipt. Frame-count, hash and
  corruption tests pass. Final pixels, PCM, save/state and controller evidence
  remain unchanged. This changes evidence storage, not game art or emulation.
- Actual 403,660,800-byte Mycelimp battle frames decode to the original SHA-256
  8b762cce63f6252c97282f1392e31cb2859affc052c92e2731611741adf75818,
  using 10,789,465 compressed bytes. The updated encoder successfully produces
  a 44.00-second native A/V clip after an initial disk-full encoding failure:
  .tools/benchmarks/slice-roster-steven-ember/review-729fbb15fc.mp4.
  This is a functional clip, not a matched comparison or human quality approval.
- Existing completed captures are being losslessly compressed to recover space;
  unrelated user files remain untouched. Required source checks including the
  new storage contracts pass. Public 0.0.17 remains current; capture/party review,
  paired art/audio clips, cast/tiles/music and all full-campaign gates remain open.

Browser/capture progress and CI budget checkpoint:

- The user requested fewer GitHub workflow runs. Validation now uses manual
  workflow_dispatch only, with concurrency cancellation for superseded deliberate
  runs. Routine pushes/PRs do not launch it; local checks remain the default.
  AGENTS.md records the rule. No active/queued runs existed when checked.
- A real Chrome 154.0.8037.98 guest window on macOS 26.6.2 loads the public home
  page anonymously, selects the verified local Emerald file and boots the player.
  The downloaded 16,777,216-byte cartridge matches target SHA-256
  11f315ea2f5c3191d067360e58465d4b2db96ff719fd0d3e5fe0d5726806e176.
  Private copy: .tools/browser-review/production-downloaded-v17.gba. The page
  accepts the actual earned post-badge native battery. Field continuation,
  exported-save equality, real sign-in and device performance remain unproven.
- Added a Docker-independent controller capture harness for the pinned WebAssembly
  core. It verifies core/cartridge fingerprints, exact state provenance and input
  bounds, restores companion Flash, and writes actual state/Flash/audio/final
  pixels plus optionally losslessly compressed video. It never changes game RAM
  directly. Metadata labels this runtime separately; the existing comparison
  harness now rejects a WASM capture as its purported independent native reference.
- Actual gameplay from the intact native wild/bag checkpoint throws one ball,
  captures level-3 BinPossum, displays its authored guide text, declines a nickname
  and returns to Sunset with a second party member. BinPossum has 15/15 HP and
  Tackle/Tail Whip/Sand Attack at 35/30/15 PP. No scripted gift or prepared levels
  substitute for capture. Evidence: slice-roster-wasm-{catch,caught-guide,caught-party}.
  The 2,184-frame capture sequence records 2,396,392 stereo pairs and a 36.57-second
  clip at slice-roster-wasm-catch/review.mp4. This is WASM gameplay evidence;
  the stalled native retry has not yet supplied the corresponding comparison.
- Source checks and capture-provenance tests pass. The prior clean CI failure was
  a missing benchmark directory in the new frame-storage test; its setup now
  creates that directory and the focused checks pass locally without a new CI run.
- Native title/guide wording still contains inherited franchise branding, and
  cast/tiles/music/pixel cleanup remain unfinished. These are explicit remaining
  originality/presentation gaps. First-slice and full-campaign quality approval
  remain 0/11; section 15.1 stays the complete objective.

Native Mac capture and caught-party save checkpoint:

- Added an explicit host backend to the existing controller capture tool. It
  builds the same pinned mGBA 0.10.5 revision with Apple Clang, records the static
  library/platform fingerprint, preserves generated cleanup targets and rejects
  snapshots without matching cartridge/core/controller provenance. Docker jobs
  and their incomplete evidence remain intact. The previously stalled retry is
  not counted as finished; this is a separate completed native Mac recording.
- Native Mac capture of the real BinPossum ball throw matches the existing
  WebAssembly recording: 2,184 controller frames, all 38,400 final RGB pixels,
  exported Flash and all 2,396,392 stereo sample pairs. Evidence:
  slice-roster-macos-catch. A separate native video records the same sequence,
  is losslessly compressed and encodes to a 36.57-second A/V clip at
  slice-roster-macos-catch-video/review.mp4. This is not yet a matched Emerald
  capture comparison or a user quality approval.
- Controller play inspects the caught creature in the party and summary menus,
  then saves through the actual in-game prompts. The continuous native sequence
  is 8,330 frames (slice-roster-macos-catch-party-saved). Its battery is identical
  to the separately played WASM save, SHA-256
  ca1024db3fcdbddac57620444f133e1c53c56aafb14dc5d8dcb358cf03e3770e.
  No creature, experience, inventory or quest-state RAM is forced.
- A 1,336-frame cold native boot of that battery matches WASM final RGB/Flash
  and all 1,465,924 stereo pairs. Later rendered inspection found that this short
  input stops at the title screen: decoded save data is preserved, but playable
  continuation is not proven by this recording. CinderCoy remains level 5, 13/19 HP with
  Scratch/Growl/Ember at 32/40/25 PP; BinPossum remains level 3, 15/15 HP with
  Tackle/Tail Whip/Sand Attack at 35/30/15 PP. Sunset position 7,11, money 3,500,
  three Potions and pre-gym flags remain. Evidence: slice-roster-macos-caught-
  cold-resume and slice-roster-wasm-native-party-cold-resume. This checkpoint
  does not establish ten consecutive transfers or fifty campaign checkpoints.
- Required source checks pass locally; no GitHub workflow was dispatched.
  Party/summary still display inherited franchise labels. Native title, original
  cast/tiles/music, pixel cleanup, wider balance and real browser performance
  remain open. Public 0.0.17 is unchanged; all 11 approvals and the complete
  section 15.1 campaign/system gates remain required.

Original native interface labels — private preview checkpoint:

- Authored 41 compact labels for team selection, summary, guide searches,
  capture messages and save information. The Start menu uses TEAM and GUIDE;
  party selection says "Choose a monster" and summary uses MONSTER INFO/SKILLS.
  A guarded post-link text overlay keeps the engine's allocated addresses and
  cartridge size unchanged. It verifies each allocation against the linked ELF,
  rejects missing/ambiguous/overlapping/stale/overflowing slots and preserves
  unrelated bytes. Reapplication is idempotent. Boundary/correspondence checks pass.
- The normal build now applies this overlay. Docker compilation is still stalled,
  so a separately labeled private text-only preview starts from verified 0.0.17.
  It does not claim a new full rebuild. Private target SHA-256:
  36156ec34d7e05614f33e9d8a9b01a034446f0fcb01500fecd03898f2f34e1f8.
  Native Flips and the browser BPS decoder reproduce that target exactly.
  The public website remains 0.0.17 until normal compilation is verified.
- Rendered QA exposed an earlier evidence error: the short 1,336-frame battery
  input loaded party data but remained at the title. That recording is retained
  as boot/decoded-save evidence and is not counted as playable continuation.
  The corrected 3,752-frame cold sequence visibly reaches Sunset. In native Mac
  mGBA and WASM it matches final RGB/Flash/all 4,116,880 stereo pairs, preserving
  both caught-party members, moves/PP, money/items and location. Evidence:
  interface-final-native-field. Actual menu captures show readable TEAM/GUIDE,
  party and summary labels; this is not real browser latency or full UI approval.
- Guide-list header art still displays inherited branding, as does the title.
  Those graphics, other labels/assets, native pixel cleanup, cast/tiles/music,
  wider balance and all complete-campaign gates remain unfinished. All 11 user
  quality approvals remain pending. No GitHub workflow was dispatched.

Original courier locomotion — native player-art checkpoint:

- Added an original eighteen-pose courier atlas: gray beanie, navy jacket,
  orange messenger strap/bag and olive trousers. Three authored views each have
  idle, two walk steps, run passing pose and two run steps. Native east-facing
  animation mirrors the west frames. Both player selections share this neutral
  courier design. Sources, prompt, native strips and conversion fingerprints are
  under assets/characters/courier-native. Pixel cleanup/human approval are pending.
- Conversion isolates transparent source bands rather than assuming an equal
  grid, uses one scale and per-row baseline, and encodes sixteen-color 16x32
  native frames. The walking/running strips each have nine distinct stepping
  frames and exactly 2,304 bytes in the engine's macro-tile order. Independent
  tile-order/pose-order, missing/blank/index-overflow and duplicate-step checks
  pass; both strips use the same native palette. Required local checks pass.
- A dedicated palette tag (0x1124) is registered for normal movement and its
  reflection pairing. Compiled records for both selections/shared normal-view
  aliases use it; existing cycling palettes remain unchanged. No animation
  commands, movement/camera code, collision geometry or save layouts change.
  Trainer/back portraits, cycling/surf/field-move poses, named NPC art and the
  complete human art library remain unfinished. These are not counted complete.
- Normally compiled private 0.0.25 target SHA-256:
  26faaec3a354db9e16dd70f2721af448a67d9f68e2196fdd103fc9e1958021aa.
  A cold battery route reaches the road at (18,22) with the caught party, money,
  items and flags intact. A 2,080-frame controller-only route walks/runs in all
  four directions, shows alternating poses/camera scrolling and returns there.
  Every RGB frame, Flash and all 2,282,280 stereo pairs match native/WASM.
  Native footage is courier-native-four-direction-motion/review.mp4, 34.82s;
  palette and comparison evidence lives beside it. Reference timing and a
  matched human review remain required; this clip alone does not establish them.
- Public 0.0.24 is unchanged while the courier comparison is prepared. Full
  quality approvals remain 0/11. No GitHub workflow was dispatched.

- Courier review evidence: courier-paired-walking-review/comparison.mp4, 32.15s,
  1,920 frames per side, equal nearest-neighbor 3x scale. Left is the supplied
  reference cartridge in its original Littleroot courtyard; right is the newly
  compiled courier in Sunset. Both run native mGBA 0.10.5 on the development Mac
  with identical direction/duration rows. Both return to their starting tiles.
  The first unblocked 480-frame rectangle has identical normalized BG1 camera
  movement in all four directions: one pixel/frame, sixteen frames/tile, zero
  measured frame difference. Later reference laps meet roaming NPCs, so the
  whole clip is not treated as uniform timing evidence. Running reference timing,
  input-consumption latency and real-time performance still need their gates.
- A prior reference evolution snapshot displays cached SF map/weather. It is
  excluded from this authentic-town walking comparison. This new reference
  lineage resumes emerald-route101-right-lane, closes the original NPC dialogue
  with controller inputs and walks to the original courtyard. Its reference
  ROM fingerprint and visible scene are verified. Prepared evolution/save
  fixtures must not substitute for pristine field/reference-world evidence.
- User feedback is requested for courier silhouette/palette/readability and
  four-direction walking art only. Audio uses the SF capture, and the separate
  34.82s SF clip shows running. No full movement, pixel-art, world or audio domain
  is approved by these measurements; all eleven full approvals remain pending.
  Source/asset checkpoint c3634a5 is pushed. Public 0.0.24 is unchanged while
  this courier checkpoint is reviewed. No GitHub workflow was dispatched.

- Native UI review clip: interface-final-native-review/review.mp4, 40.25 seconds,
  2,404 controller frames and 2,637,788 stereo pairs, source commit 0a5c888.
  It shows the Start menu, caught-party selection, summary, stats and moves.
  This private text preview remains unreviewed; it is not an Emerald comparison
  suite or a replacement for the pending normal rebuild.

Original Field Guide header — private native-art checkpoint:

- Generated an original transparent FIELD GUIDE wordmark with the built-in
  image tool. Its exact prompt, source, two-color native conversion and binary
  ink mask are under assets/ui/field-guide. No inherited menu sheet is published.
  Native rendering is readable at 240x160; typography approval remains pending.
- The graphics overlay clears thirteen center header tiles, places the 80x8
  wordmark at the pill's center, and preserves both caps and every unrelated raw
  tile. The first preview retained a column of the old final letter; rendered
  inspection exposed it and the corrected range removes that residue.
- The pinned native LZ77 codec reencodes the complete 8,192-byte resource to
  2,564 bytes inside its existing 2,584-byte allocation. Lossless decoding and
  allocation/neighbor/nibble checks pass. Normal builds apply text then graphics;
  private previews are still explicitly marked as not fully recompiled.
- Corrected private target SHA-256:
  96e663547a2beb28287c1613b04f9a7ab3f6bbad81c067191bf8a26adead20d9.
  A 4,608-frame cold run reaches Sunset, opens the guide and matches native Mac
  mGBA/WASM final RGB/Flash/all 5,056,128 stereo pairs. The actual caught party,
  moves/PP, items/money and location survive. Evidence: guide-header-final-native-open.
  Native Flips/browser BPS reapplication and required local source checks pass.
- Private review clip: guide-header-final-native-review/review.mp4, 39.85 seconds,
  2,380 controller frames and 2,611,452 stereo pairs. It shows guide navigation,
  an original creature entry and return to the list. This is not a paired Emerald
  comparison or a user approval. Public 0.0.17 remains unchanged; normal compilation,
  original title/other graphics, full slice polish and every section 15.1 gate
  remain required. Approved quality remains 0/11. No GitHub workflow was dispatched.

Original title lettering and compiler diagnosis — private checkpoint:

- Generated original SF MINI MONSTERS and SAN FRANCISCO wordmarks. Editable
  source/prompt, indexed native conversions, palettes and tile payloads are under
  assets/ui/title. The main logo uses sixteen RGB555 colors in an eight-bit tile
  sheet; the subtitle uses contiguous left/right 64x32 sprite blocks. Pixel/art
  approval remains pending; the background creature/footer and title music remain
  inherited. This replaces two branding elements, not the whole title experience.
- Rendered inspection caught clipping from the engine's 29-pixel horizontal
  affine offset. The corrected visible logo is 180 pixels wide and centered at
  source x=91; all letters now fit on the 240x160 screen. Existing title animation
  code, input, sprite positions and the creature/cloud palette tail are preserved.
- A reusable native-resource writer validates ELF correspondence, allocation
  bounds, overlap, exact reapplication and lossless compression before writing
  the cartridge. Logo compression uses 3,668 of 5,892 bytes; the subtitle uses
  its full 1,588-byte allocation. Neighbor/palette-tail and actual split-sprite
  ordering tests pass. The native codec now accepts the required 16 KiB logo.
- Private target SHA-256:
  5ac09182ec46d89484b7aa717f8b22fd58c9b51a576d85c8a7780a5571926ad8.
  A 4,608-frame cold route reaches Sunset and the guide, preserving the caught
  party/save state and matching native/WASM RGB/Flash/all 5,056,128 stereo pairs.
  Native Flips/browser BPS reapplication and required local source checks pass.
- Docker host logs report disk-full writes and missing-image-blob I/O failures;
  the VM console records an aborted ext4 journal. The supported start command
  reports the app already running. One supported restart, bounded to 45 seconds,
  fails because desktop/backend processes will not exit. No storage is removed
  or reset. Force-quit/recovery approval is requested because Docker may serve
  other work; no dependent recovery action proceeds without the response.
- Public 0.0.17 is unchanged. Normal compilation, the original title scene/music,
  full slice polish and every full-game gate remain required. All eleven quality
  approvals remain pending. No GitHub workflow was dispatched.

- Native title-lettering review: title-lettering-final-native-review/review.mp4,
  40.18 seconds at the original GBA rate, 2,400 controller frames. The main logo
  and subtitle are readable throughout the inherited title animation. This is
  a private candidate clip, not a paired Emerald suite or user quality approval.

Bayveil title silhouette — private original-art checkpoint:

- Generated original fog-manta silhouette art from the existing Bayveil design:
  broad curled wings, kelp-like whiskers, fog-ribbon tail and two lighthouse eyes.
  Source/prompt, native preview, scene tile payloads and conversion fingerprints
  are under assets/ui/title-bayveil. Its visible footprint is 116x63; two separate
  19-pixel eye regions use the existing pulsing color slot. This is title art,
  not a new obtainable species or an implemented legendary quest. The eighteen
  roster candidates and finished-monster counts are unchanged.
- Replaced the stock title creature's graphics and map within their original
  allocations. The first map removed the backing color used by the cloud blend,
  producing a black background; that failed preview is retained. Corrected code
  reserves thirty-two background tiles for an authored blue/teal row gradient,
  and maps only occupied silhouette tiles. Native eye-component, nibble-order,
  gradient/placement and resource-boundary checks pass. No palette changes or
  game-state forcing are needed; cloud animation and existing input remain intact.
- Corrected private target SHA-256:
  c4ff84b3e6859654cbed323ac83e6a7a784e7c36c3e31c867389cddfc1fee950.
  Graphics use 1,276 of 2,020 bytes; the map uses 460 of 768 bytes. Native/browser
  BPS reapplication and required source checks pass. A 4,608-frame cold route to
  Sunset/guide preserves both caught monsters and save data, matching native/WASM
  RGB/Flash/all 5,056,128 stereo pairs. Evidence: bayveil-final-native-cold-guide.
- Matched private review: bayveil-paired-title-review/comparison.mp4, 40.18 seconds,
  2,400 frames per side, native mGBA 0.10.5, equal nearest-neighbor 3x scale.
  Left is the supplied Emerald reference; right is the corrected SF preview.
  Metadata includes both ROM/core identities and hashes. Audio uses the SF clip's
  currently inherited title track. User feedback is requested for logo/silhouette/
  layout art only; it does not approve the soundtrack or a full quality domain.
- Public 0.0.17 remains unchanged while normal compilation/recovery is pending.
  Title clouds/footer/music, complete slice polish and every full-game gate remain
  open. Approved full domains stay 0/11. No GitHub workflow was dispatched.

Foglight Overture — original native title-music checkpoint:

- Authored an original thirty-two-bar, eight-track title theme: melodic lead,
  answering/plucked lines, arpeggio, bass, triad pad and three percussion parts.
  The form varies its main motif, lifts in register, rests the answering line
  in an eight-bar bridge and returns with a pickup into the loop. Editable score,
  generated MIDI and metadata are under assets/audio/foglight-overture*.
  Native monophonic-note, release and shared-loop marker checks pass.
- The native overlay uses the pinned MIDI converter/ARM data linker, retains the
  existing song-table/header address and fits the 1,988-byte sequence in its
  11,784-byte region. Header/track bounds and fixed-address tests pass. Every
  sample pointer and byte is verified against our original SF battle-bank PCM;
  the commercial title melody/instrument samples are not used by this theme.
- Private target SHA-256:
  9a68c513a8ebdad994a56ce9178166815a2fe7c38f74f72eda68827987168810.
  A 4,608-frame cold route reaches Sunset and the guide, preserves the caught
  party/save and matches native/WASM RGB/Flash/all 5,056,128 stereo pairs.
  Native/browser BPS reapplication and required source checks pass. This changes
  the title song only; approved/pending title artwork is preserved.
- An actual 18,000-frame native title capture advances the driver clock from
  561 to 14,481 with all eight score tracks active. Its 3,072-tick loop takes
  66.509 seconds on the GBA clock. The 53.5–255.5-second listening window contains
  three complete consecutive cycles; .tools/benchmarks/foglight-native-listening/
  {capture.pcm,three-loops.mp3,listening.json} retains clocks and provenance.
  Native PCM peak is 9,984, with zero clipped samples; RMS is -20.90 dBFS versus
  -20.54 dBFS in the forty-second Emerald title excerpt. No gain trick is applied.
- The reference title is a finite sequenced arrangement rather than this new
  loop. Complete reference-playthrough listening, human composition/mix review
  and real browser playback remain pending; loop/RMS checks do not establish
  Emerald-tier audio. Intro/other context music and the full sixteen-hub soundtrack
  remain required. Public 0.0.17 is unchanged while normal compilation/recovery
  is pending. All eleven full approvals stay pending; no CI run was dispatched.

- Extended the title-loop comparison through the full 18,000-frame listening
  capture: native/WASM final RGB, Flash and every one of 19,750,500 stereo pairs
  match, including repeated loop boundaries. Evidence: foglight-wasm-listening.
  PCM SHA-256: 86feb02da81eb08b9da8afd980b64b82426f80d843e10166ddafa00dda520370.
  Comparing the prior art candidate to this cartridge confirms every byte outside
  the declared title-song allocation is unchanged. Real browser playback and
  human soundtrack approval remain unproven.

Sunset rowhouse — original native world-art checkpoint:

- Added an original peach-stucco residential facade with projecting bay windows,
  a garage, teal trim and separate entry steps. Source/prompt and native 80x80
  conversion are under assets/tiles/sunset-rowhouse. The visible art uses fifteen
  opaque RGB555 colors plus transparency. Six existing five-by-five footprints
  receive the facade; these are decorative houses, not completed interiors.
- The first encoded sheet exceeded its original allocation and was rejected.
  The corrected private sheet removes unused tiles, retains the actual four road
  quadrants, and deduplicates ninety-one original facade tiles. It compresses to
  2,060 of 2,300 bytes. Mixed inherited tile/palette tables remain private.
  Only palette bank ten, twenty-five metatile records/attributes and the six
  facade block regions change. Collision/elevation bits, roads, events and save
  coordinates remain intact. Guards reject a second active SF map sharing the
  same secondary tileset without reviewing its references.
- Added explicit end-symbol bounds for the native block array, which has no ELF
  size field. Resource overflow/overlap, unrelated prior edits and map mismatch
  fail before writing. Reapplication is byte-identical; comparison against the
  preceding title/music candidate finds zero changed bytes outside the five
  declared house-resource allocations. Meaningful layout, road preservation and
  native quadrant-order tests pass, as does scripts/check.sh locally.
- Private 0.0.23 target SHA-256:
  43b3107493aa0e44b454047c61375730d35eac4fe18950cfb0d10affe74f2428.
  Native Flips and the browser BPS decoder reproduce exactly that cartridge.
  A 3,968-frame cold battery route reaches Sunset and stops at the house wall
  at (12,11), preserving the actual caught CinderCoy/BinPossum party and Flash.
  Native/WASM final RGB and all 4,353,888 stereo pairs match. Their raw frame
  alpha padding differs (native zero, WASM 255); RGB is checked independently.
- A subsequent controller-only 576-frame walk shows wall collision, walking and
  camera scrolling to the second facade at (22,15). Every RGB frame, Flash and
  all 632,016 stereo pairs match native/WASM. Evidence is in
  .tools/benchmarks/sunset-rowhouse-{native,wasm}-{cold-east,walk}; the native walk
  has a 9.64-second review.mp4. This is an implementation clip, not a matched
  Emerald comparison, performance gate or human art approval.
- Public 0.0.17 remains unchanged pending a verified normal rebuild. Distinct
  facade variants, original streets/terrain, detailed interiors and complete
  neighborhood map design remain unfinished. All eleven full domain approvals
  stay pending. No GitHub Actions workflow was dispatched.

Native Mac compilation — complete source-build checkpoint:

- Built the pinned old/normal/ARM compiler variants as native Mac executables
  in separate work directories and a fresh .tools/pokeemerald-host checkout.
  No commercial/compiler C or assembly was changed. Cleanup actions preserve
  intermediates; make commands have ninety-minute deadlines. The Docker checkout
  and prior verified cartridges remain intact. Our obsolete stalled capture CLI
  processes were stopped; Docker Desktop/storage was not force-quit or reset.
- The fresh host baseline reproduces the pinned reference exactly: SHA-1
  f3ae088181bf583e55daf962a92bb46f4f1d07b7; SHA-256
  a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af.
  Compiler/library hashes, tool versions and actual baseline bytes are checked
  before reuse. Proof is in .tools/pokeemerald-host/sf-host-build.json and
  .tools/romhack-baseline/build-host.json. This verifies a fresh base build, not
  all complete-game clean-build/quality gates.
- build_probe.py --backend host compiles the entire SF source overlay and applies
  the original text, guide/title art, title music and house-resource stages.
  Drafts retain immutable private cartridge/ELF pairs. Public release output
  contains only the patch and integrity manifest. A second source build produces
  the same target fingerprint. The prior private preview no longer substitutes
  for normal compilation; this new target comes from the normal source pipeline.
- Compiled 0.0.24 target SHA-256:
  fe17001af73fd6f6cb989323e418bc3880ee15fbd3bf0bdd75211f451a5f9de6.
  Patch: 673,686 bytes, SHA-256
  9a936ec4a4c2b0fbe652e13a985886712f7a5828085b80c5119b76e3e40f7567.
  Native Flips reapplication is byte-identical; required local source checks pass.
- A 4,608-frame cold caught-party route reaches the guide and preserves both
  monsters/save. Native/WASM final RGB, Flash and all 5,056,128 stereo pairs match.
  The established 71,038-frame first-gym route earns the badge with CinderCoy
  level eleven, HP 4/31, money 4,000 and three Potions. Final RGB, Flash and all
  77,946,444 stereo pairs match native/WASM. Evidence uses host-slice-* benchmark
  directories. This is one Fire-starter strategy, not three fresh campaigns.
- Public deployment of this normally compiled preview is being prepared.
  All eleven full approvals and the remaining full SF campaign gates remain
  open. No GitHub workflow was dispatched.

- Published the normally compiled 0.0.24 preview through Sites, preserving public
  access. Site version 18; source 3407da2ffd289b60a1d30112bbafb6e3f4c46656;
  saved version appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_f783e2d8a9948191a2e9ac87cbc7da6e;
  deployment appgdep_6ac763d5aa548191b845061849342671 reports succeeded at
  https://sf-mini-monsters.devkunjadia03.chatgpt.site. The archive contains our
  patch/manifest, emulator, site output and earlier standalone homebrew cartridge;
  no inherited full cartridge is packaged. Native save/deploy identifies eighty-
  four deployment files. Build output from the previous Site is preserved.
- Hands-on fresh in-app browser verification loads the local base, renders the
  SF title and downloads a 16 MiB cartridge matching the compiled target SHA-256.
  Evidence: .tools/browser-review/public-v24{.json,-title.png}; downloaded file
  is /Users/devkunjadia/Downloads/sf-mini-monsters (2).gba. The browser download
  event API times out, but the completed file's timestamp/size/hash verify the
  actual UI download. The initial Chrome Guest reload produces an empty view;
  a fresh in-app browser loads and patches successfully. This is not a measured
  performance result or proof of the complete campaign.
- The public sign-in link reaches the expected OpenAI account login after
  automatic security verification. The browser has no authenticated account
  session; the user is asked to complete login before /play can be verified.
  No credentials are requested in chat and no auth bypass is used. All full
  quality approvals remain pending. No GitHub workflow was dispatched.

Sunset streets — original compiled terrain checkpoint:

- Added eight original asphalt/sidewalk/curb/corner/lane/crossing/drain source
  tiles under assets/tiles/sunset-streets. Native conversion uses one RGB555
  palette and derives eighteen orientation variants. Adjacency selects outer
  and concave junction corners; lane/crossing/drain details use the existing
  street grid. This improves the map art, not the count of finished adventures.
- The complete owned house/street sheet uses 161 unique tiles. Normal source
  compilation declares 192 secondary tiles (6,144 raw bytes), rather than forcing
  new art into the old 159-tile allocation. Native compression is 2,896 bytes,
  matching its newly compiled allocation. Lossless codec/ELF/bounds checks pass.
  No inherited tile pixels are included in this secondary sheet; original
  primary ground/beach/fence art and the rest of the map library remain pending.
- All 329 road blocks select native curb/lane variants while retaining collision
  and elevation bits. House footprints, sign, NPC/warp coordinates and routes
  remain intact. The older road ID aliases our asphalt, and the existing authored
  map-resume guard refreshes old saved views. Unit checks cover orientation,
  road-only differences, junctions, capacity/palette separation and the alias.
  scripts/check.sh passes locally. No database change or GitHub CI run is used.
- Normally compiled private 0.0.26 target SHA-256:
  67e1ff17e5ce53083b2db72914735c97267a70982b05b3671438043dbe92eab9.
  Old caught-party battery reaches (18,22); native/WASM final RGB, Flash and all
  4,586,504 stereo pairs match across 4,180 frames. Subsequent four-direction
  walk/run footage matches every RGB frame, Flash and all 2,282,280 stereo pairs
  across 2,080 frames. Its camera/controller trace is unchanged from the courier
  candidate, and it returns to (18,22) with the same party/items/money/flags.
  Evidence: streets-{native,wasm}-{cold-to-road,four-direction-motion}.
- Native review.mp4 is 34.82 seconds. It is an implementation clip, not a matched
  full world-design approval or real-time performance result. Original grass,
  beach/fence/sign details, distinct facade variants, named cast and interiors
  still require work. The first-slice and all eleven full quality approvals
  remain pending. Public 0.0.24 is unchanged at this checkpoint.

- Published courier/street source build 0.0.26 through Sites. Site version 19;
  source 1debecb50e3e5b2a94853c77de97491ea1c82ab1;
  saved version appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_e28eda0e73d48191833498c2f8016787;
  deployment appgdep_6ac77a3d99d881919451e287f6bc95bc reports succeeded at
  https://sf-mini-monsters.devkunjadia03.chatgpt.site. The deployment archive
  verifies the patch hash and contains no inherited full cartridge.
- Fresh in-app browser loads the local base and downloads a 16 MiB cartridge
  matching the source-built target. Evidence: .tools/browser-review/public-v26.json;
  actual download /Users/devkunjadia/Downloads/sf-mini-monsters (3).gba.
  The old caught-party backup is accepted and reaches the Continue menu with
  two catalog entries/zero badges. Browser field resume is visually confirmed with the new courier and roads;
  the party view shows CinderCoy level five HP 13/19 and BinPossum level three
  HP 15/15, matching the imported backup. Screenshots: public-v26-{resume,party}.png
  under .tools/browser-review. Native/WASM recorded routes are verified separately.
  No human art score, signed-in completion or performance pass is inferred.


Courier apartment / Sunset mini-adventure checkpoint (October 8, 2026):

- Source follows art checkpoint 0ac1c33. Added one enterable studio to the
  Sunset rowhouses, authored collision and reciprocal door/exit warps; five
  other houses remain decorative. New art uses its own native secondary
  tileset and palette. Initial gameplay exposed an opaque foreground layer
  hiding the courier; corrected all room cells to the native covered layer.
- Optional adventure: observe fog, reject or correct a cached indoor forecast,
  receive one capsule, rest the party, read an N-Judah postcard and revisit the
  beacon. Reserved VAR_GIFT_UNUSED_3 (0x40E0) stores states 0–3. Reward is
  deferred when the bag is full. After the Build Badge, dialogue foreshadows the
  habitat signal; this is a clue, not a completed villain/legendary arc.
- Native controller evidence: apartment-native-window, -refused, -rest,
  -postcard, -exit, -return and -battery-resume under .tools/benchmarks.
  Refusal preserves state 1; completion/re-entry/resume preserve state 3 and
  exactly one Great Ball. Rest heals CinderCoy from 13/19 to 19/19 HP and
  Scratch from 32 to 35 PP. Exit returns to Sunset (16,9); re-entry succeeds.
  In-game SAVE, then cold boot from its actual Flash file, resumes inside the
  apartment (7,4) with the healed two-monster party and earned reward.
- Full route: 18,236 controller frames in apartment-full-route.csv. Native
  apartment-native-full-route and WASM apartment-wasm-full-route yield
  identical final RGB, 20,009,448 stereo sample pairs (80,037,792 PCM bytes)
  and 128 KiB Flash. Receipt: native capture's comparison.json. This trace
  does not verify every rendered frame or real-browser deadline/input/audio
  performance. Native-to-WASM cold battery resume also matches PCM/Flash and
  preserves the quest; it does not count as ten release round trips.
- Full scripts/check.sh passed locally; 14 map tests include path reachability
  for every apartment interaction and both door endpoints. Native art checks
  protect the sprite layer and exit behavior. The source cartridge compiles
  normally and its BPS round trip is byte-identical; target 5e05f1bdb9b2b635c31672f3497870fb1ac993053a2d16d3318201b507965186.
- Still required: authored door opening animation, matched human room/quest
  review, full-bag runtime branch, earned post-gym revisit, public publication
  and hands-on web checks. This adds detail to the first slice; no additional
  hub or full quality domain is approved. All 11 full approvals stay pending.
  GitHub Actions was not dispatched; normal checks and captures ran locally.


Courier apartment publication checkpoint:

- Release source 9afdaa9; public version 0.0.27-courier-apartment-preview.
  Patch 696,691 bytes; SHA-256 e5bebe18dbe6aff169463af4b9363a5b58efe7091d8bc0eb0aca7eb00ca73482.
  Target remains the locally tested 5e05f1bdb9b2b635c31672f3497870fb1ac993053a2d16d3318201b507965186.
- Site source 541f6fc1f57341a5cdd291031e2a22f84648fb7d, saved version 20
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_5176fbea04788191910549c908528648.
  Deployment appgdep_6ac788f052c0819190cfc68dc3c4586e succeeded at
  2026-10-08T12:13:44Z. Public URL remains
  https://sf-mini-monsters.devkunjadia03.chatgpt.site.
- Local archive audited for target/patch hashes and exclusion of full inherited
  cartridges; Sites accepted 84 deployment files. No DB migration, audience
  change, recurring monitor or GitHub workflow was used. Public hands-on
  load/download/apartment-save checks follow; sign-in still awaits user login.


Public apartment hands-on check:

- Existing public IAB tab reloaded; the supported base ROM patched locally.
  Actual Download GBA ROM produced Downloads/sf-mini-monsters (4).gba, 16 MiB,
  SHA-256 5e05f1bdb9b2b635c31672f3497870fb1ac993053a2d16d3318201b507965186.
- Imported apartment-native-saved/capture.sav through Import save. Continue
  entered the original room at the beacon and displayed completed-quest
  dialogue. Screenshot .tools/browser-review/public-v27-apartment.png shows
  the live game with public page context; receipt public-v27.json records the
  download and import checks. This is hands-on guest play, not signed-in QA.
- User login, matched review, door animation, bag-full and earned post-gym
  branch checks remain required. Full campaign/quality/performance/save gates
  stay open. Routine validation stayed local; no Actions run was dispatched.


Original rowhouse doorway checkpoint:

- Added three original 16x32 door-opening stages using the built-in imagegen
  tool and our own rowhouse crop. Source and exact prompt are in
  assets/tiles/sunset-door. Technical conversion preserves aligned columns
  and uses the existing 16-color house palette; source-quality review is pending.
- Source compilation registers a 768-byte native animation and palette bank 10
  for Sunset door metatile 635. The engine's opening/closing frame tables,
  sound, warp control and task timing stay intact. A narrow Sunset-only camera
  drawing hook puts the two animated cells on the same layer as the facade.
  Other native door drawing keeps its original path. The first capture exposed
  inconsistent fog lighting; a whole-facade fog experiment washed out the art
  and was rejected. The final candidate preserves the facade's existing colors.
- Actual open/enter/exit route ends outside at Sunset (16,9); matched reference
  route ends outside Littleroot (5,9). Both start outside facing west and use
  door-open-exit.csv. First 70 frames' normalized camera Y deltas match exactly.
  Captures from the earlier incorrect indoor start and fog experiment are
  diagnostic only; they are excluded from the review and acceptance evidence.
- Native/WASM door-layer-{native,wasm}-open-exit captures: all 464 RGB frames,
  2,036,496 PCM bytes and Flash match. This proves the recorded native/core
  route; it does not prove real-browser latency or the full performance gate.
  Compiled asset bytes match the original eight-tile-per-stage payload.
- 7.77-second matched clip: .tools/benchmarks/door-paired-review/comparison.mp4;
  equal nearest 3x scale, Emerald left / SF candidate right, SF audio. Receipt
  comparison.json records both inputs, targets and scope. A user review request
  is pending for doorway art/traversal only. Full domains remain 0/11 approved.
- Native-format tests reject malformed, overflowing or identical stages and
  independently check each 256-byte tile allocation. Full local checks pass.
  Latest target aac9091c9bc1a35a668829b0238d4d1edda98e1bd3449bca220985eac58a4afe;
  BPS round trip is byte-identical. Public version remains the apartment preview.
- Next: earned post-gym beacon return, full-bag runtime branch, original ground
  tiles and named cast art. The entire section 15 campaign and acceptance gates
  remain required. No GitHub workflow or recurring monitor was started.


Earned post-gym apartment branch checkpoint:

- Continued the existing 71,038-frame controller-only gym-victory capture on
  its original 0.0.24 target. Finished badge/TM dialogue and used in-game SAVE;
  apartment-earned-gym-saved/capture.sav is its actual Flash output.
- Cold resumed that file on the normally compiled 0.0.28 candidate. Build Badge,
  gym stage 4, 4,000 money, three Potions and CinderCoy level 11 with 4/31 HP,
  Leer/Growl/Ember/Quick Attack and their PP survive the upgrade. Returned
  through South Park and Muni to Sunset (28,22), then walked to the studio.
  The initial combined travel route hit a building; later controller segments
  corrected the route normally. No RAM/flag edits or scripted fixture was used.
- Observed fog, calibrated the beacon and claimed exactly one Great Ball.
  Re-interaction displays the earned post-badge text: someone is waking
  habitats / bigger than a lost parcel. State remains 3, badge and original
  party/money remain intact. Evidence: apartment-earned-after-badge/final.png
  and controller/state/Flash receipts under .tools/benchmarks. This verifies
  the branch and a clue, not completion of the antagonist or legendary arc.
- Doorway subset review remains pending. Full-bag deferred reward runtime
  verification and original terrain/cast work remain next. Full section 15
  approvals and campaign gates stay open; no GitHub workflow was dispatched.


Doorway preview publication checkpoint:

- Normally compiled release source 73ec36a, version 0.0.28-rowhouse-door-preview.
  Patch 703,552 bytes, SHA-256 aacfd85e2a42fe545e5884471c2ddd9e17855e7f09b5f95de2a79bc161b0c7f0;
  target aac9091c9bc1a35a668829b0238d4d1edda98e1bd3449bca220985eac58a4afe.
  The BPS round trip reproduces the tested cartridge exactly.
- Site source 713afcc658e43acb558af9976d75eaaa5fa6e46b; saved version 21,
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_87546bdaf0008191a34d13e6dd6b6d18.
  Deployment appgdep_6ac78f48bf2c8191b8ee7ad420fa642d succeeded at
  2026-10-08T12:40:48Z; public URL unchanged. Archive audit confirms patch
  identity and excludes full inherited cartridges; Sites accepted 84 files.
- The prior public apartment battery save cold-resumes on 0.0.28 at (7,4)
  with beacon state 3, the healed two-monster party, 3,500 money and three
  Potions. Evidence: door-v27-apartment-battery-resume. The earned 0.0.24
  gym upgrade and post-badge revisit are recorded separately above.
- No database migration, audience change, recurring monitor or GitHub Actions
  dispatch was used. Doorway review and every unapproved full quality/campaign
  gate remain open. Public download check follows; sign-in awaits user login.


Public 0.0.28 cartridge check:

- Hands-on local-ROM load completed on the published player. Actual Download
  GBA ROM produced Downloads/sf-mini-monsters (5).gba, 16 MiB, SHA-256
  aac9091c9bc1a35a668829b0238d4d1edda98e1bd3449bca220985eac58a4afe.
  Receipt: .tools/browser-review/public-v28.json. This is the same normally
  compiled cartridge used for native/WASM animation checks, not a browser-only
  adaptation. Real sign-in and full physical-device/performance gates stay open.


Public 0.0.28 resume follow-up:

- Continue on the actual published player resumes the existing guest save in
  the courier apartment. Screenshot .tools/browser-review/public-v28-resume.png
  includes the live game and public page context; public-v28.json records this
  alongside the exact downloaded cartridge hash. This proves the tested guest
  resume only, not signed-in play or the ten full release round trips.
- Doorway review remains pending, all full quality approvals remain 0/11,
  and the full campaign/acceptance objective remains active. Pushed commits
  were checked: GitHub still shows no new, queued or running Actions jobs.


Coastal terrain asset checkpoint (original source; not yet a playable release):

- Original 4x4 atlas authored with built-in imagegen using only our own SF
  house/street style inputs. Saved source, exact prompt, native atlas, RGB555
  palette and three wave stages in assets/tiles/sunset-terrain. No commercial
  game artwork was used as an input. Native cells remain candidates pending
  in-game and human pixel-art review; resized generated art is not approval.
- terrain_art.py converts aligned 16x16 cells, validates resource fingerprints,
  builds 256-byte ocean/shore stages and chooses railing/grass orientations.
  The remapper changes only low metatile IDs, preserving collision/elevation
  and event/save coordinates. Three targeted tests pass, including encounter
  patch and transit-sign positions. Native integration follows this checkpoint.
- This is first-slice polish, not another completed neighborhood. Borders,
  field-effect sprites, named cast and other first-slice art remain outstanding;
  public build stays 0.0.28. No approval score or acceptance count changed.


Coastal terrain native integration checkpoint:

- Source follows asset commit 3f44da2. The compiled secondary sheet grows from
  192 to 256 tiles, with palette bank 12 for coastal terrain. Ocean and shoreline
  reserve eight private VRAM slots (752–759), independent of static-art dedup.
  Three 256-byte stages advance every 16 frames through the native tileset DMA
  queue. House margins now use original SF lawn instead of inherited grass.
- Remapped 7 ground tokens into nineteen possible orientations while preserving
  collision/elevation and all event/save positions. Tall grass retains native
  encounter behavior. Sand now uses MB_SAND instead of the prior arbitrary
  southeast-blocking behavior; water uses MB_OCEAN_WATER. These are authored
  terrain corrections, not a claim that all movement behavior stayed unchanged.
- In-game coastline inspection exposed the old forest in camera padding west of
  the map. A Sunset-only visual selector continues ocean/surf/dune/lawn strips
  outside the rendered map. Field collision, connections and physical map data
  are unchanged by this selector. Independent C tests cover interior cells,
  both outside corners, strip edges and differently sized map bounds.
- Controller evidence: terrain-border-native-coast-ready and
  terrain-{native,wasm}-coast-waves. All 720 RGB frames, 3,160,080 PCM bytes and
  Flash match. Visible water has exactly three phases at a sixteen-frame cadence;
  static sand stays constant. Reserved VRAM matches an authored wave stage.
  Holding west stops at (4,8), preserving the blocked shoreline. Receipt:
  native capture's comparison.json; 12.05-second review.mp4 preserves native A/V.
- Walking the new dune grass produces a native wild BinPossum encounter
  (terrain-native-encounter/final.png). Old 0.0.27 apartment Flash cold-resumes at
  (7,4), beacon state 3, with the healed party, 3,500 money and three Potions
  (terrain-v27-apartment-resume). The doorway/apartment art remains intact.
- Full scripts/check.sh passes locally; native allocation tests protect mutable
  slots from aliasing even identical static pixels. Normal cartridge compilation
  and BPS round trip pass; target 3e1cff65075ce0e029c395998f73e61ab7f07bf0e2952229b684bb34605939c8.
  Source-only checks and recorded core routes do not prove physical-browser
  performance or Emerald-tier art approval. Full domains remain 0/11 approved.
- Remaining first-slice art includes field effects/footprints, battle player back
  poses, cast, the other maps and pixel cleanup. Full campaign remains required.
  No GitHub workflow or recurring monitor was started.


Coastal terrain publication checkpoint:

- Normally compiled release source a1e9b57, 0.0.29-coastal-terrain-preview.
  Target 3e1cff65075ce0e029c395998f73e61ab7f07bf0e2952229b684bb34605939c8;
  patch 718,122 bytes, SHA-256 b6de7cc182bb5b04e826f4165e11fec47a7ee8994ef93f2909dd88412d0a5f63.
- Site source d6a433052072b2608e7b08bcaca5734db8538fad; saved version 22,
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_5daa91dc89ec81919c0a9886a61e8d92.
  Deployment appgdep_6ac79774fcb0819191ef47de2565eb81 succeeded at
  2026-10-08T13:15:42Z; public URL unchanged. Archive audit checks exact
  patch/target identity and excludes full inherited cartridges; 84 files accepted.
- A staging copy initially used the Site directory instead of the game repo;
  its path was corrected before building and the archive's 0.0.29 target was
  independently verified. Public load/download/beach-save checks follow.
- In-game SAVE at the new coast produced terrain-coast-saved/capture.sav at
  (4,8), with the two-monster party, 3,500 money and three Potions preserved.
  Human art/performance and the full campaign gates stay open; no DB migration,
  audience change, recurring monitor or GitHub workflow was used.


Coastal foreground regression and correction:

- The public 0.0.29 screenshot exposed a presentation bug missed in the earlier
  native image review: opaque coastal ground on BG1 concealed the courier on
  sand. Equal native/WASM frames and valid saved positions did not prove a
  visible player. The 0.0.29 candidate is rejected for presentation; its earlier
  art/core checks do not establish approval. Saved data remains supported.
- Corrected roads/coastal ground to the native covered layer below field sprites;
  facades and doors retain their foreground layer. Sunset-only horizontal fog
  now uses a lighter 3/14 blend so ground artwork remains readable. Fog on other
  maps retains its original blend. Field collision, encounter behaviors and
  sprite priority rules are not changed by this rendering correction.
- New source-format test independently checks ground layers, sand/ocean/grass
  behaviors and foreground door flags. coastal_scene_check.py validates the
  documented standing-at-(4,8) beach capture: warm sand plus a visible courier
  silhouette. It rejects the actual 0.0.29 capture and passes the fixed capture
  with 132 dark sprite pixels across 23 rows. This detects the known regression;
  it does not grade art or generalize to arbitrary scenes.
- Fixed target e071e78c2ca5938a577eb7f65132c9ac7b482914d4bd7c321d77275bc0bb1505,
  version 0.0.30-ground-layer-fix-preview, builds normally with exact BPS round
  trip. terrain-fixed-{native,wasm}-waves match all 720 RGB frames, 3,160,080
  PCM bytes and Flash; the final visible-courier check passes. Full local checks
  pass. Walking visibility and replacement public publication follow.
- No approval was carried forward from the faulty ground rendering. All full
  quality scores stay unapproved; the full section 15 objective stays active.
  No GitHub workflow was dispatched.


Walking visibility regression verification:

- terrain-fixed-native-walking records three controller-driven 2x1 beach
  rectangles and returns to (4,8). The scene check passes all 768 frames with
  at least 115 dark sprite pixels across at least 21 rows. Actual images show
  the complete courier during standing and walking. Visibility is now checked
  explicitly in addition to native/WASM agreement and saved coordinates.
- 12.86-second fixed walking clip: .tools/benchmarks/terrain-fixed-native-walking/review.mp4.
  Its visibility.json records per-route minima. This is a regression check,
  not a user art approval or the complete reference/performance gate.
- Source f136bed; replacement public version 0.0.30 uses the already tested
  e071e78c2ca5938a577eb7f65132c9ac7b482914d4bd7c321d77275bc0bb1505 target.
  Full section 15 scope remains unchanged; no Actions workflow was dispatched.


Ground-layer fix publication checkpoint:

- Release source f136bed, version 0.0.30-ground-layer-fix-preview.
  Target e071e78c2ca5938a577eb7f65132c9ac7b482914d4bd7c321d77275bc0bb1505;
  patch 745,165 bytes, SHA-256 61997aa35e928c599edff8128e31bf4d3793d5ab00cc7aa6244687a9542a2a47.
- Site source 10c15c95664b6027f392f547cecf7ae68d09613d; saved version 23,
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_d7e4dc5c403c8191938e333ea2e4c43a.
  Deployment appgdep_6ac79dd18734819197e0be83c66d0422 succeeded at
  2026-10-08T13:42:50Z. Archive target/patch hashes independently checked;
  no full inherited cartridges included, 84 files accepted. Public URL unchanged.
- Replaces the faulty 0.0.29 presentation while preserving its valid save data.
  Hands-on public standing/visibility/download checks follow. Human approvals,
  account sign-in, physical performance and full campaign gates remain open.
  No GitHub workflow or database operation was used.


Fixed coastal public visibility and battery-transfer check:

- Hands-on public loading produced Downloads/sf-mini-monsters (7).gba, 16 MiB,
  SHA-256 e071e78c2ca5938a577eb7f65132c9ac7b482914d4bd7c321d77275bc0bb1505.
  Continue resumes the existing coast save with the courier visibly standing
  on the sand. Screenshot .tools/browser-review/public-v30-coast.png includes
  the public game/page context; public-v30.json records the exact download.
- Public Save backup produced Downloads/sf-mini-monsters.sav, 128 KiB,
  byte-identical to terrain-coast-saved/capture.sav (SHA-256
  0d755458f2c2fd1fed247aab5f11e123e86fcf6269aac050311732c6e0a42db9).
  Copied that actual download into local evidence and cold-booted it natively:
  terrain-public-export-native-resume returns to (4,8), same two-monster party,
  HP/moves/PP, 3,500 money and three Potions. The visible-courier check passes.
  Receipt public-v30-save.json documents the exported-file identity.
- This verifies one guest checkpoint transfer, not ten consecutive final-release
  round trips, all campaign checkpoints or signed-in play. Source/runtime art
  reviews and the full campaign/performance/acceptance gates remain required.
- No new, queued or running GitHub Actions jobs appeared after pushing source;
  tests, compilation, captures and site packaging ran locally.


South Park original asset checkpoint:

- Replaced the planned institutional facades with original warehouse/clinic
  art, saved under assets/tiles/south-park-buildings with the exact built-in
  imagegen prompt. Native size is 112x80 per facade; separate palette banks
  preserve brick/stone colors. These are fictional SF venues, not exact offices.
- Original bench, planter and information board are in
  assets/tiles/south-park-furniture. Native 16x16 conversion shares the existing
  original lawn palette. All images remain unapproved art candidates.
- park_art.py converts/validates these resources and packs four-bit metatiles
  into at most 512 secondary VRAM tiles. Three native-format tests pass:
  aligned facade/door cells, independent palette/layer flags on deduplicated
  graphics, and allocation overflow rejection. Generic street edge selection
  now supports authored road tokens; existing Sunset street tests still pass.
- Integration follows. Public 0.0.30 and all approval counts stay unchanged.
  No GitHub workflow, DB change or delegated agent was used.


South Park standalone world integration (private candidate):

- Source follows bf89077. Added gTileset_SFSouthPark, built entirely from original
  roads, lawn, railings, furnishings and SF facades. 469 native secondary tiles,
  122 metatiles and five separate palette banks fit below the eight slots reserved
  for native door animation. Ground uses covered layers below field sprites;
  vertical facades use foreground layers. Margins reveal original sidewalk.
- Replaced indoor-floor street graphics with asphalt/curbs/center markings and
  distinct sidewalk. Original meadow, benches, planters and boards define the
  park. Annexes reuse a technically resized original SF rowhouse candidate;
  pixel cleanup and all art approval remain pending.
- New facade lower walls close twelve former sidewalk cells; center entrance
  coordinates (13,5)/(32,5), all NPCs, transport, history and discovery locations
  stay connected. Four native/resource tests pass, including complete map
  allocation, sprite layers and path reachability. Existing saved coordinates
  blocked by new foundations must use the established same-map recovery guard;
  actual older-save verification follows. Save schemas are unchanged.
- First source build 0.0.31-south-park-preview, target
  e63e59539fca4af983c1d80a7ba4830a0a737457741ec9b25001270fb5c92209,
  compiles normally with exact BPS round trip. Doors are initially native fades;
  original opening frames are being integrated before publication.
- This remains first-slice polish. Public build is 0.0.30 and full domains stay
  0/11 approved. No CI workflow, database change or delegated agent was used.


South Park native doors and older-save recovery checkpoint:

- Added original three-stage warehouse/clinic door frames in
  assets/tiles/south-park-doors with their exact built-in imagegen prompt.
  Six 16x32 frames use the existing facade palettes. Each door compiles to
  exactly 768 original bytes; compiled ELF/cartridge allocations match those
  bytes. Native opening/closing timings and warp logic remain unchanged.
- Registered metatiles 583/618 and matching upper cells in the foreground door
  drawing hook. Transparent animated margins reveal our own sidewalk; Sunset
  doors reveal original lawn. Other map door drawing retains its native path.
- Actual 0.0.30 in-game SAVE at South Park (11,5), newly occupied by a
  foundation, cold-resumes on 0.0.31 at adjacent sidewalk (11,6). Build Badge,
  gym stage 4, 4,000 money, three Potions and CinderCoy level 11, HP 4/31,
  moves/PP survive. Evidence: park-old-foundation-saved and
  park-new-foundation-resume. No RAM/flag edits or DB migration were used.
- Gym entry/exit: park-{native,wasm}-gym-door-roundtrip, 616 RGB frames,
  2,703,632 PCM bytes and Flash identical; returns to (13,6). Clinic entry/exit:
  park-{native,wasm}-clinic-door-retry, 980 RGB frames, 4,301,216 PCM bytes and
  Flash identical; returns to (32,6). Source city/door images were inspected,
  with the courier visible outside and native interiors reached normally.
  Each native capture has comparison.json and a synchronized review.mp4.
- The first clinic recording failed when local storage filled; its partial
  files are retained and excluded from evidence. Verified lossless compression
  of completed captures freed 2,148.5 MiB, preserving every original frame.
  The successful retry has a distinct name. No user files were removed.
- New meadow/bench are reachable and the native Oran Berry reward executes
  (park-native-bench-discovery/final.png). Full local checks pass after the
  art tests use the project's Pillow-enabled Python environment. These routes
  do not prove physical-browser performance or human Emerald-tier approval.
- Final candidate target e1b4c66fd4eb1c5aa1731fdc18c7985e199791d3480ad90106d25bdbcc7574a4;
  source compilation/BPS round trip pass. Public build remains 0.0.30 until
  this candidate is published. Full quality approvals remain 0/11. First-slice
  cast/interior/battle art and the complete campaign remain required; no CI ran.


South Park public release checkpoint (October 8, 2026):

- Normal build 0.0.31-south-park-preview, source 18b68f9, verifies byte-exact
  target e1b4c66fd4eb1c5aa1731fdc18c7985e199791d3480ad90106d25bdbcc7574a4.
  BPS patch is 759,406 bytes, SHA256
  51ce40ffc5fec101dabdb35395e8537c1870c5d866c5f91e2cc787eb1492ee5c.
  Source dirty marker reflects retained unrelated/untracked local files.
- Native bench discovery save at (18,20) records reserved flag 0x41 set and
  three Oran Berries (item 139). Earned badge, gym stage 4, 4,000 money, three
  Potions and level-11 CinderCoy HP 4/31 survive the actual in-game SAVE.
  Evidence: park-discovery-saved; read-only encrypted-party/inventory decode.
  Public import/cold resume verification follows; this is not a full campaign
  checkpoint or proof of ten cross-platform round trips.
- Site source a9280a3aca53d62972b8ad0627c564476932a25a passes TypeScript and
  production build. Archive verified against exact patch/target manifest,
  with no inherited BPEE cartridge. Saved Site version 24:
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_ef72738c7ae48191be72c40c69f22297.
  Deployment appgdep_6ac7ae2a2798819181a01e709a8a1c3c succeeded at
  2026-10-08T14:52:36Z, retaining public audience and local-only ROM patching.
- All full quality approvals remain 0/11. Pending comparison reviews, signed-in
  QA, first-slice original cast/interior/battle art and the complete campaign
  remain required. No database migration, recurring job or GitHub Actions run
  was used. Last turn verified remote manual-only triggers and no active/queued
  jobs; this turn publishes the already locally verified candidate.


South Park public hands-on verification:

- Public Site version 24 loads/patches the local base ROM normally. Actual browser
  cartridge download `sf-mini-monsters (8).gba` has exact target SHA256
  e1b4c66fd4eb1c5aa1731fdc18c7985e199791d3480ad90106d25bdbcc7574a4.
  Imported park-discovery-saved battery resumes at (18,20), with the courier
  visible beside the original park bench, meadow, planters and annex facades.
  Screenshot: .tools/browser-review/public-v31-south-park.png; structured
  release evidence: public-v31-south-park.json in the same directory.
- Actual public Save backup produces 131,072 bytes identical to the native
  imported battery: SHA256
  50d85a8b78a22a9e05a535a38de8d3be0a66bfa48128194b550dd8687717b2f7.
  Controller-only native cold resume (park-bench-cold-resume) verifies (18,20),
  discovery flag 0x41, three Oran Berries, three Potions, 4,000 money, earned
  Build Badge/stage 4 and level-11 CinderCoy HP 4/31 with its four moves/PP.
  This validates one guest checkpoint, not the final ten-round-trip gate.
- Original outdoor art now replaces the borrowed South Park terrain/facades.
  Sparse composition, resized-pixel cleanup, remaining inherited field effects,
  named cast sprites and interior art still need improvement and matched user
  review. Approval stays unreviewed, with 0/11 full domains accepted.
- Source/art/release commits bf89077, 21cca90, 18b68f9 and 784c19f are pushed.
  The latest GitHub Actions run remains 37731870689 from 05:20:22Z, with no
  new workflow caused by publication or pushed commits. All checks ran locally.
  Sign-in QA remains pending the user's existing login handoff. Full section 15
  scope and all remaining campaign, mechanics and performance gates stay active.


Cognition original field cast candidate checkpoint:

- Added original field-sprite sheets for Scott Wu, Walden Yan and Steven Hao,
  generated with built-in imagegen. Each source and exact prompt is saved under
  assets/characters/cognition-cast/{character}. Fictional costumes distinguish
  navy jacket, green jacket and gray top/glasses. Likeness and art are unreviewed.
- Native conversion preserves nine 16x32 frames per character, consistent feet
  baseline, idle/two footsteps for south/north/west and mirrored east. One
  shared 16-color palette avoids competing colors in the three-person gym.
  Registered tag 0x1125, native special NPC slot and reflection pairing; unused
  native graphic slots 76–78 are reserved. Save format and dynamic IDs stay fixed.
- cast.json assigns data-driven graphics aliases to the existing three NPCs.
  Their locations, dialogue, trainer sight, battles and progression stay intact.
  Trainer battle portraits and other named cast still use placeholders.
- Three native tests pass: independent cartridge nibble/tile decoding, shared
  palette and distinct pose cycles; malformed atlas rejection; stale palette
  rejection before engine writes. Full local checks pass. Source build target
  311642145d16a51a0eff63cdb13b0799771f8d48f29c79ad73fc045bda45f780 compiles
  normally and the 764,680-byte BPS applies byte-identically. Actual controller
  routes, rendered native sprites and cross-runtime confirmation follow.
- This is first-slice pixel-art/NPC progress. All full domains stay 0/11 approved.
  Source images resized into native candidates still need pixel cleanup and
  matched user review. Public build remains 0.0.31 until publication verifies
  the new candidate. No CI workflow, DB operation or delegated agent was used.


Cognition cast rebuild and native rendering verification:

- A second source compilation exposed duplicate cast frame declarations.
  The cast overlay now restores its own pointer/frame headers from the pinned
  engine before appending records, while preserving courier/map-owned headers.
  Corrected normal build succeeds and reproduces target
  311642145d16a51a0eff63cdb13b0799771f8d48f29c79ad73fc045bda45f780.
  No broken candidate was published. Further consecutive-build check follows.
- Controller-only older-save entry reaches the gym with earned badge/stage 4,
  CinderCoy level 11 HP 4/31, four moves/PP, 4,000 money and three Potions intact.
  Existing scripts station Scott at (8,3) after delivery; this behavior is retained.
  cast-native-room-view shows all three new sprites with the courier at (8,7).
- cast-{native,wasm}-gym-dialogue-review has 2,932 identical RGB frames,
  12,868,544 identical PCM bytes and identical Flash. Its 49.09-second native
  A/V clip and route-contact.png were inspected. It exercises Scott's return
  dialogue but movement during text pacing misses later intended approaches;
  it is explicitly not evidence of completed three-person dialogue coverage.
  Corrected close/dialogue route reaches the room overview normally.
- Native capture compression preserves every original frame and frees
  441,738,648 bytes. Actual browser, newer in-game save and publication checks
  follow. Native rendering/rebuild evidence does not replace matched Emerald
  approval, physical-browser performance or complete campaign gates.
  Human approvals remain 0/11; no GitHub workflow or DB operation was used.


Cognition cast public publication checkpoint (October 8, 2026):

- Corrected consecutive source builds reproduce target
  311642145d16a51a0eff63cdb13b0799771f8d48f29c79ad73fc045bda45f780.
  Published BPS is 764,680 bytes, SHA256
  45d5bc8f6f449fa35d50d342469030507f3eb54a79c4f439582d240a704102da.
  Immutable manifest retains its first successful candidate source receipt
  d39da11 with dirty marker; repeat-build fix d754113 produces identical bytes.
  The source registry/frame tests and full local checks pass after the fix.
- Actual native SAVE at gym (8,7), cast-room-saved, cold-resumes at (8,7)
  in cast-room-cold-resume with all three new sprites and earned badge, stage,
  party, moves/PP, money and Potions intact. Public browser verification follows.
- Site source efa06a7f9049637a12fd563907f64c28923486f5 passes TypeScript and
  production build; its archive contains the exact patch/manifest and no
  inherited cartridge. Public Site version 25:
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_74620fdeb9f881918abb0571c60b50b5.
  Deployment appgdep_6ac7b3bef1208191870777e942de79d1 succeeded
  at 2026-10-08T15:16:23Z, retaining the public audience/local ROM patching.
- Full quality approvals stay 0/11. Field sprites remain likeness/art candidates;
  battle portraits, other named cast, original gym/clinic interiors and their
  matched reviews remain outstanding. This does not complete the NPC/pixel-art
  domains or the first-slice acceptance gate. No CI workflow, DB migration or
  delegated agent was used. Full section 15 campaign/system scope stays active.


Cognition cast public hands-on verification:

- Actual public cartridge download `sf-mini-monsters (9).gba` matches target
  311642145d16a51a0eff63cdb13b0799771f8d48f29c79ad73fc045bda45f780.
  Native gym battery cast-room-saved imports and resumes at (8,7), showing
  Scott, Walden and Steven's original sprites together. Public screenshot:
  .tools/browser-review/public-v32-cognition-cast.png; structured evidence
  public-v32-cognition-cast.json in the same directory.
- Actual Save backup is 131,072 bytes identical to the imported native battery,
  SHA256 0d815344d5da4c9166efcb589955ee954c51fec041b0fb6a0e53cedf7fa67494.
  That battery independently cold-resumes natively with the preserved earned
  team/badge state. This is one guest checkpoint, not ten final round trips.
- Browser import initially showed white without console errors. Pause/Resume
  reached the native Continue screen and resumed the correct room normally.
  Cause and browser boot/frame pacing remain unverified; investigate before
  final release acceptance. Do not infer performance/input gates from this QA.
- First GitHub push terminated with HTTP 408; remote API confirmed old HEAD.
  HTTP/1.1 retry succeeded, and remote API confirms source 218beb3. No workflow
  was triggered: the latest Actions run remains 37731870689 from 05:20:22Z.
  Source/art/rebuild/publication are committed in d39da11, d754113 and 218beb3.
- Signed-in QA and existing user comparison reviews remain pending. All 11 full
  domain approvals remain outstanding. Next work follows the current table;
  the complete SF campaign and every section 15 gate stay required.


Browser import investigation, first checkpoint:

- Previous goal turn made source/art/publication progress (d4d61e6 and prior
  cast commits), with actual downloaded-ROM and native/public save evidence.
- Reimporting cast-room-saved into the running public Site 25 advances through
  the native copyright/intro normally without Pause/Resume. The document reports
  visible; no repeat white-screen stall is proven in this warm session. The
  earlier first-load observation remains unresolved, not silently cleared.
- Corrected Emerald save-restoration prompts: press Start at the title screen,
  then choose Continue. The prototype's existing A prompt stays intact.
  Added a DOM-only diagnostic data-emulator-fps on the canvas from the SDK's
  existing frame event. It reports executed core frames/second; it does not
  expose a new player-facing panel or establish the game deadline/input gates.
- TypeScript validation passes. A public build with the diagnostic/prompt change
  is being prepared so fresh-load/import frame pacing can be measured through
  the real browser, rather than inferred from a still screenshot. No ROM bytes,
  save format, DB state or quality approval changed. No GitHub workflow ran.


Public import diagnostics and original office checkpoint:

- Site source a29cf98c08ea8e5631cf66a41fdd4a100cb12ab0 passes TypeScript and
  production build. Saved Site version 26:
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_4d7a0421fbc88191838847e28f7c5878.
  Deployment appgdep_6ac7b7b242f481919547ed43fd25e569 succeeded at
  2026-10-08T15:33:14Z. ROM patch/target are unchanged and archive has no
  inherited cartridge. Source prompt/diagnostic change is committed in 66e327b.
- Fresh local ROM load restores the existing save, then a second import during
  initial boot reaches title, Continue and the gym without Pause/Resume.
  SDK executed-core-frame samples are 59.0, 59.9, 59.6, 60.6 and 59.6 fps.
  Screenshot: .tools/browser-review/public-v32-fresh-import-diagnostics.png.
  These samples are not the 99% game deadline, input p95 or audio trace gates.
  Earlier white display remains an unconfirmed one-time observation; no general
  stall is proven in this fresh/warm retry, and no scheduler fix is claimed.
- Added original modular office source/prompt and native derivatives under
  assets/tiles/cognition-office, generated with built-in imagegen. Sixteen cards
  provide floor/aisle/walls/windows, workstations, servers, plants, chairs,
  whiteboard, books, coffee, relay consoles, barrier, exit and storage.
  Native tileset has 319 tiles, 81 metatiles and one palette bank, below VRAM
  capacity. No inherited office pixels remain in this room candidate.
- Map adapter preserves collision/elevation and all existing story/NPC/event
  coordinates. Scripted open gate keeps floor record 0x202; south exit keeps
  MB_SOUTH_ARROW_WARP. Server terminal/whiteboard/coffee art aligns with the
  corresponding text interactions. Two native office tests and full checks pass.
- Initial candidate bfbae84d2f736c0a9fe2c38c52008c739834de5bb53003d292eb3e942a6acfec
  was inspected locally; aligned final target is
  0dfc69dc6b7473bd0dec180fec9f9603645693dfec41ffcc039e9ac0e5f0660f, with
  772,747-byte BPS byte-exact application. office-aligned-old-save-resume
  cold-loads the actual older gym battery at (8,7), preserving earned badge,
  stage 4, CinderCoy level 11 HP 4/31, moves/PP, 4,000 money and three Potions.
- office-{native,wasm}-exit-return: 1,024 identical RGB frames, 4,494,336
  identical PCM bytes and identical Flash; exits to South Park and returns to
  gym (8,6) with visible courier and preserved earned state. Native directory
  contains comparison.json, final.png and synchronized review.mp4. Verified
  lossless frame compression preserves every pixel and frees 153,998,111 bytes.
- Office art remains an unreviewed native candidate. This 17-second functional
  route is not a matched 30–60-second Emerald quality approval. Public office
  release/QA, pixel cleanup, clinic art, other cast/portraits/music and full
  section 15 scope remain required. Full approved domains stay 0/11. No DB
  operation, delegated agent, recurring monitor or GitHub workflow was used.


Office publication, matched review and user feedback:

- Normal release build reproduces office target
  0dfc69dc6b7473bd0dec180fec9f9603645693dfec41ffcc039e9ac0e5f0660f.
  BPS SHA256 55ca8fa888af23927fd541b14de8eb785fbe44a16f6100b0d73363cfd40b6468,
  772,747 bytes. Site source 9adae707b890ae8ffef7fc6742823f1e27670f06 passes
  TypeScript/build; exact archive contains no inherited cartridge. Version 27
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_1c745d412fac819199b2d526ffc280a5,
  deployment appgdep_6ac7bf1d1ae881918a97c707a827f37e succeeded at
  2026-10-08T16:04:54Z. Public audience and local ROM patching are preserved.
- Actual public cartridge download (10).gba matches the target; older native
  cast-room-saved battery resumes visibly in the new room. Public Save backup
  is byte-identical (131,072 bytes, SHA256
  0d815344d5da4c9166efcb589955ee954c51fec041b0fb6a0e53cedf7fa67494).
  Screenshot/receipt: .tools/browser-review/public-v33-cognition-office.{png,json}.
  Sampled core throughput 60.0 fps is not a complete performance gate.
- Produced 2,048-frame, 34.29-second paired interior walking clips with identical
  controller rows, native GBA timing and equal nearest 3x display. Emerald lab
  reference enters from the verified original-town doorway lineage; stock
  scene/ROM identity and empty starting party are inspected. It does not use
  a prepared evolution snapshot with cached SF map/weather. Both interior
  walks return to their starting positions. Scope is upper-office scene art
  and walking readability, not a full world/pixel-art/movement/audio domain.
- Corrected review: .tools/benchmarks/office-interior-paired-review-tracks/
  comparison.{mp4,png,json}. Its two audio tracks are labelled Emerald reference
  and SF candidate; the earlier package lacked MP4 track labels and is retained.
  Reference footage stays private. Added a guarded reusable private packager;
  three tests reject wrong reference/core, controller provenance, mismatched
  timing/input/resolution and too-short clips. Full local checks pass.
- User feedback on that exact clip: "the biggest gap is that sf maybe looks too
  gloomy and reuses the same sprites too much, the quality of the animation is
  good". No numerical score or 4/4 approval is inferred. Preserve the positively
  reviewed walking animation; brighten the room and diversify repeated props.
- First corrective native conversion splits floor/walls, furniture, plants and
  relays/boards across banks 6–9, with shared ground/outline colors. Versioned
  v2 derivatives preserve the old one-bank assets. Tests verify palette records
  and shared colors, with exit/gate/layer behavior unchanged. Draft target
  6216be102b6d52db9a7c11b872a0a69824907ccf8bc2da917fdaecc84d2ababd compiles
  normally and BPS applies exactly; brighter source/prop variation follows.
- Verified compression of three older completed recordings freed 1,036.2 MiB
  without losing frames. Both new complete comparison captures are also
  losslessly compressed. No files were removed, no DB operation or workflow
  was run, and all full-domain/campaign/system gates remain required.


Brighter office revision following direct user feedback:

- Built-in imagegen edited our own atlas into source-bright-v2.png. Exact edit
  prompt is saved in bright-prompt.md. Warm ivory floors/honey wood, clean blue
  carpet, vivid green plants and clearer relay details replace the gloomy cast.
  Original source and prior derivatives remain preserved. Strong alpha-band
  extraction ignores sparse gutter artifacts before native conversion.
- Current v3 conversion uses banks 6–9 with shared ground/outline colors. Four
  formerly identical workstation corners now use storage, desk, whiteboard and
  server equipment; secondary furniture arrangements also vary. Existing
  collision/elevation, NPC/event coordinates, exit/gate behavior and every
  courier/character animation resource remain unchanged.
- Draft 0.0.34-brighter-office-preview target
  3d03b45d6c9edef949ca7b7c3b4933f124cf5d5149d2f105922d442840d2acad compiles
  normally; 773,937-byte BPS applies exactly. Native old gym save resumes at
  (8,7) with visible courier, earned badge/stage 4, 4,000 money, three Potions
  and CinderCoy level 11 HP 4/31, four moves/PP preserved.
- brighter-office-{native,wasm}-exit-return: 1,024 identical RGB frames,
  4,494,336 identical PCM bytes and identical Flash. Returns to gym (8,6).
  Full local checks pass, including native palette/shared-ground/room/event
  coverage and guarded paired-review tests. A new same-input 2,048-frame
  interior clip returns to (8,7); paired review packaging/publication follows.
- This addresses the user's stated gloom/repetition gaps while preserving
  the positively reviewed walking animation. Numerical scores and full-domain
  approval stay unassigned; all 11 full approvals and the complete campaign/
  systems remain required. No CI workflow, DB operation or delegated agent ran.


Brighter office public publication:

- Normal release compilation from c9b19c4 reproduces target
  3d03b45d6c9edef949ca7b7c3b4933f124cf5d5149d2f105922d442840d2acad.
  BPS is 773,937 bytes, SHA256
  0c1b20a942daabb8db13fe300ef3be93c0875dbafaeedef88e4a41064b3fefb3.
- Site source 36b2afbeab02799f480892b2ad29729fc7c0a33f passes TypeScript
  and production build. Archive has the exact patch/manifest, no inherited
  cartridge. Saved Site version 28:
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_bf490b03ef4081919017577597f2d23b.
  Deployment appgdep_6ac7c985701881919069bbbaecba0877 succeeded at
  2026-10-08T16:49:18Z. Public audience and on-device patching are preserved.
- New paired evidence: .tools/benchmarks/brighter-office-interior-paired-review/
  comparison.{mp4,png,json}. Same Emerald lab capture, identical 2,048-frame
  controller sequence, 34.29 seconds and equal nearest 3x scale. SF walk returns
  to (8,7); updated still inspected for brighter ground, plant/furniture color
  and distinct corner arrangements. No courier/NPC animation asset or timing
  changed. This remains an office subset, not a full quality-domain approval.
- New native captures were losslessly compressed, preserving every frame and
  freeing 153,227,014 and 300,884,406 bytes. Native/WASM exit-return also verifies
  1,024 identical RGB frames, 4,494,336 PCM bytes and identical Flash.
- Direct user feedback and the positive animation note stay recorded. New
  numerical/full-domain approval remains pending. Old-save public QA follows;
  original clinic/cast portraits/music, all 16 hubs/eight gyms/150 creatures and
  every system gate remain required. No GitHub workflow or DB operation ran.


Brighter office public hands-on verification:

- Site 28 actual cartridge download sf-mini-monsters (11).gba is 16,777,216
  bytes and matches v34 target SHA256
  3d03b45d6c9edef949ca7b7c3b4933f124cf5d5149d2f105922d442840d2acad.
- Explicitly imported the older cast-room-saved battery; normal native intro,
  title and Continue resume visibly into the brighter office. Courier and
  three cast characters remain visible; ivory ground, blue aisle, plants and
  varied storage/desk/chairs/whiteboard/server arrangements are inspected.
- Actual public Save backup downloads sf-mini-monsters (4).sav and exactly
  preserves the 131,072-byte imported battery, SHA256
  0d815344d5da4c9166efcb589955ee954c51fec041b0fb6a0e53cedf7fa67494.
  Screenshot and structured receipt: .tools/browser-review/
  public-v34-brighter-office.{png,json}. This is one checkpoint verification,
  not completion of ten final campaign round trips. Sampled 60.0–60.5 core
  fps is not the deadline/input/audio performance gate.
- Requested a 0–4 art/readability score and remaining gap for the revised
  34.29-second office comparison. The prior positive animation feedback stays
  qualitative; no full quality-domain approval or numeric score is inferred.
- Release and source commits pushed successfully. Actions inventory still
  ends at completed run 37731870689 (2026-10-08T05:20:22Z); these pushes and
  Sites publication triggered zero new Actions jobs. No DB operation ran.


Original South Park clinic interior implementation:

- Added an original sixteen-card clinic source atlas and exact built-in imagegen
  prompt in assets/tiles/south-park-clinic. Bright ivory/teal recovery equipment,
  terminal, waiting chairs, manuals, supply cabinet, counter, plant and notes
  replace inherited lab furniture. This is first-slice art; approval is pending.
- Shared the deterministic interior conversion/installation helpers with the
  office; existing office derivatives are byte-unchanged. Clinic allocates
  320 native tiles, 81 metatiles and four secondary palette banks. Every cell
  uses the actor-visible floor layer. Original service scripts and animations
  are unchanged; collision/elevation bits and all event/warp coordinates remain
  intact. The terminal, notes and shop retain their authored interaction sites.
- All local checks pass; two focused native tests verify capacity, draw/warp
  behaviors, shared ground colors, installation paths and complete collision/
  elevation preservation. Initial v35 draft compiles normally and BPS applies
  exactly. An older earned save resumes with badge, stage 4, money, inventory
  and wounded party preserved, then reaches the new clinic at (6,12).
- Initial entry inspection exposed the old border record now pointing at the
  exit arrow. Explicit border_tile 512 replaces that repeated arrow outside
  the room; corrected draft compilation and healing/terminal/shop/exit/native-
  WASM checks follow. The two earlier street approaches stopped outside and
  are retained as diagnostic evidence, never counted as successful entry.
- No quality score is inferred from generation, native conversion or tests.
  Public release stays v34/Site 28; all full section 15 gates remain required.
  No GitHub Actions, DB operation or delegated agent ran.


Clinic native verification and matched review checkpoint:

- Corrected v35 target 0007ea7b1e2680de707e4bc300465f5ade39081c3154b583f0edb695ff046302
  compiles normally; 783,070-byte BPS applies exactly. Entering from the older
  earned campaign battery retains badge/stage 4, 4,000 money, three Potions,
  level 11 CinderCoy HP 4/31 and its four moves/PP. Entry reaches (6,12).
- Clinic native/WASM entry: 704 identical RGB frames, 3,089,856 identical PCM
  bytes and identical Flash. Healing: 400 identical RGB frames, 1,755,600 PCM
  bytes and identical Flash; HP becomes 31/31 and Ember PP returns to 25.
  Exit/re-entry: 576 identical RGB frames, 2,528,064 PCM bytes and identical
  Flash, ending (6,12). Receipts accompany the native captures under .tools/
  benchmarks/clinic-v35-*. These core comparisons do not prove browser timing.
- Generated a fresh 2,048-frame 34.29-second clinic walk from (6,8), returning
  there. Same original Emerald lab reference, exact controller sequence, GBA
  clock, nearest 3x scaling and two labelled audio tracks; private package
  .tools/benchmarks/clinic-v35-paired-interior-review/comparison.{mp4,png,json}.
  Candidate label is now configurable so the tool labels this scene SF CLINIC.
  No numeric score/full approval is inferred. Reference footage stays private.
- Complete entry and healing recordings and the complete walking retry are
  losslessly compressed. A first walk recording failed on full local storage;
  its partial output is preserved and excluded from review. One build log was
  also preserved as gzip. Native dialogue/PC/shop and a new saved clinic
  checkpoint are being exercised; public remains v34 until publication succeeds.


Clinic services and public release:

- Native controller checks reach storage boxes from the terminal at (2,3),
  the four-item priced supply list from Patrick, and the native Save prompt.
  No money/inventory changes occurred while browsing. A native SAVE at clinic
  (6,8), then cold resume, retains earned badge/stage 4, 4,000 money, three
  Potions and the wounded CinderCoy's level/moves/PP/HP. See clinic-v35-
  {terminal-menu,storage-boxes,shop-supplies,saved,native-saved-cold}.
- Normal release from c6098e7 reproduces the corrected draft target exactly.
  Public BPS SHA256 8d11323bf325d5ea7dc97a088922549eb07d30d43de1ae2e3694d752a67a4662,
  783,070 bytes. Website mirrors contain that exact release.
- Site source bfb7dd3a15688fb5afb5efcd4ee9e7e314e8fbca passes TypeScript and
  production build. Archive verifies exact patch/manifest and no inherited
  cartridge. Saved Site version 29:
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_b737da42a4a08191b583da696a5285c2.
  Deployment appgdep_6ac7d0789884819193e15676701e9459 succeeded at
  2026-10-08T17:18:58Z. Public audience and on-device patching are preserved.
- Public cartridge download and explicit clinic save import/export checks
  follow. Sign-in still awaits the user's login. Full-domain approvals stay
  0/11; existing office review remains pending. No CI workflow or DB operation
  ran; latest Actions inventory remains run 37731870689 from 05:20:22Z.


Clinic public hands-on verification:

- Site 29 actual cartridge download sf-mini-monsters (12).gba is 16,777,216
  bytes and matches v35 target 0007ea7b1e2680de707e4bc300465f5ade39081c3154b583f0edb695ff046302.
- Explicit native clinic battery import reaches title/Continue and visibly
  resumes the original clinic at (6,8). Public screenshot and structured receipt:
  .tools/browser-review/public-v35-clinic.{png,json}.
- Public Save backup sf-mini-monsters (5).sav preserves the imported native
  battery byte-for-byte: 131,072 bytes, SHA256
  01536628638451d12541c2cdfe37972cc069bd94fbe9b6a5525b4716ee37dedc.
  The same battery already passed native cold resume. This checkpoint is not
  completion of the ten final consecutive campaign round trips.
- Sampled web core throughput 60.0–60.6 fps is not the deadline/input/audio
  gate. The clinic art/readability 0–4 subset review is requested and pending.
  Existing office review and all full-domain/system/campaign gates stay open.
- Original clinic source and exact built-in prompt are checked in. Source/
  release commits are pushed; no new Actions runs or DB operations occurred.
  Next weakest first-slice work is remaining named cast/portraits and music.


Original clinic cast implementation checkpoint:

- Added original Justine Moore and Patrick McKenzie nine-frame field atlases
  in assets/characters/south-park-cast, with exact built-in prompts and inspected
  public portrait references. Costumes/clinic roles remain fictional; refreshed
  primary identity/work sources are in cast-research.md. Likeness and native
  pixel-art approval are pending. East mirrors authored west frames.
- Generalized the existing converter to independent cast groups. The clinic
  pair share palette tag 0x1126; Cognition retains 0x1125 and all existing atlas/
  palette/conversion files byte-unchanged. Five native characters retain their
  16x32, nine-frame, 30-pixel feet-baseline and four-bit allocation contracts.
- The native installer resets shared tables only once, then preserves both
  groups. It rejects cross-group ID/slot collisions, stale palette/asset
  receipts and a registered character left on generic map graphics. Services
  now use the two new graphics IDs; scripts, locations, collisions, saves and
  courier walking resources are unchanged.
- All local checks pass; cast suite now covers all five independent pose
  cycles, independent nibble/tile decoding, cross-group native-slot collisions
  and actual service-event wiring. v36 draft target
  d3e28f36df0db5b3f03ffd16da45a33d02e785a0e2848afc4a22f84dede40c75
  compiles normally; 786,365-byte BPS applies exactly. Old v35 clinic battery
  cold-resumes at (6,8), with badge/stage 4, 4,000 money, three Potions
  and wounded level-11 party moves/PP preserved. Inspection shows the older
  save retains generic cached NPC graphics; a named-cast cache refresh is
  required before this is a successful visual migration.
- Public stays v35/Site 29 until cast runtime checks and publication succeed.
  No approval score is inferred; all first-slice/full gates remain required.
  No Actions workflow, DB operation or delegated agent ran.


Clinic cast resume compatibility correction:

- Initial v36 cold resume exposed native saved object/template graphics caches:
  map definitions alone did not replace the old woman/gentleman sprites. That
  diagnostic capture is retained and is not successful visual-migration evidence.
- Added a data-derived named-cast predicate and bounded pre-sprite resume hook.
  It refreshes only registered cast graphics in authored SF maps, preserving
  saved locations, facing, movement state, script/quest/gameplay fields and
  unrelated, inactive, other-map and player objects. Native sanitizer tests
  cover selective refresh, idempotence and complete unrelated-state preservation.
- Corrected draft ece0d2ea4a381395df7a440eb76531f7a7c111764cd2c4cdf06f30e61d9f9c6b
  compiles normally; 788,390-byte BPS applies exactly. The initial build lacked
  the native graphics-constant include; the corrected source now includes it.
  Full local checks pass with the new native resolver test.
- Actual old v35 clinic battery resumes at (6,8) with both new sprites visibly
  inspected, and badge/stage 4, money, items, level/moves/PP/HP retained. Native
  and WASM cold-resume final RGB, 16,467,520 PCM bytes and Flash match. Those
  trace-only captures do not establish equality for every video frame.
- Full native/WASM healing route: 336 identical RGB frames, 1,474,704 PCM bytes
  and identical Flash. Exit/re-entry: 576 identical RGB frames, 2,528,064 PCM
  bytes and identical Flash, ending (6,12) with original clinic NPCs. HP/PP
  refresh and all earned progression fields remain correct. Comparison receipts
  accompany .tools/benchmarks/clinic-cast-v36-* captures.
- Updated paired walking review and public publication follow. Public remains
  v35/Site 29 and approval remains 0/11; no CI workflow or DB operation ran.


User-directed clinic tiling correction:

- User reviewed the v36 paired still and objected to the chopped, oversized
  floor grid and disconnected wall joins compared with Emerald. This is
  negative art feedback, not a numeric score or full-domain approval. The
  prepared v36 Site archive/source are preserved and are not deployed.
- Added source-seamless-v2.png and exact built-in edit prompt. Current v2
  native materials use a low-contrast eight-pixel paving repeat, a flat teal
  carpet and edge-connected ground alignment around enclosed props. A source
  card's decorative border is no longer stamped across walkable floor.
- Authored wall strips now form straight runs and mitered NW/NE/SW/SE joins;
  windows share the wall-band alignment. Outside the cutaway room is quiet
  dark backdrop. A connected two-cell welcome mat replaces the arrow picture;
  native exit behavior stays 0x65 at the same (6,12) warp. Movement/collision
  remain the existing native grid; texture density is independent of it.
- Native tests verify the eight-pixel repeat, absence of dark prop outline on
  floor, corner endpoints, protected outlined white-prop interiors and all
  collision/elevation/event/warp contracts. Three clinic tests and full local
  checks pass. Initial v37 draft target
  aeea0b31083be08bc4f3fc8f6b2601bb48bac346b707650d8f3c542536114d1f
  compiles normally; 785,858-byte BPS applies exactly. Old v35 clinic battery
  resumes (6,8), both original NPCs visible, with earned party/items/money/
  badge/stage preserved. Native preview inspected for reduced grid contrast
  and continuous wall/carpet joins. Native/WASM routes and publication follow.
- Public remains v35/Site 29. All section 15 gates and unapproved first-slice
  domains remain required; no GitHub workflow or DB operation ran.


Seamless clinic runtime and public packaging:

- Normal release from 31745eb reproduces v37 target exactly. BPS is 785,858
  bytes, SHA256 36f98c46e82fb173660e5720029361166b8db789cfae5c9024545b179d9c5cd5.
  Native/WASM healing: 336 identical RGB frames, 1,474,704 PCM bytes and
  identical Flash. Exit/re-entry: 576 identical RGB frames, 2,528,064 PCM
  bytes and identical Flash. Both original clinic sprites remain visible.
- Revised same-input 2,048-frame, 34.29-second private comparison:
  .tools/benchmarks/seamless-clinic-v37-paired-review/comparison.{mp4,png,json}.
  Equal nearest 3x display, native clock and original Emerald lab reference.
  SF walk returns (6,8); new still inspected for subtle smaller floor texture,
  uninterrupted carpet and joined cutaway walls. Complete recordings are
  compressed losslessly; no review or full-domain score is inferred.
- Site source d0953b2b751991f02ff83b20b58042e5d3d1f9db passes TypeScript and
  production build. Archive verifies exact patch/manifest and no inherited
  cartridge. Saved Site version 30:
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_99f14be67190819180b9fe66ab89e7b4.
  Public audience/local patching remain unchanged. Actual public older-save
  download/import/resume/export checks follow. All full gates remain required;
  no workflow, DB migration or delegated agent ran.


Seamless clinic successful deployment:

- Deployment appgdep_6ac7db0484148191a96270d4eb75e693 succeeded at
  2026-10-08T18:03:57Z, publishing Site 30 at the existing public URL.
  The earlier cast-only prepared source/archive was not deployed.
- Actual public cartridge download sf-mini-monsters (13).gba matches the
  v37 target exactly. Older clinic battery import is accepted and public
  native title/Continue/resumed-room/export verification is in progress.
- Prior game/sign-in browser handles are no longer in this session's live
  inventory. Guest play is being retested in the current public tab; real
  signed-in player verification remains open, not an inferred successful login.


Further direct user art feedback and clinic recomposition:

- User rejected the v37 still as below Emerald quality and explicitly asked
  to stop using the chopped teal color. This remains negative qualitative
  feedback; no numeric approval or parity is inferred. The seam correction
  alone did not solve flat walls, tiny props or sparse room composition.
- Added source-neutral-v3.png and exact built-in edit prompt: neutral stone,
  plaster, brown wood, charcoal and navy replace the teal environment. Removed
  the large carpet from the map entirely. Full north wall/window art and deeper
  cutaway wall materials replace the thin outline treatment.
- Terminal now uses its full 32x32 footprint; recovery equipment is relocated
  into the visible left-side care area. Reception supplies counter uses all
  four native quadrants, including a transparent prop foreground with its own
  floor behind actors. This gives the desk physical volume without hiding
  players under opaque floor. Notes use a full two-cell board.
- NPC IDs/positions and original direct service scripts stay stable. Added
  a native facing-sensitive front-counter interaction for Patrick, selecting
  the actual local NPC before his existing shop script. PC access takes the
  authored path around the larger recovery equipment.
- Four clinic tests cover independent drawing/ground layering, full native
  capacity, corner joins, collision/elevation contracts and reachability of
  healer, PC, direct/front shop and notes interactions. All local checks pass.
  Initial v38 draft 02205f55d9099bd82dc4325deadc869f316635156918cdd10d740608ec0d2a18
  compiles normally; 786,936-byte BPS applies exactly. Cold resume, service
  routes, matched review and public release verification follow.
- Public remains v37/Site 30 until the neutral revision verifies. Original
  first-slice art, music, all full domains and campaign/system gates remain
  required. No GitHub workflow, DB operation or delegated agent ran.


Neutral clinic reading-corner and native preview checkpoint:

- Source-neutral-v4 replaces one unused corner card with a wood bookcase. The
  right-side reading corner balances the left care/storage area; source and
  exact built-in prompt are preserved alongside the prior neutral candidate.
  A native-facing shelf sign contains paraphrased South Park garden history
  from SF Recreation and Parks plus an original group-chat joke. Attribution
  and scope are recorded in the asset folder's history-source.md.
- Final draft a93d6c0a9f9e1a8e551d74c96d00996813b22665ee9776a4ce0af2891bc18f82
  compiles normally; 787,700-byte BPS applies exactly. Full local checks pass.
  The old v35 clinic battery cold-resumes at (6,8), with both named NPCs
  visible, reception counter depth inspected and earned badge/stage/party/
  moves/PP/items/money retained. Room screenshot contains no teal carpet or
  trim treatment. No visual-parity score is inferred from this preview.
- Final native/WASM service and exit routes, matched comparison and public
  release follow. Public remains v37/Site 30; this is first-slice art and
  layout work, not a complete quality domain or campaign. No CI or DB ran.


Neutral clinic v38 publication and verification:

- Normal build source 12be73894159c56d3dae99b038856f9e0ab6a3f7; target
  a93d6c0a9f9e1a8e551d74c96d00996813b22665ee9776a4ce0af2891bc18f82.
  BPS is 787,700 bytes, SHA256
  342330559c1c8426a1afce90826a8b5c0e02aa2c11a4bfb65e9c1a156a88d040.
- Native/WASM healing: 336 RGB frames, 1,474,704 PCM bytes and Flash identical.
  Native/WASM exit-return: 576 RGB frames, 2,528,064 PCM bytes and Flash identical;
  ends at clinic (6,12), preserving party/items/money/earned badge/stage.
  PC boot, front-counter dialogue and reading shelf are reached through controls;
  front-counter purchase menu and this revision's PC boxes are not yet verified.
- Private 34.29-second matched comparison is in
  .tools/benchmarks/neutral-clinic-v38-paired-review/comparison.mp4.
  Original reference stays private; no human score is inferred.
- Site source 10dfde4873bc483581dde7724f77b1dda6d93215, saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_35b016f90f288191b4c222055bb0033b.
  Deployment appgdep_6ac7e6875570819189d85f4479e3f1ff succeeded
  2026-10-08T18:53:03Z at the existing public URL. Archive patch/manifest
  match the release exactly and contain no BPEE ROM; Apple metadata forks
  are distinguished from playable files during the audit.
- Actual public old-battery import, title/Continue and neutral room inspected.
  Screenshot: .tools/browser-review/public-v38-neutral-clinic.png; sampled
  core throughput 60.0 fps is not a complete performance gate. Public download
  link clicks produced no new file or download event; download/export and
  sign-in checks remain open, not assumed successful.
- Original teal carpet and wall trim are removed. NPC shirt colors are separate
  from the rejected environmental material treatment. Full art quality still
  requires user approval; all full-domain and campaign/system gates stay open.
- One-time 6 PM local work-stop reminder recorded above. No workflow, DB change,
  PR merge or delegated agent ran for this checkpoint.


Release checks and storage terminology checkpoint:

- Previous goal turn classified as progress: neutral clinic v38 was deployed,
  committed and visually resumed on the actual public website.
- Chrome public session was already signed in and visibly identifies the account.
  No credential entry or new authentication grant occurred. Before import it
  had no supported saved game; explicit v35 battery import reaches the clinic.
  Actual downloaded cartridge sf-mini-monsters (14).gba is the exact v38 target.
  Export sf-mini-monsters (6).sav is 131,072 bytes, byte-identical to the imported
  v35 battery (SHA256 01536628638451d12541c2cdfe37972cc069bd94fbe9b6a5525b4716ee37dedc).
  Those actual downloaded files, copied into ignored private benchmark storage,
  cold-resume in native mGBA at (6,8), preserving level-11 CinderCoy, HP 4/31,
  all four moves/PP, three Potions, 4000 money and earned badge/gym stage 4.
  This is a supported older-save transfer, not ten full same-release round trips.
- Signed-in screenshot: .tools/browser-review/public-v38-signed-in-chrome.png.
  Existing authenticated play/download/export works; the entire fresh sign-in
  flow and controlled same-browser guest/account isolation remain unproven.
  IAB downloadMedia also timed out on the blob link; Chrome succeeds with the
  same release. No product download regression is concluded from IAB alone.
- Native controller checks reach storage action menus and the front-counter
  purchase flow. Diagnostic named potion-purchase actually bought 20 basic
  capture items at 200 each: capture pocket 5 -> 25, money 4000 -> 0, Potions
  stay 3. Preserve this diagnostic and its accurate result; it is not a Potion
  purchase test. The counter behaves normally; storage box editing is pending.
- Continue and eight storage labels exposed inherited branding in these checks.
  Added original Guide/monster terminology through the existing allocation-safe
  text overlay, preserving save layout, menu actions and native timing. Other
  inherited item/text/art references remain pending; this is not an originality
  or complete interface approval.
- v39 draft 00c55c0d1ad410e96cb52656c73b7efec240d17103721b224f0e5fcea7a4d735
  compiles normally and applies exactly (787,791-byte BPS). All local checks pass.
  Old battery resumes at (6,8); storage menu screenshot confirms new labels and
  descriptive text without clipping. Native/WASM menu route matches all 1,116
  RGB frames, 4,898,128 PCM bytes and Flash, ending at (2,4) with state preserved.
- Requested the user's 0-4 clinic art/readability score and biggest gap using
  .tools/benchmarks/neutral-clinic-v38-paired-review/comparison.mp4. No answer
  or numeric approval yet; 0/11 full domain approvals remains unchanged.
- Public stays v38/Site 31 while v39 and further first-slice work are prepared.
  No workflow, DB mutation, PR merge or delegation ran. The goal remains active
  until the user-requested cutoff or a genuine completion audit.


Storage-label source/release checkpoint:

- Source commit 8d700e75921069ab90dd10c63b822a988195c7b8 is pushed.
  Normal release v39 reproduces the reviewed draft target exactly; BPS SHA256
  636b8b9f16eebda072c38515d33f61c5acbedbc242314a9c550884dffd83bd69,
  787,791 bytes. Versioned original patch/manifest are checked in; no full ROM.
- This small completed label correction is a coherent commit exception to the
  200-300 handwritten-line cadence. No padding or unrelated edits are added.
- Next weakest work: first-slice music identity/arrangement. Current original
  bindings cover field/title/wild contexts; separate interior/gym/trainer music
  remains unfinished. Inspect actual native map song wiring before adding the
  clinic/office compositions, then audition in the real engine and compare mix/
  transition evidence. The full Audio domain and other acceptance gates stay open.
- Public remains v38/Site 31; v39 will be bundled into the next first-slice release.


Original clinic music composition checkpoint:

- Previous goal turn classified as progress: actual signed-in Chrome ROM/save
  transfer was verified and original Continue/storage labels were committed.
- Inspected native map song wiring: SF clinic's inherited lab map uses
  MUS_BIRCH_LAB, distinct from the field and gym bindings. Added the original
  Park Bench Break score only to that song/voicegroup binding. Healing still
  uses an inherited fanfare; gym/trainer/interior contexts remain unfinished.
- Editable 32-bar, 104 BPM score: first theme, varied second statement, harmonic
  bridge with percussion rest/re-entry, and a returning cadence. Seven mono
  tracks use original additive flute/bass, voiced seventh-chord piano, a damped
  plucked string and synthesized soft percussion; no imported samples/melodies.
  Native loop is 3072 ticks (~73.85 seconds). Score/artifact licensing documented
  in assets/audio/park-bench-break.md. This remains a musical candidate.
- Existing owning MIDI/voice tests now cover its note lifetimes, program bounds,
  exact per-track loop markers, sample headers and silent transient endpoints.
  These protect native note/loop safety, not composition/mix parity. All local
  checks pass; prior field/wild assets remain byte-unchanged in Git.
- Normal draft target 5d9e8a8a1ee68d5ebb666d18b2616124f73c7413a1d1ba00a307ca47df4f0538
  compiles and round-trip applies (813,705-byte BPS). Actual native/WASM playback,
  two-loop capture, transitions and old-save verification follow. Public remains
  v38/Site 31; there is no audio approval or full-domain completion.


Clinic initial native mix audition evidence:

- Initial two-loop capture is 167.43 seconds, peak 4320, RMS 1135.93. The matched
  34.29-second segment has RMS 1122.74 versus reference lab RMS 2416.32 (~6.7 dB
  quieter). Raised score channel/native levels before publication. Initial
  patch/captures are preserved, not deployed; revised mix is still unreviewed.
- Initial 2048 native/WASM walking RGB frames, 8,988,672 PCM bytes and Flash are
  identical; end state remains (6,8) with party/badge/stage/items/money retained.
  These are runtime equivalence checks, not browser deadline/underrun evidence.


Clinic v40 revised music release and user review:

- Source 0898f0838e34b715e4ec0ff374de9f67c851a9c2 builds final target
  fcdb5aeb7266af8af0938d52bfd13c00fc9a1db9ba111abac2a2667aff8e3b94.
  BPS 813,704 bytes, SHA256
  c87d61428615461184b1d92188731151c708f6a89f0cf14b2c3d04597171b8a2;
  normal compilation and byte-identical patch round trip pass.
- Revised native/WASM walking: 2048 RGB frames, 8,988,672 PCM bytes and Flash
  identical. Healing: 336 RGB frames, 1,474,704 PCM bytes and Flash identical;
  level-11 starter HP restores 4/31 -> 31/31 and Ember PP 16 -> 25 while
  money/items/badge/stage persist. Inherited healing fanfare is still pending.
- Revised 167.43-second native clinic recording: peak 6528, RMS 1741.73.
  Matched segment RMS 1728.19 (~2.9 dB below reference lab 2416.32). The native
  tempo produces an approximately 74.175-second repeat (25 ms energy-envelope
  correlation 0.969; second repeat 148.375 seconds, correlation 0.962). This
  supports two actual loops in the capture, not a browser underrun/click verdict.
- Candidate listening file:
  .tools/benchmarks/clinic-music-v40-revised-native-two-loop/park-bench-break-native.mp3.
  Private matched comparison:
  .tools/benchmarks/clinic-music-v40-revised-paired-review/comparison.mp4.
  Reference remains private. Candidate composition and instruments are original.
- User rated this clinic music subset 2/4 on October 8, 2026. This is an explicit
  below-target result, not approval. Full Audio and all 11 full domains remain
  incomplete. Asked which gap dominates: instrument sounds, melody/arrangement
  or mix/energy. Awaiting that optional feedback; no specific criticism inferred.
- Site source 24ddc372ab9f3248724e6ee82ba2b230f562f26e; saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_32acc9db20948191b93ed7bcc4be64f1.
  Deployment appgdep_6ac7ec3a07108191ae2de2d7499955a0 succeeded
  2026-10-08T19:17:22Z at the existing public URL. Archive patch/manifest match
  release exactly; no full BPEE ROM is hosted. Current audience stays public.
- Actual Chrome signed-in public player downloads sf-mini-monsters (15).gba
  matching final target, restores prior local battery, displays GUIDE at
  Continue and enters neutral clinic. Backup sf-mini-monsters (7).sav matches
  imported v35 battery byte-for-byte (131072 bytes, SHA256
  01536628638451d12541c2cdfe37972cc069bd94fbe9b6a5525b4716ee37dedc).
  Screenshots: .tools/browser-review/public-v40-guide-continue.png and
  public-v40-clinic-music.png. Sampled core counter 60.0 fps is not a deadline gate.
- No workflow, DB mutation, PR merge or delegation ran. Goal stays active with
  the original full scope and the recorded 6 PM local stop condition.


Clinic instrument revision 2 checkpoint:

- Previous goal turn classified as progress: original clinic soundtrack v40
  was deployed and its below-target human score (2/4) recorded.
- Specific gap feedback is still pending. Instrument tone is the working
  hypothesis, not a criticism attributed to the user. Keep v40 as the scored
  baseline and compare a single controlled revision rather than changing tune
  and instruments together.
- Revision 2 MIDI is byte-identical to v40: same melody, form, timing and mix.
  New original voices add flute breath/long moving sustain, bass pluck/sustain,
  piano tine strike and pitched damped guitar partials. All are synthesized
  locally, with no copied/commercial instrument samples. Revision 1 remains
  preserved under native-v1 and reproducible from its pinned commit.
- Added validated native sustain offsets matching the pinned WaveData struct.
  Existing owning MIDI/sample tests cover both generations and loop join
  continuity, range and silent transient endpoints. This tests format/safety,
  not instrument realism or musical quality. All local checks pass; previous
  field/wild native assets remain byte-unchanged.
- Draft target 9cf14795ee4fc41cd772abd2a2f61572003659995aeb4cf970744202de1cd5bc
  compiles normally and round-trip applies (841,806-byte BPS). Native/WASM
  playback, old-save resume and controlled audio comparison follow. Public
  remains v40/Site 32; revised music is unreviewed and full Audio is incomplete.


Clinic voice v41 native A/B verification:

- Normal source build 59371e302ee97e2f10fa30d8d4d18d752dd0bca7 reproduces draft
  target 9cf14795ee4fc41cd772abd2a2f61572003659995aeb4cf970744202de1cd5bc.
  BPS 841,806 bytes, SHA256
  8645c3c95a13f9ef653e657bcc8190cb26732209f3889670c652cacf744ed15b.
  All local checks pass; a trailing blank-line warning is corrected separately
  without changing runtime output.
- Old v35 battery cold-resumes at (6,8), preserving starter/HP/moves/PP/items/
  money/badge/stage. Native/WASM walking matches 2048 RGB frames, 8,988,672 PCM
  bytes and Flash. v40/v41 walking RGB is also identical across all 2048 frames;
  MIDI bytes are identical, isolating this change to instruments/native sustain.
- A 167.43-second native capture reaches two loops without capture failure or
  digital clipping: peak 5952, RMS 1562.80. Matched 34.29-second v41 segment RMS
  1552.94, versus v40 1728.19; level-matched A/B scales only the review copy
  (gain 1.11285), never in-game audio. Native output remains separately available.
- A/B first plays user-rated v40, pauses half a second, then plays v41. Evidence:
  .tools/benchmarks/clinic-voice-v41-audio-review/v40-then-v41-rms-matched.mp3.
  Native candidate: .tools/benchmarks/clinic-voice-v41-native-two-loop/park-bench-break-native.mp3.
  Emerald matched comparison: .tools/benchmarks/clinic-voice-v41-paired-review/comparison.mp4.
  Asked for a new 0-4 instrument score and remaining gap; no answer yet.
- v40 remains the last explicit clinic music score, 2/4. v41 is unreviewed.
  These format/capture/level checks do not establish acoustic realism, musical
  taste, transition cleanliness, browser underrun safety or full Audio parity.


Clinic voice v41 publication checkpoint:

- Site source 47ceac6a503fbb62aa986acdf4f42eb7a55ba7ed, saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_5ab34aa831a48191b0d4810e2d8ed148.
  Deployment appgdep_6ac7f1bb34788191877cfa7bc5d2270f succeeded
  2026-10-08T19:40:51Z, publishing Site 33 at the existing public URL.
  Archive patch/manifest match release and contain no full Emerald ROM.
- Native/WASM healing verifies all 336 RGB frames, 1,474,704 PCM bytes and
  Flash identical with the revised sustain voices. Ends at (6,5), HP31/31 and
  Ember PP25; party/items/money/earned badge/stage retained. This does not
  approve the inherited fanfare or certify every audio transition.
- Actual public Chrome account session downloads sf-mini-monsters (16).gba
  matching v41 target, restores prior local battery through GUIDE/Continue
  into neutral clinic, and exports sf-mini-monsters (8).sav byte-identically
  to the v35 import: 131072 bytes, SHA256
  01536628638451d12541c2cdfe37972cc069bd94fbe9b6a5525b4716ee37dedc.
  Screenshot: .tools/browser-review/public-v41-clinic-voices.png. Player is
  muted and paused after QA so review audio can play alone. Goal stays active.
- Latest human result remains clinic v40 music 2/4; v41 instrument review and
  exact gap feedback are pending. No full-domain approval is inferred.
- Inspected next audio context: native FANFARE_HEAL waits 160 frames and
  MUS_HEAL uses MUSIC_PLAYER_SE2 with the shared fanfare voicegroup. An original
  replacement must preserve that event timing and avoid changing other
  fanfares' instrument mappings; implement an independent one-shot voicegroup.
- No workflow, DB mutation, PR merge, delegation or recurring monitor ran.
  Original full scope and recorded 6 PM local cutoff remain in force.


Original recovery cue implementation checkpoint:

- Previous goal turn classified as progress: clinic instrument revision 2 was
  published with byte-identical walking/MIDI and controlled A/B evidence.
  v41 review is pending; the last explicit clinic score remains v40 music 2/4.
- Composed Team Refresh, an original two-bar, 192 BPM one-shot with bell/bass/
  keys and a four-chord cadence. MIDI end is tick 192 (nominal 2.5 seconds),
  last notes end at tick 180. No loop markers or hanging notes. Four synthesized
  original waves and a separate sf_heal voicegroup replace only MUS_HEAL.
- Importer appends the custom bank and redirects only this song's configuration;
  existing shared fanfare.inc is byte-identical to pinned source (SHA256
  d3e1c7539e87fbbf94a8b5ec5ab76e983a989f85f2392f0b8111162eca2ce728).
  New untracked engine include stays inert when tracked include/config files
  are restored; it is not listed as a nonexistent upstream restoration path.
- Existing MIDI/wave tests cover the new one-shot, note lifetimes and silent
  endpoints. All local checks and normal draft compilation/BPS round trip pass.
  Draft target 5542a01edefcd14a12b4e0669ffe63f95fef025d30fd0b244085c3e24bd90632,
  BPS 866,594 bytes. Playback quality remains unreviewed.
- Added a read-only music-state inspector for pinned controller snapshots,
  validating the ELF companion cartridge identity before reading native player
  status, clock, voicegroup and remaining fanfare frames. Use it to verify the
  one-shot actually ends and BGM resumes through the existing 160-frame service
  gate; no game-state writes or production hooks are added.
- Native/WASM healing, old-save resume, jingle lifetime and public QA follow.
  Public remains v41/Site 33. Full Audio and all final acceptance gates remain
  open; no CI, DB mutation, PR merge or delegation ran.


Recovery cue v42 playback verification:

- Normal build source 101ca9d0d9505d033da0def8aa7bd82a9c85c8e2 matches draft
  5542a01edefcd14a12b4e0669ffe63f95fef025d30fd0b244085c3e24bd90632.
  BPS 866,594 bytes, SHA256
  86f3f0478bb0a3d5d277424c8419a02e370bca908e41eb61f6f68505726471f8.
- Controller-only old-save resume preserves position (6,8), party/HP/moves/PP,
  items/money/badge/stage. Native/WASM healing matches all 336 RGB frames,
  1,474,704 PCM bytes and Flash. v41/v42 RGB is also identical across the
  complete service route, preserving dialogue/game timing. Ends (6,5), HP31/31
  and Ember PP25 with other earned state retained.
- Compiled music-state inspection shows the cue's dedicated bank and three
  active song tracks while BGM is paused, with 122 fanfare frames remaining
  at the intermediate controller snapshot. At completion the cue has zero
  active tracks, clock 194, counter zero, and all seven BGM tracks resumed.
  Inspector labels now distinguish the active bitmask/count, player capacity
  and actual song-header track count to avoid confusing capacity with voices.
- Actual cue/service clip:
  .tools/benchmarks/recovery-cue-v42-native-heal/review.mp4 (5.63 seconds).
  Listening file: same folder/team-refresh-native.mp3. These demonstrate the
  candidate in-game; a genuine Emerald-centre comparison and human score are
  still required. An older SF clip containing inherited music is not promoted
  to an authentic reference-ROM comparison.
- Shared fanfare bank remains byte-unchanged. Public v42 release follows;
  the original full Audio/domain/campaign/system gates remain open.


Recovery cue v42 public release checkpoint:

- Site source c8fc44c5e08a1d5230be320f3c75837148228297, saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_f73ab5684a9481918e19ad9585f1594d.
  Deployment appgdep_6ac7f8add9908191b58557f83baa7e12 succeeded
  2026-10-08T20:10:31Z, publishing Site 34 at the existing public URL.
  Archive patch/manifest match release exactly and contain no full Emerald ROM.
- Actual public Chrome account downloads sf-mini-monsters (17).gba matching
  v42 target, restores old local save through GUIDE/Continue into neutral
  clinic, then exports sf-mini-monsters (9).sav matching the v35 import:
  131072 bytes, SHA256
  01536628638451d12541c2cdfe37972cc069bd94fbe9b6a5525b4716ee37dedc.
  Screenshot: .tools/browser-review/public-v42-recovery-cue.png. The first
  chooser wait timed out after reload; fresh state showed no console errors,
  and alternate Load ROM control worked. No persistent product bug is inferred
  from one transient observation; early-load behavior remains worth checking.
- Recovery service is proven in native/WASM captures and the exact public ROM
  is verified; actual browser healing interaction/audio deadline checks are
  still pending, not substituted by cartridge identity alone.
- Inspecting the pinned original maps establishes a genuine reference route:
  original lab exits (6/7,12) -> Littleroot (7,16), then Route101 -> Oldale.
  Oldale centre door is (6,16); nurse is (7,2), approached at (7,4). Existing
  office-emerald-paired-interior snapshot has the exact baseline hash and
  pinned controller-only lineage; extend it through normal gameplay.
- Latest explicit user music score remains 2/4 for v40. No score/approval is
  inferred for v41 voices or v42 cue. Full Audio and all full-domain, campaign
  and system requirements remain unfinished. No CI, DB mutation, PR merge or
  delegated work ran. Goal remains active with the same 6 PM local cutoff.


Genuine Emerald recovery comparison checkpoint:

- Previous goal turn classified as progress: original recovery cue v42 was
  published with verified timing/state restoration and public download/resume.
- Extended the genuine controller-only reference lineage from the original lab:
  obtained Torchic through Birch rescue, completed normal dialogue, crossed
  Route101, took a Tackle after Growl, fled, and reached Oldale centre. Exact
  reference ROM/core hashes retained; no SF state or RAM writes are used.
- Corrected setup assumptions using pinned map/variable evidence: rival intro
  was already complete; the first exit lane was blocked by an NPC and then a
  tree. Centre door is (6,16), not the previously mistyped (6,5); nurse is
  approached from (7,4) across the counter. Unused detours remain preserved
  diagnostics and do not replace the actual parent lineage.
- Added a read-only static-map controller planner that favors avoiding grass
  and conservatively avoids authored NPCs. It labels outputs planned-only;
  encounters, directional terrain and live events require actual replay.
  No benchmark input is overwritten by the planner.
- The first paired service input selected NO in the reference Yes/No prompt:
  reference HP/PP stayed 17/19 and 39/40. Preserved that failed diagnostic.
  Corrected input (four A taps, four B taps) produces one completed healing
  event in both games at identical 2048-frame/34.289-second controller input.
- Genuine reference restores level-5 Torchic HP17/19 -> 19/19 and Growl PP39 ->
  40; money3000/moves/other PP retained. SF v42 restores level-11 CinderCoy
  HP4/31 -> 31/31 and Ember PP16 -> 25, retaining three Potions/money4000/
  earned badge/stage. Both close dialogue; an additional Down controller replay
  verifies unblocked movement afterward. Content/stat/layout/confirmation
  differences are recorded; this is not an identical-state damage case.
- Recipe/input: docs/quality/recovery-service-review.md and
  data/quality/recovery-service-review.csv. Packager now labels the actual
  reference scene EMERALD CENTRE and declares healing-event/audio-only scope,
  retaining genuine-ROM/core/input/length/frame provenance guards. Existing
  paired-review tests pass; game source/build is unchanged for this checkpoint.
- Private 34.29-second comparison:
  .tools/benchmarks/recovery-service-v42-genuine-review/comparison.mp4.
  Separate listening files are in recovery-service-emerald-confirmed/listen.mp3
  and recovery-service-v42-confirmed/listen.mp3. Commercial reference remains
  private. Asked for separate 0-4 healing cue and visual-sequence scores; pending.
- Visible next gap: reference nurse/equipment has recovery movement/effects,
  while SF equipment remains static. Improve that scene, preserve its verified
  service behavior, and gather a new same-protocol comparison. Full domain
  approvals remain 0/11; latest clinic soundtrack rating is v40 at 2/4.
  Public stays v42/Site34. No workflow, DB mutation, PR merge or delegation ran.

Recovery animation source checkpoint (v43, not yet released):

- Previous turn produced progress: genuine controller-only Emerald healing
  reference and a same-input comparison now exist. No quality approval inferred.
- User reiterated clinic music 2/4. This remains the recorded score; full Audio
  and all eleven full-domain approvals remain open. Teal flooring stays removed.
- Added native amber equipment palette phases that reuse the exact four pod
  metatile geometries. Only equipment color indices 10/12/13 change, isolated
  in banks10/11/12; neutral floor/outline/other furniture colors stay unchanged.
- Healer faces equipment, plays the existing original recovery cue with five
  24-frame light holds, restores idle equipment and waits for the original
  fanfare gate before facing the player and releasing control after dialogue.
  No actor coordinates, inventory, save format or recovery mechanics change.
- Tileset uses106 metatiles/328 native tiles, within capacity. Five local clinic
  tests pass, including phase geometry/layer/material invariants. Build,
  native/WASM replay, public release and human visual/audio review are pending.
- Public remains v42/Site34 until validated v43 is published. No Actions run,
  DB mutation, PR merge or delegation. Goal remains active until 6 PM SF local.

Recovery animation verified and published checkpoint:

- v43 source25603f2 compiled normally; BPS866334 bytes, SHA256
  4cbb4c0b5add19e3011b1ee607d0f8a0027520bbb43990ee195f14506a382995.
  Target aca23d84b531a2b76e103ecddeeecb931a231b62bb7ed9f252c4a82b70066ce6.
  Build reports dirty worktree because unrelated user PDF is untracked; it is
  excluded from source/assets/release and remains untouched.
- Native and WASM run2048 same-protocol frames from a cold imported v35 battery,
  with byte-identical RGB,8988672 PCM bytes and Flash. Both restore HP4/31 to
  31/31 and EmberPP16 to25; moves/level/items/money4000/badge/stage4 retained.
  Additional native Down moves6,5 to6,6 after dialogue: control is released.
- Captured snapshots confirm warm/bright/peak/idle equipment phases and healer
  facing change. No geometry added:328 native tiles/106 metatiles. Local checks
  pass. Scene is still sparse; this does not establish Emerald-quality parity.
- New genuine34.29second comparison:
  .tools/benchmarks/recovery-service-v43-genuine-review/comparison.mp4.
  Shared controller protocol and original reference provenance unchanged.
- Site source919cec27e674fced3219c3176e43befbb22d70fa; archive
  .tools/site-v43-recovery-animation.tar.gz verifies one v43 patch/manifest and
  no commercial BPEE cartridge. Site35 saved id:
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_b45a6a9f732c8191b47c107f4571c940.
  Deployment appgdep_6ac8079f096c8191bb7b8fa67e8660da succeeded
  2026-10-08T21:14:15Z, preserving public audience and existing auth.
- Actual browser healing/download verification is underway. Latest clinic music
  rating remains2/4; full-domain approvals0/11. No GitHub workflow, DB mutation,
  PR merge or delegation ran. Goal remains active with6PM local stop.

Public v43 healing interaction checkpoint:

- Actual Chrome account reloads Site35, uses visible Load ROM with local baseline,
  downloads /Users/devkunjadia/Downloads/sf-mini-monsters (18).gba matching the
  verified v43 target, and resumes the prior save through title/Continue.
- Three Up taps approach Justine; A produces her left-facing gesture and visible
  amber equipment phase, then idle equipment returns and healing dialogue opens.
  Three B taps close the pages; Down first changes facing and the next tap walks
  away. Screenshot confirms separation from healer and normal field activity.
  Test player is muted and paused afterward; no browser audio deadline claim.
- Private public screenshots: .tools/browser-review/public-v43-recovery-playing.png
  and public-v43-recovery-walk-away.png. Paused overlay hides the scene, so an
  intermediate paused screenshot alone is not counted as movement evidence.
- Native final music inspection finds fanfare counter0 and seven BGM tracks active
  and unpaused. SE2 has since been reused by text effects; its final bank does
  not represent the earlier healing cue and is not misreported as cue evidence.
- Asked for updated0-4 healing visual subset review against genuine Emerald;
  pending. Latest explicit clinic music score2/4 is retained. Next weakest
  measured area is clinic soundtrack; no full-domain approval inferred0/11.
- Source/release/progress commits25603f2 and5668521 pushed. No workflow, DB change,
  PR merge or delegation. Complete SF campaign and required system/quality gates
  remain unfinished; goal stays active with final stop/commit at6PM SF local.

### 15.7 Requested deadline stop — October 8, 2026

Work stopped at 6 PM San Francisco local time (October 9, 01:00 UTC).
The one-time deadline fired at 01:00:05Z. No new implementation, build,
deployment, monitor or GitHub workflow was started after the cutoff.
Process inspection found no active project build/capture/publishing operation.
Only this final progress record, commit/push and requested goal pause remain.

Latest delivered release remains v43 / Site35, from source25603f2, with
native/WASM healing replay and actual public download/resume/interaction checks
recorded above. Last pre-cutoff repository commit was fd32bb0. The unrelated
untracked data-center-three-hour-learning-guide.pdf remains untouched.

The goal is not complete. Required outstanding work includes:

- Complete sixteen SF neighborhood adventures, eight startup gyms, all150
  obtainable monsters, championship, rival/villain/legendary arcs, Marina bars,
  Tenderloin altered-state scenes, dates, lore and scoped postgame.
- User-approved4/4 comparisons in all eleven quality domains: currently0/11.
  Latest explicit clinic soundtrack score is2/4; later instrument/healing
  comparisons remain unapproved. Passing runtime checks does not imply parity.
- All300 independent reference mechanics cases, including50 doubles; full
  performance/input/audio gates and three ten-minute deadline/audio traces.
- Ten full cross-platform save round trips, fifty resume checkpoints, three
  complete starter campaign runs, and remaining public authentication/account
  isolation, Safari/mobile and browser audio checks.

The complete section15 objective is preserved. Pause at the user's request;
resume work only after the user resumes the goal. Final commit contains this
honest deadline snapshot only; no database change or PR merge is involved.


### 15.8 October 13 resume and independent alignment review

The user explicitly resumed implementation and requested another thread to work
with the main thread and keep it aligned with the goal. The goal is active again;
the old October 8 deadline is historical, not a new daily stop condition. No
replacement schedule or monitor is created. All section15 requirements remain.

- Starting commit1b1a199; public v43/Site35. No content or quality score is
  upgraded merely because execution resumed. Full domain approvals stay0/11;
  latest explicit clinic music score stays2/4.
- Created project thread “SF Monsters goal alignment review”, id
  01a13900-5c2c-7973-bea7-389deda8a5ab, for one finite read-only audit. It will
  check priorities and concrete first-slice gaps; main thread owns edits, builds,
  commits and releases. Main may send authorized follow-up review requests.
- Immediate candidate: a controlled clinic soundtrack revision, preserving the
  existing cue, recovery behavior and supported saves. Ask for the largest music
  gap, retain original comparisons, and evaluate native captures before release.
  Independent review may identify a higher-impact first-slice blocker.
- No campaign expansion before the section15.5B slice review. Do useful work on
  unapproved gates while awaiting optional user feedback; never invent approval.
- Continue coherent small commits and routine local checks. GitHub Actions stays
  manual-only. No DB changes, PR merges or commercial ROM/media publication.


October 13 bounded arrangement candidate and updated deadline:

- Independent thread01a13900-5c2c-7973-bea7-389deda8a5ab completed its finite
  alignment/source reviews and stopped. It agreed the2/4 clinic music is the
  next bounded priority and caught the earlier two-loop evidence shortfall.
  The protocol requires at least three consecutive loops.
- Code-based inference: nearly identical backing patterns across A/A2/A3 may
  sound repetitive. This is not an auditory diagnosis; this session cannot
  audition audio directly. Asked the user which music gap is largest; pending.
- Implemented one arrangement experiment: phrase dynamics, section-specific key
  rhythms, bass approaches, guitar responses only in explicit rests, and
  sparser percussion. Multiple sequencing features limit causal attribution.
- Melody pitches/durations/rests, harmony, tempo, channel volume/pan and native
  volume remain unchanged. Independently compared v2/v3 generated PCM, headers,
  sustain offsets, voices.inc and waves.inc: byte-identical. Asset revision3
  is separate from unchanged instrument revision2, preserving v1/v2 files.
- Existing MIDI/sample tests pass with v3 included. Reviewer independently
  confirms legacy revision1 event lists match1b1a199, seven-track monophony,
  valid bass targets and note-offs before3072 ticks. Final guitar response
  ends at3070: release across the boundary still needs native listening.
- Genuine baseline centre idle capture:15000 controller-only frames, about
  251.14seconds, .tools/benchmarks/clinic-audio-v44-emerald-three-loops.
  Its name denotes the planned review; loop periods have not yet been analyzed.
  No claim that the entire three-loop comparison packet is complete.
- v44 source/assets are committed as an unbuilt, unreviewed candidate. No native
  v44 cartridge, BPS release, WASM replay, audio comparison or public deployment
  exists yet. Latest verified public release remains v43/Site35.
- Updated objective arrived with a6PM Pacific-today stop. Clock read
  2026-10-14T06:06:20Z = October13,11:06PM Pacific, already past that cutoff.
  Stopped implementation/build/deploy immediately, collected the running
  read-only review, and made the final concrete-change/spec commit and push.
  No active build/capture/publishing process remained. No monitor was created.
- Full campaign, all required system checks and0/11 domain approvals remain
  unchanged. Goal pause requested by the updated deadline, not completion.
  No GitHub Actions, DB changes, PR merge or commercial media publication.


Cutoff removed by explicit user instruction:

- The user said “remove the cut off and keep going.” This supersedes every
  earlier6PM stop and the stale cutoff sentence in the goal record. Continue
  the full section15 objective without a time-based stop; do not recreate the
  expired reminder. Historical stop entries above remain historical evidence.
- Resume v44 build, native/WASM and supported-save checks, three-loop review
  preparation and independent alignment review. Public staysv43 until a
  validated release. No quality approval is inferred; music remains2/4.

v44 build, regression and loop-evidence checkpoint:

- Cutoff remains revoked. Independent alignment thread reviewed the source and
  loop protocol; no code-level blocker was found, and no human score inferred.
- Native v44 build/BPS round trip passes: target
  735197f21e88fe58b6d0d6ee86329b816cf98599c0621cd58719707742dadc6b,
  patch866420 bytes, source56deb55. Normal release exists locally; public stays
  v43 until publishing. Local checks pass, including four new loop-evidence
  contract cases; actual reference/native captures exercise the observation path.
- Native/WASM18000-frame idle PCM and Flash match byte-for-byte. Native/WASM
  2048-frame healing RGB/PCM/Flash match; v43/v44 healing RGB is unchanged.
  Healing restores HP4/31 to31/31 and EmberPP16 to25, preserving money4000,
  three Potions, moves, level, badge and gym stage4.
- Added optional read-only per-frame native MPlay trace with matching-ELF/ROM
  identity checks. First guard incorrectly assumed EWRAM-only track storage;
  failed safely and diagnostic remains preserved. Correct guard accepts bounded
  native IWRAM/EWRAM. No engine RAM writes or cheat input are introduced.
- SF actual first-track jumps occur at3613/8044/12475/16906:3072 ticks and
  4431frames per period. Exact ROM GOTO corroborates them. Reference periods are
  1536ticks,2215/2216frames. Static score checks support equal periods across
  all7 SF and9 reference tracks; only first-track runtime cursors are observed.
- Reproducible private listening packager keeps raw WAVs, constant RMS-matched
  copies, hashes/sample bounds,250ms padding and frame-level uncertainty. It
  does not certify sample-exact phase, clean joins, underruns or quality.
  Protocol: docs/quality/clinic-music-review.md. Final review packet, public
  deployment and user review remain pending. Latest human score stays2/4,
  full approvals0/11; full campaign/system gates remain unchanged.

v44 review packet and release preparation:

- Final private packet: clinic-arrangement-v44-final-three-loop-review under
  .tools/benchmarks, with raw WAVs, separate level-matched MP3s and receipt.
  SF three observed periods are74.1869316s each; reference37.1018372/37.0850945/
  37.0850945s. Reference RMS2513.8 is attenuated to SF RMS1453.88 with one
  fixed gain; no limiter/crossfade. These are first-track runtime periods with
  independent static multitrack duration checks, not quality/underrun approval.
- A49-second old/new review plays24s v43,1s silence,24s v44. Both retain the
  same melody/instruments and global three-period RMS matching. Full before/
  after files remain available. Asked user for a0-4 clinic-subset score and gap;
  pending. Latest explicit score remains2/4, full-domain approvals0/11.
- Actual entry/healing attempt initially ended one tile short, HP unchanged;
  preserved diagnostic. Corrected Up96 to112 reaches6,5 and restores HP/PP.
  Valid46.48s native clip: clinic-arrangement-v44-entry-healing-valid/review.mp4.
  Door fade pauses are frames136–147 and410–421; healing pauses BGM734–899.
  End state has fanfare counter0 and seven BGM tracks active/unpaused. These
  transition intervals are observed behavior, not a browser deadline certificate.
- Additional native Down replay proves released control at6,6. Same-input
  genuine34.29s healing comparison is clinic-arrangement-v44-heal-paired-review.
- Public publishing is underway through the existing Site identity/audience.
  Old temporary Site checkout has unreadable Git metadata; it is preserved.
  Supported helper restored the same remote source into a new empty checkout,
  retaining source919cec27e674fced3219c3176e43befbb22d70fa before edits.
- Alignment reviewer recommends Scott Wu's original trainer portrait next:
  the current first-gym trainer still selects LEADER_BRAWLY. Bound next work to
  one original portrait integrated into the existing encounter, preserving team,
  AI, rewards, flags and saves; do not expand campaign while slice review waits.


v44 public release and Scott portrait source checkpoint:

- Site36 saved id
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_406eed41f5388191b38c10c24e850234.
  Source79c71148903f1176d33a2e8e0d78b32b490cc239; archive
  .tools/site-v44-clinic-arrangement.tar.gz verifies one current patch/manifest
  and no commercial BPEE cartridge. Deployment
  appgdep_6acf275ffc188191afcbb695105d969f succeeded2026-10-14T06:55:37Z,
  retaining public audience and existing authentication. Actual guest IAB QA
  underway; old Chrome4 connection is unavailable. No product regression
  inferred from a disconnected browser.
- Using imagegen built-in tool, generated one original Scott battle portrait
  from the established field appearance reference. Source and exact prompt are
  in assets/characters/cognition-cast/scott-wu/battle-portrait-v1. Original
  fictional costume; likeness/native cleanup/art approval remain pending.
- New native picture slot93 preserves original0–92. Original figure converts
  to one64x64 four-bit frame/2048bytes and16-color/32byte palette, baseline62.
  Importer registers coords, sheet, palette and one-frame animation, preserving
  existing field-cast graphics declarations. Only Scott's portrait selector
  changes in battle data; independent comparison preserves every other field.
- Three battle-content tests pass. v45 portrait candidate is not yet built,
  replayed or released. Source review is running in the alignment thread.
- Full approvals remain0/11; all complete campaign/system gates stay required.
  Cutoff remains revoked; no workflow, DB mutation or PR merge ran.

Scott portrait draft compilation checkpoint:

- Draft v45 normal compilation/BPS round trip passes. Target
  b4846cfe0b614b8d278b91cb4ad50b4076493ced0c732e5ff4bf9986c35c977b,
  patch874488 bytes. Human art/likeness review remains pending.
- Reviewer found no pre-build blocker and independently confirmed native PNG
  packing/palette/baseline and trainer-data preservation. Both reviewer and
  main identified the consumed-PNG hash gap; conversion metadata now also
  protects portrait.png, preventing stale previews bypassing binary guards.
- Compiled slot/table/decompression/trainer-record audit is running in the
  alignment thread. Actual trainer encounter and older-save/victory/re-entry
  replays are still required. Public remainsv44/Site36.


### 15.9 October 14 priority update and new stop deadline

- The latest explicit stop is October 15, 2026 at 6 PM America/Los_Angeles
  (October 16 at 01:00 UTC). This supersedes the no-cutoff instruction above.
  Reused the paused deadline automation as a single fixed-date invocation; it
  must disable itself on firing. No recurring monitor or GitHub workflow.
- User reports courier hidden beneath Sunset rowhouses and buildings spaced
  too far apart. Reproduce the bottom-facade overlap, correct draw priority,
  then tighten the residential frontage while keeping entrances accessible.
- v45 Scott portrait normal release is locally built: target b4846cfe0b614b8d
  278b91cb4ad50b4076493ced0c732e5ff4bf9986c35c977b; patch874488 bytes.
  Same2048-frame introduction input produces identical native/WASM RGB, PCM
  and Flash. Portrait is visible in the actual encounter at frame1400.
  Existing prebadge and earned-badge battery saves cold-resume; repeat dialogue
  preserves money/bag bytes and earned flags. No new victory is claimed.
- An old long trainer input replay blacked out; retained as a failed controller
  diagnostic. A subsequent normal Steven retry is unfinished. This does not
  establish balance or a completed first-gym route. Public staysv44/Site36 while
  the user-reported facade issue takes priority; v45 is not published.
- Alignment thread completed genuine controller-only Emerald progression to
  Calvin: rival, healing, Dex/Balls gate, Route102. Verified pre-encounter
  snapshot and34.29s intro/deployment clip support a fair presentation subset
  comparison. Commercial reference media remain private. It independently
  identified bottom-facade foreground priority as a plausible overlap cause.
- Human domain approvals remain0/11; music's latest explicit subset score2/4.
  The full campaign, mechanics, art, audio, performance and release gates remain.


Facade edge regression checkpoint (local candidate v46):

- Reproduced reported hidden head at Sunset25,15 on v45 from a supported
  older battery save. The same position/input on v46 shows the complete head.
  All six rowhouses' blocked bottom rows now draw behind approaching actors;
  roof/upper-wall foreground layers and collision/elevation words are preserved.
- Applied the same correction to both South Park service facades and annexes.
  Static door behavior remains0x69. Animated upper/lower halves follow their
  respective static layer so animation cannot restore the bad foreground edge.
- Native1296-frame wall/door replay stays25,15 against the blocked wall, walks
  around the block, enters the apartment, and exits to16,9. Every RGB frame,
  PCM sample and Flash byte matches WASM after decoding its lossless frame file.
  Evidence: facade-v46-door-native and facade-v46-door-wasm; screenshot pair
  facade-v46-before-after.png. No cross-ROM savestate was used.
- Local full check.sh passes. Independent read-only review found no code-level
  blocker, confirmed bottom-row indices and per-half animation behavior. Further
  South Park doorway/corner replays are pending; no full visual approval inferred.
- Public remainsv44 until the denser-frontage candidate passes local checks.


Compact Sunset block checkpoint (candidate v47):

- Shifted only the second residential column fromx22 tox19. Six houses remain;
  the gap narrows from four16px tiles to one. First column, apartment entrance
 16,8, central rows16–23, starter/NPC coordinates and scripts remain unchanged.
  Residential side streets move tox25–27; no campaign or balance changes.
- Independent layout review found all652 non-NPC walkable tiles connected,
  every road cell accepted by the selector, and all existing events accessible.
 45 formerly walkable coordinates are newly occupied; existing resume resolver
  has safe reachable destinations for all45 in the reviewer's static check.
- Actual v46 controller save completed at19,13 (Flash section/counter verified).
  Cold Continue on v47 relocates to18,13, preserving party, HP/PP, money3500,
  Potions3 and progression. Earlier confirmation attempts stopped mid-save;
  retained as diagnostics, not counted as relocation evidence.
-1728-frame walking/running/apartment-route replay matches native/WASM every
  RGB frame, PCM sample and Flash byte. Supported pre-change coast save stays
 4,8; earned-badge save stays8,4 with badge/reward state intact.
- Local check.sh passes. South Park doorway/annex edge replay is underway.
  Screenshot comparison: .tools/benchmarks/compact-v47-frontage-review.png.
  Native art/lighting/variety still need human review; full approvals remain0/11.


v47 release validation and publication:

- Normal build at sourcecb71361 reproduces draft targetfa373906c1d315922d8e966d
  11f75b23535ec15d631472ca7990532ab47ce382 and BPS874892bytes, SHA256
 34299d8520818e9dd5846f50c3bb5833411eef2dc9ca78dc63e9de6f529e5ebf.
-2008-frame South Park office entry/exit plus both annex front-edge collision
  replay matches native/WASM RGB, PCM and Flash. Separate clinic entry/exit
  returns32,6 with earned badge, party,4000money and2Potions preserved. Native
  contact sheet confirms unobscured heads below both annexes and service doors.
- Sunset1728-frame native review.mp4 preserves walking/running, camera and
  apartment round trip. Native frame evidence is losslessly compressed after
  encoding; raw music/Flash/snapshot artifacts remain private.
- Web patch/manifest now selectv47, including the verified original Scott portrait
  checkpoint. Same existing Site/audience/authentication; no database changes.
  Supported Sites source workflow is packaging the release; public deployment
  confirmation and guest browser smoke check are pending.


v47 public deployment confirmation:

- Site37 saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_da4bfb4622548191a7bccb059088aaab
  uses source5387f469e7b05fcf0f3c42c1f82bfd47079bc2bd. Audited archive has
  exactly one current patch and manifest, with no commercial BPEE cartridge.
- Deploymentappgdep_6acf315ff810819195b8739c8bde53f3 succeeded
  2026-10-14T07:38:18Z at the existing public URL. Audience/auth unchanged.
- Actual IAB guest smoke check locally patches the supplied baseline, restores
  the existing guest slot, shows Continue with earned badge, and reaches the
  clinic field. Walking responds. This checks basic public boot/Continue, not
  full browser performance/audio gates or a human art approval.
- No GitHub Actions dispatched. Source, native fix and density change are in
  separate coherent commits. User's unrelated PDF remains untracked/untouched.
  Full-scope quality goal remains unfinished; October15 6PM Pacific stop applies.

- Deployed guest doorway smoke check also exits the clinic to South Park with
  complete courier head visible in front of the facade. Screenshot:
  .tools/browser-review/public-v47-smoke.png. Test-only tab muted, paused and
  closed afterward; original user tab remains open. Existing open sessions must
  reload the page and locally load their ROM again to use the new patch.


### 15.10 Continuous work and alignment cadence — October 14

- User reiterated: always keep going until the6PM mark, including after local
  fixes and public releases. This is October15,6PM Pacific per latest deadline.
  No task completion is inferred from a shipped subset.
- User explicitly authorizes broad collaboration with the existing alignment
  chat and requires a check-in every30minutes. Last check: October14 00:45
  Pacific /07:45UTC; next due by01:15 Pacific /08:15UTC. Main is producing
  original facade variants; reviewer is preparing the genuine trainer-intro
  comparison with a60-minute task limit. Main owns engine builds/publication.
- App goal card remains paused and stale; only the user can resume/change that
  control. Canonical spec governs current work and preserves the full objective.
  This limitation was stated to the user; no fake completion/replacement goal.


Original facade variety source checkpoint:

- Added two distinct original architectural candidates: butter-yellow with
  inset side windows and a red slatted garage, lavender with a central bay,
  flanking sash windows and scalloped cornice. Sources/exact prompts are under
  assets/tiles/sunset-rowhouse-butter and sunset-rowhouse-lavender. Built-in
  image tool used; deterministic80x80 native conversion uses15 opaque RGB555
  colors plus transparency. No commercial building art is copied.
- Native previews show different window/cornice/garage designs, not recolors.
  Per-file/source hashes include the consumed preview. Pixel cleanup/readability
  and in-game human review remain pending; art approval is not inferred.
- Loader and fixed decorative placements are staged separately from integration.
  Enterable original apartment facade/animation stays unchanged. Existing six
  house tests pass; public staysv47 while native resource expansion is developed.


Facade integration checkpoint (v48):

- Native compilation expands only Sunset's secondary graphics allocation to
 512tiles and194metatiles;406slots used including isolated wave animation slots.
  Original enterable house stays at its existing IDs. Four decorative footprints
  use two original variants. All authored collision/elevation words, event/warp
  coordinates, compact layout and animated apartment door remain unchanged.
- First private draft used reserved palette slots13/14, causing dark/miscolored
  houses. Failed native/WASM evidence is preserved; no public release used it.
  Pinned engine loads map palettes0–12. Corrected variants use unused6/7;
  regression rejects13–15. Expanded tables now rebuild from pinned Git bytes,
  avoiding double expansion after an earlier overlay.
- Corrected draft target86bb0553cd5f8f5311f0ade096c3416a28ae571d4f176dda297
 10eb4a2b002dc; patch878088bytes. Eight owning tests and full check.sh pass.
  Every RGB frame, PCM sample and Flash byte matches across native/WASM for
  the1728-frame walk/run/apartment route. Older saved19,13 relocates to18,13
  with party, HP/PP, money3500, Potions3 and progression preserved.
- Actual captured native art: facade-variety-v48-fixed-frontage.png and
  facade-variety-v48-fixed-walk/review.mp4 under private benchmarks. This28.93s
  implementation clip is not a completed30–60s matched Emerald quality gate.
- Genuine34.29s Calvin/Scott intro comparison packet is ready and requested
  for user0–4 subset review. Human approval remains pending; full domains0/11.
  Alignment thread now has a90-minute controller-only Steven/Scott route task;
  it may not alter stats/balance or count its historicalv45 route asv48 evidence.
- Goal card is now ACTIVE, confirmed2026-10-14T07:58:30Z after user resumed it.
  Keep working until the explicit October15,6PM Pacific deadline in15.1.


v48 normal release checkpoint:

- Normal rebuild at sourcec0e2dad reproduces the corrected draft exactly:
  target86bb0553cd5f8f5311f0ade096c3416a28ae571d4f176dda29710eb4a2b002dc,
  patch878088bytes, SHA256
  cc4d008cf764423bdbfed29708c42f0a0f2edd28e467e3fc445932f340584519.
  Repeat-build safety is exercised by that normal rebuild after the draft.
- Web/Sites patch manifests selectv48. Supported source workflow typecheck and
  production build pass. Audited archive contains one matching patch/manifest
  and no commercial cartridge. Native source/public changes are committed
  independently of later mechanics work. Public deployment confirmation pending.


v48 public deployment:

- Site38 saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_48afd423e59c8191b9843903a73b4823
  uses source46976905d143024f910b69fc3c111548a156a314. Deployment
  appgdep_6acf37009f3481918c0cabad67c91b03 succeeded2026-10-14T08:02:17Z.
  Existing public URL, access and authentication remain unchanged. No DB or
  GitHub Actions. Existing sessions need reload/local ROM loading to adoptv48.
- Next work moves toward the still-missing300-case mechanics gate while user
  art/audio/intro subset reviews are pending. Controlled function fixtures must
  be labeled separately from controller-only campaign/progression evidence.


Alignment check October14,01:14 Pacific /08:14UTC:

- Previous alignment turn was interrupted after winning Steven, completing
  normal save/cold resume and activating blue INPUT. Status was notLoaded;
  work was not assumed live. Explicit continuation sent from the earned state,
  with a new60-minute limit ending09:14UTC. No route restart/stat changes.
- Exchanged priorities/evidence: v48 original facade integration and24 passing
  native base-damage fixtures (including4 doubles) on main; earned first-gym
  route and weakest-slice assessment on reviewer. No approval inferred.
- Next alignment check due by08:44UTC /01:44 Pacific. Main proceeds with fixture
  identity/negative controls and documented mechanics coverage in the meantime.


Native mechanics fixture foundation:

- Added our own RAM/register fixture driver and Python identity/expectation
  runner. It executes actual CalculateBaseDamage instructions in the exact
  reference andv48 cartridges under pinned native mGBA. The campaign capture
  harness is unchanged. Fixtures are explicitly not controller-only gameplay,
  trainer wins, saves or performance evidence. No fixture ROM is published.
-24 independently specified base-damage scenarios pass against both the fixed
  Emerald reference andv48. Four exercise real doubles screen/spread/absent-ally
  branches. Covered: GenIII physical/special types, integer rounding, stat
  stages/critical-stage bypass, burn/Guts, HugePower, ThickFat, Blaze threshold,
  rain/sun and screens. Each stores a hand-derived expected integer. Final
  critical multiplier, STAB/effectiveness/randomness/HP resolution are excluded.
- Exact ROM/state/core/ELF companion and function-byte identity are checked.
  Per-case reset, explicit native ABI, RNG-before/after observation, ROM hash
  preservation, instruction/time limits and duplicate-input rejection protect
  the evidence. Schema/ABI unit checks and full check.sh pass. Three extra
  negative controls reject ROM writes, wrapped addresses and non-ROM calls;
  these controls do not add mechanics cases.
- Final evidence: mechanics-v48-base-damage-final/result.json under private
  benchmarks. Catalog: data/quality/mechanics/base-damage.json. Protocol and
  exact invocation: docs/quality/mechanics-fixtures.md.24cases count once each,
  not once per ROM. At least276additional broad scenarios/46additional doubles
  and all uncovered system gates remain. No human approval inferred.
- Next mechanics work: speed/priority/held-item/weather interactions, followed
  by stat generation, full hit/type/status resolution and capture/resource cases.


Native turn-order checkpoint:

- Added34 independent GetWhoStrikesFirst scenarios: speed/stages/paralysis,
  MachoBrace, weather abilities and six doubles partner-presence interactions,
  QuickClaw strict threshold13107, positive/negative priorities and tie branches.
  Actual reference andv48 functions match every expected winner. Three tie
  cases also match the specified LCG state advance; non-ties preserve RNG.
- Native chosen-move positions/protection/action data are explicit scratch
  fixtures. Absent slots also have0 HP. Pinned item enum values are parsed;
  no item IDs or native outcomes are guessed from observations.
- Re-ran24damage cases after shared setup changes: all pass. Total58 distinct
  scenarios,10doubles; not116 counted separately by ROM. Full local check.sh
  and fixture guard tests pass. These are still controlled native-function
  fixtures, not controller-only battles or complete action/HP resolution.
- Evidence: mechanics-v48-turn-order-initial and
  mechanics-v48-base-after-turn-support under private benchmarks. Full approval
  remains0/11. Next: actual generated stats/natures/IV/EV boundaries, then full
  action/type/status/resource/capture behavior; at least242cases/40doubles remain.


Native generated-stat checkpoint:

-40 scenarios pass actual CreateMon/SetMonData/CalculateMonStats/GetNature on
  reference andv48. Each checks seven HP/stat values, nature, level and unchanged
  RNG. Covered all25 natures, IV/EV/level rounding boundaries, distinct IV fields,
  fainted/damaged HP preservation, Shedinja exception and declared SF starter
  stat mappings. Three intentional base-stat differences have explicit separate
  reference/candidate vectors; formulas remain the same.
- Refactored common driver identity/compilation for actual reuse. Reran all
  catalogs afterward:24/24damage,34/34turn-order,40/40stats. Total98scenarios,
 10doubles, counted once each. Native input ROM hashes remain unchanged.
- Driver/runner/data source hashes, binary hashes, source commit and dirty-state
  provenance accompany final artifacts. Fixture-schema/ABI tests and full local
  check.sh pass. Native stat fixtures do not establish natural RNG distributions,
  actual EV award caps, evolution or campaign acquisition gates.
- Catalog generated-stats.json and protocol docs/quality/mechanics-fixtures.md
  are public source; complete ROMs/snapshots and results remain private under
  mechanics-v48-stats-guarded-final and sibling shared-driver evidence directories.
  Full human approval stays0/11. At least202more broad cases/40more doubles remain.


Alignment check October14,01:43 Pacific /08:43UTC:

- Alignment chat completed the historicalv45 Fire-starter first-gym route using
  normal controls: Steven won, one Scott loss to a critical hit, normal recovery,
  then Scott won. No stat edits or rollback. Earned Build Badge/stage4, exactly
  one Reflect TM, money1900 and level11 CinderCoy25/31HP survive gym re-entry,
  repeat dialogue and normal save/cold Continue. One viable preparation/recovery
  route is established; three balanced strategies/campaigns are not established.
- Main cold-loaded that actual earned battery onv48 in native and WASM:3752
  frames each. Final RGB, complete PCM and Flash match; trainer flags, badge,
  stage, money, party/moves/PP and one TM are preserved. This is save compatibility
  evidence, not a replay of the historical battles onv48. Private evidence:
  earned-alignment-v48-cold-native/compatibility-result.json and sibling-wasm.
- Reviewer now tests a fresh Water-starterv48 route with an empty save and normal
  controls only. Task is bounded to90minutes, ending by10:13UTC; report the actual
  saved checkpoint/blocker if unfinished. Capture harness remains frozen during
  that task. Main owns mechanics fixtures and source changes independently.
- Next alignment check due by09:12UTC /02:12 Pacific. No new quality approval;
  continue work through the explicit October15,6PM Pacific cutoff in15.1.


Native complete-action-order checkpoint:

-21 four-battler scenarios pass actual SetActionsAndBattlersTurnOrder on both
  reference andv48. Covered item/switch group precedence, multiple simultaneous
  items/switches, run selection, positive/negative priority brackets, paralysis,
  MachoBrace, weather abilities and AirLock, QuickClaw activation/strict threshold
  and priority interaction, and speed stages across the whole field.
- Each checks the complete battler permutation and matching action array, native
  next-turn callback, reset FocusPunch tracker and unchanged RNG. Distinct speeds
  avoid accidental tie randomness. All four participants are present; no party
  or save changes. This verifies scheduling, not execution/HP/resource outcomes.
- Shared setup extraction is exercised by rerunning every earlier catalog:
 24/24damage,34/34pairwise order,40/40stats,21/21complete sorting. Total119
  independent scenarios,31 meaningful doubles. Full local check.sh passes.
  Evidence: mechanics-v48-{base,turn,stats}-after-actions and
  mechanics-v48-action-order-guarded under private benchmarks. Full human
  approval remains0/11; at least181 broad cases/19 doubles remain.


Native type-interaction checkpoint:

- 72 distinct scenarios pass actual TypeCalc on reference and v48: one weakness
  per attacking type that has one, one resistance for each of the 17 standard
  types, all seven basic immunities, neutral cases, dual-type stacking and
  cancellation, STAB and integer rounding, Levitate, Wonder Guard, Foresight,
  Struggle and minimum damage. This is not the entire ordered type matrix.
- Every scenario checks both result flags and intermediate damage. Levitate and
  Wonder Guard blocking flags do not necessarily zero the intermediate value;
  actual subsequent HP resolution remains a separate required gate. No doubles
  count is added for isolated two-participant type calculations.
- An initially redundant monotype scenario was rejected by the duplicate-input
  guard and omitted. Failed evidence is preserved; it is not counted. All 119
  earlier cases pass after shared ABI/profile changes; full local check.sh passes.
- Private results: mechanics-v48-type-effects-deduplicated and
  mechanics-v48-{base,turn,stats,action}-after-types. Public catalog:
  data/quality/mechanics/type-effects.json. Total 191 scenarios / 31 doubles;
  at least 109 broad cases / 19 doubles remain. Human approvals stay 0/11.


Native accuracy-command checkpoint:

- 54 scenarios pass actual Cmd_accuracycheck on reference and v48, including
  15 meaningful doubles. Explicit hit/miss branch, result flags, miss message,
  consumed hit markers and final RNG are checked. Native seeded LCG expectations
  are authored mathematically, not inferred from observed outcomes. This does
  not establish natural RNG distributions or complete attack execution.
- Coverage: exact accuracy thresholds, accuracy/evasion stages and clamps,
  CompoundEyes, Hustle physical versus special, BrightPowder, LaxIncense,
  Foresight, rain/sun Thunder, Swift/VitalThrow, Protect, LockOn ownership,
  airborne/underground/underwater states and consumed bypass markers. Doubles
  exercise active/absent partner AirLock/CloudNine weather suppression and
  spread-move miss messages. Protection/invulnerability precedence is explicit.
- All earlier 191 cases pass after shared ABI changes. Full local check.sh and
  accuracy input guards pass. Private final evidence: mechanics-v48-accuracy-guarded
  and mechanics-v48-{base,turn,stats,action,types}-after-accuracy. Public catalog:
  data/quality/mechanics/accuracy.json. Total 245 scenarios / 46 doubles; at
  least 55 broad cases / 4 doubles remain, alongside uncovered required systems.
  Human approvals remain 0/11; counting cases alone cannot complete the gate.


Native critical/resource checkpoint and 09:08 UTC alignment:

- 23 critical-hit cases, 16 PP cases and 14 HP cases pass on both ROMs. Critical
  coverage includes stage odds/clamping, FocusEnergy, high-critical moves,
  ScopeLens, species-specific items and suppression. This checks deterministic
  branches and exact RNG transitions, not empirical probability distributions.
- PP checks normal/Pressure costs, opposing versus all-field spread targets,
  zero saturation, temporary moves, bypass markers and controller deferral.
  Six new doubles bring the total to 52. HP checks actual loss/heal saturation,
  physical/special retaliation trackers, overkill, missed/immune results, passive
  damage, Substitute absorption/bypass, PainSplit and controller deferral.
- An initial PP/HP fixture run exposed missing default RNG initialization. Fixed
  the harness to seed explicitly; original expectations were retained and all
  cases rerun. Failed artifacts remain. Final results: mechanics-v48-{critical,
  pp,hp}-seed-guarded. Earlier 245 cases pass again in the after-resources runs;
  full local check.sh passes. Total 298 scenarios, 52 doubles. Status/capture,
  the complete type matrix and integrated move resolution still need coverage;
  the mechanics gate remains open regardless of reaching a numerical minimum.
- These commands mutate private battle RAM and queue controller updates. They
  do not establish durable party/save writes, complete attacks or campaign wins.
- Alignment chat is active on the fresh Water route: BrinePup level 8 learned
  MudSlap normally; BinPossum recruited; clinic revived/healed both and cleared
  contact paralysis. Shared the earned Fire save compatibility and fixture
  results, and requested exact checkpoint artifacts plus first-play clarity gap.
  Existing finite task ends by 10:13 UTC. Next alignment check by 09:38 UTC.
  Public remains v48; human approvals remain 0/11.


Original courier battle-back checkpoint (private v49):

- Built-in image generation produced four original throw poses matching the
  existing courier beanie/navy jacket/orange messenger bag. Source and exact
  prompt are saved in assets/characters/courier-battle-v1. Native conversion
  aligns waist anchors with a common scale, 64x64 frames and 15 opaque RGB555
  colors. It does not copy commercial trainer artwork. Human approval pending.
- First private draft exposed a native frame-order mismatch: the engine waits
  on frame3, so the authored follow-through incorrectly appeared while waiting.
  Preserved that draft/capture and remapped source poses to native order1,2,3,0.
  Corrected capture visibly waits neutrally, then winds up/throws. Native timing,
  movement, four-frame ABI and battle rules are unchanged. Regression covers
  idle-frame mapping, native tile decoding, geometry and palette/hash identity.
- Corrected private target45985c62da0fbe8c8e3a6a2b0041856e06f6f50a71beaa3c8
  aea5c6d80d7a052; patch881879 bytes. Both player selections use the original
  courier back art with a dedicated palette. Native audit proves six other back
  graphics, original player front palettes and Scott portrait/palette unchanged.
- Actual earned recovery battery cold-loads with level10 CinderCoy29/29HP,
  money1100, Potions2 and stage3 preserved; controller-only approach reaches
  Scott. Cold1712 and approach2232 frames match final RGB/PCM/Flash across cores.
  Every RGB frame of the2452-frame intro, complete PCM and Flash match. Private
  evidence: courier-v49-mapped-{cold,approach,intro}-{native,wasm}, parity.json
  and native-resource-audit.json under benchmarks. Full local check.sh passes.
- Public stays v48 until normal release packaging/deployment. All298 mechanics
  cases also pass on this corrected immutable target in mechanics-v49-*-mapped. No quality domain is
  approved by these implementation checks; the complete campaign remains open.


v49 normal-release packaging:

- Normal rebuild from source0fc1eb64acdbd691992921a2ac427ab35194c9b4 reproduces
  corrected target45985c62da0fbe8c8e3a6a2b0041856e06f6f50a71beaa3c8aea5c6d80d7a052.
  Patch881879 bytes, SHA256
  fc9e6fd70eaf32320879961943359ef4693ef4ab1ec07baa0a878a875182f242.
  BPS roundtrip is byte-identical; only patch/manifests enter public sources.
- All298 focused mechanics cases also pass on this exact corrected target
  (mechanics-v49-*-mapped). Public release manifests selectv49; Sites checks/build
  and publication are in progress. Current public remains Site38/v48 until the
  deployment result confirms otherwise. No GitHub Actions or DB changes.


v49 public deployment and initial browser QA:

- Site39 source792cd454e3b31ed39aa4c3b4fe736376ba159a6a passed typecheck and
  production build. Saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_6ce44c86d2d08191aea8d64b08cd4b6a;
  deployment appgdep_6acf4b190eb08191a0e33c2fe81baa81 succeeded at
  2026-10-14T09:28:01Z. Audience/auth remain unchanged. No DB/GitHub Actions.
- Archive identity audit confirms one v49 patch/manifest and no commercial-derived
  cartridge. Earlier extension/name guards were too broad: the archived original
  67820-byte SFMM homebrew prototype and AppleDouble metadata remain distinct
  from the BPEE hack. Exact original checksum verified; failed audits preserved.
- Actual public browser selected the local Emerald base, patched it on-device,
  and exported a16777216-byte GBA file with exact target45985c62...d7a052 hash.
  Save-backup UI also exported131072 bytes. Existing guest save was auto-restored;
  no test save was imported over it and no in-game save was performed. Native
  cold load of those actual downloaded files is being checked. This is not yet
  a completed browser/native/browser roundtrip or fresh authentication gate.


v49 public export/resume verification completed:

- The actual website-exported ROM and128KiB guest backup cold-load under pinned
  native mGBA: clinic position6,8, stage4/badge, money4000, Potions3 and level11
  CinderCoy4/31HP with moves/PP intact. Private evidence:
  courier-v49-public-export-native-cold-mounted. The capture harness requires
  project-local paths, so byte-identical copies of Downloads files were used;
  the initial outside-root invocation was rejected before emulation.
- The browser also visibly reaches Continue (one badge) and the SF clinic from
  that existing guest slot. No test save imported, no in-game save performed;
  the temporary QA tab was muted, paused and closed. Screenshot:
  .tools/browser-review/public-v49-resume.png. Download identity receipts:
  courier-v49-public-{rom,save}-download.json under private benchmarks.
- This establishes local patching, usable GBA export, backup download and one-way
  browser-to-native save compatibility. It is not one of the ten completed
  browser/native/browser save roundtrips. Authentication isolation, Safari/mobile,
  sustained browser performance/audio and human quality gates remain open.


Alignment check October14,02:37 Pacific /09:37 UTC:

- Reviewer completed a fresh Water-starter v48 route from no battery/state through
  the first badge. All110 controller captures have verified parent/input hashes.
  Both wild encounters became recruits; no repeated wild XP farming. Steven
  caused one teammate faint, restored at the clinic; Scott won on first attempt
  without blackout/rollback. Native route evidence does not establish pacing.
- Earned battery e79664352a1c4108814a28527b4b8a8d98e98db5f6c3398afaebfac063cfcbad
  is brine-route-alignment-109-earned-badge-saved/capture.sav. Full receipt:
  brine-route-alignment-110-earned-badge-cold/fresh-water-route-result.json.
  Stage4, all three trainer flags, one Reflect TM, money3000, one Potion/five
  capture items; BrinePup10(27/33HP), BinPossum4(17/17), Hushmoth5(13/19).
- Main bridges that earned battery onto v49 native/WASM: final RGB, complete PCM
  and Flash match, with team/resources/badge preserved. Evidence:
  brine-earned-v49-cold-{native,wasm}. This is compatibility, not a fresh v49 run.
- The reviewer identified surprise sight-triggered practice encounters and vague
  preparation advice. New read-only20-minute task ends09:57 UTC: locate precise
  pre-sightline script hooks and propose roster/type/free-clinic guidance, keeping
  native sight behavior and balance. No new route or source changes delegated.
  Next routine alignment check by10:07 UTC; collect a completed report earlier.

Matched courier/trainer subset review:

- Added trainer scope to the existing private comparison packager. New34.289s
  packet uses genuine Emerald Calvin and current v49 Scott/courier, each2048
  native frames with the same controller sequence,3x nearest scaling, no retiming
  and two selectable original audio streams. Full encode/identity guards pass.
- Private video courier-v49-paired-intro-review/comparison.mp4, SHA256
  076ca5c24f4ad2d03b5cc2b565eca513ccf2b6d6e5bc8883bcdd458976058d81.
  Receipt records different trainer classes/teams/dialogue/scene timing and the
  earned candidate/reference lineage. Requested user0–4 courier art/throw subset
  review; no response or full-domain approval inferred.


Native status-application checkpoint:

- 38 SetMoveEffect scenarios pass reference and current v49, including5 meaningful
  doubles. All seven ordinary/volatile status effects are covered, sleep/confusion
  duration boundaries, prevention abilities/types, existing status, fainting,
  Substitute, secondary ShieldDust/Safeguard, ability-origin bypass, sun freeze
  prevention, active/absent weather suppressors and ally Uproar/Soundproof.
- Each verifies target status1/status2, script destination, stack depth, queued
  controller update, effect byte, ability/result flags, hit markers and exact RNG.
  Expected script roles are explicit whitelisted ELF labels, not observed output.
  Scratch resource stack/history allocations are initialized; no save exported.
- This is status application only: outer move scripts, secondary-effect chance,
  Synchronize execution, residual damage, status recovery and presentation remain
  separate coverage. GenIII rules are preserved, including Electric-type paralysis
  eligibility. Existing primary-status-move Safeguard/type checks are not bypassed
  in the game merely because this isolated function has a narrower role.
- All earlier298 cases pass again after shared changes; full local check.sh and
  oracle guards pass. Final evidence: mechanics-v49-*-after-status. Total336
  scenarios /57 doubles meet numerical minimums, but the mechanics gate remains
  open for capture, full type matrix, integrated move resolution and coverage
  review. Human quality approvals remain0/11. Public game stays v49.


Preparation guidance checkpoint (private v50):

- Applied the alignment audit through four existing dialogue labels: first Scott
  delivery/reminder, TEAM PLAN and clinic sign. Players are warned that optional
  practice triggers on sight, can read both level5 rosters/types, learn Bide and
  the Grass matchup, and find free healing/revival east at Justine's clinic.
  Native compiled trainer team/move/item bytes and scalar AI/reward fields match
  v49 exactly; sightlines, map positions and progression logic are unchanged.
- Private target edcd4d8554820b60d69f0e89c617da59248e54f874f1f08bbcd495718a007d78,
  patch882803 bytes. Native source lines measure at most202px; actual seven-page
  TEAM PLAN capture shows complete text fitting at native size.3416 RGB frames,
  complete PCM and Flash match WASM. A first shorter capture did not give every
  page enough printing time; preserved and reran with complete page waits.
- Fresh Grass route supplied a normal pre-Scott v49 battery (Sprout5/BinPossum3,
  money3500,3 Potions,4 capture items, stage0/no trainer flags). Onv50 it cold-loads
  correctly and reaches first delivery before sightlines. All2928 delivery frames
  and976 clinic-sign frames match RGB/PCM/Flash across cores. All pages fit,
  delivery advances stage0 to1 and keeps team/resources intact.
- Evidence: preparation-v50-complete-pages-{native,wasm}, first-delivery-pages
  and clinic-sign-pages siblings, dialogue-parity.json, trainer-preservation.json.
  Full local check.sh passes. All336 mechanics scenarios pass against
  the new immutable target (mechanics-v50-*-guarded). Public remains v49 pending normal packaging/deployment.
- 09:52 UTC alignment exchange: preparation audit completed and received. A new
  bounded90-minute fresh Grass v49 first-badge route is active, ending by11:22 UTC;
  supplied pre-Scott save22 without rollback and continues sequentially. Reviewer
  writes private route evidence only; main owns source/builds. Next check by10:21 UTC.
  Capture harness remains frozen; no quality approval inferred.


v50 normal-release packaging:

- Source1cab3587c62fc1b4d9e1821cc57c431c0b18e5f4 normal rebuild reproduces
  edcd4d8554820b60d69f0e89c617da59248e54f874f1f08bbcd495718a007d78 exactly.
  Patch882803 bytes, SHA256
  9aa89b313e7a37bba2edf03261a188e766f3c453936f63e0236819ab7ec14b99.
  All336 native mechanics scenarios pass this exact target. Web manifests select
  v50; Sites checks/build/publication are in progress. Public is still Site39/v49
  until a deployment result confirms otherwise. No DB/GitHub Actions.


v50 public deployment:

- Source1b2ae6b3c0f1cbd6ab8fa31773b8f1159f2557e4 passed Sites typecheck and
  production build. Exact archive audit found84 files, one matching patch/manifest,
  no commercial-derived cartridge and no AppleDouble metadata. Original SFMM
  homebrew prototype identity is separately verified.
- Site40 saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_9598368d13088191932214eef8e37783;
  deployment appgdep_6acf551a048c8191828b84de8909c5bc succeeded at
  2026-10-14T10:10:41Z. Existing public URL/auth/audience unchanged. No DB/GitHub
  Actions. No separate actual-browser v50 replay claimed beyond prior v49 export
  checks and exact v50 native/WASM render/save tests.
- Continue with South Park street density while the finite Grass route and user
  comparison review proceed. Preserve door/recovery locations if possible and
  prove older saves escape any newly occupied tiles. Full scope/gates stay open.


Grass first-badge and alignment checkpoint October14,03:32 Pacific:

- Reviewer completed a fresh Grass v49 first-badge route:143 controller captures,
  normal inputs, no state edits/rollback/XP farming. Walden13 rounds, Steven8,
  Scott44; all first attempts. Hushmoth fainted, Sprout retained paralysis.
  All8 Potions used,7 against Scott; this is a difficult viable route, not balance
  approval or evidence for a nerf. The57:17 game clock includes automation waits.
- Earned battery sprout-route-alignment-142-earned-badge-saved/capture.sav SHA256
  9bd05b8efc687de3486a97219bc2a4980354e9afd14e428b83e169b4c2726b1e; report
  sprout-route-alignment-143-earned-badge-cold/fresh-grass-route-result.json.
  Stage4/all3 trainers, one Reflect TM, money3400,0 Potions/3 capture items.
  Sprout11(20/32HP,PAR), BinPossum3(15/15), Hushmoth3(0/15).
- Actual earned battery cold-loads onv50 with native/WASM final RGB, full PCM and
  Flash identical: sprout-earned-v50-cold-{native,wasm}/compatibility-result.json.
  This is compatibility only. Three first-badge routes do not satisfy the three
  full starter campaigns, performance or ten complete save-roundtrip gates.
- Alignment completed a finite South Park geometry audit: connected services and
  adventures,24 newly blocked/12 freed cells, native relocation model within2tiles.
  Follow-up checks external resource references and immutable compiled cells.
  Next bounded read-only task reviews remaining mechanics/capture/type coverage,
  ending by11:02UTC. Main retains source/build ownership; harness remains frozen.
  Next routine check no later than11:02UTC, collect finite task completion earlier.

Private v51 South Park frontage:

- Move the upper coral annex to18,2, add existing original butter facade at23,2,
  retain lower coral11,20. Largest north-frontage sidewalk gap12→3 tiles. Gym and
  clinic doors, recovery, signs, NPCs and adventure anchors stay fixed.
- Prune pixels only for seven unreferenced terrain metatiles; keep all IDs,
  attributes and referenced cells. New allocation490/504 graphics tiles and134
  metatiles. Native service-door VRAM remains reserved. Border references prevent
  pruning; tests verify all seven. No tileset animation callback is introduced.
- Actual normal v50 saves at19,4 and24,4 cold-load onv51 at17,4/22,4. Native/WASM
  final RGB, complete PCM and Flash match; team/money/items/stage preserved. Both
  older batteries were first cold-verified onv50; no RAM/save-coordinate edits.
  Evidence density-v51-old-save-parity.json, gap-{19,24}-cold-{native,wasm}.
- Normal approaches stop at coral19,6/westedge17,3 and butter24,6. Each service
  entrance matches all316 RGB frames/PCM/Flash across cores; normal exits return
  to13,6/32,6 with final RGB/PCM/Flash identical. Door evidence:
  density-v51-{gym,clinic}-{enter,exit}-{native,wasm}, door-parity.json.
- All336 mechanics scenarios pass this immutable target,57 doubles; full mechanics
  coverage gate remains open. Full local check.sh passes; seven focused resource
  tests include packed native pixels/palette/underlay, bounds, graph and border
  retention. No human quality approval, full campaign or publicv51 claim.
- Independent alignment decoding of immutable v50/v51 ROMs confirms all115
  nonpruned prior metatiles render identically, all122 prior attributes and
  registered door bytes match, and South Park has zero retired-ID references.
  Evidence density-alignment-20261014/pruning-review/compiled-v50-v51-proof.json.


v51 normal-release packaging:

- Source3aa702f1b7b215fd984a17b0e4fe4ccfb0bce139 reproduces immutable target
  ba3d954bcbb4b83a33f81e9d646ea47960faf89c56956703170f127e87314abe.
  BPS883582 bytes, SHA256
  bc002513051832df649135e8fafa57a3b0b2411a1d4032161f95a632252fbea9.
  Web patch/manifest updated; Sites packaging/publication pending. Public stays
  Site40/v50 until deployment succeeds. No DB changes or GitHub Actions.
- Alignment external-reference audit found no unsafe active reference. Clinic
  writes542/543 belong to its own tileset; South Park callback isNULL. Added
  explicit checks that every new decorative butter cell has no door behavior
  and remains blocked, including global635 shared with a Sunset door-table row.
  Border retention, seven park resource tests and two door tests pass.


v51 public deployment:

- Sites source d100e53208bdb8acb84bfde4ed937b7dfb33c8c1 passed typecheck/build.
  Exact archive audit:84files, one matching BPS/manifest, no commercial-derived
  cartridge or AppleDouble metadata. Original SFMM homebrew identity verified.
- Site41 saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_12407711e1bc8191bff534b1bede0665;
  deployment appgdep_6acf5a7150dc81919487dcf61f69fea2 succeeded at
  2026-10-14T10:33:29Z. Public URL/auth/audience unchanged. No DB/GitHub Actions.
  Evidence density-v51-public-archive-audit.json; actual-browser v51 QA pending.
- Alignment pruning audit complete with no unsafe active references. Next finite
  mechanics coverage audit active until11:02UTC; continue implementation meanwhile.


v51 actual-browser and capture-command checkpoint:

- Public IAB applies the approved local base and exports GBA SHA256
  ba3d954bcbb4b83a33f81e9d646ea47960faf89c56956703170f127e87314abe, exactly
  the native target. Existing guest Continue resumes one badge in the clinic,
  exits normally into South Park and shows the new butter frontage. Screenshot
  .tools/browser-review/public-v51-frontage.png; ROM receipt
  density-v51-public-rom-download.json. No test-save import or in-game save;
  temporary QA tab muted/paused/closed. Not a full save roundtrip/performance test.
-28 capture-command scenarios pass reference/v51, bringing total364/57 doubles.
  Observe five shake outcomes, RNG thresholds, basic ball differences, statuses,
  odds254/255, party-full message, busy/trainer/tutorial paths, attempt saturation
  and the pinned Master RNG edge. Actual fixed Pokemon objects and command calls,
  controlled RAM/register setup; no campaign or inventory/storage proof.
- Initial controller-buffer write exceeded the fixture parser bound; failed
  evidence retained and runner writes split into1024-byte chunks. No oracle
  changed after execution. Capture driver/core/harness unchanged. New strict
  allocation, vector and write-bound guards/local check.sh pass. Final evidence
  mechanics-v51-capture-guarded. All full-domain approvals remain0/11.


Complete native type-chart checkpoint:

- Added247 previously uncovered ordered monotype pairs, independently specified
  from pinned reference relationships before execution. Combined with42 existing
  pairs, all17×17=289 native relationships pass reference/v51; retain the30
  existing interaction/boundary cases. No duplicate42-pair count.
- TypeCalc flags and intermediate damage are checked, with179 neutral/57 resisted/
  46 super-effective/7 immune pairs. Dedicated dataset guard checks exact full
  product, unique pairs, flags/damage and42old/247new counts. Full check.sh passes.
  Evidence mechanics-v51-type-matrix-initial. Total611/57 doubles; integrated
  move resolution, capture integration, SF species mappings and full gate remain
  open. No public patch change is needed for these verification tools/vectors.


All native ball-command branches and alignment checkpoint:

- Capture55/55 reference/v51: all12 balls, Net type conditions, Dive map context,
  Nest levels, Timer cap/wrap, stored Luxury/Premier, integer-rounding order,
  Repeat seen/caught mirrors and Safari factors. Total638/57 doubles.
- Intermediate47-case run passed46 because fixture wrote cached mapheader rather
  than saved location. Fixed scratch setup and added native map-type observation;
  original capture outcomes unchanged.47/47 then55/55 pass. Failed run preserved.
- Compile capture_layout.c with actual pinned agbcc before native execution.
  Modern ARM GCC nested save layout differed and was rejected; native save sizes
  0x3d88/0xf2c and relevant offsets are verified. Native Repeat setters populate
  mirrors; owned-only invalid data is cleared as expected. Controller harness and
  fixture driver unchanged; full local check.sh passes.
- Evidence mechanics-v51-capture-native-map-context and
  mechanics-v51-capture-all-balls-initial. Isolated command proof only; inventory
  consumption, actual delivery/storage, Dex registration and campaign saves open.
- Alignment read-only mechanics audit completed early. New bounded implementation
  task owns only new move_pipeline_fixtures.py/test/catalog paths; main owns
  capture/shared tools/spec/builds. Task ends11:50UTC; next check by11:18UTC.
  It must distinguish script resolution from controller presentation/full turns.


Capture-to-party/PC delivery checkpoint:

- Eight shared-state native capture/delivery chains pass reference/v51. Capacity
  boundaries: final party slot even with fullPC, first/last box slots, box13→0
  wrap,420th final space and full refusal. Party preserves45/90HP,PAR and3PP;
  boxed Tackle restores35PP or56 with3PPups. Own original-trainer ID matches
  normal wild creation; encrypted checksums and all nondestination bytes pass.
- Native storage/Pokemon/save ABI verified with agbcc; PC boundary canaries
  intact. Initial foreign-OT fixture exposed invalid encryption precondition,
  corrected creation to recipient ID without changing outcomes. Failed evidence
  preserved. Common ABI helper refactor also passes all55 capture cases.
- Evidence mechanics-v51-delivery-boundary-guarded and
  mechanics-v51-capture-after-abi-refactor. Three new focused guards/fullcheck.sh
  pass. Total646/57 doubles; actual bag handler, Dex registration, controllers
  and durable capture-save paths remain open. Full-capacity refusal test bypasses
  the UI guard intentionally and does not claim actual no-spend UI evidence.
- Alignment returned ten passing bounded move-effect-script scenarios. Main
  requested duplicate-state and post-run ROM-integrity guards; both added and
  fresh native evidence passes. Main review/commit pending; not counted yet.


Native move-script integration checkpoint:

- Main reviewed alignment's ten independently specified actual move-effect-script
  scenarios, requested effective-state deduplication and post-run ROM hashes, and
  verified both guards. Native interpreter executes cancellation/accuracy/PP/crit/
  damage/STAB/type/randomHP/secondary paths to MoveEnd entry. Queued controller
  PP/HP/status payloads, script opcodes, exact RNG and scratch canaries pass.
- Extracted finite native PTY transport for coherent commits and reuse. Final
  main-reviewed source passes10/10 reference/v51 at
  mechanics-v51-move-pipeline-split-transport. Eight focused guards/fullcheck.sh
  pass. Total656/57 doubles; no full turn, fainting, residual, party sync,
  presentation/performance or durable-save claim. All human full domains0/11.
- Continue native move-end/residual verification with the alignment chat and
  hands-on desktop browser save roundtrips, keeping existing public guest saves
  isolated from QA. Public patch remainsv51/Site41; tooling needs no redeploy.


Save-roundtrip QA preparation:

- A finite localhost production-worker session serves exact Site41 source/client/
  WASM/patch from http://127.0.0.1:18765, with6000-second hardstop. Its guest
  origin is isolated from the public guest save. No DB/binding/access changes.
- Normal-controller Grass-earned save continuation deposits BinPossum in Box1;
  Sprout remains paralyzed and Hushmoth remains fainted in the party. Complete
  native PC exit/ordinary save baseline is in progress; zero new roundtrips
  counted yet. Localbrowser paused/muted until that baseline is ready.
- Alignment audits normalization: actual old save already has clock flag0,
  Safari0, species revision8 and consistent Dex mirrors. Must prove those on
  post-deposit baseline. Encryption normalization includes all64 stats, five
  bag quantity pockets, money/coins and BerryPowder; party/PC bytes remain raw.
- Temporary human notification restriction: no WHOOP/Dhoop/vibration/ready buzzes
  through2026-10-14T21:26:57Z; do not queue or replay suppressed alerts. Ordinary
  updates/work continue. Alignment chat has the restriction too.


Native residual-phase checkpoint:

- Main reviewed/reran21 native field/battler end-turn-phase scenarios. Native
  selectors and callback-wrapper scripts execute through end2; both phases
  restore callbacks with empty stacks, expected trackers/order and no outcome.
  Exact HP/status/status3/weather/duration/screens/RNG, selected effect/damage
  and intermediate HP controller payloads match independent oracles.
- Poison/burn/toxic, Leftovers/Ingrain, LeechSeed/LiquidOoze, sandstorm/rain/sun,
  Reflect and healing-before-poison interactions covered. Main receipt
  mechanics-v51-residual-main-review:21/21 both ROMs; interpreter-call totals
  are in individual receipts; no extra scenario count per opcode/checked field.
- Eight strict schema/phase/callback/controller/canary/deduplication guard units
  and full localcheck.sh pass. Total677/57 doubles. Move actions, move-end,
  fainting, party synchronization, full turn, presentation and saves still open.
- Next alignment task is read-only save-normalization audit, ending11:45UTC.
  No ROM build, workflow, deployment or recurring monitor for these tool changes.


Flash import safety correction (publication pending):

- Alignment found the earlier synthetic wrap fixture used reversed physical
  slots. Native SaveValidStatus chooses unsigned maximum except exactFFFFFFFF/0,
  then CopySaveSlotData loads counter%2. Web validator now uses that same choice
  and requires a complete matching physical slot. Equal counters select the
  parity slot's actual schema; another slot cannot hide unsupported data.
- Corrected synthetic wrap positions, added far-apart unsigned counters, unsafe
  parity rejection and equal-counter/schema checks. Valid earned populated
  counter5 save remains accepted. No save bytes rewritten or import attempted
  before validation. New code is under local checks, public remainsSite41.


Site42 native Flash validation deployment:

- Source286f9b0bae7cf7874e89a70ca1721ed24559bf2e passed Sites typecheck/build.
  Audited84-file archive has one exact v51 patch/manifest, no commercial-derived
  cartridge/AppleDouble metadata; original SFMM prototype identity verified.
- Saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_64992b874298819189b5007e0816c26c;
  deployment appgdep_6acf6ad1c5808191b83fec6422ceb8e1 succeeded at
  2026-10-14T11:43:20Z. PublicURL/audience/auth unchanged, same v51 GBA hash.
  No DB/GitHub Actions. Actual import-retention UI checks are next.
- Local worker restarted from this exact source/build BEFORE cycle1, with a new
  6000-second hardstop. Fresh baseline counter5 has party2 (PAR Sprout, fainted
  Hushmoth), Box1 BinPossum; clock0/Safari0/revision8/consistentDex verified.
  Zero completed roundtrips yet; origin remains isolated from public guest.
- Read-only flash_audit.py never rewrites batteries. Twenty independent synthetic
  guards pass for CRC/rotation/recovery/native slot choice, all24 Pokemon layouts,
  key normalization, all declared domains, time/stat bounds and corruption.
  Synthetic tests are not gameplay/save-transfer evidence.


Actual desktop save-transfer cycle1:

- Site42 localhost IAB rejects synthetic wrong-slot/truncated imports, then
  exports exactly the original baseline131072 bytes (SHAfa2e377bf3153c6ecde01c
  06567b6c30b8c098dde2ef05695b49563afa81e1c9). Evidence
  roundtrip-v51-invalid-inputs/retention-result.json. Current progress retained.
- Native counter5 → actual browser ordinary Save6 → native coldContinue and
  ordinary Save7. All declared persistent domains match, including raw600-party
  and33744-PC bytes, settings, flags/vars, money and decrypted inventory.
  Cycle receipt roundtrip-v51-cycle-01/complete-cycle.json; source/core identity
  and complete consecutive lineage in roundtrip-v51-actual-browser-ledger.json.
- Count1/10 desktop direction subtest only. Public auth/isolation, other devices,
  close/reopen persistence,50 campaign checkpoints and full save release gates
  remain open. Cycle2 in progress; public guest origin untouched.


Native item-effect checkpoint:

- Main reviewed the alignment chat's three new files and independently reran
  mechanics-v51-item-effects-main-review:34/34 reference/v51. Eight focused
  schema/object/resource/controller/canary guards pass. Pinned native ABI and
  actual Main.inBattle bitfield mask verified; fixed whole-mon oracles include
  all600 party bytes, battle objects, inventory/save resources and exact RNG.
- Healing/revival/cures/PP restoration include clamps, no-effect cases, toxic
  counters, PPups and seven direct battle contexts. HP queries remain pending
  without fabricated replies. No actual bag action/consumption, battle Revive
  dispatch, UI/full turn or durable-save evidence claimed. Total711/57 doubles;
  complete mechanics gate and all human full quality domains remain open.
- Actual save-transfer cycle2 also passed native9 after browser8; cycle3 underway.
  Isolated Site42 localhost guest only; public auth/device/full save gates open.
- Alignment now reviews the smallest Stage B visual improvement read-only,
  reporting by12:25UTC with a12:35UTC hardstop; no monitor/build/deploy.


Service-sign differentiation in progress:

- Alignment read-only art review identified gym/clinic/history signs all using
  generic metatile540. Added two original native16x16 cream/navy emblems: code
  chevrons for Cognition and a heart for clinic care. No new palette/footprint.
  Existing sign scripts/positions and actual service doors583/618 stay intact.
- Resource audit preserves every old graphics/record/attribute byte and all
  palettes, appending two metatiles:498/504 tiles,136metatiles. Eight focused
  park tests pass, including safe door VRAM, transparency/underlay, native
  decode, separate history sign and reachable interaction positions.
- v52 source awaits native build/actual dialog-door/controller and WASM checks;
  public remainsv51/Site42. No human visual approval inferred from this change.
- Actual desktop save cycles1–4 complete consecutively (native counter13);
  cycle5 in browser now. Full save/auth/device/campaign gates remain open.


Verified v52 service-sign release (public deployment pending):

- Normal source builda81ac69929d51dfae3eab6f32a4bd0de98e976f1 reproduces
  draft targetf45c62fe57188f96349adb2e4c001a88356c2ec854c88a54ec66a8804d08bef0.
  Patch882173bytes SHA44579e29a8453662ed49a60bd40a192669bcd95b1adcce742402d411699f40f9.
  Exact independent BPS reapplication passes; only patch/manifest are public.
- Native ordinary old-save Continue relocates the v50 gap save to17,4, then
  normal controls reach/read both new signs at10,7 and29,7. Gym and clinic
  display their correct existing dialogue pages. Four sign/dialog finalRGB/PCM
  checks match WASM; delayed clinic text required another normal close input,
  preserved failed approach evidence was not counted as successful movement.
- All316 RGBframes and PCMbytes match for each gym/clinic entry and exit.
  Expected interiors and sidewalk returns13,6/32,6 verified. No save-transfer or
  real-browser performance claim from these controlled frame captures. Evidence
  service-signs-v52-resources/{runtime-parity,door-parity}.json.
- All16 mechanics catalogs independently reran on this immutable v52 cartridge:
  mechanics-v52-summary.json711/711,57 doubles; complete mechanics gate open.
- Six actual desktop save cycles passed consecutively through native17. Seventh
  in progress. CUA import/download provenance is retrospectively indexed from
  actual tool events, explicitly not independently cryptographically attested.
  Alignment audits final sealing; localhost Site42 assets remain frozen.


Ten-cycle desktop save-direction subtest sealed:

- Ten consecutive actual IAB imports/Continue/ordinary Save/backup exports, each
  followed by native coldContinue/ordinary Save, pass. Twenty ordinary saves
  advance native counter5→25; final browser24. Raw party600/PC33744bytes, full
  declared settings/locations/Dex/flags/vars/inventory/money/resource domains
  preserve expected semantics through native encryption-key changes. Both Flash
  slots valid, previous active slot and special sectors unchanged on each leg.
- Independent final audit rehashes all ten chronological rows, capture metadata,
  parent battery/state and controller CSV identities, frozen harness/core/client,
  actual raw UI downloads and final downloaded v51 ROM. Final actual file
  sf-mini-monsters(21).gba matches targetba3d954...314abe. UI observations are
  retrospectively indexed from CUA tool events, not cryptographic UI attestation.
- Seal roundtrip-v51-final-seal/final-seal.json SHA256
  f909e2bfef80f6c3152a482f4354bef63d2b79f3170e257fca7db6c3574f4682.
  Private final audit helper7602beca...61cb6 explicitly keeps full release false.
  First Continue legitimately refreshes cached mapView, unused template script
  pointers and Rival TV layout outside declared domains; whole opaque save-block
  byte invariance is not claimed. Native playtime bounds and source pins pass.
- Scope: one earned first-badge checkpoint, one isolated desktop IAB guest
  session with exact Site42 assets, pinned native mGBA. This does not complete
  public sign-in/isolation, Safari/physical mobile, fresh-session persistence,
  fifty distinct campaign resumes, full campaigns or the whole release gate.
- Temporary QA tab closed and only its finite worker process group stopped
  before Site source changes. Existing public guest origin remains untouched.
- v52 publication preparation preserves the complete prior dist directory. A
  private copy of the Sites1.0.1 helper retains staging output instead of its
  deletion cleanup; installed plugin/source/publication semantics unchanged.
  Site43 typecheck/build/archive preparation underway; public stillSite42/v51.

Next visual work: original fictional Roon amber-hood field atlas drafted with
imagegen, source360a740...9cf5. Native review isolates18 proposed west-stride
pixel changes; source/likeness/animation approval remains pending. No registry
integration or new game build claimed for this draft. All full human domains0/11.


Site43 v52 deployment and independent final review:

- Site source071a6c7f5fa42a9ff0ba6d562f00976b0e3c029d typecheck/build passed.
  Audited84-file archive SHA18ddb95ecc93638f8c40e55647b40ee51dac0b14b397d52366aa9bb579361dc4
  contains exact v52 patch/manifest, original SFMM prototype, zero commercial
  full cartridges/private saves/AppleDouble. Installed helper stayed unchanged.
- Saved Site43 version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_eeb71c2cc30881918c8ecd1b952298f6;
  deployment appgdep_6acf79b994ac8191b0c7b450b958b169 succeeded
  2026-10-14T12:46:56.778748Z. Public audience/auth/DBbindings unchanged.
  No GitHub workflow runs, DB migrations or access changes.
- Actual public IAB loader and Download SF patch event pass; downloaded882173
  bytes match SHA44579e29...f40f9. Public guest ROM/Continue were not touched;
  temporary tab closed. Browser-user-agent HTTP requests without auth/cookies
  also retrieve exact public manifest/patch200; default Python-agent probe403
  was not counted as a successful anonymous-client check.
- Separate v51-final-save25→v52 ordinary coldContinue/Save26 passes all declared
  persistent domains in both native and NodeWASM. Final RGB, PCM and full Flash
  are byte-identical across cores. Party PAR Sprout/fainted Hush and Box1 Bin
  retained. Evidence service-signs-v52-earned-save-upgrade.json. This supports
  this version transition; ten-cycle seal remains correctly scoped to v51.
- Alignment independently rebuilt final seal in memory: all106 evidence files
  and every scope field agree apart from fresh timestamp. Rechecked pending
  Site source/archive/helper adaptations; differences were patch/manifest only.
  No broader human quality, sign-in/device, fresh-session or campaign approval.
- Next: original Roon native-pixel cleanup/registry/old-save appearance refresh,
  more Stage B visual variety and credible update/input/audio instrumentation.
  Full scope/deadline unchanged; next alignment check no later12:55UTC.


Roon native-art integration in progress:

- Original fictional amber-hood Roon source remains360a740...9cf5; native palette
 9eb83182...089a6, nine16x32 poses. Reviewed recipe changes18 west-stride2
 lower-leg pixels only, yielding1cc6545c...9d4e, with source/head/torso/arms intact.
 Other five original cast sources/native files/palettes were not regenerated.
- Dedicated Sunset palette0x1127 and unused slot81 replace Roon's shared stock
 MAN_3 appearance. Fresh map entry permits one-tile wandering on nine clear
 boardwalk cells; NPC/quest/warp anchors unchanged. Existing Continue hook changes
 appearance while preserving cached movement/positions until map re-entry.
- Source/palette/whole-pose hashes and every old pixel are checked before edits;
 stale, duplicate, no-op, out-of-bounds, missing-oracle or collapsed poses fail.
 Five cleanup and six native cast checks pass; fullcheck.sh passes. Generic cast
 manifest collection now includes this third group's conversion/recipe receipt.
- v53source awaits native build, actual movement/dialogue, old-save appearance
 and palette/reflection checks. Public staysv52/Site43. No new human approval.

- Independent Roon review confirms exact18 edits, unique slot81/tag0x1127 and
 unchanged older cast files. Added a registry guard against multiple independent
 special NPC palettes on one map (a real shared native/reflection-slot limit);
 seven cast and five cleanup units pass. All manifest cast groups are included.

Verified v53 Roon candidate (public publication pending):

- Normal source build0e40db9 reproduces immutable draft target
  04196df813241d27b5d14f145c30d130712656cc65fd0461aba544521d7a9bbf.
  Exact BPS reapplication passes:885003bytes, patch SHA256
  31354d47c90b39c4fd15e5034fd16dfe12a42f44d3ebe069fb988a24316a9015.
- Independent compiled-resource audit verifies all nine native frames, palette,
  animation pointers and the sole graphics-slot replacement81. All238 other
  graphics bindings,39 old palette bindings, five earlier original cast sources,
  courier field/run and battle resources retain their prior content.
- Actual older Sunset battery coldContinue refreshes only Roon's cached graphics
  field, preserving cached coordinates/movement/ranges. Normal dialogue works.
  Ordinary native/WASM Save advances3→4 with identical Flash and unchanged
  declared persistent domains; coldContinue restores the saved appearance.
  Existing cached LOOK_AROUND stays until actual map re-entry. Palette/reflection
  checks preserve the courier and clinic; dynamic live facing/flags may change.
- Earned first-badge controls exit the clinic, reach Jonathan's Muni and return
  to Sunset. Actual fresh map entry activates Roon's one-tile native wandering.
  Independent audit matches exactly one source-derived opaque sprite pose in
  every one of2400 frames, observing all twelve direction/phase combinations.
  All full-frame RGB and PCM match native/NodeWASM. North idle feet remain one
  pixel higher; no human art approval or browser performance claim is inferred.
- All16 independently specified mechanics catalogs rerun on v53:711/711 pass,
  including57 doubles. Complete actions/move-end/whole-turn integration and all
  other full mechanics gates remain open.
- Private matched40.183s review:roon-v53-paired-cast-review/comparison.mp4,
  SHA56435d8ee51665124bc3927d43d5b9d6459178d79962d905489ff0e13db538e3.
  Genuine Emerald BOY_2 and original Roon use the same2400-frame controller input,
  native clock and equal nearest3x scale, with two audio tracks. Authored wander
  paths/radii differ. Requested rating covers NPC art/readability/walking only;
  world, audio and full quality-domain approval remain separate and pending.
- Alignment reviews clip provenance read-only by14:00UTC, hardstop14:10UTC;
  next check no later14:08UTC. Deadline remains October15 18:00 Pacific.
  Public remainsv52/Site43 until audited Site publication succeeds. Full human
  domains remain0/11. Next visual priority is denser, varied South Park frontage.

Site44 v53 published and checked:

- Site source29ac591eec86fefe84e3ad157c692cf71083a5f7 passes TypeScript/build.
  Archive098c0bde967b5390b384e33bb1e3c85578086a42c9ed9847a1878fe9d568e4ed
  contains84files, exact patch/manifest and the original SFMM prototype only;
  zero commercial cartridges/private saves/AppleDouble. Prior dist preserved.
- Saved versionappgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_cadb41638bc48191bcf993b2d07afe51;
  deploymentappgdep_6acf86b8b48081919287e7c5f47368f2 succeeded
  2026-10-14T13:42:28.096330Z. Existing public audience/auth/DBbindings unchanged.
- Actual public IAB loader/patch download and anonymous normal-browser-agent
  HTTP200 checks retrieve the exact885003-byte patch31354d47...6a9015 and release
  manifest. No public ROM import/Continue performed or guest progress modified;
  temporary QA tab closed. No GitHub workflow or DB operation performed.
- Alignment independently decodes2400frames from both source clips and paired
  clip, verifies labels/scale/clock/parent states/controller hashes and copied
  audio tracks. Lossless raw frames remain the pixel oracle; encoded reviews
  have expected H264 loss and AAC resampling. Reference gzip metadata was added
  after packaging without changing decompressed bytes. No reviewed technical
  blocker; human NPC rating, full domains and actual-browser gameplay remain
  separate gates. Goal stays active; next alignment check no later14:08UTC.

South Park graphics budget, source iteration:

- Native horizontal/vertical BG flips reduce existing resources498→459 tiles,
  freeing39 slots with no art reduction. All136 released metatiles independently
  decode to their prior indexed pixels/palette banks; attributes and palettes
  retain pinned pre-change hashes. The normal native door reserve1016..1023 is
  enforced by the packer, using actual stored tile count rather than alias count.
- Four focused checks cover all four orientations/all secondary palette banks,
  deterministic symmetric ties, exact503/504 acceptance and505 rejection, and
  released pixel preservation. Eight existing park checks pass with flip-aware
  native decoding. Independent alignment source review pending, ends14:15UTC.
- No new cartridge or visual improvement is claimed yet. This creates space
  for a varied facade filling the three-tile butter-house/clinic frontage gap.
  Existing collision, event, service-door and map placements are unchanged.
  Public staysv53/Site44; next alignment check no later14:15UTC.

Compact lavender frontage source candidate:

- Added original lavender facade26..28,y2..5 between butter and clinic, appending
  IDs136..147 after both service signs. Bank12 occupies previously zero palette
  space; all earlier136 metatile pixels/attributes and old palette banks retain
  their pre-change oracle.502/504 static tiles leave native door slots intact.
- All twelve new footprint cells block walking, including the visible bottom
  row. Both sidewalk rows6/7 stay clear. Restoring those twelve tokens toPPP
  reproduces the entire releasedv53 plan hash40fdb3fd...deb79, including every
  other collision/elevation, NPC, warp, script and interaction anchor.
- Full local checks initially caught the shared packer changing clinic storage
  counts. Restricted flip reuse to an explicit park-only option; independent
  resource hashes confirm office/clinic graphics, records, attributes and
  palettes are byte-identical to releasedv53. Revised fullcheck.sh passes.
  Six focused flip/frontage tests and eight park tests pass.
- Native build/visual, door paths, collision and actual older-save resumes are
  pending. Existing generic resume resolver remains unchanged; safe relocation
  must be observed, not inferred from tests. Alignment prepares twelve ordinary
  v53 saved batteries at future footprint cells with frozen controller harness,
  ending14:40UTC. Main owns newv54 coldContinue/save/WASM checks. No publication
  or human quality approval claimed; public staysv53/Site44. Check by14:20UTC.

Verified v54 compact-frontage release (publication pending):

- Normal source6dad1e6 reproduces draft target
  cdd792f000185d7ef46cd7ceab8b37be6a703570e37873edbd8274b0d344c05b;
  exact BPS roundtrip passes. Patch885387bytes SHA256
  2258b3bd58a025de5f8b8af0090cd8694e264f725a6abcd8f60256a5f9dd5c38.
- Independent actual compiled LZ/ELF audit matches all502 tiles/148 metatiles,
  attributes/palettes/header bindings to source. Prior136 pixel/bank oracle and
  old attributes remain exact. Only twelve actual map words change, all blocked;
  borders, service warps and event/script bindings remain unchanged. Actual
  compiled clinic/office resources preserve their existing zero-tile padding.
  Receipt park-v54-compiled-resource-audit/receipt.json SHA5c6aa320...a40ea93.
- Normal Up pushes at all three front columns26/27/28 remain on row6. All1024
  frontage-walk RGBframes/PCM match native and NodeWASM. Clinic/gym entry404/708
  and exit316/316 frames also match entirely, returning32,6 and13,6. Six focused
  tests, eight park checks and fullcheck.sh pass; all711 mechanics/57 doubles
  rerun successfully. No actual-browser performance or full mechanics claim.
- Alignment prepared twelve actual v53 batteries with ordinary Save at every
  future occupied cell. Actual v54 coldContinue relocates upper rows2/3 to safe
  row1, lower rows4/5 to sidewalk6, keeping each column. Ordinary Save26→27 and
  subsequent coldContinue retain that location. Native/WASM full resulting Flash
  and finalRGB match for all twelve; other declared persistent domains remain
  unchanged. Only current-position/same-map warp ID/coordinate header bytes are
  permitted to change; map IDs and other warps remain strict. Recovery receipt
  compact-frontage-v54-legacy-recovery.json SHAaf84da804270578a805d6acdcd7c7fa0905efc7aee21ca85247a11795a2f01d2.
- The initial split-native recording versus continuous-WASM PCM comparison
  failed after the savestate boundary and remains preserved, not counted as
  parity. Added identical-parent-state/input1260frame Save-leg comparisons:
  all twelve PCMstreams match. Continuous walking/door comparisons above have
  no such boundary difference. Frozen native/shared harnesses remain unchanged.
- Separate earned v51 clinic checkpoint25→26 on v54 preserves party/PC/resources
  and all declared domains, with equal native/WASM Flash/finalRGB/PCM. This and
  twelve layout recovery positions do not complete fifty campaign checkpoints,
  public authentication/device/persistence or full save acceptance gates.
- Alignment independently audits final recovery identities/bounds/events; no
  human quality approval inferred. Public remainsv53/Site44 until publication.
  Full domain approvals0/11, full goal active, deadline October15 18:00 Pacific.

Site45 v54 published; independent recovery audit sealed:

- Site source442364d1a2ceadbfba0d4fb5eb8661f96e056dd8 passes TypeScript/build;
  audited84-file archive SHA7461aa9637d7219e234258d135c104243809f7020241efef518f298910f43c38
  retains exact patch/manifest, original SFMM prototype, zero commercial full
  cartridges/private saves/AppleDouble. Prior Site44 dist preserved.
- Saved versionappgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_21d04e472e5c8191a39cf0d21b52a5ca;
  deploymentappgdep_6acf8b26a1a08191ad408a41536b3866 succeeded
  2026-10-14T14:01:21.905371Z. Public loader/patch download and anonymous normal
  browser-agent HTTP200 retrieve exactv54bytes. Public ROM/Continue and guest
  progress untouched; QA tab closed. Audience/auth/DBbindings unchanged, no Actions.
- Independent recovery receiptcompact-frontage-v54-legacy-independent-audit/receipt.json
  SHAa2bf9efc69e6d2c583dd8ac38b125804abdeb77ae9d2fbc8662b23bbf8f38afa
  binds423 evidence files and all native/web/private helpers, ROM/ELF/plan and
  inputs/states/batteries/audio. Actual positions match existing resolver's
  Manhattan tie order, strict bounds and NPC/warp avoidance for all twelve cells.
  Location changes are exactly bytes2/6/8/9/10/11; all other declared domains,
  prior active Flash slots and special sectors preserve expected semantics.
  Cold reloads are stable. Continuous final Flash/RGB and same-boundary Save-leg
  PCM scopes remain explicit; failed cross-boundary PCM comparison excluded.
- Original Roon/NPC comparison remains pending user rating. Full human domains
  stay0/11; first-slice polish, real-browser/device performance and full campaign
  remain unfinished. Goal active; next alignment check no later14:20UTC.

Next Stage B cast improvement, Karpathy source candidate:

- Alignment generated original fictional navy-crewneck/short-dark-hair field
  atlas a60e087653530020fd75052419432d805497d92bac2f9be9b3e8df176f97d940,
  with recorded prompts/limitations. Exactly nine S/N/W poses; two generation
  attempts, rejected first preserved. Source is unapproved and not integrated.
- Added optional explicitly authored16-color RGB5 palette policy and per-person
  pinned quantization palette support. Existing cleanup still validates against
  its exact source palette; every used native index must retain the same final
  color. An occupied index recolor fails rather than silently changing old art.
  Policy and quantization-palette presence/content are bound to conversion hashes.
- All existing six cast assets/conversion receipts regenerate byte-identically
  through this optional pipeline. Four palette tests, seven cast tests and five
  cleanup checks pass. Current Roon uses indices0..14 only; unused duplicate
  opaque slot15 can supply a light skin/sneaker color without changing Roon.
- Main owns palette/registry/native conversion; alignment source-only work is
  complete. Karpathy still stock scientist in publicv54/Site45. Next checks are
  native pose readability, reserved-slot ownership, palette preservation, normal
  interaction and older-save refresh. No new approval inferred; full goal active.

Karpathy native-art source integration:

- Registered original nine16x32 Karpathy poses in Sunset's existing palette group.
  Shared palette changes only unused index15 toRGB5(31,27,23); Roon's exact packed
  walking hash remains e5dc40733671ee6bb4f7198253e6cf812f8eeb5fdd8d4e16a8585497592d91fc.
  Roon's old source palette and18-pixel recipe remain pinned; only unused PNG
  palette metadata changes. Other five cast assets/palettes remain untouched.
- All six unused doll slots are occupied, so this reviewed replacement retains
  Karpathy's existing scientist slot46.239-entry graphics table and dynamic ID
  ranges stay unchanged. The allowlist permits onlySF_Karpathy/sunset.json;
  registry rejects another authored NPC using the old scientist appearance.
  Quest/mentor/party-healing scripts, positions and movement stay unchanged.
- Ten cast checks, four palette checks, five cleanup checks and fullcheck.sh
  pass. Independent source/palette/pose audit pending; native build, ordinary
  mentor dialogue/healing, older-save/cache and compiled preservation are next.
  Public staysv54/Site45. No art/walking/domain approval inferred from conversion.
- Public persona reference checked2026-10-14:https://karpathy.ai/ identifies
  Karpathy as an AI researcher and educator. Game outfit/mentor role are fiction;
  source photos/site images were not copied. Atlas source/prompts remain original.
  Goal active; next alignment check no later14:30UTC.

Karpathy native-pixel refinement before release:

- Initial privatev55 target99b3367c...17c54da exposed orange skin highlights and
  repeated north-arm/west-foot phases. That draft is preserved and unpublished.
- Original source PNG staysa60e087...f97d940. Reviewed recipe lightens231 skin,
  hand and sneaker accents, lifts the west first-stride trailing shoe one row
  inside x8..11/y27..29, and reflects north second-stride outer arm strips only
  inside x2..4/11..13,y20..24.252 net changes bind all nine input/output poses;
  recipeSHA5c2cf30cf91f46bc51f9df1155894ba3eada4aaf344a1c25992d09004cf5e643.
- Independent source/pixel audit verifies exactly those three operations, zero
  other differences. North second-stride SHA9240829f...51fab04 agrees with the
  independent proposal. West baseline contacts alternate left4/5 versus right
  8..11; north hand phases alternate. Packed art02f0c4b074da27d427fd1e5b43e0769ddc95409ac94983b1997b309ef4006065
  decodes exactly to all nine PNG poses; no opaque pixels below baseline30.
  Roon remains exact4bppe5dc407...2d91fc and identical visibleRGBA, source/recipe
  and all used palette colors. Shared palette remainsf4fc7a76...b4c0aad5.
- Eleven cast, four palette and five cleanup checks pass; revised fullcheck.sh
  passes. Normal build/runtime/older-save/mentor interaction checks still needed.
  Full human domains0/11; public staysv54/Site45. No quality approval inferred.

October14 continuation and v55 runtime verification:

- Both chats were interrupted around14:21UTC; resumed16:09UTC from authoritative
  clean source state d337496. No continuous work/check-ins are claimed during
  that interruption. Alignment restarted a finite read-only audit ending16:45UTC;
  next check no later16:35UTC. Deadline remains October15 18:00 Pacific.
- Revised private/normal v55 target
  446434d6fb8f957e1b34279f3268a1bc16203e51626e3a500dfc55b5fcdf9818
  reproduces exactly from source d337496.886933-byte patch SHA256
  54a2384bae75fe95d00e07051d05805dfec983276787bb3a2937723ad0838c75;
  exact BPS roundtrip passes. Earlier99b336...draft stays private and excluded.
- Actual supported v53 Sunset Save4 coldContinue succeeds native/NodeWASM.
  Normal28-tile walk reaches mentor23,18 from player7,11 to23,19. New original
  sprite appears through existing slot46; mentor's standard dialogue/fanfare
  restores CindercoyHP13→19 and ScratchPP32→35. Second party member stays exact;
  identities/moves/levels/held items remain intact. Actual576 approach frames
  and428 talk frames have identical full RGB/PCM in both runtimes.
- Ordinary Save4→5 after closing dialogue persists the healed party and23,19.
  Subsequent native coldContinue preserves location/party/Flash. Matched1260-frame
  native/WASM Save legs produce identical full Flash/finalRGB/PCM. Expected
  gameplay changes are explicit: position bytes0/2, HP/PP healing, steps91→119
  and friendship-step variable0x402A91→119. All other declared domains preserve
  expected semantics. This is one actual checkpoint, not full save acceptance.
  Evidence karpathy-v55-mentor-{healing,save-reload}.json.
- All711 reference scenarios/57 doubles rerun on revised v55 and pass. Existing
  cast/palette/cleanup/full checks pass. Independent compiled/cache/palette audit
  underway; public remainsv54/Site45 until audited publication succeeds.
- Runtime exposed a separate story defect: mentor always repeats the beach
  recovery hint after the sensor has already been returned. Next bounded story
  change will follow actual parcel/relay/badge state and preserve rewards/healing.
  Full human domains0/11 and full campaign/performance/auth gates remain open.

Independent v55 compiled/cache review before publication:

- Actual final-ROM/ELF comparison changes only pointer slot46 among239; dynamic
  graphics base240 stays fixed. Karpathy's nine packed frames,16x32 info,
  standard animations/shared tag1127/slot10/reflection match original assets.
  Sixteen prior cast/courier resources and eight normalized prior graphics infos
  remain unchanged. Roon's packed frames and used palette entries0..14 are exact;
  shared palette changes only unused index15. Actual Sunset final-ROM map/events/
  scripts/warps remain unchanged after relocation. Post-link map overlay is
  accounted for, rather than treating the unpatched ELF map as final scenery.
- Receipt karpathy-v55-compiled-cache-audit/compiled.json
  SHA625c96118e2df374f5340f209e8ef3c356a64116d9a68b5bb958d945d23e2d3a.
  All64 older saved templates preserve non-script fields; mentor ID46 already
  matches the new binding. Actual shared palette buffers/PRAM are correct.
- Independent cold native/WASM RAM comparison differs at two RTC-minute bytes
  (sRtc/gLocalTime) across a host minute boundary; no complete cold RAM equality
  is claimed. FinalRGB/PCM agree. Approach/talk seeded from the same native
  parent state match all RAM as well as full RGB/PCM. No human, performance or
  full release approval inferred. Public publication pending; full goal active.

Site46 v55 publication verified:

- Site source461973c88670eb84638678d01940e0f31b9e3ecf passes TypeScript/build;
  archivec89f91822cdd45a724b4fecf2ecaf7f82fd50012467d15a079b32d6d765c4bfc
  audits84files with exact patch/manifest, original SFMM prototype and no
  commercial full cartridges/private saves/AppleDouble. Previous dist preserved.
- Saved versionappgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_f363702ea5a08191bb861d76882fe9bf;
  deploymentappgdep_6acfab4704748191b81b0d82ba0d7040 succeeded
  2026-10-14T16:18:24.908590Z. Actual public IAB loader/download and anonymous
  normal-browser-agent HTTP200 retrieve exact886933-byte patch54a2384b...38c75.
  No public ROM/Continue or guest progress changed; QA tab closed. Existing
  audience/auth/DBbindings preserved; no GitHub workflow or DB operation.
- Final independent cache/palette receipt55d2a80cc327f351171bb6a20fb56817fd759c59dcf5d118fa279bf972bf9dca
  binds42 evidence files. Both unfaded/faded palette buffers and hardware PRAM
  match intended shared/courier palettes in all six snapshots. FinalRGB/PCM
  agree for all pairs; cold RTC-minute RAM difference remains explicitly scoped.
- Next story fix: mentor heals as before, then gives the current objective:
  starter/chosen→beach; sensor recovered→Roon; sensor returned→Muni/Scott;
  delivered→blue INPUT; first relay→green OUTPUT; second relay→Scott challenge;
  badge→incident log. Roon's post-return hints also stop repeating delivery
  after Scott has received the sensor. Rewards/party healing/save schema and
  travel gates remain unchanged. Validate branches with actual campaign states.
  Full scope/deadline unchanged; human domains0/11; goal active.

Contextual story hints, v56 source checkpoint:

- Karpathy retains the same HealPlayerParty/fanfare sequence, then selects one
  hint from actual parcel, relay and earned-badge state. Players without a starter
  still receive companion selection. Beach advice stops once the sensor is held;
  delivered sensors point to the blue INPUT/green OUTPUT/challenge sequence,
  and an earned badge points to the available incident log.
- Roon's post-return dialogue distinguishes delivery pending, Scott working on
  the sensor and earned-badge follow-up. Existing recovery reward500coins and
  quest3→4 transition remain unchanged and occur once. No new flags, save schema,
  battles, rewards, travel gates, maps or party-healing rules added.
- Five bounded source safety checks cover the seven mentor objectives, no-starter
  choice, badge priority over an older relay value, Roon's five later phases,
  and reward-once behavior. These parse source control flow; they are explicitly
  not native engine execution proof. Fourteen map checks/fullcheck.sh pass.
- Alignment found genuine v49 Sprout controller states for q2/q3/q4 and relay
  phases0/1/2/3; ordinary older batteries are being prepared with source RAM and
  saved phases verified separately. Main owns v56 native/WASM cold/interaction
  checks; no synthetic campaign state or byte-edited battery will count.
  Public staysv55/Site46 until verification. Next alignment check by16:45UTC;
  prep hardstop17:00UTC. Full human domains0/11; full goal remains active.

v56 story execution and compatibility verified:

- Six genuine v49 ordinary checkpoints cover parcel2/3/4 and relay0/1/2/3;
  original RAM phases were inspected before saving rather than trusting stale
  companion Flash. An existing earned v51 badge checkpoint adds phase4/4.
  Seven actual v56 coldContinues preserve phases/maps/positions and input Flash.
  Provenance receipt story-hints-legacy-checkpoints/receipt.json
  SHAb06b3043ff6dc78e2444f4205069bef6a696a3ae4d5db651781a15a609412683.
- Normal travel reaches Karpathy from all seven checkpoints. Actual expanded
  message bytes equal the correct immutable-ROM hint symbol in each phase.
  All796 RGBframes/PCM per conversation match native/NodeWASM; phases stay
  unchanged. Mentor receipt SHAe3b08c519df37674793d3e0f38cb6a1af402c4842ab33753253d3578d23b7cb8.
- Independent normal Roon conversations verify all seven branches. Sensor
  return changes quest3→4 and money3000→3500; repeats pay zero. Other branches
  preserve actual phases/money. Receipt story-roon-v56-audit/receipt.json
  SHA2c947254f040ac54e93217340f314d9b80fdce9a64ec6707634f8c8373cb6d49.
  Subsequent ordinary Save1→2/coldContinue/repeat retains3500 and4/0, with no
  extra reward; matched native/WASM Save Flash/finalRGB/PCM agree. Evidence
  story-hints-v56-roon-reward-save-reload.json. This is checkpoint proof only.
- A genuine before-starter source finishes its normal opening, then saves
  quest1/relay0/party0 using actual menu Save index2. Valid CRC/SF marker and
  real browser TypeScript validator accept it. v56 coldContinue and normal
  mentor conversation select Choose; all600 party bytes, flags/vars/phase/money
  remain unchanged. No function-call trace collected, so no claim of tracing
  absence of healing. Receipt story-hints-prestarter-v56/receipt.json
  SHA7af72c7e347cde8f6af6e2d7b2a2ac3b72bc657435a10c67778fc594465aa177.
- Controlled native GetStringWidth fixtures measure33 actual encoded lines at
  at most200px. They intentionally use scratch RAM/CPU registers and never
  export campaign saves; separate from normal controller evidence. Font receipt
  SHAab706dbf03831c7f14ba5857add48cfd235f6411337b2c41624a55cff86221e8.
- Five source checks/fullcheck.sh and all711 mechanics/57 doubles pass. Normal
  release/publication pending. No human/performance/full-story approval inferred.
  Next: separate read-only guest-loop/input profiler pilot, with exact PC/cycle
  semantics independently reviewed; frozen capture helpers remain unchanged.
  Alignment audit hardstop17:35UTC, next check by17:15UTC. Publicv55/Site46.

Site47 v56 publication verified, 2026-10-14:

- Public now serves0.0.56-story-hints-preview, target91a1349d1e3069d243cfea7bc30f18f2bf7943d26ed3460c95ae099b00ae70da.
  Exact885983-byte BPS SHA1ddd994b8b777583c718442e1912cb1282744c710422d51f9e88c1962f2a63b4;
  normal release roundtrip and all711 mechanics/57 doubles pass.
- Site source75eb546e73d2278646d9299703ab741fbd549842 passes TypeScript/build;
  archive0312c96eea352bb93fadcb4b257e715dbd132f7f79e07549414c3710d49f2bf5
  audits84files: exact patch/manifest, original SFMM prototype, no commercial
  full ROM/private saves/AppleDouble. Prior dist preserved without deletion.
- Saved versionappgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_94905632ab6c819188dc789c15994ec3;
  deploymentappgdep_6acfb44631d48191a8b43db6d2395237 succeeded
  2026-10-14T16:56:47.533410Z. Anonymous no-cookie HTTP200 manifest/patch and
  actual IAB download match exact released bytes. Public loader paint verified
  with browser visible; earlier background-compositor blank screenshots retained
  as failed paint observations. Valid image: public-v56-loader-visible.png.
  Temporary QA tab closed and previous browser visibility restored. No public
  ROM import/Continue, guest progress, audience/auth/DB changes or workflow run.
- Alignment independently validated native ReadKeys/dispatch/wait sites, ARM
  Main key offsets and pinned clock behavior. Stock library disables debug global
  cycle accumulation: use explicitly unwrapped mTimingCurrentTime, never infer
  whole-run time from mTimingGlobalTime. Next separate pilot measures actual
  KEYINPUT hook entry and frame-end held-key acknowledgement, with stock-control
  equivalence first. These cannot establish callback completions, render deadlines,
  browser/mobile performance or input-to-photon. Frozen capture helpers unchanged.
  Next alignment check by17:40UTC. Full human domains0/11; full goal active.

Bounded native input pilot, 2026-10-14:

- New separate native_input_profile.c uses stock runFrame plus the existing
  keysRead callback, filtered to actual ReadKeys LDRH. No guest RAM/register
  writes or reads of the KEYINPUT device by the observer. Unsigned clock-wrap,
  signed-boundary and discontinuity checks pass; reset/load precedes its epoch.
  Validated pinned agbcc offsets are4/28/2a/2c/2e hex for pointer size/key fields.
- Calibration input-v56-calibrated-pilot-v2/receipt.json
  SHA f2a4333cbfd642509d49660a256928c399a18651af78254165a8f26dfd5cde81:
  all120 actual video frames,131668 stereo PCM samples, final397312-byte state
  and131072-byte Flash are exact across control, observer and unchanged frozen
  capture harness. All120 stock calls advance exactly one video frame.
  Eight distinct stable press/release masks get real hook entries and changed
  heldRaw acknowledgements at the first frame-end sample. Hook-entry latency
  22151–53415 guest cycles; acknowledgement upper bounds280887–280899 cycles.
- Scope is one120-frame field route, input submitted at stock frame boundaries.
  Hook entry precedes final instruction cost; frame-end acknowledgement is only
  an upper bound. No callback/render deadline, browser/mobile/input-to-photon,
  ten-minute run or robust overhead claim. Single-pair wall timings are noisy
  and include audio callback writes. Full performance gate remains open.
- Alignment independently rehashed all four exact outputs and reviewed observer
  effects. Hardened truncated CSV rejection and actual frame increment checks;
  outer wrapper timeout bounds bootstrap/IO too. Frozen capture helpers unchanged.
  Next: commit reusable calibration/provenance wrapper and failure guards, then
  separately validate instruction-level callback observation against stock core.
  Next alignment check by17:45UTC; full human domains0/11; goal active.

Reusable input calibration command verified:

- profile_native_input.py pins ROM/ELF/state/Flash/controller provenance, library
  and generated flags, verifies actual ReadKeys ROM/ELF bytes and compiles Main
  offsets with pinned agbcc. Each process has an outer60second timeout. Existing
  output names are refused; all inputs and frozen helpers must remain unchanged.
- Final wrapper receipt input-v56-calibrated-pilot-v3/receipt.json
  SHA36ac9d28c52be84052cc26121c98a8681d6ccf9e8b6bd6ce6f6c3b325c1af89e
  repeats exact three-way calibration and eight input observations. Five failure
  guards reject stale matches, missing events, impossible chronology and corruption
  in any output. A real truncated CSV fails native execution with exit2; partial
  artifacts retained and never accepted. Full local scripts/check.sh passes.
  No new game ROM, deployment or workflow run needed for this tooling change.

Instruction boundary calibration:

- Optional separate step path drains the pinned core's actual pending event
  function before PC observation, then uses core->step. At frameCounter change
  it yields immediately after processEvents, matching stock runFrame rather than
  executing an extra instruction. No guest RAM/register edits or breakpoints.
- input-v56-step-calibrated-v1/receipt.json
  SHAefff414e120b0cb39427559e6eb8475bd7334f7625988609727ad190111f3542
  verifies exact RGBA/PCM/state/Flash across five variants: stock control/observer,
  step control/observer and frozen capture. All120 KEYINPUT hook cycles match
  stock exactly;11630195 instructions and115689 event drains observed.
- Records1440 actual transitions across12 selected event kinds, including actual
  callback dispatch/pending return and wait/clear/return. No display-deadline or
  host responsiveness claim. Initial/final partial spans still need interpretation;
  independent alignment review in progress, ends17:50UTC. Five safety guards pass.

Native work/wait interpretation pilot:

- Added schema1 VBlank-delivery observations using actual vcount160 and the
  already-scheduled video event. Nominal time subtracts measured delivery lateness;
  all120 consecutive nominal periods equal280896 guest cycles. No paint inferred.
- Final five-way calibration input-v56-step-vblank-pilot-v3/receipt.json
  SHA68f7cd69a73b048bb65d03524526a8c5cb9b31593aefd8dc2f3ebfd02a8215f1
  retains exact outputs and input-hook timing. Source/build inputs are fingerprinted
  before compilation and checked unchanged afterward; mode metadata hashes bound.
- Interpreter loop-summary.json SHAcb4d40565232dbb188e6b928319e5cc43ebaac7e679b5aad9cb7c40c11e5ca82:
  120paired callback1/2 spans,119 complete start-to-start periods and119 waits.
  One initial wait/loop return and one trailing open wait/loop are excluded.
  Callback2 max104937cycles; observed work-through-wait-clear max136467cycles.
  All120 work-clear points precede the first nominal VBlank after loop start;
  minimum margin113561cycles. This is a short native work metric, not a display
  deadline/99percent host or full performance acceptance. All larger gates open.
- Six interpreter guards and full local scripts/check.sh pass. Independent nominal
  clock/pairing review ends18:00UTC; next alignment check by17:57UTC. Full goal active.

Browser audio measurement foundation:

- Extracted the maintained MPL audio sink into mgba.audio-worklet.js. Optional
  diagnostic messages enable cumulative startup-silence, post-start starvation,
  dropped source frames, rendered output frames/quanta and queue-depth counts.
  Enabling/stopping observation never flushes or alters the audio ring/cursor.
  Default playback sends only its existing numeric consumption messages.
- Actual worklet VM checks verify analytical half-rate interpolation, identical
  observed/control output through depletion,128 startup frames classified separately,
  ten post-start starved frames, four excess dropped source frames and disabled
  reporting. These are controlled sink tests, not live-browser audio acceptance.
- Preparation previously regenerated the SDK from upstream, risking loss of SF
  fixes. It now preserves maintained SDK/audio/performance modules while verifying
  pinned core artifacts. An isolated two-run regression check and actual workspace
  prepare preserve frontend hashes. Full local checks pass; public remainsSite47.
- Native alignment review confirms current formula/pairing; arbitrary snapshots
  with an unobserved initial wait-clear, pre-epoch nominal VBlank or lateness over
  1008cycles fail closed and are not universally supported. Next: foreground web
  pacing/input/audio instrumentation. Alignment owns bounded probe aggregation
  and its tests only, hardstop18:15UTC; main owns SDK and actual browser checks.

- Alignment completed the bounded web performance aggregation module. Explicit
  start creates one timeout, maximum10minutes; no automatic/recurring job. It
  separates requested/executed/video frames, discarded debt, hidden ticks, input
  pipeline stages and cumulative audio counters; first unknown rAF gap is excluded.
  Main reviewed the interface and independently ran all13 supplied guards: pass.
  SDK integration and actual browser observations are still pending; no live
  browser performance claim. Module is committed as a separate coherent checkpoint.

Actual foreground browser pipeline smoke checks:

- SDK diagnostics are opt-in and preserve existing five-frame pacing/input rules.
  Count pre-cap demand/discarded debt, actual video counter increments, batch work,
  canvas submission and changed-input pipeline timings. First rAF gap is excluded;
  hidden starts rejected. Pause/reset/import/load/destroy end measurement scope.
- Worklet epoch IDs bind final asynchronous audio ACKs. Final packets require
  exact type/epoch/boolean marker, nonregressing finite counters, positive sample
  rate and a contiguous output interval. Missing/invalid ACKs remain explicit.
  Probe stops at10minutes maximum plus bounded500ms final-ACK wait.
- Two real visible IAB Chrome155 ten-second field checks each record1200rAF ticks,
  597actual video frames, no discarded debt/video mismatch and8scripted DOM-input
  changes. Original run max dispatch-to-submit11.8ms; hardened run12.5ms. These
  end at completed frame-batch/canvas submission, not physical key/paint/guest ACK.
- Hardened report web-performance-v2/report-2476350893ed41e5a6e6a0c53cb3f81b.json
  SHA32980b05aa29e2130bcb2dbbbff7f2b059292c8fac42d1f1dcca745810ef3758.
  Final audio240128outputframes at24000Hz,1876quanta;0warmup/starvation/drop.
  Audio epoch10.005333s is asynchronous to main10.0011s, not exact thread alignment.
  Earlier run retained480000frames/48000Hz. Actual sample rate is recorded per run.
- Original runtime snapshots/identity hashes retained for both runs. Offline auditor
  verifies them and report accounting, preserving its own exact source. All15 probe
  guards/worklet tests/full local checks pass. Hardened smoke overlapped local QA;
  no quiet-host or instrumentation-overhead conclusion. Public staysSite47.
- Measured120Hz rAF requires more than40000samples for10minutes; tick capacity now
  bounded160000, input40000. A fresh600000ms field-only run started~17:52UTC with
  visible browser, fixed30minute local server and no public save/account changes.
  Mixed battle/menu/story, disabled/enabled overhead, physical phone/Safari,
  guest-update/display deadlines and human approvals remain open. Full goal active.

Ten-minute field finding and reusable local harness:

- Actual desktop host: MacBookProMac16,5, AppleM4Max/36GB, macOS26.6.2; IAB
  Chrome155 agent.600.0013s main epoch,71999visible ticks/35837actual videoframes,
  0discarded debt/mismatch,16scripted DOM-input records, maxdispatch→submit16.9ms.
  Report web-performance-v2/report-bd939735a46341eda8127327b75fc48a.json
  SHA14ab94c369c307f6e58c4833583a31a363919b9f181f16ac8a18c6f0ffbf1c99.
- Audio FAIL:469829sourceframes dropped,0sink starvation,14228736outputframes at
  24000Hz=592.864audio seconds. No hidden/pause/reset events. Well-formed receipt
  is not a passing performance result; no proven hardware-drift or silence cause.
  Existing wall pacing has no queue feedback. Do not revive posted-minus-consumed
  accounting after drops: posted samples include rejected worklet data.
- Reusable finite localhost server/page preserve runtime, HTML, state metadata,
  identity and server source. Actual generic browser load/report smoke succeeds;
  wrongHost/path/Origin rejected and a one-second session exits normally. No full
  ROM is packaged; server binds127.0.0.1 only, expires at most3600seconds and
  refuses existing evidence names. Main added an explicit two-minute comparison
  option and visible audio-drop counts. Source reviewed; no public deployment.

- Guarded offline auditing now checks input percentile cardinality/order and scope
  booleans too. Four owning tests reject mismatched runtime, invalid audio tails,
  inconsistent frame totals and malformed timings while retaining actual drops
  as findings. Reusable review instructions are in docs/quality/browser-performance.md.
- Regular Chrome two-minute comparison records7167video frames/14399visible ticks,
  no debt/drop/starvation and120.012336audio seconds at44100Hz. Report SHA
  28b7e06bdfea274eab8f0c774ba7644058566e440530d732f8c21dcdca1084ae.
  Different duration/rate prevents declaring an IAB-specific cause. A fresh600s
  Chrome baseline started~18:17UTC, using an immutable old-runtime snapshot;
  newer working-tree reset fixes do not affect that ongoing capture.

Playback reset and measurement-boundary fixes:

- Regular Chrome600s baseline also fails strict audio continuity:35837actual
  video frames,0debt/drop,873starved outputframes at44100Hz (~19.8ms), final
  rendered interval600.044263s. Report SHA8eb58a3981360b56a81d611dc573fc451adb48049f90f001976efe6ecbd4d531.
  Last periodic count142 precedes final873 by133.5ms of output, including44ms
  beyond the main epoch. Do not attribute all tail starvation to aggregation.
- New onClose stops worklet observation before aggregate processing. Exact-number
  count histograms preserve rank percentiles while sorting unique values; no
  rounding, sample dropping or worst-case overhead guarantee. Separate callback
  error/idempotence/rank checks pass; reportPreparationMs is now measured.
- Successful reset/reboot/import/load discard bounded stale shim PCM, clear the
  sink via a separate acknowledged playback epoch, resend source rate and rebase
  presentation clocks/ledgers. Diagnostics start never flushes playback. Missing
  playback ACK is recorded after500ms; wall-video behavior stays unblocked.
- Seven real-helper/worklet marker checks and independent review pass. Actual
  Node/WASM drains5620queued sourceframes without advancing frame3974; all397312
  serialized bytes and131072Flash bytes match after canonical output initialization.
  Proof audio-reset-v56-core-state-proof-zeroed/receipt.json
  SHA fefd55eef52affba92d02934d877df8583d568a69c0c878cc17dda84ee83b60f.
  Initial uninitialized-output comparison failed981bytes in unwritten/conditional
  fields/IO holes0x138..7ff; preserved as failed. No captured bytes were masked.
- SDK snapshot exports now initialize only allocated output scratch after checking
  allocation success, with guaranteed cleanup. Four memory-safety/determinism
  guards and real-helper WASM repeat pass. Frozen capture helpers remain unchanged.
- Actual Chrome UI checks repeated exports and restored RAM/Flash exactly. Fresh
  ten-second candidate:597video/1200visible ticks,0debt/starvation/drop, playback
  resetepoch3 ACK=true/no timeout, report preparation0.5ms. Report SHA
  0c2251d75357682f1b20a1b1983f0a5f6085f7f9497e4e6862ebc30b2bc09363.
  Full local checks pass. This proves local reset/export behavior, not a new Save
  checkpoint or full audio gate. Public staysSite47; longer/mixed traces remain open.

- Independent source review found synchronous custom onClose callback reentry could
  start another SDK diagnostic before the final-ACK wait was installed. A closing
  lock now covers that interval and clears before user onReport delivery. SDK syntax
  and19 probe guards pass; these guards do not execute every SDK asynchronous edge.
- Actual production canonical-state helper proof retains all397312state bytes and
  131072Flash bytes unchanged while discarding5620stale shim audioframes. Receipt
  audio-reset-v56-canonical-helper-proof/receipt.json
  SHA d49aa3adaf52f753f34b93dd5d2063f296b7287a5eb23ba4fd66bb1a6419283c.
- New private QA pages also destroy the emulator at their declared session limit;
  no recurring monitor starts. Unused duplicate local server stopped explicitly.
  New ten-minute candidate uses frozen runtime and the genuine mentor-approach
  checkpoint; results pending. Full objective, approvals and public version unchanged.


Next native visual candidate — quieter Sunset lawn:

- Authored three editable16x16palette-index lawn cells instead of resampling more
  bitmap detail. Shared sage ground/edges removes the alternating lighter cell;
  six deliberate blade pixels per tile replace scattered blue/dark speckles.
- Only native cells0,12,13 change:315of768pixels differ across those cells. Other
  thirteen terrain cells, RGB555 palette and all shoreline/water animation bytes
  match the preserved preceding assets exactly. Map/traversal/event coordinates
  and encounter behavior are unchanged. Source identity is checked on consumption.
- Five terrain tests pass, including source→native fidelity and rejection of
  unrelated cell ownership, ocean-color indices and edge seams. Native ROM build,
  actual field comparison and user quality approval are pending. Public staysv56.


- Added opt-in start/close AudioContext clock anchors, bracketed by main-thread
  monotonic reads. Offline audit keeps their interval separate from sink-frame
  observations; clock deficits are reported without choosing a cause or changing
  playback speed/pitch. Six audit tests pass, including legacy missing anchors,
  nonfinite/reversed/partial anchors and a synthetic clock-deficit diagnostic.
  The ongoing Chrome600s run retains its earlier frozen SDK without these anchors;
  new source applies only to future sessions. No new performance gate is passed.


- Completed candidate Chrome600s field run:35836video frames/72001visible ticks,
  0discarded debt/mismatch/drop,8DOM input changes maxdispatch→submit16ms,
  report preparation0.9ms. Audio stillFAILs zero-underrun criterion:73starved
  outputframes at44100Hz (~1.655ms), with599.997823audio seconds. Receipt SHA
  f6843351c9f95785dd97f075fb08481bcc1c7aed68ca68bb7427fb30560b1bcd.
  Exact runtime/identity/auditor preserved. Do not infer causation or approval
  from a smaller failure count than the earlier run. Test emulator/server stopped.
- Alignment released to bounded mixed-route native capture at19:03UTC, using
  immutablev56/pinned prebuilt capture binary. Root owns v57 build. No wall-time
  performance claims from native captures overlapping local builds. Next check19:25UTC.
- Full source checks exposed shared lawn use in South Park: decoded grass cells
  20/32/33 intentionally change too; unique packed tiles502→497. All other prior
  136-cell pixels retain their pinned historical hash after substituting only
  these three independently checked authored cells with preserved original-art
  fixtures. Palettes/attributes and reserved-door capacity checks remain strict.
  The original failed check log is retained; revised six pack/decode tests pass.


One-time playback cushion candidate:

- Sink now waits for40ms of source-rate PCM at boot/actualplayback-reset only.
  Threshold fits below the ring capacity; no extra guestframes, rate/pitch or wall
  video pacing changes. Deliberate audio delay includes chunk/quantum alignment.
  Durable started flag survives diagnostic epochs and live rate changes; later
  starvation always remains an underrun and never triggers another prefill.
- Ten reset/source-rate/marker tests and sink interpolation/observer checks pass.
  Audits expose initial warmup and playbackStarted=false, so no-PCM startup is
  not misrepresented as a continuity pass. Full local checks pass. Actual browser
  candidate validation remains pending; this does not fix the sustained IAB deficit.
- v57draft target22beceecbe5d5edf607a3411fa19af4585a51e92a7ddd1cf1c6bbb1b54df1afd
  builds normally. Existing ordinaryFlash coldContinue succeeds atSunset28,21 with
  party2. Native/WASM final38400RGBpixels,16,467,520PCMbytes and131072Flashbytes
  match exactly. RawRGBA buffers differ only in unused alpha(native0/WASM255);
  whole-buffer failed comparison is preserved separately from proper RGB proof.
- First ordinarySave1→2 persists existing legacyContinue revision0→8/TVwatchflag
  changes; strict stationary audit correctlyfails and is retained. ActualRAM already
  contains those values beforeSave; party/PC remain exact. A second ordinarySave2→3
  passes the unmodified full declared-domain audit with no changed domains. Native
  coldreload of that normalized realSave is in progress. No new full roundtrip claim.


- Normalized v57ordinarySavecounter3 coldContinue passes: all600partybytes match
  the actual saved payload, party2, Sunset28,21, contentrevision8; Flash unchanged
  SHA15aa2ce44b14653f21d9acbf75c6545df9d9aadb56edd6449710c9f2a559df52.
- Alignment completed native mixed-route proof (receipt62af40f722bacfd0bb308c1d126d969577a459097dd0c3ef5704a5bcb277b1e7):
  8888continuousframes coverparty, relaydialogue, warp, ordinarySave3→4, leader,
  battle/action/move menus and oneAbsorbturn. AllRGBframes match selected segments;
  segmentedPCM doesNOTmatch continuousPCM after state-reload boundaries. Continuous
  PCM is authoritative; no browser/speaker or battlewin claim. Failed earlySave
  branches remain preserved and excluded from the verified controller sequence.
- New private finite DOM-replay helper parses actual verified8888frame input into
  148.809174nominal seconds. Headerless masks/durations/rowcount are bounded; only
  one timer is outstanding, keysrelease on every stop, >50ms lateness or hidden tab
  aborts. Actual dispatch logs remain separate from scene/guest-key claims. Five
  replay tests and HTML/Python syntax checks pass. Actual browser replay pending.
- New40ms-cushion Chrome600s field observation started~19:15UTC using frozenv57
  runtime/normalizednativeSave; result pending. Alignment now audits compiledv57
  resource preservation read-only, hardstop19:45UTC; next exchange by19:35UTC.
  Human approvals remain0/11, public staysv56/Site47, full goal active.


- Finite route server preflight freezes the exact62row/8888frame input and helper,
  verifies both hashes, then exits normally after one second. No emulator playback
  occurred in that preflight. Browser replay still pending.
- Replay receipt audit now binds preserved CSV/helper bytes, row/mask/duration
  totals, dispatch order/timing and the current measurement window. A stale replay,
  altered input, hidden lateness or partial completion cannot claim complete input
  coverage. Eight audit tests pass. Stop measurement now also releases replay keys.
  This remains dispatch evidence, not guest key/scene or physical presentation proof.


Actual40ms-cushion field result:

- Report audio-prefill-chrome-600-v1/report-c9b36783a93743ceb6b31a7fd6dc1580.json
  SHAadb241c2e690d5d373bf8f30085c35a1e68adcd7aa13ab57addb3e7101c94695.
 600.0013s wall-read interval,600.003628context/output seconds at44100Hz,
 26460160rendered outputframes,0warmup/starvation/drop; playbackStartedtrue,
  prefilltarget2622sourceframes. Queue observations1609.36..3487.74sourceframes;
  final2227.10. Report preparation1.2ms. No physical speaker-timing claim.
- Actual35836video frames/71999visible rAF ticks,0debt/mismatch,8scripted input
  changes maxsubmit16.4ms. This is a passing field-only sink/pipeline observation,
  not a causal proof against earlier different runs or full quality acceptance.
  Exact runtime/identity/auditor preserved; emulator/tab/server stopped.
- Independent compiledv57audit receipt8c4a7150d8fb9d5b7af3003651ea9bad156bed96cd5e94131c03dc1335845d73:
  Sunset194records/512tiles: only3lawn+75facade underlays change; opaqueforegounds
  andother116records exact. Park148records: only3lawn change,502→497packedtiles.
  Palettes/attributes, layouts/borders/collision/events/bindings and wave240..247
  exact; reserved door1016..1023 untouched. Clinic/office resources exact.
- Broad script-data raw comparison fails4009bytes; retained as failed. Every
  changed byte is accounted by2233actual named-pointer operands with the same
  bindings and−184address shift. This is explicit symbolic-relocation accounting,
  not whole-section byte identity or an address mask. No unexplained difference.


Actual mixed-browser and finite-lease checks:

- Nativev57replays the8888frame route from an ordinaryFlash coldContinue seed:
  gym13,13/party3 → Savecounter4 → activebattle, starter24/26HP, AbsorbPP19.
  Browser180s actual replay62/62rows reaches the same visible battle HP. SavingUI
  and exteriortransition also observed. Party GUI/SAVEDsuccessmessage were not
  captured at their short intervals; no browserFlash-counter or full-scene claim.
- Browser report0e9c4023b42d4384bf51e2249e5da649 SHA
  5c173a29f1a5601e02f65f7d33c17569013d833d5a5ebe7798d4e7da6dc9548c:
  10751video/21600visible ticks,0debt/mismatch/drop/underrun/warmup,62DOM inputs,
  maxsubmit20.2ms,180.001088audio seconds/44100Hz. Replay maxlateness5.143ms;
  dispatch evidence validated against preserved input and current measurement.
  This is a three-minute mixed smoke, not the required ten-minute scene regimes.
- Alignment caught an auditor hole accepting a complete267.883ms route compressed
  into1ms. Now dispatches must stay within2ms early/50ms late of nominal timing;
  complete duration has those explicit bounds too. The collapsed-time negative
  case fails; the actual browser replay passes. DOM keyup dispatch is not immediate
  guest-register release: SDK retains its existing≤70ms minimum-hold policy.
- Server exposes monotonic remainingtime; page uses a conservative earlier request
  anchor and never extends its existing deadline. Every measurement reserves its
  duration+2500ms for preparation/upload; replay starts only after asynchronous
  budget validation and diagnostic start. Upload and lease fetches are bounded.
- Actual50s-session late-load UI rejects the three-minute route without inputs,
  permits a10s report (597video/1200ticks,0audio failures/input events, replaynot-run),
  then autonomous emulator teardown is observed; server exits0. Exact relative
  client/server teardown timestamp was not independently recorded. Report SHA
  e0ff1f0521099c7c56251b64684b1eb2625709610e44950731b74c0aa8694f1f.
  Full local checks pass; all private sessions/tabs stopped. Public unchanged.


- v57normal release rebuilt to the exact tested drafttarget22beceecbe5d5edf607a3411fa19af4585a51e92a7ddd1cf1c6bbb1b54df1afd.
  BPS888452bytes/SHA82880edae3130610686c9dd41d6817c38ce811034dbb33d9ce8f28cd19e34c68,
  source7cffa0b469fc2693e177b1167212dbd3431ab87b; applyingtoverifiedbase is byte-identical.
  Only manifest/delta are committed. Full cartridges/ELFs/native saves remain private.
- Site48preparation copies all five changed/new SDKmodules from the exact15-file
  runtime used in the passing600sfieldcheck. Prior Site47build preserved intact,
  public hosting/auth/storage configuration unchanged. Typecheck/package inprogress;
  archive and publication checks pending. Public remainsSite47 until deployment.


Published v57 / Site48:

- Saved versionappgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_3daee28930f48191b035429c90f66438;
  deploymentappgdep_6acfdb1da5a881919c2132aa2740b68c succeeded2026-10-14T19:42:31.780463Z.
  URLhttps://sf-mini-monsters.devkunjadia03.chatgpt.site/; sourcea0ca6c9e83b98a1b0fbe17927e97539189cac6e9.
- First archivefailed AppleDouble check (111macOSmetadata members); retained private,
  neveruploaded. Repacked unchangedbuild/source withCOPYFILE_DISABLE=1; cleanarchive
  SHA59b0712fa275eb9711b84e63e20b0b90f5e2d4ce35fe45cd1341bf7013f42224.
 88-fileaudit passes, exacttested15-fileemulator runtime andv57manifest/BPS; no
  commercialcartridge/privateSave. Only ownedSFMMprototypeGBA iswhitelisted.
- ActualvisibleIAB loaderpaintscorrectly; DownloadSFpatch produces888452bytes,
  exactBPS SHA82880edae3130610686c9dd41d6817c38ce811034dbb33d9ce8f28cd19e34c68.
  Guest/signin controls remainavailable, ROMupload required, emulatorcontrolsinactive.
  No ROMimport/Continue/existingusergameprogress mutation. Own QA tabclosed and
  previousbrowservisibilityrestored. Screenshotpublic-v57-loader-visible.png.
- First anonymousHTTPbatch raised403; failingpath wasnotretained, so no cause is
  asserted. ExplicitQAUserAgentrecheck returns200andbyte-exactcontent forall18
  runtime/manifest/patch/originalprototype resources. Actualbrowserdownload also
  matches independently. Accessstayspublic; auth/storage unchanged; noGitHubActions.
- Fullcampaign/11humanqualitydomains, Safari/phone, IABlongclockdeficit, physical
  input/display deadlines, fullaudio/listening and50distinctsavecheckpoints remain
  open. This publication is an improved preview; fullgoal staysactive.


Critical creature-asset integration audit and fix:

- Independent immutablev57ROM/ELFaudit: all18species×6visual resources (stillfront,
  animatedfront, back, icon, normal/shinypalette)=108/108match Emerald baseline,
  0/108match intendedauthored assets. Engine PNG/paletteinputs do match authored
  files, but everyinput isolder than its generatedcache. All90tablebindings,
  18iconselectors and3sharedpalettes are correct. All18compiledcries match recipes.
  The battle screenshot indeed shows stockTreecko/Magnemite under SF names; prior
  original-creature visual-integration claims were wrong. Human approvals stay0/11.
- Cause: copy2 preserves oldsource mtimes, so Make retains newer inherited .4bpp,
  .gbapal andcompressedoutputs. Preserved216pre-fix intermediatefiles for18species
  privately before rebuilding. No filesremoved. Native contentrevision remains8;
  species/saveidentities/stats/moves/progression remain unchanged.
- Actual art-install boundary now validates front/back/animation/iconpalettes and
  uses timestamp-updating copies for allsix files/shared iconpaletteinputs. An
  independent real-Make test first reproduces six stale outputs with preserved
  timestamps, then reapplies identicalauthored inputs and rebuilds everytarget to
  exactsourcebytes. Six creature authoring/build tests pass. Nativev58build and
 108compiled-resource validation/coldsave/actualbattle/browser are pending.
- Alignment owns focused compiled-resource checker/tests only, deadline20:15UTC;
  root owns source installation/build/capture/publication. No more generic harness
  work ahead of this visible integration failure. Next check by20:10UTC.
- FreshIAB120s40ms-buffer smoke passes0audiofailures/debt/mismatch,7167video /
 14400visibleticks,8DOM inputs maxsubmit10.4ms; context/output120.000726s vs
  wall120.0006s. Report SHA57952ac274a51f5c41027237df903822ff79def15ce6f53f544436c29b037207.
  This short run does not close the older600s IAB discrepancy or fullaudio gate.
  Owned test tab/server stopped; browser visibility restored.


- v58firstdrafttarget63b10d0425af8a73bbae969dcbb9e75b6eae4777cfd31b44dde6da7f6f77a297
  nowpasses independent portableELF/ROM validation:108/108authoredvisual resources,
 90/90bindings,18/18iconselectors,3/3sharedpalettes and18/18originalcrycontrols.
  Twelve independent public format/bounds/ROM-ELFassociation tests pass. The
  negativev57audit stillfails0/108visual matches. No externalbinutils dependency.
- Actualnativev58coldContinue→partymenu→ordinarySave→gymbattle shows authored
  SproutSlugback/TrolleyKitfront andcustomthree-partyicons. Starterends24/26HP,
  AbsorbPP19, sameasv57route. Thisfixesintegration, not pixelcleanup/humanapproval.
  Productionchecker is beingadded beforeanyBPScreation; privatefullreceipt and
  public count/hashsummary willretainprovenance withoutpublishingbaseassets.


- Portablecompiled checker is now a mandatorypost-overlay/pre-BPS buildgate.
  A mismatch preserves an exclusive private fullreceipt and stops patchcreation;
  public manifests include only counts/checkerhash/receipthash andpendingapproval.
  Twelve format/association tests joinroutine localchecks; fullchecks pass.
- Same8888frame nativecontroller route onv57/v58 produces byte-identical131072Flash
  afterSavecounter4, with zerochanged declared domains. This is same-route evidence,
  not another fullcross-platform roundtrip or50distinctcheckpoint acceptance.
- Alignment other-art audit finds23/23checked non-creature resources exacttoauthored
  source in BOTHv57/v58, includingScottWu/courierportrait+field, doors/apartment/title;
 4/4trainer pointerbindings pass. No additional visible stale-art defect identified,
  so v58 staysfocused on creatures ratherthan producer-policy churn.


v58 / Site 49 publication — October 14, 20:25 UTC:

- Normal release target 63b10d0425af8a73bbae969dcbb9e75b6eae4777cfd31b44dde6da7f6f77a297;
  BPS 958249 bytes, SHA 1c42d19f4ddd10723f0ca79c216c9334900749d7ea5b8d82b04298aad20e3e1a.
  Final compiled-resource receipt SHA 96290808edec225b473a6c98a9d23c664f915532df259710790d2c03013a6be5.
- Actual Chrome battle/party navigation verified authored creature sprites/icons.
  Ten-second battle smoke: 597 video frames / 1199 visible ticks, zero dropped
  frames, debt, mismatch, underruns or warmup gaps. This is a short smoke only.
- Website source 96f1f70137b496b5f270511365e34fe6feaa21fa; saved Site 49 version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_f5c83947c1b88191b270a12f71f92ca6;
  deployment appgdep_6acfe49940b481919fe27d6d83223d48 succeeded at 20:22:58 UTC.
- Clean archive SHA ce5761354655e786c844b9535b8c4fe318264f9d1fd5a58e96522c57a3da5497:
  88 files, exact runtime/patch, no commercial cartridge, private saves or AppleDouble.
  Production browser BPS decoder reproduces the exact native target from private
  base input. All 18 anonymous public resources match local bytes; HTTP receipt
  SHA 9270c4f967f7a53c36225a6b98f92c02b38e2a1ef4cd7eecfee86ce7c1b2a3ba.
- Live loader and actual Download SF patch checked. Download SHA matches release;
  user cartridge/save/progress untouched. Screenshot public-v58-loader-visible.png.
  Public audience and auth/storage unchanged. No GitHub workflow runs.
- Alignment identified likely inherited enemy elevation causing TrolleyKit to
  float above its ground shadow; compiled metadata audit pending. Next visible
  task is correct authored creature placement and a matched review clip.
- Full campaign, 11 human domains and outstanding performance/save gates remain
  open. Goal stays active; no completion claim.


v59 creature placement work — October 14, 20:26 UTC:

- Peer read-only audit confirms TrolleyKit inherited enemy elevation 16 from its
  stable Magnemite slot. Native battle code raises the sprite and enables the
  airborne shadow for a nonzero value. Its authored cable-stoat concept is grounded.
  All 36 front/back coordinate records already match intended authored settings.
- Added explicit per-creature enemy elevation: TrolleyKit 0; the other 17 retain
  their current effective values, including airborne PierPeep 16. The installer
  overrides inherited or implicit entries. Compiled-resource gate now checks all
  18 placement bytes. Seven authoring tests / twelve format tests pass locally.
- Acceptance pending: compiled table changes only byte81, fresh native/browser
  ordinary-Continue battle, feet/crop/UI check and same-route save comparison.
  A native matched review clip and user art score remain pending. No art score,
  content-revision change or full-campaign progress is claimed for metadata alone.

- Negative-control audit on immutable v58 fails exactly TrolleyKit elevation
  (17/18 placement matches); all 237 existing visual/binding/selector/palette/cry
  controls still pass. Full local checks pass before the v59 native build.


v59 compiled/native/browser placement acceptance — October 14, 20:29 UTC:

- Draft and normal release reproduce target
  3c4950c727ef1bdd84487245571e6342a349ed47a169fa997a839a75f28df01f.
  Whole-ROM comparison to v58 changes exactly one byte at offset 3182917:
  gEnemyMonElevation[81] 16→0. Other 411 elevation bytes and every remaining ROM
  byte are unchanged. All 18 placement and existing 237 resource controls pass.
- Native cold Continue with existing ordinary Flash, gym deployment and one
  Absorb places TrolleyKit on the platform without airborne shadow or clipped
  feet/UI overlap. The matched route ends at 24/26 HP, Absorb PP19. All 131072
  Flash bytes match v58 at save counter4; zero changed declared save domains.
- Actual Chrome shows the same grounded pose. Ten-second static battle smoke:
  597 video frames / 1200 visible ticks; zero debt/mismatch/drop/underrun/warmup,
  final audio acknowledged. Report SHA
  e19e7a813bf767d05df1e6d1367550312cd84092bc3ab284763b67b73010d99b.
  No measured inputs; not a new performance or full round-trip acceptance.
  Temporary browser tab/server stopped; public progress untouched.
- Private 53.309-second matched controller-only native comparison shows v57
  inherited creature art beside v59 authored art and corrected placement. This
  is an SF before/after, not a vanilla Emerald quality reference. Clip SHA
  8ae176ba676edc98b250a4b7b72b513a2d97f37a4eef39281518acc42ea5439b;
  path creature-placement-v59-before-after/comparison.mp4. User review requested;
  no score inferred. Full quality-domain approvals remain 0/11.
- Peer survey also notes inherited entrance motions and three possible hovering
  poses for later art review. PierPeep's folded-wing pose deserves separate
  review; this fix preserves its existing elevation16 rather than expanding scope.


v59 / Site 50 publication — October 14, 20:32 UTC:

- BPS 958258 bytes, SHA8e3774a6d9e88706fb591449d7c1491b856b5ba96fab6dd532e9efc10acc7b69.
  Website source b73b5d0793b5ff3a35d512082be01311bd899fbc; saved Site50 version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_5e8019fdc1088191b9251f54f3de0d67;
  deployment appgdep_6acfe674d0f48191b81e5a54549c8774 succeeded20:30:56UTC.
- Clean88-file archive SHA50d8e5a7a827c2984797d7a339e5217d85255d754302917bb9ac895430b02ef1;
  no commercial ROM/private saves/AppleDouble. Browser BPS decoder produces exact
  tested target. All18 anonymous public resources match local bytes. Live loader
  and actual Download SF patch verified; screenshotpublic-v59-loader-visible.png.
- Public audience, auth/storage and player progress unchanged. Temporary QA tab
  closed and IAB visibility restored. GitHub Actions not run. Human scores still
  pending, goal active, stop deadline unchanged. Next: actual Safari120s smoke
  while alignment reviews the next concrete first-slice world-art improvement.


Safari attempt / v60 park approach — October 14, 20:35 UTC:

- Actual native Safari loaded and verified the local v59 cartridge/checkpoint,
  but its page remained hidden and its canvas black. Diagnostic start rejected
  with "Keep the diagnostic tab visible." Raising the window and normal Window
  menu controls did not produce an eligible foreground observation. No timing
  report was created; no compatibility pass or engine/rendering defect inferred.
  Test instance/audio stopped, own tab closed, finite server terminated. Safari
  remains an open acceptance gate. Public progress/settings untouched.
- Alignment composition review proposes a continuous 3x2 landing at x15–17,
  y21–22 beside South Park's discovery bench. Five existing ordinary lawn cells
  become existing neutral pavement; the sixth is already paved. No new palette,
  metatile, prop, blocker or map expansion. Bench/script/NPCs/warps unchanged.
- v60 acceptance pending: exactly five of 1280 compiled words change tile ID;
  collision/elevation/other words/resources/events remain equal. Actual cold
  Continue approach and interaction must show the joined landing in native and
  browser play; human art approval remains pending. No new tests for the small
  reversible map edit; existing checks and compiled/native evidence will verify it.

- Existing frontage whole-map snapshot correctly detected the five planned lawn
  changes. Its expected baseline now includes only that reviewed landing; the
  frontage assertions and all other map/event/collision protection are retained.


v60 / Site 51 acceptance and publication — October 14, 20:43 UTC:

- Draft and normal target3ae1f9d52904d4e1efe3d04785f905b6a92f1c67d8c9bb49a104c2262b1deff6;
  BPS958259bytes SHA4d8f97ddb8ea223ffc610871241e9f5eebf5c729cf88541582ffa2fdc9daaced.
  Whole-ROM diff from v59 is exactly five intended map bytes. Other1275 mapwords,
  every collision/elevation bit and all other ROM bytes/resource addresses remain
  equal, including events, scripts, doors and graphics. Existing local checks pass.
- Actual native cold Continue and40.182s controller route reaches17,21 beside
  bench18,21, sets the one-time flag and awards3 Oran Berries. Full SaveBlock1
  (15752bytes), SaveBlock2(3884bytes) and party match the same v59 route exactly.
  This is in-RAM interaction evidence, not an ordinary Save or new round trip.
- Actual Chrome displays a flush connected landing. Controller A activates the
  already-claimed branch: "A sunny bench... REBRAND BEFORE DEMO DAY." Own test
  instance/tab/server stopped. Screenshotpark-v60-browser-bench-repeat.png.
- Matched40.182s SF before/after clip: park-approach-v60-before-after/comparison.mp4.
  Human art approval pending; this is not the vanilla Emerald reference gate.
- Website source5db0a91d7f23acc27987336452b3c42891c83519; Site51 savedversion
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_1290379aca408191b49b923db158d85d;
  deploymentappgdep_6acfe8e26f588191994d54c711faf3e4 succeeded20:41:23UTC.
  Clean88-file archive SHA84fef9b59c904636f21d5ec5ef8e740c0ae649514d52ed64ccb9918eb976e68c,
  no commercial ROM/private saves/AppleDouble. Browser BPS decoder matches exact
  target. Both changed live resources match local bytes; unchanged15-file runtime
  matches the audited archive. Live loader screenshotpublic-v60-loader-visible.png.
  Download control unchanged from v59; no redundant user-folder download needed.
- Public audience/auth/storage/player progress unchanged. No GitHub Actions.
  Human full-domain approvals0/11; all campaign/performance/save gates stay open.
- Alignment's finite intro audit confirms original PuddlePrig already renders,
  but NAVAL dialogue still accompanies baseline64x64 Birch art (2048rawbytes,
  dedicated16-color palette). Next: one original full-body Naval intro candidate,
  retaining current text, fades, platform, monster, player-selection and save flow.


v61 original Naval intro figure — October 14, 20:54 UTC:

- Replaces the inherited large Birch figure accompanying existing NAVAL welcome
  text with one original generated public-person caricature. A second source
  improves head proportions; a deliberate RGB555 palette preserves gray beard
  and eye accents. Eighteen pinned native face pixels separate eyes/brows and
  connect beard clusters. Likeness/pixel-art approval remains pending.
- Selected source and both exact prompts/appearance reference are in
  assets/characters/naval-intro-v1. Original first two native conversions are
  preserved privately. Native output: one64x64 frame, fifteen opaque colors plus
  transparent index0, figure27x58, baseline62. No commercial image used as input.
- Reuses the portrait converter and existing palette-policy parser. Rebuilding
  Scott's default portrait privately yields identical PNG/2048graphics/32palette
  bytes. Hash-pinned native cleanup rejects changed source/palette/input/output,
  duplicate/invalid/no-op edits; four independent pixel contract tests pass.
- New engine graphics path avoids inherited caches. Only two raw graphics/palette
  declarations change; existing tag0x1006, template, coordinates, fades, platform,
  displayed creature and player-selection behavior are retained. Pre-BPS compiled
  check reads both actual linked blobs and three frame/palette/template bindings.
- Selected-art negative control on immutable v60 fails exactly graphics/palette
  while all three display bindings match. Existing full local checks pass.
  Native build, actual NewGame/Continue paths and browser appearance still pending.
- Naval's separate field placeholder and inherited gender-selection portraits
  remain separate future work. No new NPCs, stats, save schema or content revision.
  Public staysv60/Site51 while this candidate is verified. Full human approvals0/11.


v61 / Site 52 verified and published — October 14, 21:06 UTC:

- Draft/normal target238d7bed7afa88c3db9204d8c921b8de83cabb31af4cb1637e709dfd03c31c96;
  BPS958943bytes SHAaeaf969c38ad87adc6454184d07e1b2955f6401421bd867cbd67931a40ef6bb2.
  Compiled intro5/5 and all255 existing creature/elevation/resource controls pass.
  Exactly796 ROM bytes change, all inside the2048-byte intro figure and32-byte
  palette. All other ROM bytes and audited symbol addresses remain identical.
- Actual controller-only native NewGame reaches authored Sunset23,22 through
  existing intro/monster/gender/name flow. Full15752-byte SaveBlock1 and3884-byte
  SaveBlock2 are identical to v60 on the same controller route (one default look).
  Existing ordinaryC4 Flash coldContinue to SouthPark13,6 also matches both full
  blocks exactly. These are scoped compatibility checks, not new save round trips.
- Actual Chrome welcome and controller A show the original figure beside
  "I'm NAVAL...". No render crop/palette conflict observed. Owned QA emulator,
  audio, tab and finite server stopped; public player progress untouched.
  Screenshotnaval-v61-browser-named-welcome.png.
- Matched40.182s SF before/after intro clip (not vanilla Emerald reference):
  naval-intro-v61-before-after/comparison.mp4 SHA
  bf6b863768743195772f1e75cdd28006cf0e720136891ba52c41f0505fcbc6a9.
  Equal controller input and byte-identical native PCM; audio unchanged/unscored.
  Likeness/art remains pending human review; full quality approvals0/11.
- Website source0185c8531bd33eb79f208049ceab919652e3dbd0; saved Site52 version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_1b6bbba3ed108191b102ea349834e67a;
  deploymentappgdep_6acfee27d3fc8191beedb5899f1c0d58 succeeded21:03:45UTC.
  Clean88-file archive SHAd85da6737fc5ce62467bb92cc3416bde1609b308951f6411da8123b305bca94d;
  no commercial cartridge/private saves/AppleDouble. Actual browser BPS decoder
  matches target. Both changed live resources match local bytes; unchanged
 15-file runtime matches archive. Live loader screenshotpublic-v61-loader-visible.png.
- Public audience/auth/storage unchanged; no redundant user-folder download or
  GitHub Actions. Goal remains active through October15,18:00 Pacific. Full campaign,
  native/browser/device/performance/listening/50checkpoint and human gates stay open.
- Next field-art task: original Naval9pose sprite in existing authored-SF-unused
  ProfBirch64 slot, Sunset localId7 only, shared existing Sunset palette unchanged.
  Existing named-cast Continue repair can refresh cached48→64 without resetting
  position/movement. Garry keepsGentleman48. No new NPC/dialogue/schema/revision.


v62 original Naval field sprite — October14,21:21UTC:

- Original9pose Naval joins the existing Sunset group. The native palette and
  Roon/Karpathy packed sprites remain exact; all32 palette bytes and every used
  color are retained.43 pinned face pixels improve tiny eye/beard separation,
  preserving all north/body/footstep pixels. Likeness/art/animation approval pending.
- Sunset localId7 changes only graphics alias to SF_NAVAL→ProfBirch64. Garry keeps
  Gentleman48. The native239-entry pointer table/dynamicbase240 remain unchanged.
  Slot64 has no other authored SF owner; unreachable Hoenn scaffolding references
  would inherit the look. No NPC/dialogue/quest/reward/schema/revision expansion.
- Existing named-cast cache helper is byte-identical; its generated predicate will
  include64. It can refresh cached templates and current-map active appearance
  without resetting positions/facing/movement. Actual old-save acceptance pending.
- Genuine v61 ordinarySavecounter5 prepared at Sunset18,18 by returning via Muni
  and using the native Save menu. Its cached Naval template is Gentleman48 at14,17.
  This is the battery used for matched coldContinue tests, not an injected fixture.
- New pre-BPS field-cast gate reads actual linked sprite bytes, all nine frame
  pointers, reserved-slot binding, palette/dimensions/frame binding and all shared
  palettes. Negative v61 control matches32 prior checks then fails missingSFNaval.
  Earlier creature/intro guards stay required. No generic test harness added.
- Existing cast authoring/resume tests pass. Full checks after the final compiled
  guard, v62 native build, compiled pointer normalization and actual native/browser
  old-cache/save/reload checks remain pending. Public staysv61/Site52; goal active.


v62 / Site53 verified and published — October14,21:51UTC:

- Draft and normal target00da16f1e22d38710e7a353c5e03ff1f88878446d7cd8eb711759c591a08a30e;
  BPS960239bytes SHA4fe6c92523fa8fc549fe06e7b6035c9a70315789fc7e997747bd5bf29d2c8856.
  Local full checks pass. Compiled cast36/36, intro5/5 and creature255 controls
  pass before patch creation. All239 field graphics pointers normalize identically
  except intended slot64; prior seven original cast figures/three palettes and
  Garry's Gentleman48 resources remain byte-identical.
- Genuine v61 ordinary FlashC5, Sunset18,18, caches Naval as48. Matched controller
  coldContinue on v61/v62 changes exactly nine SaveBlock1 bytes: Naval template
  graphics at0xd01 becomes64, plus two bytes each in four inert ROM pointers.
  Exact symbol identities at0xde8/0xed8/0x1160/0x1268 are OldaleTown_MapWarps,
  DewfordTown_MapWarps, FallarborTown_MapWarps, VerdanturfTown_ObjectEvents.
  The unchanged inherited48-byte LoadSaveblockObjEventScripts copies64 records
  even when the map contains8, so adjacent ROM event headers enter unused localId0
  cache records15/25/52/63. Source and destination offsets were verified against
  each ELF, not broadly ignored. No unrelated inherited-loop change was made.
- Every other15752-byte SaveBlock1 byte, all3884 SaveBlock2 bytes,600 party bytes
  and128KiB input Flash are exact. Of576 active object bytes, only Naval graphics
  at0x71 changes. Position/facing/movement/flags and other NPC state stay exact.
  Initial unclassified failure receipt is retained alongside final symbol-aware
  legacy-cache-comparison.json; alignment independently confirmed provenance.
- Actual native Save menu upgradesC5→C6; declared party/items/money/quests/badges/
  location/settings remain unchanged, save counter/stat increment once, clock
  advances. ColdC6 reload retains Naval64. Flash audit passes. This is scoped
  compatibility, not another cross-platform round trip or campaign checkpoint.
- Actual Chrome starts from a v62 title-state with unupgraded genuineC5 Flash and
  cached Naval48, then normal controller X opens CONTINUE and enters Sunset. New
  Naval appears without map exit. It is not a pre-upgraded field checkpoint.
  No browser save/export was made. Own emulator/audio/tab/finite server stopped.
  Screenshotnaval-v62-browser-legacy-continued.png; public player progress untouched.
- Matched40.182s actual walking/conversation SF before/after clip:
  naval-field-v62-before-after/comparison.mp4 SHA
  3ec2b6da94ab4a2fb4786933fc7737b790c23f9f3d24abd7453041bd97ae3475.
  Equal controller input and byte-identical PCM. This is not vanilla Emerald
  reference footage; art/likeness/animation acceptance remains pending.
- Website sourcef75c4dbb748a3806291760992df0f89adf78e987; saved Site53 version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_1a5f9d19577081918d0f901f2b48d421;
  deploymentappgdep_6acff8c281588191b44940f94e9eba67 succeeded21:48:59UTC.
  Clean88-file archive SHAbed65395f4c8fc95e4a5ea0efdd420031e42fee2ce457ef3d1bf4add1e35c93d;
  no commercial cartridge/private saves/AppleDouble. Browser BPS decoder matches
  exact target. Initial live patch fetch differed during publication; subsequent
  canonical revalidation and versioned URL both match. Final two-resource receipt
  SHA936fb0cd13bd3fae0b4970e5c97c92134640335d10259ae9c581828ac975cbca.
  Unchanged15-file runtime matches audited archive. Live loader screenshot
  public-v62-loader-visible.png. Public audience/auth/storage unchanged.
- No GitHub Actions, DB migration, redundant download or campaign expansion. Human
  full-domain approvals remain0/11. October15,18:00 Pacific deadline stays active.
  Alignment next-priority review requested21:50UTC, finite20minute read-only task.
  Full campaign, first-slice comparison, music, performance/device and50distinct
  save-checkpoint acceptance gates remain open.


v63 portable field journal — October14,22:00UTC:

- Alignment's finite read-only review identifies the absent journal as the next
  useful first-slice workflow. Correct SF city-map art/markers/Guide AREA mapping
  remain separate unfinished work; renamed labels do not replace Hoenn geometry.
- Adds SF-only JOURNAL before EXIT in the normal native Start menu. SAVE/OPTION
  indices stay unchanged. Inherited PokeNav is suppressed only on authored SF maps,
  including older saves with its flag set, keeping the menu within eight rows.
  No flag grant, item/reward, new NPC, save schema or content-revision change.
- Eight read-only leads use existing starter/parcel/relay/badge state, with earned
  badge priority. Location caption covers all five authored maps. Sensor delivery
  directions adapt after Muni arrival instead of sending the player back west.
  Post-badge text explicitly identifies the preview endpoint and future chapter.
- Native framed26x17-tile card uses the existing font/palette and one short text
  line per callback. B restores the Start menu/cursor; Start closes and restores
  field controls. Allocation failure preserves the existing menu. Default menu
  fade is excluded. The page never writes quest/party/item/save state.
- Draft target663539f154c5456caa4b17b13501f0b4b58a4f58447d30136b2cd750278451dd;
  existing compiled cast36/36, intro5/5 and creature255 controls pass. Sanitized
  production-header tests cover all eight leads, badge precedence, five location
  captions, arrival directions, read-only state, cleanup and allocation failure.
- Earlier native/browser candidates display the journal and return to normal
  movement. Fresh no-starter and earned-badge pages are readable. Final text
  variant native/browser/save acceptance and normal publication remain pending.
  Initial synchronous text build showed seven play-clock VBlank-count difference
  from a matched idle menu; staged text reduced this to four. This remains scoped
  observation, not a native deadline, physical-input or performance-gate pass.
- Public remains v62/Site53. Full human approvals0/11 and all campaign/map/audio/
  first-slice/performance/save-checkpoint gates remain open. No GitHub Actions.


v63 journal native acceptance — October14,22:02UTC:

- Full local checks pass with sanitized production-header journal tests included.
  Nine independent chapter cases cover the eight leads plus badge overriding old
  quest/relay state; five location captions and Muni-arrival hint are checked.
  Native window allocation bounds, read-only state, B/Start lifecycle and allocation
  failure pass. Tests use small native-ABI stubs without a private SDK dependency.
- Final compiled cartridge actually displays companion choice after fresh NewGame,
  Scott challenge from genuine olderC6 Save, and preview endpoint from an earned
  first-badgeC4 Save. Opening dialogue was advanced through normal controller A;
  no quest injection or state from another cartridge was used. These are three
  native scenarios; all eight leads are not claimed as native campaign captures.
- Matched final-cartridge C6 coldContinue routes differ only by opening JOURNAL
  versus waiting in Start menu for equal requested frames. All15752 SaveBlock1
  bytes,600 party bytes and input Flash remain exact. SaveBlock2 differs only at
  observed playTimeVBlanks offset0x12 (journal17, idle21); all other3883 bytes equal.
  No blanket clock/opaque-byte exclusion. Read-only gameplay receiptSHA
  c5ddd66fa695a9afa8fae5e33d830e481a81c9fd3176d209f6361e29d69b7a6b.
  This clock observation does not prove native render deadlines or physical input.
- Native B returns the eight-row menu with JOURNAL selected and SAVE still row4.
  Start closes; actual controller Right then moves18,18→19,18 in the staged build.
  Actual Chrome controls also open/B-return/reopen/Start-close and resume movement.
  Latest text variant browser review is underway; no public save/auth touched.
- After opening the final journal, normal B→two Up→SAVE produces ordinaryC7.
  Flash audit passes unchanged declared party/items/money/quest/badge/location/
  settings, one counter/stat increment and nondecreasing clock. ColdC7 reload
  opens the correct Scott objective. This is not an additional cross-platform
  round trip or another distinct completed campaign checkpoint.
- Public remains v62/Site53 until v63 normal build and publication verify. All
  first-slice quality/complete SF map/music/device/performance/campaign gates and
  full human approvals0/11 remain open. No GitHub Actions or DB changes.


v63 / Site54 verified and published — October14,22:04UTC:

- Normal sourcef8d873e363830554c1e791d5f0e90c197009f003 reproduces final draft
  target663539f154c5456caa4b17b13501f0b4b58a4f58447d30136b2cd750278451dd.
  BPS1004087bytes SHA79e3e8050e32d77a952e09674402c9c77c839bc87d2f8172b7bbbed77f1bb275.
  Native resource gates and complete local checks pass. Public patch roundtrip
  through the actual browser decoder matches the exact target.
- Final Chrome normal X opens the journal with corrected COGNITION clinic hint.
  Ten-second visible opening smoke records597video frames/1200ticks, no discarded
  debt/frame mismatch/audio drops/underruns/warmup and final audio ACK. Two DOM
  events max68.4ms to dispatch and4.1ms dispatch-to-submit. Not physical input,
  guest consumption, full native update deadlines or a broader performance pass.
  Report SHA1bca5b1ade0752bf7d5e89ee2d957ca9d474ff25412ee48aa47bccfea2a3b69d.
  Screenshotjournal-v63-final-browser-page.png. Own emulator/audio/tab/server stopped.
- Website source8bc17cc966a945939145277a4e36437092cd4ac9; saved Site54 version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_258e951fa498819195322055a1f2a4c0;
  deploymentappgdep_6acffc23ef048191a09fe963c7528d43 succeeded22:03:25UTC.
  Clean88-file archive SHA824af56b5bb942363b6f75e637fb66dfceee736697f1370aff062cf673f0a7e4;
  no commercial ROM/private saves/AppleDouble. Unchanged15-file runtime and hosting
  match; public audience/auth/storage retained. Immediate manifest response was
  stale during propagation; subsequent canonical revalidation matches both assets.
  Live receipt SHA6b4e3bfc598d911fd87fed2c1e53d2b974cc8b3880fc193bb290adab08f63f6c.
  Live screenshotpublic-v63-loader-visible.png; no player ROM/save imported.
- Journal is one completed scoped workflow, not full interface/map/campaign or
  first-slice quality acceptance. All eleven human domains remain0/11. SF city map,
  Guide AREA geography, original audio/remaining cast, campaign, real-device/full
  performance and50distinct-save-checkpoint gates remain open. No GitHub Actions.
  Goal continues through October15,18:00 Pacific; next alignment check by22:20UTC.


SF habitat map preparation — October14,22:11UTC:

- Actual controller Guide→detail→AREA in v63 confirms visible Hoenn geography and
  inherited player head, despite SF labels. Private screenshot sf-map-v63-area-before.
  Alignment completed a finite read-only engine audit; next check by22:35UTC.
- Pinned DataSF Analysis Neighborhoods actual source j2bu-swwd, PDDL metadata,
  produces an original geographic SF coastline/park/urban pixel-map candidate.
  Catalog p5b7-5n3h is a visualization; its returned null-geometry GeoJSON is kept
  privately as diagnostic evidence. Exact source hash and projection are tracked.
- Native atlas fits232 tiles. Shared geometry exports both32x32u16 Guide tilemap
  and64x64u8 affine regular-map tilemap, plus full48-color96byte palette atBG7–9.
  Only Outer Sunset/South Park receive active markers; no new campaign areas.
- Engine integration still pending: replace both backgrounds, same28x15 section
  grid and two entry bounds, SF-only encounter filtering before table scans,
  correct per-kind encounter lengths, explicit five-map player-parent positions
  and an original courier map head. Legacy special/roamer paths must not add
  Hoenn habitats. Art/native/browser/save acceptance remains pending; publicv63.


v64 SF habitat-map engine integration — October14,22:14UTC:

- Native first candidate32b575128a803e44d4f1d2c81a94294496b2d365be215fc190a14fd324ea5686
  renders the geographic SF map through ordinary Guide→detail→AREA controls.
  Original courier head appears at the Sunset anchor. Starter wild-area unknown
  is expected for the gift/evolution lines; wild-species highlights still pending.
- Both native background surfaces use one109-tile original atlas, distinct correct
  tilemap encodings and full48-color palette. Two hub entry rectangles and the
  28x15 section grid share the same projected coordinates; other cells are NONE.
  Existing map IDs/headers and real-world five-map SF graph remain unchanged.
- Native habitat search reads only the canonical encounter-map whitelist derived
  from existing chapter data, before accessing encounter lists. Four encounter
  kinds use their own native lengths, including ten fishing slots. Inherited
  special/hidden/roamer logic is retained as unused scaffolding and bypassed by
  the SF entry point. No encounter probabilities/species/world/save data change.
- Explicit parent rows derived from the five authored headers place apartment
  at Sunset and clinic/gym at South Park, ignoring stale escape/dynamic warps.
  Original map head reuses the courier's authored indexed face/palette for both
  current shared player looks; native128-byte graphic/32-byte palette per path.
- Draft builds and prior compiled creature/intro/cast controls pass. Mandatory
  compiled-map verification, native behavioral tests, wild highlights/interior
  markers, browser controls and ordinary save acceptance remain pending. Public
  staysv63/Site54; human0/11. No new travel/campaign/areas or GitHub Actions.


v64 habitat integration controls — October14,22:17UTC:

- Mandatory pre-BPS map gate reads final ROM/ELF: ten background/head resources,
  shared420-byte grid, two entry rectangles/two label pointers, four-byte habitat
  whitelist and fifteen-byte player-parent table. All17 checks pass. The same
  validator on immutablev63 passes only the two preexisting names and fails15
  integration checks. Full private receipts retained; quality approval pending.
- Portable ELF reader admits the specific map resource families/tables. Existing
  twelve parser/resource tests pass. Guarded rebuild reproduces32b575128a803e44d4f1d2c81a94294496b2d365be215fc190a14fd324ea5686.
  Full local checks pass, including native sanitizer tests and map serialization.
- Production habitat tests poison foreign encounter pointers, verify Sunset-only,
  Park-only/both/absent species, exact land12/water5/rock5/fishing10 bounds and
  stale special-count reset. Five player-parent cases ignore stale warp fields
  and preserve full supplied game state; unsupported maps preserve native state.
  Hardware-format test reconstructs both tilemap strides and verifies geographic
  anchors(7,8)/(18,5), palette isolation and109≤232 tile budget.
- Actual controller Binpossum AREA capture reads native species288, two areas
  (0,9,section0)/(0,10,section1), and zero special areas. Both highlights align
  with SF pins; no legacy map highlighted. Starter AREA remains unknown as expected.
  This is scoped native evidence, not all150-monster/campaign/art acceptance.
- Interior native marker/save checks and browser/matched review still pending.
  Public remainsv63/Site54; full human approvals0/11 and all broader gates open.


v64 native/browser acceptance — October14,22:23UTC:

- Actual native Guide AREA verifies Binpossum both SF maps, Pinepip Sunset only
  (native species298), Hushmoth Park only(species392), and zero special areas.
  These three actual wild cases plus gift-starter unknown complement the bounded
  production-header tests; all150 species are not claimed as checked.
- Actual ordinary saved-context Continue opens AREA from Sunset, South Park,
  clinic and gym. A new normal walk into the apartment, ordinaryC8 Save and cold
  Continue supplies the fifth context. All five map pairs/sections/cursor/icon
  values match native anchors(8,10)/(19,7), cavefalse. Full receipt SHA
  4230044e712c361547740d83cea2a2b326f3dc39391e212617c920c02aa2b10b.
- Apartment travel changes declared location/warps, friendship-step variable
  0x402A91→103 and GAME_STAT_STEPS347→360. All other declared domains remain exact;
  save counter/stat increment once. Initial overly strict location-only assertion
  failed; exact walking counters were checked against native definitions. No
  blanket variable/stat exclusion and no stationary/cross-platform roundtrip claim.
- Chrome displays the SF map with both habitat glows; normal B returns to actual
  Binpossum info. Ten-second visible smoke597video/1200ticks, zero audio drops/
  underruns/warmup/frame-debt/mismatch, final ACK. Two DOM events max69.4ms dispatch,
  max4.9ms dispatch-to-submit. Scoped pipeline receipt SHA
  dea10a55a4b66630f26812493e8b75f152ea36d5a1db6f0c09222578e78e4a17.
  Screenshot sf-map-v64-browser-two-habitats.png. Own emulator/audio/tab/server stopped.
- Matched31.543s controller before/after (SFv63 inherited geography vsSFv64 SF map):
  sf-map-v64-before-after/comparison.mp4 SHA
  0bf4d58183168a043b54e4ec4f329deef886eaa6a298141c92605951943256d6.
  Both complete native240x160 captures share input/clock/frame count. Native PCM
  differs; both audio tracks retained, unscored. This is not a vanilla Emerald
  reference gate. Art/likeness/geography readability approval remains pending.
- Normal source709e295017c3aa9eae40ee645d6e3cde957ae246 reproduces tested target
  32b575128a803e44d4f1d2c81a94294496b2d365be215fc190a14fd324ea5686;
  BPS1021231bytes SHA3dcf90344c33f8209056453e28e6e67127fe20829f83364835099c6928d2c5ad.
  Compiled map17/17, cast36/36, intro5/5 and creature255 controls pass; full local
  checks pass. Publication pending; public staysv63/Site54. Human0/11; full16hub
  interactive map/campaign/device/performance/save gates remain open. No CI runs.


v64 / Site55 verified and published — October14,22:25UTC:

- Website source56f1cb6f59d2fb888f3877db31ce5fbf751ab24f; saved Site55 version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_22de2efae17881918f308bf02793a274;
  deploymentappgdep_6ad000f8d0408191a770be6a687e7f2f succeeded22:24:00UTC.
  Clean88-file archive SHA1142aba7e4e0f42f6cdc3315b3a7204d07e621a89404fbb561d23c753cd59c98;
  no commercial cartridge/private saves/AppleDouble. Actual production BPS decoder
  reproduces exact target32b57512. Both changed canonical live resources match local
  bytes; receipt SHA4880300f61fb28cafbce3e19760a36d7ea2390a1bf8fcc223ecbd14a73c1e96b.
  Unchanged15-file runtime/hosting match; public audience/auth/storage retained.
  Live screenshotpublic-v64-loader-visible.png; no ROM/save imported publicly.
- Original SF geographic outline, two first-slice habitat entries, courier head
  and source-derived player/encounter tables are integrated; geometry/art/habitat
  clip approval remains pending. This does not complete the sixteen-hub map,
  full interface, campaign, native/device/performance or50checkpoint gates.
  Full human approvals remain0/11. No GitHub Actions, DB migration or new monitor.
- Alignment check22:24UTC shared all native/browser/save evidence and assigned a
  finite20minute read-only Garry Tan field-sprite slot/palette/cache safety audit.
  Remaining Jonathan/Dylan/Garry field placeholders are visible first-slice art
  gaps. Root owns research/art/implementation/build/publication; next check by
  22:54UTC. October15,18:00 Pacific stop remains active.


Original Garry candidate and city-map access collaboration — October14,22:32UTC:

- v64 remains public. Existing Garry is the sole authored SF owner of Gentleman48
  at South Park34,23. Original nine-pose public-person caricature uses his official
  YC portrait appearance and our original Karpathy atlas as style reference.
  Photo reference stays private; original generated source and exact prompt tracked.
  Outfit/game dialogue are fictional. No NPC/position/script/movement expansion.
- Initial fixed32-byte South Park palette reproduces both prior clinic characters'
  packed PNG/gallery exactly. First native Garry pass makes overshirt merge with
  skin. Deliberate followup uses only previously unused14/15 for cream and gray;
  snapshots preserve original quantization for Justine/Patrick. First28 palette
  bytes, both2304-byte sprites and all their visible RGBA pixels stay exact.
  Whole shared palette/PNG metadata are not claimed identical after this change.
- A232-edit pinned native head pass stabilizes south/west head positions across
  steps and separates spectacle lens gaps, cheeks and beard. North and all body/
  footstep pixels y19+ remain untouched. Source/palette/before/after/every pixel
  are hash-pinned by existing cleanup tooling; no new art framework. Human
  likeness/readability/animation approval remains pending.
- Existing slot48 can stay numeric48 on older saves; new pointer/appearance and
  special palette load will require actual coldContinue/clinic/save tests. Native
  engine build is deliberately held while the alignment chat owns separate files.
- Alignment's22:29 exchange prioritizes discoverable city-map access alongside
  art: finite30minute implementation task owns field_journal.h/field_journal.py
  and focused map-bridge/tests only, with no builds/deploy/commits. Root owns
  cast/content/art and all integration review/build/spec/publication. Intended
  JOURNAL SELECT→native SF MAP preserves eight menu rows/Save position and save
  schema; short SF MAP title must fit native seven-tile window. Source/acceptance
  pending. Next alignment exchange by22:59UTC; user stop October15,18:00 Pacific.


v65 journal map handoff and first native checks — October14,22:40UTC:

- Alignment delivered/froze six owned files22:34:55UTC, within its30minute task.
  Root reviewed production/native return lifecycle and reran both sanitizer
  binaries. SELECT fades from JOURNAL into the existing native field map; A/B
  returns to Start menu with JOURNAL selected. Existing B→menu/Start→field behavior
  remains. Allocation failure retains journal ownership and fades it back in;
  no queued journal DMA follows native VBlank handoff. No flags/items/schema change.
- Short SF MAP title stays within the native seven-tile title window; non-SF
  scaffolding keeps its original title. Existing native display/cursor/close loop
  is reused. Root's full local checks pass after reviewing one expected whole-plan
  snapshot: the sole source-world JSON change is Garry's symbolic alias, which
  still expands to numeric48; map rows/events/coordinates/flags otherwise exact.
- Combined draft0.0.65-city-map-and-garry-preview target
  0b5d830eed40015d3f782f6bfa420732cd110013b210754a4d5f10ce7c986fff builds.
  Compiled cast40/40, map17/17, intro5/5 and creature255 controls pass. Native map
  opens from both Park older-save JOURNAL and fresh no-starter Sunset JOURNAL;
  SF MAP/section labels fit. Actual B returns eight-row menu with SAVE unchanged;
  another B and Left moves33,23→32,23. Screenshotscity-map-v65-park/newgame/back-menu.
- Genuine v64 ordinaryC5 Save beside Garry atPark33,23 has SHA
  b56489a2a318fab7d345c66707100072bc5c95b04c66696780ee2e54cfcc499a.
  ColdContinue displays original Garry without leaving the map. Cached graphics
  stays48→48. All3884 SaveBlock2,600 party and576 active-object bytes match v64.
- Exactly14 SaveBlock1 bytes differ, solely13 script-pointer words: three actual
  SF NPC scripts and ten unused records from the unchanged inherited64-record
  copy loop over the current three-NPC Oldale array. EACH pointer is verified
  against this ROM's exact copy-source offset and same named target in both ELFs;
  no Sunset exceptions reused. All remaining SaveBlock1 bytes exact. Copy-function
  bytes match. Raw unclassified receipt retained; symbol-aware proof SHA
  9ee613c9ea62edcd42f2d5edc1423534fe6b903475087f5463fb24091a047887.
- Native/browser dialog/clinic/ordinarySave, footer/read-only map workflow and
  final release acceptance remain pending. Public staysv64/Site55; human0/11.
  Latest alignment handoff acknowledged22:36UTC; next check by23:05UTC. Root owns
  all further edits/builds/publication; peer task stopped. No GitHub Actions.


v65 public city-map access and original Garry — October14,22:49UTC:

- Native source8bff425 and normal release reproduce draft target
  0b5d830eed40015d3f782f6bfa420732cd110013b210754a4d5f10ce7c986fff.
  BPS1024149bytes SHA333aa289bfaff81ad13f50e485d5f00dc50786339a651ac0fa05e83cd431b688.
  Full local checks pass; compiled cast40/40, SFmap17/17, intro5/5 and
  creature255 controls match. Production web BPS decoder reproduces exact target.
- Before-starter native map capture has party0, starter flag0x860 false and
  Guide flag0x861 false. No debug unlock, new item or progression flag is used.
  Park/Outer Sunset captions, native close/return and walking pass. Complete
  sixteen-hub geographic/campaign map and human interface approval stay open.
- Existing Garry uses numeric48 throughout; no cached-ID migration is needed.
  Independent compiled239-entry pointer-table comparison changes ONLY slot48,
  Gentleman→SFGarryTan. All previous eight original2304-byte sprite resources
  remain byte-exact. South Park palette first28 bytes and other two cast palettes
  remain exact; only previously unused14/15 receive new cream/gray colors.
  Proofgarry-field-v65-plan/compiled-isolation-proof.json.
- Genuine olderC5 native Continue displays Garry without leaving the map.
  Ordinary Save createsC6 SHA78d6fe1996c1d896e465b3e16b75b844e4061f1a536a86cc5723788aa61115b3;
  read-only Flash auditor passes all declared domains/counter/stat checks.
  ColdC6 reload preserves ALL15752 SaveBlock1 bytes, all3884 SaveBlock2 bytes
  except actual clock seconds/VBlanks0x11/0x12, and the exact Flash battery.
  save-proof.json preserves this limited claim; this adds no cross-platform
  round trip or distinct campaign checkpoint to the fifty-checkpoint gate.
- Actual native dialogue turns Garry west; Chromium normal X interaction shows
  the same original sprite/dialogue. Existing script content is unchanged.
  Genuine older clinic save cold-resumes with Justine/Patrick visible using
  the revised shared palette; their packed resources/visible colors stay exact.
  Garry likeness, nine-pose art and movement quality remain human-unreviewed.
- Chromium JOURNAL ShiftRight opens native SF MAP, B returns eight-row menu
  with JOURNAL selected/SAVE row4, B returns field and X talks to Garry.
  Ten-second map smoke reports597 executed/video frames,1200 visible ticks,
  zero frame debt/mismatch, zero audio underruns/dropped source frames and
  final audio acknowledgment. Report29b03e7924af4a9ca8f2c35c5ee3842e;
  this does not pass guest-update, physical-input, full-duration or device gates.
  Owned QA tab/emulator/audio/server18789 were stopped after capture.
- Opening/closing native map changes encryption keys as the inherited engine
  relocates save blocks. Initial raw comparison (382 SaveBlock1/seven SaveBlock2
  byte differences) is retained, not called byte-exact. Alignment independently
  review confirms ALL15752 plaintext SaveBlock1 bytes exact after decrypting
  ONLY native encrypted fields with EACH capture own key. SaveBlock2 changes
  solely key representation/berry powder encryption and five VBlank ticks.
  Party/storage/Flash exact; seven live Dylan bytes and RNG differ as native
  field return consumes Random and resumes existing wandering. Whole RAM/future
  trajectories are NOT called exact. Root independently reproduces plaintext
  proof; raw differences are retained in city-map-v65-readonly.
- Actual Map→B menu→B field→ordinarySave→coldContinue createsC6 SHA
  486b917d8666bbcde95e8a3a2194aa05f2b0a07f5f9de6928b930e650e94e62b.
  All audited gameplay domains preserve C5 values; counter/saveStat each+1.
  ColdContinue preserves ALL15752 plaintext SaveBlock1 bytes and exact Flash;
  SaveBlock2 differs only clock seconds/VBlanks and key representation after
  exact berryPowder decryption. Raw RAM encrypted bytes are NOT identical.
  save-proof.json records both actual keys and every residual offset.
- First attempted post-map Save route assumed cursor0 and opened Bag instead
  (C5 unchanged); failed evidence retained. Corrected route respects retained
  JOURNAL cursor6 and chooses SAVE4 via two Up presses. Initial raw post-map
  cold-reload assertion also failed on legitimate encryption differences;
  field-by-field plaintext comparison passes without blanket byte exclusions.
- Sites56 sourceaa5a3d1429b70591aed2198fd0b4593259d4206c; saved version
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_2ea24b021660819198a0d21354e8702d.
  Deploymentappgdep_6ad006b76fd481918ed0a277a6a373f5 succeeded22:48:31UTC.
  Archive229df1db6a67152d525be02f0ad4bbfacb6523c5a920b400bf2c57bc763db021
  passes88-file audit with no commercial cartridge, private save, fixture, ELF,
  movie, ZIP or AppleDouble. Only approved original SFMM homebrew is included.
- Both canonical anonymous live resources match local bytes; receiptSHA
  01bc017705c6a120fec5e0bb6d11abb669119eda147f5611c7b6a17e6c1c0182.
  Public loader screenshotpublic-v65-loader-visible.png; no public ROM/save
  import/account changes. Hosting and15 runtime files unchanged, audience public.
- Goal active through October15,18:00 Pacific. Human approvals0/11, music2/4
  last ratedv40; revisedv44 pending. Full campaign/performance/mechanics/save
  gates remain open. No GitHub Actions, DB migration, PR merge or new monitor.
  Alignment's finite read-only acceptance task finished22:50UTC; followup
  twenty-minute first-slice priority review requested. Next exchange by23:20UTC.
  Root owns all implementation/build/publication.


v66 first-slice density work started — October14,22:55UTC:

- Public remainsv65/Site56. Source-only whole-map preview shows an empty paved
  western stretch between the main street and oval garden. Root plans two
  attached3×4 coral/butter frontages at11,13 and14,13, using existing original
  tiles/palettes. Exactly24 previously paved cells change; no new graphics or
  VRAM use. Two clear sidewalk rows above and one below remain, with both side
  routes connected. All service/Muni/discovery/NPC/grass anchors remain fixed.
- Acceptance: all existing destination approaches remain reachable, all24
  building cells block walking and match visual depth, prior map bytes outside
  the24 cells stay exact, secondary graphics/palettes/attributes/door reservations
  stay exact, native/browser traversal is observed and an ordinary v65 save on
  a newly occupied tile resumes safely without lost progress. This is first-slice
  density work, not new campaign content, a usable interior, or art approval.
- Private plan/current/candidate preview in park-density-v66-plan. Alignment
  is reviewing this first-slice priority independently, with a finite20minute
  task ending by23:10UTC. Source edits/build/recovery checks remain pending.


v66 native density candidate acceptance — October14,23:00UTC:

- Draft targetb2b5e135f52c711d626640a9ab54cd127f98b3d05e42f35ff1de29d578230bda
  changes EXACTLY48bytes fromv65, the24 reviewed layout words. Every other ROM
  byte stays exact: graphics, palettes, attributes, engine, NPC/event tables,
  scripts, encounters and door VRAM. Existing497/504 unique8px tiles unchanged.
- Original two-house street wall occupies11..16,y13..16. Both side approaches
  and two upper sidewalk rows remain clear; native traversal goes round the east
  side to16,17, and an Up attempt stays blocked in front of the butter house.
  Rooftop Down attempt is blocked too. All existing service/discovery approaches
  pass reachability; full local checks pass. Two focused behavior checks retain
  blocked footprints, clear approaches, native bindings and no anchor overlap.
- Native ordinaryv65 C6 Save genuinely walked to13,14 on the old open pavement.
  v66 coldContinue relocates it to nearest safe sidewalk13,12 via existing resolver.
  Plaintext proof verifies every saved byte except EXACT warp coordinates and
  native template reconstruction:1536-byte array equals the three current ROM
  records followed by61zero records, matching LoadObjEventTemplatesFromHeader.
  Keys/clock separately classified. Party, storage, flags, vars, items, money and
  non-save stats remain exact; active NPC trajectories/RNG are not called exact.
- Ordinary Save after recovery createsC7 SHA
  aab84ae8fcdbc31d27b77739f1e0ea11050094daed52eeb41cd7b859eabd3664.
  Declared gameplay-domain audit changes ONLY location/warps; counter/saveStat
  each6→7. ColdC7 Continue keeps exact Flash and visibly resumes safe sidewalk.
  Proofs underpark-frontage-v66-occupied-cold/recovered-save/recovered-reload.
  Native save recovery is not a new cross-platform or full campaign checkpoint.
- Browser route/normal release/publication pending; public remainsv65/Site56.
  Alignment accepted the empty western frontage gap and recommends one purposeful
  usable room after the density checkpoint. Assigned finite60minute implementation
  owns ONLY new seed-room source/art-helper/tests; root owns existing Park sources,
  door/warp integration, builds, commits and publication. Planned butter entrance
  is RIGHTMOST16,16 with apron16,17; no third building or Park raster allocation.
  First-slice scope remains locked; no claim of map-art/user parity approval.


v66 public western frontage — October14,23:03UTC:

- Native sourceb761eb3 normal build reproduces drafttarget
  b2b5e135f52c711d626640a9ab54cd127f98b3d05e42f35ff1de29d578230bda.
  BPS1024185bytes SHA65a469be8161b192abfc836ce99c1029972177570b173beab02d0dbe2cb9e50f.
  Native48-byte isolation/recovery/collision proofs above pass; original
  creature255/cast40/intro5/map17 compiled gates and local checks pass.
- Actual Chromium controller route24/24 rows completes around the new street
  wall, with final Up blocked outside the butter front. Screenshot
  park-frontage-v66-browser-blocked.png shows the observed scene. Manual scoped
  measurement lasted43.493seconds (NOT the180seconds on the route button).
  Report169062dc424343afbaa372b10d79100a:2598 executed/video frames,5219 visible
  ticks, zero debt/mismatch/dropped source frames/underruns/warmup and final
  audio acknowledgment. Controller schedule latenessmax3.393ms is not guest
  key consumption/physical response proof. Owned tab/audio/server18790 stopped.
- Sites57 sourcead385f54b7d08cd272847a16b046c77dd0f4e1b5, saved
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_cca262024168819183519176da233480.
  Deploymentappgdep_6ad009c34b1c819190ae7846f8faa1db succeeded23:01:32UTC.
  Archivec2a3699db26c65560a0a80b4939ec6fcaec32e5b0c42fd58c6cfba30c19ea4cf
  passes88-file audit: no commercial ROM/private saves/fixture/ELF/movie/ZIP/
  AppleDouble; approved original SFMM homebrew unchanged. All15 runtime files
  and hosting configuration exact; public audience/auth/storage retained.
- Both anonymous canonical live resources match local bytes; receiptSHA
  9478f55c9a2a0b4ebadf4d388a307d9f1351ecb0f704802a50448044ab83217a.
  Production web BPS decoder reproduces target. Public loader screenshot
  public-v66-loader-visible.png; no ROM/save imported publicly.
- This improves one empty stretch using original existing facade art; it does
  not claim new interiors, architectural art variety approval or complete SF
  world design. Human approvals0/11 and all remaining gates remain open.
  Root continues integration preparation for alignment's bounded seed room;
  next exchange by23:25UTC. User stop October15,18:00 Pacific unchanged.
  No GitHub workflow run, DB migration, PR merge or new monitor.


v67 optional seed room integration started — October14,23:07UTC:

- Public remainsv66/Site57. Alignment owns only new seed-room JSON/script and
  focused tests; root owns integration, native/browser checks and publication.
  Unmanned8×8 community room reuses original apartment tiles and Ocean Commute
  music, with coherent whole furniture groups, no bed, no inherited room graphics.
- New entry16,16 in the butter frontage connects to OldaleTown_House1(2,0),
  with exit/arrival warp3,7 facing north and clear inward aisle3,6.
  Dedicated clone metatile660 preserves original
  butter door pixels/palette without making every reused butter facade enterable.
  Functional candidate uses native non-animated door behavior0x60; custom matching
  door animation is explicitly unfinished and cannot be counted as parity.
- Two environmental interactions refer to existing Roon sensor/window discovery
  and held-berry care. No rewards, new flags, inventory changes or real-person
  NPC invented for this room. Main quest/badge stays independent of entry/reading.
- Acceptance: native/browser walk-in/read/return, all branch text fits and matches
  existing quest states, original art/music bindings, six authored map parents,
  Journal/map location, old Save compatibility and native Save/coldContinue in
  room. All23 other frontage cells stay blocked; original butter doors stay
  blocked. Room entry is an intentional doorway, never free walking under walls.
  Human story/art/animation approval and complete sixteen-hub campaign stay open.


v67 integration build repair — October14,23:13UTC:

- First native build stopped before producing a BPS: the Sunset resource guard
  assumed every authored map's layout name equals engine_map+_Layout. Native
  OldaleTown_House1 actually references shared LAYOUT_HOUSE1. Root now resolves
  each map's actual metadata layout ID, matching the existing map installer,
  while retaining the check rejecting another active SF user of Petalburg art.
  No guard was removed. First full local suite passed; native rebuild pending.
- Room JSON/script/test handoff is frozen with all three peer hashes verified.
  Root integration-focused Park/Journal/six-parent tests pass. Root owns all
  further source/build/publication; alignment's15minute read-only integration
  review ends by23:27UTC. Next check no later23:40UTC. Public staysv66/Site57.

- Alignment finished read-only integration review23:13UTC: no blocker beyond
  correcting the proposed arrival wording. Native non-door arrival remains at
  room warp3,7 facing north; the clear3,6 aisle needs an inward step. Returning
  to exterior0x60 door automatically steps16,16→16,17. Source/anchor/read-only
  story review passes; root runtime checks remain pending. Peer task stopped.


v67 source/native first-entry checkpoint — October14,23:17UTC:

- Corrected drafttarget96d5b50698d5b91e36dbcd606404694312f28ec7e4c1630c24a0b0a5a223c662
  builds with compiled creature255/cast40/intro5/map17 controls passing. Full
  local suite passes after the actual-layout-ID repair, including the seven
  source room checks and existing Park/Journal/six-parent protections.
- Genuine ordinaryv66 C7 Save at16,17 (SHA
  84ebbf0dafbb59c8a7352ae1e4524310d99953ee7ec06fda81e8263dec30cb19)
  coldContinues with the new door collision, without a map exit to refresh it.
  Normal Up enters room3,7(2,0); inward step reaches3,6. Actual native field and
  care notes display readable first pages, using the existing prototype-recovered
  and held-berry branches. Native return, Save/coldContinue and complete read-only
  dialog comparison are being finalized. Browser/publication remain pending.
- All original148 Park records/296 attribute bytes/512 palette bytes independently
  match immutable compiledv66; dedicated record148 clones original133 exactly,
  only newattribute0x1060. Unique8px graphic count497 remains unchanged.
  Native room visual uses coherent original wood/walls/furniture; human review
  remains pending. Source checkpoint does not claim parity or final acceptance.


v67 native room acceptance and source checks — October14,23:23UTC:

- Source5088a04 is pushed. New202-line focused suite checks connected floor/one
  exit, full original furniture cells with matching collision, reciprocal warp,
  original music/parent, all existing-state text branches and finite pages with
  zero state-writing commands. Wired into the existing manual local check script.
  Complete local suite passes; no GitHub Actions requested.
- Native entry from genuine olderC7 at16,17 reaches3,7 facing north; one inward
  step reaches3,6. Correct held-Down exit returns via exterior door to16,17.
  First16-frame exit attempt only stepped onto south-arrow3,7; trace retained,
  not called a return. Holding Down40frames completes the normal native exit.
- C7→roomSaveC8 SHA98efab1570a2c32a5e13cc097af86594ee1f6e4e7804ab4c3f74c12dfec8a30c
  changes only audited location/warps, native VAR402A1→2/VAR402B3→0 and step
  stat385→387; Save counter/stat7→8. Remaining declared gameplay domains exact.
  ColdC8 resumes3,6 with exact Flash. Actual coldContinue→SaveC9 SHA
  d5e6160758d470334fdb4104c118cf8bd66dddc0a2283d177e5bcb324481bd61
  passes stationary semantic audit with counter/stat8→9 and no domain changes.
- Full recovered-prototype field-note open/three-page/close cycle compared with
  equal1240-frame idle from the same checkpoint preserves ALL15752 SaveBlock1,
  ALL3884 SaveBlock2, global600-byte party,33744-byte storage and128KiB Flash
  EXACTLY. No normalization/excluded bytes. state-proof.json retains scopedclaim.
  This is one actual runtime branch; seven source tests cover remaining branches.
- Native Journal names SEED ROOM / SOUTH PARK and keeps the existing chapter
  objective; SELECT SF MAP shows South Park player marker/caption. Roomcompiled
 128layout bytes and8×8header/originalHome tileset binding/records/attributes/
  palettes and native Ocean Commute songID independently match expected sources.
  Private compiled-room-proof.json records checks; runtime art approval pending.
- Private39.982second native visit-and-return clip is captured/encoded; original
  gameplay/audio, one SF track only, not a matched Emerald reference or approval.
  Browser route/smoke/publication acceptance is being finalized. Publicv66/Site57
  stays live; no new fullcampaign/crossplatform/device/performance credits.


v67 public seed-room release — October14,23:29UTC:

- Native normal source35e97a1 reproduces target
  96d5b50698d5b91e36dbcd606404694312f28ec7e4c1630c24a0b0a5a223c662.
  BPS1023731bytes SHAa140ec31e8bfe44ffb80042efb67d554a3dbf9bb1784e12e802e668a5de0dab5.
  Local suite and compiled creature255/cast40/intro5/map17 checks pass; source
  5088a04 (243lines) and companion35e97a1 (236lines) are pushed with skip-ci.
- Browser route18/18 completes notes and automatic exterior return; actual
  manual ArrowUp (turn, then step) re-enters the room and X displays recovered
  prototype field notes. Screenshotseed-room-v67-browser-notes.png proves the
  observed browser scene; return screenshot separately retained.
  Scoped manual measurement55.436seconds,3311 executed/video frames,6652 visible
  ticks, zero debt/mismatch/audio drops/underruns/warmup, final audio ACK.
  Report4c73b1d967824683976bb00dea3a5de5; maxcontrollerlateness2.686ms is not
  physical/guest-consumption proof. Owned tab/emulator/audio/server18791 stopped.
- Private39.982second2388-frame native visit/notes/return clipreview.mp4 SHA
  c53e110efff253b9efa0aabd8d1a46adeeec830353aa5c14fcf43b831604e37b
  is human-unreviewed and contains one SF track. Metadata pins actual source
  5088a04/target96d5b506/core/controller; normal source35e97a1 reproduces sameROM.
  It is not a paired Emerald comparison or music listening acceptance.
- Sites58 source4a13dc1b849cc9626c248826bd7d1825213fd7ef; savedversion
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_f5312c7267d8819190e2740d6aaa508c.
  Deploymentappgdep_6ad00fd907108191a5324f8685406880 succeeded23:27:30UTC.
  Archive903d551111da5d570c5c0e9cccb726e4838799afedc6b9a22f088be6e29aa1e2
  passes88-file audit, with no commercial ROM/private saves/fixture/ELF/movie/
  ZIP/AppleDouble. Approved original SFMM homebrew and15 runtime files unchanged;
  hosting/audience/public auth/storage retained. Production BPSdecoder matchesROM.
- Both anonymous canonical live resources match local bytes; receiptSHA
  aadd5bbe6231044fe8f93190ccf1f4f9ba68f31cdf1ce3910ad698dd6260ff74.
  Public loader screenshotpublic-v67-loader-visible.png; no public ROM/save
  import/account mutation. Unrelated userPDF remains untouched/untracked.
- Six authored maps remain two hubs plus four interiors, not six neighborhoods.
  Eight text branches and read-only environmental discovery add first-slice
  exploration; no gift, new quest flag or score approval. Door currently uses
  native non-animated fade; matching opening frames/arrival-apron polish remain
  concrete next gaps. Full campaign and all human/performance/mechanics/device/
  save gates remain open (0/11 approved; last clinicmusic2/4 atv40).
  Goal remains active until October15,18:00 Pacific. Next alignment exchange
  by23:40UTC; no new monitor, GitHub workflow, DB migration or PR merge.


v68 centered animated door plan — October14,23:32UTC:

- Publicv67/Site58 remains live. A read-only native geometry review identifies
  the existing tiny inset panel at cardx0..4, left of the player's tile center.
  Root is preparing original centered closed/half/open door frames for ONLY
  the seed-room entry, with top8 native window rows fixed. Portal centerx8
  matches the approach tile, improving the doorway affordance and transition.
- Use native size1 16×32 animation/unchanged timing/palette11. Newupper661 and
  existinglower660 get the newclosedcard; upper staysblocked, lower changes
  from0x60 toanimated0x69 withsamewarp16,16. Original other facade IDs stay fixed.
  Preservingtop8rows bounds newgraphics to≤6tiles,497+6≤503 within504; validate
  actual dedupcount beforebuild. Camera layerexception mustinclude661/660.
- Native size2 was audited and rejected: residenttile1008 is occupied, while
  size2overwrites1008..1023 and needs different anchor/close/static-open fixes.
  No broader door-engine/VRAM change is planned. Generation/conversion/native
  entry/exit/collision/cache/Save/browser checks remain pending. Root ownsart and
  implementation; alignment's finite25minute read-only geometry audit is active
  and ends by23:55UTC. Next exchange by00:00UTC. No score/complete claim.


v68 original door-art checkpoint — October14,23:45UTC:

- Built-in imagegen produced original closed/half/open source; selected source
  is saved atassets/tiles/seed-room-door/source-v1.png with exactprompt.md.
  Native serializer uses existing palette11, pins original top8window rows,
  and holds all newclosed-card pixels outside aperturex4..11/y12..25 fixed.
  Opaque portal stages progressively darken; no transparent opening exposes
  background ground. Three256-byte stages serialize exactly to768bytes.
- Six focused checks independently decode native4bpp tile order and reject
  moved window, jamb jitter, alpha holes or identical stages. Native candidate
  and whole-house source visualization inspected; no runtime/art approval claim.
  Newcenter matches nativeavatar8 withinhalfapixel; boundedproof≤6newtiles holds.
  Root ownsworld/animation/camera integration next. Alignment owns a separate
  bounded35minute compiled-audit helper/test/explicitELFallowlist task, with
  no builds/captures/commits. Next exchange by00:15UTC; public remainsv67/Site58.


v68 centered native animation source checkpoint — October15,00:01UTC:

- Combined drafttargete7fa86a10acc213c6b3d7e2722799cc3ccda74b20af6d12e4f39327b55dd04d9
  passes creature255/cast40/intro5/map17 and NEW seed-door11/11 compiled checks.
  Immutable v67 negative control fails eight checks (3/11 match), so the gate
  distinguishes old artwork/behavior; BPS creation now stops on any mismatch.
  Full local suite passes including six art and eight compiled-audit cases.
- Actual503 resident tiles: original497tile bytes,148metatile records,148attribute
  records and all512palette bytes are EXACT against immutablev67. Last resident
  global1014 leaves1015 free and native1016..1023 animation reservation intact.
  Only newentry upper661/lower660 cards/attributes and paved16,17/17,17 change
  field presentation; all existing anchors, shared butter645 and otherdoors fixed.
- GenuineoldC7 coldContinue preserves16,17 and displays centereddoor. Matched
  native2300frame38.508second v67/v68 visits are captured. Entryphases119/124/129
  are entire-RGB exact (no closed-frame snap); half134changes44pixels and full139
  changes74pixels confined to opening. Native closeup shows actor passing behind
  opening before warp and door closing afterward. Asset window/jamb/threshold
  remain fixed. Actualreturn scene differs173pixels inside the player's16×32
  standing-pose box only; every other visible pixel is exact after fullvisit.
- Compiled-audit handoff hashes independently verified; source importtiming
  fix accepted and eight tests pass. Root owns nativeSave/browser/release next;
  alignment now performs finite15minute technical-only visualreview of phases.
  Next exchange by00:30UTC. Publicv67/Site58 stays live; human approvals0/11.
  Custom door art/animation approval and full campaign/device/performance/save
  gates remain open. No GitHub workflow, DB migration or PR merge.


v68 save and independent technical review — October15,00:08UTC:

- Controller-only v68 full visit returns to SouthPark16,17; ordinarySaveC7→C8
  increments savecounter/stat once. Only declared changes are native location/
  warp history, friendshipstep402A1→7, poisonstep402B3→1 and stepstat385→391.
  All other audited persistent domains preserve values. C8 SHA
  d49c9a2993243ae17d091c40ed5760ec6aaca52883ff45e35ff8663005766b40.
- Genuinev67 indoorC9 coldContinues in v68 at room3,6 with Flash EXACT, then
  ordinarySaveC10 passes every stationary semantic check, no changed domains.
  C10 SHA5860620541864a983cd633c4a39ea3fc08a83dcb972580d100ea40b3d8548a9c.
  Private seed-door-v68-plan/save-acceptance.json retains actual comparisons.
  These are persistent-domain checks, not opaque-RAM/cross-platform/newcampaign
  checkpoint credit. Eight independent compiled-fixture tests join routine checks.
- Alignment independently inspected all2300RGBAframes/metadata and matched
  phase pixel counts, stable window/wall/sidewalk before movement, camera and
  closed-door endpoint. No actionable issue in that boundedtechnicalsample.
  Animatedentry differs about20frames from oldinstantdoor: clips cannot imply
  correspondingworldpositions after warp. Humanartapproval remains pending.
  Root proceeds to actual privatebrowserroute, normalbuild and publicpatch.


v68 public centered-door release — October15,00:10UTC:

- Source8d923af native integration/gate and a5e28ff companion checks are pushed
  with skip-ci. Normal sourcea5e28ff reproduces actualdrafttarget
  e7fa86a10acc213c6b3d7e2722799cc3ccda74b20af6d12e4f39327b55dd04d9.
  BPS1023389bytes SHA9c3a40cd94af219e44b2e84b8bbc5ac51eae118f5b023d7db6d77c37ac0b838d.
  Creature255/cast40/intro5/map17/seed-door11 compiled checks all pass.
- Native returnC8 coldContinue independently retains SouthPark16,17 and exact
  Flash; privatecold-return-proof.json records scope. OldindoorC9→C10 ordinary
  save semantic acceptance remains valid. No new campaign checkpoint credit.
- Actual Chrome suppliedroute23/23rows completes38.508seconds; observed42.8445s,
  2559executed/video frames,5141visible ticks, zero debt/mismatch/audio drops/
  underruns/warmup, finalACK. Report122056f02847426d811d0e703e4460bc.
  Manual ordinarykeyboard re-entry works; exterior-return and interior-entry
  screenshots retained. Maxreplaylateness4.234375ms is not guest/physicalinput
  proof. Owned tab/emulator/audio/server18792 are stopped. Full device/deadline/
  listening/long-duration performance gates stay open.
- Native SFv67/SFv68 before-after clip2300frames38.508seconds retains bothaudio
  tracks and metadata; comparison.mp4 SHA
  ac211b83035f02081f696794d50f61baf0a012ad57f0679c734f52999866febe.
  This is SF versus previousSF, NOT an Emerald comparison or approval. Native
  animation changes transition duration; later scenes are not position-aligned.
- Site59 source8023fdaea18b0d0efa4750b13ab2b70c15c195f6; savedversion
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_27fc3ef71df481919711dbfd0c1d97f2.
  Deploymentappgdep_6ad0199a61c481919844006195dcd055 succeeded00:09:07UTC.
  Archivef7bce16064b5e6c1472375a2fa5ee13e58f5f35709a40692490f5391c128e40a
  passes88file audit; no commercial ROM/private save/ELF/movie/AppleDouble.
  ApprovedSFMMprototype/15runtimefiles/hosting/auth/storage/publicaudience exact.
  Production BPS decoder reproduces candidate. Both canonical live resources
  byte-match local; receipthash91fca7737fbdac41ec7d5006e16081722b41c6121fd72b34caabef37813f61f2.
  Publicloader screenshotpublic-v68-loader-visible.png retained; no public
  ROM/save import or accountmutation. OwnIAB18closed; unrelatedPDF untouched.
- Goal staysACTIVE untilOctober15,18:00Pacific; humanapproval0/11, musiclast2/4
  atv40, sixmaps/twohubs, completecampaign and remainingacceptance gatesOPEN.
  Alignment next performs finite20minute read-only density/collision source
  review, reportingby00:30UTC; next exchangeby00:40UTC. No new monitor, GitHub
  workflow, DB migration or PR merge. Root continues first-slice polish.


v69 first-slice source checkpoint — October15,00:16UTC:

- Alignment's density review identified isolated lower-west house frontage.
  Accepted source adds one adjacent existing butter house at14..16,20..23 and
  moves tree16,20→19,20. Exact13mapwords change; original503resident tiles,
  150records,150attributes and512palette bytes all remain exact. Eleven newly
  occupied house walkable cells plus relocatedtree make12newblocked positions.
  All NPC/warp/sign anchors, six encountergrass cells and four bench approaches
  remain reachable; no extra route disconnection or new house warp.
- Source handoff hashes independently match, source is frozen. Full local suite
  passes including12park-art/6flip/14map/7room/6door-art/8compiled-door tests and
  native map-resume harness. These tests establish source geometry/resources;
  genuine old-position Save/Continue and actual rendering remain separate gates.
- Original Dylan nine-pose candidate generated using built-in imagegen, source
  stored atassets/characters/south-park-cast/dylan-field/source.png and prompt.md;
  official Figma newsroom photo is private reference only. Native436pixel edits
  pin directional heads, neutralgray tee and creamsneakers. Sharedpalette and all
  nine prior native cast graphics remain exact. Dylan exclusively reuses MAN_3
  slot, retaining eventid2/26,18/wandering ranges1/script/dialogue. Ten original
  field cast candidates now compile; likeness/art/animation approval pending.
- Draft275444c30a17cb877f87778fa7cf61e06f7b278d1f278833789f3078b2944a85
  passes compiledcreature255/cast44/intro5/map17/door11. BPS1024477bytes remains
  private; public staysv68/Site59. Native controller-only ordinary oldv68C9s are
  being recorded at each12newblocked positions before v69 coldContinue/recovery.
  No battery/RAM edits; all save/campaign/quality claims remain scoped.
- Alignment implemented only four owned map/test files, then returned ownership;
  root handles cast/build/native/browser/publication. Next exchangeby00:40UTC.
  GoalACTIVE throughOctober15,18Pacific; humanapprovals0/11; remainingfull gatesOPEN.


v69 public neighbors/Dylan release — October15,00:24UTC:

- Normal source5ca3b236b97ebe3501e6cbc3bf18b47ed2535d4f reproduces draft
  275444c30a17cb877f87778fa7cf61e06f7b278d1f278833789f3078b2944a85.
  BPS1024477bytes SHA985f18dcb25ac2e7cd173f015ca76b2dad29b0f043f064c68ed0e5b2a43bf45c.
  Actual compiled16prior park/cast/palette resources are exact; only13parkmap
  words change. Compiled-preservation proofSHA
  26f898af8622635db5c87d65337b0241c97c25af36f8bd9ffc0637fb950d93be.
- Twelve genuine oldv68C9 ordinary saves, one per newlyblocked position, all
  coldContinue in v69 to a minimum-distance safe cell, with originalFlash exact.
  Each ordinaryC10 resave changes ONLY location/warp history among declared
  gameplay domains. Actual counter/saveStat increments9→10. ReceiptSHA
  4009fddd4a5f6137421d14090c0336a00494ba2db77dc2eb6dbfbf1c14f290c3.
  Independent recoveredC10 coldreload retains14,24 and exactFlashSHA
  ec17597cd394aa7fd79a6ae0588ecf79624ec8ba495920baacaaefaf86534fd9.
  These are footprint recovery cases, not12newcampaigncheckpoint credits.
- Actual native wall-push prefixes hold14/15/16,24 across three front cells,
  side17,20 and roof14,19. ReceiptSHA
  9ed9721755055b058b7a3a0ff0a0ea3006aa4f78b09dbcd3040724cae81c6cbc.
  Full1848frame30.940521s native review shows frontage joins, collision route
  and Dylan wandering; clipSHAeb5959911c3b5e188eaf610e5a9175d88b0bd0224bd0882a34c2c1f559f25d80.
  Finalplayer24,17; Dylanlocal2/nativegfx33 at27,17. Separate actual native
  interaction opens existing DYLAN FIELD dialogue. No dialogue/state schema change.
- Alignment technical samples confirm continuous facade/ground/threshold joins,
  visible hero head/feet on front/side/roof approaches and gray-shirt Dylan with
  separate legs. This was sampled technical review, not continuous video/human
  art approval or formal all-nine-pose runtime sweep. No approval score inferred.
- Actual Chrome route27/27rows completes30.9405seconds; scoped observation
  53.8073s,3214executed/video frames,6457visible ticks, zero debt/mismatch/audio
  drop/underrun/warmup, finalACK. Reportd59a9fcf8b334586b2e0001d2b38aca3.
  Replaylateness2.763ms does not prove guest/physicalinput. Owned tab/core/audio/
  finite1200s server18793 are stopped; full performance/listening/devices stayOPEN.
- Site60 sourcebaf463c6132dad495ab79e49e5828ed8fef83d9d; savedversion
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_aa16728f0d008191ae1e2f8eac981c45.
  Deploymentappgdep_6ad01caf817081919a67c9d583d7adb2 succeeded00:22:16UTC.
  Archive9ed3d42208cb6eec07e10b54ebb36dbca58a4455ef2401266e0962daf867e5c5
  passes88file/no-commercialROM/privateSave/ELF/movie/AppleDouble audit.
  ApprovedSFMMprototype/15runtimefiles/hosting/auth/storage/publicaudience exact.
  ProductionBPSdecoder reproduces target. Anonymous canonicalpatch+manifest exact;
  live receipthashfaf8cd1f5df7e5e2f4d713d76adb9afd1d039197af0564a76281c592f15f19dc.
  Publicloader screenshotpublic-v69-loader-visible.png retained; no publicROM/
  Save import or accountmutation. OwnIAB19closed; unrelatedPDF untouched.
- GoalACTIVE toOctober15,18Pacific; humanapproval0/11; fullcampaign/remaining
  mechanics/performance/devices/50resumecheckpoints/humanclip gatesOPEN.
  Six authoredmaps stilltwohubs; ten original fieldpeople with Jonathan still
  generic. Alignment finite20minute read-only slot/palette/publicappearance audit
  for Jonathan in both hubs ends00:45UTC; next exchangeby00:45UTC. Root continues
  first-slice polish. No new monitor/GitHubworkflow/DBmigration/PRmerge.


v70 two-map Jonathan source checkpoint — October15,00:31UTC:

- Alignment's finite slot/palette audit is complete; root implemented original
  Jonathan art from one built-in-generated atlas, copied byte-identically to
  sunset-cast/jonathan-sunset and south-park-cast/jonathan-park. Exact prompts
  and public-reference notes are tracked. Ownwebsite→GitHub/X identity chain
  verified; public avatar is private QA reference, not game art or endorsement.
- ExistingSunsetMAN5 slot66 and previously unclaimedParkMAN4 slot65 become unique
  map aliases. Only two event graphics fields change: Sunsetlocal8/29,22 and
  Parklocal1/7,25. All scripts, movement, coordinates, warps, layouts and palettes
  remain fixed. Existing generated native cache refresh handles oldPark66→65;
  no new rendering hook, group, schema, reward or table expansion.
- Separate indexed cleanup467Sunset/257Park corrections pins directional heads
  and cream shirt/hood/sneakers. Sunset removes orange skin quantization using
  existingcream15; Park retains skin and uses existingcream14. Every one of ten
  prior native cast graphics and three sharedpalettes stays EXACT (13resource
  aggregateaea5411ce0e5298cb9b7c36346c8337c42e353b854437e553abac1a5f3fe23c1).
  Fifteen cast tests plus full local suite pass; humanartapproval stays pending.
- Draftfc3fbf94ad2440fccc4d35276cb4319181508c619ea0d042e1ba59e66c109f4c
  passes compiledcreature255/cast52/intro5/map17/door11; BPS1026706bytes private.
  Genuinev69 ordinaryParkC11 at7,24 and SunsetC12 at28,22 recorded via walking,
  normal MuniReturn and native Save. No RAM/battery editing. Root is checking
  both actual old-save Continue/liveactor/ordinaryresave before browser/publication.
- Eleven named fieldpeople now have twelve map-specific candidates; this is
  field integration, not all trainer portraits or full art acceptance. Public
  remainsv69/Site60, fullcampaign and acceptancegatesOPEN, humanapprovals0/11.
  GoalACTIVE throughOctober15,18Pacific; next alignment exchangeby00:45UTC.


v70 public original Muni operator release — October15,00:39UTC:

- Normal source3111cd09b2a37388d8bd954295d608d87d86c7a2 reproduces draft
  fc3fbf94ad2440fccc4d35276cb4319181508c619ea0d042e1ba59e66c109f4c.
  BPS1026706bytes SHA4b4ec15aa38b9382f88b4e80f55b9d9c2d09c64cbfc68d8befedce72bd417c57.
  Full local suite and compiled255/52/5/17/11 pass. Actual13prior native cast/
  palette resources and Park blockdata exact; static pointertable956bytes239slots.
  Compiled-preservation proofSHA279f4299fcb1b71d3c4838361f978441b92f6a6a3517b215f0337655c536480f.
- Genuineoldv69ParkC11 and SunsetC12 coldContinue in v70 at unchangedpositions
  7,24 and28,22 with Flash exact. Currentlive Jonathan is local1/gfx65 in Park,
  local8/gfx66 in Sunset. Ordinaryresaves increment12/13 and preserve EVERY
  declared gameplay domain; two-map proofSHA
  acae74a2076e8890b780cdc6ed9c4556ca8ef3db1def503e8c23aa1fb3740eca.
  Independent coldreloads of those new ordinarysaves retain matching positions,
  live graphics65/66 and entireFlash exact. No opaque-RAM/fullcampaign claim.
- Native3308frame55.384872s full Muni outward/return journey shows both source
  variants, dialogue/YesNo prompts and finalSunset28,22; original Flash unchanged.
  ClipSHA103cc5b7ee35fac27751a0691f0a5d1ea6c1399eb1fc47e4fe65b66a1b7b88a3.
  This is a single SF interaction review, not an Emerald reference/qualityapproval.
- Actual Chrome route23/23 completes55.3849s; scoped89.7317s observation,
  5360executed/video frames,10766visible ticks,0debt/mismatch/audio drop/underrun/
  warmup, finalACK. Report898a080c23074f108cbeb9d265c0a3d3. Replaylateness3.817ms
  does not prove guest/physicalinput. Separate ordinarykeyboard conversation
  advances through allpages/YesNo and visibly arrives in SouthPark with matching
  Jonathan. Screenshotsbrowser-sunset-dialogue/browser-park-arrival retained.
  Owned Chrome tab/audio/core and finite1200s server18794 stopped. Full devices,
  guest deadlines, physical response and listening/long-duration gates remainOPEN.
- Site61 source75382381e59c91383f8046f8440e9b0aefa89bf4; savedversion
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_3c7bb053b3b081919579cf1ae86811d9.
  Deploymentappgdep_6ad020463fa08191bcaca9c2c1a9cbc6 succeeded00:37:34UTC.
  Archive63ce1b66a84230ed76a7429c1f853149e914e74487bc873976aefb1bee4f5294
  passes88file/no-commercialROM/privateSave/ELF/movie/AppleDouble audit.
  ApprovedSFMMprototype/15runtimefiles/hosting/auth/storage/publicaudience exact.
  ProductionBPSdecoder reproduces target. Anonymous canonical livepatch/manifest
  exact; receipthash7729f5e7866c48267434696c9d21307d0df5f85a02614b9bd658da1b3dad6c32.
  Publicloader screenshotpublic-v70-loader-visible.png retained; no publicROM/
  Save import or accountmutation. OwnIAB20closed; unrelatedPDF untouched.
- Eleven named fieldpeople now have twelve map-specific original candidates.
  Originality/integration is not human art/likeness approval or all battleportrait
  completion. Fullscope, remainingmechanics/performance/50resume/campaign gates
  stayOPEN; humanapprovals0/11, lastmusic2/4 atv40. GoalACTIVE toOctober15,18Pacific.
  Alignment completed finite read-only remainingbattleportrait audit: append
  Walden94/Steven95 after existingScott93, no stock slot or battle-rule changes.
  Root will handle original art and native/browser acceptance; next exchange
  by01:00UTC. No new monitor/GitHubworkflow/DBmigration/PRmerge; work continues.


v71 original Cognition portrait source checkpoint — October15,00:53UTC:

- Built-in imagegen produced original Walden and Steven battle figures matching
  their established fictional field costumes. Selectedsource/prompt/native64x64
  frame2048bytes/palette32bytes/conversion/README are tracked under each
  cognition-cast/{person}/battle-portrait-v1. Deliberate independent palettes
  separate green/ivory/skin for Walden and gray/navy/glasses/skin for Steven.
  Original Scott source, frame6b132b9f...da79b and palettef4e2ab2a...cec6 unchanged.
- Producer registry keeps Scottpicture93 and appends Walden94/Steven95. Only
  JOSH320/TOMMY321 picture selectors change; completebattle/encounter/reward
  document normalizes to original canonicale3a8dc08dea3100eb539cff40ef7578d06cf83c892cfa85ead26ca44dbc1bbb1.
  No team/item/move/AI/class/flag/script changes or new battle-engine hooks.
- First actual compile353ff5bd...7c667 correctly failed the new resource gate
  at23/26: the checker/fixture incorrectly assumed packed2byte MonCoords rows.
  Pinned agbcc uses STRUCTURE_SIZE_BOUNDARY32: native rows are4bytes08 01 00 00,
  table96×4=384bytes. SourceC structs and productiontables were correct. Failed
  receipt and original ROM/ELF are preserved; validator/fixture corrected only.
  New checks reject packed192byte tables, either nonzero padding byte and wrong
  semantic coords at each93/94/95. Eleven focused synthetic tests pass.
- Independent re-audit of the SAME actual firstcandidate now passes26/26; old
  v70 negativecontrol fails. Scope is compiled pixels/palettes/descriptors/
  trainer selectors/animation pointers, not humanquality or gameplay acceptance.
  Peer four-file handoff and corrected two-file hashes independently verified.
  Root owns completebuild/checks and actual native/browser battles next.
- Genuine currentv70 prebattle saves recorded by normal play/Save, no flag or
  RAM/battery edits: preWaldenC3 at4,14 SHA
  24133218397436dfad3d82bf4219560c0f1365038c1112b6055f9cf084cb50d0;
  preStevenC4 at4,13 SHAe806a0efec0441cd205c5adee4d52332c700da9018bad64c5abd4845b468624c.
  Earlier older batteries underwent existing native species-content upgrade;
  these actual ordinary v70 saves establish the current revision8 baseline.
  Public remainsv70/Site61; goalACTIVE, humanapproval0/11, all remaininggatesOPEN.


v71 compiled portrait gate checkpoint — October15,00:54UTC:

- Corrected draft reproduces SAME353ff5bd5adb5b52df1d6b7f1b2d68bbb7df9956ab283e4d99ca2e991937c667,
  confirming the repair changed only validation. BPS1026146bytes remains private.
  Compiledcreature255/cast52/intro5/map17/door11/portrait26 all pass. Full local
  suite passes, including11 independent portrait fixtures and4battle limits.
- The bounded ELF reader adds EXACT15 portrait/table/animation/trainer symbols,
  retaining existing resource checks. Audit independently specifies265→93,
  320→94,321→95, exact pixels/palettes/ABI/animation links and96complete front
  table entries. Actual oldv70 fails8/26; actual candidatepasses26/26.
  No stub image or synthetic fixture is counted as native presentation approval.
- Build now preserves a unique portrait receipt and refuses BPS creation on
  failure; release metadata carries scoped26checks/validator+receipt hashes.
  Three source checkpoints separate assets/producer, compiledgate and companion
  synthetic tests. Public staysv70/Site61 until actual native/browser acceptance.
  Root proceeds to both real prebattle old-save Continue and native battles;
  humanapproval0/11 and full goalACTIVE throughOctober15,18Pacific.


v71 companion tests/native entrance checkpoint — October15,00:57UTC:

- Eleven bounded synthetic ROM/ELF cases reject wrong selectors (including
  Scott), pointer/tag/size errors, every truncated front table, packed2byte
  coords, either nonzero nativepadding byte, malformed/stale data, source/PNG
  disagreement and wrong animation chains. Producer registry misuse and all
  generated registrations/header preservation are tested independently.
  Routine local check now runs this suite; all local checks pass.
- Actual current-v70 preWaldenC3 and preStevenC4 coldContinue in v71 then
  ordinaryresaveC4/C5 preserve every declared game domain and increment Save
  exactly once. Native live stages open Walden's green-jacket94 and Steven's
  glasses/gray-shirt95 images, then continue the original battle entrance.
  Two2048frame34.289second common-controller captures are retained for matched
  genuine-Emerald comparison packaging. These are presentation subsets only;
  completebattle returns, actualbrowser and humanreviews are still pending.
- Public staysv70/Site61. No mechanics/team/encounter/reward/classID changes;
  full remaininggatesOPEN and goalACTIVE throughOctober15,18Pacific.

v71 public trainer-portrait checkpoint — October15,01:25UTC:

- Normal sourcee7da69c7a3e0b99d433162c987c788239a0c4260 produces target
  353ff5bd5adb5b52df1d6b7f1b2d68bbb7df9956ab283e4d99ca2e991937c667.
  BPS1026146bytes SHAecae227cb17d352d29ed64526f5eceff8ad8738329f76b44270f5bb55274abbd.
  Worktree-dirty is honestly recorded in the manifest; unrelated PDF and the
  peer-owned untracked turn fixture are excluded from this release checkpoint.
- Original Walden green-jacket and Steven glasses/gray-shirt portraits use
  native IDs94/95; Scott93 remains byte-exact. Built-in image generation used
  our original character sheets, followed by reproducible palette conversion.
  Exact prompts/sources/cleanup recipes live under each cognition-cast person's
  battle-portrait-v1 folder. No commercial image/reference likeness is imported.
  Both inherited trainer class IDs/display classes remain unchanged in v71.
- Independent compiled audit passes26/26, and oldv70 fails8/26. The native agbcc
  MonCoords stride is4 despite two u8 fields; preserved failed receipt identified
  the validator's original2byte assumption. Correcting validation reproduces the
  identical first target353ff5bd; no engine or portrait table change hid the error.
  Eleven bounded companion cases and the full local check pass.
- Genuine v70 preWaldenC3/preStevenC4 ordinary saves coldContinue and stationary
  v71 resave preserve all declared gameplay domains. Separate native branches
  actually approach the trainers, display new portraits, deploy both sides and
  reach the command menu. Both2048frame34.2890625second captures are paired with
  genuine Emerald Calvin introductions using identical controller input/native
  clocks, nearest scaling and two unmodified audio tracks. Human0–4 requests
  remain pending; no rating or approval is inferred.
- Both underleveled battle branches end in actual losses, then return to field,
  heal, ordinarySave and coldContinue. StevenC4→C5 returns to existing last-heal
  SouthPark6,17; WaldenC3→C4 returns to existing last-heal Sunset23,22. These are
  legacy save destinations, not proof of current clinic blackout destination.
  Cold Flash and all600 native party bytes match the ordinary saved result.
  Flags stay exact: Steven remains undefeated, and Walden's earlier defeated
  flag is retained only on the separate preSteven branch. Each uses one Potion;
  money3800→1900 /3500→1750. Walden branch earns a level3→4 bench level before
  losing to Pinepip's Bide. These are not victories or new campaign checkpoints.
- Battle-outcome receipt precisely bounds changed domains: existing location/
  warp history, party, seen-bitfields, native variables, money, one bag item and
  battle/step/loss statistics. Everything else declared remains exact. Private
  receipt: portraits-v71-plan/battle-outcome-proof.json; opaque RAM equality,
  balance and complete campaign-save acceptance are not claimed.
- Chrome actual new portraits are separately visible in ordinary input QA.
  Walden sample180001.1ms:10751 core/video frames,21600 visible ticks; complete
  17row34.289s intro followed by menu idle. Steven complete sample39730.8ms:
  2373 core/video frames, complete17rows. Both report zero frame mismatch/drop,
  warmup/drop/underrun and final audio acknowledgement. Steven earlier21.6245s
  interrupted12/17row receipt is preserved and excluded from complete-route
  claims. Own QA tabs/finite servers were closed. This is not ten-minute mixed
  gameplay, physical response, native update deadlines, Safari/phone or listening
  approval. Private browser screenshots and original timing receipts are retained.
- Site62 succeeded at2026-10-15T01:24:32.271555UTC; source
  be095d2e18a5686e6dc8b7ba3665ad78d00a9555. Savedversion
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_4e9e294c58508191860c382a4916e4f6;
  deploymentappgdep_6ad02b4805f88191b8a879852b50ab48.
  Archivebac9544b75093b7d651d11553124ebc02b9e5bda53957d601908fc751b8e3d27:
  all88files pass; no commercialcartridge/privateSave/ELF/MP4/ZIP/AppleDouble.
  Approved originalSFMM prototype remains. Production browser decoder reproduces
  the target byte-for-byte; all15 runtime files, hosting/auth/storage stay exact.
- Anonymous public manifest/BPS responses match localSHA at01:24:41UTC; receipt
  portraits-v71-live-resources.json SHAc1fc1f7464fb95d2aae5ef5367a6af17afae8a88ea3f11841ccadc485b33b54f.
  Actual visible public loader verified and screenshot retained; no public ROM/
  save upload or account mutation. Root public patch files and versioned release
  are committed together with this spec. GitHubActions stays manual-only.
- GoalACTIVE throughOctober15,18Pacific, humanapprovals0/11, all remaining
  campaign/art/audio/type/catalog/full-turn/performance/save gates OPEN. Next
  work remains first-slice polish plus source-derived full-turn/party-sync proof;
  no campaign expansion is authorized by these technical subset passes.

v72 frontage asset checkpoint — October15,01:30UTC:

- User's density/repetition feedback remains the current first-slice priority.
  Built-in imagegen produced four distinct original building candidates: red
  brick loft, sage Edwardian, sandstone warehouse and a narrow coffee storefront.
  Sources, exact generation prompt, design brief and conversion recipes are
  stored in assets/tiles/south-park-frontage-v1. No commercial source image.
- Alpha-band extraction respects actual card bounds; source cards are not
  perfectly quarter-aligned. Native outputs are48x80 for three facades and32x64
  for the shop, with individual RGB55515-opaque-color palettes and transparent0.
  Conversion records the deliberate final dimensions rather than silently
  claiming the original requested64x80 footprints. Native montage inspected;
  these remain unreviewed candidates without an art approval increase.
- Five portable resource-contract cases pass: distinct native cards/banks,
  stale source/prompt rejection, malformed RGB555 rejection even with an updated
  hash, preview/index disagreement even with updated hashes, and wrong-bank/
  missing-resource rejection. Existing secondary graphics are not changed.
- Root owns forthcoming primary tileset/map integration. Proposed53 blocked
  cells require source routing, compiled pixels/attributes, genuine occupied
  old-save recovery, native collision/door traversal, browser and human review.
  No map change/build/deployment is claimed at this asset-only checkpoint.
- Public remainsv71/Site62. Alignment owns its finite full-turn profile/tests;
  its latest01:30 result is two controlled native cases with stronger party/
  callback/packet checks, still awaiting handoff/independent root review. These
  are not yet added to accepted fixture totals. GoalACTIVE; all broad gatesOPEN.

v72 primary/map source checkpoint — October15,01:35UTC:

- Four original frontage cards occupy53 previously walkable cells: brick at
  2,1 (3x5), sage2,12 (3x5), sandstone2,20 (3x5), coffee21,2 (2x4). Coffee joins
  the gap between northern rowhouses. Western sidewalk column5 and surrounding
  cross-street approaches remain open. Decorative doors are solid, with no new
  interior, warp, quest, item or real-business-location claim.
- Original primary allocation:213 resident8x8tiles,54metatiles/attributes,
  banks0..3; callbackNULL. Primary tile0 is transparent. Native records retain
  the existing secondary sidewalk under every facade. Front foundation rows
  use BG2 priority behind the approaching hero; upper walls use BG1. Every
  footprint cell is collision-blocked at elevation0. Existing secondary503
  tiles/150records/attributes/palettes and door-reserved tiles stay byte-exact.
- Three independent source/resource cases decode all53 primary facade cells,
  including RGB555 bank binding, quadrant flips, underlay and layer attributes.
  Pinned prior map hash proves only53 cells and the primary binding change;
  remaining reachable space stays reachable, event/warp/grass locations stay
  exact, and a safe recovery candidate is at most3 Manhattan steps away.
  Malformed cross-tileset underlays are rejected. Existing map14/park12/door6
  tests pass; routine local check includes both new asset and infill suites.
- The static source comparison is inspected and retained in
  park-frontage-v72-plan/source-comparison.png. It is explicitly a proposal,
  not in-engine proof. Native compilation, independently bounded ROM/ELF audit,
  actual occupied-save recovery, collision/door checks and browser play remain
  required before publication. No art approval or finished-neighborhood credit.
- Public staysv71/Site62; forthcoming version0.0.72-park-infill-preview remains
  source-only at this checkpoint. Root continues integration; alignment still
  owns only its isolated full-turn fixture/tests. Broad gates remainOPEN.
- Full local check passes after historical map tests remove only the new infill
  before asserting their unchanged older map hashes. New53-cell pinned test
  separately covers the complete new delta; no historical expected hash changed.

Controlled turn-resolution runner checkpoint — October15,01:38UTC:

- Alignment's frozen runner is reviewed and independently rerun by root against
  exact Emerald a9dec84d and immutable v71 target353ff5bd, using each cartridge's
  matching ELF and genuine in-battle controller snapshot. Both pass2/2 and the
  declared normalized observations agree. RunnerSHAb9e0a71016cb42771d1280a895dd51ad385cb0686a6816b5387f0bb7acd18adb.
- Living case executes both selected Pound attacks, native MoveEnd/residual
  callbacks and returns to next-turn action selection: HP72/72, PP9/9,
  RNG4231221723 after nine independently derived LCG draws, turn1, empty stacks.
  KO case reaches an unanswered native player CHOOSEPOKEMON plus opponent
  standby: HP0/90, PP10/9, RNG833674724 after four draws, faint1, turn0. Native
  faint cleanup restores Normal types; native party-screen command increments
  its switch counter before asking. This is a partial boundary, not completed
  replacement, cancellation after replacement or a complete KO turn.
- Actual native per-side SETMONDATA handlers update secure party records; only
  explicitly listed presentation packets are acknowledged by transport. All
 1200 party bytes/nonparticipants/checksums,352 battle-mon bytes,68 result
  bytes, packet order, save blocks/pointers, party counts, action order, stacks,
  outcomes, RNG and canaries match fixed source-derived postconditions. Unknown
  choices/controllers/scripts fail closed. Controlled Rattata parties and
  battle-only stat/type/speed overrides are disclosed, with TRAINER|BATTLE_TOWER
  rules and no LINK flag. This is not player UI, natural stat generation,
  animation/audio, EXP, durable-save or campaign evidence.
- Actual native agbcc ABI probes verify struct sizes/offsets, message-window
  allocation and Main.inBattle mask; no host sizeof assumption. Each case45s /
  4096 dispatches, whole CLI240s, driver120s/2M instructions per call; private
  unique executable avoids concurrent frame-capture binary ownership.
- Root receipt turn-resolution-root-reviewed-v71/result.json
  SHA603bcc90587b3b8a9356626a6fb852d82f597b3582ae3dd6229a87779cf3da8f.
  Peer positive receipt SHA797772a34381804a53b62017ec41e4446f0bdb6da874b8be2295f03d3cfb65b2;
  native wrong-RNG negative SHAb2580120bd4a4b7581a1894dd562ada29554141029c3a8f05078986f3e3d64fa
  fails only the deliberately wrong oracle. Frozen capture_core.py,
  core_capture.c and function_fixture.c remain unchanged. Broader existing
 711/57 totals are not automatically inflated by two stronger overlap profiles.
- The483-line runner is one coherent native setup/dispatch/oracle lifecycle and
  is committed intact as a justified size exception; its201-line portable
  guard suite/check wiring follows as a separate checkpoint. Existing mechanics
  guards4/4 and move-pipeline guards8/8 pass. Full-turn acceptance remainsOPEN.
- v72 draft1f404cb626cafde1edeb2d786d41e76471dd1a62446539dcd3e8bdea82186249
  compiles with all pre-existing gates passing, but its new primary audit and
  genuine53-position recovery/runtime/browser checks are still in progress.
  One genuine old v71 saved occupied center3,14 resumes outside the new sage
  building in native v72; complete save-domain proof is still pending.

Controlled turn guard checkpoint — October15,01:39UTC:

- The201-line portable suite is committed separately and wired into routine
  local checking. Eleven cases cover independent damage/LCG arithmetic, strict
  schemas and duplicate setups; native SETMONDATA completion; wrong controller
  slots/requests/masks; unanswered replacement+standby; truncated observations;
  instruction/dispatch/wall limits; unknown callbacks/scripts/choices; complete
  postcondition corruption, omitted second action/MoveEnd and native faint-type
  cleanup. These are guard transcripts, not extra native mechanics scenarios.
- Root's actual native paired run remains the evidence for the two scenarios.
  Full-turn/type/status/ability/item/weather/switching coverage remainsOPEN;
  the broader711/57 totals and0/11 human approvals remain unchanged.
- Alignment now owns a finite independent v72 compiled-primary audit, due02:36
  UTC, only new auditor/tests and seven explicit bounded reader symbol names.
  Root owns engine compilation and native53-position save-recovery work. No
  public v72 release is claimed before those checks and field/browser traversal.

v72 compiled primary gate checkpoint — October15,01:43UTC:

- Root reviewed and reran the independent auditor: actual immutable draftv72
  passes23/23; actualv71 fails for absent new primary/header/layout bindings.
  Exact native24-byte headers include compression/role/resource pointers and
  NULL callbacks. The40x32 layout binds both tilesets correctly. All213 primary
  tiles/54 metatiles/54 layer attributes/512 palette bytes are bounded, all53
  solid/elevation0 map cells are pinned independently of production placement,
  and original PNG pixels are decoded with actual4bpp/palette/flip semantics.
- All54 secondary sidewalk underlays, transparent primary tile0 and palette
  tail are checked. Entire v71 secondary resources remain pinned by exact
  hashes;503 resident tiles leave1016..1023 available to native door animation.
  Only seven named resource symbols were added to the existing strict reader;
  bounds, ELF-section backing and ROM/ELF byte agreement remain unchanged.
- Root actual positive receipt06c59c4542cddd85dd2e5c30708dfcb0d11c6e1e29e3b6a265b5e1eb9875f107;
  oldv71 negative receipt66ea4302158009eecc54c3061f6e8cfd261a372c927afe77816c7fbb92321527.
  Separate direct compiled-map comparison confirms exactly53 changed words and
  all1227 others byte-exact: park-frontage-v72-plan/compiled-map-delta.json.
- Build now preserves a unique independent primary audit receipt and refuses
  BPS creation on failure, alongside existing gates. The manifest records audit
  counts and validator/receipt hashes with human approval pending. Twelve
  portable fault-vector cases pass; their separate source checkpoint follows.
- Existing draft1f404cb6 predates gate wiring and remains immutable evidence;
  a subsequent normal build must reproduce it with the new gate. Native53-case
  old-save recovery is still running; no public v72 deployment is claimed.

v72 audit guard/recovery checkpoint — October15,01:45UTC:

- Twelve portable independent ROM/ELF fault-vector cases pass and are wired
  into the routine local check. They manually serialize original PNG pixels,
  all flip combinations, native headers and53 map cells; production primary
  packing is not their pixel oracle. Wrong pointers/roles/callbacks, map IDs/
  collision/elevation, underlays/layers, palettes/tails, primary pixels/VRAM,
  preserved secondary data, missing/truncated/non-file-backed/stale resources
  and changed source receipts are rejected. Full local check passes.
- All53 genuinely walked/ordinary v71 C6 occupied-position saves coldContinue
  in v72 at independently predicted nearest-safe positions, maximum2 tiles
  away. Cold Flash and all600 party bytes stay exact. Ordinary native C7 Save
  changes ONLY the declared location/warp domain; counters/save statistics
  increment once, all other declared gameplay domains stay exact.
- Private all-occupied-recoveries.json receipt
  SHA70ecc9176eac1a9b85910d488d4dde16667294a603464d72a76a5511d7ca0be1.
  Every branch starts from the same genuine v71 pre-travel battery/state; no
  RAM/battery editing or fabricated coordinates. These53 geometry regressions
  are not53 distinct campaign checkpoints and do not complete the save gate.
- Native field held-wall checkpoints and a normal59.604s walking capture are
  now running. Root owns these captures and final build/publication. Alignment
  owns only one additional controlled QuickAttack priority-turn profile,
  due02:30UTC; next alignment exchange by02:15UTC. Publicv71/Site62 unchanged.

Controlled priority-turn checkpoint — October15,01:53UTC:

- One additional source-derived full-turn case is integrated: player speed90
  uses QuickAttack98/priority1 before enemy speed110/Pound1/priority0. Both
  attacks use power40/accuracy100 and the same native hit script; there is no
  priority/speed tie RNG. Independent expected HP72/72, PP9/9 and ninth-draw
  RNG4231221723 match both actual ROMs in root's rerun. Native execution order
  is player then enemy despite the player's lower speed.
- Strict cases now declare per-battler moves and expected order. Native secure
  party initialization uses actual CreateMon/SetMonData. Expected move bytes,
  checksum and XOR encryption are derived independently from the fixed PID0/
  owner format; full party and battle-result last-move fields are compared.
  Unknown move pairs or contradictory order schemas fail closed. No controller
  ACK, transport, ABI or frozen capture source changes.
- Thirteen portable guards pass, including rejection of speed-only ordering,
  unchanged Pound secure bytes, wrong last-move results and reversed executed
  PP order. Root verifies the original two traces/packets/postconditions and
  full party hashes stay exact on both ROMs. Counts are three scenarios: two
  full living turns and one partial unanswered KO boundary, not three complete
  turns or broad type/status/item/weather/switching acceptance.
- Root receipt turn-resolution-root-priority-v71/result.json
  SHA2ae6e2ddbbfdb4dc590a7f3aa0fbd71f8c428ed3224412e5a264466683ce7c7c;
  peer receiptSHAa52afa29ed33e9d8c221ce0134efbb565eb1b737cab9782d535d1d505812406f.
  Absolute exact ROM/ELF/state paths now accompany hashes. Functional private
  fixture proof is on v71, not automatically v72 campaign or UI evidence.
- The first v72 browser route visually completes but reports338 audio underrun
  output frames over75.4099s; no frame mismatch/discard or dropped source audio.
  That sample is preserved, not counted as an audio-clean pass. A settled repeat
  without mid-route screenshots/native jobs is active; no causal fix is claimed.
  All broad performance gates and0/11 human approvals remainOPEN.

v72 public denser-frontage checkpoint — October15,02:05UTC:

- Normal native sourcecacdc7e3f5dc2b48a50fe074f91dbe781b32f117 reproduces exact
  drafttarget1f404cb626cafde1edeb2d786d41e76471dd1a62446539dcd3e8bdea82186249.
  BPS1034127bytes SHAccbc89b0c089d79699e4f3b8a33b06b7beef5bc4c89754f88766e545609a51ef.
  New primary23/23 gate runs before patch creation alongside all older gates;
  full local checks including13 turn guards and12 primary-audit guards pass.
- Actual six held-wall checks stop outside brick east/front, sage front,
  sandstone roof/front and coffee front. First coffee route hit the existing
  Cognition sign10,6; failed diagnostic is retained. Corrected route uses row7
  and succeeds; earlier five matching-prefix captures are reused only after
  verifying exact input/target provenance. Native59.604s3560frame review shows
  all four facades and camera/walking. No all-boundary or human occlusion score
  is inferred. Native wall receiptSHA12092b40699ffa7acc68508316a6a0bf11b814f6fd1dde87fcd4633ba81ee373.
- Actual clinic/Cognition/seedroom entries and returns land respectively at
  Park32,6 /13,6 /16,17 with Flash unchanged. All213 primary VRAM tiles and all
  four unfaded palette banks match compiled resources after every return.
  Return receiptSHA7b71ab5e0fbe76a7ae76c6074554b73929cddc6852db14ec1837e95440c7aa5e;
  loaded-resource receiptSHA81662669720cca56b810159d21729f27cb5b673ae97f5b3efaf78a823bf30eb1.
  This does not claim opaque RAM identity, current clinic blackout destination
  or additional campaign-save checkpoint credit. Earlier53 recovery cases stay
  bounded to gameplay domains/location/warps as recorded above.
- Chrome49row59.604s route visually reaches coffee. First75.4099s sample:
 4504 core/video frames,4501 render submissions,338 underrun outputframes,
  zero discard/mismatch/source-audio drop and final ACK. It is not a clean audio
  pass. Settled129.7993s repeat with no mid-route screenshot/native jobs has
 7752 core/video/submission frames,0discard/mismatch/warmup/drop/underrun,
  maxRAFgap10.4ms and finalACK. Both receipts retained; no causal fix claimed.
  Clean repeatSHA8fecb29075dec44b33f7fe987561767c90b80b59feafc522616953db41a6f1e3;
  firstSHAe916e7b77d908c884e07ea133bc5cbbea52144540610103b40410700e0bdc451.
  Repeat includes about70s idle after the route; not129s of distinct gameplay.
- Ordinary browser keys enter/leave clinic and show the correct street again.
  Screenshots retained; own tab/audio/core and finite1200s server closed. No
  public save/account/ROM upload. Physical response, guest update deadlines,
  three ten-minute workload classes, Safari/phone and listening remainOPEN.
- Private genuine Emerald Oldale/SF frontage comparison uses identical1992frame
 33.3514709473s controls/native clock, equal nearest3x and two original audio
  tracks. Both first loops meet a facade wall, then circle the sidewalk; no
  commercial reference is published. Scope explicitly exterior-frontage art/
  readability/native walking; helper adds only that label, without relaxing
  pairing provenance or bounds. Existing pairing guards3/3 pass.
  VideoSHAc386ffef9c0003a11ea86ef62add43cf04fc94fab1665cedd2fee2dc0cd480ea.
  User0–4 request is pending. Neither this row nor all four cards grants whole
  world art approval. Earlier Walden/Steven review also stays pending.
- Site63 succeeded2026-10-15T02:03:34.486156UTC, website source
  e7862d79648dff805d35eb3223eee0c0b8a0a44d; savedversion
  appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_deaefdc0920081918ed11bbe8b59f1a3;
  deploymentappgdep_6ad0346e60148191af5da997fd79303c. Archive
 59a05b5451e45acfc95accf04ef17994938ce7c1b01430b86812096b4b8f963e has88
  audited files: no commercial ROM, private save, ELF, ZIP, movie, AppleDouble,
  symlink or traversal. Approved originalSFMM homebrew remains. Production BPS
  decoder matches target byte-for-byte;15 runtime files/hosting/auth/storage exact.
- Anonymous live manifest/BPS match local; receipt
 30ea6f7277dbbf60077e6fb36342fc083b28cf830a409835277d2aff4f3b5ac3.
  Visible public loader verified/screenshot saved and own tab closed. Versioned
  release, public patch, comparison scope and this spec are committed together.
  GitHubActions remains manual-only, all pushes[skip ci].
- GoalACTIVE throughOctober15,18Pacific. Human0/11; clinic music remains last
  explicit2/4 with revision awaiting review; full campaign/quality gatesOPEN.
  Next first-slice cleanup is scoped BUILDER role labels for Walden/Steven,
  preserving all numeric classes and unrelated table text. Alignment's read-only
  recommendation is complete; no label change is included in publicv72.

v73 scoped role-label source checkpoint — October15,02:10UTC:

- Read-only alignment identified a shared66x13 class table. Globally replacing
  POKéMANIAC would also rename seven inherited trainers and special-mode
  displays. Root instead compiles one BUILDER8byte constant and a trainer-ID
  getter alias for Walden320/Steven321, gated on their existing numericclass23,
  after the existing out-of-range guard. All original table text stays intact.
- Ordinary battle A/B class placeholders route through the existing getter.
  SecretBase/Union/Frontier/Hill/ereader and other special branches remain
  exact. This catches native battle introductions and other existing class
  placeholder templates; getter-only changes would miss the actual intro.
  No trainer class/AI/team/item/level/portrait/reward/flag change is intended.
- Anchored source overlay composes after species changes and validates both
  complete sources before writing either. Changed/stale/duplicate anchors or
  already-applied hooks fail closed. Restore registration includes both native
  source files; no ROM instruction patch or general text-writer relaxation.
- Four portable source guards and one optional complete pinned-engine source
  check pass locally. Portable checks require no ROM or private checkout; the
  optional complete-source check skips clearly when the engine is absent.
  Tests preserve all unrelated source bytes/special lookups and verify failed
  second-source validation cannot partially write the first file.
- Version0.0.73-builder-labels-preview is source-only at this checkpoint; public
  remainsv72/Site63. Native compile, independent all855-ID getter/whole-table/
  trainer-data audit, ordinary intro text for both people and save behavior
  remain pending. Alignment owns only new getter runner/tests and two exact
  reader symbols, finite task due03:15UTC. Root owns source/builds/UI evidence.
  Human0/11 and all broad remaining gates stayOPEN; goalACTIVE.

v73 independent getter checkpoint — October15,02:24UTC:

- Actual immutable draft37e60ad325df1f8e3369b13aa707ca418cd5a02c4905de59cb919ad8cf0d0c6b
  compiles with all older creature/cast/intro/map/door/portrait/primary gates
  passing. Both ordinary native introductions visibly say BUILDER WALDEN YAN
  and BUILDER STEVEN HAO with their original portrait candidates. Root retains
  full2048frame inputs/frames/audio and inspected frame720 montage.
- Root reviewed and independently reran the pure getter audit against v72/
  v73 genuine field snapshots. Each passes857/857 calls:855 valid trainer IDs
  plus855/65535 fallback. Exactly320/321 resolve to the single8byte BUILDER
  constant. Seven other class23 trainers stay POKéMANIAC; Scott265 staysLEADER.
- Native agbcc ABI verifies Trainer40bytes/class1/count32/AI28/partyPointer36,
  four team strides8/16/8/16, save/storage sizes,855trainer count and alias IDs.
  All66x13 original class rows, all855 first36 scalar bytes and ALL855 resolved
  team payloads stay exact, including both SF32byte parties. Pointer relocation
  is resolved semantically rather than comparing absolute ROM addresses.
- Native getter max19before/25after instructions; accepted bound512 with frozen
  driver hardcap2M. Sixty seconds per side/240s overall; private unique driver.
  Fourteen declared protected spans and per-call pointer/count/RNG observations
  stay exact. Temporary CPU registers/stack may change; no opaque RAM claim.
  Read-only scope excludes battle UI, durable saves and campaign acceptance;
  the separate actual introduction captures supply ordinary-A display evidence.
- Root receipt trainer-class-root-reviewed-v73/result.json
  SHAdf7438d6877443665a8382f67965857c0b8506c940f12992a1cdd3e510eea7db.
  Peer final receiptSHAf18d1a422a9920a020c8a23e394d6cba3ef0149df352d27d40382876c03ee7cc;
  deliberately old-label native negativeSHAf44af39aad872321cb3400f93aa31381a1ef8d5dcccc5623ce33249c7319c4f0
  rejects exactly the two intended aliases, with protected state preserved.
- Only two exact data symbols were added to the strict Cartridge whitelist.
  Frozen capture/core/function drivers, shared transport/ABI and original class
  table writer stay unchanged. Portable guard suite/check wiring follows as a
  separate checkpoint; actual model code214lines remains one coherent audit.
  Publicv72/Site63 and human0/11 unchanged; all broad gatesOPEN, goalACTIVE.

v73 getter guards/save/browser checkpoint — October15,02:30UTC:

- Nine portable getter/resource guard cases are wired into routine checking.
  Synthetic distinct66-row class strings keep commercial table bytes out of
  public fixtures; only two short interoperability labels are retained. Tests
  locally substitute a synthetic table hash, while actual native runs continue
  to enforce original full-tableSHA745460e8. The real fingerprint constant is
  separately pinned; synthetic transcript passes are not native evidence.
- Tests reject every class/alias-byte mutation, invalid class/party allocation,
  bad indirect team pointer, scalar/team changes across builds, stale/truncated/
  non-file-backed ROM/ELF, wrong native return/alias/ID/fallback, instruction/
  side deadlines and protected-state changes. Full local checks pass.
- Genuine old ParkC7 and preWaldenC3/preStevenC4 batteries coldContinue in v73
  and ordinary stationarySaveC8/C4/C5 with EVERY declared gameplay domain exact.
  Counter/save statistic increases once and playtime is monotonic. Receipt
 22fc4cbfeb38d8339cbe4852f2559943447325775596f10ac00ceb0492fcf9cb.
  These are stationary compatibility subsets, not additional campaign checkpoints.
- Ordinary Chrome input on a verified37e60ad3 checkpoint shows BUILDER WALDEN
  YAN in the actual native introduction. Native captures separately show both
  people. Browser screenshot retained; no timing/performance approval inferred.
  Own browser/audio/core and finite900s server closed; public saves/accounts
  untouched. This text-only scope does not change the earlier art-review clips.
- Full local check ran with the turn-extension source held fixed. Alignment's
  one-miss native handoff is now ready but NOT yet accepted/committed by root;
  root still must review/rerun it independently. Root owns all files again.
  Normal v73 rebuild and publication follow; public staysv72/Site63, human0/11.

v73 repeat-build repair — October15,02:35UTC:

- First normal rebuild correctly stopped: the engine workspace still contained
  this hook from the draft, so a fresh-only source anchor refused to apply it
  twice. Preserved logbuilder-v73-release-build.log records the failure; no
  public v73 was published from that attempt. This was an overlay repeatability
  error, not a change to the already verified draft gameplay.
- The installer now removes ONLY its own complete prior getter/include/two
  lookup changes, validates both complete sources, then reapplies. Unrelated
  earlier/later edits stay exact. Partial/stale/duplicate hooks still fail
  before either file is written. No general anchor checks were weakened.
- Six source guards pass, including repeated installation, unrelated-overlay
  preservation and atomic failure on an incomplete prior hook. Repaired normal
  build reproduces exact37e60ad3 with every older compiled gate passing. A
  further normal rebuild after committing this fix verifies repeatability and
  records the committed source rather than an uncommitted repair.
- Public staysv72/Site63; root owns source/turn handoffs. Last alignment exchange
  at02:34UTC; next by03:04UTC. Peer only derives an immunity oracle read-only,
  due02:50UTC. Native miss4/4 root verification is ready but not yet committed.

Controlled first-miss full-turn checkpoint — October15,02:40UTC:

- Root reviewed/reran the fourth controlled native scenario on exact a9 Emerald
  and immutable v71. Seed30/fasterplayer110 Tackle33 misses accuracy95, still
  spends PP, and slowerenemy90 Pound1 replies. End HP72/90, PP9/9, turn1,
  faint0, empty stacks, next-turn endpoint; only player receives an HP update.
  Full objects/save/pointers/canaries and three exact write packets pass.
- Oracle was derived from pinned source BEFORE peer execution: upper16 draws
 46397/47244/24877/5747/11048/46750; accuracy98>95 misses, reply45hits, crit13
  is noncritical, base19*97//100=18. Miss skips crit/damage/HP commands but reaches
  PP and MoveEnd; reply includes its complete path. Sixth LCG state3063870748
  matches; chance0/end-turn draws are included. Required per-case seed and seed
  in effective-setup identity prevent hidden default/deduplication ambiguity.
- Four scenarios pass each ROM: three full living turns plus one partial KO
  replacement boundary. Root proves original three traces/packets/checks/full
  party hashes remain exact. Fifteen portable guards cover independent six-draw
  arithmetic, secure Tackle checksum/XOR bytes, bad seed schema, incorrect enemy
  HP packet/omitted reply, wrong RNG and forbidden/missing miss-path commands.
  No extra controller ACK, transport/ABI/frozen-driver edits or object masks.
- Root receipt turn-resolution-root-miss-v71/result.json
  SHAb8ac3c1837c23beeeb7a542205395c5d40d74b1097b38bb34dc1b769ae798ff6.
  Peer positive75936f69f4ed8238fe0d0cc54c05a9f93d0e0ac7cf0941a4efa9757d0edab86a;
  wrong ninth-draw oracle negativea2cd9f62be8da1c2347fc836df24781e9ba7536fbbff09363925d33e1fcc9999
  rejects only miss RNG on both sides, preserving every other postcondition.
  Counts are not automatically added to overlapping711/57 baseline cases.
- Repaired v73 repeat build and full local check now pass; fresh unpublished
  manifest records committed sourceaec9c11180d4e0ef1db2266618ba104ef3e0aa54 and
  identical target37e60ad3/BPS527d8b396ec20c5f9309538a66630b0c5b73e94b142e7ea26abc5b49595e959f.
  Earlier successful but dirty-source package is retained under private validation
  storage rather than overwritten. Public remainsv72/Site63 until publication.
- Alignment delivered a read-only source-derived immunity plan; no fifth case
  is implemented or accepted yet. Root owns source, human0/11 and all broad
  type/catalog/full-turn/performance/campaign gatesOPEN; goalACTIVE.


v73 public Builder-label checkpoint — October15,02:55UTC:

- Normal repeat build from committed aec9c11180d4e0ef1db2266618ba104ef3e0aa54
  reproduces target37e60ad325df1f8e3369b13aa707ca418cd5a02c4905de59cb919ad8cf0d0c6b.
  Release0.0.73-builder-labels-preview includes BPS1037990bytes, SHA
 527d8b396ec20c5f9309538a66630b0c5b73e94b142e7ea26abc5b49595e959f.
  Public content changes only the two ordinary Cognition trainer class labels;
  no global class rename, new team, reward, ability or campaign claim. All older
  compiled gates, six source guards and nine getter guards pass.
- Both ordinary native introductions show BUILDER WALDEN YAN / STEVEN HAO.
  Three genuine older batteries coldContinue and stationarySave with declared
  gameplay domains exact, counter/statistic+1 and monotonic playtime. Chrome
  Walden introduction confirms actual rendered label/portrait; no performance
  inference from this text-only check. Native audio/video captures retained.
- Site64 succeeded2026-10-15T02:52:36.091350UTC, website source
 28198502ea5008e2860b80e78893471c2ac977de; savedversion
 appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_1edbee10d5cc8191b9417a4a1e2274da;
  deploymentappgdep_6ad03fea7e608191adedb0a2294b0b63. Archive
 site-v73-builder-labels.tar.gz SHA7f194e4141f62ae98dc791f80854fc3d06b7bd34064a4911085ebacd986505a5
  independently audits88 files: approved homebrew prototype only, no commercial
  ROM/ELF/private save/ZIP/movie/AppleDouble/symlink/traversal. Production BPS
  decoder reproduces exact target37e60ad3. Runtime15 emulator files unchanged.
- Anonymous live manifest and BPS return200 and byte-match local release.
  First default urllib user-agent got403; ordinary Mozilla user-agent succeeds,
  no authentication/bypass used. Receipt builder-v73-live-resources.json SHA
 1f8dafb963143ba8e9784980f95fcd44016438cc542d41eca15e11e3d65810d7.
  Own visible public IAB loader verified and screenshot saved; own tab closed,
  user tab/saves/accounts untouched. No GitHub workflow or database operation.
- Alignment handoff delivered one immunity extension; root review/rerun is
  underway, not accepted by this release. Peer files remain separately unstaged.
  Last exchange02:53UTC; next by03:23UTC. Peer read-only first-slice priority
  recommendation is finite30min. Human0/11 and broad gatesOPEN, goalACTIVE.


Controlled Normal/Ghost immunity checkpoint — October15,02:54UTC:

- Root reviewed and independently reran exactly one fifth controlled scenario
  against exact a9 Emerald and immutable v71. Faster player110 uses Normal
  Pound against a Ghost7/7 battle-only target, spends PP without enemy damage;
  slower enemy90 replies for18 damage. HP72/90, PP9/9, turn1, faint0, empty
  stacks and next-turn endpoint pass;159 native dispatches and21 checks/side.
- Oracle derived from pinned source BEFORE execution: accuracy/critical/type/
  adjustment/chance stages still execute on the immune attack. Damage/HP
  opcodes run but NO_EFFECT prevents any enemy HP-write packet. Chance0 still
  consumes RNG. Enemy neutral reply plus end-turn yields ninth state4231221723.
  Required ordered opcode path differs explicitly from the earlier miss path.
- All five cases declare complete strict live type pairs in effective setup
  identity. Original four remainMystery9/9; only this case enemyGhost7/7.
  Native secure Rattata parties remain natural and independently checked, not
  rewritten to match the battle-only overrides. Every352 BattleMon bytes,
  full1200 party bytes,68 results bytes and declared protected spans remain
  exact; Ghost bytes121/122 cannot silently revert. Controller ACK/transport/
  ABI/frozen-source policies unchanged; no extra input queries answered.
- Root receipt turn-resolution-root-immunity-v71/result.json SHA
 5f685a56cb132fd615bde92d280ed9521ec61cc5ae3fb6b8274b09f206495a35.
  Original four traces/packets/checks/party hashes/HP/PP/RNG/turns/faints exactly
  match prior root miss receipt. Peer positive790567397ae95680242874250473d4e6a3f4991b12c144ef22f02adcb89fb803;
  wrong early-immunity RNG negative8d985b988d7fa19f99b6e0db93bbcb8db46e597291874c325efd20198e2c8a5b
  rejects ONLY this case RNG on both sides, preserving all other postconditions.
- Seventeen portable guards pass; missing/reordered immune stages, absent reply,
  extra enemy HP packet, corrupted type bytes and wrong RNG all reject. Existing
  mechanics4/4 and move-pipeline8/8 pass. Exactly five profiles: four full living
  chosen turns plus one partial unanswered KO replacement boundary. No UI,
  animation, audio, EXP, replacement completion, durable-save or campaign proof;
  no additive inflation of overlapping711/57 baseline totals.
- Publicv73/Site64 unchanged. Human0/11 and broad gatesOPEN; goalACTIVE. Root
  owns all source again; alignment read-only first-slice recommendation pending.


v74 challenge briefing source checkpoint — October15,02:58UTC:

- Alignment reviewed actual first-slice content: optional TEAM PLAN already
  explains practice teams, but mandatory Scott fight starts without roster/level
  preview or confirmation once relaystage3 is reached. Root accepts one scoped
  improvement: four short native briefing pages followed by Yes/No on existing
  talk-to-Scott path. No returns control; Yes uses unchanged trainer battle.
- Briefing names actual TrolleyKit6/Puddleprig7/Hushmoth8, Reflect's physical
  reduction, existing special-move alternatives, Brinepup's Electric/Grass
  threats, and eastward clinic access. Pinned normal-font widths138..199px
  fit202px interior; actual rendering still requires inspection. No roster,
  stats, items, levels, map, sightline, reward or battle rule change.
- Source-onlyv74 proposal is not yet built or deployed. Actual old-stage3
  decline/repeat-decline/movement/save preservation, Yes→original introduction,
  compiled trainer/team preservation and browser interaction remain required.
  Human0/11; publicv73/Site64, goalACTIVE. Alignment last exchange02:57UTC,
  next by03:27UTC; read-only control-flow/data-comparison review due03:17UTC.


v74 public challenge-briefing checkpoint — October15,03:07UTC:

- Native four-page briefing at existing relaystage3 talk-to-Scott fits the
 202px text area (max199px) and displays complete roster/tactics/clinic hint
  plus Yes/No. No and B cancel with release/end, not the badge/TM path.
  Repeat decline remains harmless. Optional trainer sightline scripts unchanged.
- Three ordinary stationary-save branches (No/B/repeatNo) from a genuine older
  stage3 battery preserve EVERY declared gameplay domain, samecounter4/save
  statistic and monotonic playtime versus matched baselineSaveC4. Receipt
 three-declines-stationary-proof.json SHA97883458a96695489bcf7039060de776b6c4ef11359b5669b4739b2cb57c4275.
  Native600 party/512 vars/flags exact throughout stationary briefing/declines.
  Separate down/up movement returns8,4, changing only stepvars402A/B by2.
- Yes reaches LEADER SCOTT WU introduction and actual native team: species
 81/295/392,levels6/7/8,moves84/33/115;55/71/45;93/45/104,OranBerry139 on
  Hushmoth. These are native SF ID bindings, not inherited creature names.
  No original battle-initialization friendship changes are masked as equality.
  Read-only branch receipt592b302afdfd4a522d91bbcd0745e288fa69f2e6ecd53f4a62cde776de865289.
- Genuine already-badged old save skips briefing and shows existing REFLECT
  follow-up. Decline→ordinary exit→clinic reaches6,12/map1,4 with stage3.
  Initial too-short exit and direct sign-blocked routes are preserved failures;
  extra exit step and row7 sign detour finish the route. Clinic receipt
 f111b5fed2adcd142d6582a4b7017834df6e3a409288353b5a4780c56bc4a73a.
  New win/loss/full-bag reward outcomes were not replayed; their source branches
  and trainer/team data are unchanged. This is not full balance acceptance.
- Static independent native resources compare all66 class rows,855 first36byte
  scalar records and855 resolved teams exactly across relocated ELF pointers.
  Scott48byte team and both Builder32byte teams remain exact. Receipt
 ed998770193e677d806a1a1aa94ae76c09b5b2f5d6e79845239467327821238e.
  Chrome actual four pages, B cancellation and resumed movement inspected; no
  diagnostic performance run or public account/save mutation. Own QA stopped.
- Normal committedsourcea11720dd6e65b1cc2b897fcfa2c3b73bd3c9c351 reproduces
  target9335199708e8d38a95d705074f8f6e38c340026a83d7a1318f9fb8972de821f7.
  BPS1037250bytes SHA571f426ce608515f7e7959b552796494c196f776a6f77a1b9c45aa5b97308314.
  All older compiled gates/full local checks pass. Production browser BPS
  decoder produces exact target. Seven native captures losslessly compressed
  with all original frames/audio/state evidence preserved, no deletion.
- Site65 succeeded2026-10-15T03:07:09.763408UTC, websitesource
 173f0d1178a32c3b910064a8fcdc16c1b93f7c8f; savedversion
 appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_c666c435c06481918b67071c7e46b5a3;
  deploymentappgdep_6ad043544bdc81919d4074bd780f3a93. Archive
 site-v74-challenge-briefing.tar.gz SHA68b68e09ff34c9258c438c83fc379f30a3511762d8c9c1473ed0f27e7edfe47e
  independently audits88 files, approved prototype only/no commercial ROM/private
  save/ELF/movie/ZIP/AppleDouble/traversal/symlink. Runtime15 files exact.
- First immediate postdeploy resource request mismatched during propagation;
  subsequent canonical manifest and BPS both return200/exact local. Public
  loader inspected in own visible tab, screenshot saved, own tab closed.
  No database changes, GitHub workflow or user account/save mutations.
- Alignment recommendation directly informed this interaction. Last exchange
 03:07UTC; next by03:37UTC. Peer finite20min read-only visual priority review
  pending; root owns all sources. Human0/11, music last explicit2/4/revision
  pending, all broad gatesOPEN. GoalACTIVE throughOctober15,18Pacific.


South Park paving asset checkpoint — October15,03:15UTC:

- Alignment identified the ground's broad muted field and single repeated
  fleck as a remaining visual gap beneath the denser frontage. Root prepares
  one original bright concrete candidate for South Park ONLY; shared Sunset
  street source/palette and all maps/events/collision remain unchanged.
- Built-in image generation supplied square source; exact prompt/source retained.
  First dashed-joint candidate was rejected as repetitive and preserved privately.
  Second source uses an8x8 cream slab with one-pixel bottom/right joints. Native
  center samples select only existing palette1/2, repeat2x2 into16x16. No palette
  change/requantization or inherited artwork. Human approval stays pending.
- Six portable converter guards pass: native color/master/bounds, repeatability,
  source/prompt drift, desynchronized master/PNG/indices and palette corruption.
  Synthetic codec fixtures never become game assets; fixture folders preserved.
- Source-only preflight reduces resident secondary tiles503→502, preserves
  attributes/palette exactly and leaves reserved door VRAM1016..1023 available.
  Frozen baseline-v74 contains only original SF resource bytes, matching previous
  independent hashes, for checking all decoded non-paving art through repacking.
- Production renderer/compiled gate are not wired yet; no new ROM or publication
  claimed. Peer owns only new paving auditor/guard files, due03:56UTC. Root owns
  converter/assets/production integration. Last exchange03:15UTC,next03:45UTC.
  Native seam/door-return/browser/ordinary-save comparisons remain required.
  Publicv74/Site65, human0/11, music2/4 pending revision; goalACTIVE.


Independent paving audit checkpoint — October15,03:20UTC:

- Root reviewed/reran peer's independent native auditor on immutable candidate
 7686e352185010e5397d91d3ffdf16d5d939beed7ffd7d68ac5dc0fa6ffd72a8.
  All152checks pass:1200 quadrant roles,448 intended bank6 paving quadrants,
 592 unchanged resident pixel/bank quadrants and160 literal blank/nonresident
  words. Original attrs300/palette512 exact;502 resident tiles reserve doors.
- Root positive receipt matches peer byte-exact:
 d4d3a368a7873687cba6884db619553df5a7818515c798780efe607733e5ce7f.
  Genuine v74 negative rejects all112 paving-bearing records,40/152matched,
  no input errors; SHAe78a7a35a171910d2e2c4f6a9d93d41d28902bc161b4fc8c5e1422a403eeef10.
  Eleven portable mutation/flip/ROM-ELF guards pass; no producer import.
- Baseline source hashes/receipt are independently pinned; candidate allows only
  opaque1/2 repeated8x8 master. Physical tile repacking/flips are decoded, not
  treated as artwork changes or masked globally. Palette/bank/attribute, every
  unauthorized pixel, reserved/blank word, truncation and stale resource reject.
- Peer returned both files frozen; root owns them again. New gate integration
  and native candidate are still local/unpublished. Same-input native frontage
  shows brighter fine slabs and intact architecture. Human approval is pending.
  Publicv74/Site65, human0/11, goalACTIVE; doorway/browser/save checks next.


User paving-color correction — October15,03:23UTC:

- User likes the grid but rejects the yellow hue, preferring light/dark gray.
  Preserve the exact grid; use neutral light-gray222 with gray189 joints. No
  numeric score or full-domain approval inferred. Yellowv75 draft7686e352 was
  never published; public remainsv74/Site65. Its source/evidence remain intact.
- Root isolates paving in previously unused primarypalette4, keeping all
  secondarypalette bytes/road/curb/crossing/building/Sunset colors unchanged.
  Original building banks0..3 remain exact; primarybank5 and later unused tail
  remain zero. This adds a deliberate narrow palette allocation, not a global
  tint or change to the user's approved grid. Native gray result still pending.
- Built-in image edit supplies recolored source; original warm candidate and
  exact prompt retained privately. Converter guards now enforce literal neutral
  RGB555 palette, source/PNG/indices consistency and bank4. New auditor guards
  independently enforce gray/source/native bank4 plus the old secondarypalette.
- Peer owns only auditor/test correction through04:09UTC; root owns source/
  production/test integration and captures. No further yellow-browser run or
  publication; own emulator/audio/tab/server stopped. Gray native cache/doors/
  matched review/save/browser checks will run on its own immutable new target.
  GoalACTIVE, human0/11 and broad campaign/audio/performance gatesOPEN.


Gray paving source/runtime checkpoint — October15,03:30UTC:

- Gray draft47909520ff1e419cdab4286c9e4507d2c35c66e83ae8703084721164dc3d0938
  keeps the user's approved master8 and16x16 grid indices BYTE-EXACT to the
  yellow candidate. Only its two visible colors become neutral222/189, isolated
  in unused primarybank4. The entire original secondarypalette stays exact; no
  road/curb/crossing/building/Sunset tint. Native before/after shown to user.
- Root reviewed/reran corrected independent auditor153/153, all1200 quadrant
  roles. Actual rejected yellow draft now fails112 paving records plus primary
  gray palette check,40/153matched/no input errors. Root receipts match peer:
  positivea9f83d1371227b2a39c2447eb112223ac83ac955d8c23393efe97c0946951d22;
  negative9f971adc5b3c46922accacf9a3938c4c4c48a3272698cbfc95e4ec2359a2100b.
- Thirteen audit guards and eight converter/palette/packer guards pass, including
  self-consistent wrong source/native hue, wrongbank6 with samegrid, transparent/
  unused palette values, primary allocation errors and bank4 used by non-paving
  cells. Primary0..3/frontage images remain exact; primary5+tail stayzero.
- Composite infill now22checks plus nested153paving checks: keep original
  headers/roles/nullcallbacks/layout/53solidcells/54underlays/foregroundpixels/
  layers/palette validation. Only former full secondary rawtile/metatile identity
  is replaced by independent decoded-delta proof; attrs/palette remain pinned.
  Historical render pins normalize only checked paving pixels AND oldbank6,
  alongside preexisting lawn normalization. Whole old fingerprints retained.
- All existing local checks and compiled gates pass. Native gray coldContinue
  from genuine olderC8, matched33sec walking, and all three actual interior
  entry/returns pass. All502 secondary/213primary tiles and all6primary/7secondary
  unfaded palette banks match compiled bytes after every return. All1280 native
  map words remain exactv74; no Flash writes during these walks. Receipt
 067732c8f9c7a2b22dc8a542f85d9b327c93b3d3337daf2155a857be2faf8958.
- Matched ordinary save checks/browser/normal clean build/publication still
  pending. Matched Emerald gray clip prepared privately; no score inferred.
  Yellow remains unpublished/superseded. Peer returned both files frozen; root
  owns all sources. Last alignment exchange03:27UTC,next03:57UTC. Publicv74/
  Site65, human0/11, goalACTIVE.


v75 public neutral-gray paving checkpoint — October15,03:34UTC:

- User requested gray while retaining the liked grid. Native master8/paving
  indices remain byte-exact; isolated primarybank4 changes only visible paving
  colors to222/189 neutral gray. All original street/curb/crossing/building/
  Sunset palette bytes remain exact. Yellow7686e352 was never published.
- Actual Chrome shows gray paving, ordinary clinic entry and gray return; own
  emulator/audio/tab/finite900s server stopped. No performance run inferred.
  Native three-interior cache proof covers all502secondary/213primary tiles and
  all6primary/7secondary unfaded palette banks, including isolated graybank4.
- Matched ordinary C8→C9 saves on v74 and grayv75 preserve EVERY declared
  gameplay domain, counter/stat+1 and monotonic playtime. Their C9 domains are
  exact across builds. Receiptf3c216c03c27c28bfe39e55b997bb3b56eadefc3ce1cc4ff312bbf8002b6ab40.
  Genuine grayC9 coldContinue preserves Flash/native600party bytes at22,6;
  receiptd3102fcb7d5a1e7cff0c4b348a7a9b064921c5b3be84553ee2fa045b306f1ca4.
  Same one field checkpoint, not extra campaign/save-suite credit.
- Normal committedsourcef85c8906a6c7bcd2101bdf7fb8ca287cb3ae2f7e reproduces
  target47909520ff1e419cdab4286c9e4507d2c35c66e83ae8703084721164dc3d0938;
  BPS1038990bytes SHAa74a788ae865d9bee832be62d54f9667f2129bb6c2bddf981b4514617f83d865.
  Full local/compiled checks pass; production web decoder reproduces exact ROM.
  Manifest honestly retains source_worktree_dirty=true for untracked output/
  preserved unrelated PDF; tracked implementation is committed. No clean-
  checkout acceptance claim and no modification/staging of that PDF.
- Site66 succeeded2026-10-15T03:34:06.037664UTC, websitesource
 ab096cf53af29f93cc80eb888a623949aa0826c9; savedversion
 appgprj_6ac5f5f2ab588191839f86b3aafb5390~appgver_a1cf99a11f7481919126b5e4e9ee8357;
  deploymentappgdep_6ad049a56fc8819193f279a3440b4fd6. Archive
 site-v75-gray-paving.tar.gz SHA14caf672bd0a5862947ac2c75e37d842ed05882c918baeb97729138d15f1ff79
  independently audits88 files, approved prototype only/no commercial ROM/
  private saves/ELF/movie/ZIP/AppleDouble/symlink/traversal. Emulator15 files exact.
- Canonical live manifest/BPS200 and byte-exact local; receipt
 a444d4192c8d5d7d3c3fd00b8ada68fba01777ff7e822b4f2dc8f52902ae77b2.
  Public loader visible/inspected/screenshot saved; own public QA tab closed.
  No GitHub workflow, database, account or user-save mutation.
- Revised matched33.351sec Emerald/gray clip prepared under
 park-paving-v75-gray-emerald-paired-review/comparison.mp4, same1992frames/input/
  nativeclock/equalnearest3x/two original audio tracks. Color request fulfilled;
  no numeric/new full-domain approval inferred. Original native frames and
  superseded yellow evidence losslessly preserved.
- Alignment next finite read-only task recommends a meaningful600sec active
  field workload instead of long idle. Last exchange03:33UTC,next04:03UTC.
  Root owns all source. Human0/11, clinic music last explicit2/4/revision pending,
  broad full-campaign/performance/audio gatesOPEN. GoalACTIVE through6PM Pacific.


Active-field workload preparation — October15,03:42UTC:

- Private replay page no longer hard-stops supplied routes at180seconds. A
  tested helper selects180..600seconds, rounds route+one-second completion
  margin upward, and rejects routes over599seconds. Existing session deadline,
 50ms timer-slip abort, hidden-page abort and final release stay unchanged.
  Six replay tests pass; no public emulator/runtime/game source changed.
- New explicit field route310rows/35756frames/598.652206seconds starts21,6,
  descends to row8 and shuttles x21..35. Direction-held34464frames (96.39%);
  no doors/NPC patrols/signs/grass/warps on corridor. Normal walking2154steps.
  Browser timings remain approximate wall-time dispatch, not guest synchronization.
- Actual native pilot reaches35,8 and returns21,8; complete route also ends
 21,8 with Flash exact. Native background scroll changes34464transitions,
  supporting active movement rather than idle. Native receipt
 b19e15bd2abb747da69ef9fa2781fe729e14f034e7e7c9ab9e87983bdc0be90b.
  Native runFrame capture is not real-time performance or speaker-interval proof.
- Alignment independently confirms geometry/arithmetic/evidence limits. Browser
 600second run is next, with complete310/310 replay/foreground/duration/final
  audioACK and zero drops/underruns/debt/mismatch required for this narrow
  checkpoint. No heavy concurrent builds/captures during measurement.
- Short native guest-loop profiler remains120frames, not an accepted10minute
  deadline probe. Full99%guest-update/render deadlines, mixed/menu workloads,
  Safari/phone, physical input and listening remainOPEN. Publicv75/Site66,
  human0/11, goalACTIVE; last alignment exchange03:41UTC,next04:11UTC.


Active-field acceptance frozen before result — October15,03:48UTC:

- First600second Chrome run began03:43:55UTC, with visible start and midrun
  road movement observed. Results are not yet available. No concurrent builds/
  captures/test suites; only low-load source review/writes. First result stays
  preserved whether it passes or fails. Fresh snapshot required for any retry.
- Separate active-field qualifier reuses the generic exact-runtime/report audit
  and requires the pinned ROM/CSV, matching310row totals, declared590..599sec
  route with at least95%directional duty,600000ms duration-end,
  uninterrupted visible scope, complete/error-free
  replay, exactly310planned input events, no pending input, zero discarded
  debt/video-count mismatches, running/primed audio and zero warmup/drop/underrun.
  These criteria are declared before reading this run's final counters.
- A generic valid/green diagnostic with an aborted/hidden/late route cannot
  qualify. Directional duty is declared input, not measured walking fraction;
  actual scenes/motion still need separate visible evidence. New qualifier/tests
  are written but tests wait until the measurement ends to avoid local load.
  No physical response/guest deadlines/native real-time/Safari/phone/listening
  or fullPerformance approval inferred. Publicv75/Site66; goalACTIVE.

- Pre-result alignment review tightens qualification: the generic auditor already
  requires the full600000ms, so no shorter quantization exception applies.
  Verified generic complete dispatch timing and configured route totals are
  mandatory; missing controller_route cannot bypass dispatch validation.
  Masks are restricted to neutral/right/left/down; action-only input cannot
  count as walking duty. These changes do not alter the running session.


First active-field result — October15,03:56UTC:

- Preserved Chrome report480c716902f042c9aac0cd3e94a20d56 SHA
 a92345bc5e1a8e01f9421f1bc15d6bd33dd680739af8a4b469185c4e68825b5f,
  exactgrayv75/runtime15.600000.2ms,71950visible/0hidden ticks; complete
 310/310dispatches/maxlateness3.3926ms. Visible start/midrun/end remain
  road scenes; no assertion of browser exact native ending coordinates.
- Generic report integrity passes; strict field qualificationFAILS:334input
  observations vs310planned,16discarded frame debt,13738audio underrun
  outputframes at44100Hz (~0.3115sec).0droppedsource/0warmup, finalsame-epoch
  audioACK received,35820executed/video frames/no mismatch/no pending input.
  No causal diagnosis from these aggregates; extra input/stall timing needs
  targeted observation. Failure is preserved, not replaced by a later retry.
- New qualifier87lines+classificationfixtures136lines;11local tests and
 8existing generic integrity tests pass. Negative cases include interrupted/
  aborted/incomplete replay, input/frame/audio loss, rehashedidle/action-only
  route, missinggenericdispatchvalidation/configuration and shortwindow.
  Actual receipt invokes real generic auditor, not mockedclassificationdata.
- Own local QA emulator/audio/tab/server stopped. Publicv75 unchanged.
  Fullperformance and all11human gates remainOPEN; goalACTIVE. Last alignment
  exchange03:56UTC,next04:26UTC; finite read-only diagnosis task requested.


Field diagnostics checkpoint — October15,03:58UTC:

- Private bounded observer retains mapped DOM keys (trusted/repeat markers),
  window focus/blur and supported browser long tasks; cap2048 with explicit
  overflow, exactmeasurement-window filtering. No unbound typing collection,
  guest-memory access, public runtime/control or pacing changes.
- Suppliedroute is now single-use per loadedcheckpoint, including aborted
  attempts. A fresh local session is required; button stays disabled after
  abort. This prevents accidentally restarting the descent from row8.
- Frozenobserverbytes join exacthelper/CSV verification; auditor also checks
  original private page/server bytes when pinned. Sixobserver+sixreplay+
 9generic+11fieldclassification local tests pass.
- Chrome10sec pilot captures1trustedRightdown/1keyup,597video frames,zero
  debt/mismatch/drop/underrun/warmup and finalACK. Receipt8127f611812ecb2b1fd6d6abb2999b723d9ef00c2039f4709bb3cce6b7953372.
  Deliberate3.04secabort records3/310replayrows+4synthetickey events and
  disabledroutebutton; preservedfd23c5d563ca0a87e88566b01a8145dfc3ec88467412f53627538a6c81b14bbd.
  Abort is not a performance pass. Own QA/audio/tab/server stopped.
- Next diagnostic repeat uses original snapshot and samegame/runtime, no
  concurrent builds/captures. First600secfailure remains authoritative evidence
  of an unresolved issue until cause/fix/retest. GoalACTIVE,publicv75 unchanged.


User facade-ground integration correction — October15,04:03UTC:

- User still sees buildings as flat objects placed on pavement, missing a
  boundary or a distinct connection to the sidewalk. No numeric paving or
  full-domain approval was given. Neutral gray/finegrid preference remains.
- Prioritize shallow foundations, door stoops, garage aprons and subtle contact
  shadows with architectural variation. Keep existing walls solid, doorway
  approaches walkable and native door-animation VRAM reserved.
- Alignment identifies free primarybank5/299primarytile slots; secondary is
 502/504residenttiles. First prototype uses primary ground-apron cells below
  existing facades, not secondary sprite repacking or footprint/collision changes.
  Brick apron(x2..4,y6),sage(x2..4,y17),sandstone(x2..4,y25),coffee(x21..22,y6);
  terrace/service approaches remain protected. Native/browser proof is pending.
- Built-in original threshold sheet and shallow refinement are preserved;
  aspect-preserving nearest/RGB555 converter source is drafted. No converter/
  build/capture/test suite executed during the current600second observation.
  Starterthreepromptsource change is ready but unbuilt; release is stillv75.
  Last alignment exchange04:03UTC,next04:33UTC; goalACTIVE until agreeddeadline.


Instrumented active-field repeat — October15,04:09UTC:

- Same exactv75ROM/runtime15/originalsnapshot/310rowinput, fresh finiteChrome
  session. Preservedreportb31bec5371ca4832ad2ec5d763498156 SHA
 f7a3d7dfbd7ced047fe175d130b26758a5751ee27a3a38a6f5578050902d8fa1.
  Genericintegrity passes; strict field qualificationFAILS9discardeddebtframes
  and8330underrunoutputframes/44100Hz (~0.1889sec).0drops/warmup/mismatch,
  finalACK,600000.8ms/71953visible/0hidden ticks,35827video frames.
- Replaycomplete310/310,maxlateness5.2308ms; SDKobserves310inputs. Bounded
  log has155syntheticdowns/155ups,0trusted/repeat/blur/focus/longtask entries
  and0overflow. Extra keyboard inputs are not necessary for this failure.
  MaxrAFgap200.7ms with corebatchmax9.7ms/rendermax2.8ms supports investigating
  scheduling gaps; aggregatecounter/timestamp correlation is not causal proof.
  No engine/core fix or fullperformance acceptance claimed.
- All localQAaudio/emulator/tab/server stopped; no new long repeat queued.
  Alignment reviewing bounded catchup/prefill tradeoffs read-only; root now
  prioritizes user-requested facade-ground integration and starterpromptproof.
  Both600secfailures remain preserved. Publicv75, human0/11, goalACTIVE.


Native street-threshold checkpoint — October15,04:24UTC:

- New original primary ground details connect44existingwalkablePcells to
  foundations/doorsteps/garageaprons; allother1236mapwords,53existing solid
  frontagecells, original213primarytileprefix/54records/54attributes and
  paletteoutsideunusedbank5 remain exactv75. Residentprimary235/512, secondary
 502/504;65primaryrecords. Doorwarps/signs/collisions/elevations unchanged.
- Independentcompiledoracle42/42 plusnestedpaving153/153; linkedfaultguards
 17/17. Original-only frozenv75baseline protects complete1280mapword history
  and oldresources. Source/nativeart/palette/alpha/banks/flips/layers/underlays
  and44precisemaps bindings verified independently of productioncomposer.
- Firsta71candidate nativecloseup catchescentralbrickstoop belowleftwindow
  andleftcafemat belowdisplaywindow. Preservedcandidate/captures. Corrected
  brickusesrightbaystoop; full32pxcafeapron is reflected toputmatbyrightdoor.
  Correctedprivatecandidate9119256974ab0a948810fcce2dc3871c53226c2948023fb76afadf3351018733,
  stillunpublished. Nativecloseup nowalignsbrickstepwithrightdoor.
- GenuineoldC8nativecold, all3interiorentries/returns pass; aftereachreturn
  all235primary/all502secondary graphicsbytes and6primary/7secondaryunfaded
  palettesmatchimmutableROM, withFlashunchanged. Receipt19859f1fd3ecb5c1b3fc1f20adf3735527507876ddc65126b26867bc6c078462.
- OrdinaryC8->C9save preserves alldeclaredgameplaydomains, counter/stat+1;
  no new50checkpoint credit. Full localcheckcommands pass after updating the
  oldprimary-only-WXYZ assertion to recognize preciselydeclaredwalkableaprons.
  Originalfailedlog preserved; noGitHubActions. Browser/clip/humanreview pending.
- Starterprompttext is an independent uncommitted three-line change included
  in the privatecandidate only; nativebranchchecks underway, noUIapprovalclaim.
  Publicremainsv75/Site66; bothperformancefailures remainOPEN; goalACTIVE.
