"""Authored block envelopes translated from the expanded neighborhood concepts.

Each envelope owns a short attached street wall and an optional second wall
around a shared back court. Stable northwest services remain outside this pass.
"""

BLOCKS = {
    'presidio': [
        (35,1,53,8,'western officers housing'), (59,1,74,8,'forest-edge residences'),
        (39,17,47,20,'visitor-center neighborhood'), (53,17,65,20,'campus workshops'),
        (38,40,55,46,'southern campus homes'), (62,40,72,46,'eastern garden homes'),
        (30,55,42,61,'southwestern homes'), (50,55,70,61,'south campus shops'),
    ],
    'dogpatch': [
        (34,1,42,9,'rail-side lofts'), (50,1,62,9,'workshop roofs'),
        (69,1,79,9,'quay stores'), (37,17,42,28,'narrow repair lane'),
        (69,17,72,29,'dock workshops'), (4,27,12,43,'railway terraces'),
        (20,37,42,47,'converted warehouse court'),
        (50,37,62,47,'makers court'), (69,37,72,47,'waterfront trades'),
        (4,49,12,60,'south rail homes'), (20,54,42,61,'coffee and homes'),
        (50,54,62,61,'south workshops'), (69,54,78,61,'pier neighborhood'),
    ],
    'potrero_hill': [
        (82,18,92,22,'east stair landing homes'),
        (82,43,92,47,'lower east terrace homes'),
        (34,1,43,9,'upper hill homes'), (46,2,54,20,'stair-side flats'),
        (60,2,74,20,'hill garden homes'), (81,5,92,21,'east overlook homes'),
        (4,27,18,42,'west terraces'), (28,31,50,42,'lower stair neighborhood'),
        (60,31,72,42,'hilltop shops'), (81,29,92,43,'east homes'),
        (29,50,50,54,'corner grocery'), (60,50,74,54,'coffee and homes'),
        (4,49,18,60,'lower work-live studios'),
    ],
    'mission': [
        (4,55,12,61,'southwest corner homes'),
        (34,1,56,8,'upper mixed-use block'), (66,1,82,8,'north corner shops'),
        (19,25,34,28,'mural lane homes'), (66,17,82,28,'market and music court'),
        (19,37,34,48,'west community block'), (42,37,58,48,'studio back courts'),
        (66,37,82,48,'garden neighborhood'), (4,40,12,55,'western homes'),
        (20,57,34,61,'south storefronts'), (42,57,58,61,'south apartments'),
        (66,57,82,61,'south shops'),
    ],
    'castro': [
        (85,1,93,20,'eastern hillside terraces'),
        (69,8,77,21,'upper garden mews'), (4,48,17,60,'west garden street'),
        (34,1,43,21,'upper hillside homes'), (52,1,60,13,'coffee corner'),
        (69,1,81,21,'upper flower-shop block'), (52,18,60,27,'theater approach'),
        (27,37,43,46,'west shop courts'), (52,37,62,46,'east cafe court'),
        (68,37,78,46,'bar and bookshop'), (4,29,17,45,'west garden flats'),
        (27,55,43,61,'southern bay homes'), (52,55,66,61,'southern shops'),
        (70,55,88,61,'quiet residential lane'),
    ],
    'outer_sunset': [
        (34,1,56,8,'north surf neighborhood'), (68,1,80,8,'north cottages'),
        (20,17,36,28,'dune-side homes'), (44,17,60,28,'bakery block'),
        (68,17,80,28,'laundry and cafe block'), (20,37,36,48,'beach neighborhood'),
        (44,37,60,48,'inner sunset court'), (68,37,80,48,'east cottage block'),
        (20,57,36,61,'south coastal homes'), (44,57,60,61,'south shops'),
        (68,57,80,61,'south cottages'),
    ],
    'marina': [
        (4,39,12,49,'western bar corner'), (4,52,12,61,'western apartment lane'),
        (34,5,56,8,'harbor-front flats'), (64,5,80,8,'harbor clubhouse block'),
        (40,17,56,34,'bar and courtyard block'), (64,17,80,34,'coastal flats'),
        (4,27,30,34,'west residential court'), (20,43,32,50,'west bars'),
        (40,43,56,50,'late-night cafe block'), (64,43,80,50,'east bar block'),
        (20,59,32,61,'south homes'), (40,59,56,61,'south flats'),
        (64,59,80,61,'south corner stores'),
    ],
    'pacific_heights': [
        (85,1,93,22,'eastern ridge homes'), (67,10,78,23,'upper courtyard homes'),
        (4,34,15,47,'western garden apartments'), (4,51,15,61,'western market corner'),
        (34,1,40,23,'west stair homes'), (49,2,58,23,'formal garden homes'),
        (66,3,79,23,'upper stone apartments'), (4,28,16,48,'west formal homes'),
        (25,39,40,50,'mansion neighborhood'), (49,35,58,50,'central garden flats'),
        (66,35,78,50,'east formal block'), (25,59,40,61,'lower corner market'),
        (49,59,58,61,'flower-shop block'), (66,59,80,61,'lower quiet homes'),
    ],
    'noe_valley': [
        (85,15,93,29,'eastern family street'), (85,38,93,50,'eastern garden mews'),
        (85,54,93,61,'southeast homes'), (4,47,17,61,'western cottage lane'),
        (34,1,54,8,'upper quiet homes'), (60,1,74,8,'upper corner stores'),
        (20,17,38,28,'bookshop neighborhood'), (46,17,74,28,'bakery and garden block'),
        (26,37,38,44,'west family homes'), (46,37,54,44,'repair cafe court'),
        (62,37,74,44,'east homes'), (4,29,17,44,'western cottages'),
        (26,53,50,61,'south playground block'), (63,53,80,61,'south domestic lane'),
    ],
    'mission_bay': [
        (34,1,56,8,'north transit labs'), (64,1,76,8,'north civic block'),
        (44,17,56,28,'research courtyard'), (64,17,76,28,'clinic and lab court'),
        (44,37,56,48,'south research block'), (64,37,76,48,'waterfront offices'),
        (4,28,34,44,'west mixed-use block'), (4,49,34,56,'food and transit block'),
        (44,57,56,59,'south promenade shops'),
    ],
    'giants_stadium': [
        (61,8,80,21,'brick ballpark frontage'), (4,47,12,61,'western warehouse lane'),
        (34,1,60,8,'north warehouse homes'), (66,1,80,8,'north fan stores'),
        (20,17,38,24,'west guest-services block'), (46,17,62,24,'pub and souvenir block'),
        (68,17,80,24,'east ballpark neighborhood'), (20,33,38,46,'west brick courts'),
        (46,55,60,60,'southern food street'), (69,55,80,60,'southern fan neighborhood'),
        (4,29,12,44,'west converted warehouses'),
    ],
    'financial_district': [
        (4,56,12,61,'southwest transit storefronts'),
        (4,26,12,39,'western stone offices'), (4,42,12,52,'western lunch counters'),
        (34,1,56,8,'north office block'), (64,1,82,8,'north bank block'),
        (40,17,56,28,'office canyon court'), (64,17,82,28,'eastern lunch block'),
        (20,37,32,50,'west commercial block'), (40,37,56,50,'redwood plaza block'),
        (64,37,82,50,'east office block'), (20,59,32,61,'south cafes'),
        (40,59,56,61,'south stone offices'), (64,59,82,61,'south transit block'),
    ],
    'north_beach': [
        (85,1,93,22,'eastern hill neighborhood'), (71,9,81,21,'upper cafe mews'),
        (4,49,17,61,'western bookshop lane'),
        (34,1,60,8,'upper Italianate homes'), (70,1,82,8,'upper hill flats'),
        (36,17,43,28,'stair alley shops'), (52,17,61,28,'cafe and music block'),
        (26,37,43,48,'west bookshop lanes'), (52,37,61,48,'central cafe court'),
        (66,37,78,48,'eastern trattoria block'), (4,29,17,46,'west garden homes'),
        (26,57,43,61,'southern shops'), (52,57,66,61,'southern homes'),
        (70,57,86,61,'east flower-shop corner'),
    ],
    'treasure_island': [
        (63,23,75,26,'north yard workshop fronts'),
        (34,7,54,8,'north former barracks'), (62,7,75,8,'north workshops'),
        (20,17,35,26,'western housing court'), (40,17,54,26,'community gardens block'),
        (62,17,75,26,'north industrial yard'), (20,35,35,48,'west sheltered homes'),
        (40,35,54,48,'island repair block'), (62,35,75,48,'terminal and workshops'),
        (20,56,35,58,'south ferry neighborhood'), (40,56,54,58,'south utility block'),
        (62,56,75,58,'south quay stores'),
    ],
}


def frontage_bands(identifier):
    """Finite individually sized wall runs; never a full-width filler stripe."""
    if identifier not in BLOCKS:
        return None
    bands = set()
    for left, top, right, bottom, _ in BLOCKS[identifier]:
        bands.add((left, right+1, top))
        # Deep parcels have a second mews, rather than two distant walls with
        # an unused lawn between them. Each four-row house retains two clear
        # frontage rows; the final attachment pass supplies the actual caps.
        for inner in range(top+7,bottom-2,7):
            bands.add((left,right+1,inner))
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
