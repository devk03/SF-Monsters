"""Build-only solid civic anchor derived from verified pinned native graphics.

This scenic facade has no entrance or inherited collision/warp behavior. Native
pixels remain in memory; the calling world compiler supplies its own palette.
"""
import io
import struct
from functools import lru_cache

from world_native_loft import HASHES, PREFIX, checked_blobs

# Reviewed material roles in the existing SF civic palette; zero is transparent.
CIVIC = (0, 5, 5, 12, 6, 3, 2, 4, 1, 5, 12, 5, 5, 6, 6, 12)


@lru_cache(maxsize=4)
def anchor(root):
    """Return a 160x128 indexed scenic card, sourced from pinned Git objects."""
    from PIL import Image

    blobs = checked_blobs(root, {
        'data/layouts/RustboroCity/map.bin': HASHES['data/layouts/RustboroCity/map.bin'],
        PREFIX + 'metatiles.bin': HASHES[PREFIX + 'metatiles.bin'],
        PREFIX + 'tiles.png': HASHES[PREFIX + 'tiles.png'],
    })
    tiles = Image.open(io.BytesIO(blobs[PREFIX + 'tiles.png']))
    layout = blobs['data/layouts/RustboroCity/map.bin']
    records = blobs[PREFIX + 'metatiles.bin']
    width, height = 160, 128
    pixels = bytearray(width * height)
    for cy in range(8):
        for cx in range(10):
            identifier = struct.unpack_from('<H', layout, 2 * ((cy + 7) * 40 + cx + 7))[0] & 1023
            if not 512 <= identifier < 512 + len(records) // 16:
                raise ValueError('Native anchor selected an unexpected primary record')
            for quadrant, word in enumerate(struct.unpack_from('<8H', records, (identifier - 512) * 16)):
                slot, bank = word & 1023, word >> 12
                # The source includes ground behind this architecture. Exclude it;
                # only the reviewed secondary civic bank belongs to the card.
                if slot < 512 or bank != 11:
                    continue
                local = slot - 512
                for y in range(8):
                    for x in range(8):
                        sx = local % 16 * 8 + (7 - x if word & 0x400 else x)
                        sy = local // 16 * 8 + (7 - y if word & 0x800 else y)
                        index = tiles.getpixel((sx, sy))
                        if index:
                            dx = cx * 16 + quadrant % 2 * 8 + x
                            dy = cy * 16 + (quadrant % 4 // 2) * 8 + y
                            pixels[dy * width + dx] = CIVIC[index]

    # Replace the removed roof emblem with neighboring intact roof masonry.
    for y in range(32, 48):
        for x in range(72, 88):
            pixels[y * width + x] = pixels[y * width + 56 + (x - 72) % 8]

    # The original central entrance is deliberately replaced by a continuous
    # solid wall: repeat an intact side bay's small windows and masonry base.
    # Copying the complete 16-pixel band keeps sill and footing aligned.
    for y in range(112, 128):
        for x in range(48, 112):
            pixels[y * width + x] = pixels[y * width + 8 + (x - 48) % 32]
    return width, height, bytes(pixels)
