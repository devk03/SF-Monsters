"""Independent observable world contracts; fixtures never call the generator."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
SPEC = importlib.util.spec_from_file_location('world_contract', ROOT/'scripts/romhack/world_contract.py')
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)


def fixture(league=True):
    """A hand-designed broad-plaza world, unlike the producer's corridor shapes."""
    names = ['dogpatch', 'north_beach', 'treasure_island', 'sutro_tower', 'lands_end']
    areas = [dict(id=name, engine_map='Area_'+name, city='San Francisco') for name in names]
    routes = [
        dict(id='road_one', engine_map='RoadOne', **{'from': 'dogpatch', 'from_port': 'right',
             'to': 'north_beach', 'to_port': 'left'}, mode='walk', requires_badge=0, bidirectional=True),
        dict(id='road_two', engine_map='RoadTwo', **{'from': 'dogpatch', 'from_port': 'up',
             'to': 'sutro_tower', 'to_port': 'down'}, mode='walk', requires_badge=0, bidirectional=True),
        dict(id='channel_one', engine_map='ChannelOne', **{'from': 'north_beach', 'from_port': 'right',
             'to': 'treasure_island', 'to_port': 'left'}, mode='surf', requires_badge=5, bidirectional=True),
        dict(id='channel_two', engine_map='ChannelTwo', **{'from': 'sutro_tower', 'from_port': 'left',
             'to': 'lands_end', 'to_port': 'right'}, mode='surf', requires_badge=5, bidirectional=True)]
    gyms = [dict(id='gym_'+str(n), badge=n, area='dogpatch', engine_map='Gym'+str(n)) for n in range(1, 9)]
    manifest = dict(schema_version=1, profile='world-blockout',
                    geometry=dict(width=32, height=24, walk_lane_width=3),
                    native=dict(primary_tileset='gTileset_General', secondary_tileset='gTileset_Petalburg',
                                save_magic=0x5742, save_schema=1, game_code='BPEE'),
                    start=dict(area='dogpatch', x=16, y=16), areas=areas, routes=routes, gyms=gyms,
                    stage_markers=dict(tower_after='treasure_island',
                                       crisis_after=['treasure_island', 'sutro_tower'], gym_8_requires='crisis_marker'),
                    story_waypoints=['dogpatch', 'north_beach', 'treasure_island', 'sutro_tower', 'lands_end'],
                    league=dict(venue='angel_island' if league else None, engine_map='LeagueIsland',
                                route_engine_map='LeagueChannel', from_area='north_beach', from_port='up',
                                requires_badges=[5, 8], city='Tiburon / Marin County',
                                scope_exception='Explicit user-approved Angel Island exception'))
    records = [(area['id'], area['engine_map']) for area in areas]
    records += [(route['id'], route['engine_map']) for route in routes]
    records += [(gym['id'], gym['engine_map']) for gym in gyms]
    if league:
        records += [('angel_island', 'LeagueIsland'), ('league_route', 'LeagueChannel')]
    plans = {}
    for name, engine in records:
        grid = [['#' if x in (0, 31) or y in (0, 23) else '.' for x in range(32)] for y in range(24)]
        plans[name] = dict(world_id=name, engine_map=engine, native_id='MAP_'+name.upper(),
                           rows=[''.join(row) for row in grid],
                           legend={'.': [1, False, 3], '#': [11, True, 3],
                                   'W': [368, False, 1], 'V': [179, False, 1]},
                           tilesets={'primary': 'gTileset_General', 'secondary': 'gTileset_Petalburg'},
                           connections=[], npcs=[], coord_events=[], bg_events=[], access_points=[],
                           script=name+'.inc')
    # Explicit independent edge table; no producer port or inverse-direction helper.
    edges = [('dogpatch', 'right', 'road_one', 'left'), ('road_one', 'right', 'north_beach', 'left'),
             ('dogpatch', 'up', 'road_two', 'down'), ('road_two', 'up', 'sutro_tower', 'down'),
             ('north_beach', 'right', 'channel_one', 'left'), ('channel_one', 'right', 'treasure_island', 'left'),
             ('sutro_tower', 'left', 'channel_two', 'right'), ('channel_two', 'left', 'lands_end', 'right')]
    if league:
        edges += [('north_beach', 'up', 'league_route', 'down'), ('league_route', 'up', 'angel_island', 'down')]
    for source, side, target, return_side in edges:
        for owner, direction, other in [(source, side, target), (target, return_side, source)]:
            board = plans[owner]
            board['connections'].append(dict(map=plans[other]['native_id'], direction=direction, offset=0))
            for d in (-1, 0, 1):
                x, y = {'left': (0, 12+d), 'right': (31, 12+d),
                        'up': (16+d, 0), 'down': (16+d, 23)}[direction]
                tile(board, x, y, '.')
    # Every route has an actual wet cut, not just a gate label or water decoration.
    for name in ['channel_one', 'channel_two']:
        for y in range(1, 23):
            for x in (15, 16, 17): tile(plans[name], x, y, 'W')
    if league:
        for y in (11, 12, 13):
            for x in range(1, 31): tile(plans['league_route'], x, y, 'V' if y == 12 else 'W')
    for name in names + (['angel_island'] if league else []):
        plans[name]['npcs'] = [dict(id=1, x=25, y=16)]
        plans[name]['access_points'].append(dict(kind='checkpoint', x=25, y=17, activation='interact'))
    plans['dogpatch']['access_points'].append(dict(kind='spawn', x=16, y=16, activation='walk'))
    for n in range(1, 9):
        gym = plans['gym_'+str(n)]
        gym['npcs'] = [dict(id=1, x=12, y=9)]
        gym['access_points'] = [dict(kind='checkpoint', x=12, y=10, activation='interact'),
                                dict(kind='arrival', x=16, y=16, activation='walk', target_id='dogpatch'),
                                dict(kind='gym_exit', x=16, y=20, activation='walk', target_id='dogpatch')]
        gym['coord_events'] = [dict(x=16, y=20, elevation=3)]
        x = 2+n*2
        plans['dogpatch']['access_points'] += [dict(kind='gym_entry', x=x, y=7, activation='walk', target_id=gym['world_id']),
                                              dict(kind='arrival', x=x, y=9, activation='walk', target_id=gym['world_id'])]
        plans['dogpatch']['coord_events'].append(dict(x=x, y=7, elevation=3))
    return manifest, plans


