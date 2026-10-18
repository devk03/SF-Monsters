"""Reject QA publication and smoke replays presented as full-world evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class PreviewGate(unittest.TestCase):
    def setUp(self):
        root=ROOT/'.tools/romhack-drafts';root.mkdir(parents=True,exist_ok=True)
        self.folder=Path(tempfile.mkdtemp(prefix='publication-gate-test-',dir=root))
        for name in ('draft','native','wasm'):(self.folder/name).mkdir()
        self.source=dict(profile='world-blockout',fixture=None,save_magic=0x5743,save_schema=1,
                         patch_roundtrip='byte-identical',source_contract={'passed':True},
                         compiled_maps={'passed':True},target_sha256='b'*64)
        self.native=dict(passed=True,rom_sha256='b'*64,maps=58,connections=76,gym_warps=16,room_warps=26)
        self.session=dict(controller_only=True,rom_sha256='b'*64,state_input_sha256='1'*64,
                          battery_input_sha256='2'*64,mgba_revision='pinned')
        self.capture=dict(self.session,frames=5,input_sha256=hashlib.sha256(b'16,2\n0,3\n').hexdigest())
        self.state=bytes(0x61000);digest=hashlib.sha256(self.state[0x19000:]).hexdigest()
        self.proof=dict(passed=True,rom_sha256='b'*64,different_bytes=0,ram_bytes=294912,
                        frames=5,native_ram_sha256=digest,wasm_ram_sha256=digest)
        (self.folder/'native/inputs.json').write_text('[[16,2],[0,3]]')
        (self.folder/'native/returned.state').write_bytes(self.state)
        (self.folder/'wasm/capture.state').write_bytes(self.state)

    def reject(self,message):
        for path,data in [('draft/manifest.json',self.source),('native/returns-result.json',self.native),
                          ('native/session.json',self.session),('wasm/capture.json',self.capture),
                          ('wasm/ram-parity.json',self.proof)]:
            (self.folder/path).write_text(json.dumps(data))
        process=subprocess.run([sys.executable,str(ROOT/'scripts/romhack/stage_world_preview.py'),
            '--draft',str(self.folder/'draft'),'--native-proof',str(self.folder/'native/returns-result.json'),
            '--wasm-proof',str(self.folder/'wasm/ram-parity.json'),'--version','999.0.0-world-preview'],
            capture_output=True,text=True)
        self.assertNotEqual(process.returncode,0)
        self.assertIn(message,process.stderr)
        self.assertFalse((ROOT/'romhack/releases/999.0.0-world-preview').exists())

    def test_injected_fixture_is_not_a_normal_world(self):
        self.source.update(profile='module-playtest',fixture={'kind':'town-services'})
        self.reject('Only a validated normal SF world')

    def test_qa_save_identity_cannot_be_published(self):
        self.source['save_magic']=0x5751;self.reject('Only a validated normal SF world')

    def test_shorter_wasm_smoke_does_not_cover_full_native_trace(self):
        self.capture['frames']=self.proof['frames']=4
        self.reject('complete native circuit inputs')

    def test_other_initial_state_does_not_qualify(self):
        self.capture['state_input_sha256']='3'*64;self.reject('complete native circuit inputs')

    def test_other_controller_trace_does_not_qualify(self):
        self.capture['input_sha256']='4'*64;self.reject('complete native circuit inputs')

    def test_success_strings_are_not_boolean_passes(self):
        self.native['passed']='true';self.reject('complete matching native return circuit')

    def test_uncontrolled_capture_cannot_qualify(self):
        self.capture['controller_only']='true';self.reject('complete native circuit inputs')

    def test_raw_guest_ram_must_match_not_only_report(self):
        data=bytearray(self.state);data[0x21000]=1
        (self.folder/'wasm/capture.state').write_bytes(data)
        self.reject('Actual final native/WASM guest RAM')


if __name__=='__main__':unittest.main()
