"""Keep the existing song-table address and reject tracks outside the owned score."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from title_song_overlay import song_region


class TitleSong(unittest.TestCase):
    def setUp(self):
        self.base, self.group = 0x08001000, 0x08002000
        self.header = struct.pack('<BBBBIII', 2, 0, 0, 178, self.group, self.base, self.base + 2)
        self.blob = b'\x80\x00\xb1\x00' + self.header

    def test_tracks_and_fixed_header_fit_without_repointing_song_table(self):
        result = song_region(self.blob, 4, 32, 48, self.base, self.group)
        self.assertEqual(len(result), 80)
        self.assertEqual(result[:20], self.blob)
        self.assertEqual(result[20:32], bytes(12))
        self.assertEqual(result[32:48], self.header)
        self.assertEqual(result[48:], bytes(32))

    def test_header_overflow_wrong_bank_and_invalid_track_addresses_are_rejected(self):
        bad_pointer = self.blob[:12] + struct.pack('<I', self.base + 4) + self.blob[16:]
        for blob, header, target, size, group in [
            (self.blob, 4, 16, 48, self.group), (self.blob, 4, 32, 8, self.group),
            (self.blob, 4, 32, 48, self.group + 4), (bad_pointer, 4, 32, 48, self.group),
            (self.blob, 40, 32, 48, self.group)]:
            with self.subTest(header=header, target=target, size=size):
                with self.assertRaises(ValueError):
                    song_region(blob, header, target, size, self.base, group)


if __name__ == '__main__':
    unittest.main()