def tile(plan, x, y, token):
    rows = plan['rows']
    rows[y] = rows[y][:x]+token+rows[y][x+1:]


def run(manifest, plans, **kwargs):
    return contract.audit(manifest, list(plans.values()), **kwargs)


class WorldContractTests(unittest.TestCase):
    def test_landmark_pixels_and_viewing_approach_survive_furnishing(self):
        m,p=fixture();m['town_finishing']={'revision':2};m['native']['save_magic']=0x5743
        board=p['dogpatch'];board['tile_profile']='nature'
        board['tilesets']['secondary']='gTileset_SFNature'
        # Explicit authored windmill allocation; no map producer is called.
        for dy in range(4):
            for dx in range(3):
                token=chr(0x100+dy*3+dx);board['legend'][token]=[574+dy*3+dx,True,3]
                tile(board,3+dx,2+dy,token)
        board['town_blocks']=[dict(style='windmill',x=3,y=2,width=3,height=4,first_metatile=574)]
        board['scenic_viewpoints']=[dict(name='windmill',x=4,y=6)]
        self.assertTrue(run(m,p)['passed'])
        before=deepcopy(board)
        board['legend']['g']=[531,True,3];tile(board,4,4,'g')
        self.reject(m,p,'frontage') # Collision stays solid; the landmark is chopped.
        p['dogpatch']=before;tile(before,4,6,'#')
        self.reject(m,p,'landmark')

    def reject(self, manifest, plans, code=None):
        result = run(manifest, plans)
        self.assertFalse(result['passed'], result)
        self.assertTrue(result['errors'])
        if code is not None: self.assertEqual(result['errors'][0]['code'], code, result)
        return result

    def test_resolved_league_requires_surf_then_waterfall_without_overclaim(self):
        m, p = fixture(); result = run(m, p)
        self.assertTrue(result['passed'], result)
        self.assertFalse(result['incomplete_scope'])
        self.assertFalse(result['full_completion'])
        self.assertFalse(result['native_gate_scripts_verified'])
        self.assertNotIn('treasure_island', result['stages'][4]['areas'])
        self.assertIn('treasure_island', result['stages'][5]['areas'])
        self.assertIn('lands_end', result['stages'][5]['areas'])
        self.assertNotIn('angel_island', result['stages'][7]['areas'])
        self.assertIn('angel_island', result['stages'][8]['areas'])

    def test_pending_venue_can_pass_only_an_explicit_incomplete_core_audit(self):
        m, p = fixture(league=False)
        result = self.reject(m, p, 'league_pending')
        self.assertTrue(result['league_venue_pending'])
        result = run(m, p, core_only=True)
        self.assertTrue(result['passed'], result)
        self.assertTrue(result['incomplete_scope']); self.assertFalse(result['full_completion'])
        m, p = fixture()
        self.assertTrue(run(m, p, core_only=True)['incomplete_scope'])

    def test_missing_return_mismatched_direction_offset_and_dangling_map(self):
        mutations = [lambda p: p['road_one']['connections'].pop(),
                     lambda p: p['road_one']['connections'][0].update(direction='up'),
                     lambda p: p['road_one']['connections'][0].update(offset=1),
                     lambda p: p['road_one']['connections'][0].update(map='MAP_MISSING')]
        for mutate in mutations:
            m, p = fixture(); mutate(p)
            with self.subTest(mutation=mutations.index(mutate)): self.reject(m, p)
        m, p = fixture()
        for board in p.values(): board['connections'].reverse()
        self.assertTrue(run(m, p)['passed'], 'Connection list order is not a native contract')

    def test_manifest_and_native_slots_ids_and_gyms_must_be_unique(self):
        mutations = [lambda m, p: m['routes'][0].update(to='missing'),
                     lambda m, p: m['areas'][1].update(engine_map=m['areas'][0]['engine_map']),
                     lambda m, p: m['gyms'][1].update(badge=1),
                     lambda m, p: m['gyms'].pop(),
                     lambda m, p: p['road_one'].update(native_id=p['dogpatch']['native_id']),
                     lambda m, p: p['road_one'].update(script=p['dogpatch']['script'])]
        for mutate in mutations:
            m, p = fixture(); mutate(m, p)
            with self.subTest(mutation=mutations.index(mutate)): self.reject(m, p)
        m, p = fixture(); plans = list(p.values()); plans.append(deepcopy(plans[0]))
        self.assertFalse(contract.audit(m, plans)['passed'])

    def test_blocked_local_passage_and_border_lane_are_rejected(self):
        m, p = fixture()
        for y in range(24): tile(p['road_one'], 16, y, '#')
        self.reject(m, p, 'passage')
        m, p = fixture(); tile(p['road_one'], 0, 12, '#')
        self.reject(m, p, 'ports')
        m, p = fixture(); tile(p['road_one'], 0, 5, '.')
        self.reject(m, p, 'ports')

    def test_arrival_safety_and_return_connectivity_are_distinct(self):
        for mutate in [lambda p: tile(p['gym_1'], 16, 16, '#'),
                       lambda p: p['gym_1']['npcs'][0].update(x=16, y=16),
                       lambda p: p['gym_1']['coord_events'].append(dict(x=16, y=16, elevation=3))]:
            m, p = fixture(); mutate(p)
            with self.subTest(mutation=str(mutate)): self.reject(m, p)
        m, p = fixture()
        for x, y in [(15, 16), (17, 16), (16, 15), (16, 17)]: tile(p['gym_1'], x, y, '#')
        self.reject(m, p, 'return')

    def test_gym_access_requires_a_real_trigger_safe_pair_and_reachable_stamp(self):
        mutations = [lambda p: p['gym_1']['access_points'].pop(),
                     lambda p: p['gym_1']['coord_events'].clear(),
                     lambda p: p['gym_1']['coord_events'][0].update(elevation=1),
                     lambda p: p['gym_1']['access_points'][-1].update(target_id='north_beach'),
                     lambda p: p['gym_1']['access_points'][1].update(target_id='gym_2')]
        for mutate in mutations:
            m, p = fixture(); mutate(p)
            with self.subTest(mutation=mutations.index(mutate)): self.reject(m, p)
        m, p = fixture()
        for x, y in [(11, 10), (13, 10), (12, 11)]: tile(p['gym_5'], x, y, '#')
        self.reject(m, p, 'stage')

    def test_water_is_not_clear_collision_land_and_a_decorative_puddle_cannot_gate(self):
        m, p = fixture()
        before = deepcopy(p['channel_one']['rows'])
        result = run(m, p)
        self.assertTrue(result['passed'], result)
        self.assertEqual(p['channel_one']['rows'], before, 'Audit must not normalize away real water')
        m, p = fixture()
        for y in range(24): p['channel_one']['rows'][y] = p['channel_one']['rows'][y].replace('W', '.')
        tile(p['channel_one'], 1, 1, 'W')
        self.reject(m, p, 'gate_bypass')
        m, p = fixture(); p['channel_one']['legend']['W'] = [368, False, 3]
        self.reject(m, p, 'terrain')
        m, p = fixture(); p['channel_one']['water_positions'] = []
        self.reject(m, p, 'terrain')

    def test_league_has_real_falls_water_above_below_and_both_badges(self):
        m, p = fixture(); p['league_route']['rows'] = [row.replace('V', 'W') for row in p['league_route']['rows']]
        self.reject(m, p, 'gate_bypass')
        m, p = fixture(); tile(p['league_route'], 16, 11, '.')
        self.reject(m, p, 'terrain')
        for badges in [[8], [5], [5, True], [5, 8, 8]]:
            m, p = fixture(); m['league']['requires_badges'] = badges
            with self.subTest(badges=badges): self.reject(m, p, 'league')

    def test_crisis_cannot_require_the_already_locked_league_destination(self):
        m, p = fixture(); m['stage_markers']['crisis_after'].append('angel_island')
        self.reject(m, p, 'stage')
        m, p = fixture(); m['stage_markers']['gym_8_requires'] = 'none'
        self.reject(m, p, 'stage')

    def test_only_approved_exception_and_isolated_save_terrain_contract_are_allowed(self):
        mutations = [lambda m, p: m['areas'][0].update(city='Oakland'),
                     lambda m, p: m['league'].update(scope_exception=''),
                     lambda m, p: m['native'].update(save_magic=0x5346),
                     lambda m, p: p['road_one']['tilesets'].update(primary='gTileset_Unknown'),
                     lambda m, p: p['road_one'].update(tile_grid_base=512),
                     lambda m, p: p['road_one'].update(metadata={'connections': []})]
        for mutate in mutations:
            m, p = fixture(); mutate(m, p)
            with self.subTest(mutation=mutations.index(mutate)): self.reject(m, p)

    def test_ambient_wander_cannot_cover_a_required_arrival_or_wall(self):
        m,p=fixture()
        npc=dict(id=len(p['dogpatch']['npcs'])+1,x=15,y=16,movement='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT',range_x=1)
        p['dogpatch']['npcs'].append(npc)
        # Dogpatch spawn is (16,16), inside this movement envelope.
        self.reject(m,p,'movement')
        npc.update(x=3,y=4)
        self.assertTrue(run(m,p)['passed'])
        tile(p['dogpatch'],4,4,'#')
        self.reject(m,p,'movement')

    def test_small_service_room_requires_its_own_safe_reciprocal_door(self):
        m,p=fixture()
        m['interiors']=[dict(id='warming_room',area='dogpatch',engine_map='RoomOne')]
        room=deepcopy(p['gym_1'])
        room.update(world_id='warming_room',engine_map='RoomOne',native_id='MAP_WARMING_ROOM',
                    script='warming_room.inc')
        room['access_points'][1].update(kind='arrival',target_id='dogpatch')
        room['access_points'][2].update(kind='room_exit',target_id='dogpatch')
        p['warming_room']=room
        p['dogpatch']['access_points'] += [dict(kind='room_entry',x=20,y=7,activation='walk',target_id='warming_room'),
                                          dict(kind='arrival',x=20,y=9,activation='walk',target_id='warming_room')]
        p['dogpatch']['coord_events'].append(dict(x=20,y=7,elevation=3))
        self.assertTrue(run(m,p)['passed'])
        room['access_points'][2]['target_id']='north_beach'
        self.reject(m,p)
        room['access_points'][2]['target_id']='dogpatch'
        tile(room,16,16,'#')
        self.reject(m,p,'arrival')

    def test_service_counter_requires_a_real_two_tile_npc_interaction(self):
        m,p=fixture();m['town_finishing']={'revision':1};m['native']['save_magic']=0x5743
        board=p['dogpatch'];board['legend']['C']=[607,True,3]
        tile(board,25,17,'C');board['access_points'][0]['y']=18
        self.assertTrue(run(m,p)['passed'])
        board['legend']['C']=[614,True,3]  # A wall cannot act as a counter.
        self.reject(m,p,'access')

    def test_ambient_actor_cannot_occupy_a_named_world_section(self):
        m,p=fixture()
        p['angel_island']['world_sections']=[dict(id='lookout',x=25,y=16)]
        self.reject(m,p,'landmark')
        p['angel_island']['world_sections'][0].update(x=24,y=16)
        self.assertTrue(run(m,p)['passed'])

    def test_props_cannot_cut_into_an_attached_building_even_if_collision_stays_solid(self):
        m,p=fixture();m['town_finishing']={'revision':1};m['native']['save_magic']=0x5743
        board=p['dogpatch']
        for dy in range(4):
            for dx in range(3):
                index=515+dy*3+dx;token=chr(index)
                board['legend'][token]=[index,True,3];tile(board,2+dx,2+dy,token)
        board['town_blocks']=[dict(x=2,y=2,width=3,height=4,first_metatile=515)]
        self.assertTrue(run(m,p)['passed'])
        board['legend']['L']=[575,True,3];tile(board,3,5,'L')
        self.reject(m,p,'frontage')

    def test_malformed_inputs_return_errors_instead_of_claiming_success(self):
        m, p = fixture()
        for bad_manifest, bad_plans in [(None, []), ({}, []), (m, None), (m, [{}])]:
            result = contract.audit(bad_manifest, bad_plans)
            self.assertFalse(result['passed']); self.assertTrue(result['errors'])


if __name__ == '__main__':
    unittest.main()
