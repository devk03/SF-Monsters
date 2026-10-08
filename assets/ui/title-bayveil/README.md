# Bayveil title-silhouette candidate

The specification proposes Bayveil as a tiny floating fog manta with kelp-like
whiskers and lighthouse eyes. `source.png` is our original generated silhouette;
`prompt.txt` records the exact request. This title appearance does not implement
its stats, acquisition quest, battle views, evolution or postgame.

The native creature has a 116x63 footprint inside a 128x128 sheet. Two separately
validated eye regions use the engine's existing pulsing color slot; the body uses
dark teal. `native-preview.png` shows maximum eye glow for inspection. Actual
title colors vary with the inherited animation. Typography/creature approval is
pending, and this does not increase the finished-monster count.

Run `.tools/venv/bin/python scripts/romhack/title_creature.py` to encode the source.
`bayveil.4bpp` includes the silhouette and authored backing-color tiles;
`bayveil.tilemap` maps its occupied tiles into the title scene. Thirty-two reserved
tiles supply a blue/teal row gradient for the existing cloud blend. Source bounds,
palette roles, eye regions and payload fingerprints are in `conversion.json`.
The inherited cloud texture, title soundtrack and footer remain separate gaps.
