"""Protect the optional room's original-art geometry, return route and read-only notes."""
from copy import deepcopy
import json
from pathlib import Path
import re
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from maps import encode_layout, validate_links

PLAN = json.loads((ROOT / 'romhack/content/seed-room.json').read_text())
SOURCE = (ROOT / 'romhack/content/seed-room.inc').read_text()


def read_program():
    labels, code, texts = {}, [], {}
    label = None
    allowed = {'lockall', 'releaseall', 'end', 'goto', 'goto_if_set',
               'goto_if_unset', 'goto_if_ge', 'msgbox'}
    for raw in SOURCE.splitlines():
        line = raw.split('@', 1)[0].strip()
        if not line or line == '.byte 0':
            continue
        if line.endswith('::'):
            label = line[:-2]
            if label in labels:
                raise ValueError('Duplicate room script label')
            labels[label] = len(code)
            continue
        match = re.fullmatch(r'\.string "(.*)"', line)
        if match:
            texts[label] = match[1]
            continue
        command, _, arguments = line.partition(' ')
        if command not in allowed:
            raise ValueError('Room must not write state or introduce other script effects: ' + command)
        args = [value.strip() for value in arguments.split(',')] if arguments else []
        if command in ('goto_if_set', 'goto_if_unset') and args[0] not in {
                'FLAG_BADGE01_GET', 'FLAG_SYS_POKEMON_GET', 'FLAG_UNUSED_0x041'}:
            raise ValueError('Room introduced another flag dependency')
        if command == 'goto_if_ge' and args[0] not in {'VAR_GIFT_UNUSED_3', 'VAR_UNUSED_0x40F7'}:
            raise ValueError('Room introduced another quest variable')
        code.append((command, args))
    return labels, code, texts


def inspect(entry, flags=(), variables=None):
    """Execute only the native read/branch/message subset; no game or ROM fixture."""
    labels, code, texts = read_program()
    variables = variables or {}
    pc, locked, shown = labels[entry], False, []
    for _ in range(64):
        command, args = code[pc]; pc += 1
        if command == 'lockall':
            if locked:
                raise ValueError('Nested room lock')
            locked = True
        elif command == 'releaseall':
            if not locked:
                raise ValueError('Release without room lock')
            locked = False
        elif command == 'goto':
            pc = labels[args[0]]
        elif command == 'goto_if_set' and args[0] in flags:
            pc = labels[args[1]]
        elif command == 'goto_if_unset' and args[0] not in flags:
            pc = labels[args[1]]
        elif command == 'goto_if_ge' and variables.get(args[0], 0) >= int(args[1]):
            pc = labels[args[2]]
        elif command == 'msgbox':
            if not locked or args[1] != 'MSGBOX_DEFAULT':
                raise ValueError('Room notes need one ordinary locked message')
            shown.append(args[0]); texts[args[0]]
        elif command == 'end':
            if locked or len(shown) != 1:
                raise ValueError('Room note did not release exactly one message')
            return shown[0]
    raise ValueError('Room script did not terminate')


