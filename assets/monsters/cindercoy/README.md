# CinderCoy sprite candidate

`source-v1.png` is original source art generated with the built-in imagegen tool
on October 7, 2026. It contains a front view, entrance-pose variant and separately
drawn back view of the Ember starter proposed in the original roster. The asset
license and attribution in `assets/README.md` apply.

It is not a finished native sprite or an approved monster. The 2172x724 output
has 772 fully opaque colors, exceeding the native dimensions and palette budget.
It requires deliberate 64x64 pixel cleanup, a shared 15-color palette, silhouette
and pose checks, animation assembly and actual battle review. Resizing alone
does not pass that gate. Preserve the transparent source.

Generation prompt: Original small Ember-type urban California coyote pup with
angular ears, rust-red body, cream muzzle/chest, charcoal paws, asymmetrical
ember-speckled tail and confident expression. Three equal horizontal transparent
cells: three-quarter front facing left, subtle ear/tail-lift entrance pose, and
separately drawn back facing upper right. Target logical sheet 192x64, 64x64
cells, character approximately 52x52 pixels; integer nearest-neighbor enlargement,
15 shared opaque colors plus transparency, sharp pixel clusters, dark colored
outlines, two or three shade values per material and upper-left light. No copied
Pokémon species, logo, text, borders, background, gradients, anti-aliasing, blur
or painted texture. Maintain native handheld creature-RPG craft and proportions.

`native-v1/` contains the first technical conversion: 64x64 front/back, 64x128
entrance frames, 32x64 party-icon frames and 16-entry normal/shiny palettes.
All PNGs share the same palette and transparent index zero. These remain
unreviewed candidates; this conversion does not perform deliberate pixel cleanup.
Reproduce with Pillow 12.3.0 and:

```
python scripts/romhack/monster_art.py assets/monsters/cindercoy/source-v1.png assets/monsters/cindercoy/native-v1 --crop 88 64 668 644
python tests/monster_art_test.py
```
