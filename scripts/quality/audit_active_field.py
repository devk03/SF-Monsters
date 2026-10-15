"""Qualify one bounded field pipeline observation; full performance stays separate."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_web_performance import audit

ROOT = Path(__file__).resolve().parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def qualify(report, identity, directory, specification):
    observation = audit(report, identity, directory/'runtime')
    route = (directory/'route.csv').read_bytes()
    rows = [tuple(map(int, line.split(','))) for line in route.decode('ascii').strip().splitlines()]
    frames = sum(count for mask,count in rows)
    held = sum(count for mask,count in rows if mask & 0xF0)
    seconds = frames*280896/16777216
    replay = report.get('controllerReplay') or {}
    ticks = report['ticks']
    final = report['audioFinalSnapshot']
    configured = identity.get('controller_route') or {}
    verified_replay = observation.get('controller_replay') or {}
    checks = {
        'exact_cartridge': identity.get('rom_sha256') == specification['target_sha256'],
        'exact_route_bytes': sha(route) == specification['input_sha256'] == identity['files'].get('route.csv'),
        'declared_route_totals': len(rows) == specification['rows'] and frames == specification['frames']
            and held == specification['held_frames'],
        'nearly_full_directional_route': all(mask in (0,16,32,128) and count > 0
            for mask,count in rows) and 590 <= seconds <= 599 and held/frames >= 0.95,
        'verified_replay_dispatches': verified_replay.get('status') == 'complete'
            and configured.get('rows') == len(rows) and configured.get('frames') == frames,
        '600_second_duration_end': report['reason'] == 'duration'
            and report['durationMs'] == specification['expected_measurement_ms'] == 600000
            and report['elapsedMs'] >= 600000,
        'uninterrupted_foreground': all(report['scope'].get(key) is True
            for key in ('valid','uninterrupted','foregroundOnly')) and ticks['hidden'] == 0,
        'complete_route': replay.get('reason') == 'complete' and replay.get('error') is None
            and replay.get('appliedRows') == replay.get('totalRows') == len(rows),
        'only_planned_keyboard_events': report['input']['count'] == len(rows),
        'final_input_consumed_by_pipeline': report['pendingInputAtEnd'] is False,
        'no_discarded_frame_debt': ticks['discardedFrames'] == 0,
        'executed_video_accounting': ticks['executedFrames'] == ticks['actualVideoFrames']
            and ticks['videoFrameMismatchTicks'] == 0 and ticks['executedFrames'] > 0,
        'audio_running_and_primed': report['context'].get('audioState') == 'running'
            and final.get('playbackStarted') is True and final['warmupOutputFrames'] == 0,
        'zero_audio_loss': final['underrunOutputFrames'] == final['droppedSourceFrames'] == 0,
    }
    return {'passed': all(checks.values()), 'checks': checks, 'observation': observation,
        'route_seconds': seconds, 'held_fraction': held/frames,
        'scope': 'One600second browser field pipeline observation. Actual scene/motion require separate visible evidence. '
            'No guest-key consumption,99%guest deadlines, physical paint/input, native real-time, Safari/phone, '
            'listening, other workload classes or full performance approval.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--specification',type=Path,default=ROOT/'data/quality/park-active-field.json')
    args = parser.parse_args()
    report_bytes = args.report.read_bytes()
    identity_bytes = (args.report.parent/'identity.json').read_bytes()
    specification_bytes = args.specification.read_bytes()
    source = Path(__file__).read_bytes()
    dependency = Path(__file__).with_name('audit_web_performance.py').read_bytes()
    try:
        result = qualify(json.loads(report_bytes),json.loads(identity_bytes),args.report.parent,
                         json.loads(specification_bytes))
    except (OSError,ValueError,TypeError,KeyError,ZeroDivisionError) as error:
        result = {'passed':False,'errors':[str(error)],'scope':__doc__}
    result.update({'report_sha256':sha(report_bytes),'identity_sha256':sha(identity_bytes),
        'specification_sha256':sha(specification_bytes),'auditor_sha256':sha(source),
        'dependency_sha256':sha(dependency)})
    output = args.report.with_suffix('.active-field.audit.json')
    with output.open('x') as file:file.write(json.dumps(result,indent=2)+'\n')
    for suffix,data in [('.active-field.auditor.py',source),('.active-field.dependency.py',dependency)]:
        with args.report.with_suffix(suffix).open('xb') as file:file.write(data)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
