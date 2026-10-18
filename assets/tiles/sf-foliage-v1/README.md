# Original small SF foliage candidates

Created with built-in imagegen; the exact prompt is `prompt.md` and the unchanged
output is `source.png`. No commercial game artwork was supplied.

`convert_world_foliage.py` isolates each connected silhouette, preserves its
aspect ratio, reduces it to a 32-pixel card (pine 32×48) and maps it to one
original RGB555 palette with 15 visible colors plus transparency. It saves the
native indices, PNGs, palette, enlarged preview and SHA-256 receipt together.
These are low-detail world art candidates, not user-approved final assets.

The native compiler uses the complete silhouettes where space permits and a
central shrub crop for dense blocked canopy. They replace the earlier repeated
quarter-tree crop. Forest collision and safe approaches are checked separately.
