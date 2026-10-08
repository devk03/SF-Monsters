"""Native map-format boundaries, authored collision and event safety."""
import sys
import json
from copy import deepcopy
from collections import deque
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

    def test_backdrop_grid_preserves_collision_and_elevation_with_unique_native_tiles(self):
        plan = {**self.plan, 'tile_grid_base': 512}
        self.assertEqual(encode_layout(plan)[2], bytes.fromhex('00 32 01 fe 02 1e 03 32'))
        for base in (511, 1021, True, '512'):
            with self.subTest(base=base), self.assertRaises(ValueError):
                encode_layout({**self.plan, 'tile_grid_base': base})

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


class InteriorRoutes(unittest.TestCase):
    def reachable(self, plan, start, gate_open=False):
        occupied = {(n['x'], n['y']) for n in plan['npcs']}
        queue, visited = deque([start]), {start}
        while queue:
            x, y = queue.popleft()
            for xx, yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if not (0 <= yy < len(plan['rows']) and 0 <= xx < len(plan['rows'][0])):
                    continue
                token = plan['rows'][yy][xx]
                blocked = plan['legend'][token][1] and not (gate_open and token == 'Q')
                if blocked or (xx,yy) in occupied or (xx,yy) in visited:
                    continue
                visited.add((xx,yy)); queue.append((xx,yy))
        return visited

    def test_apartment_has_a_return_warp_and_reachable_story_interactions(self):
        root = Path(__file__).resolve().parents[1] / 'romhack/content'
        home = json.loads((root / 'apartment.json').read_text())
        street = json.loads((root / 'sunset.json').read_text())
        plans = [{**home, 'native_id': 'MAP_LITTLEROOT_TOWN_BRENDANS_HOUSE_1F'},
                 {**street, 'native_id': 'MAP_LITTLEROOT_TOWN'}]
        validate_links(plans)
        encode_layout(home); event_objects(home)
        entry = home['warp_events'][0]
        accessible = self.reachable(home, (entry['x'], entry['y']))
        for event in home['bg_events']:
            x, y = event['x'], event['y']
            positions = ({(x, y + 1)} if event['player_facing_dir'].endswith('NORTH')
                         else {(x-1,y), (x+1,y), (x,y-1), (x,y+1)})
            self.assertTrue(positions & accessible, event['script'])
        self.assertEqual(len(street['warp_events']), 1)
        exterior = street['warp_events'][0]
        check_position(street, exterior['x'], exterior['y'])
        self.assertIn((exterior['x'], exterior['y'] + 1),
                      self.reachable(street, (18, 22)))
        self.assertEqual(exterior['dest_map'], plans[0]['native_id'])
        self.assertEqual(entry['dest_map'], plans[1]['native_id'])

    def test_gym_keeps_relay_practice_and_earned_gate_routes(self):
        root = Path(__file__).resolve().parents[1] / 'romhack/content'
        plan = json.loads((root / 'cognition.json').read_text())
        encode_layout(plan); event_objects(plan)
        closed = self.reachable(plan, (8,21))
        for target in [(8,17),(4,13),(12,13),(3,13),(13,13),(1,16),(5,20)]:
            self.assertIn(target, closed)
        self.assertNotIn((8,4), closed)
        opened = self.reachable(plan, (8,21), gate_open=True)
        for target in [(8,4),(1,7)]: self.assertIn(target, opened)

    def test_clinic_keeps_healing_shop_storage_notes_and_exit_accessible(self):
        root = Path(__file__).resolve().parents[1] / 'romhack/content'
        plan = json.loads((root / 'services.json').read_text())
        encode_layout(plan); event_objects(plan)
        reachable = self.reachable(plan, (6,12))
        for target in [(6,5),(9,8),(2,4),(10,3)]:
            self.assertIn(target, reachable)


if __name__ == '__main__':
    unittest.main()
