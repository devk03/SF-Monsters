"""Check complete native action sorting without executing or fabricating a battle."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from mechanics_fixtures import ROOT, battle_setup, build_driver, constants, digest, verify_bundle

FUNCTION = 'SetActionsAndBattlersTurnOrder'
CALLBACK = 'CheckFocusPunch_ClearVarsBeforeTurnStarts'
SLOTS = ('attacker', 'defender', 'ally', 'opponent_ally')


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 128:
        raise ValueError('Supply1–128 independent action scenarios.')
    ids = set()
    for case in cases:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', case.get('id', '')) or case['id'] in ids:
            raise ValueError('Action IDs must be unique safe names.')
        ids.add(case['id'])
        if set(case) - {'id', 'derivation', 'actions', 'expected_order', 'weather',
                        'quick_claw_draw', *SLOTS} or not case.get('derivation'):
            raise ValueError('Reject unknown action controls or missing derivations.')
        order = case.get('expected_order')
        if not isinstance(order, list) or any(type(v) is not int for v in order) or sorted(order) != list(range(4)):
            raise ValueError('Expected order must be an explicit four-battler permutation.')
        actions = case.get('actions', ['B_ACTION_USE_MOVE'] * 4)
        allowed = {'B_ACTION_USE_MOVE', 'B_ACTION_USE_ITEM', 'B_ACTION_SWITCH', 'B_ACTION_RUN'}
        if not isinstance(actions, list) or len(actions) != 4 or any(v not in allowed for v in actions):
            raise ValueError('Use four explicit supported actions.')
        draw = case.get('quick_claw_draw', 65535)
        if type(draw) is not int or not 0 <= draw <= 65535:
            raise ValueError('QuickClaw draw must fit16 bits.')
    return cases


def program(case, syms, resolve):
    controls = {key: value for key, value in case.items() if key in {*SLOTS, 'weather', 'quick_claw_draw'}}
    # All four slots are live. Link-rule flag disables campaign badge bonuses.
    lines = battle_setup({**controls, 'double': True, 'rng_seed': 0}, syms, resolve)
    actions = bytes(resolve(v) for v in case.get('actions', ['B_ACTION_USE_MOVE'] * 4))
    lines += [f'write {syms["gChosenActionByBattler"][0]:x} {actions.hex()}',
              f'write {syms["gActionsByTurnOrder"][0]:x} ffffffff',
              f'write {syms["gBattlerByTurnOrder"][0]:x} ffffffff',
              f'write {syms["gBattleMainFunc"][0]:x} 00000000',
              # BattleStruct focusPunchBattlerId offset0x48: poison then verify reset.
              'write 203f148 a5',
              f'call {syms[FUNCTION][0]:x} 0 0 0 0 0 0 0 0',
              f'read {syms["gBattlerByTurnOrder"][0]:x} 4',
              f'read {syms["gActionsByTurnOrder"][0]:x} 4',
              f'read {syms["gBattleMainFunc"][0]:x} 4',
              'read 203f148 1', f'read {syms["gRngValue"][0]:x} 4']
    return '\n'.join(lines) + '\n', actions


def run_side(label, rom, elf, state, executable, cases, resolve, output):
    identity, syms = verify_bundle(label, rom, elf, state, output, {FUNCTION, CALLBACK, 'GetWhoStrikesFirst'})
    programs = [program(case, syms, resolve) for case in cases]
    if len({sequence for sequence, _ in programs}) != len(cases):
        raise ValueError('Duplicate effective action fixtures cannot add coverage.')
    sequence = ''.join(sequence for sequence, _ in programs)
    (output / (label + '-commands.txt')).write_text(sequence)
    process = subprocess.run([str(executable), str(rom), str(state)], input=sequence,
                             capture_output=True, text=True, timeout=60)
    (output / (label + '-stdout.txt')).write_text(process.stdout)
    (output / (label + '-stderr.txt')).write_text(process.stderr)
    lines = process.stdout.splitlines()
    if process.returncode or len(lines) != 7 * len(cases) or digest(rom) != identity['rom_sha256']:
        raise ValueError('Action fixture observations incomplete or input ROM changed.')
    observed = []
    for index, (case, (_, actions)) in enumerate(zip(cases, programs)):
        before, returned, order, actual_actions, callback, focus, after = lines[index * 7:(index + 1) * 7]
        if not re.fullmatch(r'return [0-9a-f]{8} steps \d+', returned):
            raise ValueError('Action function did not return cleanly.')
        order, actual_actions = list(bytes.fromhex(order)), list(bytes.fromhex(actual_actions))
        callback = int.from_bytes(bytes.fromhex(callback), 'little')
        expected_actions = [actions[i] for i in case['expected_order']]
        observed.append({'id': case['id'], 'order': order, 'expected_order': case['expected_order'],
                         'actions': actual_actions, 'expected_actions': expected_actions,
                         'rng_before': before, 'rng_after': after, 'focus_tracker': int(focus, 16),
                         'callback': callback, 'expected_callback': syms[CALLBACK][0] | 1,
                         'pass': order == case['expected_order'] and actual_actions == expected_actions
                             and callback == syms[CALLBACK][0] | 1 and int(focus, 16) == 0
                             and before == after == '00000000'})
    return {**identity, 'cases': observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom', 'reference-elf', 'reference-state', 'candidate-rom', 'candidate-elf', 'candidate-state'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--cases', type=Path, default=ROOT / 'data/quality/mechanics/action-order.json')
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
    evidence = {'kind': 'controlled native four-battler sorting, not move execution or campaign evidence',
                'core': core, 'cases_sha256': digest(args.cases), 'runner_sha256': digest(Path(__file__)),
                'shared_runner_sha256': digest(ROOT / 'scripts/quality/mechanics_fixtures.py'),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                'sides': {}}
    for side in ('reference', 'candidate'):
        evidence['sides'][side] = run_side(side, getattr(args, side + '_rom'), getattr(args, side + '_elf'),
            getattr(args, side + '_state'), executable, cases, resolve, output)
    rows = [{'id': a['id'], 'double': True, 'pass': a['pass'] and b['pass']} for a, b in
            zip(evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases'])]
    evidence.update({'results': rows, 'passed': sum(row['pass'] for row in rows), 'total': len(rows),
                     'full_mechanics_gate_complete': False, 'human_quality_approval': 'pending'})
    (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'passed': evidence['passed'], 'total': len(rows), 'evidence': str(output)}))
    if evidence['passed'] != len(rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
