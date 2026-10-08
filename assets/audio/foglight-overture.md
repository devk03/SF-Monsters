# Foglight Overture — title theme candidate

An original D-major journey theme for the SF title and Bayveil's fog-light motif.
The thirty-two-bar form presents and varies the main melody, lifts into a higher
register, relaxes into an eight-bar bridge, then returns with a closing pickup.
The nominal loop is about 66 seconds at 116 BPM. Native mGBA measures 66.509
seconds with the GBA video clock. A three-complete-cycle listening window is
recorded privately; reference listening and soundtrack approval remain pending.

Eight monophonic tracks provide harmonic lead, plucked answers/arpeggios, bass,
triad pad, kick, snare and hats. They use the project's original Fogbank Frenzy
PCM bank; no commercial title samples or melody are copied. Airy sections rest
the answering line and reduce percussion density. Every part shares the same
3,072-tick loop and releases its final note before the loop marker.

Edit `foglight-overture.json`, then run `python3 scripts/romhack/title_music.py`
to rebuild the MIDI and score metadata. `title_song_overlay.py` links the sequence
into the old title-song allocation while retaining its song-table/header address.
All eight waveform pointers and sample bytes are checked against our PCM sources.
Native listening measured no clipped samples and RMS within 0.36 dB of the
forty-second Emerald title reference excerpt. That is a mix check, not composition
parity. The full reference comparison and user approval remain pending.
