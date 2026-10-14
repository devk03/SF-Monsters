"""Run native move-effect scripts to move-end, with bounded controller acknowledgements.

This is controlled battle RAM evidence. Controller ACKs do not execute animation,
party synchronization, move-end, residual processing, or a complete battle turn.
"""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
import time
from mechanics_fixtures import ROOT, battle_setup, build_driver, constants, digest, verify_bundle
from native_fixture_transport import Driver, writes

FUNCTIONS = {'RunBattleScriptCommands', 'Cmd_attackcanceler', 'Cmd_accuracycheck',
             'Cmd_attackstring', 'Cmd_ppreduce', 'Cmd_critcalc', 'Cmd_damagecalc',
             'Cmd_typecalc', 'Cmd_adjustnormaldamage', 'Cmd_datahpupdate',
             'Cmd_seteffectwithchance', 'SetMoveEffect', 'CalculateBaseDamage'}
ALLOCATIONS = {'gBattleBufferA': 2048, 'gBattleBufferB': 2048, 'gBattleResults': 68,
               'gBattleOutcome': 1, 'gPauseCounterBattle': 2, 'gMultiHitCounter': 1,
               'gDynamicBasePower': 2, 'gChosenMove': 2, 'gChosenMovePos': 1,
               'gCurrentTurnActionNumber': 1, 'gBattleTextBuff1': 16,
               'gBattleTextBuff2': 16, 'gBattleTextBuff3': 16}
MOVES = {'MOVE_POUND', 'MOVE_TACKLE', 'MOVE_WATER_GUN', 'MOVE_EMBER'}
ENDPOINT = 'BattleScript_MoveEnd'
EXPECTED = {'attacker_hp', 'defender_hp', 'pp', 'defender_status', 'flags', 'rng'}
BATTLER_FIELDS = {'type1', 'type2', 'species', 'level', 'hp', 'max_hp', 'ability',
                  'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'item',
                  'attack_stage', 'defense_stage', 'sp_attack_stage', 'sp_defense_stage',
                  'accuracy_stage', 'evasion_stage', 'status', 'status2'}
# No controller queries or selections may be guessed by this fixture transport.
ACK_COMMANDS = {2, 15, 16, 24, 26, 27, 41, 43}
BATTLE_STRUCT_SIZE = 0x2a4
HISTORY_SIZE = 0x54
CANARIES = {0x0203c2a4: bytes([0x5a])*16, 0x0203f824: bytes([0xa5])*16,
            0x0203f8d4: bytes([0x69])*16}


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 32:
        raise ValueError('Use 1–32 independently specified move pipelines.')
    seen = set()
    for case in cases:
        allowed = {'id', 'derivation', 'move', 'attacker', 'defender', 'rng_seed', 'pp', 'expected'}
        if set(case) - allowed or not case.get('derivation'):
            raise ValueError('Unknown pipeline control or missing derivation.')
        ident = case.get('id', '')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', ident) or ident in seen:
            raise ValueError('Pipeline IDs must be unique safe names.')
        seen.add(ident)
        if case.get('move') not in MOVES:
            raise ValueError('Use a reviewed single-target hit move.')
        if type(case.get('rng_seed', 0)) is not int or not 0 <= case.get('rng_seed', 0) <= 0xffffffff:
            raise ValueError('Pipeline RNG seed must fit 32 bits.')
        if type(case.get('pp', 10)) is not int or not 1 <= case.get('pp', 10) <= 40:
            raise ValueError('Starting PP must be 1–40.')
        for slot in ('attacker', 'defender'):
            value = case.get(slot, {})
            if not isinstance(value, dict) or set(value) - BATTLER_FIELDS:
                raise ValueError('Unknown or ignored battler control.')
        expected = case.get('expected')
        if not isinstance(expected, dict) or set(expected) != EXPECTED or any(type(v) is not int or v < 0 for v in expected.values()):
            raise ValueError('Require explicit final HP, PP, status, flags and RNG expectations.')
        for key, limit in [('attacker_hp',65535), ('defender_hp',65535), ('pp',40),
                           ('defender_status',0xffffffff), ('flags',255), ('rng',0xffffffff)]:
            if expected[key] > limit:
                raise ValueError('Expected observation exceeds its native width.')
        if expected['attacker_hp'] == 0 or expected['defender_hp'] == 0:
            raise ValueError('This bounded profile excludes faint resolution.')
    return cases


