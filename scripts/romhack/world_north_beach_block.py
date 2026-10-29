"""Extend the northern North Beach street wall beside its reading court.

This is one frontage segment; the wider district remains unfinished.
"""

# Nine contiguous tiles terminate against the existing (70, 1) street wall.
FRONTAGE = (('arcade__slate', 55, 1), ('duplex__sage', 58, 1),
            ('shophouse', 61, 1), ('arcade__slate', 63, 1),
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
    return {(x, y) for x, y in _cells(cards) if x >= 61} if identifier == 'north_beach' else set()


def furnish(plan, stamp, grid, token, lanes, occupied, cards, passage_cells):
    """Add candidate wall and walkable court paving; preserve events/fixtures."""
    if plan['world_id'] != 'north_beach':
        return
    # The original court is proposed before packing. Relocate its fixture only
    # afterwards so that changing this block cannot perturb other frontages.
    def exactly_one(items, predicate, label):
        matches = [item for item in items if predicate(item)]
        if len(matches) != 1:
            raise ValueError('North Beach reading court ' + label + ' changed')
        return matches[0]

    script = 'WBCourt_north_beach_0'
    fixture = exactly_one(plan['town_blocks'], lambda b: b['style'] == 'flower_box'
                          and (b['x'], b['y']) == COURT_EVENT, 'fixture')
    event = exactly_one(plan['bg_events'], lambda e: e.get('script') == script
                        and (e['x'], e['y']) == COURT_EVENT, 'event')
    checkpoint = exactly_one(plan['access_points'], lambda e: e.get('name') == 'pedestrian_court_0'
                             and (e['x'], e['y']) == COURT_CHECKPOINT, 'checkpoint')
    viewpoint = exactly_one(plan['scenic_viewpoints'], lambda e: e['name'] == 'Planted pedestrian court 1'
                            and (e['x'], e['y']) == COURT_CHECKPOINT, 'viewpoint')
    notice = exactly_one(plan['court_notices'], lambda e: e['script'] == script
                         and e['object'] == [59, 4] and e['standing'] == [58, 4], 'notice')
    court = exactly_one(plan['pedestrian_courts'], lambda e: e['zone'] == 0
                        and e['x'] == 57 and e['top'] == 6 and e['rest'] == [58, 4], 'footprint')
    old_passage = {(x, y) for x in range(57, 60) for y in range(3, 12)}
    nook = {(x, y) for x in range(57, 60) for y in range(7, 10)}
    actors = {(n['x'] + dx, n['y'] + dy) for n in plan['npcs']
              for dx in range(-n.get('range_x', 0), n.get('range_x', 0) + 1)
              for dy in range(-n.get('range_y', 0), n.get('range_y', 0) + 1)}
    if (event.get('type') != 'sign' or event.get('player_facing_dir') != 'BG_EVENT_PLAYER_FACING_ANY'
            or checkpoint.get('activation') != 'interact' or fixture['width'] != 1 or fixture['height'] != 1):
        raise ValueError('North Beach reading court semantics changed')
    if not old_passage <= passage_cells or COURT_EVENT not in occupied:
        raise ValueError('North Beach reading court reservation changed')
    event_cells = {(e['x'], e['y']) for e in plan['bg_events']}
    access_cells = {(e['x'], e['y']) for e in plan['access_points']}
    if nook & (set(lanes) | set(occupied) | actors | event_cells | access_cells):
        raise ValueError('North Beach reading nook conflicts with street or actors')
    if any(plan['legend'][grid[y][x]][1] for x, y in nook):
        raise ValueError('North Beach reading nook is not walkable')
    plan['town_blocks'].remove(fixture)
    occupied.remove(COURT_EVENT)
    passage_cells.difference_update(old_passage)
    grid[4][59] = token('brick_walk', 59, 4)
    if not stamp('flower_box', 59, 8, passage=True):
        raise ValueError('North Beach reading nook fixture cannot fit')
    event['y'] = checkpoint['y'] = viewpoint['y'] = 8
    notice['object'] = [59, 8]
    notice['standing'] = [58, 8]
    court.clear()
    court.update(zone=0, kind='nook', bounds=[57, 7, 59, 9], rest=[58, 8])

    events = {(e['x'], e['y']) for e in plan.get('bg_events', [])}
    checkpoints = {(e['x'], e['y']) for e in plan.get('access_points', [])}
    if (59, 8) not in events or (58, 8) not in checkpoints:
        raise ValueError('North Beach reading court binding changed')
    wall = _cells(cards)
    if wall & (set(occupied) | set(lanes) | events | checkpoints):
        raise ValueError('North Beach candidate wall conflicts with existing features')
    # Ensure card dimensions and attachment to the existing east facade before
    # making changes. The caller's final edge pass selects real end caps.
    edge = 55
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
