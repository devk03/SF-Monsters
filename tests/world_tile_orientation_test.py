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


    def test_crosswalk_has_continuous_paint_bars_without_repeated_fence_edges(self):
        import struct
        for profile in ('neighborhood','mixed_use','industrial','civic','culture','stadium'):
            kit=compile_kit(profile=profile)
            card=kit['catalog']['crossing'];self.assertFalse(card['blocked'])
            words=kit['records'][card['tiles'][0][0]-512]
            paint=set();paint_colors=set()
            # Decode the actual layered/flip-packed native metatile, then repeat
            # it across the same five-by-three road section used in the towns.
            for y in range(48):
                for x in range(80):
                    px,py=x%16,y%16;quadrant=(py//8)*2+px//8;color=None
                    for layer in (0,4):
                        word=words[layer+quadrant];tile=kit['tiles'][(word&1023)-512]
                        tx=7-px%8 if word&0x400 else px%8
                        ty=7-py%8 if word&0x800 else py%8
                        index=tile[ty*8+tx]
                        if index:
                            value=struct.unpack_from('<H',kit['palettes'][word>>12],index*2)[0]
                            color=tuple((value>>shift)&31 for shift in (0,5,10))
                    if color and sum(color)>70:
                        paint.add((x,y));paint_colors.add(color)
            components=[];pending=set(paint)
            while pending:
                found={pending.pop()};queue=list(found)
                for x,y in queue:
                    for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                        if point in pending:pending.remove(point);found.add(point);queue.append(point)
                components.append(found)
            with self.subTest(profile=profile):
                self.assertEqual(len(components),5,'One paint bar per crossing module')
                self.assertTrue(all({y for _,y in part}==set(range(48)) for part in components),
                                'Bars must cross all three road tiles without a horizontal spine')
                self.assertTrue(all(max(x for x,_ in part)-min(x for x,_ in part)<8 for part in components))
                self.assertTrue(all(max(rgb)-min(rgb)<=1 for rgb in paint_colors),
                                'Crossing paint is neutral white')


if __name__=='__main__':unittest.main()
