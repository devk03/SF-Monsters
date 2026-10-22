# Neighborhood architecture and sidewalk contract

The October21 refinement requires at least eight structural building types in
**each of the13urban destinations**, with available paint variants. Paint,
end-cap aliases and repeated Victorian crops do not count as different types.
Nature destinations keep their park, coastal and island character; their
landscape refinement remains separate from the urban building count.

## Original native forms

| Form | Distinguishing architecture |
| --- | --- |
| Walkup | Three sash-window bays, stone belts, external fire escape |
| Shophouse | Narrow upper flats, striped awning, recessed shop entrance |
| Workshop | Steel loft windows, loading shutter, roof vent |
| Gable | Pitched roof, attic window, horizontal siding |
| Deco | Stepped parapet, vertical ribs, tall recessed glazing |
| Flats | Narrow residential frontage and sheltered porch |
| Arcade | Arched shop openings and a continuous sign band |
| Duplex | Paired entries, projecting window bays and central party wall |

Residential/cultural streets also use the original Victorian bay house. The
structural mix favors cottages and duplexes in the Sunset/Noe Valley, commercial
arcades in North Beach/Castro, and workshops or office forms in industrial/civic
areas. The independent gate counts families actually stamped in each map.
Special service buildings and reserved gym fronts keep their explicit door
contracts; their paint does not needlessly allocate unused variant records.

## District treatment

| District | Street character and paint emphasis | Sidewalk |
| --- | --- | --- |
| Dogpatch | Rust brick, working lofts, recycling/loading furniture | Concrete slabs / dark thresholds |
| Potrero Hill | Warm hill homes, slate accents, stair overlook | Concrete slabs / stone thresholds |
| Mission | Warm mixed-use fronts, mural, planted shop edges | Brick bonds / dark thresholds |
| Castro | Rose/cream commercial fronts, theater, flower boxes | Stone panels / brick thresholds |
| Outer Sunset | Slate and warm cottages, surf shop, seawall | Neutral concrete promenade |
| Marina | Slate/warm flats, planted bar frontage and curb sign | Concrete slabs / stone thresholds |
| Pacific Heights | Warm formal homes, mansion, lavender/shrubs | Stone panels / dark thresholds |
| Noe Valley | Sage/warm residential shops, book box, gardens | Concrete slabs / brick thresholds |
| Mission Bay | Cool white civic fronts, lab/clinic and tree wells | Stone panels / concrete thresholds |
| Giants Stadium | Rust/cream commercial blocks and bike parking | Brick bonds / dark thresholds |
| Financial District | White/gray office fronts and granite entries | Dark stone / lighter thresholds |
| North Beach | Warm cafe/arcade fronts, theater and planters | Brick bonds / stone thresholds |
| Treasure Island | Industrial rust/concrete fronts and utility edge | Concrete slabs / dark thresholds |

Warm, sage and slate variants share graphic tiles. Industrial/civic kits use
base material plus sage; other urban kits offer all three. Each district's paint
balance varies while roofs, glass and neutral pavement remain coordinated.
Residents retain their dialogue, local IDs and quest ownership; sprite ordering
varies by destination so every block does not restage the same cast.

## Geometry and release checks

- Keep32×24maps, at least48declared frontage cells, complete exposed building
  ends, stable gym entrances and the actual service door at[5,8].
- Maintain a continuous pedestrian route across both sidewalks without entering
  the road or an automatic doorway. Check all ambient NPC movement ranges,
  not only their initial positions. The Sunset starts at its seawall edge.
- Place south furniture along the curb, keeping the inner sidewalk open. Preserve
  local-activity objects and their standing positions when rearranging fixtures.
- Pack at most512secondary graphic tiles and512metatile records per kit. Include
  foreign connection margins in the final budget; unused recolors cannot crowd
  out real neighboring architecture.
- Run local world checks, compiled-resource audits, actual older ordinary Save
  loading, all58-map native traversal, full WASM replay and native screenshot
  tours from both ends of each urban block. Check changed signs/activities.
- Browser smoke tests and counts do not prove complete route performance or
  human visual acceptance. Publish only after the relevant release gates pass.

Source: `world_architecture.py`, `world_tiles.py`, `world_towns.py` and the
independent `world_street_contract.py`; allocations live in
`romhack/world/art-contract.json`. Progress/evidence remains authoritative in
`docs/game-spec.md` section15.1. Gym interiors remain contributor-owned.
