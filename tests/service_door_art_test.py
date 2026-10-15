"""Protect native door-frame order, stationary architecture and opaque openings."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from service_door_art import load,validate


class ServiceDoorArt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.doors=load(ROOT)

    def test_serialized_native_tiles_decode_to_each_of_the_six_source_stages(self):
        for name,frames in self.doors.items():
            data=(ROOT/'assets/tiles/service-door-v2'/(name+'.4bpp')).read_bytes()
            self.assertEqual(len(data),768)
            for stage,expected in enumerate(frames):
                decoded=bytearray(512)
                for tile in range(8):
                    for y in range(8):
                        for x in range(8):
                            byte=data[stage*256+tile*32+y*4+x//2]
                            decoded[(tile//2*8+y)*16+tile%2*8+x]=(byte>>(x%2*4))&15
                self.assertEqual(bytes(decoded),expected,(name,stage))

    def test_stationary_jamb_or_step_cannot_jump_during_an_opening_stage(self):
        for frames in self.doors.values():
            for pixel in (0,15,31*16+8):
                damaged=list(frames);frame=bytearray(frames[1]);frame[pixel]^=1
                damaged[1]=bytes(frame)
                with self.assertRaisesRegex(ValueError,'stationary'):validate(damaged)

    def test_portal_cannot_become_a_transparent_hole(self):
        for frames in self.doors.values():
            damaged=list(frames);frame=bytearray(frames[2]);frame[10*16+8]=0
            damaged[2]=bytes(frame)
            with self.assertRaisesRegex(ValueError,'opaque'):validate(damaged)

    def test_collapsed_animation_stage_is_rejected(self):
        for frames in self.doors.values():
            for stage in (1,2):
                damaged=list(frames);damaged[stage]=frames[0]
                with self.assertRaisesRegex(ValueError,'distinct'):validate(damaged)

    def test_truncated_or_out_of_palette_frames_are_rejected(self):
        frames=self.doors['warehouse']
        for changed in (frames[:2],[frames[0][:-1],*frames[1:]],
                        [bytes([16])+frames[0][1:],*frames[1:]]):
            with self.assertRaisesRegex(ValueError,'four-bit'):validate(changed)


if __name__=='__main__':unittest.main()
