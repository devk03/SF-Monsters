"""Execute native accuracy script commands against explicit hit/RNG oracles."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
from mechanics_fixtures import ROOT, battle_setup, build_driver, constants, digest, verify_bundle

FUNCTION = 'Cmd_accuracycheck'
SLOTS = ('attacker', 'defender', 'ally', 'opponent_ally')


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 128:
        raise ValueError('Supply1–128 accuracy scenarios.')
    ids = set()
    for case in cases:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', case.get('id', '')) or case['id'] in ids:
            raise ValueError('Accuracy IDs must be unique safe names.')
        ids.add(case['id'])
        allowed = {'id', 'derivation', 'move', *SLOTS, 'double', 'absent', 'weather',
                   'rng_seed', 'expected_rng', 'expected_hit', 'expected_flags', 'expected_message',
                   'target_status3', 'hitmarker', 'expected_hitmarker', 'protect', 'sure_hit_battler'}
        if set(case) - allowed or not case.get('derivation'):
            raise ValueError('Reject unknown accuracy controls or missing derivations.')
        for key in ('expected_hit', 'double', 'protect'):
            if type(case.get(key, False)) is not bool or key == 'expected_hit' and key not in case:
                raise ValueError('Use explicit boolean accuracy outcomes/switches.')
        for key in ('rng_seed', 'expected_rng'):
            if type(case.get(key)) is not int or not 0 <= case[key] <= 0xffffffff:
                raise ValueError('Explicit seed and resulting32-bit RNG are required.')
        for key in ('expected_flags', 'expected_message'):
            if type(case.get(key)) is not int or not 0 <= case[key] <= 255:
                raise ValueError('Explicit byte-sized result/message expectations are required.')
        if type(case.get('sure_hit_battler', 0)) is not int or not 0 <= case.get('sure_hit_battler', 0) <= 3:
            raise ValueError('Sure-hit owner must be a battler slot.')
    return cases


def program(case, syms, resolve):
    controls = {key: value for key, value in case.items() if key in {*SLOTS, 'move', 'double', 'absent', 'weather', 'rng_seed'}}
    lines = battle_setup(controls, syms, resolve)
    script, failure = 0x0203f600, 0x0203f680
    disable = bytearray(112)
    disable[28 + 21] = case.get('sure_hit_battler', 0)
    protect = bytearray(64)
    protect[16] = int(case.get('protect', False))
    writes = {'gBattlescriptCurrInstr': struct.pack('<I', script),
              'gHitMarker': struct.pack('<I', resolve(case.get('hitmarker', 0))),
              'gMoveResultFlags': b'\0', 'gDisableStructs': bytes(disable),
              'gBattleCommunication': bytes(8), 'gLastUsedAbility': b'\0',
              'gLastLandedMoves': bytes(8), 'gLastHitByType': bytes(8),
              'gProtectStructs': bytes(protect),
              'gStatuses3': struct.pack('<4I', 0, resolve(case.get('target_status3', 0)), 0, 0)}
    for name, data in writes.items():
        lines.append(f'write {syms[name][0]:x} {data.hex()}')
    # Command opcode1, failure pointer, ACC_CURR_MOVE=0; RAM scripts are not ROM edits.
    lines += [f'write {script:x} ' + (b'\1' + struct.pack('<I', failure) + b'\0\0').hex(),
              f'call {syms[FUNCTION][0]:x} 0 0 0 0 0 0 0 0',
              f'read {syms["gBattlescriptCurrInstr"][0]:x} 4',
              f'read {syms["gMoveResultFlags"][0]:x} 1',
              f'read {syms["gBattleCommunication"][0] + 6:x} 1',
              f'read {syms["gHitMarker"][0]:x} 4', f'read {syms["gRngValue"][0]:x} 4']
    return '\n'.join(lines) + '\n'


def run_side(label, rom, elf, state, executable, cases, resolve, output):
    identity, syms = verify_bundle(label, rom, elf, state, output, {FUNCTION})
    programs = [program(case, syms, resolve) for case in cases]
    if len(set(programs)) != len(cases):
        raise ValueError('Duplicate effective accuracy fixtures cannot add coverage.')
    sequence = ''.join(programs)
    (output / (label + '-commands.txt')).write_text(sequence)
    process = subprocess.run([str(executable), str(rom), str(state)], input=sequence,
                             capture_output=True, text=True, timeout=60)
    (output / (label + '-stdout.txt')).write_text(process.stdout)
    (output / (label + '-stderr.txt')).write_text(process.stderr)
    lines = process.stdout.splitlines()
    if process.returncode or len(lines) != 7 * len(cases) or digest(rom) != identity['rom_sha256']:
        raise ValueError('Accuracy observations incomplete or input ROM changed.')
    observed = []
    for index, case in enumerate(cases):
        before, returned, *raw = lines[index * 7:(index + 1) * 7]
        if not re.fullmatch(r'return [0-9a-f]{8} steps \d+', returned):
            raise ValueError('Accuracy command did not return cleanly.')
        pointer, flags, message, marker, rng = [int.from_bytes(bytes.fromhex(v), 'little') for v in raw]
        expected = {'pointer': 0x0203f607 if case['expected_hit'] else 0x0203f680,
                    'flags': case['expected_flags'], 'message': case['expected_message'],
                    'hitmarker': resolve(case.get('expected_hitmarker', 0)), 'rng': case['expected_rng']}
        actual = dict(zip(expected, (pointer, flags, message, marker, rng)))
        observed.append({'id': case['id'], 'actual': actual, 'expected': expected,
                         'pass': actual == expected and int.from_bytes(bytes.fromhex(before), 'little') == case['rng_seed']})
    return {**identity, 'cases': observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom', 'reference-elf', 'reference-state', 'candidate-rom', 'candidate-elf', 'candidate-state'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--cases', type=Path, default=ROOT / 'data/quality/mechanics/accuracy.json')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name):
        parser.error('Use a safe evidence name.')
    output = ROOT / '.tools/benchmarks' / args.name
    if output.exists():
        parser.error('Choose a new evidence directory.')
    cases = validate(json.loads(args.cases.read_text()))
    output.mkdir(parents=True)
    executable, core = build_driver()
    resolve = constants(ROOT / '.tools/pokeemerald-host')
    evidence = {'kind': 'controlled native accuracy command, not complete attacks or campaign evidence',
                'core': core, 'cases_sha256': digest(args.cases), 'runner_sha256': digest(Path(__file__)),
                'shared_runner_sha256': digest(ROOT / 'scripts/quality/mechanics_fixtures.py'),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                'sides': {}}
    for side in ('reference', 'candidate'):
        evidence['sides'][side] = run_side(side, getattr(args, side + '_rom'), getattr(args, side + '_elf'),
            getattr(args, side + '_state'), executable, cases, resolve, output)
    rows = [{'id': case['id'], 'double': case.get('double', False), 'pass': a['pass'] and b['pass']}
            for case, a, b in zip(cases, evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases'])]
    evidence.update({'results': rows, 'passed': sum(row['pass'] for row in rows), 'total': len(rows),
                     'full_mechanics_gate_complete': False, 'human_quality_approval': 'pending'})
    (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'passed': evidence['passed'], 'total': len(rows), 'evidence': str(output)}))
    if evidence['passed'] != len(rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
