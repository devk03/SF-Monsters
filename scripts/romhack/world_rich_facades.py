"""Original SF facade modules for the shared world art compiler.

Pixels come from our original connected-frontage-v3 atlas and authored modules,
never an Emerald reference. Index0 is transparent; use that atlas's RGB555
palette. The facade/closed/variants API matches world_facade_modules. Doorway
bindings are deliberately NOT inferred from these decorative ordinary fronts.
Run this file with --preview DIRECTORY for a private labeled contact sheet and
an exact flip-aware graphics count (Pillow is only needed for that command).
"""
import argparse
import hashlib
import json
import struct
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORMS = ('walkup', 'shophouse', 'workshop', 'gable', 'deco', 'flats', 'arcade', 'duplex')
SOURCE = ROOT / 'assets/tiles/connected-frontage-v3'


@lru_cache(maxsize=1)
def source():
    receipt = json.loads((SOURCE / 'conversion.json').read_text())
    files = {}
    for name in ('block.indices', 'block.gbapal'):
        raw = (SOURCE / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != receipt['files'][name]:
            raise ValueError('Original SF frontage source differs: ' + name)
        files[name] = raw
    if len(files['block.indices']) != 176 * 80 or len(files['block.gbapal']) != 32:
        raise ValueError('Original SF frontage dimensions changed')
    return files


def facade(name, closed=('left', 'right')):
    if name not in FORMS or not set(closed) <= {'left', 'right'}:
        raise ValueError('Unknown facade family or attachment edge')
    width, height = (32 if name in ('shophouse', 'flats') else 48), 64
    p = bytearray(width * height)
    atlas = source()['block.indices']

    def box(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(height, y1 + 1)):
            for x in range(max(0, x0), min(width, x1 + 1)):
                p[y * width + x] = c

    def patch(sx, sy, w, h, x, y):
        if not (0 <= sx <= 176-w and 0 <= sy <= 80-h
                and 0 <= x <= width-w and 0 <= y <= height-h):
            raise ValueError('Facade module exceeds its source or destination')
        for dy in range(h):
            p[(y+dy)*width+x:(y+dy)*width+x+w] = atlas[(sy+dy)*176+sx:(sy+dy)*176+sx+w]

    def window(x, y, w=8, h=12):
        # One lit reveal, one shadowed reveal, inset glass and projecting sill.
        box(x-2, y-2, x+w+1, y+h+2, 6)
        box(x-2, y-2, x+w, y-1, 5)
        box(x-1, y, x+w, y+h, 1)
        box(x, y, x+w-1, y+h-1, 4)
        box(x, y, x, y+h-1, 5)
        box(x+1, y+1, x+2, y+3, 3)
        box(x+w-1, y, x+w, y+h, 8)
        box(x, y+h//2, x+w-1, y+h//2, 2)
        box(x-2, y+h+1, x+w+1, y+h+1, 5)
        box(x-1, y+h+2, x+w+2, y+h+2, 13)

    def entry(x):
        # Reuse the original recessed glazed door, threshold and actual steps.
        patch(65, 43, 14, 21, x, 43)

    def roof():
        # Original shallow roof planes and cornice modules, aligned at8px.
        for x in range(0, width, 16):
            patch(96, 0, 16, 16, x, 0)
        box(0, 15, width-1, 15, 8)

    # Every form shares a foundation and material language, not a silhouette.
    box(0, 12, width-1, 59, 7)
    box(0, 59, width-1, 61, 6)
    box(0, 62, width-1, 63, 13)
    roof()
    if name == 'walkup':
        patch(0, 0, 48, 64, 0, 0)
        # Restore a broad brick/recessed sash section beside the original bay.
        box(24, 15, 47, 44, 9)
        window(30, 19, 9, 15)
        box(24, 39, 47, 41, 6)
        entry(32)
        # External iron landing and ladder, with modest cast shadow.
        box(24, 37, 46, 38, 1)
        for x in (25, 30, 35, 40, 45): box(x, 34, x, 37, 1)
        for y in range(39, 46):
            box(26+(y-39)//2, y, 27+(y-39)//2, y, 2)
    elif name == 'duplex':
        # Two projecting bays use the same original full-height bay module.
        patch(0, 0, 24, 64, 0, 0)
        patch(0, 0, 24, 64, 24, 0)
        box(22, 12, 25, 60, 7)
        box(23, 12, 23, 58, 5)
        entry(8); entry(32)
    elif name == 'shophouse':
        patch(48, 0, 32, 64, 0, 0)
        box(1, 31, 30, 33, 7)
        box(1, 34, 30, 38, 1)
        box(2, 34, 29, 36, 10)
        # Striped awning has a top plane, hanging valance and underside shadow.
        for x in range(0, 32, 4):
            box(x, 38, x+3, 42, 7 if x % 8 else 10)
            box(x, 43, x+3, 44 if x % 8 else 43, 8 if x % 8 else 6)
        box(0, 45, 31, 46, 1)
        window(4, 49, 9, 9); entry(18)
    elif name == 'flats':
        # Keep the original cream building's complete left/right16px modules;
        # omit its center16px module rather than chopping an exposed right end.
        patch(80, 0, 16, 64, 0, 0)
        patch(112, 0, 16, 64, 16, 0)
        box(17, 40, 31, 44, 6); box(17, 40, 31, 40, 5)
        entry(18)
        # Paint the original plaster panels; keep roof, stone belt and glass.
        for y in range(16,59):
            for x in range(2,30):
                if p[y*width+x]==5:p[y*width+x]=10
    elif name == 'gable':
        box(0, 0, 47, 16, 0)
        for y in range(2, 18):
            half = min(23, (y-2)*2)
            box(23-half, y, 24+half, y, 2)
            box(23-half, y, 24-half, y, 1)
            box(23+half, y, 24+half, y, 3)
        box(0, 17, 47, 19, 6); box(0, 17, 47, 17, 5)
        for y in range(21, 57, 4): box(0, y, 47, y, 6)
        window(5, 25, 9, 12); window(29, 25, 9, 12)
        window(18, 8, 8, 6); window(5, 46, 9, 10); entry(32)
    elif name == 'workshop':
        box(0, 0, 47, 12, 0)
        box(0, 14, 47, 59, 9)
        # Sawtooth roof, steel loft glazing and a deeply framed loading shutter.
        for x in (0, 16, 32):
            for y in range(2, 13):
                box(x+max(0, 12-y), y, x+15, y, 2)
                box(x+max(0, 12-y), y, x+max(0, 12-y), y, 5)
            box(x+10, 5, x+14, 10, 4)
            window(x+4, 19, 8, 13)
            box(x+8, 19, x+8, 31, 2)
        box(0, 36, 47, 39, 9); box(0, 36, 47, 36, 5)
        box(3, 41, 29, 61, 1); box(5, 43, 27, 59, 2)
        for y in range(45, 60, 3): box(5, y, 27, y, 8)
        box(3, 41, 29, 42, 6); entry(32)
    elif name == 'deco':
        box(0, 12, 47, 59, 10)
        box(8, 4, 39, 8, 6); box(16, 0, 31, 7, 5)
        box(20, 0, 27, 2, 6)
        for x in (5, 21, 37):
            window(x, 17, 7, 21)
            box(x-3, 12, x-3, 44, 5); box(x-2, 13, x-2, 44, 6)
        box(0, 43, 47, 46, 6); box(0, 43, 47, 43, 5)
        entry(17)
        box(14, 47, 15, 59, 5); box(32, 47, 33, 59, 6)
    else:  # arcade: original upper sash over three ground-floor stone arches.
        box(0, 13, 47, 59, 10)
        for x in (4, 20, 36): window(x, 18, 8, 12)
        box(0, 35, 47, 40, 6); box(0, 35, 47, 35, 5)
        box(2, 36, 45, 38, 9)
        for x in (4, 20, 36):
            window(x, 47, 8, 11)
            box(x-2, 44, x+9, 46, 6)
            box(x, 42, x+7, 44, 5)
            box(x, 44, x+7, 46, 4)
        entry(17)

    if name in ('gable','deco','arcade','workshop'):
        # Shared deep sash modules align to16px cells. Distinct roof, entry,
        # loading door/arches and central ribs retain the structural identity.
        # This also leaves enough native metatile IDs for the actual margins.
        for x in (0,32):
            box(x,16,x+15,31,7)
            window(x+4,18,8,12)
    # Start each edge with continuous wall/roof/foundation pixels. Add a full
    # finished pier only at exposed ends; middle variants truly lose the pier.
    for side in ('left', 'right'):
        edge, inner = (0, 1) if side == 'left' else (width-1, width-2)
        if side in closed:
            box(edge, 12, edge, 61, 1)
            box(inner, 13, inner, 59, 5 if side == 'left' else 6)
        else:
            # Continue the adjacent material through the shared boundary.
            neighbor = 2 if side == 'left' else width-3
            for y in range(16, 60):
                p[y*width+edge] = p[y*width+neighbor]
                p[y*width+inner] = p[y*width+neighbor]
    return width, height, bytes(p)


def fronts(profile, *, variants=False):
    if profile in ('residential', 'nature'):
        return []
    result = []
    for name in FORMS:
        for suffix, closed in [('', ('left', 'right'))] + (
                [('_l', ('left',)), ('_m', ()), ('_r', ('right',))] if variants else []):
            w, h, pixels = facade(name, closed)
            result.append((name+suffix, w, h, pixels))
    return result


def tile_inventory(cards):
    """Count exact8x8graphics modulo horizontal/vertical reflection."""
    from world_shared_primary import canonical_tile
    unique = set()
    for _, w, h, raw in cards:
        for y in range(0, h, 8):
            for x in range(0, w, 8):
                tile = bytes(raw[(y+dy)*w+x+dx] for dy in range(8) for dx in range(8))
                unique.add(canonical_tile(tile)[0])
    return unique


def preview(directory):
    from PIL import Image, ImageDraw
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    palette = struct.unpack('<16H', source()['block.gbapal'])
    rgb = [tuple(((c >> shift) & 31)*255//31 for shift in (0, 5, 10)) for c in palette]
    sheet = Image.new('RGB', (760, 820), (235, 232, 218))
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 8), 'PRIVATE ART PROTOTYPE / original SF source / not native gameplay', fill=(35, 40, 48))
    for index, name in enumerate(FORMS):
        x0, y0 = 12+(index % 4)*188, 38+(index // 4)*300
        w, h, raw = facade(name)
        art = Image.new('RGB', (w, h), (207, 210, 207))
        art.putdata([rgb[p] if p else (207, 210, 207) for p in raw])
        sheet.paste(art.resize((w*3, h*3), Image.Resampling.NEAREST), (x0, y0+20))
        draw.text((x0, y0), name, fill=(35, 40, 48))
    # One real attached row, all attachment roles, at native2x pixel scale.
    row = [('walkup', ('left',)), ('shophouse', ()), ('workshop', ()), ('deco', ('right',))]
    x, y = 12, 670
    draw.text((x, y-20), 'Attachment strip: left / middle / middle / right', fill=(35,40,48))
    for name, closed in row:
        w, h, raw = facade(name, closed)
        art = Image.new('RGB', (w, h));art.putdata([rgb[v] if v else (207,210,207) for v in raw])
        sheet.paste(art.resize((w*2,h*2), Image.Resampling.NEAREST), (x, y));x += w*2
    sheet.save(directory/'facades.png')
    cells = set()
    for _, w, h, pixels in fronts('mixed_use', variants=True):
        for y in range(0,h,16):
            for x in range(0,w,16):
                cells.add(bytes(pixels[(y+dy)*w+x+dx] for dy in range(16) for dx in range(16)))
    report = dict(status='private source-art preview; native rendering and visual approval remain separate',
                  base_tiles=len(tile_inventory(fronts('mixed_use'))),
                  all_attachment_tiles=len(tile_inventory(fronts('mixed_use', variants=True))),
                  facade_cell_patterns=len(cells),
                  three_paints_cell_upper_bound=3*len(cells),
                  source_sha256={n:hashlib.sha256(b).hexdigest() for n,b in source().items()},
                  palette='connected-frontage-v3/block.gbapal',
                  scope='Facade graphics only; excludes terrain/props, palettes and metatile record budgets')
    (directory/'art-counts.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', required=True, type=Path)
    print(json.dumps(preview(parser.parse_args().preview), indent=2))
