"""Native title silhouette for the spec's Bayveil; not a campaign acquisition."""
import hashlib
import json
from pathlib import Path
import struct
from native_resources import apply_resources
from title_art import tiles8

ASSET = 'assets/ui/title-bayveil'


def pack4(pixels):
    if len(pixels) % 2 or any(value > 15 for value in pixels):
        raise ValueError('Four-bit graphics need paired native palette indices.')
    return bytes(pixels[i] | pixels[i + 1] << 4 for i in range(0, len(pixels), 2))


def eye_clusters(pixels, width, height):
    remaining = {index for index, color in enumerate(pixels) if color == 15}
    clusters = []
    while remaining:
        pending, points = [min(remaining)], []
        while pending:
            index = pending.pop()
            if index not in remaining:
                continue
            remaining.remove(index)
            x, y = index % width, index // width
            points.append((x, y))
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height and ny * width + nx in remaining:
                    pending.append(ny * width + nx)
        clusters.append({'pixels': len(points), 'bounds': [min(x for x, _ in points),
            min(y for _, y in points), max(x for x, _ in points) + 1, max(y for _, y in points) + 1]})
    return clusters


def scene_resources(pixels, left=7, top=5):
    if len(pixels) != 16384 or any(value not in (0, 11, 15) for value in pixels):
        raise ValueError('The scene needs a 128x128 silhouette using body/eye palette slots.')
    if left < 0 or top < 0 or left + 16 > 32 or top + 16 > 32:
        raise ValueError('The 128x128 creature must fit the native 32x32 tile map.')
    if any(pixels[:128 * 16]):
        raise ValueError('Reserve the first two empty silhouette rows for backing-color tiles.')
    colors = (10, 9, 8, 7, 6, 5, 4)
    color_at = lambda y: colors[min(6, y * 7 // 160)]
    tiles = bytearray(tiles8(pixels, 128, 128, 16, 16))
    entries = [0xe000 | y for y in range(32) for _ in range(32)]
    for y in range(16):
        for x in range(16):
            tile = y * 16 + x
            occupied = any(tiles[tile * 64:tile * 64 + 64])
            for dy in range(8):
                for dx in range(8):
                    index = tile * 64 + dy * 8 + dx
                    if not tiles[index]:
                        tiles[index] = color_at((top + y) * 8 + dy)
            if occupied:
                entries[(top + y) * 32 + left + x] = 0xe000 | tile
    # One reusable background tile per screen row preserves cloud blending.
    for row in range(32):
        tiles[row * 64:row * 64 + 64] = bytes(color_at(row * 8 + dy) for dy in range(8) for _ in range(8))
    return pack4(tiles), struct.pack('<1024H', *entries)


def encode_creature(root):
    # Threshold/resampling and palette encoding preserve the generated silhouette.
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    alpha = source.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    bounds = alpha.getbbox()
    if not bounds:
        raise ValueError('Bayveil needs visible silhouette art.')
    cell, mask = source.crop(bounds), alpha.crop(bounds)
    scale = min(116 / cell.width, 96 / cell.height)
    size = (round(cell.width * scale), round(cell.height * scale))
    cell = cell.resize(size, Image.Resampling.NEAREST)
    mask = mask.resize(size, Image.Resampling.NEAREST)
    image = Image.new('P', (128, 128), 0)
    palette = [0] * 768
    palette[33:36] = [0, 74, 98]
    palette[45:48] = [255, 210, 76]  # Preview maximum glow; runtime pulses palette slot 15.
    image.putpalette(palette)
    left, top = (128 - size[0]) // 2, (128 - size[1]) // 2
    eye_pixels = 0
    for y in range(size[1]):
        for x in range(size[0]):
            if mask.getpixel((x, y)):
                r, g, b, _ = cell.getpixel((x, y))
                eye = r > 160 and g > 100 and b < 120
                image.putpixel((x + left, y + top), 15 if eye else 11)
                eye_pixels += eye
    if not 2 <= eye_pixels <= 128:
        raise ValueError('Review the gold lighthouse-eye mask before native encoding.')
    pixels = bytes(image.get_flattened_data())
    eyes = eye_clusters(pixels, 128, 128)
    if len(eyes) != 2 or not (eyes[0]['bounds'][2] <= 64 <= eyes[1]['bounds'][0]):
        raise ValueError('The title silhouette needs two separate eyes, one on each side.')
    image.save(directory / 'native-preview.png', transparency=0, bits=4)
    graphics, tilemap = scene_resources(pixels)
    files = {'bayveil.4bpp': graphics, 'bayveil.tilemap': tilemap}
    for filename, data in files.items():
        (directory / filename).write_bytes(data)
    (directory / 'conversion.json').write_text(json.dumps({
        'source_size': list(source.size), 'alpha_bounds': list(bounds),
        'native_size': [128, 128], 'silhouette_size': list(size),
        'placement': [left, top], 'tilemap_origin': [7, 5], 'palette_bank': 14,
        'background': 'authored blue/teal row gradient in reserved first 32 tiles',
        'body_palette_index': 11, 'eye_palette_index': 15, 'eye_pixels': eye_pixels,
        'eye_clusters': eyes,
        'preview_eye_color': 'maximum glow; actual title uses its existing animated color',
        'campaign_acquisition_implemented': False, 'quality_approval': 'pending',
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    }, indent=2) + '\n')


def apply_title_creature(root, emerald, target):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    for filename, digest in metadata['files'].items():
        if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != digest:
            raise ValueError('Regenerate the native Bayveil title assets after editing.')
    return apply_resources(root, emerald, target, [
        {'symbol': 'sTitleScreenRayquazaGfx', 'data': (directory / 'bayveil.4bpp').read_bytes(), 'compressed': True},
        {'symbol': 'sTitleScreenRayquazaTilemap', 'data': (directory / 'bayveil.tilemap').read_bytes(), 'compressed': True}])


if __name__ == '__main__':
    encode_creature(Path(__file__).resolve().parents[2])
