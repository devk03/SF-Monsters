"""Guard independent delivery oracles and encrypted object verification."""
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/quality'))
from delivery_fixtures import validate, decode_mon, observe


class DeliveryFixtures(unittest.TestCase):
    def test_catalog_requires_complete_outputs_and_bounded_unique_capacity_controls(self):
        document = json.loads((ROOT / 'data/quality/mechanics/delivery.json').read_text())
        validate(document)
        for key, value in [('party_size', 0), ('party_size', True), ('box', 14),
                           ('filled_boxes', [0, 0]), ('first_slots', 31), ('hole', 420),
                           ('expected', {}), ('derivation', ''), ('partySize', 1)]:
            bad = deepcopy(document); bad['cases'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): validate(bad)
        bad = deepcopy(document); bad['cases'][0]['expected']['party_count'] = True
        with self.assertRaises(ValueError): validate(bad)
        with self.assertRaises(ValueError): validate({'cases': document['cases'] * 2})

    def test_independent_decoder_checks_xor_checksum_moves_ball_and_party_tail(self):
        plain, mon = bytearray(48), bytearray(100)
        struct.pack_into('<H', plain, 0, 19); plain[8] = 3
        struct.pack_into('<H', plain, 12, 33); plain[20] = 56
        struct.pack_into('<H', plain, 38, (4 << 11) | (1 << 15))
        struct.pack_into('<I', mon, 4, 0x11223344)
        struct.pack_into('<H', mon, 28, sum(struct.unpack('<24H', plain)) & 65535)
        mon[32:80] = struct.pack('<12I', *[word ^ 0x11223344 for word in struct.unpack('<12I', plain)])
        struct.pack_into('<I', mon, 80, 64); struct.pack_into('<HH', mon, 86, 45, 90)
        result = decode_mon(mon)
        self.assertEqual((result['species'], result['ball'], result['ot_gender'], result['ot_id']), (19, 4, 1, 0x11223344))
        self.assertEqual((result['moves'], result['pp']), ([33, 0, 0, 0], [56, 0, 0, 0]))
        self.assertEqual((result['hp'], result['max_hp'], result['status']), (45, 90, 64))
        self.assertIsNone(decode_mon(mon[:80], True)['hp'])
        mon[32] ^= 1
        with self.assertRaisesRegex(ValueError, 'checksum'): decode_mon(mon)
        with self.assertRaises(ValueError): decode_mon(mon[:79], True)

    def test_storage_boundary_corruption_fails_before_any_delivery_pass(self):
        with self.assertRaisesRegex(ValueError, 'allocation boundary'):
            observe({}, ['00' * 16, '5a' * 16],
                    [('read', 'pc_left_guard', 16), ('read', 'pc_right_guard', 16)])


if __name__ == '__main__': unittest.main()
