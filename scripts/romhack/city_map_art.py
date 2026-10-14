"""Build original native SF map tiles from pinned public-domain geographic data."""
from pathlib import Path
import hashlib
import json
import math
import struct

ASSET = Path('assets/world/sf-city-map')
# GBA BG banks7–9; bank10 belongs to native habitat glow. Index0 is transparent.
COLORS = [
    (0, 0, 0), (123, 172, 222), (140, 189, 238), (173, 213, 246),
    (90, 140, 197), (238, 230, 197), (222, 213, 180), (197, 197, 164),
    (156, 164, 139), (115, 148, 90), (148, 172, 106), (82, 115, 74),
    (255, 246, 222), (197, 106, 74), (238, 164, 106), (74, 90, 98),
]


def geography(root):
    from PIL import Image, ImageChops, ImageDraw
    plan = json.loads((root / ASSET / 'plan.json').read_text())
    source = (root / ASSET / 'source-neighborhoods.geojson').read_bytes()
    if hashlib.sha256(source).hexdigest() != plan['source_sha256']:
        raise ValueError('Pinned SF geography changed.')
    projection = plan['projection']
    scale = projection['pixels_per_latitude_degree']
    cosine = math.cos(math.radians(projection['center_latitude']))
    def xy(longitude, latitude):
        return (round(projection['center_x'] + (longitude - projection['center_longitude']) * cosine * scale),
                round(projection['center_y'] - (latitude - projection['center_latitude']) * scale))
    land, parks = Image.new('L', (256, 256)), Image.new('L', (256, 256))
    for feature in json.loads(source)['features']:
        if feature['geometry']['type'] != 'MultiPolygon':
            raise ValueError('Expected pinned SF multipolygons.')
        part = Image.new('L', land.size)
        draw = ImageDraw.Draw(part)
        for polygon in feature['geometry']['coordinates']:
            draw.polygon([xy(*point) for point in polygon[0]], fill=255)
            for hole in polygon[1:]:
                draw.polygon([xy(*point) for point in hole], fill=0)
        land = ImageChops.lighter(land, part)
        if feature['properties']['nhood'] in plan['parks']:
            parks = ImageChops.lighter(parks, part)
    hubs = []
    for hub in plan['hubs']:
        x, y = xy(hub['longitude'], hub['latitude'])
        gx, gy = x // 8 - 1, y // 8 - 2
        if not 0 <= gx < 28 or not 0 <= gy < 15:
            raise ValueError('Hub falls outside the native28x15 region grid.')
        hubs.append(dict(hub, x=gx, y=gy, width=1, height=1))
    if len({(hub['x'], hub['y']) for hub in hubs}) != len(hubs):
        raise ValueError('SF hub markers overlap.')
    return plan, land, parks, hubs


def make_map(root):
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    plan, land, parks, hubs = geography(root)
    palette = [0] * 768
    # Both engine loaders start their map palette at112.
    for i, color in enumerate(COLORS):
        palette[(112 + i) * 3:(113 + i) * 3] = color
    image = Image.new('P', land.size, 113)
    image.putpalette(palette)
    draw = ImageDraw.Draw(image)
    # Repeating eight-pixel patterns keep the native atlas small and coherent.
    for y in range(4, 256, 8):
        for x in range(0, 256, 16):
            draw.line((x, y, x + 7, y), fill=114)
    coast = ImageChops.subtract(land.filter(ImageFilter.MaxFilter(3)), land)
    image.paste(115, mask=coast)
    image.paste(117, mask=land)
    urban = Image.new('P', land.size, 117)
    ud = ImageDraw.Draw(urban)
    for x in range(2, 256, 8):
        ud.line((x, 0, x, 255), fill=118)
    for y in range(2, 256, 8):
        ud.line((0, y, 255, y), fill=118)
    image.paste(urban, mask=land)
    image.paste(123, mask=parks)
    image.paste(121, mask=parks.filter(ImageFilter.MinFilter(3)))
    pd = ImageDraw.Draw(image)
    for y in range(0, 256, 8):
        for x in range(0, 256, 8):
            if parks.getpixel((x + 4, y + 4)):
                pd.line((x + 3, y + 3, x + 5, y + 3), fill=123)
                pd.line((x + 2, y + 4, x + 6, y + 4), fill=123)
                pd.point((x + 4, y + 2), fill=122)
                pd.point((x + 4, y + 5), fill=123)
    # The two active neighborhood pins share the exact engine entry coordinates.
    for hub in hubs:
        x, y = (hub['x'] + 1) * 8 + 4, (hub['y'] + 2) * 8 + 4
        pd.rectangle((x - 3, y - 3, x + 3, y + 3), fill=127)
        pd.rectangle((x - 2, y - 2, x + 2, y + 2), fill=125)
        pd.point((x - 1, y - 1), fill=124)
    # Keep UI/future affine background outside the28x15 map field simple.
    pd.rectangle((0, 144, 255, 255), fill=113)
    tiles, table, indices = [bytes(64)], {bytes(64): 0}, []
    for y in range(0, 256, 8):
        for x in range(0, 256, 8):
            tile = image.crop((x, y, x + 8, y + 8)).tobytes()
            if tile not in table:
                table[tile] = len(tiles)
                tiles.append(tile)
            indices.append(table[tile])
    if len(tiles) > 232:
        raise ValueError(f'SF map needs{len(tiles)} tiles; Guide allows232.')
    atlas = Image.new('P', (128, 120))
    atlas.putpalette(palette)
    for i, tile in enumerate(tiles):
        frame = Image.frombytes('P', (8, 8), tile)
        atlas.paste(frame, (i % 16 * 8, i // 16 * 8))
    # Regular BG is32x32 u16. The other region map uses64x64 affine u8.
    regular = struct.pack('<1024H', *indices)
    affine = bytearray(4096)
    for y in range(64):
        for x in range(64):
            affine[y * 64 + x] = indices[y * 32 + x] if x < 32 and y < 32 else table[bytes([113]) * 64]
    colors = COLORS + [(0, 0, 0)] * 32
    native_palette = struct.pack('<48H', *[(r // 8 | g // 8 << 5 | b // 8 << 10) for r, g, b in colors])
    return image, atlas, regular, bytes(affine), native_palette, hubs, len(tiles)


def write_assets(root):
    image, atlas, regular, affine, palette, hubs, count = make_map(root)
    folder = root / ASSET
    image.save(folder / 'map-preview.png')
    atlas.save(folder / 'tiles.png')
    for name, data in [('guide-map.bin', regular), ('region-map.bin', affine), ('palette.gbapal', palette)]:
        (folder / name).write_bytes(data)
    (folder / 'conversion.json').write_text(json.dumps({
        'tile_count': count, 'guide_tile_limit': 232, 'region_tile_limit': 233,
        'palette_start': 112, 'palette_colors': 48, 'hubs': hubs,
        'geometry_sha256': hashlib.sha256((folder / 'source-neighborhoods.geojson').read_bytes()).hexdigest(),
        'approval': 'pending', 'engine_integration': 'pending'
    }, indent=2) + '\n')
    return count


if __name__ == '__main__':
    print('Original SF map candidate tiles:', write_assets(Path(__file__).resolve().parents[2]))
