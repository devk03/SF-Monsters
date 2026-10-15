# Original South Park frontage candidates

Built-in imagegen created source.png from the exact prompt in prompt.md.
The longer design-brief.md records layout intent. No commercial image input.
Original generated output is retained in the Codex generated_images directory.

The source separates four buildings with transparent horizontal gaps. Detect
those alpha bands rather than assuming equally spaced cards: the generator did
not place the first facade inside one exact quarter of the sheet.

Run the repository venv Python on scripts/romhack/park_frontage.py to regenerate.
Three original facades become48x80 native pixels; coffee becomes32x64. The brief
requested64x80, but the generated tall/narrow designs suit three metatile columns.
Final native dimensions are explicit in STYLES and conversion.json. Conversion
uses nearest sampling and one15-opaque-color RGB555 palette per facade, entry0
transparent. Foundations are substantial; no alpha flood fill changes the art.

Proposed integration uses primary banks0..3 and its own primary tileset, leaving
existing secondary graphics/palettes and eight door animation tiles untouched.
These are unreviewed candidates. Current public v71 does not contain them.
Native cleanup, in-engine scale/joins, collision, save recovery, doors and user
comparison approval must pass before claiming a polished density improvement.
