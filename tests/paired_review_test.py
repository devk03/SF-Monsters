"""Reject mismatched timing, inputs or provenance before packaging a review."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
from pair_field_review import validate_pair,REFERENCE,CORE


class PairedReview(unittest.TestCase):
    def setUp(self):
        common={'frames':2048,'frequency':16777216,'frame_cycles':280896,
                'controller_only':True,'trace_only':False,'mgba_revision':CORE,
                'width':240,'height':160,'input_sha256':'a'*64}
        self.left=dict(common,rom_sha256=REFERENCE)
        self.right=dict(common,rom_sha256='b'*64)

    def test_normal_native_capture_pair_has_a_34_second_review_window(self):
        self.assertAlmostEqual(validate_pair(self.left,self.right),34.2890625)

    def test_different_inputs_clock_provenance_or_resolution_are_rejected(self):
        for key,value in [('input_sha256','c'*64),('frames',2047),('controller_only',False),
                          ('trace_only',True),('frame_cycles',561792),('width',480),('mgba_revision','unknown')]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_pair(self.left,dict(self.right,**{key:value}))
        with self.assertRaises(ValueError):validate_pair(dict(self.left,rom_sha256='d'*64),self.right)

    def test_short_aligned_clips_cannot_replace_the_full_review_window(self):
        with self.assertRaises(ValueError):
            validate_pair(dict(self.left,frames=464),dict(self.right,frames=464))


if __name__=='__main__':unittest.main()
