"""Original native-pixel service emblems; no new palette or collision footprint."""

# Each board is drawn on a transparent sidewalk underlay. Cream and navy are
# existing terrain-bank colors, so adding these signs cannot recolor the park.
GYM = (
    '0000000000000000',
    '000dddddddddd000',
    '000d11111111d000',
    '000d11111111d000',
    '000d11d11d11d000',
    '000d1d1111d1d000',
    '000dd111111dd000',
    '000d1d1111d1d000',
    '000d11d11d11d000',
    '000d11111111d000',
    '000dddddddddd000',
    '0000d000000d0000',
    '0000d000000d0000',
    '0000d000000d0000',
    '0000000000000000',
    '0000000000000000',
)
CLINIC = (
    '0000000000000000',
    '000dddddddddd000',
    '000d11111111d000',
    '000d11111111d000',
    '000d1dd11dd1d000',
    '000dddddddddd000',
    '000dddddddddd000',
    '000d1dddddd1d000',
    '000d11dddd11d000',
    '000d111dd111d000',
    '000dddddddddd000',
    '0000d000000d0000',
    '0000d000000d0000',
    '0000d000000d0000',
    '0000000000000000',
    '0000000000000000',
)


def sign_cells():
    """Two appended16x16 metatiles, with palette0 revealing existing paving."""
    cells = []
    for rows in (GYM, CLINIC):
        if len(rows) != 16 or any(len(row) != 16 or set(row) - set('01d') for row in rows):
            raise ValueError('Service signs require16x16 transparent/cream/navy pixels.')
        cells.append((bytes(int(value, 16) for row in rows for value in row), 7))
    return cells
