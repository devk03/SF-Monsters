"""Convert our transparent title atlas into native logo/banner resources."""
import hashlib
import json
from pathlib import Path
import struct
from native_resources import apply_resources

ASSET = 'assets/ui/title'


def tiles8(pixels, width, height, macro_width, macro_height):
    if min(width, height, macro_width, macro_height) < 1 or len(pixels) != width * height or \
       width % (8 * macro_width) or height % (8 * macro_height):
        raise ValueError('Indexed pixels must fill complete native macro-tile blocks.')
    output = bytearray()
    for my in range(0, height // 8, macro_height):
        for mx in range(0, width // 8, macro_width):
            for ty in range(my, my + macro_height):
                for tx in range(mx, mx + macro_width):
                    for y in range(ty * 8, ty * 8 + 8):
                        output.extend(pixels[y * width + tx * 8:y * width + tx * 8 + 8])
    return bytes(output)


def encode_title(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source.png').convert('RGBA')
    if source.size != (1774, 887):
        raise ValueError('Review panel crops when changing the generated title atlas.')
    metadata = {'source_size': list(source.size), 'quality_approval': 'pending', 'assets': []}
    for name, bounds, canvas_size, limit, macro in [
        ('logo', (0, 0, 1018, 887), (256, 64), (180, 56), (32, 8)),
        ('subtitle', (1018, 0, 1774, 887), (128, 32), (120, 24), (8, 4))]:
        cell = source.crop(bounds)
        mask = cell.getchannel('A').point(lambda alpha: 255 if alpha >= 128 else 0)
        box = mask.getbbox()
        if not box:
            raise ValueError('Both title panels need visible lettering.')
        cell, mask = cell.crop(box), mask.crop(box)
        scale = min(limit[0] / cell.width, limit[1] / cell.height)
        size = (round(cell.width * scale), round(cell.height * scale))
        cell = cell.resize(size, Image.Resampling.NEAREST)
        mask = mask.resize(size, Image.Resampling.NEAREST)
        visible = [rgb[:3] for rgb, alpha in zip(cell.get_flattened_data(), mask.get_flattened_data()) if alpha]
        samples = Image.new('RGB', (len(visible), 1)); samples.putdata(visible)
        palette = samples.quantize(colors=15, method=Image.Quantize.MEDIANCUT).getpalette()[:45]
        colors = [(0, 0, 0)] + [tuple(round(c * 31 / 255) * 255 // 31 for c in palette[i:i + 3]) for i in range(0, 45, 3)]
        image = Image.new('P', canvas_size, 0)
        image.putpalette([c for color in colors for c in color] + [0] * 720)
        left, top = ((canvas_size[i] - size[i]) // 2 for i in range(2))
        if name == 'logo':
            # The native affine title layer adds 29 px, so x=91 maps to screen center x=120.
            left = 91 - size[0] // 2
        for y in range(size[1]):
            for x in range(size[0]):
                if mask.getpixel((x, y)):
                    rgb = cell.getpixel((x, y))[:3]
                    color = min(range(1, 16), key=lambda i: sum((rgb[c] - colors[i][c]) ** 2 for c in range(3)))
                    image.putpixel((x + left, y + top), color)
        image.save(directory / f'{name}-native.png', transparency=0, bits=8)
        raw = tiles8(bytes(image.get_flattened_data()), *canvas_size, *macro)
        pal = b''.join(struct.pack('<H', sum(round(rgb[c] * 31 / 255) << (5 * c) for c in range(3))) for rgb in colors)
        files = {f'{name}.8bpp': raw, f'{name}.gbapal': pal}
        for filename, data in files.items():
            (directory / filename).write_bytes(data)
        metadata['assets'].append({'name': name, 'panel': list(bounds), 'alpha_bounds': list(box),
            'native_size': list(canvas_size), 'lettering_size': list(size), 'palette_entries': 16,
            'macro_tiles': list(macro), 'placement': [left, top],
            'files': {filename: hashlib.sha256(data).hexdigest() for filename, data in files.items()}})
    (directory / 'conversion.json').write_text(json.dumps(metadata, indent=2) + '\n')


def apply_title_art(root, emerald, target):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    for asset in metadata['assets']:
        for filename, digest in asset['files'].items():
            if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != digest:
                raise ValueError('Regenerate native title resources after changing their assets.')
    data = lambda name: (directory / name).read_bytes()
    return apply_resources(root, emerald, target, [
        {'symbol': 'gTitleScreenPokemonLogoGfx', 'data': data('logo.8bpp'), 'compressed': True},
        {'symbol': 'gTitleScreenBgPalettes', 'data': data('logo.gbapal') + bytes(416), 'preserve_tail': True},
        {'symbol': 'gTitleScreenEmeraldVersionGfx', 'data': data('subtitle.8bpp'), 'compressed': True},
        {'symbol': 'gTitleScreenEmeraldVersionPal', 'data': data('subtitle.gbapal')}])


if __name__ == '__main__':
    encode_title(Path(__file__).resolve().parents[2])
