"""Native region-map chart coordinates; never alters playable geography."""

# Deliberate orthogonal corridors, including the long Pacific Heights return.
# Endpoints come from the authoritative place positions, not a second node list.
BENDS = {
    'route_01': [(140, 92)], 'route_02': [], 'route_03': [(96, 84)],
    'route_04': [(36, 84)], 'route_05': [(36, 60)],
    'route_06': [(56, 44), (84, 44)], 'route_07': [(100, 36)],
    'route_08': [(112, 48), (112, 64), (60, 64)],
    'route_09': [(76, 100), (76, 104)],
    'route_10': [(132, 104)], 'route_11': [(140, 80)],
    'route_12': [], 'route_13': [], 'route_14': [],
    'route_15': [], 'route_16': [(20, 60), (20, 36)],
    'route_17': [(172, 40)], 'route_18': [(184, 64), (184, 88), (144, 88), (144, 80)],
    'league_route': [(156, 40), (156, 28)],
}


def chart_positions(manifest):
    return {key: (round((20 + x * 174 / 100) / 4) * 4,
                  round((24 + y * 92 / 100) / 4) * 4)
            for key, (x, y) in manifest['city_guide']['positions'].items()}


def route_path(route, positions):
    points = [positions[route['from']], *BENDS[route['id']], positions[route['to']]]
    points = [p for n, p in enumerate(points) if not n or p != points[n - 1]]
    if len(points) > 6 or any(a[0] != b[0] and a[1] != b[1] for a, b in zip(points, points[1:])):
        raise ValueError('Region-map route must use at most six orthogonal chart points')
    if any(not 5 <= x <= 218 or not 20 <= y <= 114 for x, y in points):
        raise ValueError('Region-map corridor overlaps the interface frame')
    return points


def path_midpoint(points):
    lengths = [abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(points, points[1:])]
    distance = sum(lengths) // 2
    for a, b, length in zip(points, points[1:], lengths):
        if distance <= length:
            return (a[0] + (distance if b[0] > a[0] else -distance if b[0] < a[0] else 0),
                    a[1] + (distance if b[1] > a[1] else -distance if b[1] < a[1] else 0))
        distance -= length
    return points[-1]
