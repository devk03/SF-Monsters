"""Native map-format boundaries, authored collision and event safety."""
import sys
import json
from copy import deepcopy
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/romhack'))
from maps import (encode_layout, check_position, event_objects, validate_links,
                  recovery_locations, validate_recovery_scripts)


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
        for rows in [[], [''], ['.', '..'], ['.' * 129], ['.'] * 129, ['.' * 128] * 128]:
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
        self.assertEqual(events[0]['local_id'], 'LOCALID_SF_TEST_1')
        for npcs in [[npc, npc], [{**npc, 'x': 1}], [{**npc, 'id': 0}], [{**npc, 'id': 2}]]:
            with self.subTest(npcs=npcs), self.assertRaises(ValueError):
                event_objects({**self.plan, 'npcs': npcs})

    def test_graph_keeps_travel_in_authored_sf_maps(self):
        town = {'native_id': 'MAP_SF_TOWN', 'warp_events': [
            {'dest_map': 'MAP_SF_ROOM', 'dest_warp_id': '0'}]}
        room = {'native_id': 'MAP_SF_ROOM', 'warp_events': [
            {'dest_map': 'MAP_SF_TOWN', 'dest_warp_id': '0'}]}
        validate_links([town, room])
        for destination, index in [('MAP_HOENN', '0'), ('MAP_SF_ROOM', '1')]:
            bad = {**town, 'warp_events': [{'dest_map': destination, 'dest_warp_id': index}]}
            with self.assertRaises(ValueError): validate_links([bad, room])
        with self.assertRaises(ValueError):
            validate_links([{**town, 'connections': [{'map': 'MAP_HOENN'}]}, room])


class RecoverySafety(unittest.TestCase):
    def setUp(self):
        self.plan = {'native_id': 'MAP_SF_CLINIC_BLOCK',
                     'rows': ['....', '.#..', '....'],
                     'legend': {'.': [1, False, 3], '#': [2, True, 3]},
                     'npcs': [{'x': 1, 'y': 2}],
                     'warp_events': [{'x': 3, 'y': 0}]}
        self.native = {'heal_locations': [
            {'id': 'HEAL_LOCATION_CLINIC', 'map': 'MAP_OLD_TOWN', 'x': 6, 'y': 17},
            {'id': 'HEAL_LOCATION_UNUSED', 'map': 'MAP_UNUSED', 'x': 4, 'y': 9}]}
        self.point = {'id': 'HEAL_LOCATION_CLINIC',
                      'map': 'MAP_SF_CLINIC_BLOCK', 'x': 2, 'y': 2}

    def test_authored_recovery_replaces_only_selected_slot(self):
        before = deepcopy(self.native)
        output = recovery_locations([self.point], [self.plan], self.native)
        self.assertEqual(output['heal_locations'][0], {
            'id': 'HEAL_LOCATION_CLINIC', 'map': 'MAP_SF_CLINIC_BLOCK', 'x': 2, 'y': 2})
        self.assertEqual(output['heal_locations'][1], before['heal_locations'][1])
        self.assertEqual(self.native, before)

    def test_recovery_rejects_foreign_map_or_missing_native_slot(self):
        for change in [{'map': 'MAP_HOENN'}, {'id': 'HEAL_LOCATION_ABSENT'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                recovery_locations([{**self.point, **change}], [self.plan], self.native)
        with self.assertRaises(ValueError):
            recovery_locations([self.point, self.point], [self.plan], self.native)

    def test_recovery_rejects_blocked_occupied_warp_and_outside_tiles(self):
        for x, y in [(1, 1), (1, 2), (3, 0), (-1, 0), (4, 0), (0, 3)]:
            with self.subTest(position=(x, y)), self.assertRaises(ValueError):
                recovery_locations([{**self.point, 'x': x, 'y': y}],
                                   [self.plan], self.native)
        for value in [True, '2', 2.5, None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                recovery_locations([{**self.point, 'x': value}], [self.plan], self.native)

    def test_script_cannot_register_an_inherited_unauthored_destination(self):
        validate_recovery_scripts('Clinic::\n\tsetrespawn HEAL_LOCATION_CLINIC\n',
                                  [self.point])
        for symbol in ['HEAL_LOCATION_UNUSED', 'HEAL_LOCATION_FOREIGN', '0']:
            with self.subTest(symbol=symbol), self.assertRaises(ValueError):
                validate_recovery_scripts('Clinic::\n\tsetrespawn ' + symbol + '\n',
                                          [self.point])
        # A mention in dialogue is not an executable registration.
        validate_recovery_scripts('.string "setrespawn HEAL_LOCATION_FOREIGN$"', [])

    def test_actual_south_park_clinic_recovers_outside_its_entrance(self):
        root = Path(__file__).resolve().parents[1] / 'romhack/content'
        content = json.loads((root / 'engine-probe.json').read_text())
        sunset = json.loads((root / 'sunset.json').read_text())
        park = json.loads((root / 'south-park.json').read_text())
        plans = [{**sunset, 'native_id': 'MAP_LITTLEROOT_TOWN'},
                 {**park, 'native_id': 'MAP_OLDALE_TOWN'}]
        native = {'heal_locations': [
            {'id': 'HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F',
             'map': 'MAP_STOCK_HOUSE', 'x': 7, 'y': 4},
            {'id': 'HEAL_LOCATION_LITTLEROOT_TOWN_MAYS_HOUSE_2F',
             'map': 'MAP_STOCK_HOUSE', 'x': 7, 'y': 4},
            {'id': 'HEAL_LOCATION_OLDALE_TOWN', 'map': 'MAP_OLDALE_TOWN', 'x': 6, 'y': 17}]}
        output = recovery_locations(content['recovery_points'], plans, native)
        self.assertEqual(output['heal_locations'][2], {
            'id': 'HEAL_LOCATION_OLDALE_TOWN', 'map': 'MAP_OLDALE_TOWN', 'x': 32, 'y': 6})
        for record in output['heal_locations'][:2]:
            self.assertEqual((record['map'], record['x'], record['y']),
                             ('MAP_LITTLEROOT_TOWN', 23, 22))
        validate_recovery_scripts((root / 'services.inc').read_text(),
                                  content['recovery_points'])


if __name__ == '__main__':
    unittest.main()
