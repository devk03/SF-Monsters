# Expanded concepts → playable world

The October 24 request authorizes implementing the expanded concepts. It does
not approve the resulting art. The objective and current evidence remain in
[game-spec.md §15.1](../game-spec.md#151-objective-and-completion-rule).

All locations below use native metatile coordinates in a 96×64 destination.
The northwest service/gym bindings remain stable. Routes are compressed walking
corridors rather than literal claims about adjacent SF blocks. Both islands and
the separate Presidio destination remain in scope; the gym count stays eight.

## District translation ledger

Every row is an implementation candidate. None has human visual acceptance.
“Source” describes authored geometry, not evidence of correct native rendering.

| District / expanded reference | Source composition now | Material gap before a close match |
| --- | --- | --- |
| [Dogpatch](../../output/imagegen/neighborhood-ideals-v2-expanded/dogpatch.png) | Native v132 adds five original sawtooth-roof factory plots, a workshop/garage working block and retained planted court; existing quay/pier/service approaches remain. Native frontage, court, old-Save, all-boundary and full-world replay checks pass. | Stronger rail-yard/drydock details and believable warehouse massing; inspect new facade depth in gameplay. |
| [Potrero Hill](../../output/imagegen/neighborhood-ideals-v2-expanded/potrero-hill.png) | Offset hill streets through `(40,26)/(76,46)`, short terrace housing, library and two reserved native stair courts. | Native v123 stairs work, but short rock faces still read as barriers. The larger residential slope and retaining-wall massing need refinement. |
| [Mission](../../output/imagegen/neighborhood-ideals-v2-expanded/mission.png) | Mural/studio court `(42,17)`, market/music block envelopes, community garden `(66,37)..(82,48)`, connected mixed-use streets. Inland. | Distinct taqueria, bakery and venue fronts; more legible mural-alley destination sequence. |
| [Castro](../../output/imagegen/neighborhood-ideals-v2-expanded/castro.png) | Existing theater/gym approach, branching cafe blocks and planted cut-throughs, short hillside mews. | A designed theater gathering space, restrained rainbow details and independent shop signs. |
| [Outer Sunset](../../output/imagegen/neighborhood-ideals-v2-expanded/outer-sunset.png) | Parallel residential streets, western ocean edge, surf-shop details and short cottage courts. | Dune transition, low coastal planting and quieter roof/lot rhythm need dedicated native review. |
| [Golden Gate Park](../../output/imagegen/neighborhood-ideals-v2-expanded/golden-gate-park.png) | Native v130 combines the two-lobed lake with12attached Richmond-edge homes/shops, all eight forms and two residents. All60new frontage cells,12front collisions, both park links, conversations and four boundary-pair audits pass. | Garden/conservatory staging, rigid forest borders and the small, simple Richmond mews still limit the concept match. Facade doors remain scenery; complete district quality and human acceptance are open. |
| [Marina](../../output/imagegen/neighborhood-ideals-v2-expanded/marina.png) | Native v129 has eleven attached venue fronts, central/eastern harbor approaches and eight existing props, with the original bar service door preserved. Actual views/full-map,11front collision pushes, harbor walks, bar return and three boundary-pair audits pass. | Awning repetition, oversized roads and thin waterfront space still limit the match. Boats, docks, palms, patios and clubhouse architecture remain absent; new fronts are scenery. |
| [Pacific Heights](../../output/imagegen/neighborhood-ideals-v2-expanded/pacific-heights.png) | Existing mansion approach, offset ridge streets, formal-home plots and upper courtyard mews. | Formal gardens and readable terrain height; avoid a generic pastel residential grid. |
| [Twin Peaks](../../output/imagegen/neighborhood-ideals-v2-expanded/twin-peaks.png) | Native v135 retains two stair-stack outlooks and17attached homes, with quieter shared lanes, curb/sidewalks, grass shoulders and native-earth western trail. All94frontage walks,17wall pushes, both residents, marked actor-side passage, prior Save and three boundary-pair audits pass. | Rock rims still fail to form convincing hill masses; oversized slab paving and rigid forest borders need refinement. Whole-map quality and human approval remain open. |
| [Noe Valley](../../output/imagegen/neighborhood-ideals-v2-expanded/noe-valley.png) | Repair cafe/book box, family-home and bakery block envelopes, quiet domestic lanes and planted passages. | Playground/garden destination and small independent shop differentiation. |
| [Mission Bay](../../output/imagegen/neighborhood-ideals-v2-expanded/mission-bay.png) | Eastern/southern waterfront, research tower court `(64,17)..(76,28)`, clinic/cafe services and quay spur. | Modern lab architecture still relies on a small existing tower asset; creek and campus identity need richer massing. |
| [Ballpark](../../output/imagegen/neighborhood-ideals-v2-expanded/giants-stadium.png) | Existing stadium gate, field/fan walk `(52,33)..(80,46)`, sand diamond and eastern waterfront. | A full stadium shell, bleachers and recognizable fan plaza are not implemented. The field is a playable public-space candidate. |
| [Financial District](../../output/imagegen/neighborhood-ideals-v2-expanded/financial-district.png) | Office/lunch court `(40,17)..(56,28)`, denser commercial blocks, eastern bay edge; v123 corrects straight window-storey repetition. Broader office/lab aliases are a later source candidate. | Tall varied office canyon and landmark silhouettes still need more than repeated narrow towers. Inspect broader blocks in a new native build. |
| [North Beach](../../output/imagegen/neighborhood-ideals-v2-expanded/north-beach.png) | Composed cafe/bookshop forecourt `(72,17)`, short alley/shop blocks and tighter eastern hill mews. | Italianate landmark/venue variety, hill transitions and destination signage. |
| [Treasure Island](../../output/imagegen/neighborhood-ideals-v2-expanded/treasure-island.png) | Shore around expanded island, former-barracks/workshop plots, community room and eastern quay spur. | Dedicated ferry terminal, industrial-yard composition and island-scale views. |
| [Lands End](../../output/imagegen/neighborhood-ideals-v2-expanded/lands-end.png) | Western coast, bath-ruins landmark, branching forest trail, two native cliff/stair candidates. | Irregular coves and a larger integrated ruins/cliff composition. |
| [Sutro Tower](../../output/imagegen/neighborhood-ideals-v2-expanded/sutro-tower.png) | Existing tower, narrow native forest, winding ridge branches and two cliff/stair candidates. | Better exposed summit clearing, tower setting and fog/ridge vegetation balance. |
| [Angel Island](../../output/imagegen/neighborhood-ideals-v2-expanded/angel-island.png) | Island coasts, switchbacks, landing/rest stops, native cliff/stair candidates and protected League approach. | Distinct ferry landing and actual summit/League architecture; the existing League landmark is a placeholder. |
| [Presidio / Presidio Heights](../../output/imagegen/neighborhood-ideals-v2-expanded/presidio.png) | Wooded campus/residential hybrid, hall/common `(44,1)`, visitor notice, pedestrian connector, local discovery, eight residents and two optional greenways. | The hall/common is reachable and inspected in native v123, but remains flat/sparse; stair gardens, overlooks and a stronger campus setting need work. |

## Evidence required for each district

1. Deterministic source generation; independent collision, frontage, NPC and
   progression checks, including every new approach and return path.
2. Compiled native tile, palette, metatile and padded-map-buffer budgets; exact
   boundary rendering in both directions. Own facade art and foreign margins
   share allocations without replacing native terrain or animation slots.
3. Actual controller-driven entry, intersection, landmark, secondary cluster and
   optional-branch views, plus a complete live-native background map. A source
   rendering is useful for composition review but does not satisfy this gate.
4. Earlier ordinary Save cold Continue, including positions made invalid by new
   shores/blocks; preserve party, items, money, chapter and contributor state.
5. Matching website-core replay and foreground browser checks before publication.
   Public v80/v92 stay available until the private candidate passes release gates.
6. Reference/native pairs presented for human critique. Neither passing tests nor
   finishing a collection of screenshots grants aesthetic approval.

## Working sources

- `world_district_layouts.py`: real street/trail circulation and route approaches.
- `world_concept_blocks.py`: finite district block envelopes and service lanes.
- `world_concept_places.py`: reserved field, garden, office and research courts.
- `world_native_parks.py`, `world_concept_terraces.py`, `world_park_water.py`:
  complete native forest groups, ridge/stair candidates and joined pond banks.
- `world_town_relief.py`: Potrero retaining courts, stairs and safe street landings.
- `world_presidio_campus.py`, `world_presidio.py`: reserved hall/common, visitor
  notice and campus/residential transition into protected native forest.
- `world_rich_facades.py`, `world_shared_primary.py`: richer original SF facade
  candidate and explicit native allocation planning; integration is in progress.

No full ROMs, extracted proprietary art, private Saves or native captures belong
in the public repository. Local checks are routine; Actions remains manual-only.
