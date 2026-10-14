# Roon fictional field-atlas draft

Generated 2026-10-14 with built-in image_gen, transparent_background=true. Fictional anonymous courier-oracle costume and role; private appearance, identity, likeness, and biography are not asserted. No copied avatar or logo. Human approval remains pending.

## Reference

assets/characters/cognition-cast/scott-wu/source.png was provided only as a style/layout reference. Main owns native conversion, palette cleanup, registry integration and approval.

## Generation prompt

Use case: stylized-concept.
Asset type: original handheld top-down RPG field character sprite atlas, three columns by three rows.
Generate a fictional anonymous game depiction called Roon, an adult chibi courier-oracle. This is a fictional costume and role, with no claim to any real private appearance, identity, biography, or likeness. Sunny amber/orange hooded rain jacket with hood UP, navy trousers, brown shoes. Very simple face mostly shaded beneath hood. No copied avatar or logo.
Input image 1 is STYLE AND LAYOUT reference only: match its nine-frame layout and original handheld pixel-cluster proportions; do not copy Scott's hair, face, clothing, or character.
EXACTLY nine distinct figures in EXACTLY 3 columns and 3 rows, equally spaced, generous completely transparent gutters. Row1 SOUTH facing: idle, left-foot-forward stride, right-foot-forward stride. Row2 NORTH facing: idle, left-foot-forward stride, right-foot-forward stride, NO FACE on back of hood. Row3 WEST facing left: idle, left-foot-forward stride, right-foot-forward stride, at most one tiny eye in the hood's shadow. East is produced later by mirroring; do not include east poses. No extra frames, no labels, no text.
Native target is16x32 pixels per frame, roughly14x24 visible pixels and feet baseline30. Present enlarged nearest-neighbor pixels with crisp square hard clusters, dark clean outlines, limited shared palette of amber/orange highlights and shadows, navy, brown, warm skin and near-black. Keep adult-chibi head/body proportions appropriate for native Emerald-tier overworld. All nine figures identical scale, hood outline, costume details, and foot baseline. Both stride columns MUST clearly alternate which boot and opposite arm advance; WEST strides MUST be distinct opposite-phase poses. No blur, gradients, antialias, noise, material texture, ground shadow, scene, props, watermark or background. True transparent alpha everywhere between silhouettes.

## Targeted revision prompt

Revise this original fictional amber-hooded courier-oracle sprite atlas. Preserve exactly 3 columns ×3 rows, same scale, costume, palette and south/north/west row order. Critical correction: BOTTOM ROW third figure must have the opposite walk phase from bottom row middle: exchange which boot extends LEFT toward travel and which boot trails RIGHT, and exchange opposite arm forward/back. Make that difference unmistakable, with one arm on each side of torso instead of copying middle frame. Also row1 right stride should exchange the advancing arm relative to row1 middle. Keep frame silhouettes consistently centered, feet baselines aligned within each row. Shade most of visible face beneath the hood, leaving simple tiny eyes, retaining fiction/no likeness. True clean transparent background, remove all colored background haze/glow/shadow entirely. Crisp hard square pixel clusters, limited palette, no soft edges, no text, no extra objects. This remains a draft for native16x32 conversion; don't include any grid or labels.

## Inspection and limitations

Selected second generated result, copied without pixel changes to source.png. RGBA 1024×1536, exactly three columns × three rows with generous separated silhouettes. Rows are south, north (no face), west; columns idle, first stride, second stride. Alpha ranges 0–254: 999,962 fully transparent pixels, 52,637 pixels alpha1–31, 5,675 alpha32–127, 514,590 alpha128–254; no fully opaque255 pixels. Tested gutter coordinates (341,512), (512,512), (341,1024) have alpha0. This is not binary/palette-ready transparency; low-alpha edge haze needs conversion review.

Visible issues: south and north boots alternate. West stride arms differ after revision, but both stride leg silhouettes still read similarly and need manual opposite-phase cleanup. The face remains more exposed than the mostly shaded request. Source uses enlarged soft/antialiased pixel edges and more colors than the final native palette. Feet baselines are close rather than exact. These are declared draft limitations, not game-ready acceptance. No conversion, code integration, build, browser use or publication performed here.

First attempt preserved at ignored .tools/roon-atlas-generation/attempt-01.png. Selected generated original remains under /Users/devkunjadia/.codex/generated_images/01a13900-5c2c-7973-bea7-389deda8a5ab/exec-699a558e-f214-4b38-a39e-0eecb36e9d61.png.

SHA256 source.png: 360a74014041d011511fc9cacc8f760a329fce15c7ff76289688c16cdfd79cf5


## Native conversion checkpoint

The threshold128 conversion now produces binary native transparency and a shared
RGB5 palette (15 opaque slots,14 distinct colors). The separately reviewed
`native-cleanup.json` applies18 indexed-pixel corrections to frame8's lower legs
only. Source PNG stays unchanged. All9 native poses remain distinct; east uses
the engine's horizontal flip. The fictional depiction and native art/animation
remain unapproved; in-game build/interaction/save evidence is recorded in the
canonical spec rather than inferred from this gallery.
