"""Audit a local browser diagnostic receipt without declaring full acceptance."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value, integer=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (
            integer and (type(value) is not int)):
        raise ValueError('Nonfinite, negative or incorrectly typed observation')
    return value


def audit(report, identity, runtime):
    if report.get('schema') != 1 or report.get('valid') is not True or (
            report.get('context', {}).get('identity') != identity):
        raise ValueError('Require a valid report and its exact original identity')
    if report['reason'] != 'duration' or not 0 < number(report['durationMs']) <= 600000:
        raise ValueError('Require a completed finite diagnostic window')
    if number(report['elapsedMs']) < report['durationMs']:
        raise ValueError('Diagnostic ended before its declared window')
    for name, expected in identity['runtime'].items():
        if not re.fullmatch(r'[A-Za-z0-9._-]+', name) or digest(runtime / name) != expected:
            raise ValueError('Original runtime bytes changed or are unavailable: ' + name)
    ticks = report['ticks']
    for name in ('count', 'visible', 'hidden', 'requestedFrames', 'executedFrames',
                 'actualVideoFrames', 'discardedFrames', 'renderSubmissions', 'videoFrameMismatchTicks'):
        number(ticks[name], True)
    if ticks['requestedFrames'] != ticks['executedFrames'] + ticks['discardedFrames'] or (
            ticks['count'] != ticks['visible'] + ticks['hidden']):
        raise ValueError('Frame accounting is inconsistent')
    for distribution in [ticks[name] for name in ('rafGapMs', 'runMs', 'renderMs')]:
        number(distribution['count'], True)
        if distribution['count']:
            values = [number(distribution[name]) for name in ('min', 'p50', 'p95', 'p99', 'max')]
            if values != sorted(values):
                raise ValueError('Timing percentiles are inconsistent')
    final = report.get('audioFinalSnapshot')
    if report.get('audioFinalAcknowledged') is not True or not final or final.get('final') is not True:
        raise ValueError('Final audio acknowledgement is missing')
    number(final['epoch'], True)
    number(final['queueDepthFrames'])
    if final.get('type') != 'diagnostics' or (
            'diagnosticEpoch' in report['context'] and final['epoch'] != report['context']['diagnosticEpoch']):
        raise ValueError('Final audio epoch or payload is invalid')
    for name in ('warmupOutputFrames', 'underrunOutputFrames', 'droppedSourceFrames',
                 'renderedOutputFrames', 'processQuanta', 'observedThroughOutputFrame'):
        number(final[name], True)
        number(report['audio'][name], True)
        if final[name] < report['audio'][name]:
            raise ValueError('Final audio counters regressed')
    if final['observedThroughOutputFrame'] - number(final['firstOutputFrame'], True) != (
            final['renderedOutputFrames']):
        raise ValueError('Audio output interval is not contiguous')
    rate = number(final['outputSampleRate'])
    if rate == 0:
        raise ValueError('Audio output rate is missing')
    audio_seconds = final['renderedOutputFrames'] / rate
    return {'receipt_well_formed': True, 'requested_seconds': report['durationMs'] / 1000,
        'actual_video_frames': ticks['actualVideoFrames'], 'visible_ticks': ticks['visible'],
        'hidden_ticks': ticks['hidden'], 'discarded_frame_debt': ticks['discardedFrames'],
        'video_frame_mismatch_ticks': ticks['videoFrameMismatchTicks'],
        'input_pipeline': report['input'], 'pending_input_at_end': report['pendingInputAtEnd'],
        'audio_observed_seconds': audio_seconds,
        'audio_window_difference_seconds': audio_seconds - report['durationMs'] / 1000,
        'underrun_output_frames': final['underrunOutputFrames'],
        'dropped_source_frames': final['droppedSourceFrames'],
        'foreground_only': report['scope']['foregroundOnly'],
        'scope': 'Browser pipeline/audio observations; no guest consumption, physical paint or full gate acceptance'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    identity_path = args.report.parent / 'identity.json'
    report_bytes, identity_bytes = args.report.read_bytes(), identity_path.read_bytes()
    source = Path(__file__).read_bytes()
    result = audit(json.loads(report_bytes), json.loads(identity_bytes),
                   args.report.parent / 'runtime')
    result.update({'report_sha256': hashlib.sha256(report_bytes).hexdigest(),
        'identity_sha256': hashlib.sha256(identity_bytes).hexdigest(),
        'auditor_sha256': hashlib.sha256(source).hexdigest()})
    output = args.report.with_suffix('.audit.json')
    with output.open('x') as target:
        target.write(json.dumps(result, indent=2) + '\n')
    with args.report.with_suffix('.auditor.py').open('xb') as target:
        target.write(source)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
