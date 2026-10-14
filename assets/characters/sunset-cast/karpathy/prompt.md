# Karpathy fictional field-atlas draft

Created 2026-10-14 with built-in image_gen: one generation and one targeted revision, transparent_background=true. Original fictional adult-chibi game costume for SF_Karpathy; no claim of real/private appearance, biography or literal likeness. Human quality approval pending.

## Reference and ownership

Original Scott sheet assets/characters/cognition-cast/scott-wu/source.png was used solely for style/layout/proportions. No public biography research or copied avatar. Main owns palette curation, native16×32 conversion, cleanup, registry and code integration. Existing Roon/Sunset palette and frame assets were not touched.

## Generation prompt

Use case: stylized-concept.
Asset: ORIGINAL adult-chibi handheld top-down RPG field sprite atlas, EXACTLY3columns×3rows, nine separate sprites. Fictional game costume for named character Andrej Karpathy; no claim of real/private appearance, biography or literal likeness.
Reference image1 is ONLY original Scott sheet STYLE/layout/proportions reference. Create a distinct original character, do not copy Scott's face, hair, hoodie or shoes.
Character in all nine frames: adult chibi, SHORT tidy dark hair with cropped sides and a modest irregular top (not long fringe covering face), natural light warm face, plain NAVY CREWNECK SWEATER(no zip, no hood, no logo), dark charcoal trousers, OFF-WHITE SNEAKERS with small gray sole. Neutral approachable simple tiny face. No labcoat, laptop, props, hat, copied avatar or text.
Grid: exactly3equally spaced columns by3rows with generous fully transparent gutters. Row1 SOUTH facing: idle, left-foot-forward, right-foot-forward. Row2 NORTH facing: idle, left-foot-forward, right-foot-forward; back of head no face. Row3 WEST facingLEFT: idle, left-foot-forward, right-foot-forward; one eye profile. EAST is later a native horizontal flip; never include extra east row.
Animation phase is crucial: columns2and3 MUST be opposite foot and arm phases, not copies. SOUTH middle lowers screen-left sneaker and raises screen-right sneaker; SOUTH right lowers screen-right sneaker and raises screen-left sneaker, opposite arm swing. NORTH likewise opposite feet and arms. WEST middle: near leg extends left, far leg trails right; WEST right: near leg trails right, far leg extends left, and arms swap forward/back. Make west second stride’s lowest visible sneaker on the opposite side from first stride so silhouettes remain distinct when reduced.
Style: native16×32 frame target, about14×24 visible pixels, consistent feet baseline30; Emerald-tier adult chibi proportions, approximately half-height head. Show enlarged nearest-neighbor square pixels, crisp hard clusters, clean near-black outlines, few solid shared navy/charcoal/skin/offwhite palette colors. Consistent size/head/torso/costume in all nine. No gradients, antialiasing, blur, texturednoise, ground shadows, background, glow, text, gridlines, labels or watermark. Actual transparent alpha everywhere between silhouettes. Keep all nine fully within their isolated cells.

## Single targeted revision

Correct ONLY the opposite walk phases in this fictional character atlas. Preserve original nine-frame3×3layout, shortdarkhair, face, navycrewneck sweater, darktrousers, offwhite sneakers, scale, head/torso identity and transparent background.
The top row middle and right currently repeat the same leading foot. CHANGE TOP-RIGHT figure's body below neck to the HORIZONTAL MIRROR of TOP-MIDDLE body: top-right lowest sneaker MUST be on viewerLEFT, opposite top-middle lowest sneaker on viewerRIGHT, and top-right raised/far sneaker on viewerRIGHT; top-right viewerRIGHT arm bends forward, viewerLEFT arm hangs back. Keep SOUTH face/head unmirrored.
The bottom row middle and right also repeat. CHANGE BOTTOM-RIGHT lower legs so its LOWEST sneaker is on viewerRIGHT, and viewerLEFT shoe is one nativepixel ABOVE baseline, opposite bottom-middle whose lowest sneaker is on viewerLEFT. On bottom-right, viewerLEFT/front hand hangs lower/down by hip, and viewerRIGHT/rear arm swings back visibly. Keep face/body WEST facingLEFT and preserve head; do not mirror the full character into east.
Middle NORTH row already alternates feet; keep those three poses unchanged. All idle frames unchanged. Both stride phases should remain obviously different even at16×32 native size. Crisp hard square pixel clusters, no gradients/antialias/noise. Clean actual alpha0 transparent gutters, no haze, no background/shadows/labels/text. No extra figures.

## Selected source and inspection

Source SHA256: a60e087653530020fd75052419432d805497d92bac2f9be9b3e8df176f97d940

Selected second result, copied without pixel changes. RGBA1024×1536. The existing source_cells extractor at alpha>=128 finds exactly nine isolated frames in three rows/columns. Rows South/North/West; columns idle and alternate strides. Back row has no face; profile faces left. Navy crewneck, dark trousers, off-white sneakers, natural light warm face, no props/logos/labcoat. South and west stride leg silhouettes now visibly alternate; south/west arms also differ. North feet alternate, but both north stride arms still read similarly and may need native cleanup. No additional generation performed after the one permitted revision.

Alpha range: 0–254. There are 1,031,576 fully transparent pixels, 54,747 pixels with alpha 1–127, 486,541 pixels with alpha 128–254, and no pixels with alpha 255. Sample gutter coordinates (341,512), (512,512), (341,1024) and canvas corners have alpha 0. Low-alpha edge haze and soft antialiasing remain; this is not final binary-alpha or palette-ready art. Source visible cells have different widths/heights and approximate rather than audited native feet baselines; main should inspect after reduction. No native conversion or palette assignment was performed here. Source faces and shoes retain their original colors; they were not forced into the existing orange-heavy palette.

Source-cell boxes [left,top,right,bottom], half-open:

- South: [71,70,265,446], [408,70,604,446], [756,70,949,446]
- North: [77,567,272,942], [418,567,611,942], [761,567,955,942]
- West: [71,1044,281,1445], [407,1044,619,1445], [756,1044,967,1445]

First attempt preserved at ignored .tools/karpathy-atlas-generation/attempt-01.png. Generated selected original retained at /Users/devkunjadia/.codex/generated_images/01a13900-5c2c-7973-bea7-389deda8a5ab/exec-f3645b34-155f-40d8-af17-0d5d5c1e9780.png. First attempt repeated south/west leg phases; the revision corrected those visible source silhouettes. All appearance/outfit/animation approval remains pending.

## Native conversion checkpoint

The shared native palette adds a single light RGB5(31,27,23) face/sneaker color at previously unused index15. Roon keeps its original quantization palette, recipe, indexed frames and visible colors; his packed4bpp remains e5dc40733671ee6bb4f7198253e6cf812f8eeb5fdd8d4e16a8585497592d91fc. Karpathy uses nine16x32 native poses and native east mirroring; fine pose/palette/runtime review remains pending.

Public persona reference checked2026-10-14: https://karpathy.ai/ describes Andrej Karpathy as an AI researcher and educator. The game mentor role, navy outfit and plot are fiction; source photography and site images were not copied.
