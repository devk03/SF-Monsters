# SF campaign — map atlas, draft 2

October 16, 2026. Proposed production blueprints, not built or player-approved maps.
Existing Sunset/South Park layouts remain unchanged by this writing pass. Dimensions
below are planning envelopes for future maps, not instructions to resize a live ROM.

## Geography and ownership

Sixteen **adventure hubs** remain the town list. Office pockets, walking connectors,
coastal dungeons, Mission Bay, the Financial District, the Ferry Building and Treasure
Island are supporting areas. Their labels retain their actual districts. A routing
parent below identifies a content package, not a claim that two neighborhoods are
geographically identical. The ocean stays west and the bay east; no Peninsula,
Oakland, South San Francisco or outside-city excursion is playable.

Campaign order is distinct from adjacency. A story gate unlocks an adventure or a
new transit destination; it does not justify invisible walls across every street.
Earlier-accessible spaces have appropriate waiting/revisit dialogue. Story-critical
long transfers are free, reversible and shown as transit, never direct walking warps.
There are no one-way trips that strand a player without supplies.

## Shared map contract

- New hub main blocks target 64×48 or 64×64 movement tiles, split when necessary;
  interiors target roughly 12×12 to 24×20. These are envelopes pending ROM budgets.
- Fit at least two connected street blocks and 18–28 façade modules where the
  composition supports it; typically 4–6 purposeful entrances. Decorative fronts
  remain visibly closed. Do not promise 28 unique interiors per hub.
- Main pedestrian routes keep a two-tile clear corridor; doors get a readable
  approach/apron. Corner curbs, foundations, low fences, planters and wall shadows
  integrate buildings with sidewalks. Keep accepted compact pixel-art scale,
  neutral gray paving, lamps and façade density; no chopped teal or yellow blanket.
- Collision covers actual solid footprints. Roof overlap can cover the top of a
  sprite only where a walkable rear path genuinely exists. No under-building
  movement, blocked exit tiles, door-to-wall warps or concealed progression triggers.
- Keep the arrival, healing/storage, next objective and return transport legible.
  Collision, object slots, tile/palette budgets, doors and old-save recovery require
  actual native checks later. Avoid more than 12 simultaneous scripted/NPC objects
  in a local scene until the engine's live object budget is confirmed.
- Each main adventure has a hidden discovery, a recurring person, a stateful payoff
  and a later revisit. A named cast slot references researched public identity;
  background scenery does not need an invented human identity.
- Sidewalk furniture is placed in edge strips, not the center of walking lanes.
  Use repeated city kit coherently; landmark silhouettes and street compositions
  distinguish hubs without demanding a different art style for each one.

## First-visit itinerary

1. Outer Sunset — Recover the sensor; optional window/beacon calibration
2. SoMa / South Park — Repair relays and earn Cognition's Build Badge; later contain an escaped demo
3. Mission — Track missing pigments, expose a projected habitat and rescue a frightened companion
4. Dogpatch — Route safe workshop power and recover the controller coupler
5. Castro — Restore light, stage power and a quiet rest area in a deliberate order
6. Haight-Ashbury — Reconstruct a performance's real timing from conflicting flyers
7. Inner Sunset — Read soil/light before restoring the beds
8. Richmond District — Compare archive clues with tide markers and find a fog-creature glimpse
9. Tenderloin — Find the musician sheltering a stressed creature; restore a rest interval
10. Fillmore — Return instruments by their sounds, then demonstrate staggered rhythm
11. Japantown — Distribute lantern and gallery supplies according to different needs
12. Presidio — Distinguish reflected signal from the source and protect habitat coordinates
13. Marina — Recover the quarter-zip and its controller log using three concrete clues
14. Russian Hill — Restore brake/wheel/signal acknowledgement order
15. North Beach — Order the notebook observations without mistaking repetition for importance
16. Chinatown — Restore festival distribution; expose uplink; return after rehearsals for Launch Night

## Hub blueprints