def verify_layout(engine, output):
    """Compile only an ABI receipt with the pinned agbcc; never build a ROM."""
    source = output/'pipeline-layout.c'
    source.write_text('#include "global.h"\n#include "battle.h"\n#include <stddef.h>\n'
        'const unsigned pipeline_layout[] = {sizeof(struct BattleStruct), '
        'offsetof(struct BattleStruct, dynamicMoveType), '
        'offsetof(struct BattleStruct, atkCancelerTracker), sizeof(struct BattleHistory), '
        'sizeof(struct BattleScriptsStack), sizeof(struct BattleScripting), '
        'offsetof(struct BattleScripting, dmgMultiplier), sizeof(struct DisableStruct), '
        'sizeof(struct ProtectStruct), sizeof(struct SpecialStatus)};\n')
    intermediate, assembly = output/'pipeline-layout.i', output/'pipeline-layout.s'
    compiler = engine/'tools/agbcc/bin/agbcc'
    subprocess.run(['arm-none-eabi-cpp', '-I', 'include', '-I', 'tools/agbcc/include',
        '-I', 'tools/agbcc', '-nostdinc', '-undef', '-std=gnu89', '-DMODERN=0',
        str(source), '-o', str(intermediate)], cwd=engine, check=True, timeout=10)
    subprocess.run([str(compiler), '-mthumb-interwork', '-O2', '-fhex-asm',
        '-o', str(assembly), str(intermediate)], cwd=engine, check=True, timeout=10)
    values = [int(v,16) for v in re.findall(r'\.word\s+0x([0-9a-f]+)', assembly.read_text())]
    if values != [BATTLE_STRUCT_SIZE, 0x13, 0x1a3, HISTORY_SIZE, 36, 40, 14, 28, 16, 20]:
        raise ValueError('Pinned pipeline ABI changed; do not guess scratch layouts.')
    return {'values': values, 'source_sha256': digest(source),
            'compiler_sha256': digest(compiler), 'method': 'Pinned agbcc sizeof/offsetof'}


def rom_symbols(elf):
    return {words[2]: int(words[0], 16) for row in subprocess.check_output(
        ['arm-none-eabi-nm', '--defined-only', str(elf)], text=True).splitlines()
        if len(words := row.split()) == 3}


def setup(case, syms, labels, resolve):
    attacker = {'type1': 'TYPE_MYSTERY', 'type2': 'TYPE_MYSTERY', **case.get('attacker', {})}
    defender = {'hp': 300, 'max_hp': 300, **case.get('defender', {})}
    lines = battle_setup({'move': case['move'], 'attacker': attacker, 'defender': defender,
                          'rng_seed': case.get('rng_seed', 0)}, syms, resolve)
    # Discard battle_setup's initial RNG observation; seed is checked after setup.
    lines = [line for line in lines if not line.startswith('read ')]
    resource = bytearray(32)
    for offset, address in [(4, 0x0203f040), (8, 0x0203f800), (24, 0x0203f880)]:
        struct.pack_into('<I', resource, offset, address)
    scripting = bytearray(40); scripting[14] = 1
    init = {'gBattleResources': struct.pack('<I', 0x0203f000),
            'gBattleStruct': struct.pack('<I', 0x0203c000),
            'gBattleScripting': scripting, 'gBattleCommunication': bytes(8),
            'gBattleControllerExecFlags': bytes(4), 'gMoveResultFlags': b'\0',
            # Tower rule suppresses badge bonuses without activating LINK transport.
            'gBattleTypeFlags': struct.pack('<I', resolve('BATTLE_TYPE_BATTLE_TOWER')),
            'gHitMarker': struct.pack('<I', resolve('HITMARKER_OBEYS')),
            'gDisableStructs': bytes(112), 'gSpecialStatuses': bytes(80),
            'gSideStatuses': bytes(4), 'gBattleResults': bytes(68),
            'gBattleOutcome': b'\0', 'gPauseCounterBattle': bytes(2),
            'gMultiHitCounter': b'\0', 'gDynamicBasePower': bytes(2),
            'gCurrentTurnActionNumber': b'\0', 'gCurrMovePos': b'\0', 'gChosenMovePos': b'\0',
            'gChosenMove': struct.pack('<H', resolve(case['move'])),
            'gBattlerByTurnOrder': bytes(range(4)), 'gLastUsedAbility': b'\0',
            'gLastLandedMoves': bytes(8), 'gLastHitByType': bytes(8),
            'gBattleBufferA': bytes(2048), 'gBattleBufferB': bytes(2048),
            'gBattleTextBuff1': bytes(16), 'gBattleTextBuff2': bytes(16), 'gBattleTextBuff3': bytes(16)}
    for name, data in init.items():
        lines += writes(syms[name][0], data)
    for address, data in [(0x0203c000, bytes(BATTLE_STRUCT_SIZE)), (0x0203f000, resource),
                          (0x0203f800, bytes(36)), (0x0203f880, bytes(HISTORY_SIZE))]:
        lines += writes(address, data)
    for address, data in CANARIES.items():
        lines += writes(address, data)
    lines += writes(syms['gBattleMons'][0] + 36, bytes([case.get('pp', 10)]))
    # Entry is the actual native move-effect script, not a copied opcode list.
    entry = 'BattleScript_EffectBurnHit' if case['move'] == 'MOVE_EMBER' else 'BattleScript_EffectHit'
    lines += writes(syms['gBattlescriptCurrInstr'][0], struct.pack('<I', labels[entry]))
    lines += writes(syms['gRngValue'][0], struct.pack('<I', case.get('rng_seed', 0)))
    return lines, entry


