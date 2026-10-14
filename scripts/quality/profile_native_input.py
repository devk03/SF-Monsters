"""Calibrate a bounded native KEYINPUT observer; not a browser deadline test."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

from capture_core import ROOT, SOURCE, HOST_BUILD, REVISION, verified_host_build
from native_abi import verify_native_layout

FROZEN = ('capture_core.py', 'core_capture.c', 'function_fixture.c')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, output, label, timeout=60):
    with (output / (label + '.stdout')).open('x') as stdout, (
            output / (label + '.stderr')).open('x') as stderr:
        subprocess.run(list(map(str, command)), cwd=ROOT, stdout=stdout,
                       stderr=stderr, check=True, timeout=timeout)


def rows(path):
    with path.open() as source:
        return [{key: int(value) for key, value in row.items()}
                for row in csv.DictReader(source)]


def compare_outputs(control, observer, reference):
    proof = {}
    for suffix in ('rgba', 'pcm', 'state', 'sav'):
        files = [Path(str(prefix) + '.' + suffix)
                 for prefix in (control, observer, reference)]
        hashes = [digest(path) for path in files]
        if len(set(hashes)) != 1:
            raise ValueError('Observer/control/frozen capture mismatch: ' + suffix)
        proof[suffix] = {'bytes': files[0].stat().st_size, 'sha256': hashes[0]}
    return proof


def summarize(control, observer):
    baseline, frames = [rows(Path(str(prefix) + '.frames.csv'))
                        for prefix in (control, observer)]
    if not frames or len(frames) != len(baseline):
        raise ValueError('Missing or different frame counts')
    for left, right in zip(baseline, frames):
        if {k: v for k, v in left.items() if k != 'cumulative_hooks'} != {
                k: v for k, v in right.items() if k != 'cumulative_hooks'}:
            raise ValueError('Frame clock/input observations changed with observer')
    hooks = rows(Path(str(observer) + '.hooks.csv'))
    meta = json.loads(Path(str(observer) + '.json').read_text())
    if meta['frames'] != len(frames) or meta['hooks'] != len(hooks) or (
            frames[-1]['cumulative_hooks'] != len(hooks)):
        raise ValueError('Input event/frame totals are incomplete')
    previous, changes = meta['initial_held_raw'], []
    for sequence in sorted({frame['sequence'] for frame in frames}):
        block = [frame for frame in frames if frame['sequence'] == sequence]
        key = block[0]['keys']
        if key == previous:
            raise ValueError('Preexisting key state cannot prove changed-input acknowledgement')
        samples = [hook for hook in hooks if hook['sequence'] == sequence]
        ack = next((frame for frame in block if frame['held_raw'] == key), None)
        if not samples or not ack or any(hook['keys'] != key for hook in samples):
            raise ValueError('Input changed again before a real read and held-state acknowledgement')
        if any(not block[0]['frame'] <= hook['frame'] <= block[-1]['frame']
               for hook in samples):
            raise ValueError('Input sample assigned to the wrong frame block')
        latency = samples[0]['hook_entry_cycle'] - block[0]['set_cycle']
        upper = ack['end_cycle'] - block[0]['set_cycle']
        if not 0 <= latency <= upper:
            raise ValueError('Input acknowledgement chronology is inconsistent')
        changes.append({'sequence': sequence, 'keys': key,
            'hook_entry_guest_cycles': latency,
            'held_state_ack_upper_guest_cycles': upper,
            'held_state_ack_frame_samples': ack['frame'] - block[0]['frame'] + 1,
            'read_samples': len(samples)})
        previous = key
    return {'changes': changes, 'actual_readkeys_hook_entries': len(hooks),
            'frame_samples': len(frames), 'guest_cycles': meta['guest_cycles']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('rom', 'elf', 'state', 'input'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--step', action='store_true',
                        help='Also calibrate event-drained instruction stepping and raw call events')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,43}', args.name):
        parser.error('Use a new lowercase name of at most44 characters')
    battery = args.state.with_suffix('.sav')
    metadata = args.state.with_suffix('.json')
    inputs = [args.rom, args.elf, args.state, args.input, battery, metadata]
    if any(not path.is_file() for path in inputs):
        parser.error('All inputs, state metadata and companion Flash must exist')
    identities = {str(path.resolve()): digest(path) for path in inputs}
    rom = args.rom.read_bytes()
    origin = json.loads(metadata.read_text())
    if len(rom) != 16777216 or rom[0xac:0xb0] != b'BPEE' or (
            origin.get('rom_sha256'), origin.get('mgba_revision'),
            origin.get('controller_only')) != (digest(args.rom), REVISION, True):
        parser.error('Require controller-only provenance for this exact native ROM/core')
    if not args.elf.with_suffix('.gba').is_file() or (
            digest(args.elf.with_suffix('.gba')) != digest(args.rom)):
        parser.error('ELF requires an identical companion cartridge')
    if battery.stat().st_size != 131072:
        parser.error('Require the same capture companion Flash')
    blocks = []  # Input has no header.
    for line in args.input.read_text().splitlines():
        if not re.fullmatch(r'\d+,\d+', line):
            parser.error('Input lines must be decimal keys,duration without a header')
        keys, duration = map(int, line.split(','))
        if keys >= 1024 or not 1 <= duration <= 120 or (
                keys & 0x30 == 0x30 or keys & 0xc0 == 0xc0):
            parser.error('Reject invalid/opposing masks or unbounded durations')
        blocks.append((keys, duration))
    if not 1 <= sum(duration for _, duration in blocks) <= 120:
        parser.error('Pilot limit is120 guest frames')
    core = verified_host_build()
    if subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'],
                               text=True).strip() != REVISION:
        parser.error('Pinned mGBA source changed')
    output = ROOT / '.tools/benchmarks' / args.name
    output.mkdir()  # Never replace existing evidence.
    frozen = {name: digest(ROOT / 'scripts/quality' / name) for name in FROZEN}
    source_inputs = {str(path): digest(path) for path in [Path(__file__),
        ROOT / 'scripts/quality/native_input_profile.c',
        ROOT / 'scripts/quality/input_layout.c', ROOT / 'scripts/quality/native_abi.py',
        HOST_BUILD / 'include/mgba/flags.h', HOST_BUILD / 'libmgba.a']}
    layout = verify_native_layout(ROOT / '.tools/pokeemerald-host', output,
        ROOT / 'scripts/quality/input_layout.c', [4, 0x28, 0x2a, 0x2c, 0x2e])
    linked = output / 'linked.bin'
    run(['arm-none-eabi-objcopy', '-O', 'binary', args.elf, linked], output, 'elf')
    symbols = subprocess.check_output(['arm-none-eabi-nm', '-S', '--defined-only',
                                      str(args.elf)], text=True)
    expected_sites = {'ReadKeys': (0x080005e4, 0xa0)}
    if args.step:
        expected_sites.update({'AgbMain': (0x080003a4, 0x120),
            'UpdateLinkAndCallCallbacks': (0x080004c4, 0x14),
            'CallCallbacks': (0x0800051c, 0x24), 'WaitForVBlank': (0x080008ac, 0x30),
            '_call_via_r0': (0x082ea358, 4)})
    function_hashes, binary = {}, linked.read_bytes()
    if not re.search(r'(?m)^030022c0 \w+ [bB] gMain$', symbols):
        raise ValueError('Validated Main address changed')
    for name, expected in expected_sites.items():
        match = re.findall(r'(?m)^([0-9a-f]+) ([0-9a-f]+) [tT] ' + name + '$', symbols)
        if len(match) != 1 or tuple(int(value, 16) for value in match[0]) != expected:
            raise ValueError('Validated function span changed: ' + name)
        address, size = expected
        offset = address - 0x08000000
        if binary[offset:offset + size] != rom[offset:offset + size]:
            raise ValueError('ELF function bytes differ from tested ROM: ' + name)
        function_hashes[name] = hashlib.sha256(rom[offset:offset + size]).hexdigest()
    executable = output / 'native_input_profile'
    source = ROOT / 'scripts/quality/native_input_profile.c'
    frameworks = ['-framework', 'CoreFoundation'] if platform.system() == 'Darwin' else []
    run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-D_GNU_SOURCE', '-DBUILD_STATIC',
        '-I' + str(SOURCE / 'include'), '-I' + str(HOST_BUILD / 'include'), source,
        HOST_BUILD / 'libmgba.a', '-lm', '-lpthread', *frameworks, '-o', executable],
        output, 'compile')
    run([executable, '--clock-test'], output, 'clock')
    modes = ['control', 'observe'] + (['step-control', 'step-observe'] if args.step else [])
    for mode in modes:
        run([executable, args.rom, args.state, battery, args.input, output / mode, mode],
            output, mode)
    reference_name = args.name + '-frozen-control'
    run([sys.executable, ROOT / 'scripts/quality/capture_core.py', '--backend', 'host',
        '--rom', args.rom, '--state', args.state, '--input', args.input,
        '--name', reference_name], output, 'frozen-control')
    calibration = compare_outputs(output / 'control', output / 'observe',
        ROOT / '.tools/benchmarks' / reference_name / 'capture')
    step_calibration = None
    if args.step:
        step_calibration = compare_outputs(output / 'control', output / 'step-control',
                                           output / 'step-observe')
        if summarize(output / 'control', output / 'step-observe') != summarize(
                output / 'control', output / 'observe'):
            raise ValueError('Instruction stepping changed input sample observations')
        if (output / 'step-observe.hooks.csv').read_bytes() != (output / 'observe.hooks.csv').read_bytes():
            raise ValueError('Instruction stepping changed actual hook-entry cycles')
    observations = summarize(output / 'control', output / 'observe')
    if observations['frame_samples'] != sum(duration for _, duration in blocks):
        raise ValueError('Observed duration differs from the complete input sequence')
    if any(digest(Path(path)) != identity for path, identity in identities.items()) or (
            frozen != {name: digest(ROOT / 'scripts/quality' / name) for name in FROZEN}):
        raise ValueError('An input or frozen capture helper changed')
    if any(digest(Path(path)) != identity for path, identity in source_inputs.items()):
        raise ValueError('Profiler sources/build inputs changed during compilation or capture')
    receipt = {'passed': True, 'inputs': identities, 'core': core, 'layout': layout,
        'profiler_sha256': digest(source), 'wrapper_sha256': digest(Path(__file__)),
        'flags_sha256': digest(HOST_BUILD / 'include/mgba/flags.h'),
        'executable_sha256': digest(executable), 'frozen_helpers': frozen,
        'source_inputs_before_compile': source_inputs,
        'calibration': calibration, 'step_calibration': step_calibration,
        'function_sha256': function_hashes, 'observations': observations,
        'raw_instruction_events_sha256': digest(output / 'step-observe.events.csv') if args.step else None,
        'mode_artifacts': {mode: {suffix: digest(output / (mode + '.' + suffix))
            for suffix in ('json', 'frames.csv', 'hooks.csv', 'events.csv')} for mode in modes},
        'clock': 'Unsigned-unwrapped mTimingCurrentTime; relative to loaded state',
        'limits': ['At most120 native guest frames; not a ten-minute run',
            'KEYINPUT hook entry precedes the instruction completion charge',
            'Held-state ACK sampled at frame end is an upper bound',
            'Step events are executed native transitions; partial spans need separate interpretation',
            'No render-deadline or browser/mobile timing proof',
            'Wall emulation timings are pilot overhead observations, not a performance gate']}
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Calibrated native input pilot:', output)


if __name__ == '__main__':
    main()
