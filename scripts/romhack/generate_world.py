"""Deterministic, deliberately plain native world geometry from one manifest."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPPOSITE = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
LEGEND = {'.': [1, False, 3], '#': [11, True, 3],
          'W': [368, False, 1], 'V': [179, False, 1]}


def native_id(name):
    return 'MAP_' + re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name).upper()


def records(manifest):
    areas = [dict(area) for area in manifest['areas']]
    routes = [dict(route) for route in manifest['routes']]
    league = manifest['league']
    if league['venue']:
        areas.append({'id': league['venue'], 'label': league['label'],
                      'engine_map': league['engine_map'], 'tags': ['league_placeholder']})
        routes.append({'id': 'league_route', 'engine_map': league['route_engine_map'],
                       'from': league['from_area'], 'from_port': league['from_port'],
                       'to': league['venue'], 'to_port': 'down', 'mode': 'waterfall',
                       'requires_badge': 8, 'bidirectional': True})
    return areas, routes


def port(direction, width, height):
    return {'up': (width // 2, 0), 'down': (width // 2, height - 1),
            'left': (0, height // 2), 'right': (width - 1, height // 2)}[direction]


def geometry(width, height, ports, *, plaza=False, wet=None):
    """Three-tile corridors meet at a clear center, including elbow connectors."""
    grid = [['#'] * width for _ in range(height)]
    cx, cy = width // 2, height // 2
    for direction in ports:
        px, py = port(direction, width, height)
        for y in range(min(cy, py), max(cy, py) + 1):
            for x in range(min(cx, px), max(cx, px) + 1):
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if 0 <= x + dx < width and 0 <= y + dy < height:
                            grid[y + dy][x + dx] = '.'
    # Towns and gym rooms reserve explicit approaches, not decorative stock maps.
    for y in range(5 if plaza else cy - 1, height - 2 if plaza else cy + 2):
        for x in range(7 if plaza else cx - 1, width - 7 if plaza else cx + 2):
            grid[y][x] = '.'
    if wet:
        for y in range(cy - 1, cy + 2):
            for x in range(cx - 1, cx + 2):
                if grid[y][x] == '.':
                    grid[y][x] = 'W'
        if wet == 'waterfall':
            # Northward ascent has water on both sides of the fall.
            for y in range(cy - 4, cy + 5):
                for x in range(cx - 1, cx + 2):
                    grid[y][x] = 'V' if y == cy else 'W'
    return [''.join(row) for row in grid]


def access(kind, x, y, target=None, activation='walk'):
    point = {'kind': kind, 'x': x, 'y': y, 'activation': activation}
    if target:
        point['target_id'] = target
    return point


def league_geometry(spec):
    """Landing, tunnel switchbacks, rival pocket and summit remain one area."""
    grid = [['#'] * 32 for _ in range(24)]
    def carve(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                grid[y][x] = '.'
    carve(*spec['landing'])
    carve(*spec['connection'])
    points = spec['tunnel_path']
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        carve(min(x0, x1)-1, min(y0, y1)-1, max(x0, x1)+1, max(y0, y1)+1)
    carve(*spec['rival_pocket'])
    carve(*spec['summit'])
    return [''.join(row) for row in grid]


def coord(x, y, script):
    return {'type': 'trigger', 'x': x, 'y': y, 'elevation': 3,
            'var': 'VAR_TEMP_0', 'var_value': '0', 'script': script}


def generate(manifest):
    areas, routes = records(manifest)
    width, height = manifest['geometry']['width'], manifest['geometry']['height']
    nodes = {item['id']: item for item in areas + routes + manifest['gyms']}
    links = {identifier: [] for identifier in nodes}
    for route in routes:
        for end in ('from', 'to'):
            area, direction = route[end], route[end + '_port']
            links[area].append({'map': native_id(route['engine_map']),
                                'direction': direction, 'offset': 0})
            links[route['id']].append({'map': native_id(nodes[area]['engine_map']),
                                      'direction': OPPOSITE[direction], 'offset': 0})
    plans = []
    gym_by_area = {gym['area']: gym for gym in manifest['gyms']}
    area_ids = {area['id'] for area in areas}
    gym_ids = {gym['id'] for gym in manifest['gyms']}
    for identifier, item in nodes.items():
        room = identifier in gym_ids
        plaza = identifier in area_ids or room
        directions = [link['direction'] for link in links[identifier]]
        rows = geometry(width, height, directions, plaza=plaza,
                        wet=item.get('mode') if item.get('mode') != 'walk' else None)
        if identifier == manifest['league']['venue']:
            rows = league_geometry(manifest['league']['blockout'])
        label = item.get('label', identifier.replace('_', ' ').title())
        plan = {'world_id': identifier, 'engine_map': item['engine_map'],
                'native_id': native_id(item['engine_map']), 'label': label,
                'rows': rows, 'legend': LEGEND, 'border_tile': 11,
                'tilesets': {'primary': manifest['native']['primary_tileset'],
                             'secondary': manifest['native']['secondary_tileset']},
                'metadata': {'music': 'MUS_PETALBURG', 'weather': 'WEATHER_SUNNY',
                             'requires_flash': False, 'allow_cycling': False,
                             'allow_escaping': False, 'allow_running': True,
                             'show_map_name': False, 'battle_scene': 'MAP_BATTLE_SCENE_NORMAL'},
                'connections': links[identifier] or None, 'npcs': [],
                'coord_events': [], 'access_points': [], 'script': identifier + '.inc'}
        if plaza:
            plan['npcs'].append({'id': 1, 'x': 12, 'y': 9,
                                  'graphics': 'OBJ_EVENT_GFX_SCIENTIST_1',
                                  'script': 'WB_' + identifier + '_Info'})
            plan['access_points'].append(access('checkpoint', 12, 10, activation='interact'))
        if identifier == manifest['league']['venue']:
            plan['world_sections'] = manifest['league']['blockout']['sections']
            for index, (x, y, section) in enumerate(
                    [(14, 21, 'Landing'), (7, 17, 'Tunnels'), (26, 14, 'Rival')], 2):
                plan['npcs'].append({'id': index, 'x': x, 'y': y,
                                      'graphics': 'OBJ_EVENT_GFX_SCIENTIST_1',
                                      'script': 'WB_angel_island_' + section})
        if identifier == manifest['start']['area']:
            plan['access_points'].append(access('spawn', manifest['start']['x'],
                                                manifest['start']['y']))
        if identifier in gym_by_area:
            gym = gym_by_area[identifier]
            plan['access_points'] += [access('gym_entry', 16, 7, gym['id']),
                                     access('arrival', 16, 10, gym['id'])]
            plan['coord_events'].append(coord(16, 7, 'WB_' + identifier + '_Enter'))
        if room:
            plan['access_points'] += [access('gym_exit', 16, 20, item['area']),
                                     access('arrival', 16, 16, item['area'])]
            plan['coord_events'].append(coord(16, 20, 'WB_' + identifier + '_Exit'))
        plan['water_positions'] = [[x, y] for y, row in enumerate(rows)
                                   for x, token in enumerate(row) if token in 'WV']
        plans.append(plan)
    return plans


def write_world(manifest, directory, modules_root=None):
    from world_scripts import map_script
    from content_modules import MODULES, load_modules, apply_module_layouts, script_with_module
    directory.mkdir(parents=True, exist_ok=True)
    modules = load_modules(manifest, modules_root or MODULES)
    plans = apply_module_layouts(generate(manifest), modules)
    by_world = {m['contract']['world_id']: m for m in modules.values()}
    for plan in plans:
        (directory / (plan['world_id'] + '.json')).write_text(
            json.dumps(plan, indent=2) + '\n')
        (directory / plan['script']).write_text(script_with_module(
            map_script(manifest, plan), by_world.get(plan['world_id'])))
    start = next(plan for plan in plans if plan['world_id'] == manifest['start']['area'])
    content = {'maps': ['world-blockout/' + plan['world_id'] + '.json' for plan in plans],
               'spawn': {'map': start['engine_map'], 'id': start['native_id'][4:],
                         'x': manifest['start']['x'], 'y': manifest['start']['y']},
               'recovery_points': [{'id': name, 'map': start['native_id'],
                                    'x': 16, 'y': 16} for name in
                                   ('HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F',
                                    'HEAL_LOCATION_LITTLEROOT_TOWN_MAYS_HOUSE_2F')]}
    teams = [team for module in modules.values() if module['meta']['status'] != 'stub'
             for team in module['meta']['trainers']]
    if teams:
        (directory / 'module-battles.json').write_text(json.dumps({'trainers': teams}, indent=2) + '\n')
        content['battle_content'] = 'world-blockout/module-battles.json'
    (directory / 'content.json').write_text(json.dumps(content, indent=2) + '\n')
    return plans, content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'romhack/world/world.json')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    plans, _ = write_world(manifest, ROOT / 'romhack/content/world-blockout')
    print(json.dumps({'maps': len(plans), 'areas': len(records(manifest)[0]),
                      'routes': len(records(manifest)[1]), 'gyms': len(manifest['gyms'])}))


if __name__ == '__main__':
    main()
