"""Independent source contract for the draft world, not native gameplay approval.

No generator or map producer is imported. Terrain classification is pinned to
the development General tileset: 368/ocean water and 179/waterfall require
traversal abilities even though their native collision bits are clear.
"""
from collections import deque
import re
from world_art_contract import load_profiles


PORTS = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
WATER = 368
WATERFALL = 179
ACCESS_KINDS = {'spawn', 'gym_entry', 'gym_exit', 'checkpoint', 'arrival', 'room_entry', 'room_exit'}
NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')


class _Invalid(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _need(condition, code, message):
    if not condition:
        raise _Invalid(code, message)


def _integer(value, low, high, label):
    _need(type(value) is int and low <= value <= high, 'numeric',
          f'{label} must be an integer in {low}..{high}')
    return value


def _unique(items, field, label):
    _need(type(items) is list, 'manifest', f'{label} must be a list')
    result = {}
    for item in items:
        _need(type(item) is dict, 'manifest', f'{label} entry must be an object')
        value = item[field]
        _need(type(value) is str and NAME.fullmatch(value), 'identity',
              f'Invalid {label} {field}: {value!r}')
        _need(value not in result, 'duplicate', f'Duplicate {label} {field}: {value}')
        result[value] = item
    return result


def _port_cells(direction, width, height):
    if direction in ('left', 'right'):
        return [(0 if direction == 'left' else width - 1, height // 2 + d)
                for d in (-1, 0, 1)]
    return [(width // 2 + d, 0 if direction == 'up' else height - 1)
            for d in (-1, 0, 1)]


class _World:
    def __init__(self, manifest, plans):
        self.manifest = manifest
        _need(type(manifest) is dict, 'manifest', 'Manifest must be an object')
        _need(manifest['schema_version'] == 1 and type(manifest['schema_version']) is int,
              'manifest', 'Unsupported world manifest schema')
        _need(manifest['profile'] == 'world-blockout', 'manifest', 'Wrong world profile')
        geometry = manifest['geometry']
        _need(geometry == {'width': 32, 'height': 24, 'walk_lane_width': 3},
              'geometry', 'This contract requires 32x24 maps with three-tile ports')
        _need(all(type(value) is int for value in geometry.values()), 'geometry',
              'Geometry dimensions and lane width must be integers')
        native = manifest['native']
        _need(native['primary_tileset'] == 'gTileset_General'
              and native['secondary_tileset'] == 'gTileset_Petalburg', 'terrain',
              'Terrain semantics require the pinned General/Petalburg tilesets')
        _need(type(native['save_magic']) is int and native['save_magic'] == (0x5743 if manifest.get('town_finishing') else 0x5742)
              and type(native['save_schema']) is int and native['save_schema'] == 1,
              'identity', 'Blockout save identity must remain separate from v80')
        self.width, self.height = 32, 24
        self.art = load_profiles() if manifest.get('town_finishing') else {}
        areas, routes = list(manifest['areas']), list(manifest['routes'])
        self.league = manifest['league']
        self.league_id = self.league.get('venue')
        if self.league_id is not None:
            _need(self.league_id == 'angel_island' and type(self.league.get('scope_exception')) is str
                  and bool(self.league['scope_exception'].strip()), 'scope',
                  'Only the explicitly recorded Angel Island exception is supported')
            _need(self.league['from_area'] == 'north_beach' and self.league['from_port'] == 'up',
                  'league', 'League connector must leave North Beach through its north port')
            _need(type(self.league['requires_badges']) is list
                  and sorted(self.league['requires_badges']) == [5, 8]
                  and all(type(badge) is int for badge in self.league['requires_badges']),
                  'league', 'League requires both Surf badge 5 and Waterfall badge 8')
            areas.append({'id': self.league_id, 'engine_map': self.league['engine_map'],
                          'city': self.league['city']})
            routes.append({'id': 'league_route', 'engine_map': self.league['route_engine_map'],
                           'from': self.league['from_area'], 'from_port': self.league['from_port'],
                           'to': self.league_id, 'to_port': 'down', 'mode': 'waterfall',
                           'requires_badge': 8, 'bidirectional': True})
        self.areas = _unique(areas, 'id', 'area')
        self.routes = _unique(routes, 'id', 'route')
        self.gyms = _unique(manifest['gyms'], 'id', 'gym')
        self.rooms = _unique(manifest.get('interiors', []), 'id', 'interior')
        _need(bool(self.areas), 'manifest', 'No world areas declared')
        _need(len(self.gyms) == 8, 'gyms', 'Exactly eight gym slots are required')
        _need({gym['badge'] for gym in self.gyms.values()} == set(range(1, 9))
              and all(type(gym['badge']) is int for gym in self.gyms.values()),
              'gyms', 'Gym badges must be unique integers 1..8')
        self.by_badge = {gym['badge']: gym for gym in self.gyms.values()}
        self.declared = {}
        slots = set()
        for kind, records in [('area', self.areas), ('route', self.routes), ('gym', self.gyms), ('interior', self.rooms)]:
            for identifier, record in records.items():
                _need(identifier not in self.declared, 'duplicate', f'Reused world ID: {identifier}')
                slot = record['engine_map']
                _need(type(slot) is str and NAME.fullmatch(slot), 'identity', 'Invalid engine map slot')
                _need(slot not in slots, 'duplicate', f'Reused engine map slot: {slot}')
                slots.add(slot)
                self.declared[identifier] = (kind, record)
        for area in self.areas.values():
            _need(area['city'] == 'San Francisco' or area['id'] == self.league_id, 'scope',
                  f'Unapproved outside-SF area: {area["id"]}')
        for room in self.rooms.values():
            _need(room['area'] in self.areas, 'reference', 'Interior parent is absent')
        for gym in self.gyms.values():
            _need(gym['area'] in self.areas, 'reference', f'Dangling gym area: {gym["id"]}')
        self.start = manifest['start']
        _need(self.start['area'] in self.areas, 'reference', 'Start area is absent')
        self.markers = manifest['stage_markers']
        _need(self.markers['tower_after'] in self.areas, 'reference', 'Tower stage references absent area')
        _need(type(self.markers['crisis_after']) is list and bool(self.markers['crisis_after'])
              and len(set(self.markers['crisis_after'])) == len(self.markers['crisis_after'])
              and all(area in self.areas for area in self.markers['crisis_after']),
              'reference', 'Crisis stages must reference distinct declared areas')
        _need(self.markers['gym_8_requires'] == 'crisis_marker', 'stage',
              'Gym 8 must explicitly require the crisis marker')
        _need(type(manifest['story_waypoints']) is list
              and all(area in self.areas for area in manifest['story_waypoints']),
              'reference', 'Story waypoint references an absent area')
        self.expected = {identifier: {} for identifier in self.declared}
        for route in self.routes.values():
            source, target = route['from'], route['to']
            _need(source in self.areas and target in self.areas and source != target,
                  'reference', f'Dangling or self route: {route["id"]}')
            _need(route['from_port'] in PORTS and route['to_port'] in PORTS,
                  'direction', f'Invalid route port: {route["id"]}')
            _need(route['bidirectional'] is True, 'return', f'Missing route return: {route["id"]}')
            badge = _integer(route['requires_badge'], 0, 8, 'required badge')
            _need(route['mode'] in ('walk', 'surf', 'waterfall'), 'terrain', 'Unsupported route mode')
            if route['mode'] == 'surf':
                _need(badge == 5, 'stage', 'Core Surf routes must declare badge 5')
            if route['mode'] == 'waterfall':
                _need(route['id'] == 'league_route' and badge == 8, 'stage',
                      'Waterfall belongs to the badge-8 League connector')
            self._expect(source, route['from_port'], route['id'])
            self._expect(route['id'], PORTS[route['from_port']], source)
            self._expect(target, route['to_port'], route['id'])
            self._expect(route['id'], PORTS[route['to_port']], target)
        self.plans = _unique(plans, 'world_id', 'generated map')
        _need(set(self.plans) == set(self.declared), 'coverage',
              'Generated map IDs differ from declared areas/routes/gyms')
        self.native = {}
        self.boards = {}
        self.sizes = {}
        script_names = set()
        for identifier, plan in self.plans.items():
            _need(plan['engine_map'] == self.declared[identifier][1]['engine_map'], 'identity',
                  f'Wrong engine map slot for {identifier}')
            native = plan['native_id']
            _need(type(native) is str and re.fullmatch(r'MAP_[A-Z0-9_]+', native),
                  'identity', f'Invalid native map ID: {identifier}')
            _need(native not in self.native, 'duplicate', f'Duplicate native map ID: {native}')
            self.native[native] = identifier
            self.boards[identifier] = self._board(identifier, plan)
            _need(plan['script'] not in script_names, 'duplicate', 'Two maps share one script file')
            script_names.add(plan['script'])
        self._connections()
        self._access_links()

    def _expect(self, identifier, direction, target):
        _need(direction not in self.expected[identifier], 'ports',
              f'Two routes occupy {identifier}.{direction}')
        self.expected[identifier][direction] = target

    def _position(self, event, label, identifier=None):
        width,height = self.sizes.get(identifier,(self.width,self.height))
        x = _integer(event['x'], 0, width - 1, label + ' x')
        y = _integer(event['y'], 0, height - 1, label + ' y')
        return x, y

    def _board(self, identifier, plan):
        _need('tile_grid_base' not in plan, 'terrain',
              'Backdrop tile overrides would invalidate the terrain contract')
        _need(not plan.get('warp_events'), 'events',
              'This blockout uses declared script warps, not extra native warp events')
        _need(not set(plan.get('metadata', {})) & {
            'connections', 'object_events', 'warp_events', 'coord_events', 'bg_events', 'layout', 'id'},
            'metadata', 'Metadata may not replace validated native graph/event fields')
        if self.manifest.get('city_guide'):
            sections=self.manifest['city_guide']['native_sections']
            _need(set(sections)==set(self.areas) and len(set(sections.values()))==len(sections)
                  and all(re.fullmatch(r'MAPSEC_[A-Z0-9_]+',v) for v in sections.values()),
                  'geography','SF location sections must cover unique approved destinations')
            parent=(self.gyms[identifier]['area'] if identifier in self.gyms else
                    self.rooms[identifier]['area'] if identifier in self.rooms else
                    self.routes[identifier]['from'] if identifier in self.routes else identifier)
            _need(plan.get('metadata',{}).get('region_map_section')==sections[parent],
                  'geography','Native location label has the wrong SF parent')
        profile_name = plan.get('tile_profile','residential')
        _need(not self.art or profile_name in self.art,'terrain','Unknown native art profile')
        profile = self.art.get(profile_name,{})
        secondary = profile.get('secondary',self.manifest['native']['secondary_tileset'])
        _need(plan.get('tilesets') == {
            'primary': self.manifest['native']['primary_tileset'],'secondary':secondary},
            'terrain', 'Plan tilesets differ from the declared native art profile')
        approved = profile.get('metatiles',{})
        width,height = self.rooms.get(identifier,{}).get('size',[32,24])
        _need((width,height) in ((32,24),(16,11)), 'geometry', 'Unsupported outdoor/interior dimensions')
        self.sizes[identifier]=(width,height)
        def position(event,label): return self._position(event,label,identifier)
        rows, legend = plan['rows'], plan['legend']
        _need(type(rows) is list and len(rows) == height
              and all(type(row) is str and len(row) == width for row in rows),
              'geometry', f'{identifier}: rows must be 32x24')
        _need(type(legend) is dict and bool(legend), 'terrain', 'Missing terrain legend')
        for token, tile in legend.items():
            _need(type(token) is str and len(token) == 1 and type(tile) in (list, tuple)
                  and len(tile) == 3, 'terrain', 'Invalid terrain legend entry')
            _integer(tile[0], 0, 1023, 'metatile')
            _need(tile[0] in (1, 11, WATER, WATERFALL) or tile[0] in approved, 'terrain',
                  'Unmodelled native metatile behavior in blockout terrain')
            _need(type(tile[1]) is bool, 'terrain', 'Collision must be boolean')
            _integer(tile[2], 0, 15, 'elevation')
            if token in ('.', '#', 'W', 'V'):
                expected = {'.': [1, False, 3], '#': [11, True, 3],
                            'W': [WATER, False, 1], 'V': [WATERFALL, False, 1]}[token]
                _need(list(tile) == expected, 'terrain', f'{identifier}: redefined {token!r} terrain')
            if tile[0] in (WATER, WATERFALL):
                _need(tile[1] is False and tile[2] == 1, 'terrain',
                      'Native traversal water needs collision 0 and elevation 1')
            else:
                solid = approved[tile[0]][0] if tile[0] in approved else tile[0] == 11
                _need(tile[2] == 3 and tile[1] is solid, 'terrain',
                      'Development ground/walls must retain collision and elevation semantics')
        cells = {}
        wet = set()
        for y, row in enumerate(rows):
            for x, token in enumerate(row):
                _need(token in legend, 'terrain', f'{identifier}: undeclared tile token')
                cells[x, y] = tuple(legend[token])
                if legend[token][0] in (WATER, WATERFALL):
                    wet.add((x, y))
        frontage = set()
        for block in plan.get('town_blocks',[]):
            x0,y0=block['x'],block['y'];width,height=block['width'],block['height']
            if 'style' in block:
                spec = profile.get('cards',{}).get(block['style'],{})
                _need((spec.get('first'),spec.get('width'),spec.get('height')) ==
                      (block['first_metatile'],width,height),'frontage','Building allocation disagrees with the art contract')
            _integer(width,1,11,'frontage width');_integer(height,1,5,'frontage height')
            for dy in range(height):
                for dx in range(width):
                    point=(x0+dx,y0+dy)
                    _need(point not in frontage and point in cells, 'frontage','Architectural footprints overlap or leave the map')
                    frontage.add(point)
                    solid=profile['cards'][block['style']]['blocked'] if 'style' in block else True
                    expected=(block['first_metatile']+dy*width+dx,solid,3)
                    _need(cells[point]==expected,'frontage','A furnishing or terrain stamp cuts through a building')
        from world_street_contract import check_streets, check_edges, CENTERS
        try:check_edges(plan,profile)
        except ValueError as error:_need(False,'frontage',str(error))
        if (plan.get('street_design') or self.manifest.get('town_finishing',{}).get('revision',0)>=4
                and identifier in CENTERS):
            try:
                check_streets(plan,cells,frontage,profile)
            except ValueError as error:
                _need(False,'frontage',str(error))
        if self.manifest.get('town_finishing',{}).get('revision',0)>=6 and identifier in CENTERS:
            from world_street_contract import check_variety,check_sidewalks
            try:
                check_variety(plan,profile)
                check_sidewalks(plan,cells)
            except ValueError as error:_need(False,'frontage',str(error))
        if 'water_positions' in plan:
            positions = [position({'x': pair[0], 'y': pair[1]}, 'water position')
                         for pair in plan['water_positions'] if len(pair) == 2]
            _need(len(positions) == len(plan['water_positions']) and len(set(positions)) == len(positions)
                  and set(positions) == wet, 'terrain', f'{identifier}: water positions differ from actual terrain')
        objects = plan.get('npcs', [])
        _need(type(objects) is list and len(objects) <= 15, 'objects', 'Native object count exceeds player reserve')
        occupied = set()
        local_ids = set()
        for index, event in enumerate(objects, 1):
            point = position(event, identifier + ' NPC')
            _need(point not in occupied, 'objects', f'{identifier}: overlapping NPCs')
            _need(not cells[point][1] and cells[point][0] not in (WATER, WATERFALL),
                  'objects', f'{identifier}: NPC stands on impassable terrain')
            _integer(event['id'], 1, 255, 'NPC ID')
            _need(event['id'] == index and event['id'] not in local_ids, 'objects',
                  'NPC local IDs must follow unique native event order')
            local_ids.add(event['id'])
            occupied.add(point)
        protected = {(event['x'],event['y']) for event in plan.get('access_points', [])}
        for event in objects:
            rx, ry = event.get('range_x',0), event.get('range_y',0)
            _integer(rx,0,1,'ambient movement x range')
            _integer(ry,0,1,'ambient movement y range')
            if rx or ry:
                _need(event.get('movement') == 'MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT'
                      and ry == 0, 'movement', 'Only bounded horizontal ambient movement is allocated')
                point = (event['x'],event['y'])
                envelope = {(point[0]+dx,point[1]+dy) for dx in range(-rx,rx+1)
                            for dy in range(-ry,ry+1)}
                _need(not envelope & (protected | (occupied-{point}))
                      and all(p in cells and not cells[p][1]
                              and cells[p][0] not in (WATER,WATERFALL) for p in envelope),
                      'movement', 'Ambient movement can obstruct a required approach or solid tile')
        coords = set()
        for event in plan.get('coord_events', []):
            point = position(event, identifier + ' trigger')
            _need(point not in coords and not cells[point][1], 'events', 'Overlapping or blocked coordinate trigger')
            _need(type(event['elevation']) is int and event['elevation'] == cells[point][2],
                  'events', 'Coordinate trigger elevation differs from its walk tile')
            coords.add(point)
        backgrounds = set()
        for event in plan.get('bg_events',[]):
            point=position(event,identifier+' background')
            _need(point not in backgrounds|occupied|coords,'events','Background interactions overlap another event')
            _need(event.get('type')=='sign' and event.get('elevation')==0
                  and event.get('player_facing_dir')=='BG_EVENT_PLAYER_FACING_ANY'
                  and bool(NAME.fullmatch(event.get('script',''))),'events','Unmodelled background interaction kind')
            backgrounds.add(point)
        if self.manifest.get('town_finishing',{}).get('revision',0)>=5 and identifier in CENTERS:
            from world_street_contract import check_details
            try:check_details(plan)
            except ValueError as error:_need(False,'street_details',str(error))
        access = plan.get('access_points', [])
        _need(type(access) is list, 'access', 'Access points must be a list')
        for event in access:
            point = position(event, identifier + ' access')
            _need(event['kind'] in ACCESS_KINDS and event['activation'] in ('walk', 'interact'),
                  'access', 'Unknown access kind or activation')
            if 'target_id' in event:
                _need(event['target_id'] in self.declared, 'reference', 'Dangling access target')
            if event['kind'] in ('spawn', 'arrival'):
                _need(not cells[point][1] and point not in occupied and point not in coords,
                      'arrival', f'{identifier}: unsafe arrival/spawn overlaps solid tile, NPC or trigger')
            elif event['activation'] == 'walk':
                _need(not cells[point][1] and point not in occupied,
                      'access', f'{identifier}: blocked walk activation')
                _need(point in coords, 'access', f'{identifier}: walk access has no native trigger')
            else:
                adjacent = {(point[0]-1, point[1]), (point[0]+1, point[1]),
                            (point[0], point[1]-1), (point[0], point[1]+1)}
                _need(not cells[point][1] and point not in occupied and point not in coords,
                      'access', f'{identifier}: interaction access position is not a safe standing tile')
                x,y = point
                across_counter = {(x+2*dx,y+2*dy) for dx,dy in ((-1,0),(1,0),(0,-1),(0,1))
                                  if approved.get(cells.get((x+dx,y+dy),(None,))[0],(False,0))[1] == 0x1080}
                _need(bool(adjacent & (occupied | backgrounds) or across_counter & occupied), 'access',
                      f'{identifier}: interaction position has no adjacent object or staffed native counter')
        _need(coords == {(point['x'], point['y']) for point in access
                          if point['activation'] == 'walk'
                          and point['kind'] not in ('arrival', 'spawn')},
              'events', f'{identifier}: native triggers and declared walk accesses differ')
        script = plan['script']
        _need(type(script) is str and re.fullmatch(r'[A-Za-z0-9_-]+\.inc', script),
              'script', 'Script must be a local .inc filename')
        landmarks = [position(event, identifier+' landmark') for event in
                     plan.get('world_sections',[])+plan.get('scenic_viewpoints',[])]
        _need(all(not cells[p][1] and p not in occupied and p not in coords for p in landmarks),
              'landmark', 'Named world section is blocked by geometry, an actor or a trigger')
        return {'cells': cells, 'water': wet, 'occupied': occupied, 'coords': coords,
                'access': access, 'landmarks':landmarks, 'connections': {}, 'warp_actions': {}}

    def _connections(self):
        for identifier, plan in self.plans.items():
            actual = {}
            for link in plan.get('connections') or []:
                _need(type(link) is dict and link['direction'] in PORTS, 'direction',
                      f'{identifier}: invalid native connection direction')
                _need(type(link['offset']) is int and link['offset'] == 0, 'ports', 'Only aligned offset-0 ports are supported')
                direction = link['direction']
                _need(direction not in actual, 'ports', f'{identifier}: duplicate connection direction')
                _need(link['map'] in self.native, 'reference', f'{identifier}: dangling native connection')
                actual[direction] = self.native[link['map']]
            _need(actual == self.expected[identifier], 'connections',
                  f'{identifier}: native connections differ from declared reversible ports')
            self.boards[identifier]['connections'] = actual
            width,height = self.sizes[identifier]
            allowed = {point for direction in actual
                       for point in _port_cells(direction, self.width, self.height)}
            for point, cell in self.boards[identifier]['cells'].items():
                x, y = point
                if x in (0, width-1) or y in (0, height-1):
                    _need(cell[1] or point in allowed, 'ports',
                          f'{identifier}: unmodelled open border outside a declared lane')
        for identifier, board in self.boards.items():
            for direction, target in board['connections'].items():
                _need(self.boards[target]['connections'].get(PORTS[direction]) == identifier,
                      'return', f'{identifier}: missing reciprocal return')
                left = _port_cells(direction, self.width, self.height)
                right = _port_cells(PORTS[direction], self.width, self.height)
                for a, b in zip(left, right):
                    _need(self._passable(identifier, a, 8) and self._passable(target, b, 8)
                          and a not in board['coords'] and b not in self.boards[target]['coords'],
                          'ports', f'{identifier}.{direction}: blocked or triggered three-tile passage')

    def _arrival(self, target, source):
        candidates = [point for point in self.boards[target]['access'] if point['kind'] == 'arrival']
        selected = [point for point in candidates if point.get('target_id') == source]
        if not selected:
            selected = [point for point in candidates if 'target_id' not in point]
        _need(len(selected) == 1, 'arrival', f'{source}->{target}: require one unambiguous safe arrival')
        return selected[0]['x'], selected[0]['y']

    def _access_links(self):
        for identifier, board in self.boards.items():
            for point in board['access']:
                if point['kind'] not in ('gym_entry', 'gym_exit', 'room_entry', 'room_exit'):
                    continue
                target = point.get('target_id')
                _need(target in self.boards, 'reference', 'Missing gym access target')
                entry_kind = 'gym_entry' if point['kind'].startswith('gym_') else 'room_entry'
                exit_kind = 'gym_exit' if entry_kind == 'gym_entry' else 'room_exit'
                slots = self.gyms if entry_kind == 'gym_entry' else self.rooms
                if point['kind'] == entry_kind:
                    _need(target in slots and slots[target]['area'] == identifier,
                          'gyms', 'Gym entrance does not match its manifest parent')
                else:
                    _need(identifier in slots and slots[identifier]['area'] == target,
                          'gyms', 'Gym exit does not return to its manifest parent')
                kind = exit_kind if point['kind'] == entry_kind else entry_kind
                _need(any(other['kind'] == kind and other.get('target_id') == identifier
                          for other in self.boards[target]['access']),
                      'return', f'{identifier}->{target}: missing gym return access')
                x, y = point['x'], point['y']
                _need((x, y) not in board['warp_actions'], 'access', 'Two warps share an activation tile')
                board['warp_actions'][x, y] = (target, self._arrival(target, identifier), point['activation'])
        for identifier, gym in self.gyms.items():
            board = self.boards[identifier]
            _need(any(point['kind'] == 'checkpoint' for point in board['access']),
                  'gyms', f'{identifier}: missing badge-stamp checkpoint')
            _need(any(point['kind'] == 'gym_exit' and point.get('target_id') == gym['area']
                      for point in board['access']), 'gyms', f'{identifier}: wrong or missing parent exit')
            _need(any(point['kind'] == 'gym_entry' and point.get('target_id') == identifier
                      for point in self.boards[gym['area']]['access']),
                  'gyms', f'{identifier}: missing entrance in its declared area')

    def _passable(self, identifier, point, stage):
        board = self.boards[identifier]
        cell = board['cells'].get(point)
        return bool(cell is not None and not cell[1] and point not in board['occupied']
                    and (cell[0] != WATER or stage >= 5)
                    and (cell[0] != WATERFALL or stage >= 8))

    def _neighbors(self, identifier, point, stage, *, local=False):
        board = self.boards[identifier]
        action = board['warp_actions'].get(point)
        if action:
            if not local:
                yield action[0], action[1]
            if action[2] == 'walk':
                return
        x, y = point
        width,height = self.sizes[identifier]
        for xx, yy, side in [(x - 1, y, 'left'), (x + 1, y, 'right'),
                             (x, y - 1, 'up'), (x, y + 1, 'down')]:
            target, position = identifier, (xx, yy)
            if not 0 <= xx < width or not 0 <= yy < height:
                if local or side not in board['connections']:
                    continue
                target = board['connections'][side]
                position = (xx % width, yy % height)
                # Native aligned edges are usable only through their authored lanes.
                if point not in _port_cells(side, self.width, self.height):
                    continue
            if self._passable(target, position, stage):
                yield target, position

    def _flood(self, identifier, point, stage, *, local=False):
        if not self._passable(identifier, point, stage):
            return set()
        start = (identifier, point)
        queue, seen = deque([start]), {start}
        while queue:
            item = queue.popleft()
            for adjacent in self._neighbors(*item, stage, local=local):
                if adjacent not in seen and self._passable(*adjacent, stage):
                    seen.add(adjacent)
                    queue.append(adjacent)
        return seen

    def _accessible(self, identifier, point, seen):
        x, y = point['x'], point['y']
        return (identifier, (x, y)) in seen

    def _declared_reach(self, stage):
        seen = {self.start['area']}
        changed = True
        while changed:
            changed = False
            for route in self.routes.values():
                if route['requires_badge'] <= stage and (route['from'] in seen or route['to'] in seen):
                    previous = len(seen)
                    seen.update((route['from'], route['to']))
                    changed |= len(seen) != previous
        return seen

    def coverage(self):
        start = self._position(self.start, 'new-game spawn')
        initial = self.boards[self.start['area']]
        _need(self._passable(self.start['area'], start, 0) and start not in initial['coords'],
              'arrival', 'New-game spawn is blocked, wet, or a trigger')
        _need(any(point['kind'] == 'spawn' and (point['x'], point['y']) == start
                  for point in initial['access']), 'arrival', 'Missing matching spawn access point')
        # Local checks catch a severed route even if an external world loop reaches both ends.
        for identifier, board in self.boards.items():
            ports = [point for side in board['connections'] for point in _port_cells(side, self.width, self.height)]
            if ports:
                local = self._flood(identifier, ports[0], 8, local=True)
                _need(all((identifier, point) in local for point in ports), 'passage',
                      f'{identifier}: ports do not intersect one reachable local walk lane')
            for point in board['access']:
                if point['kind'] not in ('arrival', 'spawn'):
                    continue
                landed = self._flood(identifier, (point['x'], point['y']), 8, local=True)
                exits = ports or [(other['x'], other['y']) for other in board['access']
                                  if other['kind'] in ('gym_exit','room_exit')]
                _need(bool(exits) and all((identifier, cell) in landed for cell in exits),
                      'return', f'{identifier}: safe-looking arrival is stranded from its return paths')
            if identifier in self.routes:
                route = self.routes[identifier]
                if route['requires_badge']:
                    _need(bool(board['water']), 'terrain', f'{identifier}: traversal gate lost all water')
                    origin = _port_cells(PORTS[route['from_port']], self.width, self.height)[1]
                    before = self._flood(identifier, origin, route['requires_badge'] - 1, local=True)
                    far = _port_cells(PORTS[route['to_port']], self.width, self.height)
                    _need(not any((identifier, point) in before for point in far), 'gate_bypass',
                          f'{identifier}: dry passage bypasses required badge')
                if route['mode'] == 'waterfall':
                    falls = {point for point, cell in board['cells'].items() if cell[0] == WATERFALL}
                    _need(bool(falls), 'terrain', 'League connector lost its actual waterfall lane')
                    for x, y in falls:
                        _need(all(board['cells'].get((x, yy), (None,))[0] == WATER
                                  for yy in (y-1, y+1)), 'terrain',
                              'Waterfall lane must preserve native water immediately above and below')
        stages = []
        for stage in range(9):
            seen = self._flood(self.start['area'], start, stage)
            areas = {identifier for identifier, _ in seen if identifier in self.areas}
            _need(areas == self._declared_reach(stage), 'stage',
                  f'Badge stage {stage}: actual terrain access differs from declared traversal gates')
            if stage < 8:
                gym = self.by_badge[stage + 1]
                _need(any(point['kind'] == 'checkpoint' and self._accessible(gym['id'], point, seen)
                          for point in self.boards[gym['id']]['access']),
                      'stage', f'Badge {stage + 1}: stamp checkpoint is unreachable before earning its own badge')
            if stage == 7:
                checkpoints = set(self.markers['crisis_after']) | {self.markers['tower_after'], 'lands_end'}
                _need(checkpoints <= areas and all(
                    any(point['kind'] == 'checkpoint' and self._accessible(area, point, seen)
                        for point in self.boards[area]['access']) for area in checkpoints),
                    'stage', 'Gym 8 crisis prerequisites must be accessible before badge 8')
            stages.append({'badges': stage, 'areas': sorted(areas),
                           'maps_reached': len({identifier for identifier, _ in seen})})
        _need(areas == set(self.areas), 'reachability', 'World areas remain unreachable at full core traversal')
        _need({identifier for identifier, _ in seen} == set(self.boards), 'reachability',
              'Generated route or gym map remains unreachable')
        for identifier, board in self.boards.items():
            _need(all((identifier,p) in seen for p in board['landmarks']),
                  'landmark', 'Named world section is unreachable')
            for point in board['access']:
                _need(self._accessible(identifier, point, seen), 'access',
                      f'{identifier}: unreachable {point["kind"]} access position')
        _need(all(area in areas for area in self.markers['crisis_after'])
              and self.markers['tower_after'] in areas and 'lands_end' in areas,
              'stage', 'Crisis/late-gym return cannot be completed')
        return stages


def audit(manifest, plans, core_only=False):
    """Return conformance facts; never attest compiled scripts or native movement.

    Badge stages assume the loan traversal monster and native badge flags implement
    the manifest. Actual stamp prerequisites, script warp coordinates and HM behavior
    require the separate native compiled/runtime checks.
    """
    result = {'passed': False, 'counts': {}, 'errors': [], 'incomplete_scope': True,
              'full_completion': False, 'stages': [],
              'scope': 'Independent manifest/source geometry contract only; not compiled map, script, native traversal or release approval.',
              'native_gate_scripts_verified': False, 'native_warp_scripts_verified': False}
    result['league_venue_pending'] = (manifest.get('league', {}).get('venue') is None
                                      if type(manifest) is dict and type(manifest.get('league')) is dict else None)
    try:
        _need(type(core_only) is bool, 'scope', 'core_only must be boolean')
        world = _World(manifest, plans)
        result['counts'] = {'areas': len(world.areas), 'routes': len(world.routes),
                            'gyms': len(world.gyms), 'interiors':len(world.rooms), 'maps': len(world.plans)}
        result['stages'] = world.coverage()
        result['counts']['badge_stages'] = len(result['stages'])
        pending = manifest['league']['venue'] is None
        result['league_venue_pending'] = pending
        _need(core_only or not pending, 'league_pending',
              'League venue is pending; core-only results are incomplete')
        result['incomplete_scope'] = core_only or pending
        result['passed'] = True
    except _Invalid as error:
        result['errors'].append({'code': error.code, 'message': str(error)})
    except (KeyError, TypeError, IndexError, ValueError, AttributeError) as error:
        result['errors'].append({'code': 'malformed', 'message': 'Missing or malformed source contract: ' + str(error)})
    return result
