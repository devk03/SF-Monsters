# Original SF landmark cards

Generated with the built-in imagegen tool for this project. Exact final prompt:
[prompt.md](prompt.md). The unmodified generated atlas is [source.png](source.png).
No commercial game art or logos were supplied. Native cards are illustrative game
landmarks, not measured architectural replicas or approved final art.

`python scripts/romhack/convert_world_landmarks.py` extracts each measured connected
alpha silhouette, preserves aspect ratio, reduces to a small native frame and
quantizes to one original 15-color RGB555 palette plus transparency, without
pixel dithering. Source, native PNGs/indices, palette, enlarged preview and exact
SHA-256 receipts remain together. GBA compilation independently bounds tile and
metatile allocations and keeps solid landmark footprints off walkable ground.
Human review of actual in-game placement is still required.

Geographical references used for placement and original dialogue:

- [Sutro Tower](https://www.sutrotower.com/about)
- [Golden Gate Park points of interest](https://www.sfrecpark.org/1116/Golden-Gate-Park-Points-of-Interest)
- [Queen Wilhelmina Garden](https://sfrecpark.org/908/Golden-Gate-Park---Queen-Wilhelmina-Gard)
- [NPS Sutro Baths / Lands End](https://www.nps.gov/places/000/sutro-baths-lands-end-tour.htm)

The crane, highrise, ballpark gate and theater are original simplified city
motifs. Their placement expresses neighborhood identity, not an office-address
claim. Final gym startup/person assignments remain contributor decisions.
