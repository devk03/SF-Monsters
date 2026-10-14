"""Independent native format vectors and stale compiled-resource rejection."""
from pathlib import Path
import struct
import sys
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/quality'))
from check_creature_resources import Cartridge, decode_lz, pack_image, palette_bytes


class MemoryFile:
    def __init__(self, data):
        self.data = data

    def read_bytes(self):
        return self.data

    def read_text(self):
        return self.data.decode()


def cartridge(rom=b'ABCD', linked=b'ABCD', edit=None):
    # Independently encoded ELF32 section/symbol/string tables; no toolchain fixture.
    elf = bytearray(260)
    elf[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<H', elf, 18, 40)
    struct.pack_into('<I', elf, 32, 52)
    struct.pack_into('<HH', elf, 46, 40, 4)
    struct.pack_into('<10I', elf, 92, 0, 1, 2, 0x08000000, 212, 4, 0, 0, 1, 0)
    struct.pack_into('<10I', elf, 132, 0, 3, 0, 0, 216, 10, 0, 0, 1, 0)
    struct.pack_into('<10I', elf, 172, 0, 2, 0, 0, 228, 32, 2, 1, 4, 16)
    elf[212:216] = linked
    elf[216:226] = b'\x00gMonTest\x00'
    struct.pack_into('<IIIBBH', elf, 244, 1, 0x08000000, 4, 0x11, 0, 1)
    if edit:
        edit(elf)
    return Cartridge(MemoryFile(rom), MemoryFile(bytes(elf)))


class CreatureResourcesTest(unittest.TestCase):
    def test_lz_literals_and_overlapping_copy(self):
        self.assertEqual(decode_lz(bytes.fromhex('10090000104142433002')), b'ABCABCABC')

    def test_lz_rejects_truncation_invalid_distance_and_output_overrun(self):
        for data in ('1001000000', '10030000800000', '1002000040410000', '10018000'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_lz(bytes.fromhex(data))

    def test_tile_order_and_low_nibble_first(self):
        image = Image.new('P', (16, 8))
        image.putdata(list(range(16)) * 8)
        self.assertEqual(pack_image(image), bytes.fromhex('10325476') * 8 + bytes.fromhex('98badcfe') * 8)

    def test_rejects_unencodable_indices_and_canvas(self):
        for image in (Image.new('RGB', (8, 8)), Image.new('P', (7, 8)), Image.new('P', (8, 8), 16)):
            with self.subTest(mode=image.mode, size=image.size), self.assertRaises(ValueError):
                pack_image(image)

    def test_rgb555_primary_colors_and_palette_bounds(self):
        colors = ['248 0 0', '0 248 0', '0 0 248'] + ['0 0 0'] * 13
        palette = ('JASC-PAL\n0100\n16\n' + '\n'.join(colors)).encode()
        self.assertEqual(palette_bytes(MemoryFile(palette)), bytes.fromhex('1f00e003007c') + bytes(26))
        for invalid in (palette.replace(b'248', b'256', 1), palette.replace(b'16\n', b'15\n', 1)):
            with self.assertRaises(ValueError):
                palette_bytes(MemoryFile(invalid))

    def test_matching_pair_reads_exact_resource(self):
        self.assertEqual(cartridge().data('gMonTest'), b'ABCD')

    def test_stale_compiled_rom_cannot_borrow_new_elf_symbols(self):
        with self.assertRaisesRegex(ValueError, 'ROM/ELF resource bytes differ'):
            cartridge(rom=b'OLD!', linked=b'NEW!').data('gMonTest')

    def test_resource_must_fit_symbol_and_cartridge(self):
        cart = cartridge()
        for length in (0, 5):
            with self.subTest(length=length), self.assertRaises(ValueError):
                cart.data('gMonTest', length)
        with self.assertRaisesRegex(ValueError, 'Missing resource'):
            cart.data('gMonMissing')
        cart.symbols['gMonTest'] = (0x07ffffff, 4)
        with self.assertRaisesRegex(ValueError, 'bounds'):
            cart.data('gMonTest')

    def test_bad_elf_identity_is_rejected(self):
        for data in (b'', b'\x7fELF' + bytes(128)):
            with self.assertRaises(ValueError):
                Cartridge(MemoryFile(b'ABCD'), MemoryFile(data))

    def test_symbol_table_bounds_and_names_are_validated(self):
        for offset, value in ((196, 99), (152, 999), (208, 8), (244, 99)):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                cartridge(edit=lambda elf: struct.pack_into('<I', elf, offset, value))

    def test_zero_size_defined_symbol_requires_explicit_read_length(self):
        cart = cartridge(edit=lambda elf: struct.pack_into('<I', elf, 252, 0))
        self.assertEqual(cart.data('gMonTest', 4), b'ABCD')
        with self.assertRaisesRegex(ValueError, 'bounds'):
            cart.data('gMonTest')

    def test_undefined_symbol_is_not_a_definition_and_duplicates_fail(self):
        with self.assertRaisesRegex(ValueError, 'no defined'):
            cartridge(edit=lambda elf: struct.pack_into('<H', elf, 258, 0))

        def duplicate(elf):
            elf.extend(elf[244:260])
            struct.pack_into('<I', elf, 192, 48)

        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            cartridge(edit=duplicate)


if __name__ == '__main__':
    unittest.main()
