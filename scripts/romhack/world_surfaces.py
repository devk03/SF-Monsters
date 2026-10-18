"""Original low-detail street materials, authored at native GBA pixel scale.

These are floor geometry, not rescaled illustrations. All use the neutral stone
palette and the lower layer so neither curbs nor tree wells cover the player.
"""
import struct


def stone_palette(original):
    colors = list(struct.unpack('<16H', original))
    for index, value in enumerate((25, 21, 18, 15, 11, 28), 3):
        colors[index] = value | value << 5 | value << 10
    return struct.pack('<16H', *colors)


def concrete():
    # Quiet foundation material. Large panel joints belong to the sidewalk
    # surface cards rather than being repeated beneath every building pixel.
    return bytes(3 if (x, y) in ((3, 11), (12, 4)) else 1
                 for y in range(16) for x in range(16))


def surfaces():
    def image(width, height, pixel):
        return bytes(pixel(x, y) for y in range(height) for x in range(width))

    return [
        ('slab_walk', 32, 32, image(32, 32, lambda x, y:
            3 if x == 31 or y == 31 else 8 if x == 0 or y == 0 else 1)),
        ('brick_walk', 32, 16, image(32, 16, lambda x, y:
            4 if y % 8 == 7 or (x + (8 if y < 8 else 0)) % 16 == 15
            else 3 if y % 8 == 0 else 1)),
        ('stone_walk', 32, 32, image(32, 32, lambda x, y:
            4 if y % 16 == 15 or (x + (16 if y < 16 else 0)) % 32 == 31
            else 3 if y % 16 == 0 else 1)),
        ('dark_walk', 16, 16, image(16, 16, lambda x, y:
            5 if y == 15 or x == 15 else 4)),
        ('curb_north', 16, 16, image(16, 16, lambda x, y:
            7 if y >= 14 else 5 if y >= 11 else 8 if y == 8
            else 3 if y >= 9 or x == 15 else 1)),
        ('curb_south', 16, 16, image(16, 16, lambda x, y:
            7 if y < 2 else 5 if y < 4 else 8 if y == 4
            else 3 if y == 5 or x == 15 else 1)),
        ('curb_cut', 16, 16, image(16, 16, lambda x, y:
            3 if y in (9, 12) and 2 <= x <= 13 else 1)),
        ('tree_well', 32, 32, image(32, 32, lambda x, y:
            1 if x < 3 or x > 28 or y < 3 or y > 28
            else 8 if x == 3 or y == 3 else 7 if x == 28 or y == 28
            else 6 if (x + y) % 7 == 0 else 5)),
    ]


# A neighborhood specifies materials and street use, not just a tint over the
# same checkerboard. The material strip is confined to the actual sidewalk.
DISTRICTS = {
    'dogpatch': ('slab_walk', 'dark_walk', 'workshop frontage and loading edge'),
    'potrero_hill': ('slab_walk', 'stone_walk', 'hill homes and stair landing'),
    'mission': ('brick_walk', 'dark_walk', 'continuous shops and mural walk'),
    'castro': ('stone_walk', 'brick_walk', 'theater forecourt and shopfronts'),
    'outer_sunset': ('slab_walk', 'slab_walk', 'low homes and ocean promenade'),
    'marina': ('slab_walk', 'stone_walk', 'bar strip and planted residential walk'),
    'pacific_heights': ('stone_walk', 'dark_walk', 'formal attached homes and stone thresholds'),
    'noe_valley': ('slab_walk', 'brick_walk', 'small shops and residential tree wells'),
    'mission_bay': ('stone_walk', 'slab_walk', 'lab blocks and broad accessible crossings'),
    'giants_stadium': ('brick_walk', 'dark_walk', 'ballpark queue and fan promenade'),
    'financial_district': ('dark_walk', 'stone_walk', 'office canyon and granite entries'),
    'north_beach': ('brick_walk', 'stone_walk', 'cafe pavement and theater corner'),
    'treasure_island': ('slab_walk', 'dark_walk', 'working waterfront and utility apron'),
}
