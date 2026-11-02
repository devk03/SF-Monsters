# Town visual evaluation

This evaluates screenshots of the actual game, not generated concept art or a
source map. It is a structured independent review, not an automatic art judge
or a substitute for the user's approval. The evaluator must look at the images
and give observable evidence; passing tests or increasing a metric cannot
establish that a town looks good.

## Evidence for each evaluation

- One complete native map image and at least three different actual player-scale
  views: arrival, main landmark/activity, and another street or trail. Include
  edges, approaches and interior views when the change affects them.
- The matching neighborhood ideal and, for changes, the matching earlier
  implementation. Label the ideal as a concept and any older image with its
  own version. Compare composition and character; do not demand literal pixels
  or impossible GBA-scale detail.
- Exact ROM SHA-256 and source/capture identifiers for each implementation
  image. Record image hashes; do not mix screenshots from different builds
  while claiming they represent one candidate. Full-map backgrounds may omit
  NPCs; note that limitation and use live views for street activity.
- A reviewer who did not implement the change, evidence tied to specific views,
  the three largest defects, and a concrete next change. Store extracted ROM
  art and native captures privately in `.tools`, not in Git or public hosting.

## Review dimensions

Score each dimension 0–4: 0 absent or broken; 1 major flaws dominate; 2 mixed,
recognizable but unfinished; 3 coherent and close with named limitations;
4 strong and consistent at actual scale. Scores are judgment, not measurements.
For nature and water areas, interpret buildings as landforms, structures and
natural edges. Do not reward filling a forest, beach or water with city blocks.

1. **Spatial composition and exploration.** Distinct connected blocks or
   organic nature areas, useful routes and focal points; avoid one flat frontage
   line, identical parallel strips, dead-end-looking routes and huge empty fields.
2. **Density and purposeful space.** City blocks have adjacent buildings and
   believable streets; parks, yards and waterfronts have deliberate uses. Flag
   oversized vacant lawns or pavement, but don't demand maximum coverage.
3. **Architecture, scale and joins.** Multiple recognizable building forms,
   complete exposed ends and seamless attached walls; coherent roof/side depth,
   ground contact and detail at the player camera. Flag cloned patterns, fake
   doors, clipped structures and mixed-resolution artwork.
4. **Ground, scenery and activity.** Readable sidewalks, curbs and crossings,
   varied purposeful plants/signs/fixtures and people. Check unnatural repeats,
   props as grids, ungrounded buildings, texture seams and color choices.
5. **Neighborhood identity.** At least one meaningful local landmark and
   believable land use should distinguish the area from other districts;
   examples include Mission murals, Marina waterfront and FiDi offices. A sign
   or color swap alone is not a distinct place.
6. **Player-scale readability and visual defects.** Inspect the actual camera
   for occlusion, clipped roofs, visual noise, misleading walkability and
   out-of-bounds borders such as trees across a bay. Full-map beauty alone is
   insufficient. Confirm graphical issues with runtime checks separately.

Every score needs a concrete reason referencing one or more supplied views.
Give the location or a pixel coordinate/crop for each major visible defect so
another reviewer can find it. Mark uncertainty or missing evidence explicitly.
The reviewer must compare the
whole town and the changed area; a better detail cannot hide a worse town.

## Decision and regression gates

Record **advance**, **revise** or **insufficient evidence**, plus whether the
candidate improves its baseline and any regression. An advance means the
reviewer recommends continuing with that candidate; it is not final approval.
Reject a candidate with a severe new visible regression (for example, clipped
building ends, a false shoreline behind homes, or a giant empty clearing), even
when averages improve. A completion recommendation requires every applicable
category at least 3/4, no unresolved major defect, actual gameplay evidence and
explicit user approval. Track unresolved findings across iterations instead of
resetting the score after each small fix.

Visual review does not prove collision, room entry, route connections, walking
animation, save recovery, web behavior or performance. Keep those checks as
separate evidence. Quantitative source-map or image diagnostics can flag areas
for inspection, but their thresholds must be calibrated against reviewed
examples; never present them as an objective aesthetic score.

## Run a structured review

Create a JSON manifest using the schema in
[`evaluate_town_visual.py`](../../scripts/quality/evaluate_town_visual.py).
The reviewer supplies the scores, screenshot references, localized defects,
comparison and uncertainties after visually inspecting the images. Then run:

```sh
python3 scripts/quality/evaluate_town_visual.py /path/to/review.json \
  --output .tools/benchmarks/my-review/report.html
```

The tool checks image hashes and declared ROM identities, required views,
review coverage and regression gates. It does not itself inspect aesthetics
or authenticate the declared capture provenance: check the original capture
session/receipt before entering those values. The HTML report stays local.
The historical v191 North Beach pilot is at
`.tools/benchmarks/town-visual-eval-pilot/north-beach-v191.html` when those
private captures are available; its scores do not describe later versions.
