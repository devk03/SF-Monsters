"""Region-scale SF positions and short chart paths; playable maps are unchanged."""

# Curated bends follow the peninsula and the bay instead of drawing subway boxes.
BENDS = {
    'route_01': [(134,115)], 'route_02': [], 'route_03': [],
    'route_04': [(68,95),(52,95)], 'route_05': [(40,85),(48,78)],
    'route_06': [(77,66),(88,57)], 'route_07': [],
    'route_08': [(83,78),(79,94)], 'route_09': [],
    'route_10': [(115,122),(132,116)], 'route_11': [],
    'route_12': [(137,76)], 'route_13': [], 'route_14': [],
    'route_15': [(44,108)], 'route_16': [(45,78),(29,72)],
    'route_17': [(144,53),(171,62)], 'route_18': [(181,89),(161,100)],
    'league_route': [(147,39)],
    'route_19': [(56,66)], 'route_20': [(77,47)],
}


def chart_positions(manifest):
    return {key:(round(x*224/100),16+round(y*112/100))
            for key,(x,y) in manifest['city_guide']['positions'].items()}


def route_path(route, positions):
    points = [positions[route['from']],*BENDS[route['id']],positions[route['to']]]
    points = [p for n,p in enumerate(points) if not n or p != points[n-1]]
    if not 2 <= len(points) <= 6 or any(not 5<=x<=218 or not 24<=y<=123 for x,y in points):
        raise ValueError('Region-map route escapes its native chart or vertex budget')
    return points


def path_midpoint(points):
    # Chebyshev length matches the native integer line rasterizer's pixel steps.
    lengths = [max(abs(a[0]-b[0]),abs(a[1]-b[1])) for a,b in zip(points,points[1:])]
    distance = sum(lengths)//2
    for a,b,length in zip(points,points[1:],lengths):
        if distance <= length:
            def part(start,end):
                delta = end-start
                return start + ((distance*abs(delta)+length//2)//length)*(1 if delta>=0 else -1)
            return part(a[0],b[0]),part(a[1],b[1])
        distance -= length
    return points[-1]
