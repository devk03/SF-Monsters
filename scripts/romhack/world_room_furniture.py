"""Original, native-scale room furniture in the existing apartment palette."""


def cards():
    def canvas(width, height):
        pixels = bytearray(width * height)

        def rect(x, y, w, h, ink):
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    pixels[yy * width + xx] = ink
        return pixels, rect

    pixels, rect = canvas(32, 16)
    rect(7, 10, 3, 5, 14); rect(23, 10, 3, 5, 14)
    for y, inset in enumerate((8, 4, 2, 1, 0, 0, 1, 2, 4, 8)):
        rect(inset + 1, y + 1, 30 - inset * 2, 1, 12)
        if y < 8:
            rect(inset + 2, y + 1, 28 - inset * 2, 1, 3 if y < 2 else 5)
    rect(13, 3, 5, 3, 1); rect(18, 4, 2, 1, 4)  # A cup, not a new interaction.
    yield 'round_table', 32, 16, bytes(pixels)

    pixels, rect = canvas(32, 16)
    rect(2, 2, 28, 8, 14); rect(3, 3, 26, 2, 3)
    rect(3, 6, 26, 2, 5); rect(1, 9, 30, 4, 12)
    rect(2, 9, 28, 2, 3); rect(4, 13, 3, 3, 14)
    rect(25, 13, 3, 3, 14)
    yield 'waiting_bench', 32, 16, bytes(pixels)

    pixels, rect = canvas(32, 16)
    rect(1, 0, 30, 15, 12); rect(2, 1, 28, 12, 2)
    for x in range(4, 29, 4):
        for y in range(3, 12, 4):
            rect(x, y, 1, 1, 4)
    rect(5, 3, 2, 8, 14); rect(3, 3, 6, 2, 11)
    rect(14, 4, 2, 7, 11); rect(12, 2, 6, 3, 14)
    rect(24, 3, 2, 8, 9); rect(22, 2, 6, 3, 11)
    yield 'tool_board', 32, 16, bytes(pixels)

    pixels, rect = canvas(16, 32)
    rect(7, 23, 2, 8, 14); rect(3, 30, 10, 2, 12)
    rect(1, 1, 14, 24, 14); rect(2, 2, 12, 21, 4)
    rect(3, 3, 10, 18, 1); rect(4, 4, 8, 3, 11)
    for y in (10, 13, 16):
        rect(4, y, 7 if y != 13 else 5, 1, 8)
    yield 'information_board', 16, 32, bytes(pixels)

    pixels, rect = canvas(16, 16)
    rect(3, 2, 10, 7, 14); rect(4, 3, 8, 4, 3)
    rect(2, 8, 12, 4, 12); rect(3, 8, 10, 2, 5)
    rect(3, 12, 2, 4, 14); rect(11, 12, 2, 4, 14)
    yield 'room_chair', 16, 16, bytes(pixels)
