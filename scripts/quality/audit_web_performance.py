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


def audio_clock_observation(report):
    """Compare two bracketed context-clock reads; never infer speaker timing."""
    start = report['context'].get('audioClockAtStart')
    if start is None:
        return None  # Earlier preserved runtimes did not collect start anchors.
    end = report.get('audioClockAtClose')
    if not isinstance(start, dict) or not isinstance(end, dict):
        raise ValueError('Audio clock anchors must be paired')
    for anchor in (start, end):
        for key in ('beforeMs', 'afterMs', 'audioTime'):
            number(anchor[key])
        if anchor['beforeMs'] > anchor['afterMs'] or not isinstance(
                anchor.get('audioState'), str) or not anchor['audioState']:
            raise ValueError('Invalid audio clock read bracket')
    if start['afterMs'] > end['beforeMs'] or start['audioTime'] > end['audioTime']:
        raise ValueError('Audio clock anchor order regressed')
    lower = (end['beforeMs'] - start['afterMs']) / 1000
    upper = (end['afterMs'] - start['beforeMs']) / 1000
    return {'context_audio_seconds': end['audioTime'] - start['audioTime'],
        'wall_read_interval_seconds': [lower, upper],
        'start_state': start['audioState'], 'end_state': end['audioState'],
        'scope': 'Main-thread AudioContext clock reads; quantized context time, not hardware output or physical speaker timing'}


def controller_observation(report, identity, directory):
    for name in ('controller-replay.js', 'route.csv'):
        expected = identity.get('files', {}).get(name)
        if expected and digest(directory / name) != expected:
            raise ValueError('Preserved controller input/helper changed: ' + name)
    configured = identity.get('controller_route')
    if not configured:
        return None
    replay = report.get('controllerReplay')
    if replay is None:
        return {'status': 'not-run'}
    start = number(replay['startedAtMs'])
    if not number(report['startedAtMs']) <= start <= number(report['endedAtMs']):
        raise ValueError('Replay belongs to another measurement window')
    if replay['reason'] == 'in-progress':
        return {'status': 'in-progress'}
    rows = [tuple(map(int, line.split(','))) for line in
            (directory / 'route.csv').read_text().strip().splitlines()]
    frames = sum(count for _, count in rows)
    duration = frames * (1000 * 280896 / 16777216)
    count = number(replay['appliedRows'], True)
    if not 0 <= count <= len(rows) or number(replay['totalRows'], True) != len(rows) or (
            number(replay['declaredFrames'], True) != frames or configured['frames'] != frames or
            configured['rows'] != len(rows) or
            not math.isclose(replay['declaredDurationMs'], duration, rel_tol=0, abs_tol=1e-6)):
        raise ValueError('Replay totals differ from preserved controller input')
    if len(replay['dispatches']) != count:
        raise ValueError('Replay dispatch count differs from applied rows')
    due = start
    for index, dispatch in enumerate(replay['dispatches']):
        mask, frames = rows[index]
        if number(dispatch['row'], True) != index or number(dispatch['mask'], True) != mask or not math.isclose(
                number(dispatch['dueMs']), due, rel_tol=0, abs_tol=1e-6):
            raise ValueError('Replay dispatch differs from supplied input')
        actual = number(dispatch['actualMs'])
        if not start <= actual <= number(replay['endedAtMs']):
            raise ValueError('Replay dispatch falls outside its observation interval')
        if actual < due - 2 or actual > due + 50:
            raise ValueError('Replay dispatch timing exceeds its explicit timer tolerance')
        if actual - due > number(replay['maxLatenessMs']) + 1e-6:
            raise ValueError('Replay hides observed timer lateness')
        due += frames * (1000 * 280896 / 16777216)
    lateness = number(replay['maxLatenessMs'])
    if number(replay['endedAtMs']) > report['endedAtMs'] or (
            replay['reason'] == 'complete' and (count != len(rows) or lateness > 50 or
            not start + duration - 2 <= replay['endedAtMs'] <= start + duration + 50)):
        raise ValueError('Replay completion scope is inconsistent')
    return {'status': replay['reason'], 'applied_rows': count, 'declared_rows': len(rows),
        'max_lateness_ms': lateness,
        'scope': 'Input-dispatch evidence only; no guest consumption or scene coverage'}


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
    inputs = report['input']
    number(inputs['count'], True)
    if number(inputs['supersededBeforeFrame'], True) > inputs['count']:
        raise ValueError('Input supersession count is inconsistent')
    distributions = [(ticks[name], ticks['count']) for name in ('rafGapMs', 'runMs', 'renderMs')]
    distributions += [(inputs[name], inputs['count']) for name in
                      ('domToDispatchMs', 'dispatchToFrameMs', 'dispatchToSubmitMs')]
    for distribution, maximum in distributions:
        number(distribution['count'], True)
        if distribution['count'] > maximum:
            raise ValueError('Timing sample count exceeds observed records')
        if distribution['count']:
            values = [number(distribution[name]) for name in ('min', 'p50', 'p95', 'p99', 'max')]
            if values != sorted(values):
                raise ValueError('Timing percentiles are inconsistent')
    if type(report['pendingInputAtEnd']) is not bool or type(report['scope']['foregroundOnly']) is not bool:
        raise ValueError('Observation scope flags must be booleans')
    final = report.get('audioFinalSnapshot')
    if report.get('audioFinalAcknowledged') is not True or not final or final.get('final') is not True:
        raise ValueError('Final audio acknowledgement is missing')
    number(final['epoch'], True)
    number(final['queueDepthFrames'])
    if 'playbackStarted' in final and type(final['playbackStarted']) is not bool:
        raise ValueError('Playback-start marker must be a boolean')
    if 'prefillTargetSourceFrames' in final and not 2 <= number(
            final['prefillTargetSourceFrames'], True) < 32768:
        raise ValueError('Audio prefill must fit inside the source ring')
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
        'warmup_output_frames': final['warmupOutputFrames'],
        'playback_started': final.get('playbackStarted'),
        'dropped_source_frames': final['droppedSourceFrames'],
        'foreground_only': report['scope']['foregroundOnly'],
        'audio_clock_observation': audio_clock_observation(report),
        'controller_replay': controller_observation(report, identity, runtime.parent),
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
