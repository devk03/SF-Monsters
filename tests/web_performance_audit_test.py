"""A plausible browser summary cannot replace exact runtime and audio evidence."""
import copy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/quality'))
from audit_web_performance import audit


class WebPerformanceAuditTest(unittest.TestCase):
    def setUp(self):
        self.runtime = Path(tempfile.mkdtemp(prefix='web-audit-test-', dir=ROOT / '.tools'))
        data = b'original verified runtime fixture'
        (self.runtime / 'sdk.js').write_bytes(data)
        self.identity = {'runtime': {'sdk.js': hashlib.sha256(data).hexdigest()}}
        self.report = {'schema': 1, 'valid': True, 'reason': 'duration', 'durationMs': 10000,
            'elapsedMs': 10001, 'context': {'identity': self.identity, 'diagnosticEpoch': 7},
            'ticks': {'count': 2, 'visible': 2, 'hidden': 0, 'requestedFrames': 2,
                'executedFrames': 2, 'actualVideoFrames': 2, 'discardedFrames': 0,
                'renderSubmissions': 2, 'videoFrameMismatchTicks': 0,
                'rafGapMs': {'count': 0}, 'runMs': {'count': 0}, 'renderMs': {'count': 0}},
            'input': {'count': 0, 'supersededBeforeFrame': 0, 'domToDispatchMs': {'count': 0},
                'dispatchToFrameMs': {'count': 0}, 'dispatchToSubmitMs': {'count': 0}},
            'pendingInputAtEnd': False, 'scope': {'foregroundOnly': True},
            'audioFinalAcknowledged': True, 'audio': {'warmupOutputFrames': 0,
                'underrunOutputFrames': 1, 'droppedSourceFrames': 0,
                'renderedOutputFrames': 470000, 'processQuanta': 3600,
                'observedThroughOutputFrame': 470100},
            'audioFinalSnapshot': {'type': 'diagnostics', 'final': True, 'epoch': 7,
                'warmupOutputFrames': 0, 'underrunOutputFrames': 2, 'droppedSourceFrames': 3,
                'renderedOutputFrames': 480000, 'processQuanta': 3750,
                'firstOutputFrame': 100, 'observedThroughOutputFrame': 480100,
                'outputSampleRate': 48000, 'queueDepthFrames': 512.5}}

    def test_final_audio_counts_remain_observations_not_a_gate_pass(self):
        result = audit(self.report, self.identity, self.runtime)
        self.assertTrue(result['receipt_well_formed'])
        self.assertEqual(result['audio_observed_seconds'], 10)
        self.assertEqual(result['underrun_output_frames'], 2)
        self.assertEqual(result['dropped_source_frames'], 3)
        self.assertIn('no guest consumption', result['scope'])

    def test_changed_runtime_is_rejected(self):
        (self.runtime / 'sdk.js').write_bytes(b'later runtime version')
        with self.assertRaisesRegex(ValueError, 'runtime bytes'):
            audit(self.report, self.identity, self.runtime)

    def test_invalid_audio_tail_and_epoch_are_rejected(self):
        for changed in ({'epoch': 8}, {'final': False}, {'outputSampleRate': 0},
                        {'renderedOutputFrames': 479999}, {'underrunOutputFrames': 0},
                        {'queueDepthFrames': float('nan')}):
            report = copy.deepcopy(self.report)
            report['audioFinalSnapshot'].update(changed)
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                audit(report, self.identity, self.runtime)

    def test_warmup_and_playback_start_are_explicit_without_becoming_a_pass(self):
        report = copy.deepcopy(self.report)
        report['audioFinalSnapshot'].update({'warmupOutputFrames': 128,
            'playbackStarted': False, 'prefillTargetSourceFrames': 2622})
        result = audit(report, self.identity, self.runtime)
        self.assertEqual(result['warmup_output_frames'], 128)
        self.assertIs(result['playback_started'], False)
        for changed in ({'playbackStarted': 'false'}, {'prefillTargetSourceFrames': 32768},
                        {'prefillTargetSourceFrames': 0}, {'prefillTargetSourceFrames': 2.5}):
            invalid = copy.deepcopy(report)
            invalid['audioFinalSnapshot'].update(changed)
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                audit(invalid, self.identity, self.runtime)

    def test_frame_accounting_and_input_percentiles_are_checked(self):
        report = copy.deepcopy(self.report)
        report['ticks']['discardedFrames'] = 1
        with self.assertRaisesRegex(ValueError, 'accounting'):
            audit(report, self.identity, self.runtime)
        report = copy.deepcopy(self.report)
        report['input']['count'] = 1
        report['input']['dispatchToSubmitMs'] = {'count': 1, 'min': 2,
            'p50': 3, 'p95': 1, 'p99': 4, 'max': 5}
        with self.assertRaisesRegex(ValueError, 'percentiles'):
            audit(report, self.identity, self.runtime)

    def test_context_clock_deficit_is_reported_separately_from_sink_frames(self):
        report = copy.deepcopy(self.report)
        report['context']['audioClockAtStart'] = {'beforeMs': 1000, 'afterMs': 1000.5,
            'audioTime': 3, 'audioState': 'running'}
        report['audioClockAtClose'] = {'beforeMs': 601000, 'afterMs': 601000.25,
            'audioTime': 595.864, 'audioState': 'running'}
        result = audit(report, self.identity, self.runtime)
        clock = result['audio_clock_observation']
        self.assertAlmostEqual(clock['context_audio_seconds'], 592.864)
        self.assertEqual(clock['wall_read_interval_seconds'], [599.9995, 600.00025])
        self.assertEqual(result['audio_observed_seconds'], 10)  # Independent sink interval.
        self.assertIn('not hardware', clock['scope'])
        self.assertIsNone(audit(self.report, self.identity, self.runtime)['audio_clock_observation'])

    def test_partial_reversed_and_nonfinite_clock_anchors_are_rejected(self):
        for start, end in [
            ({'beforeMs': 1, 'afterMs': 2, 'audioTime': 0, 'audioState': 'running'}, None),
            ({'beforeMs': 2, 'afterMs': 1, 'audioTime': 0, 'audioState': 'running'},
             {'beforeMs': 3, 'afterMs': 4, 'audioTime': 1, 'audioState': 'running'}),
            ({'beforeMs': 1, 'afterMs': 2, 'audioTime': 3, 'audioState': 'running'},
             {'beforeMs': 3, 'afterMs': 4, 'audioTime': 2, 'audioState': 'running'}),
            ({'beforeMs': 1, 'afterMs': 2, 'audioTime': 0, 'audioState': 'running'},
             {'beforeMs': 3, 'afterMs': float('nan'), 'audioTime': 1, 'audioState': 'running'}),
        ]:
            report = copy.deepcopy(self.report)
            report['context']['audioClockAtStart'] = start
            report['audioClockAtClose'] = end
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                audit(report, self.identity, self.runtime)

    def test_replay_requires_preserved_input_matching_dispatches_and_current_window(self):
        report, identity = copy.deepcopy(self.report), copy.deepcopy(self.identity)
        # Use session-unique auxiliary names through an isolated runtime parent.
        directory = self.runtime / 'session'; runtime = directory / 'runtime'
        runtime.mkdir(parents=True)
        (runtime/'sdk.js').write_bytes((self.runtime/'sdk.js').read_bytes())
        inputs = {'route.csv': b'8,8\n0,8\n', 'controller-replay.js': b'verified helper fixture'}
        identity['files'] = {}
        for name, data in inputs.items():
            (directory/name).write_bytes(data)
            identity['files'][name] = hashlib.sha256(data).hexdigest()
        duration = 16 * 1000 * 280896 / 16777216
        identity['controller_route'] = {'rows': 2, 'frames': 16}
        report['context']['identity'] = identity
        report.update({'startedAtMs': 1000, 'endedAtMs': 11001,
            'controllerReplay': {'reason': 'complete', 'startedAtMs': 1100, 'endedAtMs': 1370,
                'appliedRows': 2, 'totalRows': 2, 'declaredFrames': 16,
                'declaredDurationMs': duration, 'maxLatenessMs': 0,
                'dispatches': [{'row': 0, 'mask': 8, 'dueMs': 1100, 'actualMs': 1100},
                    {'row': 1, 'mask': 0, 'dueMs': 1100+duration/2, 'actualMs': 1100+duration/2}]}})
        self.assertEqual(audit(report, identity, runtime)['controller_replay']['status'], 'complete')
        for changes in ({'startedAtMs': 999}, {'appliedRows': 1}, {'maxLatenessMs': 51}):
            invalid = copy.deepcopy(report); invalid['controllerReplay'].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                audit(invalid, identity, runtime)
        (directory/'route.csv').write_bytes(b'1,16\n')
        with self.assertRaisesRegex(ValueError, 'input/helper changed'):
            audit(report, identity, runtime)


if __name__ == '__main__':
    unittest.main()
