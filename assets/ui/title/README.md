# SF title-lettering candidates

`source.png` is our original transparent two-wordmark atlas, generated with the
built-in image tool using `prompt.txt`. The actual transparent gap determines
the two panel crops recorded in `conversion.json`. No franchise artwork is used
as an input or published here.

`logo-native.png` uses the engine's 256x64 affine tile sheet. Its visible lettering
is anchored around source x=91, because the pinned title transform adds 29 pixels.
`subtitle-native.png` uses two contiguous 64x32 eight-bit sprite blocks. Both have
sixteen-entry RGB555 palettes with slot zero reserved for transparency. Native
resampling/pixel cleanup and typography approval remain pending.

Run `.tools/venv/bin/python scripts/romhack/title_art.py` to rebuild native files
from the source atlas. The converter records bounds, sizes, layout and hashes.
The title postprocessor verifies native LZ77 decoding and the existing allocation
budgets before writing any resource. It preserves the final sixteen background
palette entries used by the inherited creature/cloud layers.

The words replace the old main logo and version subtitle only. The inherited
background creature, other title art/music and copyright footer remain explicit
remaining work; this is not the complete original title or an approved game build.
