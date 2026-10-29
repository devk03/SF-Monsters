"""Extend the northern North Beach street wall beside its reading court.

This is one frontage segment; the wider district remains unfinished.
"""

# Nine contiguous tiles terminate against the existing (70, 1) street wall.
FRONTAGE = (('shophouse', 61, 1), ('arcade__slate', 63, 1),
            ('flats', 66, 1), ('shophouse__sage', 68, 1))
COURT_EVENT = (59, 4)
COURT_CHECKPOINT = (58, 4)
# Court paving connects its south side to the existing north/south sidewalk.
PAVING = (55, 5, 65, 12)  # half-open rectangle


def _cells(cards):
    cells = set()
    for style, x, y in FRONTAGE:
        card = cards[style]
        if not card.get('architecture_type'):
            raise ValueError('North Beach candidate requires architecture: ' + style)
        for dy, row in enumerate(card['tiles']):
            for dx, _ in enumerate(row):
                cells.add((x + dx, y + dy))
    return cells


def deferred_cells(identifier, cards):
    """Reserve the wall only after the existing court has been proposed."""
    return _cells(cards) if identifier == 'north_beach' else set()


def furnish(plan, stamp, grid, token, lanes, occupied, cards):
    """Add candidate wall and walkable court paving; preserve events/fixtures."""
    if plan['world_id'] != 'north_beach':
        return
    events = {(e['x'], e['y']) for e in plan.get('bg_events', [])}
    checkpoints = {(e['x'], e['y']) for e in plan.get('access_points', [])}
    if COURT_EVENT not in events or COURT_CHECKPOINT not in checkpoints:
        raise ValueError('North Beach reading court binding changed')
    wall = _cells(cards)
    if wall & (set(occupied) | set(lanes) | events | checkpoints):
        raise ValueError('North Beach candidate wall conflicts with existing features')
    # Ensure card dimensions and attachment to the existing east facade before
    # making changes. The caller's final edge pass selects real end caps.
    edge = 61
    for style, x, y in FRONTAGE:
        rows = cards[style]['tiles']
        if x != edge or y != 1 or len(rows) != 4 or not rows or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError('North Beach candidate wall dimensions changed')
        edge += len(rows[0])
    if edge != 70 or not any(b['x'] == 70 and b['y'] == 1 and b['height'] == 4
                             and cards[b['style']].get('architecture_type')
                             for b in plan['town_blocks']):
        raise ValueError('North Beach candidate requires its eastern party wall')
    # Stamp performs its own frontage, road, parcel and existing occupancy checks.
    # Integration must discard the entire candidate if any stamp is rejected.
    for style, x, y in FRONTAGE:
        if not stamp(style, x, y, shoulder=True, parcel=True):
            raise ValueError('North Beach candidate cannot stamp ' + style)
    left, top, right, bottom = PAVING
    protected = set(occupied) | set(lanes)
    for y in range(top, bottom):
        for x in range(left, right):
            if (x, y) not in protected and not plan['legend'][grid[y][x]][1]:
                grid[y][x] = token('brick_walk', x, y)
