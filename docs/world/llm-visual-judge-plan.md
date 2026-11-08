# Visual judge: development focus

The next development focus is a reliable LLM judge for town and route quality.
It must look at the rendered game, identify the most consequential visual
problems, and improve its agreement with the user's preferences through
measured calibration. The current `evaluate_town_visual.py` validates a human or
agent review; it does not call an LLM or automatically inspect images.

## Inputs and output

Each case needs a native full map, at least three real player-scale views,
matching neighborhood concept, versioned ROM/capture receipts, and a matched
prior candidate when assessing a change. Include native Emerald comparison
captures locally only when available and relevant; distinguish them from the
aspirational SF concept, which may have non-GBA detail or projection. For
routes and parks, substitute landscape-specific composition criteria rather
than urban density. Label which full maps omit actors.

The judge should emit the six dimensions from `town-visual-evaluation.md`,
localized observations tied to image IDs and coordinates, three prioritized
fixes, a candidate-vs-baseline decision and explicit uncertainties. It must
flag severe regressions even when an average score rises. It must not infer
walkability, collision, meaningful interactions, audio or user approval from a
screenshot. Evidence identity and provenance must be validated separately.

## Calibration and evaluation

1. Build a versioned, private dataset of actual screenshots and user feedback,
   including accepted and rejected comparisons, as well as known failures:
   shallow repeated blocks, visible clipped ends, tiny false doors, oversized
   lawns/paving, checkerboard trees, boxed-in water, sparse city detail, and
   different requirements for natural spaces. Record the scope of each user
   comment and keep unresolved or unscored cases unlabeled.
2. Split by neighborhood and visual family, with unseen builds held out; do
   not put crops from the same map or variant in both tuning and test sets.
   Preserve the user's existing approvals and distinctions such as Angel
   Island's forest. Balance good/bad pairs and avoid labeling a candidate as
   globally good merely because one feature improved.
3. Measure agreement with user labels on held-out pairs (win/loss/tie),
   per-dimension rating error, critical-defect recall and false positives,
   location/evidence accuracy, and abstention on missing or ambiguous inputs.
   Report counts, uncertainty and breakdowns by urban, nature, waterfront
   and routes. Establish targets after measuring a representative baseline;
   do not claim thresholds or quality that have not been measured.
4. Evaluate robustness to screenshot scaling, harmless color changes, image
   order, omitted evidence, and swapped before/after labels. Compare with a
   simple baseline and with a fresh independent visual reviewer. Keep
   user-supplied feedback as the authority for aesthetic acceptance.
5. Iterate prompts/model settings on the training split only, freeze a version
   before the holdout run, record exact model, prompt, input hashes, labels,
   outputs and costs, and inspect disagreements. Repeat after new user
   feedback without silently changing or retroactively relabeling results.

## Delivery gates

A first implementation should read the existing structured evidence manifest,
run an explicitly configured vision model on the actual images, produce the
same validated output schema, and save reproducible request/response receipts.
It must fail closed on missing images or inconsistent versions; no API key or
private source images belong in the repository. Costs, image transmission and
model/provider settings should be explicit. Use local tests for schema and
failure cases, and a bounded real-image evaluation for model behavior. Until
calibrated against user feedback, judge scores are experimental triage, not a
release gate or a substitute for human approval. Report the evaluation and
remaining failure modes before applying the judge to changes automatically.
