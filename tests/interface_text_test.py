"""Protect ROM boundaries, neighboring data and correspondence to the linked ELF."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from interface_text import replace_allocations, symbols_from_nm


class NativeLabels(unittest.TestCase):
    def setUp(self):
        self.rom = b'\x11\x22\xbb\xbb\xbb\xff\x33\x44'
        self.records = [{'symbol': 'gText_Label', 'text': 'AB'}]
        self.table = {'A': b'\xbb', 'B': b'\xbc'}
        self.symbols = {'gText_Label': (2, 4)}

    def apply(self, rom=None, records=None, symbols=None):
        return replace_allocations(self.rom if rom is None else rom,
            self.records if records is None else records,
            self.symbols if symbols is None else symbols, self.table, self.rom)

    def test_replacement_preserves_size_and_every_neighboring_byte(self):
        output, _ = self.apply()
        self.assertEqual(output, b'\x11\x22\xbb\xbc\xff\x00\x33\x44')
        self.assertEqual(self.rom, b'\x11\x22\xbb\xbb\xbb\xff\x33\x44')
        self.assertEqual(self.apply(rom=output)[0], output)

    def test_overflow_overlap_missing_and_stale_allocations_are_rejected(self):
        bad = [(None, [{'symbol': 'gText_Label', 'text': 'AAAA'}], None),
            (None, self.records * 2, None),
            (None, None, {}), (None, None, {'gText_Label': (-1, 4)}),
            (None, None, {'gText_Label': (6, 4)}),
            (b'\x11\x22\xbc\xbb\xbb\xff\x33\x44', None, None),
            (b'\x11\x22\xbb\xbb\xbb\x00\x33\x44', None, None)]
        for rom, records, symbols in bad:
            with self.subTest(rom=rom, records=records, symbols=symbols):
                with self.assertRaises(ValueError):
                    self.apply(rom, records, symbols)

    def test_duplicate_requested_symbols_cannot_select_an_arbitrary_address(self):
        with self.assertRaises(ValueError):
            symbols_from_nm('08000002 00000004 R gText_Label\n08000006 00000002 r gText_Label', {'gText_Label'})


if __name__ == '__main__':
    unittest.main()
