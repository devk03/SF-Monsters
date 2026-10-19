# Private connection rendering experiment

Status: opt-in native experiment, not published or human-approved. Normal builds
leave it disabled. Public v92 remains the separate map-only release.

## Problem and implementation

Stock seamless connections assume compatible secondary tile allocations. SF
profiles do not share those allocations. The engine copied foreign numeric
metatile IDs into connection margins, carried cached map-view IDs across the
crossing, replaced secondary graphics/palettes, and refreshed only incoming screen
slices. Native and WASM could therefore agree on the same visibly corrupt scene.

`world_seams.py` generates a faithful atlas for every connected outdoor map:

- Foreign margin cells retain their real architecture and terrain. Their source
  records are translated into host-compatible records, preserving exact RGB555
  pixels, transparency, reflection, layer and behavior. Collision/elevation bits
  remain unchanged. Native primary water and Waterfall IDs remain unchanged.
- Extra graphics occupy unused primary VRAM tiles. The generator reserves all
  primary graphics actually used by the world, tiles0–15, implicit background
  tile20, the complete primary animation range432–511, and door scratch space.
  Maximum usage is406 of413 spare
  slots. Current secondary graphics remain unchanged in their original bank.
- Exact per-quadrant colors are packed into unused palette entries. Banks needed
  by the current map and actual foreign margins, plus UI banks14/15, are unavailable.
  Primary palettes are restored before each connection's atlas palettes are
  applied, so reuse on one map cannot leak into the next map's terrain.
  Implicit NORMAL-layer background word0x3014 retains its tile and all used
  palette3 entries; only its unused color entries may be reused. Palette0 is used
  only after verifying that the primary terrain addresses transparent tile0 there;
  its backdrop entry0 remains unchanged. Palette13 requires the guide's existing
  save/restore on both exit paths. No approximate recoloring is performed.
- Current-map cells come from their authored layout after each connection;
  old-profile `MoveMapViewToBackup` copying is skipped. The complete viewport is
  rebuilt after the tile-offset update, retaining the exiting partial row/column
  while its pixel scroll catches up. Same-profile connections are also checked.
- Connection loads defer new graphics, palettes and tilemap DMA requests until
  the complete scene and camera offsets are ready. A raw, frozen copy of each
  secondary graphics bank avoids the stock multi-frame decompression task. The
  requests are queued together without an intervening VBlank interrupt. Native
  animation-frame checks verify either the unchanged coherent source scene or
  the complete destination scene, never a mixture.

The implementation changes no authored footprints, source map cells, connections,
warps, service/gym bindings, source art or contributor packages. Capacity overflow
fails the build rather than substituting scenery. The current palette commit is
restricted to the authored sunny-weather maps; other weather requires review.

## Build and provenance

```sh
.tools/venv/bin/python -B scripts/romhack/build_world.py \
  --engine .tools/pokeemerald-seam-host --connection-atlas
```

`--connection-atlas` defaults off. The build freezes its boolean in
`build-mode.json`, records `experimental_connection_atlas` in the receipt, and
freezes the generated engine header plus `connection-atlas.json` capacity and
reservation evidence. A different `--engine` keeps ordinary engine QA isolated.
Do not stage this experiment as a normal preview without a separate review.

Validated private target:
`a421b0f8b768be4172b9c9f43e3da070f7886179f5a68e395bb1e0d0c3ce1876`.
Its immutable build receipt is under
`.tools/romhack-drafts/0.0.92-neighborhood-world-draft/<target>/receipts/`.
The normal source/compiled map audit and exact BPS roundtrip pass.

## Verification and limits

Four unit cases reconstruct every foreign margin quadrant independently from
the generated records and transferred graphics/palettes, compare it with the
source art, enforce allocation limits, and reject exhausted capacity. They pass
normally and with Python optimization enabled.

`scripts/quality/verify_world_seams.py` starts from an actual v88 ordinary battery
Save and uses the native Continue path. Before walking, all600 live party bytes
match that Save exactly. It then checks live current-map cells, foreign margin
collision/attributes, exact foreign pixels from linked ROM art versus VRAM,
reserved primary terrain/water colors, and the actual visible BG tilemaps.

Evidence for the private target:

- `town-seam-reserved-all-0`, `-8`, `-16`, `-24` and
  `town-seam-reserved-all-32`:38 walk-only trials cover all76 directed
  connections and37 outdoor maps, with228 edge/inward stages. Each trial walks
  both ways and into the destination without intervening rooms, menus, warps or
  Continue. The native controller's200,000-frame ceiling requires bounded groups.
- `town-seam-reserved-transient`: six trial pairs inspect all four movement
  directions, both sides and192 animation frames, including the largest atlas.
  Source scenes may remain frozen while loading, but must remain coherent until
  the complete new scene appears. Actual partially visible edge tiles are checked.
- `town-seam-reserved-water`: actual Surf entry/exit and native Waterfall
  ascent are exercised. Water/fall IDs, behavior and colors remain intact.
- Protected party fields, held items, money, inventory, flags, chapter state and
  Flash are checked. Ordinary walking can increase friendship: its encrypted-data
  checksum is validated, all other party fields must match, and friendship changes
  are bounded by actual native step counts. This is not a claim that walking
  leaves all600 party bytes unchanged.
- `town-seam-reserved-guide`: a separate post-trial SF Map interaction restores both
  palette13 buffers and the complete field view on a map using that atlas bank.

Each final proof freezes the verifier, read-only helper dependencies and manifest,
alongside the controller trace and exact ROM/ELF/battery identities. No host capture
ABI or public runtime was changed.

Run a bounded group with:

```sh
.tools/venv/bin/python -B scripts/quality/verify_world_seams.py \
  --engine .tools/pokeemerald-seam-host \
  --battery .tools/benchmarks/town-v88-noe-preview-save/saved.sav \
  --name unique-private-proof --group all --start-trial 0 --trial-count 8
```

Earlier failures remain private and preserved: unmodified v91 fails the foreign
graphics check; the first atlas target85bd563f passed settled checks but exposed a
multi-frame graphics transfer; target09954909 exposed the graphics/tilemap timing
gap. The first unpartitioned all-connections attempt hit the harness frame ceiling.
Target1da8f043 passed those native checks but was superseded after the final
reservation audit identified the implicit NORMAL-layer background tile20 and
palette3 entries. Its evidence is retained separately. None of these earlier
candidates is the final accepted experiment or a world-quality acceptance receipt.

Remaining gates include maintainer review, integration with the selected release,
the full58-map room/gym/service/save regressions on that integrated ROM, matching
native/WASM replay, actual browser play/performance and human visual acceptance.
No full-world quality or browser traversal gate is closed by this experiment.
