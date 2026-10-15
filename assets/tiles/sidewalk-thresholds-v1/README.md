# Original sidewalk connections

Four original built-in image-generation candidates: bay-house garage/stoop,
brick plinth/central step, Edwardian stone stoop and coffee threshold/mat.
The exact refinement prompt and byte-exact consumed source are preserved.
No commercial art was supplied as a reference.

`sidewalk_thresholds.py` crops the four source quadrants and alpha bounds,
keeps their aspect ratios at native widths48/48/48/32, top-aligns the resulting
6/5/6/3-pixel art in16-pixel cells and serializes a shared RGB555 palette.
The lower eight rows always stay transparent so the existing gray paving remains
visible. No synthetic background slab or interpolated scaling is introduced.

Intended isolated primary palette bank5; existing paving bank4 is unchanged.
These candidates do not add collisions, doors or warp events. Map integration,
player layering, seam/contact alignment and native/browser review are required
before publication. Pixel quality has no automatic approval score.

Reproduce with `.tools/venv/bin/python scripts/romhack/sidewalk_thresholds.py`.
Source edits require regenerating and reviewing all consumed resources together.
