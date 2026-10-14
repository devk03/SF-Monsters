"""Reject stale or unsafe edits to original native cast sprites."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/romhack'))
from cast_cleanup import apply_cleanup, digest


def fixture():
    frames = [bytes([index+1])+bytes(511) for index in range(9)]
    expected = bytearray(frames[8]); expected[26*16+4] = 11
    document = {'format':1, 'intent':'An independently specified lower-leg correction.',
                'source_sha256':digest(b'original source'), 'palette_sha256':digest(bytes(32)),
                'before_frame_sha256':{'8':digest(frames[8])},
                'after_frame_sha256':{'8':digest(expected)},
                'changes':[{'frame':8,'x':4,'y':26,'old':0,'new':11}]}
    return frames, document, bytes(expected)


class NativeCleanup(unittest.TestCase):
    def test_only_declared_pixel_changes_and_inputs_remain_immutable(self):
        frames, document, expected = fixture(); before = list(frames)
        output = apply_cleanup(frames, document, b'original source', bytes(32))
        self.assertEqual(output[:8], frames[:8])
        self.assertEqual(output[8], expected)
        self.assertEqual(output[8][:26*16], frames[8][:26*16])
        self.assertEqual(frames, before)

    def test_source_palette_and_complete_input_output_pose_hashes_are_required(self):
        for key in ('source_sha256','palette_sha256','before_frame_sha256','after_frame_sha256'):
            frames, doc, _ = fixture()
            doc[key] = {'8':'0'*64} if key.endswith('frame_sha256') else '0'*64
            with self.subTest(key=key), self.assertRaises(ValueError):
                apply_cleanup(frames, doc, b'original source', bytes(32))
        for source, palette in ((b'changed source',bytes(32)),(b'original source',bytes([1])*32)):
            frames, doc, _ = fixture()
            with self.subTest(source=source,palette=palette), self.assertRaises(ValueError):
                apply_cleanup(frames, doc, source, palette)

    def test_bounds_boolean_duplicate_noop_and_wrong_old_pixel_are_rejected(self):
        for change in ({'frame':9},{'x':16},{'y':30},{'old':16},{'new':16},
                       {'frame':True},{'new':True},{'old':1},{'new':0}):
            frames, doc, _ = fixture(); doc['changes'][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                apply_cleanup(frames, doc, b'original source', bytes(32))
        frames, doc, _ = fixture(); doc['changes'] *= 2
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            apply_cleanup(frames, doc, b'original source', bytes(32))

    def test_missing_oracles_unknown_controls_and_collapsed_steps_are_rejected(self):
        for change in ({'format':True},{'intent':''},{'extra':1},{'changes':[]},
                       {'before_frame_sha256':{}},{'after_frame_sha256':{'08':'0'*64}}):
            frames, doc, _ = fixture(); doc.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                apply_cleanup(frames, doc, b'original source', bytes(32))
        frames, doc, _ = fixture()
        doc['changes'] = [{'frame':8,'x':0,'y':0,'old':9,'new':8}]
        doc['after_frame_sha256']['8'] = digest(frames[7])
        with self.assertRaisesRegex(ValueError, 'collapsed'):
            apply_cleanup(frames, doc, b'original source', bytes(32))

    def test_invalid_frame_or_palette_allocations_cannot_enter_the_packer(self):
        for mode in ('missing','short','outside_palette','below_baseline','short_palette'):
            frames, doc, _ = fixture(); palette = bytes(32)
            if mode == 'missing': frames.pop()
            if mode == 'short': frames[0] = bytes(511)
            if mode == 'outside_palette': frames[0] = bytes([16])+bytes(511)
            if mode == 'below_baseline': frames[0] = bytes(511)+b'\1'
            if mode == 'short_palette': palette=bytes(31);doc['palette_sha256']=digest(palette)
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                apply_cleanup(frames, doc, b'original source', palette)


if __name__ == '__main__':
    unittest.main()
