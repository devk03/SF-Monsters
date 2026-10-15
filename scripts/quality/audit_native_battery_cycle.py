"""Offline audit of one private v80 stationary browser-save/native-cold cycle.

CLI: extract POST_REPORT SAVE_REPORT NEW_PRIVATE_OUTPUT; cold OUTPUT CAPTURE.
Use --label NAME for a fresh cold re-audit. No emulator is started. This proves
only the recorded private stationary subset, not public or campaign persistence.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import re
import struct
import sys
import zlib

R = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEPENDENCY_DIRECTORY = HERE if (HERE / 'audit_worker_proof.py').is_file() else R / 'scripts/quality'
sys.path.insert(0, str(DEPENDENCY_DIRECTORY))
import audit_worker_proof as worker_audit
import audit_saved_frames as saved_audit
import flash_audit

REV = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
ROM = '9b5e6bc4fa5658ec686ab95cc3b1108feef0875393503c7adb5d210aaa0d1edd'
COLD_ROUTE = '6e4f7ff1e4a9c6b9bfa7315680fdd037f037579be8479aeb7597d5ea3c13c34f'
COLD_FRAMES = 3752
DEPENDENCIES = ('audit_worker_proof.py', 'audit_saved_frames.py', 'flash_audit.py', 'audit_web_performance.py')
SOURCE_PATHS = {name: DEPENDENCY_DIRECTORY / name for name in DEPENDENCIES}
SOURCE_PATHS.update({'audit_native_battery_cycle.py': Path(__file__),
                     'capture_core.py': R / 'scripts/quality/capture_core.py'})
SOURCES_AT_LOAD = {name: path.read_bytes() for name, path in SOURCE_PATHS.items()}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same(value, expected, message):
    require(type(value) is type(expected) and value == expected, message)


def true(value, message):
    same(value, True, message)


def read_json(path):
    def invalid(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(path.read_bytes(), parse_constant=invalid)


def private_path(path):
    path.resolve().relative_to((R / '.tools').resolve())
    return path


def write_json(path, value):
    with path.open('x') as out:
        json.dump(value, out, indent=2, allow_nan=False)
        out.write('\n')


def dependency_bytes():
    # Refuse to label new on-disk code as the already imported verifier.
    for name, path in SOURCE_PATHS.items():
        same(path.read_bytes(), SOURCES_AT_LOAD[name], 'Verifier dependency changed during audit: ' + name)
    return dict(SOURCES_AT_LOAD)


def freeze_dependencies(directory):
    sources = dependency_bytes()
    directory.mkdir()
    for name, data in sources.items():
        with (directory / name).open('xb') as out:
            out.write(data)
    return {name: sha(data) for name, data in sources.items()}


def extract_facts(post, save):
    same(post.parent.resolve(), save.parent.resolve(), 'Reports must share a frozen session')
    identity_path = post.parent / 'identity.json'
    identity = read_json(identity_path)
    same(identity['rom_sha256'], ROM, 'Unsupported v80 ROM')
    same(identity['mgba_revision'], REV, 'Unsupported native core')
    reports = [read_json(path) for path in (save, post)]
    facts = [worker_audit.audit(report, identity, post.parent) for report in reports]
    stores = [saved_audit.storage_observation(report) for report in reports]
    for fact in facts:
        true(fact['loss_free'], 'Guest frame credits were dropped')
        true(fact['caught_up_at_close'], 'Guest frame debt remains')
        same(fact['planned_mismatch_ticks'], 0, 'Native frame calls differ from plan')
        true(fact['foreground_observed'], 'Runtime was not continuously visible')
        true(fact['input_transport']['all_reported_edges_accounted_for'], 'Input transport is incomplete')
        for key in ('warmupOutputFrames', 'underrunOutputFrames', 'droppedSourceFrames'):
            same(fact['audio'][key], 0, 'Audio loss: ' + key)
    route = facts[0]['controller_replay']
    require(type(route) is dict, 'Missing ordinary Save controller route')
    true(route['all_planned_masks_reported'], 'Ordinary Save route masks differ')
    same(route['status'], 'complete', 'Ordinary Save route is incomplete')
    packets = [action for action in reports[1]['saveProtocol']['saveActions']
               if action['type'] == 'paused-flash-receipt']
    same(len(packets), 2, 'Require exactly two paused Flash backups')
    for key in ('saveEpoch', 'playbackEpoch'):
        same(reports[0]['worker'][key], reports[1]['worker'][key], 'Save cycle reset presentation state: ' + key)
    for packet in packets:
        same(packet['saveEpoch'], reports[0]['worker']['saveEpoch'], 'Paused backup crossed a save mutation')
        worker_audit.num(packet['counter'], 'backup native counter', integer=True, maximum=0xffffffff)
        true(packet['storedBytesExact'], 'Paused backup differs from browser storage')
        same(packet['size'], 131072, 'Paused backup size differs')
        worker_audit.num(packet['at'], 'paused backup time')
    require(packets[0]['at'] < reports[0]['worker']['startedAt'] < reports[0]['worker']['endedAt']
            < packets[1]['at'] < reports[1]['worker']['startedAt'], 'Backup/Save/observation order differs')
    for before_counter, after_counter in [
            (packets[0]['counter'], reports[0]['worker']['initialGuestCounter']),
            (reports[0]['worker']['finalGuestCounter'], packets[1]['counter']),
            (packets[1]['counter'], reports[1]['worker']['initialGuestCounter'])]:
        require(((after_counter - before_counter) & 0xffffffff) < 0x80000000,
                'Native counter regressed across Save/backup boundaries')
    raw = [base64.b64decode(packet['bytesBase64'], validate=True) for packet in packets]
    for packet, data in zip(packets, raw):
        same(len(data), 131072, 'Raw Flash size differs')
        same(sha(data), packet['sha256'], 'Raw Flash backup hash differs')
    same(sha(raw[0]), identity['files']['battery.sav'], 'Before Flash differs from boot battery')
    before, after = [flash_audit.audit_bytes(data) for data in raw]
    comparison = flash_audit.compare(before, after, 1)
    true(comparison['passed'], 'Stationary Save comparison failed: ' + str(comparison))
    rom_paths = [path for path in identity['inputs'] if path.endswith('.gba')]
    same(len(rom_paths), 1, 'Ambiguous source ROM')
    proof = dict(kind='private-stationary-browser-save-cycle', rom=ROM, core=REV,
                 rom_path=str(Path(rom_paths[0]).resolve()), identity_sha256=sha(identity_path.read_bytes()),
                 save_report=str(save.resolve()), post_report=str(post.resolve()),
                 save_report_sha256=sha(save.read_bytes()), post_report_sha256=sha(post.read_bytes()),
                 before_sha256=sha(raw[0]), after_sha256=sha(raw[1]),
                 before_counter=before['counter'], after_counter=after['counter'],
                 comparison=comparison, runtime=facts, storage=stores,
                 scope='Private Chrome Worker stationary battery cycle; native cold consumption pending. '
                       'No public storage, physical device or campaign approval.')
    return proof, raw


def reverify_browser(out):
    proof_path = out / 'browser.json'
    proof = read_json(proof_path)
    same(proof['kind'], 'private-stationary-browser-save-cycle', 'Wrong browser proof kind')
    same(proof['rom'], ROM, 'Browser proof ROM differs')
    same(proof['core'], REV, 'Browser proof core differs')
    true(proof['comparison']['passed'], 'Browser proof comparison failed')
    for field in ('save_report', 'post_report'):
        same(sha(Path(proof[field]).read_bytes()), proof[field + '_sha256'], 'Bound raw report changed: ' + field)
    actual, raw = extract_facts(Path(proof['post_report']), Path(proof['save_report']))
    for field in ('rom', 'core', 'rom_path', 'save_report_sha256', 'post_report_sha256',
                  'before_sha256', 'after_sha256', 'before_counter', 'after_counter', 'comparison'):
        same(proof[field], actual[field], 'Reverified browser proof differs: ' + field)
    if 'identity_sha256' in proof:
        same(proof['identity_sha256'], actual['identity_sha256'], 'Frozen session identity changed')
    for name, data in zip(('before.sav', 'after.sav'), raw):
        same((out / name).read_bytes(), data, 'Current full Flash differs from bound backup: ' + name)
    if 'auditor_sha256' in proof:
        same(sha((out / 'cycle-auditor.py').read_bytes()), proof['auditor_sha256'], 'Frozen cycle auditor changed')
    if 'dependencies' in proof:
        require(type(proof['dependencies']) is dict and set(proof['dependencies']) == set(SOURCE_PATHS),
                'Frozen browser dependency manifest is incomplete')
        for name, digest in proof['dependencies'].items():
            require(name in (*DEPENDENCIES, 'audit_native_battery_cycle.py', 'capture_core.py'), 'Unknown dependency')
            same(sha((out / 'cycle-dependencies' / name).read_bytes()), digest, 'Frozen dependency changed: ' + name)
    return proof, actual, raw[1]


def validate_capture(meta, state, flash, after, rom):
    same(sha(rom), ROM, 'Cold ROM hash differs')
    same(len(rom), 16777216, 'Cold ROM size differs')
    same(len(state), 0x61000, 'Native state size differs')
    same(struct.unpack_from('<I', state)[0], 0x01000007, 'Native state version differs')
    same(struct.unpack_from('<I', state, 8)[0], zlib.crc32(rom), 'Native state ROM CRC differs')
    same(state[16:32], rom[0xa0:0xb0], 'Native state cartridge header differs')
    for field in ('controller_only', 'trace_only'):
        true(meta[field], 'Capture provenance flag differs: ' + field)
    same(meta['state_input_sha256'], None, 'Cold capture used an input state')
    same(meta['battery_input_sha256'], sha(after), 'Cold capture battery input differs')
    same(meta['rom_sha256'], ROM, 'Cold capture ROM differs')
    same(meta['mgba_revision'], REV, 'Cold capture core differs')
    for field, expected in [('frequency', 16777216), ('frame_cycles', 280896), ('sample_rate', 65536),
                            ('frames', COLD_FRAMES), ('input_sha256', COLD_ROUTE)]:
        same(meta[field], expected, 'Pinned cold capture differs: ' + field)
    same(flash, after, 'Native Flash output differs from browser backup')


def loaded_checks(state, after):
    def mem(address, count):
        if 0x02000000 <= address and address + count <= 0x02040000:
            offset = 0x21000 + address - 0x02000000
        elif 0x03000000 <= address and address + count <= 0x03008000:
            offset = 0x19000 + address - 0x03000000
        else:
            raise ValueError('Captured native pointer outside RAM')
        require(count >= 0 and len(state[offset:offset + count]) == count, 'Truncated native RAM')
        return state[offset:offset + count]
    ptr = lambda address: struct.unpack('<I', mem(address, 4))[0]
    # Exact v80 symbol addresses; this function is gated by the pinned ROM hash.
    sb1 = mem(ptr(0x03005d8c), 0x3d88)
    sb2 = mem(ptr(0x03005d90), 0xf2c)
    pc = mem(ptr(0x03005d94), 33744)
    parsed = flash_audit.audit_bytes(after)
    selected = flash_audit.unpack_slot(after, parsed['counter'] % 2)
    require(selected is not None, 'Latest physical Flash slot is invalid')
    _, sections = selected
    old1 = b''.join(sections[index] for index in range(1, 5))
    old2 = sections[0]
    oldpc = b''.join(sections[index] for index in range(5, 14))
    checks = dict(loaded_save_counter_exact=ptr(0x03006200) == parsed['counter'],
                  loaded_party_count_exact=mem(0x020244e9, 1)[0] == old1[0x234],
                  loaded_party_exact=mem(0x020244ec, 600) == old1[0x238:0x490],
                  loaded_storage_exact=pc == oldpc, loaded_position_exact=sb1[:6] == old1[:6],
                  loaded_flags_vars_exact=sb1[0x1270:0x159c] == old1[0x1270:0x159c],
                  loaded_settings_exact=sb2[0x13:0x18] == old2[0x13:0x18])
    def playtime(data):
        require(struct.unpack_from('<H', data, 14)[0] <= 999 and all(data[index] < 60 for index in (16, 17, 18)),
                'Loaded playtime is outside native bounds')
        return ((struct.unpack_from('<H', data, 14)[0] * 60 + data[16]) * 60 + data[17]) * 60 + data[18]
    checks['loaded_playtime_nondecreasing'] = playtime(sb2) >= playtime(old2)
    key = struct.unpack_from('<I', sb2, 0xac)[0]
    oldkey = struct.unpack_from('<I', old2, 0xac)[0]
    for field, offset in [('loaded_saved_game_stat_exact', 0x159c), ('loaded_money_exact', 0x490)]:
        checks[field] = (struct.unpack_from('<I', sb1, offset)[0] ^ key) == (struct.unpack_from('<I', old1, offset)[0] ^ oldkey)
    for name, (offset, count) in flash_audit.POCKETS.items():
        def decode(data, encryption):
            return [(struct.unpack_from('<H', data, offset + index * 4)[0],
                     struct.unpack_from('<H', data, offset + index * 4 + 2)[0] ^ (encryption & 65535))
                    for index in range(count)]
        checks['loaded_bag_' + name] = decode(sb1, key) == decode(old1, oldkey)
    return checks, parsed, list(struct.unpack('<hhBB', sb1[:6]))


def audit_cold(out, cold):
    private_path(out); private_path(cold)
    proof, reverified, after = reverify_browser(out)
    meta = read_json(cold / 'capture.json')
    state = (cold / 'capture.state').read_bytes()
    flash = (cold / 'capture.sav').read_bytes()
    rom = Path(proof['rom_path']).read_bytes()
    validate_capture(meta, state, flash, after, rom)
    checks, parsed, position = loaded_checks(state, after)
    same(parsed['counter'], proof['after_counter'], 'Native counter differs from bound browser proof')
    checks['full_flash_exact'] = flash == after
    return dict(kind='private-native-cold-cycle', passed=all(checks.values()), checks=checks,
                counter=parsed['counter'], position=position, full_flash_sha256=sha(flash),
                state_sha256=sha(state), capture_metadata_sha256=sha((cold / 'capture.json').read_bytes()),
                capture_directory=str(cold.resolve()), capture_source_commit=meta.get('source_commit'),
                rom=ROM, core=REV, browser_proof_sha256=sha((out / 'browser.json').read_bytes()),
                browser_reverified_from_raw=True, reverified_identity_sha256=reverified['identity_sha256'],
                current_verifier_dependency={'capture_core.py': sha((R / 'scripts/quality/capture_core.py').read_bytes())},
                scope='One private stationary controller-only battery cycle and native loaded-state checks; '
                      'not public storage, physical devices, fifty campaign checkpoints or full release approval.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    extract = sub.add_parser('extract')
    extract.add_argument('post', type=Path); extract.add_argument('save', type=Path); extract.add_argument('out', type=Path)
    cold = sub.add_parser('cold')
    cold.add_argument('out', type=Path); cold.add_argument('capture', type=Path)
    cold.add_argument('--label', default='', help='Fresh audit label; existing evidence is preserved')
    args = parser.parse_args(argv)
    if args.mode == 'extract':
        private_path(args.out)
        proof, raw = extract_facts(args.post, args.save)
        args.out.mkdir()
        proof['auditor_sha256'] = sha(Path(__file__).read_bytes())
        proof['dependencies'] = freeze_dependencies(args.out / 'cycle-dependencies')
        with (args.out / 'cycle-auditor.py').open('xb') as output:
            output.write(Path(__file__).read_bytes())
        for name, data in zip(('before.sav', 'after.sav'), raw):
            with (args.out / name).open('xb') as output:
                output.write(data)
        write_json(args.out / 'browser.json', proof)
        print(json.dumps({'out': str(args.out), 'before': proof['before_counter'],
                          'after': proof['after_counter'], 'comparison': proof['comparison']}, allow_nan=False))
    else:
        if args.label and not re.fullmatch('[a-z0-9][a-z0-9-]{0,31}', args.label):
            parser.error('Use a bounded lowercase fresh audit label')
        result = audit_cold(args.out, args.capture)
        stem = 'native' + ('.' + args.label if args.label else '')
        result['auditor_sha256'] = sha(Path(__file__).read_bytes())
        result['dependencies'] = freeze_dependencies(args.out / (stem + '-dependencies'))
        write_json(args.out / (stem + '.json'), result)
        print(json.dumps(result, allow_nan=False))
        require(result['passed'], 'Native loaded-state checks failed: ' + str(result['checks']))


if __name__ == '__main__':
    main()
