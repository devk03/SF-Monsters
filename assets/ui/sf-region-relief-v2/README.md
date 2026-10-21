# SF region relief v2

Original terrain generated with the built-in imagegen tool for this project.
No commercial game pixels or reference images were supplied. The generation
prompt is in `prompt.md`; `source.png` is the selected unchanged tool output.

`convert_world_map.py` reduces it to224x112, maps to one curated16color RGB555
palette without dithering, and writes `native.png`, `native.indices`,
`palette.json` and `conversion.json`. The native window compiler reads verified
indices, packs complete4bpp tiles and overlays real game routes/markers in code.
The source image is not a screenshot of the playable game. Native quality still
requires in-game review; image generation is not automatic user acceptance.

Regenerate native conversion:

```sh
.tools/venv/bin/python scripts/romhack/convert_world_map.py
```

The old v92 code-authored image and its private screenshots remain historical
comparison evidence in Git history and ignored benchmarks.
