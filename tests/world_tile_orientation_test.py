"""Native mirrored tile reuse must retain the handedness of original facades."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from world_tiles import compile_kit


class TileOrientationTests(unittest.TestCase):
    def test_original_facade_pixels_survive_native_flip_deduplication(self):
        source=(ROOT/'assets/tiles/connected-frontage-v3/block.indices').read_bytes()
        offsets={'coral':(0,48),'cafe':(48,32),'cream':(80,48),'lilac':(128,48)}
        for profile in ('residential','industrial','civic','neighborhood','culture','stadium'):
            kit=compile_kit(profile=profile)
            for name,(left,width) in offsets.items():
                if name not in kit['catalog']:continue
                actual=bytearray(width*64)
                for my,row in enumerate(kit['catalog'][name]['tiles']):
                    for mx,metatile in enumerate(row):
                        words=kit['records'][metatile-512][4:]
                        for quadrant,word in enumerate(words):
                            tile=kit['tiles'][(word&1023)-512]
                            for y in range(8):
                                for x in range(8):
                                    sx=7-x if word&0x400 else x
                                    sy=7-y if word&0x800 else y
                                    px=mx*16+quadrant%2*8+x;py=my*16+quadrant//2*8+y
                                    actual[py*width+px]=tile[sy*8+sx]
                expected=b''.join(source[y*176+left:y*176+left+width] for y in range(64))
                with self.subTest(profile=profile,facade=name):self.assertEqual(bytes(actual),expected)


if __name__=='__main__':unittest.main()
