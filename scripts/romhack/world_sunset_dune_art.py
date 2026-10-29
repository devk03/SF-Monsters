"""Original transparent dune-grass overlays for Outer Sunset.

Each 16x16 indexed image uses palette 7: 0 is transparent and 9–11 are
existing botanical greens. The caller supplies the pinned General 0x124 sand
lower layer and selects collision/behavior; these pixels contain no sand art.
"""


def cards():
    """Return three sparse, independently placeable 16x16 pixel overlays."""
    patterns = (
        ((5, 11, -3, -5), (7, 11, -1, -7), (8, 11, 2, -6), (9, 11, 4, -4)),
        ((9, 12, -4, -4), (10, 12, -2, -7), (11, 12, 1, -6), (12, 12, 2, -3)),
        ((4, 12, -2, -4), (5, 12, 0, -6), (6, 12, 3, -5),
         (11, 10, -1, -3), (12, 10, 1, -4)),
    )
    result = []
    for index, blades in enumerate(patterns, 1):
        pixels = bytearray(256)
        for blade_index, (x, y, dx, dy) in enumerate(blades):
            steps = max(abs(dx), abs(dy))
            color = (9, 10, 11)[blade_index % 3]
            for step in range(steps + 1):
                px = round(x + dx * step / steps)
                py = round(y + dy * step / steps)
                pixels[py * 16 + px] = color
        result.append((f'dune_grass_{index}', bytes(pixels)))
    return tuple(result)
