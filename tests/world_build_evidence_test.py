"""Build receipts preserve immutable ROMs and each matching debug ELF."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from build_world import freeze_artifacts


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        # Preserve even synthetic fixtures under the repository's no-removal
        # rule; each test gets a fresh, tiny directory in the system temp area.
        self.root = Path(tempfile.mkdtemp(prefix='sf-world-evidence-'))
        self.rom, self.elf = self.root/'input.gba', self.root/'input.elf'
        self.rom.write_bytes(b'cartridge-A')
        self.elf.write_bytes(b'ELF from checkout A')
        self.output = self.root/'frozen'
        self.output.mkdir()

    def receipt(self, name):
        path = self.output/'receipts'/name
        path.mkdir(parents=True)
        return path

    def test_checkout_debug_variant_is_stored_without_replacing_first_pair(self):
        first = freeze_artifacts(self.rom, self.elf, self.output, self.receipt('one'))
        original = (self.output/'target.elf').read_bytes()
        self.elf.write_bytes(b'ELF from checkout B')
        second = freeze_artifacts(self.rom, self.elf, self.output, self.receipt('two'))
        self.assertEqual(first['path'], 'target.elf')
        self.assertEqual(second['path'], 'receipts/two/target.elf')
        self.assertEqual((self.output/'target.elf').read_bytes(), original)
        self.assertEqual((self.output/second['path']).read_bytes(), self.elf.read_bytes())
        self.assertEqual(second['sha256'], hashlib.sha256(self.elf.read_bytes()).hexdigest())
        self.assertEqual(second['canonical_sha256'], first['sha256'])

    def test_identical_pair_reuses_canonical_elf(self):
        freeze_artifacts(self.rom, self.elf, self.output, self.receipt('one'))
        run = self.receipt('two')
        result = freeze_artifacts(self.rom, self.elf, self.output, run)
        self.assertEqual(result['path'], 'target.elf')
        self.assertFalse((run/'target.elf').exists())

    def test_changed_cartridge_still_refuses_and_preserves_prior_evidence(self):
        freeze_artifacts(self.rom, self.elf, self.output, self.receipt('one'))
        self.rom.write_bytes(b'cartridge-B')
        self.elf.write_bytes(b'different ELF')
        with self.assertRaisesRegex(ValueError, 'cartridge differs'):
            freeze_artifacts(self.rom, self.elf, self.output, self.receipt('two'))
        self.assertEqual((self.output/'target.gba').read_bytes(), b'cartridge-A')
        self.assertEqual((self.output/'target.elf').read_bytes(), b'ELF from checkout A')

    def test_a_receipt_cannot_replace_its_already_frozen_variant(self):
        freeze_artifacts(self.rom, self.elf, self.output, self.receipt('one'))
        run = self.receipt('two')
        self.elf.write_bytes(b'ELF B')
        freeze_artifacts(self.rom, self.elf, self.output, run)
        self.elf.write_bytes(b'ELF C')
        with self.assertRaisesRegex(ValueError, 'receipt ELF differs'):
            freeze_artifacts(self.rom, self.elf, self.output, run)
        self.assertEqual((run/'target.elf').read_bytes(), b'ELF B')
