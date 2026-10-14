"""Observe native critical-hit, PP and HP commands; no campaign saves are edited."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
from mechanics_fixtures import ROOT, battle_setup, build_driver, constants, digest, verify_bundle

FUNCTIONS = {'critical': 'Cmd_critcalc', 'pp': 'Cmd_ppreduce', 'hp': 'Cmd_datahpupdate'}
SLOTS = ('attacker', 'defender', 'ally', 'opponent_ally')


def validate(document):
    profile, cases = document.get('profile'), document.get('cases')
    if profile not in FUNCTIONS or not isinstance(cases, list) or not 1 <= len(cases) <= 128:
        raise ValueError('Use a supported command profile and1–128 scenarios.')
    ids = set()
    for case in cases:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', case.get('id', '')) or case['id'] in ids:
            raise ValueError('Command IDs must be unique safe names.')
        ids.add(case['id'])
        allowed = {'id', 'derivation', *SLOTS, 'move', 'double', 'absent', 'rng_seed', 'expected'}
        allowed |= {'critical': {'no_crit', 'battle_flags'},
                    'pp': {'pp', 'hitmarker', 'pressure_exempt', 'mimicked', 'controller_busy'},
                    'hp': {'damage', 'result_flags', 'hitmarker', 'substitute_hp', 'controller_busy'}}[profile]
        if set(case) - allowed or not case.get('derivation'):
            raise ValueError('Reject unknown command controls or missing derivations.')
        for key in ('double', 'no_crit', 'pressure_exempt', 'mimicked', 'controller_busy'):
            if key in case and type(case[key]) is not bool:
                raise ValueError('Command switches must be boolean.')
        if type(case.get('rng_seed', 0)) is not int or not 0 <= case.get('rng_seed', 0) <= 0xffffffff:
            raise ValueError('RNG seed must be32-bit.')
        required = {'critical': {'critical', 'pointer', 'rng'},
                    'pp': {'pp', 'pointer', 'controller', 'hitmarker', 'rng'},
                    'hp': {'hp', 'dealt', 'substitute_hp', 'physical', 'special', 'shell_bell',
                           'bide', 'pointer', 'controller', 'hitmarker', 'rng'}}[profile]
        expected = case.get('expected')
        if not isinstance(expected, dict) or set(expected) != required or any(type(v) is not int for v in expected.values()):
            raise ValueError('Every native observable needs an explicit integer expectation.')
        for key in ('pp', 'substitute_hp'):
            if key in case and (type(case[key]) is not int or not 0 <= case[key] <= 255):
                raise ValueError('PP and substitute HP must fit native bytes.')
        if 'damage' in case and (type(case['damage']) is not int or not -1000000 <= case['damage'] <= 1000000):
            raise ValueError('Use bounded signed HP damage.')
    return profile, cases


def program(profile, case, syms, resolve):
    controls = {key: value for key, value in case.items() if key in {*SLOTS, 'move', 'double', 'absent', 'rng_seed'}}
    controls['rng_seed'] = case.get('rng_seed', 0)
    lines = battle_setup(controls, syms, resolve)
    script = 0x0203f600
    disable, special = bytearray(112), bytearray(80)
    if case.get('mimicked'):
        disable[24] = 0x10  # mimickedMoves slot0 is bit4, after the low bitfields.
    disable[28 + 10] = case.get('substitute_hp', 0)
    if case.get('pressure_exempt'):
        special[0] = 0x20
    writes = {'gBattlescriptCurrInstr': struct.pack('<I', script),
              'gHitMarker': struct.pack('<I', resolve(case.get('hitmarker', 0))),
              'gBattleTypeFlags': struct.pack('<I', case.get('battle_flags', 9 if case.get('double') else 8)),
              'gBattleControllerExecFlags': struct.pack('<I', int(case.get('controller_busy', False))),
              'gMoveResultFlags': bytes([case.get('result_flags', 0)]),
              'gDisableStructs': bytes(disable), 'gSpecialStatuses': bytes(special),
              'gCurrMovePos': b'\0', 'gCritMultiplier': b'\1', 'gHpDealt': bytes(4),
              'gBideDmg': bytes(16), 'gBideTarget': bytes(4),
              'gStatuses3': struct.pack('<4I', resolve('STATUS3_CANT_SCORE_A_CRIT') if case.get('no_crit') else 0, 0, 0, 0)}
    for name, data in writes.items():
        lines.append(f'write {syms[name][0]:x} {data.hex()}')
    if profile == 'pp':
        lines.append(f'write {syms["gBattleMons"][0] + 36:x} {case.get("pp", 10):02x}')
    if profile == 'hp':
        lines.append(f'write {syms["gBattleMoveDamage"][0]:x} ' + struct.pack('<i', case.get('damage', 20)).hex())
    # BS_TARGET=0; the command chooses the actual target slot initialized above.
    lines += [f'write {script:x} 0000', f'call {syms[FUNCTIONS[profile]][0]:x} 0 0 0 0 0 0 0 0']
    reads = {'pointer': (syms['gBattlescriptCurrInstr'][0], 4, False),
             'rng': (syms['gRngValue'][0], 4, False)}
    if profile == 'critical':
        reads['critical'] = (syms['gCritMultiplier'][0], 1, False)
    else:
        reads.update({'controller': (syms['gBattleControllerExecFlags'][0], 4, False),
                      'hitmarker': (syms['gHitMarker'][0], 4, False)})
    if profile == 'pp':
        reads['pp'] = (syms['gBattleMons'][0] + 36, 1, False)
    if profile == 'hp':
        reads.update({'hp': (syms['gBattleMons'][0] + 88 + 40, 2, False),
                      'dealt': (syms['gHpDealt'][0], 4, True),
                      'substitute_hp': (syms['gDisableStructs'][0] + 28 + 10, 1, False),
                      'physical': (syms['gProtectStructs'][0] + 16 + 4, 4, False),
                      'special': (syms['gProtectStructs'][0] + 16 + 8, 4, False),
                      'shell_bell': (syms['gSpecialStatuses'][0] + 20 + 4, 4, True),
                      'bide': (syms['gBideDmg'][0] + 4, 4, False)})
    lines += [f'read {address:x} {size:x}' for address, size, _ in reads.values()]
    return '\n'.join(lines) + '\n', reads


def run_side(label, profile, rom, elf, state, executable, cases, resolve, output):
    identity, syms = verify_bundle(label, rom, elf, state, output, {FUNCTIONS[profile]})
    programs = [program(profile, case, syms, resolve) for case in cases]
    if len({s for s, _ in programs}) != len(cases):
        raise ValueError('Duplicate effective command fixtures cannot add coverage.')
    sequence = ''.join(s for s, _ in programs)
    (output / (label + '-commands.txt')).write_text(sequence)
    process = subprocess.run([str(executable), str(rom), str(state)], input=sequence,
                             capture_output=True, text=True, timeout=60)
    (output / (label + '-stdout.txt')).write_text(process.stdout)
    (output / (label + '-stderr.txt')).write_text(process.stderr)
    lines, observed = process.stdout.splitlines(), []
    if process.returncode or digest(rom) != identity['rom_sha256']:
        raise ValueError('Command fixture failed or changed its input ROM.')
    for case, (_, reads) in zip(cases, programs):
        count = len(reads) + 2
        chunk, lines = lines[:count], lines[count:]
        if len(chunk) != count or not re.fullmatch(r'return [0-9a-f]{8} steps \d+', chunk[1]):
            raise ValueError('Command returned incomplete observations.')
        actual = {key: int.from_bytes(bytes.fromhex(raw), 'little', signed=spec[2])
                  for (key, spec), raw in zip(reads.items(), chunk[2:])}
        observed.append({'id': case['id'], 'actual': actual, 'expected': case['expected'],
                         'pass': actual == case['expected'] and int.from_bytes(bytes.fromhex(chunk[0]), 'little') == case.get('rng_seed', 0)})
    if lines:
        raise ValueError('Unexpected extra native observations.')
    return {**identity, 'cases': observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom', 'reference-elf', 'reference-state', 'candidate-rom', 'candidate-elf', 'candidate-state', 'cases'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name):
        parser.error('Use a safe evidence name.')
    output = ROOT / '.tools/benchmarks' / args.name
    if output.exists():
        parser.error('Choose a new evidence directory.')
    profile, cases = validate(json.loads(args.cases.read_text()))
    output.mkdir(parents=True)
    executable, core = build_driver()
    resolve = constants(ROOT / '.tools/pokeemerald-host')
    evidence = {'kind': 'controlled native command, not controller/campaign or durable save evidence',
                'profile': profile, 'core': core, 'cases_sha256': digest(args.cases),
                'runner_sha256': digest(Path(__file__)),
                'shared_runner_sha256': digest(ROOT / 'scripts/quality/mechanics_fixtures.py'),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                'sides': {}}
    for side in ('reference', 'candidate'):
        evidence['sides'][side] = run_side(side, profile, getattr(args, side + '_rom'), getattr(args, side + '_elf'),
            getattr(args, side + '_state'), executable, cases, resolve, output)
    rows = [{'id': c['id'], 'double': c.get('double', False), 'pass': a['pass'] and b['pass']}
            for c, a, b in zip(cases, evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases'])]
    evidence.update({'results': rows, 'passed': sum(r['pass'] for r in rows), 'total': len(rows),
                     'full_mechanics_gate_complete': False, 'human_quality_approval': 'pending'})
    (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'passed': evidence['passed'], 'total': len(rows), 'evidence': str(output)}))
    if evidence['passed'] != len(rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