### 01 — Outer Sunset (outer_sunset)

- **Anchor:** Judah / Great Highway.
- **Composition:** Beach boardwalk, connected low-rise homes, courier studio, field mentor corner.
- **Entrances / circulation:** Apartment door→Judah sidewalk; west→boardwalk; north beach pocket; east signed Muni stop.
- **Adventure:** Recover the sensor; optional window/beacon calibration.
- **Support:** Home/studio supplies, Karpathy healing, basic encounters.
- **Hidden discovery:** Apartment beacon and N-Judah postcard.
- **Afterward / revisit:** Calibrated beacon displays two genuinely different readings; Karpathy notices the starter's growth.
- **Art direction:** Cold gray pavement, ocean blue, warm house fronts; benches, low fences, transit pole.
- **Node ownership:** O01; A01, A02, A03. These references
  describe proposed scene placement, not implementation status.

### 02 — SoMa / South Park (soma)

- **Anchor:** South Park / Third Street.
- **Composition:** Oval park, compact office street, Cognition, clinic, Seed Room.
- **Entrances / circulation:** Transit arrival→south apron; park walk loop; clinic east of gym; service alleys return to same street.
- **Adventure:** Repair relays and earn Cognition's Build Badge; later contain an escaped demo.
- **Support:** Clinic, shop/storage, safe save/rest area.
- **Hidden discovery:** Berry bench, startup notebook, Seed Room hints.
- **Afterward / revisit:** Park discovery notebook changes from a startup-name list to a field-care checklist.
- **Art direction:** Neutral paving, planted edges, warm office windows; preserve accepted dense homes and street props.
- **Node ownership:** O05; O06, O07, O08, G01, O09, H07, A04, S01, S02. These references
  describe proposed scene placement, not implementation status.

### 03 — Mission (mission)

- **Anchor:** Valencia / mural side street.
- **Composition:** Mural block, small plaza, print workshop, demonstration alley.
- **Entrances / circulation:** Signed Mission arrival→plaza; mural order leads around block, not through walls; Dogpatch transit at southeast exit.
- **Adventure:** Track missing pigments, expose a projected habitat and rescue a frightened companion.
- **Support:** Clinic kiosk, storage, low-cost supplies.
- **Hidden discovery:** A pigment mark visible only from the public side of a fence.
- **Afterward / revisit:** Repaired mural includes the neighborhood's own changing weather marks.
- **Art direction:** Warm painted walls on gray walks; stoops, bike racks, paper notices; no generic giant lab.
- **Node ownership:** H05; M51, M52, P01. These references
  describe proposed scene placement, not implementation status.

### 04 — Dogpatch (dogpatch)

- **Anchor:** Third Street industrial connector.
- **Composition:** Brick workshops, rail-edge fence, machinery court, waterfront lookout.
- **Entrances / circulation:** Third Street arrival→workshop forecourt; fenced nonwalkable rail boundary; signed Mission Bay branch.
- **Adventure:** Route safe workshop power and recover the controller coupler.
- **Support:** Workshop rest/storage terminal and supplies.
- **Hidden discovery:** A spare parts bin contains a cosmetic workshop stamp.
- **Afterward / revisit:** Danielle tests a slow, reliable repair while a formerly frantic helper naps.
- **Art direction:** Brick and steel with restrained orange accents; loading aprons and readable curbs.
- **Node ownership:** H06; H06. These references
  describe proposed scene placement, not implementation status.

### 05 — Castro (castro)

- **Anchor:** Castro / Market corridor.
- **Composition:** Celebration plaza, compact storefronts, stage, sheltered rest garden.
- **Entrances / circulation:** Market arrival→public plaza; circuits are inspectable without entering the stage walls; north route via Duboce.
- **Adventure:** Restore light, stage power and a quiet rest area in a deliberate order.
- **Support:** Field clinic, storage and supplies.
- **Hidden discovery:** A poster changes after the celebration rather than spawning a mandatory fetch quest.
- **Afterward / revisit:** Celebration becomes a small recurring gathering with a visibly calm rest corner.
- **Art direction:** Bright flags and signs over neutral paving; avoid flooding the full map with saturated tiles.
- **Node ownership:** H04; C41. These references
  describe proposed scene placement, not implementation status.

