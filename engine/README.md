# Experimental native foundation

This is checkpoint A's hardware-renderer candidate. It is unreviewed, does not
replace the public prototype, and does not certify Emerald quality. The first
scene proves four-direction interpolated walking, alternating footsteps and
running on actual GBA hardware graphics. Timing is provisional until measured.

Build prerequisites: Docker, Git, Python 3, and the root `make setup` environment.
Run `python3 scripts/foundation/build.py --setup` once, then `make foundation`.
Open `engine/sf-foundation.gba` with native mGBA 0.10.5. PAD walks; hold B to run.
The build retains containers and intermediate files for inspection.

Pinned dependencies: Butano 21.9.0, commit
`a9426cf21b8b6372e4f43678464345a1bf4594de` (zlib license), and the official
devkitARM image digest in `scripts/foundation/build.py`. Dependency licenses
remain in `.tools/butano`; distribution attribution must accompany promotion
of this renderer into the release build. No reference ROM or assets are used.

Original courier source: `assets/characters/courier-walk-candidate.png`.
The pipeline reserves transparent palette index zero, packs twelve 16x32 frames,
and records source hash/crop metadata. This conversion is not pixel-level art
cleanup. Font glyphs use the existing public-domain font with its notice intact.
