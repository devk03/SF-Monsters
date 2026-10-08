# Field Guide wordmark candidate

`header-source.png` is our original transparent FIELD GUIDE wordmark, generated
with the built-in image tool using the exact prompt in `prompt.txt`.
`header-native.png` is its two-color 80x8 native conversion; the glyphs occupy
six rows between empty top/bottom rows. `conversion.json` records source bounds,
resampling and native fingerprints. Pixel/typography approval remains pending.

Run `.tools/venv/bin/python scripts/romhack/interface_graphics.py` after changing
the native asset to regenerate its binary ink mask and fingerprints.
The ROM postprocessor maps ink into the engine's black/white palette entries,
preserves the header's two outer cap tiles and every unrelated raw tile, and
verifies lossless recompression fits the original allocation.

The inherited sheet used during compilation stays private. This directory
contains only our new wordmark, its source and conversion metadata. The native
title and other inherited graphics still need their own original replacements.
