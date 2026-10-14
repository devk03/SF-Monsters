# Naval field sprite candidate

Original nine-pose fictional public-person game caricature made with built-in
ImageGen on October14,2026. `source.png` and exact `prompt.md` are included.
The original Naval intro source provided appearance; Karpathy's native gallery
provided only field scale/direction/cluster guidance. No commercial art input.

Three south, north and west poses become native16x32 frames; east uses the native
horizontal flip. The shared Sunset palette remains byte-identical, including all
colors already used by Roon and Karpathy. `native-cleanup.json` records43 pinned
face pixels across six south/west poses. Every north/body/footstep pixel remains
unchanged. Source, palette and per-frame before/after hashes reject stale edits.
Human likeness, native art and walking approval remain pending.

Rebuild the existing group with:
`.tools/venv/bin/python -c "from pathlib import Path; import sys; sys.path.insert(0,'scripts/romhack'); from cast_art import encode_cast; encode_cast(Path.cwd(),'assets/characters/sunset-cast','0x1127')"`

Native alias SF_NAVAL reuses ProfBirch64, which has no other authored SF owner.
Garry retains Gentleman48; the static239-slot table/dynamic-ID boundary stay
unchanged. Native Hoenn scaffolding references to64 inherit this replacement;
this is not a claim that64 is globally unused in the baseline cartridge.
Existing named-cast Continue repair updates old cachedNaval48→64 while retaining
position/movement. No new NPC, dialogue, story reward, schema or content revision.
Licensing: repository CC BY4.0 terms to the extent licensable; attribution to
SF Mini Monsters contributors. Costume/dialogue are fictional, no endorsement.
