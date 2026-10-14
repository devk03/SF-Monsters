"""Reject plausible-looking input reports without consumption evidence."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/quality'))
from profile_native_input import compare_outputs, summarize


class InputProfileTest(unittest.TestCase):
    def setUp(self):
        # Preserve diagnostic fixtures; no deletion or cleanup commands.
        self.path = Path(tempfile.mkdtemp(prefix='input-profile-test-', dir=ROOT / '.tools'))
        self.control, self.observe = [self.path / name for name in ('control', 'observe')]
        header = ['frame', 'sequence', 'keys', 'set_cycle', 'end_cycle',
                  'held_raw', 'cumulative_hooks']
        for prefix, count in ((self.control, 0), (self.observe, 1)):
            self.write_csv(prefix, 'frames', header, [[0, 1, 16, 0, 100, 16, count]])
        self.write_csv(self.observe, 'hooks', ['frame', 'sequence', 'keys',
                       'hook_entry_cycle'], [[0, 1, 16, 25]])
        Path(str(self.observe) + '.json').write_text(json.dumps({
            'frames': 1, 'hooks': 1, 'initial_held_raw': 0, 'guest_cycles': 100}))

    def write_csv(self, prefix, suffix, header, values):
        with Path(str(prefix) + '.' + suffix + '.csv').open('w') as target:
            writer = csv.writer(target)
            writer.writerow(header)
            writer.writerows(values)

    def test_changed_mask_has_separate_hook_and_upper_bound(self):
        result = summarize(self.control, self.observe)
        self.assertEqual(result['changes'][0]['hook_entry_guest_cycles'], 25)
        self.assertEqual(result['changes'][0]['held_state_ack_upper_guest_cycles'], 100)
        self.assertEqual(result['changes'][0]['held_state_ack_frame_samples'], 1)

    def test_preexisting_match_does_not_count_as_acknowledgement(self):
        path = Path(str(self.observe) + '.json')
        meta = json.loads(path.read_text())
        meta['initial_held_raw'] = 16
        path.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError, 'Preexisting'):
            summarize(self.control, self.observe)

    def test_missing_read_is_rejected_even_with_matching_held_state(self):
        self.write_csv(self.observe, 'hooks', ['frame', 'sequence', 'keys',
                       'hook_entry_cycle'], [])
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            summarize(self.control, self.observe)

    def test_read_after_ack_bound_is_rejected(self):
        self.write_csv(self.observe, 'hooks', ['frame', 'sequence', 'keys',
                       'hook_entry_cycle'], [[0, 1, 16, 101]])
        with self.assertRaisesRegex(ValueError, 'chronology'):
            summarize(self.control, self.observe)

    def test_calibration_rejects_corruption_in_any_output(self):
        reference = self.path / 'reference'
        for suffix in ('rgba', 'pcm', 'state', 'sav'):
            for prefix in (self.control, self.observe, reference):
                Path(str(prefix) + '.' + suffix).write_bytes(b'unchanged')
        for suffix in ('rgba', 'pcm', 'state', 'sav'):
            with self.subTest(output=suffix):
                path = Path(str(self.observe) + '.' + suffix)
                path.write_bytes(b'corrupted')
                with self.assertRaisesRegex(ValueError, suffix):
                    compare_outputs(self.control, self.observe, reference)
                path.write_bytes(b'unchanged')


if __name__ == '__main__':
    unittest.main()
