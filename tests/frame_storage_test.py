"""Preserve every captured byte and reject damaged compressed frame evidence."""
from pathlib import Path
import gzip
import hashlib
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/quality'))
from frame_storage import compress_capture, verify_frames


class FrameStorage(unittest.TestCase):
    def setUp(self):
        # Keep fixtures for inspection; do not remove evidence on test completion.
        self.directory = Path(tempfile.mkdtemp(prefix='frame-storage-', dir=ROOT / '.tools/benchmarks'))
        self.prefix = self.directory / 'capture'
        self.raw = bytes(range(256)) * 1200
        self.prefix.with_suffix('.rgba').write_bytes(self.raw)
        self.metadata = {'frames': 2, 'trace_only': False, 'controller_only': True}
        self.prefix.with_suffix('.json').write_text(json.dumps(self.metadata))

    def test_raw_and_compressed_roundtrip_keep_every_byte(self):
        expected = (hashlib.sha256(self.raw).hexdigest(), len(self.raw))
        self.assertEqual(verify_frames(self.prefix, self.metadata), expected)
        self.assertGreater(compress_capture(self.directory), 0)
        metadata = json.loads(self.prefix.with_suffix('.json').read_text())
        with gzip.open(self.prefix.with_suffix('.rgba'), 'rb') as frames:
            self.assertEqual(frames.read(), self.raw)
        self.assertTrue(metadata['controller_only'])
        self.assertEqual(verify_frames(self.prefix, metadata), expected)
        self.assertEqual(compress_capture(self.directory), 0)

    def test_changed_bytes_and_truncated_frames_fail_verification(self):
        compress_capture(self.directory)
        metadata = json.loads(self.prefix.with_suffix('.json').read_text())
        altered = bytes([self.raw[0] ^ 1]) + self.raw[1:]
        self.prefix.with_suffix('.rgba').write_bytes(gzip.compress(altered))
        with self.assertRaises(ValueError): verify_frames(self.prefix, metadata)
        self.prefix.with_suffix('.rgba').write_bytes(gzip.compress(self.raw[:-4]))
        with self.assertRaises(ValueError): verify_frames(self.prefix, metadata)


if __name__ == '__main__': unittest.main()