def verify_unique_setups(cases, syms, labels, resolve):
    """Compare effective native commands, excluding descriptive fixture metadata."""
    seen = {}
    for case in cases:
        commands, entry = setup(case, syms, labels, resolve)
        key = (tuple(commands), entry)
        if key in seen:
            raise ValueError(f'Duplicate effective pipeline setup: {seen[key]} and {case["id"]}.')
        seen[key] = case['id']


def verify_path(trace, missed):
    opcodes = {row['opcode'] for row in trace}
    required = {0, 1, 2, 3} if missed else {0, 1, 2, 3, 4, 5, 6, 7, 11, 12, 21, 25}
    return required <= opcodes and (not missed or not opcodes & {4, 5, 6, 7, 11, 12})


def verify_queued_updates(case, acknowledgements):
    updates = []
    for ack in acknowledgements:
        if ack['command'] != 2:
            continue
        packet = bytes.fromhex(ack['header'])
        request = packet[1]
        if request not in {9, 40, 42}:
            raise ValueError('Unreviewed SetMonData request in move pipeline.')
        size = {9: 1, 40: 4, 42: 2}[request]
        updates.append((ack['slot'], request, int.from_bytes(packet[3:3+size], 'little')))
    expected = case['expected']
    wanted = [(0, 9, expected['pp'])]
    if expected['defender_hp'] != case.get('defender', {}).get('hp', 300):
        wanted.append((1, 42, expected['defender_hp']))
    if expected['defender_status'] != case.get('defender', {}).get('status', 0):
        wanted.append((1, 40, expected['defender_status']))
    return updates == wanted


