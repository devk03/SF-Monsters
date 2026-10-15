"""Exercise native build inputs and read-only verification, without a full build."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts/romhack'), str(ROOT/'scripts/quality'), str(ROOT/'tests')]
from sunset_compilation import compose, prepare, verify, pinned, native_palette, SYMBOLS, PREFIX, MAP, HEADER
from sunset_density import decorate, BASE
from trainer_portrait_audit_test import linked_pair, literal_lz, MemoryFile
from title_art import tiles8
from title_creature import pack4
from PIL import Image

ENGINE = ROOT/'.tools/pokeemerald-host'


@unittest.skipUnless((ENGINE/'.git').exists(), 'Private pinned engine checkout required; no inherited test payload is published.')
class SunsetCompilation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = ROOT/'.tools/sunset-compilation-tests'; parent.mkdir(parents=True, exist_ok=True)
        cls.directory = Path(tempfile.mkdtemp(prefix='native-', dir=parent))
        cls.engine = cls.directory/'engine'
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(ENGINE), str(cls.engine)], check=True)
        paths = ['data/layouts/layouts.json']
        for name in json.loads((ROOT/'romhack/content/engine-probe.json').read_text())['maps']:
            plan = json.loads((ROOT/'romhack/content'/name).read_text())
            paths.append('data/maps/'+plan['engine_map']+'/map.json')
        for name in paths:
            target = cls.engine/name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ENGINE/name, target)
        cls.old = json.loads((ROOT/BASE/'source-plan.json').read_text())
        cls.dense = decorate(cls.old, ROOT)

    def original(self, name):
        return pinned(self.engine, name).decode()

    def test_legacy_native_inputs_match_the_frozen_actual_v79_resources(self):
        import hashlib
        resources, receipt = compose(ROOT, self.engine, self.old)
        baseline = ROOT/BASE; expected = json.loads((baseline/'receipt.json').read_text())
        self.assertEqual(resources[SYMBOLS[0]], (baseline/'secondary.4bpp').read_bytes())
        for name, field in ((SYMBOLS[1], 'full_palettes_sha256'), (SYMBOLS[2], 'full_metatiles_sha256'),
                            (SYMBOLS[3], 'full_attributes_sha256')):
            self.assertEqual(hashlib.sha256(resources[name]).hexdigest(), expected[field])
        self.assertEqual(resources[SYMBOLS[4]], (baseline/'sunset-map.bin').read_bytes())
        self.assertEqual(receipt['unique_tiles'], 401)

    def test_stale_checkout_and_repeated_prepare_produce_complete_identical_build_inputs(self):
        for plan in (self.old, self.dense):
            expected, _ = compose(ROOT, self.engine, plan)
            for name in (PREFIX+'tiles.png', PREFIX+'metatiles.bin', PREFIX+'metatile_attributes.bin', MAP, HEADER,
                         PREFIX+'sf-palettes.gbapal'):
                target = self.engine/name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(b'stale')
            restored = prepare(ROOT, self.engine, self.original, plan)
            paths = restored+[PREFIX+'sf-palettes.gbapal']
            first = {name:(self.engine/name).read_bytes() for name in paths}
            prepare(ROOT, self.engine, self.original, plan)
            self.assertEqual(first, {name:(self.engine/name).read_bytes() for name in paths})
            self.assertNotIn(PREFIX+'sf-palettes.gbapal', restored)
            self.assertEqual(first[PREFIX+'metatiles.bin'], expected[SYMBOLS[2]])
            self.assertEqual(first[PREFIX+'metatile_attributes.bin'], expected[SYMBOLS[3]])
            self.assertEqual(first[MAP], expected[SYMBOLS[4]])
            self.assertEqual(first[PREFIX+'sf-palettes.gbapal'], expected[SYMBOLS[1]])
            with Image.open(self.engine/PREFIX/'tiles.png') as image:
                actual = pack4(tiles8(image.tobytes(), 128, 256, 16, 32))
                self.assertEqual(actual, expected[SYMBOLS[0]])
            self.assertEqual(first[HEADER].count(b'const u32 gTilesetTiles_Petalburg[]'), 1)
            self.assertIn(b'-num_tiles 512 -Wnum_tiles', first[HEADER])
            self.assertIn(b'INCBIN_U16("'+(PREFIX+'sf-palettes.gbapal').encode()+b'")', first[HEADER])

    def test_invalid_declaration_fails_before_any_native_output_changes(self):
        paths = prepare(ROOT, self.engine, self.original, self.dense)+[PREFIX+'sf-palettes.gbapal']
        before = {name:(self.engine/name).read_bytes() for name in paths}
        with self.assertRaises(ValueError): prepare(ROOT, self.engine, lambda _: 'bad native header', self.dense)
        self.assertEqual(before, {name:(self.engine/name).read_bytes() for name in paths})

    def test_posthook_only_verifies_and_never_repairs_matching_or_corrupt_cartridges(self):
        expected, _ = compose(ROOT, self.engine, self.dense)
        resources = {name:literal_lz(data) if name == SYMBOLS[0] else data for name, data in expected.items()}
        rom, elf = linked_pair(resources); before = (rom.data, elf.data)
        result = verify(ROOT, self.engine, rom, elf=elf, plan=self.dense)
        self.assertTrue(result['normal_compilation_verified']); self.assertFalse(result['post_link_writes'])
        self.assertFalse(result['collision_elevation_preserved']); self.assertEqual(result['new_solid_cells'], 36)
        self.assertEqual(before, (rom.data, elf.data))
        damaged = bytearray(rom.data); damaged[0] ^= 1; broken = MemoryFile(damaged)
        with self.assertRaises(ValueError): verify(ROOT, self.engine, broken, elf=elf, plan=self.dense)
        self.assertEqual(broken.data, damaged); self.assertEqual(elf.data, before[1])
        wrong = resources.copy(); raw = bytearray(wrong[SYMBOLS[2]]); raw[-1] ^= 1; wrong[SYMBOLS[2]] = bytes(raw)
        rom2, elf2 = linked_pair(wrong); before2 = (rom2.data, elf2.data)
        with self.assertRaises(ValueError): verify(ROOT, self.engine, rom2, elf=elf2, plan=self.dense)
        self.assertEqual(before2, (rom2.data, elf2.data))


class PaletteSource(unittest.TestCase):
    def test_invalid_palette_shape_and_channels_are_rejected(self):
        for source in (b'bad', b'JASC-PAL\n0100\n16\n'+b'256 0 0\n'*16,
                       b'JASC-PAL\n0100\n16\n'+b'0 0\n'*16):
            with self.assertRaises(ValueError): native_palette(source)


if __name__ == '__main__': unittest.main()
