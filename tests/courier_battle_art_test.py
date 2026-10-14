"""Protect native battle frame geometry, tile order and isolated palette identity."""
import hashlib
import json
from pathlib import Path
import struct
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'assets/characters/courier-battle-v1'


class CourierBattleArt(unittest.TestCase):
    def test_four_distinct_native_frames_decode_in_engine_tile_order(self):
        image = Image.open(ASSET / 'back.png')
        self.assertEqual(image.size, (64, 256))
        self.assertEqual(image.mode, 'P')
        self.assertEqual(image.info['transparency'], 0)
        raw = (ASSET / 'back.4bpp').read_bytes()
        self.assertEqual(len(raw), 4 * 2048)
        frames = []
        for frame in range(4):
            pixels = bytearray(4096)
            for tile in range(64):
                for row in range(8):
                    for pair in range(4):
                        packed = raw[frame * 2048 + tile * 32 + row * 4 + pair]
                        x, y = tile % 8 * 8 + pair * 2, tile // 8 * 8 + row
                        pixels[y * 64 + x:y * 64 + x + 2] = bytes([packed & 15, packed >> 4])
            self.assertEqual(bytes(pixels), image.crop((0, frame * 64, 64, (frame + 1) * 64)).tobytes())
            self.assertTrue(any(pixels))
            self.assertTrue(all(pixels[row * 64] == pixels[row * 64 + 63] == 0 for row in range(64)))
            frames.append(bytes(pixels))
        self.assertEqual(len(set(frames)), 4)

    def test_palette_and_build_consumed_assets_match_recorded_conversion(self):
        image = Image.open(ASSET / 'back.png')
        palette = image.getpalette()[:48]
        words = struct.unpack('<16H', (ASSET / 'back.gbapal').read_bytes())
        for i, word in enumerate(words):
            channels = palette[i * 3:i * 3 + 3]
            self.assertEqual(word, sum(round(c * 31 / 255) << (j * 5) for j, c in enumerate(channels)))
        metadata = json.loads((ASSET / 'conversion.json').read_text())
        self.assertEqual(metadata['frames'], 4)
        self.assertEqual(metadata['native_frame_size'], [64, 64])
        # Native idle animation selects frame3, whose authored pose must be neutral0.
        self.assertEqual(metadata['native_frame_order'], [1, 2, 3, 0])
        self.assertEqual(metadata['idle_native_frame'], 3)
        self.assertEqual(metadata['quality_approval'], 'pending')
        for name, digest in dict(metadata['files'], **{'source.png': metadata['source_sha256']}).items():
            self.assertEqual(hashlib.sha256((ASSET / name).read_bytes()).hexdigest(), digest)


if __name__ == '__main__':
    unittest.main()
