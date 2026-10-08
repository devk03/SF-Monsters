"""Encode authored battle views and distinct icon frames into native GBA assets."""
from pathlib import Path
import argparse
import json
from PIL import Image


def atlas_assets(source, output, layout, icon_palette):
    image = Image.open(source).convert('RGBA')
    rectangles = layout['battle'] + layout['icons']
    if len(layout['battle']) != 3 or len(layout['icons']) != 2:
        raise ValueError('Atlas needs front, pose, back and two authored icons.')
    cells = []
    for left, top, right, bottom in rectangles:
        if not 0 <= left < right <= image.width or not 0 <= top < bottom <= image.height:
            raise ValueError('Atlas rectangle leaves the source image.')
        cell = image.crop((left, top, right, bottom))
        mask = cell.getchannel('A').point(lambda alpha: 255 if alpha >= 128 else 0)
        if mask.getbbox() is None: raise ValueError('Every authored frame needs a visible subject.')
        cells.append((cell, mask))

    def fitted(group, limit):
        if len({cell.size for cell, _ in group}) != 1:
            if not layout.get('pad_frames'):
                raise ValueError('Corresponding atlas frames need equal source canvases.')
            size = (max(cell.width for cell, _ in group), max(cell.height for cell, _ in group))
            padded = []
            for cell, mask in group:
                position = ((size[0] - cell.width) // 2, size[1] - cell.height)
                canvas = Image.new('RGBA', size); canvas.paste(cell, position)
                alpha = Image.new('L', size); alpha.paste(mask, position)
                padded.append((canvas, alpha))
            group = padded
        bounds = [mask.getbbox() for _, mask in group]
        crop = (min(b[0] for b in bounds), min(b[1] for b in bounds),
                max(b[2] for b in bounds), max(b[3] for b in bounds))
        width, height = crop[2] - crop[0], crop[3] - crop[1]
        scale = min(limit / width, limit / height)
        size = (max(1, round(width * scale)), max(1, round(height * scale)))
        return [(cell.crop(crop).resize(size, Image.Resampling.NEAREST),
                 mask.crop(crop).resize(size, Image.Resampling.NEAREST)) for cell, mask in group], crop

    battle, battle_crop = fitted(cells[:3], 56)
    icons, icon_crop = fitted(cells[3:], 24)
    colors = [rgb[:3] for cell, mask in battle
              for rgb, alpha in zip(cell.get_flattened_data(), mask.get_flattened_data()) if alpha]
    samples = Image.new('RGB', (len(colors), 1)); samples.putdata(colors)
    palette = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    entries = [(0, 0, 0)]
    for i in range(0, len(palette), 3):
        color = tuple(round(c * 31 / 255) * 255 // 31 for c in palette[i:i + 3])
        if color not in entries[1:]: entries.append(color)
    entries += [entries[-1]] * (16 - len(entries))
    lines = Path(icon_palette).read_text().splitlines()
    if lines[:3] != ['JASC-PAL', '0100', '16'] or len(lines) != 19:
        raise ValueError('Icons need a sixteen-color shared JASC palette.')
    icon_colors = [tuple(map(int, line.split())) for line in lines[3:]]
    if any(len(color) != 3 or any(not 0 <= c <= 255 for c in color) for color in icon_colors):
        raise ValueError('Shared icon colors must be RGB triples.')

    def blank(size, colors):
        result = Image.new('P', size, 0)
        result.putpalette([c for color in colors for c in color])
        result.info['transparency'] = 0
        return result

    def encode(cell, mask, colors):
        pixels = [0 if not alpha else min(range(1, 16),
                  key=lambda i: sum((rgb[c] - colors[i][c]) ** 2 for c in range(3)))
                  for rgb, alpha in zip(cell.get_flattened_data(), mask.get_flattened_data())]
        result = blank(cell.size, colors); result.putdata(pixels)
        return result

    encoded = []
    for cell, mask in battle:
        canvas = blank((64, 64), entries)
        canvas.paste(encode(cell, mask, entries), ((64 - cell.width) // 2, 60 - cell.height))
        encoded.append(canvas)
    animation = blank((64, 128), entries)
    animation.paste(encoded[0], (0, 0)); animation.paste(encoded[1], (0, 64))
    icon = blank((32, 64), icon_colors)
    for index, (cell, mask) in enumerate(icons):
        icon.paste(encode(cell, mask, icon_colors), ((32 - cell.width) // 2, index * 32 + 32 - cell.height))
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    for name, sprite in [('front', encoded[0]), ('anim_front', animation), ('back', encoded[2]), ('icon', icon)]:
        sprite.save(output / (name + '.png'), transparency=0, bits=4)
    for name, colors in [('normal', entries), ('shiny', [(b, g, r) for r, g, b in entries])]:
        (output / (name + '.pal')).write_text('JASC-PAL\n0100\n16\n' + '\n'.join('%d %d %d' % c for c in colors) + '\n')
    (output / 'conversion.json').write_text(json.dumps({'source_size': list(image.size),
        'authored_rectangles': layout, 'battle_crop': battle_crop, 'icon_crop': icon_crop,
        'icon_palette': str(icon_palette), 'opaque_palette_budget': 15,
        'method': 'aspect-preserving nearest-neighbor, shared RGB555 battle palette, authored icon frames',
        'pixel_cleanup': 'pending', 'quality_approval': 'pending'}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path); parser.add_argument('output', type=Path)
    parser.add_argument('--layout', type=Path, required=True)
    parser.add_argument('--icon-palette', type=Path, required=True)
    args = parser.parse_args()
    atlas_assets(args.source, args.output, json.loads(args.layout.read_text()), args.icon_palette)
