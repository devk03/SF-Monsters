# Recovery service comparison

This reviews healing presentation and its audio cue, not complete Audio,
NPC/event or Interface domains. The left capture is the genuine pinned Emerald
ROM; the right is SF v42. Both use native mGBA 0.10.5 on the development Mac,
240x160 pixels, the same 2048-frame input and native GBA clock (34.289 seconds).
Commercial reference footage, ROMs and saves stay in ignored private storage.

The input is `data/quality/recovery-service-review.csv`. It confirms through
the greeting with four A taps, then closes subsequent text with B. Down taps
are excluded because they can select NO in Emerald's healing prompt. The
failed earlier capture is preserved as diagnostic evidence and is not reviewed.

Reference setup follows normal gameplay from the existing verified lab
snapshot: leave via Littleroot's east north-exit lane, rescue Birch with Torchic,
finish the lab dialogue, cross Route 101, take damage in a wild encounter,
flee and enter Oldale centre. The rival introduction was already complete;
an initially blocked lane was an NPC/tree obstruction, not an unmet story gate.
The original centre entrance is (6,16), approached from (6,17). Inside, approach
the nurse from (7,4) across the counter. Record every controller-only parent.

Reference before/after: level-5 Torchic HP 17/19 -> 19/19, Growl PP 39 -> 40;
other moves and 3000 money preserved. SF before/after: level-11 CinderCoy HP
4/31 -> 31/31, Ember PP 16 -> 25; other moves, three Potions, 4000 money,
earned badge and gym stage 4 preserved. Both end outside dialogue, facing the
service actor. Species/content/room layouts and confirmation dialogue differ;
this is a comparable free-healing workflow, not an identical-state damage case.

Private captures: `recovery-service-emerald-confirmed` and
`recovery-service-v42-confirmed` under `.tools/benchmarks`. Encode each with
`scripts/quality/encode_core_capture.py`, then package using
`scripts/quality/pair_field_review.py --reference-label 'EMERALD CENTRE'
--candidate-label 'SF CLINIC' --review-scope healing` and the two directories.
The packager retains ROM/core/input/length/native-frame provenance checks.
The video has separate reference and candidate audio tracks. Separate listening
files are provided when the viewer cannot select audio tracks.

Visible remaining gap: the reference equipment/nurse sequence has movement
and effects; SF v42 plays its original cue beside static recovery equipment.
The next revision should improve that scene without losing the service's
verified state restoration. Human cue/event scores remain pending.
