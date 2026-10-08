# SproutSlug sprite candidate

`source-v1.png` is original Bloom garden slug source art generated with the built-in
imagegen tool on October 7, 2026. The exact prompt is in `prompt.txt`.
The source and technical conversions use the license/attribution in
`assets/README.md`.

`native-v1/` contains separate 64x64 front/back views, two front entrance frames,
two 32x32 party-icon frames, and 16-entry normal/shiny palettes. The shared crop
preserves proportions and relative poses. Native palette/dimension checks are
format evidence, not pixel cleanup or user approval.
The original cry, FernSlug (level 16) and Canoptera (36) candidates are
now integrated, with new views, authored icon poses and move progression.
Native-size cleanup and user art/animation approval remain pending.

Reproduce with Pillow 12.3.0:

```
python scripts/romhack/monster_art.py assets/monsters/sproutslug/source-v1.png assets/monsters/sproutslug/native-v1 --crop 88 68 672 652
```
