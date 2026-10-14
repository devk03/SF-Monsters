"""Exercise native creation/stat recalculation; never inject a campaign creature."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
from mechanics_fixtures import ROOT, EMERALD_REVISION, digest, constants, verify_bundle, build_driver

FUNCTIONS = {'CreateMon', 'SetMonData', 'CalculateMonStats', 'GetNature'}


def property_ids(engine):
    text = subprocess.check_output(['git', 'show', f'{EMERALD_REVISION}:include/pokemon.h'], cwd=engine, text=True)
    body = re.search(r'enum\s*\{(.*?)\}', text, re.S)[1]
    names = [name.strip() for name in body.split(',') if name.strip()]
    if any(not re.fullmatch(r'MON_DATA_\w+', name) for name in names):
        raise ValueError('Pinned native property enum changed.')
    return {name: index for index, name in enumerate(names)}


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 128:
        raise ValueError('Use1–128 explicit stat scenarios.')
    ids = set()
    for case in cases:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', case.get('id', '')) or case['id'] in ids:
            raise ValueError('Stat scenario IDs must be unique safe names.')
        ids.add(case['id'])
        if set(case) - {'id', 'species', 'level', 'iv', 'nature', 'ivs', 'evs', 'current_hp',
                        'expected', 'reference_expected', 'candidate_expected', 'derivation',
                        'intentional_content_difference'} or not case.get('derivation'):
            raise ValueError('Stat cases need explicit controls and independent derivations.')
        for key, default, low, high in [('level', 50, 1, 100), ('iv', 31, 0, 31), ('nature', 0, 0, 24)]:
            value = case.get(key, default)
            if type(value) is not int or not low <= value <= high:
                raise ValueError('Invalid native stat fixture ' + key)
        for key, default, maximum in [('ivs', [case.get('iv', 31)] * 6, 31), ('evs', [0] * 6, 255)]:
            values = case.get(key, default)
            if not isinstance(values, list) or len(values) != 6 or any(type(v) is not int or not 0 <= v <= maximum for v in values):
                raise ValueError('Invalid six-stat IV/EV vector.')
            if key == 'evs' and sum(values) > 510:
                raise ValueError('Use legal individual/total EV fixture states.')
        for side in ('reference', 'candidate'):
            expected = case.get(side + '_expected', case.get('expected'))
            if not isinstance(expected, list) or len(expected) != 7 or any(type(v) is not int or not 0 <= v <= 65535 for v in expected):
                raise ValueError('Each side needs seven explicit HP/stat expectations.')
        if case.get('reference_expected') != case.get('candidate_expected') and not case.get('intentional_content_difference'):
            raise ValueError('Different SF stats require a declared content mapping.')
        if 'current_hp' in case and (type(case['current_hp']) is not int or not 0 <= case['current_hp'] <= 65535):
            raise ValueError('Current HP must be a native unsigned value.')
    return cases


def program(case, syms, resolve, fields):
    mon, value_ptr = 0x0203f400, 0x0203f500
    lines = [f'read {syms["gRngValue"][0]:x} 4']
    def call(name, *args):
        lines.append(f'call {syms[name][0]:x} ' + ' '.join(f'{v:x}' for v in (*args, *([0] * (8 - len(args))))))
    def set_data(field, value):
        lines.append(f'write {value_ptr:x} ' + struct.pack('<I', value).hex())
        call('SetMonData', mon, fields[field], value_ptr)
    call('CreateMon', mon, resolve(case.get('species', 'SPECIES_BULBASAUR')),
         case.get('level', 50), case.get('iv', 31), 1, case.get('nature', 0), 1, 0)
    suffixes = ('HP', 'ATK', 'DEF', 'SPEED', 'SPATK', 'SPDEF')
    for suffix, value in zip(suffixes, case.get('evs', [0] * 6)):
        if value:
            set_data('MON_DATA_' + suffix + '_EV', value)
    if 'ivs' in case:
        for suffix, value in zip(suffixes, case['ivs']):
            set_data('MON_DATA_' + suffix + '_IV', value)
    if 'current_hp' in case:
        set_data('MON_DATA_HP', case['current_hp'])
    call('CalculateMonStats', mon)
    call('GetNature', mon)
    # Pokemon party tail: currentHP0x56/maxHP0x58, five stats through byte99.
    lines += [f'read {mon + 86:x} e', f'read {mon + 84:x} 1', f'read {syms["gRngValue"][0]:x} 4']
    return '\n'.join(lines) + '\n'


def run_side(label, rom, elf, state, executable, cases, resolve, fields, output):
    identity, syms = verify_bundle(label, rom, elf, state, output, FUNCTIONS)
    programs = [program(case, syms, resolve, fields) for case in cases]
    if len(set(programs)) != len(programs):
        raise ValueError('Duplicate effective stat fixtures do not add coverage.')
    observed = []
    for case, sequence in zip(cases, programs):
        directory = output / label / case['id']
        directory.mkdir(parents=True)
        (directory / 'commands.txt').write_text(sequence)
        result = subprocess.run([str(executable), str(rom), str(state)], input=sequence,
                                text=True, capture_output=True, timeout=10)
        (directory / 'stdout.txt').write_text(result.stdout)
        (directory / 'stderr.txt').write_text(result.stderr)
        lines = result.stdout.splitlines()
        calls = sum(line.startswith('call ') for line in sequence.splitlines())
        if result.returncode or len(lines) != calls + 4 or any(not re.fullmatch(r'return [0-9a-f]{8} steps \d+', line) for line in lines[1:-3]):
            raise ValueError('Stat fixture failed or produced incomplete observations: ' + case['id'])
        stats = list(struct.unpack('<7H', bytes.fromhex(lines[-3])))
        nature = int(lines[-4].split()[1], 16)
        level = int(lines[-2], 16)
        expected = case.get(label + '_expected', case.get('expected'))
        observed.append({'id': case['id'], 'stats': stats, 'expected': expected,
                         'nature': nature, 'level': level, 'rng_unchanged': lines[0] == lines[-1],
                         'pass': stats == expected and nature == case.get('nature', 0)
                             and level == case.get('level', 50) and lines[0] == lines[-1]})
    if digest(rom) != identity['rom_sha256']:
        raise ValueError('Native stat fixtures changed the input ROM.')
    return {**identity, 'cases': observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom', 'reference-elf', 'reference-state', 'candidate-rom', 'candidate-elf', 'candidate-state'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--cases', type=Path, default=ROOT / 'data/quality/mechanics/generated-stats.json')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name):
        parser.error('Use a short safe evidence name.')
    output = ROOT / '.tools/benchmarks' / args.name
    if output.exists():
        parser.error('Choose a new evidence directory.')
    cases = validate(json.loads(args.cases.read_text()))
    output.mkdir(parents=True)
    executable, core = build_driver()
    engine = ROOT / '.tools/pokeemerald-host'
    resolve, fields = constants(engine), property_ids(engine)
    evidence = {'kind': 'controlled native generation/stat fixtures, not campaign evidence',
                'core': core, 'cases_sha256': digest(args.cases),
                'runner_sha256': digest(Path(__file__)),
                'shared_runner_sha256': digest(ROOT / 'scripts/quality/mechanics_fixtures.py'),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                'sides': {}}
    for side in ('reference', 'candidate'):
        evidence['sides'][side] = run_side(side, getattr(args, side + '_rom'), getattr(args, side + '_elf'),
            getattr(args, side + '_state'), executable, cases, resolve, fields, output)
    rows = [{'id': a['id'], 'pass': a['pass'] and b['pass']} for a, b in
            zip(evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases'])]
    evidence.update({'results': rows, 'passed': sum(row['pass'] for row in rows), 'total': len(rows),
                     'full_mechanics_gate_complete': False, 'human_quality_approval': 'pending'})
    (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'passed': evidence['passed'], 'total': len(rows), 'evidence': str(output)}))
    if evidence['passed'] != len(rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
