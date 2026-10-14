# Naval welcome figure candidate

Original fictional public-person game caricature generated with built-in ImageGen
on October 14, 2026. `source.png` is the selected second source; `prompt.md` records
its exact instructions and appearance-reference role. The first illustration and
its prompt are retained as `appearance-reference.png` and
`appearance-reference-prompt.md`. No commercial character image was used as input.

The native figure fits one 64x64 indexed frame with fifteen opaque RGB555 colors
and transparent index0. A deliberate `palette-policy.json` reserves beard gray,
skin bands and eye highlights. `native-cleanup.json` pins eighteen face pixel
edits to the exact source, palette and before/after native frames. Other pixels
are unchanged. `conversion.json` records all consumed output hashes.

Rebuild with `.tools/venv/bin/python scripts/romhack/intro_art.py`. The new engine
path replaces only the intro figure's raw graphics/palette inputs; its dedicated
tag0x1006, animation, coordinates, platform, text and intro flow are retained.
The pre-patch build gate reads both linked resources and three display bindings.
This asset does not replace Naval's separate field placeholder or player portraits.

Human likeness, pixel-art and intro-scene approval remain pending. Generation,
native format compliance and a passed compiled audit do not establish quality parity.
Original asset licensing follows repository CC BY4.0 terms to the extent licensable;
attribution: SF Mini Monsters contributors. Existing public-person context is in
`docs/cast-research.md`; costume/dialogue are fictional and imply no endorsement.
