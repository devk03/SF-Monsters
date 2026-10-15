"""Declared curbside footprint, collision and clear entrances for original props."""
from copy import deepcopy
from city_furniture import CARDS

# Coordinates name the upper-left native cell, not a sprite's visual center.
# North sidewalk bases are row7; the opposite curb is row11.
PLACEMENTS = (
    ('lamp',17,6), ('lamp',36,6),
    ('meter',21,7), ('meter',26,7),
    ('hydrant',11,7), ('bin',15,7), ('rack',23,7),
    ('tree',37,6), ('bench',20,11), ('recycling',33,11),
)
FIRST_RECORD = 120
TOKENS = {'u':[0,False,3], 'U':[0,True,3]}


def catalog():
    result = {};first = FIRST_RECORD
    for name,_,(width,height) in CARDS:
        result[name] = (width//16,height//16,first)
        first += width*height//256
    return result


def footprint():
    """One bottom row of grounded collision; walkable overhead cells above it."""
    cards = catalog();cells = {}
    for name,left,top in PLACEMENTS:
        width,height,first = cards[name]
        for y in range(height):
            for x in range(width):
                point = (left+x,top+y)
                if point in cells:
                    raise ValueError('City furniture footprints overlap.')
                cells[point] = (first+y*width+x, 'U' if y==height-1 else 'u')
    return cells


def strip(plan):
    """Recover precisely the pre-dressing plan for historical preservation checks."""
    result = deepcopy(plan)
    if 'city_furniture' not in result:
        if any(token in result['legend'] for token in TOKENS):
            raise ValueError('Unregistered city furniture legend.')
        return result
    expected = [{'name':name,'x':x,'y':y} for name,x,y in PLACEMENTS]
    if result.pop('city_furniture') != expected or any(result['legend'].get(t)!=v for t,v in TOKENS.items()):
        raise ValueError('City furniture placement or collision declaration changed.')
    cells = footprint()
    for y,row in enumerate(result['rows']):
        updated = list(row)
        for x,token in enumerate(row):
            cell = cells.get((x,y))
            if (cell is not None and token!=cell[1]) or (cell is None and token in TOKENS):
                raise ValueError('City furniture token escaped its declared footprint.')
            if cell is not None:updated[x] = 'P'
        result['rows'][y] = ''.join(updated)
    for token in TOKENS:result['legend'].pop(token)
    return result


def decorate(plan):
    """Require existing paving and keep event tiles and door approaches clear."""
    if 'city_furniture' in plan:
        raise ValueError('City furniture is already installed.')
    result = deepcopy(plan);cells = footprint()
    protected = {(e['x'],e['y']) for kind in ('npcs','warp_events','bg_events') for e in plan[kind]}
    protected |= {(13,6),(13,7),(32,6),(32,7),(16,17)}
    protected |= {(x,y) for x in range(18,29) for y in range(2,7)}
    if protected & cells.keys():
        raise ValueError('City furniture covers a door, event or connected home.')
    for (x,y),(_,token) in cells.items():
        if not (0<x<len(plan['rows'][0])-1 and 0<y<len(plan['rows'])-1) or plan['rows'][y][x]!='P':
            raise ValueError('City furniture must occupy existing interior sidewalk.')
        row = result['rows'][y];result['rows'][y]=row[:x]+token+row[x+1:]
    result['legend'].update(deepcopy(TOKENS))
    result['city_furniture'] = [{'name':name,'x':x,'y':y} for name,x,y in PLACEMENTS]
    if strip(result)!=plan:
        raise ValueError('City dressing must preserve every unrelated source field.')
    return result


def tile(plan,x,y):
    if 'city_furniture' not in plan:return None
    cell = footprint().get((x,y))
    if cell is None:
        if plan['rows'][y][x] in TOKENS:raise ValueError('Unregistered city furniture cell.')
        return None
    record,token = cell
    if plan['rows'][y][x]!=token or plan['legend'].get(token)!=TOKENS[token]:
        raise ValueError('City furniture collision or elevation differs from its footprint.')
    return record
