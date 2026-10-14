"""Palette growth may use an unused color, never silently recolor a prior pose."""
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/romhack'))
from cast_palette import cast_palette, palette_colors, quantization_palette, preserve_used_colors


class SharedCastPalette(unittest.TestCase):
    def setUp(self):
        parent = ROOT/'.tools/cast-palette-tests'
        parent.mkdir(exist_ok=True)
        self.directory = Path(tempfile.mkdtemp(prefix='case-', dir=parent))
        source = ROOT/'assets/characters/sunset-cast/roon/quantization-palette.gbapal'
        self.old = source.read_bytes() if source.exists() else (
            ROOT/'assets/characters/sunset-cast/cast.gbapal').read_bytes()

    def document(self):
        return {'format': 1, 'intent': 'Use an unused opaque color for the next character.',
                'colors_rgb5': [[(word >> (5*c)) & 31 for c in range(3)]
                               for word in struct.unpack('<16H', self.old)]}

    def policy(self, document):
        (self.directory/'palette-policy.json').write_text(json.dumps(document))

    def test_adding_unused_color_preserves_the_actual_prior_roon_poses(self):
        from PIL import Image
        document = self.document(); document['colors_rgb5'][15] = [31, 27, 23]
        self.policy(document)
        colors, shared, digest = cast_palette(self.directory, [])
        self.assertEqual(shared[:30], self.old[:30])
        self.assertEqual(colors[15], (255, 222, 189))
        self.assertEqual(len(digest), 64)
        image = Image.open(ROOT/'assets/characters/sunset-cast/roon/walk.png')
        frames = [image.crop((i*16, 0, i*16+16, 32)).tobytes() for i in range(9)]
        self.assertFalse(any(15 in frame for frame in frames))
        preserve_used_colors(frames, self.old, shared)
        used = next(index for frame in frames for index in frame if index)
        changed = bytearray(shared)
        changed[used*2] ^= 1
        with self.assertRaisesRegex(ValueError, 'recolor'):
            preserve_used_colors(frames, self.old, bytes(changed))

    def test_an_old_quantization_palette_is_explicit_and_checked(self):
        colors, raw = quantization_palette(self.directory, self.old)
        self.assertEqual(raw, self.old)
        self.assertEqual(colors, palette_colors(self.old))
        path = self.directory/'quantization-palette.gbapal'
        path.write_bytes(self.old)
        modified = self.old[:30]+struct.pack('<H', 0x5f7f)
        self.assertEqual(quantization_palette(self.directory, modified)[1], self.old)
        path.write_bytes(self.old[:-1])
        with self.assertRaisesRegex(ValueError, 'sixteen'):
            quantization_palette(self.directory, modified)

    def test_invalid_policy_fields_rgb_values_and_transparency_fail(self):
        for invalid in ([], {}, {'format': 1}, dict(self.document(), format=True),
                        dict(self.document(), intent=' ')):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.policy(invalid); cast_palette(self.directory, [])
        for invalid in (True, -1, 32, 1.5, '1'):
            document = self.document(); document['colors_rgb5'][4][1] = invalid
            with self.subTest(channel=invalid), self.assertRaises(ValueError):
                self.policy(document); cast_palette(self.directory, [])
        for entry in ([1, 0, 0], [0, 0], None):
            document = self.document(); document['colors_rgb5'][0] = entry
            with self.subTest(transparent=entry), self.assertRaises(ValueError):
                self.policy(document); cast_palette(self.directory, [])

    def test_invalid_native_palette_and_unmapped_indices_fail(self):
        for raw in (bytes(31), b'\x01'+bytes(31), bytes(30)+b'\x00\x80'):
            with self.assertRaises(ValueError):
                palette_colors(raw)
        with self.assertRaisesRegex(ValueError, 'recolor'):
            preserve_used_colors([bytes([16])], self.old, self.old)


if __name__ == '__main__':
    unittest.main()
