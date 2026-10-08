# SF Mini Monsters — v1 specification

Status: technical prototype shipped; Emerald quality parity is NOT achieved.
Section 15 is the active goal and overrides the earlier prototype completion criteria.
This file is the source of truth for scope, acceptance, and progress.
Updated: October 7, 2026.
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

### 15.1 Objective and completion rule

User-requested work cutoff: October 8, 2026, 6 PM San Francisco local time
(October 9, 01:00 UTC). Stop new work at the cutoff, record remaining gates,
make the final coherent commit, and pause the goal. A one-time thread reminder
is scheduled; no recurring monitor or GitHub workflow is authorized by this.

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

Current snapshot (October 8, 2026; historical checkpoint details follow):

| Item | Authoritative current status |
| --- | --- |
| Active stage | B: polish Sunset/South Park/Cognition before campaign expansion. Full section 15.1 scope stays required. |
| Human-approved full domains | 0/11. Title-art, courier-walking and doorway subset reviews are pending. |
| Public build | 0.0.40-clinic-music-preview; target fcdb5aeb7266af8af0938d52bfd13c00fc9a1db9ba111abac2a2667aff8e3b94; Site version 32. Neutral clinic art and original Continue/storage labels preserved; original clinic music added. Clinic music subset rated 2/4 by user; full Audio remains incomplete. |
| Latest local source build | Same v40 target, source 0898f08. Normal compilation/BPS and full local checks pass. Old v35 battery resumes; 2,048 walking and 336 healing native/WASM RGB/PCM/Flash frames match. Two actual music loops captured. |
| Content implemented so far | Sunset opening and courier apartment adventure, Muni, South Park, clinic and first Cognition gym draft; eighteen creature candidates and three starter lines. Complete 16-hub/8-gym/150-entry campaign remains unfinished. |
| Relevant functional evidence | Public 0.0.24 earned Fire-starter first-gym route; local 0.0.26 old caught-party resume and four-direction walking/running. Native/WASM RGB, audio and Flash match for the recorded routes. |
| Reference movement evidence | Courier candidate's first unblocked four-direction rectangle: sixteen frames/tile, zero difference against the reference. Full movement/performance/input gate remains open. |
| Public QA | Site 32 Chrome account session restores old local save, displays GUIDE at Continue and resumes clinic. Actual ROM download matches v40; battery export remains byte-identical to v35 import. Sampled core counter 60.0 fps. Fresh auth, controlled account/guest isolation, Safari/mobile and full save/performance gates remain open. |
| Remaining system gates | 300 independent mechanics cases, three ten-minute deadline/audio traces, ten full save round trips, fifty campaign checkpoints and three fresh complete campaigns are outstanding. |
| Next work | Clinic music is explicitly 2/4; improve its weakest audible aspect after requested gap feedback. Clinic art subset score also pending. Other first-slice music, cast/portraits and interior material rules remain required. Preserve walking. Checks stay local; Actions manual-only. |

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
