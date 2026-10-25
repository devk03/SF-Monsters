"""Authored block envelopes translated from the expanded neighborhood concepts.

Each envelope owns a short attached street wall and an optional second wall
around a shared back court. Stable northwest services remain outside this pass.
"""

BLOCKS = {
    'dogpatch': [
        (34,1,42,9,'rail-side lofts'), (50,1,62,9,'workshop roofs'),
        (69,1,79,9,'quay stores'), (37,17,42,28,'narrow repair lane'),
        (69,17,72,29,'dock workshops'), (4,27,12,43,'railway terraces'),
        (20,37,42,47,'converted warehouse court'),
        (50,37,62,47,'makers court'), (69,37,72,47,'waterfront trades'),
        (4,49,12,60,'south rail homes'), (20,54,42,61,'coffee and homes'),
        (50,54,62,61,'south workshops'), (69,54,78,61,'pier neighborhood'),
    ],
}


def frontage_bands(identifier):
    """Finite individually sized wall runs; never a full-width filler stripe."""
    if identifier not in BLOCKS:
        return None
    bands = set()
    for left, top, right, bottom, _ in BLOCKS[identifier]:
        bands.add((left, right+1, top))
        if bottom-top>=10:
            bands.add((left, right+1, bottom-4))
    return bands


def mark_composition(plan):
    if plan['world_id'] in BLOCKS:
        plan['concept_blocks'] = [dict(bounds=list(b[:4]), purpose=b[4])
                                  for b in BLOCKS[plan['world_id']]]


def furnish_ground(plan, grid, stamp, token):
    if plan['world_id'] != 'dogpatch':
        return
    # A real service lane links the workshop backs to the southern coffee/home
    # court. It occupies the narrow interval between attached block envelopes.
    from world_district_layouts import raster_path
    paths = [[(16,36),(16,60)], [(16,58),(42,58)]]
    for line in paths:
        for x,y in raster_path(line,radius=0):
            if not plan['legend'][grid[y][x]][1]:
                grid[y][x]=token('slab_walk',x,y)
    for style,x,y in [('street_tree',13,44),('bench',17,60),('lamp',18,46)]:
        if stamp(style,x,y,shoulder=True):
            plan.setdefault('expanded_details',[]).append(dict(name=style,x=x,y=y))
    plan.setdefault('scenic_viewpoints',[]).extend([
        dict(name='Workshop service lane',x=16,y=48),
        dict(name='Eastern working pier',x=88,y=22),
        dict(name='Southern working pier',x=88,y=42),
    ])