def run_case(driver, case, syms, labels, resolve, rom):
    setup_lines, entry = setup(case, syms, labels, resolve)
    seed = driver.exchange(setup_lines + [f'read {syms["gRngValue"][0]:x} 4'], 1)
    if int.from_bytes(bytes.fromhex(seed[0]), 'little') != case.get('rng_seed', 0):
        raise ValueError('Pipeline setup did not establish its declared RNG seed.')
    trace, acknowledgements = [], []
    call = f'call {syms["RunBattleScriptCommands"][0]:x} 0 0 0 0 0 0 0 0'
    pointer, deadline = labels[entry], time.monotonic()+20
    for step in range(1024):
        if time.monotonic() >= deadline:
            raise ValueError('Move pipeline exceeded its 20-second bound.')
        before = pointer
        opcode = rom[before-0x08000000]
        reads = [f'read {syms[n][0]:x} {size:x}' for n, size in
                 [('gBattlescriptCurrInstr', 4), ('gBattleControllerExecFlags', 4)]]
        response = driver.exchange([call, *reads], 3)
        if not re.fullmatch(r'return [0-9a-f]{8} steps \d+', response[0]):
            raise ValueError('Interpreter did not return cleanly.')
        pointer, controller = [int.from_bytes(bytes.fromhex(x), 'little') for x in response[1:]]
        trace.append({'step': step, 'before': hex(before), 'opcode': opcode,
                      'pointer': hex(pointer), 'controller': controller})
        if controller:
            if controller & ~3:
                raise ValueError('Unexpected controller slots or LINK transport.')
            slots = [i for i in range(2) if controller & (1 << i)]
            commands = driver.exchange([f'read {syms["gBattleBufferA"][0]+i*512:x} 8' for i in slots], len(slots))
            for slot, raw in zip(slots, commands):
                command = bytes.fromhex(raw)[0]
                if command not in ACK_COMMANDS:
                    raise ValueError(f'Unreviewed controller command {command}; do not fabricate a response.')
                acknowledgements.append({'step': step, 'slot': slot, 'command': command, 'header': raw})
            driver.exchange(writes(syms['gBattleControllerExecFlags'][0], bytes(4)), 0)
        if pointer == labels.get('BattleScript_FaintTarget'):
            raise ValueError('Unexpected faint path: full faint resolution is outside this fixture.')
        if pointer == labels[ENDPOINT]:
            break
        if not 0x08000000 <= pointer < 0x09000000:
            raise ValueError('Pipeline left the cartridge script region.')
    else:
        raise ValueError('Move script exceeded the 1024-command-call bound.')
    mons = syms['gBattleMons'][0]
    read_specs = {'attacker_hp': (mons+40, 2), 'defender_hp': (mons+88+40, 2),
                  'pp': (mons+36, 1), 'defender_status': (mons+88+76, 4),
                  'flags': (syms['gMoveResultFlags'][0], 1), 'rng': (syms['gRngValue'][0], 4)}
    values = driver.exchange([f'read {a:x} {n:x}' for a, n in read_specs.values()], len(read_specs))
    actual = {key: int.from_bytes(bytes.fromhex(raw), 'little') for key, raw in zip(read_specs, values)}
    guard_values = driver.exchange([f'read {a:x} {len(v):x}' for a,v in CANARIES.items()], len(CANARIES))
    if any(bytes.fromhex(got) != want for got,want in zip(guard_values,CANARIES.values())):
        raise ValueError('Pipeline scratch allocation crossed a native ABI boundary.')
    path_pass = verify_path(trace, bool(case['expected']['flags'] & 1))
    queue_pass = verify_queued_updates(case, acknowledgements)
    return {'id': case['id'], 'entry': entry, 'endpoint': ENDPOINT, 'actual': actual,
            'expected': case['expected'],
            'pass': actual == case['expected'] and path_pass and queue_pass,
            'path_pass': path_pass, 'queued_updates_pass': queue_pass,
            'rng_before': int.from_bytes(bytes.fromhex(seed[0]), 'little'),
            'trace': trace, 'controller_acknowledgements': acknowledgements, 'scratch_canaries_intact': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom', 'reference-elf', 'reference-state', 'candidate-rom', 'candidate-elf', 'candidate-state'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--cases', type=Path, default=ROOT/'data/quality/mechanics/move-pipeline.json')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name):
        parser.error('Use a safe evidence name.')
    output = ROOT/'.tools/benchmarks'/args.name
    if output.exists():
        parser.error('Preserve previous evidence; choose a new name.')
    cases = validate(json.loads(args.cases.read_text())); output.mkdir(parents=True)
    layout = verify_layout(ROOT/'.tools/pokeemerald-host', output)
    executable, core = build_driver(); resolve = constants(ROOT/'.tools/pokeemerald-host')
    evidence = {'kind': 'Native move-effect interpreter through move-end entry; bounded controller ACKs',
                'core': core, 'layout': layout, 'runner_sha256': digest(Path(__file__)), 'cases_sha256': digest(args.cases),
                'shared_runner_sha256': digest(ROOT/'scripts/quality/mechanics_fixtures.py'),
                'driver_source_sha256': digest(ROOT/'scripts/quality/function_fixture.c'),
                'transport_sha256': digest(ROOT/'scripts/quality/native_fixture_transport.py'),
                'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
                'source_worktree_dirty': bool(subprocess.check_output(['git','status','--porcelain'], text=True).strip()),
                'battle_rules': 'Tower flag suppresses badge bonuses; no link transport or facility gameplay',
                'limits': ['Already-obedient healthy single attacker; no obedience/campaign claims',
                           'Stop before move-end, faint resolution, residuals or next action',
                           'ACK only reviewed write/animation/audio commands; no response fabrication',
                           'Battle RAM and queued update payloads verified; party controllers are not executed',
                           'No frame, audio, timing, durable save or full-turn evidence'],
                'full_turn_proven': False, 'presentation_proven': False,
                'party_or_durable_save_proven': False, 'full_mechanics_gate_complete': False, 'sides': {}}
    for side in ('reference', 'candidate'):
        rom, elf, state = (getattr(args, side+'_'+name) for name in ('rom', 'elf', 'state'))
        identity, syms = verify_bundle(side, rom, elf, state, output, FUNCTIONS, ALLOCATIONS)
        labels = rom_symbols(elf)
        if not {'BattleScript_EffectHit', 'BattleScript_EffectBurnHit', ENDPOINT,
                'BattleScript_FaintTarget'} <= set(labels):
            raise ValueError('Pinned move-effect script labels are missing.')
        verify_unique_setups(cases, syms, labels, resolve)
        driver = Driver(executable, rom, state, output/side)
        try:
            results = [run_case(driver, c, syms, labels, resolve, rom.read_bytes()) for c in cases]
        finally:
            driver.close()
        if digest(rom) != identity['rom_sha256']:
            raise ValueError('Pipeline ROM changed during native execution.')
        evidence['sides'][side] = {**identity, 'cases': results}
    rows = [{'id': c['id'], 'pass': a['pass'] and b['pass']} for c,a,b in zip(cases,
            evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases'])]
    evidence.update(results=rows, total=len(rows), passed=sum(v['pass'] for v in rows))
    (output/'result.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps({'passed': evidence['passed'], 'total': len(rows), 'evidence': str(output)}))
    if evidence['passed'] != len(rows):
        raise SystemExit(1)

if __name__ == '__main__':
    main()
