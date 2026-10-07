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
The archive/header/hash have been inspected; benchmark clips have not been collected.

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
- Next checkpoint: South Park/Cognition and the polished first slice, while
  completing the reference measurements and comparison suite.
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