### 06 — Haight-Ashbury (haight)

- **Anchor:** Haight street / parkward path.
- **Composition:** Flyer wall, record-shop pocket, tiny performance court, connected houses.
- **Entrances / circulation:** Duboce/Castro connector→south; correct flyer sequence points to court; west path leads toward Inner Sunset.
- **Adventure:** Reconstruct a performance's real timing from conflicting flyers.
- **Support:** Healing contact, shop and storage in compact service interior.
- **Hidden discovery:** A wrong flyer leads to a short optional conversation and returns to route.
- **Afterward / revisit:** The correct flyer gains a pencilled set time; the performer remembers the player's choice.
- **Art direction:** Muted painted façades, paper notices, trees, lamp posts; original pixel density.
- **Node ownership:** H03; H03, S11. These references
  describe proposed scene placement, not implementation status.

### 07 — Inner Sunset (inner_sunset)

- **Anchor:** Ninth / Irving / park edge.
- **Composition:** Greenhouse, three varied beds, small shopping block, park gate.
- **Entrances / circulation:** East approach→service block; greenhouse has visible front door; north gate enters Golden Gate Park route.
- **Adventure:** Read soil/light before restoring the beds.
- **Support:** Greenhouse rest point and ordinary storage/shop services nearby.
- **Hidden discovery:** Inspectable seed drawer hints at later starter access.
- **Afterward / revisit:** One unchosen starter source is unlocked after credits through a repeatable care task.
- **Art direction:** Leafy cool green, pale walls and gray walks; beds bordered rather than pasted on paving.
- **Node ownership:** H02; H02. These references
  describe proposed scene placement, not implementation status.

### 08 — Richmond District (richmond)

- **Anchor:** Geary / coastal route.
- **Composition:** Residential shops, archive room, Lands End path, Sutro tidal pocket.
- **Entrances / circulation:** Park approach→south; coastal path west; tide puzzle is contained and does not require real-time tide.
- **Adventure:** Compare archive clues with tide markers and find a fog-creature glimpse.
- **Support:** Archive-side healing/storage and supplies.
- **Hidden discovery:** A sourced Sutro plaque gives real history separately from relay notes.
- **Afterward / revisit:** Repaired tide refuge is one Bayveil observation site; no random hourly spawn.
- **Art direction:** Windy grass and stone borders, blue-gray coast; safe railings and short readable stairs.
- **Node ownership:** H11; P03. These references
  describe proposed scene placement, not implementation status.

### 09 — Tenderloin (tenderloin)

- **Anchor:** Community room / music block.
- **Composition:** Ordinary shops, rehearsal room, busy corner, supported community garden.
- **Entrances / circulation:** Signed central transit→wide sidewalk; musician clues through visible public doors; west connector to Fillmore.
- **Adventure:** Find the musician sheltering a stressed creature; restore a rest interval.
- **Support:** Community clinic, shop and storage.
- **Hidden discovery:** Optional altered descriptions reveal a cosmetic-note joke; main clue is available sober.
- **Afterward / revisit:** Rehearsal room now plays music with real pauses; musician offers optional cry-listening activity.
- **Art direction:** Dense occupied frontage, posters, lamps and planters; community life beyond the surreal branch.
- **Node ownership:** H08; S04. These references
  describe proposed scene placement, not implementation status.

### 10 — Fillmore (fillmore)

