"""Native WaveData bounds and audible, bounded original cry sources."""
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from creature_audio import synthesize


class CreatureAudio(unittest.TestCase):
    def test_encoded_samples_match_native_header(self):
        recipe = json.loads((ROOT / 'assets/audio/creature-cries.json').read_text())
        for cry in recipe['cries']:
            with self.subTest(name=cry['name']):
                data = (ROOT / 'assets/audio/cries-v1' / (cry['name'] + '.bin')).read_bytes()
                kind, status, frequency, loop, length = struct.unpack_from('<HHIII', data)
                self.assertEqual((kind, status, frequency, loop), (0, 0, 10512 * 1024, 0))
                self.assertEqual(length, len(data) - 16)
                self.assertEqual(data[16:], synthesize(cry, recipe['sample_rate']))
                values = struct.unpack('<%db' % length, data[16:])
                self.assertEqual((values[0], values[-1]), (0, 0))
                self.assertLessEqual(max(abs(value) for value in values), 120)
                self.assertGreater(sum(value * value for value in values) / length, 100)

    def test_pulse_outside_wave_is_rejected(self):
        cry = {'name': 'bad', 'duration': 0.2, 'pulses': [[0.1, 0.2, 400, 200]]}
        with self.assertRaises(ValueError): synthesize(cry, 10512)


if __name__ == '__main__': unittest.main()
