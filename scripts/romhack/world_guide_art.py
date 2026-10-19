"""Original, native-resolution SF region relief, compiled to tiled GBA4bpp.

No reference pixels are read. Geography/landmarks are authored here; towns and
corridors are supplied by the real world graph. The result fits one16color bank.
"""
from PIL import Image, ImageDraw

PALETTE = [
    (0, 0, 0), (31, 31, 29), (5, 10, 14), (25, 29, 23),
    (12, 21, 30), (17, 25, 31), (24, 30, 10), (15, 25, 7),
    (5, 17, 8), (30, 27, 13), (21, 15, 5), (31, 24, 7),
    (8, 16, 26), (10, 25, 30), (29, 9, 5), (31, 29, 18),
]
COAST = [(28, 37), (38, 31), (48, 31), (60, 34), (72, 31),
         (84, 32), (98, 29), (112, 28), (128, 32), (142, 36),
         (151, 44), (155, 55), (157, 72), (164, 85), (160, 100),
         (155, 119), (39, 119), (34, 109), (30, 92), (31, 73), (28, 56)]
ANGEL = [(161, 26), (166, 21), (177, 20), (187, 25), (188, 30),
         (181, 35), (166, 34)]
TREASURE = [(163, 58), (177, 54), (185, 56), (190, 64), (185, 71),
            (172, 73), (161, 68)]


def terrain():
    image = Image.new('P', (224, 104), 4)
    image.putpalette([v * 255 // 31 for color in PALETTE for v in color] + [0] * (768 - 48))
    draw = ImageDraw.Draw(image)
    # Every coordinate in the chart is a native window pixel; bitmap begins y16.
    def polygon(points, color):
        draw.polygon([(x, y - 16) for x, y in points], fill=color)
    def line(points, color, width=1):
        draw.line([(x, y - 16) for x, y in points], fill=color, width=width)
    # Restrained horizontal wave bands; darker navigable bay water is distinct.
    for y in range(0, 104, 3):
        draw.line((0, y, 223, y), fill=5)
    polygon([(149, 35), (204, 35), (204, 116), (161, 116), (160, 79)], 12)
    for y in range(24, 104, 3):
        draw.line((160, y, 203, y), fill=4)
    land = Image.new('1', image.size)
    mask = ImageDraw.Draw(land)
    polygons = [COAST, ANGEL, TREASURE]
    for points in polygons:
        mask.polygon([(x, y - 16) for x, y in points], fill=1)
    # Shallow water, sandy coastal lip, dark coastal foliage, then bright land.
    for x in range(1, 223):
        for y in range(1, 103):
            if land.getpixel((x, y)):
                if any(not land.getpixel((x + dx, y + dy)) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                    image.putpixel((x, y), 9)
                elif any(not land.getpixel((min(223, max(0, x + dx)), min(103, max(0, y + dy))))
                         for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2))):
                    image.putpixel((x, y), 8)
                else:
                    image.putpixel((x, y), 6)
            elif any(land.getpixel((x + dx, y + dy)) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                image.putpixel((x, y), 5)
    # Western ridges and parks: stepped contour patches, with deliberate shapes.
    relief = [([(34, 41), (43, 35), (64, 37), (78, 43), (70, 49), (41, 48)], 8),
              ([(37, 41), (45, 37), (61, 39), (70, 43), (65, 46), (42, 46)], 7),
              ([(38, 53), (77, 53), (84, 57), (78, 63), (37, 63), (33, 59)], 8),
              ([(38, 55), (75, 55), (79, 58), (75, 61), (38, 61)], 7),
              ([(42, 68), (55, 65), (64, 72), (69, 84), (65, 98), (53, 104), (41, 96), (39, 80)], 7),
              ([(48, 71), (55, 70), (59, 76), (61, 89), (57, 97), (47, 94), (44, 82)], 8),
              ([(50, 75), (55, 75), (57, 82), (55, 91), (49, 90), (47, 81)], 6),
              ([(66, 80), (75, 76), (83, 82), (84, 92), (76, 103), (65, 101), (61, 91)], 7),
              ([(69, 83), (75, 80), (80, 85), (79, 93), (72, 98), (65, 92)], 8),
              ([(71, 85), (75, 83), (77, 88), (73, 94), (68, 91)], 6),
              ([(94, 35), (111, 32), (127, 36), (128, 43), (119, 47), (99, 43)], 7)]
    for points, color in relief:
        polygon(points, color)
    # Built-up eastern neighborhoods: broad terraces, not a repeated street grid.
    polygon([(91, 51), (128, 45), (144, 49), (148, 64), (143, 75),
             (151, 85), (148, 108), (120, 112), (89, 105), (85, 88)], 3)
    polygon([(94, 56), (124, 50), (140, 53), (140, 69), (134, 78),
             (141, 91), (141, 105), (113, 107), (94, 99), (91, 82)], 6)
    # Island contours retain separate silhouettes and a small western ridge.
    polygon([(166, 26), (171, 23), (178, 23), (183, 27), (179, 31), (168, 30)], 7)
    polygon([(168, 60), (177, 58), (183, 61), (184, 65), (177, 68), (167, 65)], 7)
    polygon([(171, 61), (177, 60), (180, 63), (177, 66), (171, 65)], 6)
    # Marin shore beyond the strait is background geography, never a destination.
    polygon([(24, 16), (75, 16), (73, 20), (63, 23), (49, 21), (37, 24), (26, 21)], 8)
    polygon([(27, 16), (69, 16), (66, 19), (53, 18), (39, 21), (29, 19)], 7)
    # Original tiny Golden Gate span, red towers and pale suspended deck.
    line([(43, 22), (46, 33)], 2, 3)
    line([(43, 22), (46, 33)], 1)
    line([(41, 21), (44, 21), (47, 25), (44, 25), (41, 21)], 14)
    line([(44, 29), (48, 29), (49, 33), (45, 33), (44, 29)], 14)
    # Quiet highlights through the park and forest canopy.
    for x, y in [(42, 41), (49, 40), (59, 43), (41, 57), (49, 58), (68, 57), (53, 84)]:
        line([(x, y), (x + 1, y - 1), (x + 2, y)], 6)
    return image


def tiled_bytes(image):
    width, height = image.size
    if width % 8 or height % 8:
        raise ValueError('Region image must fill complete native tiles')
    out = bytearray()
    for top in range(0, height, 8):
        for left in range(0, width, 8):
            for y in range(8):
                for x in range(0, 8, 2):
                    a, b = image.getpixel((left + x, top + y)), image.getpixel((left + x + 1, top + y))
                    if not 0 <= a < 16 or not 0 <= b < 16:
                        raise ValueError('Region artwork exceeds one native palette bank')
                    out.append(a | b << 4)
    return bytes(out)


def compile_art():
    raw = tiled_bytes(terrain())
    palette = ', '.join('RGB' + str(color).replace(' ', '') for color in PALETTE)
    rows = ['    ' + ','.join(hex(v) for v in raw[n:n + 24]) for n in range(0, len(raw), 24)]
    return ('// Original SF region relief; generated from world_guide_art.py.\n'
            'static const u16 sSFGuidePalette[16] = {' + palette + '};\n'
            'static const u8 sSFGuideRelief[] = {\n' + ',\n'.join(rows) + '\n};\n')
