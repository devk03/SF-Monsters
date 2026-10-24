"""Physical intermediate maps while retaining coarse story/guide journeys."""
from copy import deepcopy

OPPOSITE = {'left':'right','right':'left','up':'down','down':'up'}


def physical_routes(routes):
    result = []
    for route in routes:
        base = deepcopy(route)
        sections = base.pop('intermediate_sections', [])
        result.append(base)
        prior = base
        for section in sections:
            added = dict(id=section['id'],engine_map=section['engine_map'],
                label=section['label'],setting=section['setting'],
                from_port=OPPOSITE[route['to_port']],to_port=route['to_port'],
                to=route['to'],mode=route['mode'],requires_badge=route['requires_badge'],
                bidirectional=True,parent_route=route['id'])
            added['from'] = prior['id']
            prior['to'] = added['id']
            result.append(added)
            prior = added
    return result
