"""Native map-format boundaries, authored collision and event safety."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from maps import encode_layout, check_position, event_objects


class MapEncoding(unittest.TestCase):
    def setUp(self):
        self.plan = {'rows': ['.#', '~.'], 'legend': {
            '.': [1, False, 3], '#': [1023, True, 15], '~': [0x170, True, 1]
        }}

    def test_native_bytes(self):
        width, height, data = encode_layout(self.plan)
        self.assertEqual((width, height), (2, 2))
        self.assertEqual(data, bytes.fromhex('01 30 ff ff 70 1d 01 30'))

    def test_layout_boundaries(self):
        for rows in [[], [''], ['.', '..'], ['.' * 129], ['.'] * 129]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                encode_layout({**self.plan, 'rows': rows})
        for tile in [[1024, False, 3], [1, 1, 3], [1, False, 16]]:
            with self.subTest(tile=tile), self.assertRaises(ValueError):
                encode_layout({**self.plan, 'legend': {**self.plan['legend'], '.': tile}})

    def test_usable_event_locations(self):
        check_position(self.plan, 0, 0)
        check_position(self.plan, 1, 0, walkable=False)
        for position in [(1, 0), (0, 1), (-1, 0), (2, 0)]:
            with self.subTest(position=position), self.assertRaises(ValueError):
                check_position(self.plan, *position)

    def test_event_identity_and_elevation(self):
        npc = {'id': 1, 'x': 0, 'y': 0, 'graphics': 'GFX', 'script': 'HELLO'}
        events = event_objects({**self.plan, 'npcs': [npc]})
        self.assertEqual(events[0]['elevation'], 3)
        self.assertEqual(events[0]['local_id'], '1')
        for npcs in [[npc, npc], [{**npc, 'x': 1}], [{**npc, 'id': 0}]]:
            with self.subTest(npcs=npcs), self.assertRaises(ValueError):
                event_objects({**self.plan, 'npcs': npcs})


if __name__ == '__main__':
    unittest.main()