- **Anchor:** Fillmore music corridor.
- **Composition:** Ensemble rehearsal, three nearby instrument stops, small venue.
- **Entrances / circulation:** East approach from central connector; instruments remain on one readable loop; north/east Post route to Japantown.
- **Adventure:** Return instruments by their sounds, then demonstrate staggered rhythm.
- **Support:** Venue rest area plus supplies/storage.
- **Hidden discovery:** A quiet audience seat has an original callback rather than copied lyrics.
- **Afterward / revisit:** Hear the completed rehearsal; optional repeat challenge grants a modest capped reward.
- **Art direction:** Warm venue windows, music posters, ordinary curbs and seating.
- **Node ownership:** H09; H09. These references
  describe proposed scene placement, not implementation status.

### 11 — Japantown (japantown)

- **Anchor:** Post Street plaza route.
- **Composition:** Festival square, lantern shop pocket, quiet gallery, supply court.
- **Entrances / circulation:** Fillmore/Post entrance→plaza; gallery has an explicitly quiet side path; central transit reaches Transbay.
- **Adventure:** Distribute lantern and gallery supplies according to different needs.
- **Support:** Clinic/storage near square; ordinary shop access.
- **Hidden discovery:** A festival stamp appears in the Field Journal, not as a new mandatory badge.
- **Afterward / revisit:** A small fog companion returns to the quiet gallery; hosts remember leaving it unlit.
- **Art direction:** Lantern accents over restrained architecture and gray paving; no invented historic claims.
- **Node ownership:** H10; H10. These references
  describe proposed scene placement, not implementation status.

### 12 — Presidio (presidio)

- **Anchor:** Woodland route / Fort Point approach.
- **Composition:** Woodland fork, signal overlook, shelter, supervised Fort Point route.
- **Entrances / circulation:** Explicit west/north transit arrival; reflected signal branch loops back; east walk continues toward Marina.
- **Adventure:** Distinguish reflected signal from the source and protect habitat coordinates.
- **Support:** Ranger-style field rest kiosk with recurring researched cast, supplies/storage.
- **Hidden discovery:** An optional researched exposition plaque is separate from the fictional signal plot.
- **Afterward / revisit:** Shelter becomes the third quiet observation site; field notes redact exact animal locations.
- **Art direction:** Trees, muted stone, ocean edges, protective rails; avoid giant empty lawns.
- **Node ownership:** H12; H12. These references
  describe proposed scene placement, not implementation status.

### 13 — Marina (marina)

- **Anchor:** Chestnut Street / waterfront link.
- **Composition:** Dense mixed-use block, three fictional bars, laundry-tag clue, karaoke pocket.
- **Entrances / circulation:** Presidio side arrives west; three venues share a legible walkable block; east corridor approaches Russian Hill.
- **Adventure:** Recover the quarter-zip and its controller log using three concrete clues.
- **Support:** Rest/recovery, diner supplies and storage; sober route always works.
- **Hidden discovery:** Optional Jonathan date assistant and drink variants.
- **Afterward / revisit:** Jacket owner returns as a recurring joke; the karaoke monster remains a venue companion.
- **Art direction:** Warm storefront light, benches, street trees and compact upper floors.
- **Node ownership:** H13; M31, S03, S05, S06, S07, S08, S09. These references
  describe proposed scene placement, not implementation status.

### 14 — Russian Hill (russian_hill)

- **Anchor:** Cable-car / stairs route.
- **Composition:** Control shed, short cable-car segment, stair landings, overlook.
- **Entrances / circulation:** West connector climbs by visible stairs; control shed front door; north/east exit reaches North Beach.
- **Adventure:** Restore brake/wheel/signal acknowledgement order.
- **Support:** Service rest stop, storage, ordinary supplies.
- **Hidden discovery:** A sourced cable-car plaque accompanies the fictional machinery fault.
- **Afterward / revisit:** Cable-car shortcut operates; a repaired sign acknowledges waiting for confirmation.
- **Art direction:** Hills shown with consistent ledges/stairs and roof heights, not random elevation cuts.
- **Node ownership:** H14; H14. These references
  describe proposed scene placement, not implementation status.

### 15 — North Beach (north_beach)

