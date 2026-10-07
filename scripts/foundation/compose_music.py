"""Compose an original four-voice AABA Sunset theme as an editable tracker module."""
from pathlib import Path
import math
import random
import struct

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'engine/audio'
OUT.mkdir(parents=True, exist_ok=True)


def waveform(length, function):
    return bytes(round(max(-127, min(127, function(n)))) & 255 for n in range(length))


samples = [
    ('Harbor bell', waveform(2048, lambda n: (math.sin(n * math.tau / 32) +
        0.25 * math.sin(n * math.tau / 16)) * 75 * math.exp(-n / 600)), 38, 0, 0),
    ('Warm bass', waveform(128, lambda n: (math.sin(n * math.tau / 32) +
        0.2 * math.sin(n * math.tau / 16)) * 70), 26, 0, 128),
    ('Major tide pad', waveform(128, lambda n: (math.sin(n * math.tau / 32) +
        math.sin(n * math.tau * 5 / 128) + math.sin(n * math.tau * 6 / 128)) * 23), 19, 0, 128),
]
# Percussion is synthesized here; no third-party samples are included.
rng = random.Random(0x53464d4d)
samples.extend([
    ('Muni kick', waveform(1024, lambda n: math.sin(0.14 * n +
        7 * (1 - math.exp(-n / 120))) * 95 * math.exp(-n / 180)), 31, 0, 0),
    ('Brush snare', waveform(1536, lambda n: (rng.random() * 2 - 1) *
        76 * math.exp(-n / 240)), 22, 0, 0),
    ('Soft hat', waveform(512, lambda n: (rng.random() * 2 - 1) *
        45 * math.exp(-n / 65)), 13, 0, 0),
    ('Minor tide pad', waveform(512, lambda n: (math.sin(n * math.tau / 32) +
        math.sin(n * math.tau * 19 / 512) + math.sin(n * math.tau * 3 / 64)) * 23), 19, 0, 512),
])


def event(note=0, instrument=0, effect=0, parameter=0):
    period = round(428 * 2 ** ((60 - note) / 12)) if note else 0
    assert 0 <= period < 4096 and 0 <= instrument < 32
    return bytes([(instrument & 0xf0) | (period >> 8), period & 255,
                  ((instrument & 15) << 4) | effect, parameter])


# Newly authored notes. A's rising motif returns after B's longer descent.
melody_a = [62, 66, 69, 66, 64, 66, 71, 69, 67, 71, 74, 71, 69, 73, 76, 73]
melody_b = [74, 73, 71, 69, 66, 69, 71, 66, 67, 66, 64, 62, 64, 68, 71, 73]
progression = [(50, 62, 3), (47, 59, 7), (43, 55, 3), (45, 57, 3)]
patterns = []
for section in range(4):
    pattern = bytearray()
    melody = melody_b if section == 2 else melody_a
    for row in range(64):
        root, pad_note, pad_instrument = progression[row // 16]
        notes = [event(), event(), event(), event()]
        if row % 4 == 0:
            note = melody[row // 4]
            # The final repeat resolves the motif down into the next loop's D.
            if section == 3 and row >= 48:
                note = [69, 66, 64, 62][(row - 48) // 4]
            notes[0] = event(note, 1)
        if row % 8 == 0:
            notes[1] = event(root if row % 16 == 0 else root + 7, 2)
        if row % 16 == 0:
            notes[2] = event(pad_note, pad_instrument)
        if row % 8 == 0:
            notes[3] = event(60, 4 if row % 16 == 0 else 5)
        elif row % 4 == 0:
            notes[3] = event(60, 6)
        if row == 0:
            notes[0] = event(melody[0], 1, 15, 108)
            notes[1] = event(root, 2, 15, 6)
        pattern.extend(b''.join(notes))
    patterns.append(pattern)

module = bytearray(b'Ocean Commute'.ljust(20, b'\0'))
for index in range(31):
    name, data, volume, loop_start, loop_length = samples[index] if index < len(samples) else ('', b'', 0, 0, 0)
    assert len(data) % 2 == 0
    module.extend(name.encode().ljust(22, b'\0'))
    module.extend(struct.pack('>HBBHH', len(data) // 2, 0, volume,
                              loop_start // 2, max(1, loop_length // 2)))
module.extend(bytes([4, 0]) + bytes([0, 1, 2, 3]) + bytes(124) + b'M.K.')
for pattern in patterns:
    module.extend(pattern)
for _, data, _, _, _ in samples:
    module.extend(data)
(OUT / 'ocean_commute.mod').write_bytes(module)
print(f'Composed original four-voice Ocean Commute draft: {len(module)} bytes.')
