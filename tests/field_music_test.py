"""Independent MIDI timing/voice contracts for the native field-score importer."""
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]


def midi_events(data):
    cursor, tick = 0, 0
    def read_length():
        nonlocal cursor
        value = 0
        while True:
            byte = data[cursor]; cursor += 1; value = (value << 7) | (byte & 127)
            if byte < 128: return value
    while cursor < len(data):
        tick += read_length()
        status = data[cursor]; cursor += 1
        if status == 255:
            kind = data[cursor]; cursor += 1; length = read_length()
            payload = data[cursor:cursor + length]; cursor += length
            yield tick, status, kind, payload
        else:
            size = 1 if status & 240 in [192, 208] else 2
            payload = data[cursor:cursor + size]; cursor += size
            yield tick, status, None, payload


class NativeScore(unittest.TestCase):
    def test_seven_mono_tracks_share_each_declared_loop(self):
        for stem, loop in [('ocean-commute', 1536), ('fogbank-frenzy', 2304)]:
            with self.subTest(score=stem): self.check_score(stem, loop)
        self.check_score('foglight-overture', 3072, 8)
        self.check_score('park-bench-break', 3072)
        self.check_score('park-bench-break', 3072, revision=2)
        self.check_score('team-refresh', 192, 3, looped=False)

    def check_score(self, stem, loop, track_count=7, revision=1, looped=True):
        data = (ROOT / f'assets/audio/{stem}-native-v{revision}/{stem.replace("-", "_")}.mid').read_bytes()
        self.assertEqual(data[:4], b'MThd')
        self.assertEqual(struct.unpack_from('>IHHH', data, 4), (6, 1, track_count, 24))
        cursor = 14
        for track in range(track_count):
            self.assertEqual(data[cursor:cursor + 4], b'MTrk')
            length = struct.unpack_from('>I', data, cursor + 4)[0]; cursor += 8
            active, markers, count = set(), [], 0
            for tick, status, kind, payload in midi_events(data[cursor:cursor + length]):
                if status == 255 and kind == 6: markers.append((tick, payload))
                if status & 240 == 144:
                    self.assertFalse(active, 'Each native track is monophonic')
                    active.add(payload[0]); count += 1
                elif status & 240 == 128:
                    self.assertIn(payload[0], active); active.remove(payload[0])
                elif status & 240 == 192: self.assertLess(payload[0], 8)
            self.assertFalse(active)
            self.assertEqual(markers, [(0, b'['), (loop, b']')] if looped else [])
            self.assertGreater(count, 0)
            cursor += length
        self.assertEqual(cursor, len(data))

    def test_original_instrument_wave_headers(self):
        for stem in ['ocean-commute', 'fogbank-frenzy', 'park-bench-break']:
            with self.subTest(score=stem): self.check_samples(stem)
        self.check_samples('park-bench-break', revision=2)
        self.check_samples('team-refresh', count=4)

    def check_samples(self, stem, revision=1, count=8):
        files = list((ROOT / f'assets/audio/{stem}-native-v{revision}').glob('*.bin'))
        self.assertEqual(len(files), count)
        for path in files:
            data = path.read_bytes(); kind, status, frequency, loop, size = struct.unpack_from('<HHIII', data)
            self.assertEqual((kind, frequency), (0, 16744 * 1024))
            self.assertIn(status, [0, 0x4000])
            self.assertEqual(size, len(data) - 16)
            if status:
                self.assertLess(loop, size)
                # Loop joins should have no isolated jump beyond the waveform slope.
                pcm = [v if v < 128 else v - 256 for v in data[16:]]
                largest_step = max(abs(a - b) for a, b in zip(pcm, pcm[1:]))
                self.assertLessEqual(abs(pcm[-1] - pcm[loop]), largest_step + 2)
            else:
                self.assertEqual(loop, 0)
            if stem in ['park-bench-break', 'team-refresh'] and status == 0:
                self.assertEqual((data[16], data[-1]), (0, 0),
                                 'Transient voices must begin/end at silence')


if __name__ == '__main__': unittest.main()