- **Anchor:** Columbus / Bay Street branch.
- **Composition:** Notebook café pocket, parrot overlook, bookshop, office-route sign.
- **Entrances / circulation:** Russian Hill approach→overlook loop; Bay Street office branch goes to Cursor; south walk to Chinatown.
- **Adventure:** Order the notebook observations without mistaking repetition for importance.
- **Support:** Café healing contact, storage and supplies.
- **Hidden discovery:** Optional notebook marginalia changes after Roon publishes the redacted method.
- **Afterward / revisit:** Parrot repeats a new short line chosen from the player's earlier harmless response.
- **Art direction:** Warm stucco, outdoor seating, lamp posts and tight shopfronts.
- **Node ownership:** H15; H15. These references
  describe proposed scene placement, not implementation status.

### 16 — Chinatown (chinatown)

- **Anchor:** Community festival / downtown boundary.
- **Composition:** Festival square, supply passage, relay court, uplink access interior.
- **Entrances / circulation:** North Beach approach→public square; clearly separate Financial District branch; uplink entrance visible before finale.
- **Adventure:** Restore festival distribution; expose uplink; return after rehearsals for Launch Night.
- **Support:** Full pre-finale healing, storage, shop and safe save staging area.
- **Hidden discovery:** A repaired sign has a small Launch Night callback after credits.
- **Afterward / revisit:** Festival lighting shows different areas operating independently; a quiet corner remains quiet.
- **Art direction:** Lantern highlights, gray paving, distinct thresholds; community is affected by scheme, not cast as faction.
- **Node ownership:** H16; F01, P06, F02, P07. These references
  describe proposed scene placement, not implementation status.

## Route register

All routes below become bidirectional/free after their story unlock. Descriptions
name compressed corridors, not verified present-day bus lines or schedules.

| Route | From → to | Mode / visible connector | Adventure unlock |
| --- | --- | --- | --- |
| R01 | outer_sunset → soma | transit: Judah Muni → South Park walk | O04 |
| R02 | soma → mission | transit: South Park → signed Market/Mission transit connector | O09 |
| R03 | mission → dogpatch | transit: Mission → Third Street workshop connector | P01 |
| R04 | dogpatch → soma | transit: Third Street return to South Park | H06 |
| R05 | soma → castro | transit: Market corridor → Castro | G08 |
| R06 | castro → haight | walk: Duboce / parkward connector, intermediate blocks compressed | C41 |
| R07 | haight → inner_sunset | walk: Park-edge / Irving connector | G02 |
| R08 | inner_sunset → richmond | walk: Golden Gate Park crossing | H02 |
| R09 | richmond → tenderloin | transit: Geary cross-town connector | P03 |
| R10 | tenderloin → fillmore | walk: Central Geary / Fillmore connector | H08 |
| R11 | fillmore → japantown | walk: Fillmore / Post connector | H09 |
| R12 | japantown → presidio | transit: Return from central office trip to signed Presidio arrival | G05 |
| R13 | presidio → marina | walk: Eastern Presidio → Marina connector | H12 |
| R14 | marina → russian_hill | walk: Chestnut / hill approach; intermediate blocks compressed | M31 |
| R15 | russian_hill → north_beach | walk: Stair / Columbus connector | H14 |
| R16 | north_beach → chinatown | walk: Columbus / neighborhood boundary connector | P05 |

Office visits have a return option to their departure stop and a clearly marked
next main-route service. Side trips to central gyms need a visible travel menu;
no forced player recollection of unmarked transfers. Unlocking a destination does
not consume a one-time ticket or replace the way home.

## Office-route pockets and factual limits

Use the user's [Silicon Valley Map](https://www.siliconvalleymap.org/) for orientation,
not as redistributed company data or proof of current occupancy. Research checked
October 16, 2026. Primary company pages are preferred; dated local reporting is
identified. Registered addresses, leases and occupied spaces are not interchangeable.

### G01 — SoMa / South Park

