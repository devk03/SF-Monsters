"""Run explicit mechanics vectors on actual ROM functions, never campaign play."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import uuid
from capture_core import ROOT, SOURCE, HOST_BUILD, REVISION, REFERENCE_HASH, verified_host_build

sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from bootstrap import EMERALD_REVISION

FUNCTION = 'CalculateBaseDamage'
FUNCTIONS = {FUNCTION, 'GetWhoStrikesFirst', 'TypeCalc'}
GLOBALS = {'gBattleMons': 352, 'gBattlerPositions': 4, 'gBattlersCount': 1,
           'gBattlerAttacker': 1, 'gBattlerTarget': 1, 'gActiveBattler': 1,
           'gAbsentBattlerFlags': 1, 'gCurrentMove': 2, 'gBattleTypeFlags': 4,
           'gCritMultiplier': 1, 'gBattleWeather': 2, 'gStatuses3': 16,
           'gBattleResources': 4, 'gBattleMovePower': 2, 'gRngValue': 4,
           'gBattleStruct': 4, 'gProtectStructs': 64, 'gChosenActionByBattler': 4,
           'gRandomTurnNumber': 2, 'gActionsByTurnOrder': 4,
           'gBattlerByTurnOrder': 4, 'gBattleMainFunc': 4, 'gBattleMoveDamage': 4,
           'gBattlescriptCurrInstr': 4, 'gHitMarker': 4, 'gMoveResultFlags': 1,
           'gDisableStructs': 112, 'gBattleCommunication': 8, 'gLastUsedAbility': 1,
           'gLastLandedMoves': 8, 'gLastHitByType': 8}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def constants(engine):
    definitions = {}
    for header in ('constants/battle', 'constants/pokemon', 'constants/moves',
                   'constants/abilities', 'constants/items', 'constants/species', 'battle'):
        text = subprocess.check_output(['git', 'show',
            f'{EMERALD_REVISION}:include/{header}.h'], cwd=engine, text=True)
        for name, expression in re.findall(r'^#define\s+(\w+)\s+([^\n]+)', text, re.M):
            definitions[name] = expression.split('//')[0].strip()
        if header == 'constants/items':
            clean = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
            for body in re.findall(r'enum\s*\{(.*?)\}', clean, re.S):
                for value, name in enumerate(name.strip() for name in body.split(',') if name.strip()):
                    if not re.fullmatch(r'\w+', name):
                        raise ValueError('Pinned item enum changed; review its explicit values.')
                    definitions[name] = str(value)
    operators = {ast.LShift: lambda a, b: a << b, ast.BitOr: lambda a, b: a | b,
                 ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b}
    def resolve(value):
        if type(value) is int:
            return value
        def visit(node):
            if isinstance(node, ast.Constant) and type(node.value) is int:
                return node.value
            if isinstance(node, ast.Name) and node.id in definitions:
                return visit(ast.parse(definitions[node.id], mode='eval').body)
            if isinstance(node, ast.BinOp) and type(node.op) in operators:
                return operators[type(node.op)](visit(node.left), visit(node.right))
            raise ValueError('Unsupported native constant: ' + str(value))
        if not isinstance(value, str) or value not in definitions:
            raise ValueError('Unknown native constant: ' + str(value))
        return visit(ast.parse(definitions[value], mode='eval').body)
    return resolve


def symbols(elf, function=FUNCTION):
    functions = {function} if isinstance(function, str) else set(function)
    wanted, result = set(GLOBALS) | functions, {}
    for line in subprocess.check_output(['arm-none-eabi-nm', '-S', '--defined-only', str(elf)], text=True).splitlines():
        match = re.fullmatch(r'([0-9a-f]+) ([0-9a-f]+) [A-Za-z] (\w+)', line)
        if match and match[3] in wanted:
            if match[3] in result:
                raise ValueError('Ambiguous fixture symbol: ' + match[3])
            result[match[3]] = (int(match[1], 16), int(match[2], 16))
    if set(result) != wanted or any(result[name][1] != size for name, size in GLOBALS.items()):
        raise ValueError('Pinned native fixture symbols/layout changed.')
    return result


def battle_mon(changes, resolve):
    fields = {'species': (0, 'H', 1), 'attack': (2, 'H', 100), 'defense': (4, 'H', 100),
              'speed': (6, 'H', 100), 'sp_attack': (8, 'H', 100), 'sp_defense': (10, 'H', 100),
              'ability': (32, 'B', 0), 'hp': (40, 'H', 90), 'level': (42, 'B', 50),
              'max_hp': (44, 'H', 90), 'item': (46, 'H', 0), 'status': (76, 'I', 0),
              'type1': (33, 'B', 0), 'type2': (34, 'B', 0), 'status2': (80, 'I', 0)}
    stages = {'attack_stage': 25, 'defense_stage': 26, 'speed_stage': 27,
              'sp_attack_stage': 28, 'sp_defense_stage': 29,
              'accuracy_stage': 30, 'evasion_stage': 31}
    if set(changes) - (set(fields) | set(stages) | {'move'}):
        raise ValueError('Unsupported battle-mon fixture field.')
    data = bytearray(88)
    struct.pack_into('<H', data, 12, resolve(changes.get('move', 1)))
    data[24:32] = bytes([6]) * 8
    for name, (offset, fmt, default) in fields.items():
        value = resolve(changes.get(name, default))
        if name == 'level' and not 1 <= value <= 100:
            raise ValueError('Fixture level must be1–100.')
        if name in ('attack', 'defense', 'sp_attack', 'sp_defense') and not 1 <= value <= 65535:
            raise ValueError('Fixture damage stats must be positive native values.')
        struct.pack_into('<' + fmt, data, offset, value)
    for name, offset in stages.items():
        value = changes.get(name, 6)
        if type(value) is not int or not 0 <= value <= 12:
            raise ValueError('Native stat stage must be0–12, neutral6.')
        data[offset] = value
    return bytes(data)


def battle_setup(case, syms, resolve):
    move = resolve(case.get('move', 'MOVE_POUND'))
    doubles = case.get('double', False)
    if type(doubles) is not bool:
        raise ValueError('Double flag must be a boolean.')
    absent = case.get('absent', 0 if doubles else 12)
    mons = []
    for index, name in enumerate(('attacker', 'defender', 'ally', 'opponent_ally')):
        data = bytearray(battle_mon(case.get(name, {}), resolve))
        if absent & (1 << index):
            struct.pack_into('<H', data, 40, 0)
        mons.append(bytes(data))
    arena, flags = 0x0203f000, 0x0203f040
    resources = bytearray(32)
    struct.pack_into('<I', resources, 4, flags)
    writes = {'gBattleMons': b''.join(mons), 'gBattlerPositions': bytes(range(4)),
              'gBattlersCount': bytes([4 if doubles else 2]), 'gBattlerAttacker': b'\0',
              'gBattlerTarget': b'\1', 'gActiveBattler': b'\0',
              'gAbsentBattlerFlags': bytes([absent]),
              'gCurrentMove': struct.pack('<H', move), 'gBattleTypeFlags': struct.pack('<I', 3 if doubles else 2),
              'gCritMultiplier': bytes([case.get('critical', 1)]),
              'gBattleWeather': struct.pack('<H', resolve(case.get('weather', 0))),
              'gStatuses3': struct.pack('<4I', resolve(case.get('sport', 0)), 0, 0, 0),
              'gBattleResources': struct.pack('<I', arena),
              'gBattleStruct': struct.pack('<I', arena + 0x100),
              'gProtectStructs': bytes(64), 'gChosenActionByBattler': bytes(4),
              'gRandomTurnNumber': struct.pack('<H', case.get('quick_claw_draw', 65535))}
    if 'rng_seed' in case:
        writes['gRngValue'] = struct.pack('<I', case['rng_seed'])
    lines = ['reset']
    for name, value in writes.items():
        lines.append(f'write {syms[name][0]:x} {value.hex()}')
    lines += [f'write {arena:x} {resources.hex()}',
              f'write {flags:x} ' + struct.pack('<4I', int(case.get('flash_fire', False)), 0, 0, 0).hex(),
              f'write {arena + 0x100:x} ' + bytes(132).hex(),
              f'read {syms["gRngValue"][0]:x} 4']
    return lines


def commands(case, syms, resolve, function=FUNCTION):
    move = resolve(case.get('move', 'MOVE_POUND'))
    lines = battle_setup(case, syms, resolve)
    args = [syms['gBattleMons'][0], syms['gBattleMons'][0] + 88, move,
            resolve(case.get('side_status', 0)), case.get('power_override', 0), 0, 0, 1]
    if function == 'GetWhoStrikesFirst':
        args = [0, 1, int(case.get('ignore_moves', False)), 0, 0, 0, 0, 0]
    if function == 'TypeCalc':
        lines.append(f'write {syms["gBattleMoveDamage"][0]:x} ' + struct.pack('<i', case.get('damage', 100)).hex())
        args = [move, 0, 1, 0, 0, 0, 0, 0]
    detail = {FUNCTION: 'gBattleMovePower', 'GetWhoStrikesFirst': 'gRandomTurnNumber',
              'TypeCalc': 'gBattleMoveDamage'}[function]
    lines += ['call ' + f'{syms[function][0]:x} ' + ' '.join(f'{arg:x}' for arg in args),
              f'read {syms[detail][0]:x} ' + ('4' if function == 'TypeCalc' else '2'),
              f'read {syms["gRngValue"][0]:x} 4']
    return '\n'.join(lines) + '\n'


def validate_cases(document):
    function = document.get('function', FUNCTION)
    if function not in FUNCTIONS:
        raise ValueError('Only explicitly supported native fixture functions are allowed.')
    cases = document.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 512:
        raise ValueError('Use1–512 uniquely named mechanics cases.')
    for case in cases:
        if not isinstance(case, dict) or not {'id', 'expected', 'derivation'} <= set(case):
            raise ValueError('Each fixture needs an ID, expected value and derivation.')
        if not isinstance(case['id'], str) or not case['id']:
            raise ValueError('Fixture IDs must be nonempty strings.')
        allowed = {'id', 'expected', 'derivation', 'move', 'attacker', 'defender', 'ally',
                   'opponent_ally', 'double', 'absent', 'critical', 'weather', 'sport',
                   'side_status', 'flash_fire', 'power_override'}
        if function == 'GetWhoStrikesFirst':
            allowed = {'id', 'expected', 'derivation', 'attacker', 'defender', 'ally',
                       'opponent_ally', 'double', 'absent', 'weather', 'rng_seed',
                       'expected_rng', 'quick_claw_draw', 'ignore_moves'}
        if function == 'TypeCalc':
            allowed = {'id', 'expected', 'expected_damage', 'damage', 'derivation', 'move',
                       'attacker', 'defender'}
            for key in ('damage', 'expected_damage'):
                value = case.get(key, 100 if key == 'damage' else None)
                if type(value) is not int or not 0 <= value <= 1000000:
                    raise ValueError('Type fixtures need explicit nonnegative native damage expectations.')
        if set(case) - allowed:
            raise ValueError('Unknown fixture field; reject ignored or misspelled controls.')
        if type(case['expected']) is not int or case['expected'] < 0 or not case.get('derivation'):
            raise ValueError('Each case needs an explicit independent expected value and derivation.')
        if type(case.get('double', False)) is not bool or type(case.get('flash_fire', False)) is not bool:
            raise ValueError('Fixture switches must be booleans.')
        if type(case.get('critical', 1)) is not int or case.get('critical', 1) not in (1, 2):
            raise ValueError('Critical context must be1 or2.')
        if type(case.get('absent', 0)) is not int or not 0 <= case.get('absent', 0) <= 15:
            raise ValueError('Absent mask must identify at most four battlers.')
        for key in ('rng_seed', 'expected_rng'):
            if key in case and (type(case[key]) is not int or not 0 <= case[key] <= 0xffffffff):
                raise ValueError('RNG fixtures require explicit32-bit values.')
        if 'expected_rng' in case and 'rng_seed' not in case:
            raise ValueError('Expected RNG transition needs its explicit seed.')
        if type(case.get('quick_claw_draw', 65535)) is not int or not 0 <= case.get('quick_claw_draw', 65535) <= 65535:
            raise ValueError('QuickClaw draw must be a native16-bit value.')
        if type(case.get('ignore_moves', False)) is not bool:
            raise ValueError('Ignore-moves control must be boolean.')
    if len({case['id'] for case in cases}) != len(cases):
        raise ValueError('Use uniquely named mechanics cases.')
    return cases


def verify_bundle(label, rom, elf, state, output, functions):
    identity = digest(rom)
    cartridge = rom.read_bytes()
    if len(cartridge) != 16777216 or cartridge[0xac:0xb0] != b'BPEE':
        raise ValueError('Native fixtures require the16MiB BPEE cartridge family.')
    companion = elf.with_suffix('.gba')
    if not companion.is_file() or digest(companion) != identity:
        raise ValueError('ELF needs its byte-identical companion cartridge.')
    metadata = json.loads(state.with_suffix('.json').read_text())
    if metadata['rom_sha256'] != identity or metadata.get('mgba_revision') != REVISION:
        raise ValueError('Fixture state belongs to another ROM or core revision.')
    if label == 'reference' and identity != REFERENCE_HASH:
        raise ValueError('Use the fixed approved Emerald reference.')
    syms = symbols(elf, functions)
    linked = output / (label + '-linked.bin')
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', str(elf), str(linked)], check=True)
    hashes = {}
    binary = linked.read_bytes()
    for function in functions:
        address, size = syms[function]
        offset = address - 0x08000000
        if offset < 0 or size < 1 or offset + size > len(cartridge) or cartridge[offset:offset + size] != binary[offset:offset + size]:
            raise ValueError('Fixture function in ELF does not match the tested ROM.')
        hashes[function] = hashlib.sha256(cartridge[offset:offset + size]).hexdigest()
    return {'rom_sha256': identity, 'elf_sha256': digest(elf), 'state_sha256': digest(state),
            'function_sha256': hashes}, syms


def run_side(label, rom, elf, state, executable, cases, resolve, output, function=FUNCTION):
    identity, syms = verify_bundle(label, rom, elf, state, output, {function})
    sequences = [commands(case, syms, resolve, function) for case in cases]
    if len(set(sequences)) != len(sequences):
        raise ValueError('Duplicate effective native fixtures do not increase coverage.')
    sequence = ''.join(sequences)
    (output / (label + '-commands.txt')).write_text(sequence)
    result = subprocess.run([str(executable), str(rom), str(state)], input=sequence,
                            text=True, capture_output=True, timeout=60)
    (output / (label + '-stdout.txt')).write_text(result.stdout)
    (output / (label + '-stderr.txt')).write_text(result.stderr)
    if result.returncode or digest(rom) != identity['rom_sha256']:
        raise ValueError('Native fixture process failed or changed its input ROM.')
    lines = result.stdout.splitlines()
    if len(lines) != len(cases) * 4:
        raise ValueError('Incomplete native fixture observations.')
    observed = []
    for index, case in enumerate(cases):
        before, returned, power, after = lines[index * 4:(index + 1) * 4]
        match = re.fullmatch(r'return ([0-9a-f]{8}) steps (\d+)', returned)
        if not match:
            raise ValueError('Fixture did not return cleanly.')
        before, after = [int.from_bytes(bytes.fromhex(value), 'little') for value in (before, after)]
        detail = {FUNCTION: 'move_power', 'GetWhoStrikesFirst': 'quick_claw_draw', 'TypeCalc': 'damage'}[function]
        observed.append({'id': case['id'], 'value': int(match[1], 16),
                         detail: int.from_bytes(bytes.fromhex(power), 'little'),
                         'instructions': int(match[2]), 'rng_before': before, 'rng_after': after,
                         'rng_pass': before == case.get('rng_seed', before)
                             and after == case.get('expected_rng', before)})
    return {**identity, 'cases': observed}



def build_driver():
    core = verified_host_build()
    if subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() != REVISION:
        raise ValueError('Pinned native core source revision changed.')
    executable = ROOT / '.tools' / ('function-fixture-' + uuid.uuid4().hex)
    frameworks = ['-framework', 'CoreFoundation'] if platform.system() == 'Darwin' else []
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-D_GNU_SOURCE', '-DBUILD_STATIC',
        '-I' + str(SOURCE / 'include'), '-I' + str(HOST_BUILD / 'include'),
        str(ROOT / 'scripts/quality/function_fixture.c'), str(HOST_BUILD / 'libmgba.a'),
        '-lm', '-lpthread', *frameworks, '-o', str(executable)], check=True)
    return executable, {**core,
        'fixture_driver_source_sha256': digest(ROOT / 'scripts/quality/function_fixture.c'),
        'fixture_driver_binary_sha256': digest(executable)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom', 'reference-elf', 'reference-state', 'candidate-rom', 'candidate-elf', 'candidate-state'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--cases', type=Path, default=ROOT / 'data/quality/mechanics/base-damage.json')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name):
        parser.error('Use a short lowercase evidence name.')
    output = ROOT / '.tools/benchmarks' / args.name
    if output.exists():
        parser.error('Choose a new evidence name; prior results are preserved.')
    document = json.loads(args.cases.read_text())
    cases = validate_cases(document)
    function = document.get('function', FUNCTION)
    output.mkdir(parents=True)
    executable, core = build_driver()
    resolve = constants(ROOT / '.tools/pokeemerald-host')
    evidence = {'kind': 'controlled native function fixtures; RAM/register setup; not controller/campaign evidence',
                'function': function, 'core': core, 'cases_sha256': digest(args.cases),
                'runner_sha256': digest(Path(__file__)),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                'sides': {}}
    for label in ('reference', 'candidate'):
        evidence['sides'][label] = run_side(label, getattr(args, label + '_rom'), getattr(args, label + '_elf'),
            getattr(args, label + '_state'), executable, cases, resolve, output, function)
    results = []
    for case, reference, candidate in zip(cases, evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases']):
        results.append({'id': case['id'], 'expected': case['expected'], 'reference': reference['value'],
                        'candidate': candidate['value'], 'double': case.get('double', False),
                        'rng_pass': reference['rng_pass'] and candidate['rng_pass'],
                        'pass': reference['value'] == candidate['value'] == case['expected']
                            and reference['rng_pass'] and candidate['rng_pass']
                            and (function != 'TypeCalc' or reference['damage'] == candidate['damage'] == case['expected_damage'])})
        if function == 'TypeCalc':
            results[-1].update({'reference_damage': reference['damage'], 'candidate_damage': candidate['damage'],
                                'expected_damage': case['expected_damage']})
    evidence.update({'results': results, 'passed': sum(row['pass'] for row in results), 'total': len(results),
                     'full_mechanics_gate_complete': False, 'human_quality_approval': 'pending'})
    (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'passed': evidence['passed'], 'total': len(results), 'evidence': str(output)}))
    if evidence['passed'] != len(results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