class SeedRoomTest(unittest.TestCase):
    def test_compact_room_has_one_clear_exit_and_connected_floor(self):
        width, height, raw = encode_layout(PLAN)
        self.assertEqual((width, height, len(raw)), (8, 8, 128))
        walkable = {(x, y) for y, row in enumerate(PLAN['rows']) for x, token in enumerate(row)
                    if not PLAN['legend'][token][1]}
        reached, pending = set(), [(3, 6)]
        while pending:
            point = pending.pop()
            if point in reached or point not in walkable:
                continue
            reached.add(point)
            x, y = point
            pending.extend([(x-1, y), (x+1, y), (x, y-1), (x, y+1)])
        self.assertEqual(reached, walkable)
        boundary = {(x, y) for x, y in walkable if x in (0, 7) or y in (0, 7)}
        self.assertEqual(boundary, {(3, 7)})
        self.assertFalse(PLAN['npcs'])
        for event in PLAN['bg_events']:
            x, y = event['x'], event['y']
            self.assertTrue(any(point in reached for point in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]))

    def test_art_is_explicit_original_apartment_cells_with_matching_collision(self):
        self.assertNotIn('tile_grid_base', PLAN)
        self.assertEqual(PLAN['tilesets']['secondary'], 'gTileset_CourierHome')
        original = json.loads((ROOT / 'romhack/content/apartment.json').read_text())
        records = (ROOT / 'assets/tiles/courier-apartment/metatiles.bin').read_bytes()
        attributes = (ROOT / 'assets/tiles/courier-apartment/attributes.bin').read_bytes()
        for y, row in enumerate(PLAN['rows']):
            for x, token in enumerate(row):
                tile, blocked, elevation = PLAN['legend'][token]
                index = tile - 512
                self.assertTrue(0 <= index < 110)
                sx, sy = index % 11, index // 11
                old_token = original['rows'][sy][sx]
                self.assertEqual((blocked, elevation), tuple(original['legend'][old_token][1:]))
                # The inherited bedroom and the rug edge must not leak into this layout.
                self.assertFalse(2 <= sx <= 4 and 2 <= sy <= 4)
                self.assertFalse(4 <= sx <= 7 and 5 <= sy <= 7)
                for word in struct.unpack_from('<8H', records, index * 16):
                    self.assertEqual(word >> 12, 6)
                    self.assertTrue(512 <= word & 1023 < 956)
                behavior = struct.unpack_from('<H', attributes, index * 2)[0] & 255
                self.assertEqual(behavior, 0x65 if (x, y) == (3, 7) else 0)
        self.assertEqual(PLAN['border_tile'], original['border_tile'])
        # Keep the full two-row window/curtains and the three-row cabinet together.
        for x in range(1, 7):
            top = PLAN['legend'][PLAN['rows'][0][x]][0]
            self.assertEqual(PLAN['legend'][PLAN['rows'][1][x]][0], top + 11)
        for x in (1, 2):
            top = PLAN['legend'][PLAN['rows'][3][x]][0]
            self.assertEqual(PLAN['legend'][PLAN['rows'][4][x]][0], top + 11)
            self.assertEqual(PLAN['legend'][PLAN['rows'][5][x]][0], top + 22)

    def test_return_link_uses_the_new_exterior_slot_not_gym_or_clinic(self):
        seed = dict(PLAN, native_id='MAP_OLDALE_TOWN_HOUSE1')
        self.assertEqual(seed['warp_events'], [{'x':3,'y':7,'elevation':0,
                                               'dest_map':'MAP_OLDALE_TOWN','dest_warp_id':'2'}])
        # Root appends exterior slot 2; no assumption about animated-door registration.
        park = {'native_id':'MAP_OLDALE_TOWN', 'warp_events':[
            {'dest_map':'MAP_RUSTBORO_CITY_GYM','dest_warp_id':'0'},
            {'dest_map':'MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB','dest_warp_id':'0'},
            {'dest_map':'MAP_OLDALE_TOWN_HOUSE1','dest_warp_id':'0'}]}
        gym = {'native_id':'MAP_RUSTBORO_CITY_GYM', 'warp_events':[
            {'dest_map':'MAP_OLDALE_TOWN','dest_warp_id':'0'}]}
        clinic = {'native_id':'MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB', 'warp_events':[
            {'dest_map':'MAP_OLDALE_TOWN','dest_warp_id':'1'}]}
        validate_links([park, seed, gym, clinic])
        bad = deepcopy(seed); bad['warp_events'][0]['dest_warp_id'] = '3'
        with self.assertRaises(ValueError):
            validate_links([park, bad, gym, clinic])

    def test_uses_existing_original_music_and_soma_parent(self):
        meta = PLAN['metadata']
        score = json.loads((ROOT / 'assets/audio/ocean-commute.json').read_text())
        self.assertEqual(score['native_song'], 'mus_littleroot')
        self.assertEqual(meta['music'], 'MUS_LITTLEROOT')
        self.assertEqual(meta['region_map_section'], 'MAPSEC_OLDALE_TOWN')
        self.assertEqual(meta['map_type'], 'MAP_TYPE_INDOOR')
        self.assertEqual(meta['weather'], 'WEATHER_NONE')
        self.assertFalse(meta['allow_running'] or meta['allow_cycling'])

    def test_field_notes_track_existing_discoveries_without_changing_them(self):
        for badge, beacon, parcel, expected in [
                (False,0,1,'FieldNotes'), (False,1,4,'RecoveredNotes'),
                (False,0,3,'RecoveredNotes'), (False,2,4,'BeaconNotes'),
                (False,3,4,'BeaconNotes'), (True,0,4,'BadgeNotes'),
                (True,1,4,'BadgeNotes'), (True,2,4,'BadgeBeaconNotes'),
                (True,3,4,'BadgeBeaconNotes')]:
            flags = {'FLAG_BADGE01_GET'} if badge else set()
            variables = {'VAR_GIFT_UNUSED_3':beacon,'VAR_UNUSED_0x40F7':parcel}
            before = (set(flags), dict(variables))
            with self.subTest(badge=badge,beacon=beacon,parcel=parcel):
                self.assertEqual(inspect('SF_SeedFieldNotes', flags, variables), 'SF_SeedText'+expected)
                self.assertEqual((flags,variables), before)

    def test_care_notes_have_companion_and_existing_bench_precedence(self):
        for starter, bench, expected in [(False,False,'BeforeCompanion'),(False,True,'BeforeCompanion'),
                                         (True,False,'CareNotes'),(True,True,'AfterBench')]:
            flags = ({'FLAG_SYS_POKEMON_GET'} if starter else set()) | ({'FLAG_UNUSED_0x041'} if bench else set())
            with self.subTest(starter=starter,bench=bench):
                self.assertEqual(inspect('SF_SeedCareNotes', flags), 'SF_SeedText'+expected)

    def test_notes_are_finite_native_pages_with_no_state_writing_commands(self):
        labels, _, texts = read_program()  # Rejects writes/rewards/extra command types globally.
        for event in PLAN['bg_events']:
            self.assertIn(event['script'], labels)
        self.assertEqual(len(texts), 8)
        for text in texts.values():
            self.assertEqual(text.count('$'), 1)
            self.assertTrue(text.endswith('$'))
            for page in text[:-1].split('\\p'):
                lines = page.split('\\n')
                self.assertLessEqual(len(lines), 2)
                self.assertTrue(all(len(line) <= 36 for line in lines))


if __name__ == '__main__':
    unittest.main()
