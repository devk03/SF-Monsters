# Original game art

`monsters-atlas.png` and `world-atlas.png` were generated with OpenAI ImageGen
for this original game on October 7, 2026. The source atlases are included so
contributors can replace individual sprites and rebuild the ROM.

To the extent licensable, these original game assets are made available under
CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
Attribution: SF Mini Monsters contributors. No company logo assets are included.
Generated people are stylized fictional game sprites, not documentary portraits.

`font8x8_basic.h` is the public-domain font by Daniel Hepper, based on
public-domain VGA fonts. Its license notice is preserved in the file.
Source: https://github.com/dhepper/font8x8

The build crops cells, sizes sprites with nearest-neighbor sampling, and
converts them into a shared indexed palette suitable for the GBA.
