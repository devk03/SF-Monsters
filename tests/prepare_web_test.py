"""Preparing verified runtime files must preserve authored SF frontend code."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrepareWebTest(unittest.TestCase):
    def test_upstream_preparation_preserves_owned_frontend(self):
        # All artifacts remain available for inspection after the test.
        root = Path(tempfile.mkdtemp(prefix='prepare-web-test-', dir=ROOT / '.tools'))
        script = root / 'scripts/prepare_web.py'
        script.parent.mkdir()
        shutil.copy2(ROOT / 'scripts/prepare_web.py', script)
        output = root / 'web/public/emulator'
        vendor = root / 'web/node_modules/@wasm-gaming/mgba-wasm/dist/mgba'
        output.mkdir(parents=True)
        vendor.mkdir(parents=True)
        owned = ('mgba.sdk.js', 'mgba.audio-worklet.js', 'mgba.performance.js', 'mgba.audio-reset.js', 'mgba.state.js')
        for name in owned:
            (output / name).write_bytes(b'authored SF source: ' + name.encode())
            (vendor / name).write_bytes(b'upstream replacement')
        (vendor / 'mgba.options.js').write_bytes(b'upstream unchanged companion')
        shim = root / 'emulator/mgba_0105_shim.c'
        shim.parent.mkdir()
        shim.write_bytes(b'fixture shim identity')
        artifacts = {}
        for name in ('mgba.js', 'mgba.wasm'):
            data = b'verified runtime: ' + name.encode()
            (output / name).write_bytes(data)
            artifacts[name] = hashlib.sha256(data).hexdigest()
        (output / 'core-build.json').write_text(json.dumps({
            'mgba_revision': '26b7884bc25a5933960f3cdcd98bac1ae14d42e2',
            'shim_sha256': hashlib.sha256(shim.read_bytes()).hexdigest(),
            'artifacts': artifacts}))
        before = {name: (output / name).read_bytes() for name in owned}
        for _ in range(2):
            subprocess.run([sys.executable, str(script)], check=True,
                           capture_output=True, timeout=10)
            self.assertEqual({name: (output / name).read_bytes() for name in owned}, before)
            self.assertEqual((output / 'mgba.options.js').read_bytes(),
                             b'upstream unchanged companion')
            self.assertEqual({name: hashlib.sha256((output / name).read_bytes()).hexdigest()
                              for name in artifacts}, artifacts)


if __name__ == '__main__':
    unittest.main()
