# Stable service-door animation candidates

Original built-in imagegen output exec-4b49f077-70ae-4193-b0e1-83992a0426b0.png.
Exact prompt: prompt.md. Two references are deterministic16×32 crops of the
original project service-building art. No commercial game art was supplied.

scripts/romhack/service_door_art.py compiles three16×32 stages per door into
native tile order. It locks every pixel outside the inset rectangle x3..12,
y5..25 to the closed stage so jambs and steps do not jump between frames. All
portal pixels remain opaque; an open doorway cannot reveal scenery through a
transparent hole. Source crops, palette, references and output hashes are saved.

When integrated, frame0 must also supply the static upper/lower door cells:
office secondary64/71; clinic99/106. Palette banks8/9 and native timing remain
unchanged. These are unapproved candidates until actual entries, closing frames,
returns, cached graphics and user comparison checks pass.
