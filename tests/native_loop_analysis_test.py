"""Capture edges and IRQ delivery jitter must not manufacture complete spans."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/quality'))
from analyze_native_loop import analyze


def event(kind, cycle, value=0, ordinal=0):
    return {'kind': kind, 'completion_cycle': cycle, 'value': value, 'to': ordinal}


class NativeLoopAnalysisTest(unittest.TestCase):
    def test_edge_returns_and_open_spans_are_excluded(self):
        result = analyze([event(12, 10), event(1, 20), event(10, 30),
            event(11, 40), event(12, 70), event(1, 80), event(10, 90), event(11, 100)])
        spans = result['complete_guest_cycle_spans']
        self.assertEqual(spans['wait'], {'count': 1, 'min': 40, 'max': 40,
            'p50_nearest_rank': 40, 'p95_nearest_rank': 40})
        self.assertEqual(spans['loop_start_period']['min'], 60)
        self.assertEqual(spans['loop_through_wait_return']['min'], 50)
        self.assertEqual(result['edge_partials'], {'initial_wait_return': 1,
            'initial_loop_return': 1, 'trailing_wait': 1, 'trailing_loop': 1})

    def test_null_callback_skips_do_not_create_callback_spans(self):
        result = analyze([event(1, 10), event(4, 20), event(5, 30),
            event(10, 40), event(11, 50), event(12, 70)])
        self.assertEqual(result['complete_guest_cycle_spans']['callback1']['count'], 0)
        self.assertEqual(result['complete_guest_cycle_spans']['callback2']['count'], 0)

    def test_overlapping_calls_or_missing_returns_fail(self):
        for values in ([event(6, 10), event(7, 20)], [event(8, 10)],
                       [event(1, 10), event(1, 20)], [event(11, 10)]):
            with self.subTest(events=values), self.assertRaises(ValueError):
                analyze(values)

    def test_clock_regression_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'nonmonotonic'):
            analyze([event(6, 20), event(8, 19)])

    def test_nominal_deadline_subtracts_delivery_lateness(self):
        result = analyze([event(1, 10), event(10, 20), event(11, 105),
            event(13, 110, value=10, ordinal=7), event(12, 120)])
        deadline = result['work_clear_next_vblank']
        self.assertEqual((deadline['scored'], deadline['met'], deadline['missed']), (1, 0, 1))
        self.assertEqual(deadline['margin_guest_cycles']['min'], -5)

    def test_video_jitter_and_counter_wrap_preserve_nominal_period(self):
        result = analyze([event(13, 100, value=5, ordinal=0xffffffff),
            event(13, 280999, value=8, ordinal=0)])
        self.assertEqual(result['nominal_vblank_events'], 2)
        with self.assertRaisesRegex(ValueError, 'period'):
            analyze([event(13, 100, ordinal=1), event(13, 200, ordinal=2)])


if __name__ == '__main__':
    unittest.main()
