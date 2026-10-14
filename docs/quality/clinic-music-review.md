# Clinic soundtrack review

This is a clinic soundtrack subset, not complete Audio acceptance. Latest human
score remains 2/4 for v40. No generated candidate inherits a higher score.

v44 changes arrangement only. Melody, tempo, harmony, channel settings, native
volume, instrument PCM/headers/loop offsets and voice envelopes are unchanged
from v43. Native-v3 preserves native-v1/v2. Multiple sequencing changes make
this one arrangement experiment, not isolated evidence for each feature.

Use the pinned controller-only native capture path with `--music-elf` and a
matching ELF/cartridge pair. The added trace reads MPlay RAM once per frame;
it does not write state or change controller input. Capture about four periods
when phase is unknown; the earlier two-loop capture is insufficient.

`music_loop_review.py` checks identity, native clock, PCM completeness, stable
active song/first-track state, actual ROM GOTO instructions/targets, four loop
boundaries and the expected tick interval. Pattern calls/returns are excluded.
Four observed boundaries establish three consecutive first-track periods.

Static compiled-score evidence establishes equal 1536-tick loops after a
96-tick intro across all nine Emerald Centre tracks. The compiled baseline is
byte-identical to the approved reference. Existing SF MIDI tests establish
3072 ticks in each of seven tracks. Runtime observation checks the first track;
the other tracks' runtime cursors are not independently observed.

Measured v44 boundaries are frames3613/8044/12475/16906:4431 frames, about
74.187 seconds per loop. Reference periods alternate2215/2216 frames, about
37.09 seconds. Command boundaries have one-frame resolution; audio-buffer
alignment is uncalibrated. Excerpts include250ms padding at both ends and
retain exact selected sample bounds, not a claim of sample-exact phase.

Preserve unprocessed WAVs separately from review MP3s. One constant RMS gain
per whole excerpt matches levels without compression, limiting or crossfades.
Keep the full three-period files plus a short old/new arrangement comparison
and the same-input 34-second healing scene. Reference media remains private
under `.tools/benchmarks`; never commit or deploy it.

Inspect the final guitar release across the loop boundary. Sample peaks and
repeated periods do not establish clean joins, absence of underruns, browser
performance or musical quality. Human review and the full Audio gate stay open.
