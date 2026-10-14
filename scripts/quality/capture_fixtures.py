"""Observe native capture commands in scratch RAM; never export a campaign save."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
from mechanics_fixtures import ROOT, battle_setup, build_driver, constants, digest, verify_bundle
from stat_fixtures import property_ids

FUNCTIONS = {'Cmd_handleballthrow', 'CreateMon', 'SetMonData', 'GetMonData2'}
ALLOCATIONS = {'gBattleBufferA': 2048, 'gBattleResults': 68, 'gEnemyParty': 600,
               'gPlayerParty': 600, 'gPlayerPartyCount': 1, 'gBattlerPartyIndexes': 8,
               'gLastUsedItem': 2, 'gMapHeader': 28}
SCRIPTS = {'BattleScript_' + suffix for suffix in
           ('TrainerBallBlock', 'WallyBallThrow', 'SuccessBallThrow', 'ShakeBallThrow')}
BALLS = {'ITEM_' + name + '_BALL' for name in
         ('POKE', 'GREAT', 'ULTRA', 'MASTER', 'NET', 'DIVE', 'NEST', 'TIMER', 'LUXURY', 'PREMIER')}
EXPECTED = {'pointer', 'animation', 'controller', 'rng', 'attempts', 'master',
            'caught_ball', 'chooser', 'party_count'}


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 128:
        raise ValueError('Use1–128 independent capture-command scenarios.')
    seen = set()
    for case in cases:
        allowed = {'id', 'derivation', 'ball', 'species', 'hp', 'max_hp', 'level',
                   'status', 'type1', 'type2', 'rng_seed', 'turn', 'attempt_count',
                   'full_party', 'controller_busy', 'trainer', 'tutorial', 'underwater', 'expected'}
        if set(case) - allowed or not case.get('derivation'):
            raise ValueError('Reject ignored capture controls and missing independent derivations.')
        ident = case.get('id', '')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', ident) or ident in seen:
            raise ValueError('Capture IDs must be unique safe names.')
        seen.add(ident)
        if case.get('ball') not in BALLS:
            raise ValueError('Use a supported native ball, excluding unaudited Safari/Repeat setup.')
        for key in ('full_party', 'controller_busy', 'trainer', 'tutorial', 'underwater'):
            if type(case.get(key, False)) is not bool:
                raise ValueError('Capture switches must be boolean.')
        for key, default, lo, hi in [('hp', 30, 1, 65535), ('max_hp', 90, 1, 65535),
                                    ('level', 50, 1, 100), ('turn', 0, 0, 245),
                                    ('attempt_count', 0, 0, 255), ('rng_seed', 0, 0, 0xffffffff)]:
            value = case.get(key, default)
            if type(value) is not int or not lo <= value <= hi:
                raise ValueError('Invalid bounded capture control: ' + key)
        if case.get('hp', 30) > case.get('max_hp', 90):
            raise ValueError('Capture HP cannot exceed maximum HP.')
        expected = case.get('expected')
        if not isinstance(expected, dict) or set(expected) != EXPECTED:
            raise ValueError('Every capture observable needs an explicit expectation.')
        for key, value in expected.items():
            if key == 'pointer' and isinstance(value, str) and value in SCRIPTS:
                continue
            if type(value) is not int or value < 0:
                raise ValueError('Capture oracles need native integers or approved script roles.')
    return cases


def program(case, syms, resolve, properties):
    defender = {key: case[key] for key in ('species', 'hp', 'max_hp', 'level', 'status', 'type1', 'type2') if key in case}
    defender.setdefault('species', 'SPECIES_BULBASAUR')
    defender.setdefault('hp', 30)
    defender.setdefault('max_hp', 90)
    lines = battle_setup({'defender': defender, 'rng_seed': case.get('rng_seed', 0)}, syms, resolve)
    party_count = 6 if case.get('full_party') else 1
    results, communication, map_header = bytearray(68), bytearray(8), bytearray(28)
    results[0x13] = case.get('turn', 0)
    ball = resolve(case['ball'])
    attempt_offset = 0x36 + ball - resolve('ITEM_ULTRA_BALL')
    if case['ball'] != 'ITEM_MASTER_BALL':
        results[attempt_offset] = case.get('attempt_count', 0)
    communication[5] = 170  # MULTISTRING_CHOOSER sentinel.
    map_header[0x17] = 5 if case.get('underwater') else 1
    flags = (resolve('BATTLE_TYPE_TRAINER') if case.get('trainer') else 0) | (
        resolve('BATTLE_TYPE_WALLY_TUTORIAL') if case.get('tutorial') else 0)
    writes = {'gBattleResults': results, 'gBattleCommunication': communication,
              'gBattleBufferA': bytes([165]) * 2048, 'gMapHeader': map_header,
              'gBattleControllerExecFlags': struct.pack('<I', int(case.get('controller_busy', False))),
              'gBattleTypeFlags': struct.pack('<I', flags), 'gBattlerPartyIndexes': bytes(8),
              'gEnemyParty': bytes(600), 'gPlayerParty': bytes(600),
              'gPlayerPartyCount': bytes([party_count]), 'gLastUsedItem': struct.pack('<H', ball),
              'gBattlescriptCurrInstr': struct.pack('<I', 0x0203f600)}
    for name, value in writes.items():
        # The guarded driver's text parser accepts at most4095 hex characters.
        for offset in range(0, len(value), 1024):
            lines.append(f'write {syms[name][0] + offset:x} {value[offset:offset + 1024].hex()}')

    def call(name, *args):
        lines.append(f'call {syms[name][0]:x} ' + ' '.join(f'{v:x}' for v in (*args, *([0] * (8 - len(args))))))

    enemy = syms['gEnemyParty'][0]
    call('CreateMon', enemy, resolve(defender['species']), case.get('level', 50), 31, 1, 0, 1, 0)
    for index in range(party_count):
        call('CreateMon', syms['gPlayerParty'][0] + index * 100, resolve('SPECIES_BULBASAUR'), 5, 31, 1, 0, 1, 0)
    lines.append('write 203f500 04000000')  # Initial native Poké Ball; detect success mutation.
    call('SetMonData', enemy, properties['MON_DATA_POKEBALL'], 0x0203f500)
    # Creation is setup, not capture RNG. Explicitly seed the command itself.
    lines.append(f'write {syms["gRngValue"][0]:x} ' + struct.pack('<I', case.get('rng_seed', 0)).hex())
    call('Cmd_handleballthrow')
    call('GetMonData2', enemy, properties['MON_DATA_POKEBALL'])
    reads = {'pointer': (syms['gBattlescriptCurrInstr'][0], 4),
             'animation': (syms['gBattleBufferA'][0] + 1, 1),
             'controller': (syms['gBattleControllerExecFlags'][0], 4),
             'rng': (syms['gRngValue'][0], 4),
             'attempts': (syms['gBattleResults'][0] + (attempt_offset if ball != resolve('ITEM_MASTER_BALL') else 0x36), 1),
             'master': (syms['gBattleResults'][0] + 5, 1),
             'chooser': (syms['gBattleCommunication'][0] + 5, 1),
             'party_count': (syms['gPlayerPartyCount'][0], 1)}
    lines += [f'read {address:x} {size:x}' for address, size in reads.values()]
    return '\n'.join(lines) + '\n', reads


def run_side(label, rom, elf, state, executable, cases, resolve, properties, output):
    identity, syms = verify_bundle(label, rom, elf, state, output, FUNCTIONS, ALLOCATIONS)
    scripts = {}
    for line in subprocess.check_output(['arm-none-eabi-nm', '--defined-only', str(elf)], text=True).splitlines():
        words = line.split()
        if len(words) == 3 and words[2] in SCRIPTS:
            scripts[words[2]] = int(words[0], 16)
    if set(scripts) != SCRIPTS:
        raise ValueError('Pinned capture scripts changed.')
    programs = [program(case, syms, resolve, properties) for case in cases]
    if len({sequence for sequence, _ in programs}) != len(cases):
        raise ValueError('Duplicate effective capture commands cannot add coverage.')
    sequence = ''.join(value for value, _ in programs)
    (output / (label + '-commands.txt')).write_text(sequence)
    process = subprocess.run([str(executable), str(rom), str(state)], input=sequence,
                             capture_output=True, text=True, timeout=60)
    (output / (label + '-stdout.txt')).write_text(process.stdout)
    (output / (label + '-stderr.txt')).write_text(process.stderr)
    if process.returncode or digest(rom) != identity['rom_sha256']:
        raise ValueError('Capture fixture failed or changed the cartridge.')
    lines, observed = process.stdout.splitlines(), []
    for case, (sequence, reads) in zip(cases, programs):
        calls = sum(line.startswith('call ') for line in sequence.splitlines())
        count = 1 + calls + len(reads)
        chunk, lines = lines[:count], lines[count:]
        if len(chunk) != count or any(not re.fullmatch(r'return [0-9a-f]{8} steps \d+', line) for line in chunk[1:calls + 1]):
            raise ValueError('Incomplete native capture observations.')
        actual = {key: int.from_bytes(bytes.fromhex(raw), 'little')
                  for key, raw in zip(reads, chunk[calls + 1:])}
        actual['master'] = (actual['master'] >> 1) & 1
        actual['caught_ball'] = int(chunk[calls].split()[1], 16)
        expected = {key: scripts[value] if isinstance(value, str) else value for key, value in case['expected'].items()}
        observed.append({'id': case['id'], 'actual': actual, 'expected': expected,
                         'pass': actual == expected and int.from_bytes(bytes.fromhex(chunk[0]), 'little') == case.get('rng_seed', 0)})
    if lines:
        raise ValueError('Unexpected trailing capture observations.')
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
        parser.error('Preserve prior evidence; choose another name.')
    cases = validate(json.loads(args.cases.read_text()))
    output.mkdir(parents=True)
    executable, core = build_driver()
    engine = ROOT / '.tools/pokeemerald-host'
    resolve, properties = constants(engine), property_ids(engine)
    evidence = {'kind': 'Controlled capture command; RAM setup, not gameplay or inventory/storage transfer',
                'core': core, 'runner_sha256': digest(Path(__file__)),
                'shared_runner_sha256': digest(ROOT / 'scripts/quality/mechanics_fixtures.py'),
                'cases_sha256': digest(args.cases), 'sides': {},
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())}
    for label in ('reference', 'candidate'):
        evidence['sides'][label] = run_side(label, getattr(args, label + '_rom'), getattr(args, label + '_elf'),
            getattr(args, label + '_state'), executable, cases, resolve, properties, output)
    rows = [{'id': case['id'], 'pass': a['pass'] and b['pass']} for case, a, b in
            zip(cases, evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases'])]
    evidence.update({'results': rows, 'passed': sum(r['pass'] for r in rows), 'total': len(rows),
                     'full_mechanics_gate_complete': False, 'human_quality_approval': 'pending'})
    (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'passed': evidence['passed'], 'total': len(rows), 'evidence': str(output)}))
    if evidence['passed'] != len(rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
