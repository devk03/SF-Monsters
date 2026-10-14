"""Interpret calibrated guest transitions, preserving capture-edge partial spans."""
import argparse
from bisect import bisect_right
from collections import Counter
import hashlib
import json
from pathlib import Path

from profile_native_input import compare_outputs, digest, rows


def stats(values):
    ordered = sorted(values)
    if not ordered:
        return {'count': 0}
    return {'count': len(values), 'min': ordered[0], 'max': ordered[-1],
            'p50_nearest_rank': ordered[(len(values) + 1) // 2 - 1],
            'p95_nearest_rank': ordered[(95 * len(values) + 99) // 100 - 1]}


def analyze(events):
    spans = {name: [] for name in ('loop_start_period', 'loop_through_wait_return',
             'callback1', 'callback2', 'wait', 'work_through_wait_clear')}
    counts, partial = Counter(), Counter()
    active, loop, prior_start, prior_time = {}, None, None, -1
    clears, vblanks, previous_vblank_counter = [], [], None
    seen_loop = seen_wait_return = False
    starts = {6: ('callback1', 8), 7: ('callback2', 9), 10: ('wait', 12)}
    for item in events:
        kind, time = item['kind'], item['completion_cycle']
        if kind not in range(1, 14) or time < prior_time:
            raise ValueError('Unknown event or nonmonotonic completion clock')
        prior_time = time
        counts[kind] += 1
        if kind == 1:
            if loop is not None or active:
                raise ValueError('New loop overlaps an unfinished observed span')
            if prior_start is not None:
                spans['loop_start_period'].append(time - prior_start)
            loop = prior_start = time
            seen_loop = True
        if kind in starts:
            name, _ = starts[kind]
            if active:
                raise ValueError('Overlapping callback/wait span')
            active[name] = {'start': time, 'clear': None}
        if kind == 11:
            if 'wait' not in active or active['wait']['clear'] is not None:
                raise ValueError('Wait clear lacks one matching observed entry')
            active['wait']['clear'] = time
            if loop is not None:
                spans['work_through_wait_clear'].append(time - loop)
                clears.append((loop, time))
        for name, finish in starts.values():
            if kind != finish:
                continue
            if name not in active:
                if name != 'wait' or seen_loop or seen_wait_return:
                    raise ValueError('Unmatched return outside initial capture edge')
                partial['initial_wait_return'] += 1
            else:
                pending = active.pop(name)
                if name == 'wait' and pending['clear'] is None:
                    raise ValueError('Wait returned without observed flag clear')
                spans[name].append(time - pending['start'])
        if kind == 12:
            if loop is None:
                if seen_loop or seen_wait_return:
                    raise ValueError('Unmatched loop return outside initial capture edge')
                partial['initial_loop_return'] += 1
            else:
                spans['loop_through_wait_return'].append(time - loop)
                loop = None
            seen_wait_return = True
        if kind == 13:
            late = item['value']
            if not 0 <= late <= 1008 or time < late:
                raise ValueError('Invalid VBlank delivery lateness')
            nominal = time - late
            if vblanks and nominal - vblanks[-1] != 280896:
                raise ValueError('Nominal VBlank period differs from pinned core')
            if previous_vblank_counter is not None and ((
                    item['to'] - previous_vblank_counter) & 0xffffffff) != 1:
                raise ValueError('Missing video callback ordinal')
            previous_vblank_counter = item['to']
            vblanks.append(nominal)
    for name in active:
        partial['trailing_' + name] += 1
    if loop is not None:
        partial['trailing_loop'] += 1
    margins, unscored = [], 0
    for start, clear in clears:
        index = bisect_right(vblanks, start)
        if index == len(vblanks):
            unscored += 1
        else:
            margins.append(vblanks[index] - clear)
    return {'event_counts': dict(counts), 'complete_guest_cycle_spans': {
        name: stats(values) for name, values in spans.items()}, 'edge_partials': dict(partial),
        'nominal_vblank_events': len(vblanks), 'work_clear_next_vblank': {
            'definition': 'Wait flag-clear completion versus first nominal VBlank after loop start',
            'scored': len(margins), 'met': sum(value >= 0 for value in margins),
            'missed': sum(value < 0 for value in margins), 'unscored_edge': unscored,
            'margin_guest_cycles': stats(margins)},
        'scope': 'Short native guest-work observation; no display/host performance acceptance'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    args = parser.parse_args()
    receipt_path = args.capture / 'receipt.json'
    receipt = json.loads(receipt_path.read_text())
    event_path = args.capture / 'step-observe.events.csv'
    if receipt.get('passed') is not True or not receipt.get('step_calibration') or (
            digest(event_path) != receipt.get('raw_instruction_events_sha256')):
        raise ValueError('Require accepted step calibration and its exact raw events')
    calibration = compare_outputs(args.capture / 'control', args.capture / 'step-control',
                                  args.capture / 'step-observe')
    if calibration != receipt['step_calibration']:
        raise ValueError('Calibrated outputs changed')
    report = analyze(rows(event_path))
    metadata_path = args.capture / 'step-observe.json'
    if digest(metadata_path) != receipt['mode_artifacts']['step-observe']['json']:
        raise ValueError('Step metadata changed after calibration')
    metadata = json.loads(metadata_path.read_text())
    if metadata.get('event_schema') != 1:
        raise ValueError('Unsupported native event schema')
    if report['nominal_vblank_events'] != metadata['frames']:
        raise ValueError('Not every captured video frame has a VBlank observation')
    report.update({'receipt_sha256': digest(receipt_path),
        'analyzer_sha256': digest(Path(__file__)),
        'events_sha256': hashlib.sha256(event_path.read_bytes()).hexdigest()})
    with (args.capture / 'loop-summary.json').open('x') as target:
        target.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
