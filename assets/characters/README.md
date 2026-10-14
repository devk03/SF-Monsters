# Courier walking candidate

Source: `courier-walk-candidate.png`, generated October 7, 2026 with the built-in
OpenAI ImageGen tool. This is an unreviewed foundation candidate. Licensing and
attribution follow `assets/README.md`; pixel-level cleanup remains outstanding.

Prompt: Original 2004 GBA adult SF courier, portrait 2:3 transparent sprite sheet,
four columns down/up/left/right and three rows idle/left foot/right foot. Intended
native sprite 16x32, nearest-neighbor hard pixels, roughly twenty colors. Gray
beanie, navy windbreaker with light blue collar, orange messenger bag, muted
olive trousers and brown shoes. Keep clothing, body, baseline and scale identical
across all twelve poses. No antialiasing, gradients, shadows, text, grid, brands
or existing trainer design.


## Cognition field cast candidates

`cognition-cast/cast.json` assigns original nine-frame field sprites to Scott Wu,
Walden Yan and Steven Hao. The three costumes are fictional game art. Each
character directory contains the original built-in imagegen source, exact
prompt, indexed native gallery, walk strip and packed cartridge bytes.
`conversion.json` records the source hashes, crops and shared palette. Human
likeness/pixel-art review and trainer battle portraits remain outstanding.

The common native palette uses tag 0x1125 and the existing special NPC slot,
with matching reflection metadata. Three explicitly unused doll graphics slots
76–78 are reserved without changing dynamic graphics IDs or battery schemas.
No inherited human sprite pixels are used in these assets. Other characters
still have placeholders. See spec section 15 for actual runtime evidence.


## Sunset field cast

`sunset-cast/cast.json` registers Roon as an original fictional amber-hooded
courier-oracle. The costume does not assert the pseudonymous person's private
appearance or biography. Palette tag0x1127 uses unused graphics slot81; the
other five original cast sprites and their palettes remain unchanged. The small
wandering radius stays on a clear boardwalk area, away from quest/warp anchors.
Cached movement is preserved on an older same-map Continue until map re-entry.

Optional `native-cleanup.json` files describe reviewed indexed-pixel edits after
source conversion and before native packing. They pin source/palette hashes,
complete input/output poses, and each old/new pixel. The converter rejects stale
or duplicate edits, out-of-frame/palette values, and collapsed footsteps; the
conversion receipt includes the recipe hash. Roon's first recipe changes only18
pixels in west stride2's lower legs, leaving head, torso and arms intact.
Human art/likeness/animation approval remains pending.

The native special NPC palette/reflection slot is shared. All original cast
visible on one authored map must belong to one palette group; the registry
rejects independently paletted groups on the same map before compilation.
Adding later Twitter cast members should extend that map's existing group.
