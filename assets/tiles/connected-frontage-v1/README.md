# Connected frontage experiment

Private visual prototype responding to the user's rejection of v76 buildings.
This folder is original art, not an accepted game release or quality reference.

Candidate A is the first built-in imagegen connected-block source. Candidate B
is its built-in refinement; the exact refinement prompt is preserved separately.
Candidate A's design brief: one original coral/brick/cream/lilac SF block, overhead
roof depth, shared party walls, consistent native door/window modules, attached
entry steps and neutral-gray approach, no detached rails, no commercial sprites.
The exact first tool prompt is now preserved in prompt-candidate-a.md; the
brief above is a summary rather than a replacement for that transcript.

Generated source files are unchanged copies from the built-in imagegen outputs:

- A: exec-a6510d77-d613-48a6-ad92-1fafcb45d1e0.png
- B: exec-13e72dc3-a83c-435a-a54a-960354ef0fc2.png

`scripts/romhack/connected_frontage.py` converts B as one connected scene to
176×80 indexed pixels, one curated 15-color RGB555 palette plus transparent entry0.
The top64 pixels remain inside the existing blocked frontage. The bottom16
are transparent so the native fine-grid gray sidewalk supplies the approach.
An actual first native preview exposed a mismatched generated pavement panel;
that candidate remains privately preserved. The source geometry did not exactly
obey the requested height budget, so the converter records its architecture crop.
Conversion does not establish native game integration or visual acceptance.

Known candidate limitations: The first automatic 15-color reduction lost plant
color; the curated palette preserves one foliage color but remains unapproved.
Door proportions, subdued materials, roof scale and surrounding coherence still
need review in the actual game. Generated source paving is excluded because its
strong bottom edge and different joints did not match the surrounding fine grid. Do not call these problems solved based on the
standalone illustration or source checks.

Public v76 and the normal producer/auditors remain unchanged by this experiment.
Any experimental cartridge and reference screenshots stay private under .tools.

Human feedback: the user explicitly rejected source-candidate-a.png as "too much
detail". It is retained solely as provenance for the simpler derived candidates,
not as a visual target. Prioritize flat colors, broad windows and restrained trim
at native GBA scale. The later actual street candidate was called "Closer; keep
refining this style"; that is direction feedback, not a domain quality approval.
