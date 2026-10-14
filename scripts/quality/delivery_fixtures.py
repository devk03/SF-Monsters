"""Capture-to-delivery function chains; controlled RAM, no UI or durable save proof."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
from mechanics_fixtures import ROOT, battle_setup, build_driver, constants, digest, verify_bundle
from capture_fixtures import ALLOCATIONS, verify_layout
from native_abi import verify_native_layout
from stat_fixtures import property_ids

FUNCTIONS = {'CreateMon', 'SetMonData', 'Cmd_handleballthrow', 'GiveMonToPlayer',
             'IsPlayerPartyAndPokemonStorageFull', 'CopyMon'}
GLOBALS = {**ALLOCATIONS, 'gPokemonStoragePtr': 4,
           'gSpecialVar_MonBoxId': 2, 'gSpecialVar_MonBoxPos': 2}
PC, SAVE1, SAVE2, TEMPLATE = 0x02010000, 0x02028000, 0x0202c000, 0x0203f400
FIELDS = {'preflight', 'delivery', 'postflight', 'party_count', 'box', 'slot',
          'destination', 'mon', 'rng_before', 'rng_after', 'neighbors_preserved'}


def validate(document):
    cases = document.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 32:
        raise ValueError('Use1–32 independent delivery scenarios.')
    ids = set()
    for case in cases:
        if set(case) - {'id', 'derivation', 'party_size', 'box', 'filled_boxes', 'first_slots', 'hole', 'pp_bonus', 'expected'}:
            raise ValueError('Reject ignored delivery controls.')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', case.get('id', '')) or case['id'] in ids or not case.get('derivation'):
            raise ValueError('Delivery IDs and independent derivations are required.')
        ids.add(case['id'])
        for key, default, low, high in [('party_size', 1, 1, 6), ('box', 0, 0, 13),
                                      ('first_slots', 0, 0, 30), ('pp_bonus', 0, 0, 3)]:
            if type(case.get(key, default)) is not int or not low <= case.get(key, default) <= high:
                raise ValueError('Invalid bounded delivery control: ' + key)
        boxes = case.get('filled_boxes', [])
        if not isinstance(boxes, list) or any(type(b) is not int or not 0 <= b < 14 for b in boxes) or len(set(boxes)) != len(boxes):
            raise ValueError('Filled boxes must be unique native indices.')
        if 'hole' in case and (type(case['hole']) is not int or not 0 <= case['hole'] < 420):
            raise ValueError('PC hole must be one of420 slots.')
        expected = case.get('expected')
        if not isinstance(expected, dict) or set(expected) != FIELDS or expected['neighbors_preserved'] is not True:
            raise ValueError('Delivery needs complete explicit oracles and preserved neighbors.')
        for key in FIELDS - {'destination', 'mon', 'neighbors_preserved'}:
            if type(expected[key]) is not int or not 0 <= expected[key] <= 0xffffffff:
                raise ValueError('Delivery scalar oracles need unsigned native integers.')
        if expected['destination'] not in ('party', 'pc', 'none'):
            raise ValueError('Use a declared delivery destination.')
        mon = expected['mon']
        if expected['destination'] == 'none':
            if mon is not None: raise ValueError('Refusal cannot claim a delivered monster.')
        else:
            required = {'species', 'held_item', 'moves', 'pp', 'pp_bonus', 'ball', 'ot_gender', 'ot_id', 'hp', 'max_hp', 'status'}
            if not isinstance(mon, dict) or set(mon) != required:
                raise ValueError('Every delivered-mon field needs an explicit oracle.')
            for key in ('moves', 'pp'):
                if not isinstance(mon[key], list) or len(mon[key]) != 4 or any(type(v) is not int or not 0 <= v <= (255 if key == 'pp' else 65535) for v in mon[key]):
                    raise ValueError('Delivered moves/PP need four bounded integers.')
            for key in required - {'moves', 'pp'}:
                if mon[key] is None and key in ('hp', 'max_hp', 'status') and expected['destination'] == 'pc': continue
                if type(mon[key]) is not int or not 0 <= mon[key] <= 0xffffffff:
                    raise ValueError('Delivered-mon scalar oracles need native integers.')
    return cases


def decode_mon(data, boxed=False):
    """Independently decrypt fixed-personality fixtures and validate their checksum."""
    if len(data) != (80 if boxed else 100):
        raise ValueError('Native mon size changed.')
    personality, owner = struct.unpack_from('<II', data)
    if personality != 0:
        raise ValueError('This audited fixture decoder requires fixed personality0.')
    plain = struct.pack('<12I', *[word ^ owner for word in struct.unpack_from('<12I', data, 32)])
    if sum(struct.unpack('<24H', plain)) & 65535 != struct.unpack_from('<H', data, 28)[0]:
        raise ValueError('Native encrypted-mon checksum failed.')
    origin = struct.unpack_from('<H', plain, 38)[0]
    result = {'species': struct.unpack_from('<H', plain)[0], 'held_item': struct.unpack_from('<H', plain, 2)[0],
              'moves': list(struct.unpack_from('<4H', plain, 12)), 'pp': list(plain[20:24]),
              'pp_bonus': plain[8], 'ball': origin >> 11 & 15, 'ot_gender': origin >> 15,
              'ot_id': owner, 'hp': None, 'max_hp': None, 'status': None}
    if not boxed:
        result.update({'status': struct.unpack_from('<I', data, 80)[0],
                       'hp': struct.unpack_from('<H', data, 86)[0], 'max_hp': struct.unpack_from('<H', data, 88)[0]})
    return result


def program(case, syms, resolve, props):
    lines = battle_setup({'rng_seed': 0, 'defender': {'species': 'SPECIES_RATTATA', 'hp': 45,
        'max_hp': 90, 'status': 64}}, syms, resolve)
    events = [('read', 'rng_before', 4)]
    def write(address, value):
        for offset in range(0, len(value), 1024):
            lines.append(f'write {address + offset:x} {value[offset:offset + 1024].hex()}')
    def call(name, *args, tag=None):
        lines.append(f'call {syms[name][0]:x} ' + ' '.join(f'{v:x}' for v in (*args, *([0] * (8 - len(args))))))
        events.append(('return', tag, 0))
    def read(tag, address, count):
        lines.append(f'read {address:x} {count:x}'); events.append(('read', tag, count))
    def set_data(mon, prop, value):
        write(0x0203f500, struct.pack('<I', value)); call('SetMonData', mon, props[prop], 0x0203f500)
    save1, save2, pc = bytearray(0x3d88), bytearray(0xf2c), bytearray(0x83d0)
    save1[4:6] = bytes([0, 10]); pc[0] = case.get('box', 0)
    struct.pack_into('<H', save1, 0x139c + 0x36 * 2, pc[0])
    save2[:8] = bytes([187] * 7 + [255]); save2[8] = 1
    struct.pack_into('<I', save2, 10, 0x11223344)
    for address, value in ((SAVE1, save1), (SAVE2, save2), (PC, pc)):
        write(address, value)
    write(PC - 16, bytes([165]) * 16); write(PC + 0x83d0, bytes([90]) * 16)
    values = {'gSaveBlock1Ptr': struct.pack('<I', SAVE1), 'gSaveBlock2Ptr': struct.pack('<I', SAVE2),
              'gPokemonStoragePtr': struct.pack('<I', PC), 'gPlayerParty': bytes(600),
              'gEnemyParty': bytes(600), 'gPlayerPartyCount': bytes([case.get('party_size', 1)]),
              'gSpecialVar_MonBoxId': b'\xff\xff', 'gSpecialVar_MonBoxPos': b'\xff\xff',
              'gBattleResults': bytes(68), 'gBattleCommunication': bytes(8), 'gBattleBufferA': bytes(2048),
              'gBattlerPartyIndexes': bytes(8), 'gLastUsedItem': struct.pack('<H', 4),
              'gBattleControllerExecFlags': bytes(4), 'gBattleTypeFlags': bytes(4),
              'gBattlescriptCurrInstr': struct.pack('<I', 0x0203f600)}
    for name, value in values.items(): write(syms[name][0], value)
    for index in range(case.get('party_size', 1)):
        call('CreateMon', syms['gPlayerParty'][0] + index * 100, 1, 5, 31, 1, 0, 1, 0)
    enemy = syms['gEnemyParty'][0]
    # Wild creation uses the recipient trainer ID. GiveMonToPlayer's OT_ID
    # setter assumes that key already matches; it does not re-encrypt a trade.
    call('CreateMon', enemy, resolve('SPECIES_RATTATA'), 50, 31, 1, 0, 1, 0x11223344)
    for prop, value in [('MON_DATA_HP', 45), ('MON_DATA_MAX_HP', 90), ('MON_DATA_STATUS', 64),
                        ('MON_DATA_MOVE1', 33), ('MON_DATA_MOVE2', 0), ('MON_DATA_MOVE3', 0), ('MON_DATA_MOVE4', 0),
                        ('MON_DATA_PP1', 3), ('MON_DATA_PP2', 0), ('MON_DATA_PP3', 0), ('MON_DATA_PP4', 0),
                        ('MON_DATA_PP_BONUSES', case.get('pp_bonus', 0)), ('MON_DATA_POKEBALL', 4)]:
        set_data(enemy, prop, value)
    call('CreateMon', TEMPLATE, 1, 5, 31, 1, 0, 1, 0)
    occupied = {box * 30 + slot for box in case.get('filled_boxes', []) for slot in range(30)}
    occupied.update(case.get('box', 0) * 30 + slot for slot in range(case.get('first_slots', 0)))
    occupied.discard(case.get('hole', -1))
    for index in sorted(occupied): call('CopyMon', PC + 4 + index * 80, TEMPLATE, 80)
    read('party_before', syms['gPlayerParty'][0], 600); read('pc_before', PC, 0x83d0)
    call('IsPlayerPartyAndPokemonStorageFull', tag='preflight')
    write(syms['gRngValue'][0], bytes(4))
    call('Cmd_handleballthrow')  # Guaranteed odds255; this does not spend a bag item.
    call('GiveMonToPlayer', enemy, tag='delivery')
    call('IsPlayerPartyAndPokemonStorageFull', tag='postflight')
    for name, count in [('gPlayerPartyCount', 1), ('gSpecialVar_MonBoxId', 2), ('gSpecialVar_MonBoxPos', 2), ('gRngValue', 4)]:
        read(name, syms[name][0], count)
    read('party_after', syms['gPlayerParty'][0], 600); read('pc_after', PC, 0x83d0)
    read('pc_left_guard', PC - 16, 16); read('pc_right_guard', PC + 0x83d0, 16)
    return '\n'.join(lines) + '\n', events


def observe(case, rows, events):
    if len(rows) != len(events): raise ValueError('Incomplete delivery observations.')
    raw = {}
    for row, (kind, tag, count) in zip(rows, events):
        if kind == 'return':
            if not re.fullmatch(r'return [0-9a-f]{8} steps \d+', row): raise ValueError('Invalid native return.')
            value = int(row.split()[1], 16)
        else:
            value = bytes.fromhex(row)
            if len(value) != count: raise ValueError('Native delivery read size changed.')
        if tag: raw[tag] = value
    if raw['pc_left_guard'] != bytes([165]) * 16 or raw['pc_right_guard'] != bytes([90]) * 16:
        raise ValueError('Native PC write crossed its audited allocation boundary.')
    party_index, result = case.get('party_size', 1), raw['delivery']
    box, slot = (int.from_bytes(raw[name], 'little') for name in ('gSpecialVar_MonBoxId', 'gSpecialVar_MonBoxPos'))
    party, pc = bytearray(raw['party_after']), bytearray(raw['pc_after'])
    mon, destination = None, 'none'
    if result == 0:
        start = party_index * 100; mon = decode_mon(party[start:start + 100]); destination = 'party'
        party[start:start + 100] = raw['party_before'][start:start + 100]
    elif result == 1:
        if not 0 <= box < 14 or not 0 <= slot < 30: raise ValueError('Native PC destination outside storage.')
        start = 4 + (box * 30 + slot) * 80; mon = decode_mon(pc[start:start + 80], True); destination = 'pc'
        pc[start:start + 80] = raw['pc_before'][start:start + 80]
    actual = {key: raw[key] for key in ('preflight', 'delivery', 'postflight')}
    actual.update({'party_count': int.from_bytes(raw['gPlayerPartyCount'], 'little'), 'box': box, 'slot': slot,
        'destination': destination, 'mon': mon, 'rng_before': int.from_bytes(raw['rng_before'], 'little'),
        'rng_after': int.from_bytes(raw['gRngValue'], 'little'),
        'neighbors_preserved': bytes(party) == raw['party_before'] and bytes(pc) == raw['pc_before']})
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reference-rom', 'reference-elf', 'reference-state', 'candidate-rom', 'candidate-elf', 'candidate-state', 'cases'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--name', required=True); args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name): parser.error('Use a safe evidence name.')
    output = ROOT / '.tools/benchmarks' / args.name
    if output.exists(): parser.error('Preserve prior evidence; choose another name.')
    cases = validate(json.loads(args.cases.read_text())); output.mkdir(parents=True)
    engine = ROOT / '.tools/pokeemerald-host'; executable, core = build_driver()
    layouts = [verify_layout(engine, output), verify_native_layout(engine, output,
        ROOT / 'scripts/quality/delivery_layout.c', [0x83d0, 100, 80, 4, 0x139c, 8, 10])]
    resolve, props = constants(engine), property_ids(engine)
    evidence = {'kind': 'Controlled capture/delivery function chain; no bag UI, Dex registration or durable save proof',
        'core': core, 'layouts': layouts, 'runner_sha256': digest(Path(__file__)), 'cases_sha256': digest(args.cases),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()), 'sides': {}}
    for side in ('reference', 'candidate'):
        rom, elf, state = (getattr(args, side + '_' + name) for name in ('rom', 'elf', 'state'))
        identity, syms = verify_bundle(side, rom, elf, state, output, FUNCTIONS, GLOBALS)
        programs = [program(case, syms, resolve, props) for case in cases]
        if len({text for text, _ in programs}) != len(cases): raise ValueError('Duplicate effective delivery fixtures.')
        sequence = ''.join(text for text, _ in programs)
        (output / (side + '-commands.txt')).write_text(sequence)
        process = subprocess.run([str(executable), str(rom), str(state)], input=sequence, capture_output=True, text=True, timeout=60)
        (output / (side + '-stdout.txt')).write_text(process.stdout); (output / (side + '-stderr.txt')).write_text(process.stderr)
        if process.returncode or digest(rom) != identity['rom_sha256']: raise ValueError('Native delivery fixture failed.')
        rows, results = process.stdout.splitlines(), []
        for case, (_, events) in zip(cases, programs):
            actual = observe(case, rows[:len(events)], events); rows = rows[len(events):]
            results.append({'id': case['id'], 'actual': actual, 'expected': case['expected'], 'pass': actual == case['expected']})
        if rows: raise ValueError('Unexpected trailing delivery observations.')
        evidence['sides'][side] = {**identity, 'cases': results}
    passed = sum(a['pass'] and b['pass'] for a, b in zip(evidence['sides']['reference']['cases'], evidence['sides']['candidate']['cases']))
    evidence.update({'passed': passed, 'total': len(cases), 'full_mechanics_gate_complete': False, 'human_quality_approval': 'pending'})
    (output / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n'); print(json.dumps({'passed': passed, 'total': len(cases)}))
    if passed != len(cases): raise SystemExit(1)


if __name__ == '__main__': main()
