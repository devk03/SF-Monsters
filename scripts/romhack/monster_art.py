"""Encode generated source art as editable GBA assets; no quality approval implied."""
from pathlib import Path
import argparse
import json
from PIL import Image


def native_assets(source, output, crop):
    image = Image.open(source).convert('RGBA')
    if image.width != image.height * 3:
        raise ValueError('Source must contain three equal square cells: front, pose, back.')
    left, top, right, bottom = crop
    if not 0 <= left < right <= image.height or not 0 <= top < bottom <= image.height:
        raise ValueError('Crop must fit every source cell.')
    if right - left != bottom - top:
        raise ValueError('Use a square crop to preserve creature proportions.')
    frames, colors = [], []
    for index in range(3):
        cell = image.crop((index * image.height + left, top,
                           index * image.height + right, bottom))
        cell = cell.resize((56, 56), Image.Resampling.NEAREST)
        mask = cell.getchannel('A').point(lambda alpha: 255 if alpha >= 128 else 0)
        if mask.getbbox() is None:
            raise ValueError('Every pose must contain a visible creature.')
        frames.append((cell, mask))
        colors.extend(rgb[:3] for rgb, alpha in zip(cell.get_flattened_data(), mask.get_flattened_data()) if alpha)
    # Quantize visible samples only. Reserve palette index zero for transparency.
    samples = Image.new('RGB', (len(colors), 1)); samples.putdata(colors)
    reduced = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    palette = reduced.getpalette()[:45]
    entries = [(0, 0, 0)]
    for index in range(0, len(palette), 3):
        # Round to RGB555 first so preview colors agree with hardware colors.
        color = tuple(round(channel * 31 / 255) * 255 // 31 for channel in palette[index:index + 3])
        if color not in entries[1:]: entries.append(color)
    entries += [entries[-1]] * (16 - len(entries))
    flat = [channel for color in entries for channel in color]

    def blank(size):
        result = Image.new('P', size, 0)
        result.putpalette(flat)
        result.info['transparency'] = 0
        return result

    encoded = []
    for cell, mask in frames:
        pixels = []
        for rgb, alpha in zip(cell.get_flattened_data(), mask.get_flattened_data()):
            pixels.append(0 if not alpha else min(range(1, 16),
                          key=lambda index: sum((rgb[channel] - entries[index][channel]) ** 2 for channel in range(3))))
        sprite = blank((56, 56)); sprite.putdata(pixels)
        canvas = blank((64, 64)); canvas.paste(sprite, (4, 4))
        encoded.append(canvas)
    front_animation = blank((64, 128))
    front_animation.paste(encoded[0], (0, 0)); front_animation.paste(encoded[1], (0, 64))
    icon = blank((32, 64))
    for index in range(2):
        icon.paste(encoded[index].resize((24, 24), Image.Resampling.NEAREST), (4, 8 + index * 32))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for name, sprite in [('front', encoded[0]), ('anim_front', front_animation), ('back', encoded[2]), ('icon', icon)]:
        sprite.save(output / (name + '.png'), transparency=0, bits=4)
    for name, colors in [('normal', entries), ('shiny', [(b, g, r) for r, g, b in entries])]:
        (output / (name + '.pal')).write_text('JASC-PAL\n0100\n16\n' + '\n'.join('%d %d %d' % color for color in colors) + '\n')
    (output / 'conversion.json').write_text(json.dumps({
        'source_size': list(image.size), 'cell_crop': crop, 'alpha_threshold': 128,
        'native_cell': [64, 64], 'opaque_palette_budget': 15,
        'method': 'nearest-neighbor and shared RGB555 median-cut palette',
        'pixel_cleanup': 'pending', 'quality_approval': 'pending'
    }, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--crop', nargs=4, type=int, required=True)
    args = parser.parse_args()
    native_assets(args.source, args.output, args.crop)
