"""Close genuine street-facing gaps in North Beach's eastern blocks."""

ROWS=(
    # These two buildings connect previously separated northern street walls.
    (1,(('shophouse__sage',81),('flats__slate',83))),
    # The following rows face existing east and south streets. Their ends stop
    # inside the map, with two clear approach rows below each frontage.
    (23,(('arcade',85),('shophouse__sage',88),('walkup__slate',90),('flats',93))),
    (45,(('duplex__sage',85),('flats',88),('arcade__slate',90),('shophouse',93))),
)


def reserved_cells(identifier,cards):
    if identifier!='north_beach':return set()
    return {(x+dx,y+dy) for y,row in ROWS for style,x in row
            for dy,tiles in enumerate(cards[style]['tiles']) for dx in range(len(tiles))}


def furnish(stamp,grid,token,lanes,cards):
    for y,row in ROWS:
        for style,x in row:
            if not stamp(style,x,y,shoulder=True,parcel=True):
                raise ValueError('North Beach street frontage conflicts at '+str((style,x,y)))
            # Join every storefront to the surrounding sidewalk, without
            # covering road lanes. Stamp already checked these approach cells.
            width=len(cards[style]['tiles'][0]);bottom=y+len(cards[style]['tiles'])
            for yy in (bottom,bottom+1):
                for xx in range(x,x+width):
                    if (xx,yy) not in lanes:grid[yy][xx]=token('brick_walk',xx,yy)
