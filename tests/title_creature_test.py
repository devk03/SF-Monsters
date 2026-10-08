"""Protect native silhouette nibble ordering, eye isolation and title-map placement."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from title_creature import pack4, scene_resources, eye_clusters


class TitleCreature(unittest.TestCase):
    def test_native_low_then_high_palette_nibbles_and_invalid_indices(self):
        self.assertEqual(pack4(bytes([0, 11, 15, 0, 11, 15])), b'\xb0\x0f\xfb')
        for pixels in (bytes([11]), bytes([0, 16])):
            with self.assertRaises(ValueError):
                pack4(pixels)

    def test_title_map_places_creature_and_preserves_matching_gradient_backing(self):
        pixels = bytearray(16384)
        pixels[16 * 128] = 11
        pixels[-1] = 15
        raw, mapping = scene_resources(pixels)
        entries = struct.unpack('<1024H', mapping)
        self.assertEqual(entries[7 * 32 + 7], 0xe020)
        self.assertEqual(entries[20 * 32 + 22], 0xe0ff)
        self.assertEqual(entries[4 * 32 + 7], 0xe004)
        self.assertEqual(entries[21 * 32 + 22], 0xe015)
        self.assertEqual(raw[:32], b'\xaa' * 32)
        self.assertEqual(raw[32 * 32], 0x8b)
        self.assertEqual(raw[-1], 0xf4)
        self.assertEqual(set(entry >> 12 for entry in entries), {14})
        for position in ((-1, 5), (17, 5), (7, 17)):
            with self.assertRaises(ValueError):
                scene_resources(pixels, *position)
        pixels[0] = 11
        with self.assertRaises(ValueError):
            scene_resources(pixels)

    def test_eye_components_do_not_wrap_between_rows(self):
        pixels = bytes([0, 0, 0, 15, 15, 0, 0, 0])
        self.assertEqual(eye_clusters(pixels, 4, 2), [
            {'pixels': 1, 'bounds': [3, 0, 4, 1]}, {'pixels': 1, 'bounds': [0, 1, 1, 2]}])
        self.assertEqual(eye_clusters(bytes([15, 15, 0, 15, 15, 0]), 3, 2), [
            {'pixels': 4, 'bounds': [0, 0, 2, 2]}])


if __name__ == '__main__':
    unittest.main()