- **Package / route parent:** office_cognition; soma.
- **Arrival:** Third Street block, facing the park-side approach. Available after O05.
- **Evidence:** 550 Third Street (reported occupied); do not treat the 333 Brannan expansion lease as already occupied.
- **Confidence / release gate:** Reported occupied, dated local reporting; company careers confirms SF office.
- **Sources:** [1](https://cognition.com/careers), [2](https://www.sfchronicle.com/realestate/article/new-sf-ai-startup-cognition-takes-cruise-s-office-22406725.php/).

### G08 — Market Street / Monadnock block

- **Package / route parent:** office_notion; soma.
- **Arrival:** Clearly signed Market office branch; do not label this block Inner Sunset or Mission. Available after P02.
- **Evidence:** 685 Market Street; local reporting describes the occupied move in 2025. Newer design coverage still describes Market Street.
- **Confidence / release gate:** Occupied historical reporting, consistent later coverage; not a live occupancy guarantee.
- **Sources:** [1](https://www.notion.com/about), [2](https://sfstandard.com/2025/06/08/notion-san-francisco-headquarters-market-street/), [3](https://www.fastcompany.com/91599202/notion-designed-its-new-hq-as-an-ode-to-classic-design).

### G02 — Central SF office connector — exact district provisional

- **Package / route parent:** office_midjourney; tenderloin.
- **Arrival:** Transit branch from Haight, returns to the same stop; district label is a release gate. Available after H03.
- **Evidence:** SF office confirmed by company careers. No occupied street address verified. The 300 Grant proposed spa is a future concept, not a verified current HQ.
- **Confidence / release gate:** SF confirmed; exact district UNVERIFIED. Interior can be assigned now; exterior/map anchor cannot be finalized.
- **Sources:** [1](https://www.midjourney.com/careers), [2](https://www.bizjournals.com/sanfrancisco/news/2026/06/17/midjourney-scanner-ai-wellness-spa-union-square.html).

### G05 — Transbay / Fremont Street

- **Package / route parent:** office_mercor; soma.
- **Arrival:** Signed Fremont office route reached by central transit; return ticket to Japantown/Presidio. Available after H10.
- **Evidence:** 181 Fremont Street is explicitly named Mercor HQ in company job listings.
- **Confidence / release gate:** Primary company careers evidence names HQ; exact interior is fictional.
- **Sources:** [1](https://www.mercor.com/careers/).

### G03 — Bay Street / North Beach waterfront branch

- **Package / route parent:** office_cursor; north_beach.
- **Arrival:** Bay Street office pocket north of the main notebook loop. Available after H15.
- **Evidence:** 295 Bay Street described as Cursor's home in May 2026 local property reporting; legal/mailing address can differ.
- **Confidence / release gate:** Dated occupied media report plus primary SF-careers confirmation; recheck before final release.
- **Sources:** [1](https://www.bizjournals.com/sanfrancisco/news/2026/05/26/helios-real-estate-cursor-295-bay.html), [2](https://prod.cursor.com/careers/startup-events-community).

### G04 — Financial District / Sansome — provisional occupancy

- **Package / route parent:** office_perplexity; chinatown.
- **Arrival:** Separate Sansome/Financial District route, reachable from the North Beach/Chinatown boundary; never relabel it Chinatown. Available after G03.
- **Evidence:** 115 Sansome Street is listed on the company-managed profile, but that alone is not proof of occupied current offices.
- **Confidence / release gate:** Listed address, occupancy UNVERIFIED. Keep the route anchor movable until corroborated.
- **Sources:** [1](https://uk.linkedin.com/company/perplexity-ai).

### G06 — SoMa / Howard Street corridor

- **Package / route parent:** office_anthropic; soma.
- **Arrival:** Howard Street office branch from the downtown transit hub. Available after H16.
- **Evidence:** 2025 principal-place filing lists 500 Howard; newer reports concern expansion leases. Use the supported corridor, not an unsupported assertion of a particular current door.
- **Confidence / release gate:** District supported; exact occupied release door remains research-gated.
- **Sources:** [1](https://search.sunbiz.org/Inquiry/CorporationSearch/GetDocument?aggregateId=forp-f24000001568-aa469358-d133-43d9-9fc6-3c7c00c42c1d&formatType=PDF&transactionId=f24000001568-2352ed70-b676-4832-86c6-008461d76534), [2](https://therealdeal.com/san-francisco/2026/04/02/anthropic-leases-more-office-space-in-san-francisco/).

### G07 — Mission Bay / Third Street corridor

- **Package / route parent:** office_openai; dogpatch.
- **Arrival:** Clearly labeled Mission Bay branch north of the Dogpatch workshop route; return transit to Chinatown. Available after P04.
- **Evidence:** 1455 Third Street is the registered office in the official privacy policy; a registered office alone is not current occupancy evidence.
- **Confidence / release gate:** Primary registered-address evidence supports proposed district, not physical occupancy. Verify release-door before final map art.
- **Sources:** [1](https://openai.com/policies/privacy-policy/).

## Dungeons, supporting areas and returns

- **Ocean Beach sensor pocket:** a short contained encounter loop off Sunset;
  visible return to Roon. Postgame fog refuge is a distinct small pocket off the
  same route, not an island outside SF.
- **Golden Gate Park crossing:** links Inner Sunset and Richmond. Three readable
  habitat zones; optional side paths reconnect. No arbitrary surf/cut HM grind is
  introduced by the story treatment.
- **Lands End / Sutro pocket:** observation/tide-marker puzzle uses in-game states,
  not real tides or real-time waiting. Return to Richmond services before battle.
- **Presidio / Fort Point:** woodland source-versus-reflection loop with a safe
  shelter and visible Marina exit. No route onto the Golden Gate Bridge beyond SF.
- **Chinatown uplink:** festival court → safe staging room → three isolation
  stations → confrontation platform → exit back to festival. Loss returns to the
  staging point; successful local repairs persist. The control room is fictional.
- **Ferry Building:** waterfront departure pocket reachable through the downtown
  connector; unlocked for championship after F02/P07 and all eight badges.
- **Treasure Island:** public arrival plaza with clinic/storage/shop, a commitment
  desk, four consecutive specialist rooms, champion room, credits exit and return
  ferry. The optional network-state exhibit has a separate door/return path.
  Never route via Oakland/Yerba Buena by pretending it is an ordinary SF street.
- **Bayveil quiet sites:** greenhouse shade, tidal refuge and Presidio shelter;
  inspect in any order after the ending. After all three, a deterministic fog
  trail opens at Ocean Beach. Retry and storage access remain available.

## Schematic map

[Open the city schematic](city-map.svg). Coordinates are illustrative, not GIS or
navigation directions. Solid lines denote compressed walking connectors; dashed
lines denote explicit transit. Office pockets are described above to avoid
plotting unverified current office locations as exact factual points.

## Historical hooks and boundaries

- [N-Judah opening](https://www.sfmta.com/blog/n-judah-turns-87): an existing apartment
  postcard refers to the October 21, 1928 launch and the Sunset Tunnel connection.
- [South Park](https://www.sfrecpark.org/576/South-Park): use the documented garden
  history for a plaque; the startup notebook and relay apparatus are invented.
- [Sutro Baths](https://www.nps.gov/goga/learn/historyculture/sutro-baths.htm): tidal
  engineering inspires the fictional puzzle; it does not establish our mythology.
- [1915 exposition](https://www.nps.gov/prsf/learn/historyculture/1915-panama-pacific-international-exposition.htm):
  a Presidio route plaque can connect eras without inventing secret real machinery.
- [Cable-car history](https://www.sfmta.com/getting-around/muni/cable-cars/cable-car-history):
  source the short Russian Hill plaque separately from the invented retry fault.

Final factual plaque prose still needs its exact source passages checked during
script editing. No actual location, bus timetable, office floor plan or historical
quote is copied into the game by this planning package.

