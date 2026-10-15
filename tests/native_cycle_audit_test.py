"""Pure corruption tests for the offline battery-cycle proof boundary."""
from pathlib import Path
import base64
import copy
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zlib

HERE = Path(__file__).resolve().parent
SOURCE = HERE if (HERE / 'audit_native_battery_cycle.py').is_file() else HERE.parent / 'scripts/quality'
sys.path.insert(0, str(SOURCE))
import audit_native_battery_cycle as audit


def tempdir():
    # Keep synthetic receipts for inspection; no destructive cleanup.
    return Path(tempfile.mkdtemp(prefix='synthetic-cycle-', dir=HERE if SOURCE == HERE else audit.R / '.tools'))


def json_file(path, value):
    path.write_text(json.dumps(value))


def extraction_fixture():
    directory = tempdir()
    before, after = b'A' * 131072, b'B' * 131072
    identity = dict(rom_sha256=audit.ROM, mgba_revision=audit.REV,
                    files={'battery.sav': audit.sha(before)}, inputs={str(directory / 'target.gba'): audit.ROM})
    json_file(directory / 'identity.json', identity)
    save = dict(worker=dict(startedAt=200, endedAt=300,saveEpoch=1,playbackEpoch=1,initialGuestCounter=100,finalGuestCounter=200))
    packets = [dict(type='paused-flash-receipt', at=at, size=131072, storedBytesExact=True,saveEpoch=1,counter=50 if at==100 else 250,
                    sha256=audit.sha(data), bytesBase64=base64.b64encode(data).decode())
               for at, data in [(100, before), (400, after)]]
    post = dict(worker=dict(startedAt=500,saveEpoch=1,playbackEpoch=1,initialGuestCounter=300), saveProtocol=dict(saveActions=packets))
    save_path, post_path = directory / 'save.json', directory / 'post.json'
    json_file(save_path, save); json_file(post_path, post)
    fact = dict(loss_free=True, caught_up_at_close=True, planned_mismatch_ticks=0,
                foreground_observed=True, input_transport=dict(all_reported_edges_accounted_for=True),
                audio=dict(warmupOutputFrames=0, underrunOutputFrames=0, droppedSourceFrames=0),
                controller_replay=dict(all_planned_masks_reported=True, status='complete'))
    return directory, save_path, post_path, fact


class BrowserProofTests(unittest.TestCase):
    def extract(self, post, save, fact):
        with mock.patch.object(audit.worker_audit, 'audit', return_value=fact), \
             mock.patch.object(audit.saved_audit, 'storage_observation', return_value={'storage_reference_integrity': True}), \
             mock.patch.object(audit.flash_audit, 'audit_bytes', side_effect=[{'counter': 13}, {'counter': 14}]), \
             mock.patch.object(audit.flash_audit, 'compare', return_value={'passed': True}):
            return audit.extract_facts(post, save)

    def test_extract_requires_true_observations_and_zero_losses(self):
        for key, value in [('loss_free', False), ('caught_up_at_close', 1), ('foreground_observed', 'false'),
                           ('planned_mismatch_ticks', 1)]:
            directory, save, post, fact = extraction_fixture(); fact[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): self.extract(post, save, fact)
        directory, save, post, fact = extraction_fixture()
        result, raw = self.extract(post, save, fact)
        self.assertEqual(result['after_counter'], 14)
        for value in [False, 1, 'false']:
            report = json.loads(post.read_bytes()); report['saveProtocol']['saveActions'][1]['storedBytesExact'] = value
            json_file(post, report)
            with self.subTest(value=value), self.assertRaises(ValueError): self.extract(post, save, fact)

    def test_extract_rejects_corrupted_backup_and_wrong_save_order(self):
        for field, value in [('sha256', '0' * 64), ('size', 32768), ('at', 250), ('bytesBase64', '!bad')]:
            directory, save, post, fact = extraction_fixture()
            report = json.loads(post.read_bytes()); report['saveProtocol']['saveActions'][1][field] = value
            json_file(post, report)
            with self.subTest(field=field), self.assertRaises((ValueError, base64.binascii.Error)):
                self.extract(post, save, fact)

    def test_save_cycle_cannot_cross_an_import_or_counter_rewind(self):
        for field,value in [('saveEpoch',2),('playbackEpoch',2),('initialGuestCounter',200)]:
            directory, save, post, fact = extraction_fixture()
            report = json.loads(post.read_bytes()); report['worker'][field] = value; json_file(post,report)
            with self.subTest(field=field),self.assertRaises(ValueError):self.extract(post,save,fact)

    def proof_fixture(self):
        directory, save, post, fact = extraction_fixture()
        proof, raw = self.extract(post, save, fact)
        for name, data in zip(('before.sav', 'after.sav'), raw): (directory / name).write_bytes(data)
        json_file(directory / 'browser.json', proof)
        return directory, proof, raw

    def test_cold_reverification_rejects_claim_changes_and_changed_raw_files(self):
        for field, value in [('kind', 'wrong'), ('rom', '0' * 64), ('core', 'wrong'),
                             ('after_counter', 15), ('before_sha256', '0' * 64), ('identity_sha256', '0' * 64),
                             ('comparison', {'passed': False})]:
            directory, proof, raw = self.proof_fixture(); changed = copy.deepcopy(proof); changed[field] = value
            json_file(directory / 'browser.json', changed)
            with mock.patch.object(audit, 'extract_facts', return_value=(proof, raw)):
                with self.subTest(field=field), self.assertRaises(ValueError): audit.reverify_browser(directory)
        for filename in ['before.sav', 'after.sav', 'save.json', 'post.json']:
            directory, proof, raw = self.proof_fixture(); (directory / filename).write_bytes(b'changed')
            with mock.patch.object(audit, 'extract_facts', return_value=(proof, raw)):
                with self.subTest(filename=filename), self.assertRaises(ValueError): audit.reverify_browser(directory)

    def test_frozen_dependency_tampering_and_existing_outputs_are_rejected(self):
        directory, proof, raw = self.proof_fixture()
        proof['dependencies'] = audit.freeze_dependencies(directory / 'cycle-dependencies')
        json_file(directory / 'browser.json', proof)
        with mock.patch.object(audit, 'extract_facts', return_value=(proof, raw)):
            self.assertEqual(audit.reverify_browser(directory)[2], raw[1])
            (directory / 'cycle-dependencies/flash_audit.py').write_text('changed')
            with self.assertRaises(ValueError): audit.reverify_browser(directory)
        with self.assertRaises(FileExistsError): audit.freeze_dependencies(directory / 'cycle-dependencies')
        with self.assertRaises(FileExistsError): audit.write_json(directory / 'browser.json', {})


class CaptureMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = bytes(16777216)
        state = bytearray(0x61000); struct.pack_into('<I', state, 0, 0x01000007)
        struct.pack_into('<I', state, 8, zlib.crc32(cls.rom)); cls.state = bytes(state)
        cls.after = b'A' * 131072
        cls.metadata = dict(controller_only=True, trace_only=True, state_input_sha256=None,
                            battery_input_sha256=audit.sha(cls.after), rom_sha256=audit.ROM,
                            mgba_revision=audit.REV, frequency=16777216, frame_cycles=280896,
                            sample_rate=65536, frames=3752, input_sha256=audit.COLD_ROUTE)

    def validate(self, meta=None, state=None, flash=None):
        real_sha = audit.sha
        with mock.patch.object(audit, 'sha', side_effect=lambda data: audit.ROM if data is self.rom else real_sha(data)):
            return audit.validate_capture(meta or self.metadata, self.state if state is None else state,
                                          self.after if flash is None else flash, self.after, self.rom)

    def test_pinned_metadata_rejects_loose_flags_route_frames_and_state_sources(self):
        self.validate()
        for key, value in [('controller_only', 1), ('trace_only', 'false'), ('frames', 3751),
                           ('input_sha256', '0' * 64), ('state_input_sha256', 'state'),
                           ('sample_rate', 32768), ('frequency', 1), ('mgba_revision', 'wrong'),
                           ('battery_input_sha256', '0' * 64)]:
            meta = dict(self.metadata); meta[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): self.validate(meta)
        for state in [self.state[:-1], bytes(len(self.state))]:
            with self.assertRaises(ValueError): self.validate(state=state)
        with self.assertRaises(ValueError): self.validate(flash=b'wrong')

    def test_checks_remain_enabled_under_python_optimization(self):
        code = ('import sys;sys.path.insert(0,' + repr(str(SOURCE)) + ');'
                'import audit_native_battery_cycle as a;a.require(False,"must reject")')
        result = subprocess.run([sys.executable, '-B', '-O', '-c', code], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('must reject', result.stderr)


class LoadedStateTests(unittest.TestCase):
    def fixture(self):
        sections = {index: bytearray(size) for index, size in enumerate(audit.flash_audit.PAYLOADS)}
        old1 = bytearray(0x3d88); old2 = sections[0]; pc = b''.join(sections[i] for i in range(5, 14))
        key = 0x12345678; struct.pack_into('<I', old2, 0xac, key)
        old1[0x234] = 3; old1[0x238:0x490] = b'A' * 600
        struct.pack_into('<I', old1, 0x159c, 14 ^ key); struct.pack_into('<I', old1, 0x490, 1000 ^ key)
        old2[17] = 10
        cursor = 0
        for index in range(1, 5):
            length = len(sections[index]); sections[index][:] = old1[cursor:cursor + length]; cursor += length
        state = bytearray(0x61000)
        def put(address, data):
            offset = 0x21000 + address - 0x02000000 if address < 0x03000000 else 0x19000 + address - 0x03000000
            state[offset:offset + len(data)] = data
        addresses = [0x02001000, 0x02006000, 0x02008000]
        for address, value in zip([0x03005d8c, 0x03005d90, 0x03005d94], addresses): put(address, struct.pack('<I', value))
        put(addresses[0], old1); put(addresses[1], old2); put(addresses[2], pc)
        put(0x020244e9, b'\x03'); put(0x020244ec, b'A' * 600); put(0x03006200, struct.pack('<I', 14))
        return state, sections, put

    def checks(self, state, sections):
        with mock.patch.object(audit.flash_audit, 'audit_bytes', return_value={'counter': 14}), \
             mock.patch.object(audit.flash_audit, 'unpack_slot', return_value=(14, sections)):
            return audit.loaded_checks(state, b'synthetic raw Flash')[0]

    def test_loaded_counter_stat_party_count_and_playtime_distinguish_cold_state(self):
        state, sections, put = self.fixture(); self.assertTrue(all(self.checks(state, sections).values()))
        for address, data, field in [(0x03006200, struct.pack('<I', 13), 'loaded_save_counter_exact'),
                                     (0x02001000 + 0x159c, struct.pack('<I', 13 ^ 0x12345678), 'loaded_saved_game_stat_exact'),
                                     (0x020244e9, b'\x02', 'loaded_party_count_exact'),
                                     (0x02006000 + 17, b'\x09', 'loaded_playtime_nondecreasing')]:
            state, sections, put = self.fixture(); put(address, data)
            with self.subTest(field=field): self.assertFalse(self.checks(state, sections)[field])
        state, sections, put = self.fixture(); put(0x03005d8c, struct.pack('<I', 0))
        with self.assertRaises(ValueError): self.checks(state, sections)


if __name__ == '__main__':
    unittest.main()
