"""Original Naval welcome figure; retain native intro timing and save flow."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys

from monsters import png_palette
from trainer_portraits import encode_portrait, replace_once

ASSET = 'assets/characters/naval-intro-v1'


def portrait_files(root):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    expected = {'portrait.png', 'portrait.4bpp', 'portrait.gbapal'}
    if set(metadata['files']) != expected or metadata['native_size'] != [64, 64]:
        raise ValueError('Intro figure needs one native frame and its own palette.')
    for name, digest in dict(metadata['files'], **{'source.png': metadata['source_sha256']}).items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Regenerate original intro figure after changing ' + name)
    policy = directory / 'palette-policy.json'
    policy_hash = hashlib.sha256(policy.read_bytes()).hexdigest() if policy.exists() else None
    if metadata.get('palette_policy_sha256') != policy_hash:
        raise ValueError('Regenerate original intro figure after changing its palette policy.')
    cleanup = directory / 'native-cleanup.json'
    cleanup_hash = hashlib.sha256(cleanup.read_bytes()).hexdigest() if cleanup.exists() else None
    if metadata.get('native_cleanup_sha256') != cleanup_hash:
        raise ValueError('Regenerate original intro figure after changing its native cleanup.')
    png_palette(directory / 'portrait.png', (64, 64))
    if (directory / 'portrait.4bpp').stat().st_size != 2048 or (
            directory / 'portrait.gbapal').stat().st_size != 32:
        raise ValueError('Intro figure must fit native 64x64 4bpp and sixteen colors.')
    return directory


def apply_intro(root, engine, original):
    directory = portrait_files(root)
    destination = engine / 'graphics/birch_speech/sf_naval.png'
    # A new path and refreshed timestamp avoid inherited generated art caches.
    shutil.copyfile(directory / 'portrait.png', destination)
    path = 'src/field_effect.c'
    source = original(path)
    for suffix, declaration in (('.4bpp', 'static const u32 sNewGameBirch_Gfx[]'),
                                ('.gbapal', 'static const u16 sNewGameBirch_Pal[16]')):
        old = f'{declaration} = INCGFX_U{32 if suffix == ".4bpp" else 16}("graphics/birch_speech/birch.png", "{suffix}");'
        source = replace_once(source, old, old.replace('birch.png', 'sf_naval.png'))
    (engine / path).write_text(source)
    return [path, 'graphics/birch_speech/sf_naval.png']


def audit_intro(rom, elf, root):
    """Read actual linked resource bytes and their native display bindings."""
    sys.path.insert(0, str(root / 'scripts/quality'))
    from check_creature_resources import Cartridge, pack_image
    from PIL import Image
    receipt = {'passed': False, 'checks': [], 'errors': [],
               'scope': 'Intro figure integration only; human likeness/art/flow approval pending'}
    try:
        directory = portrait_files(root)
        cart = Cartridge(rom, elf)
        with Image.open(directory / 'portrait.png') as image:
            graphics = pack_image(image)
            rgb = image.getpalette()[:48]
        palette = b''.join(struct.pack('<H', (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10)
                           for r, g, b in zip(rgb[::3], rgb[1::3], rgb[2::3]))
        checks = [('graphics', graphics, cart.data('sNewGameBirch_Gfx')),
                  ('palette', palette, cart.data('sNewGameBirch_Pal')),
                  ('frame_binding', struct.pack('<IHH', cart.symbols['sNewGameBirch_Gfx'][0], 2048, 0),
                   cart.data('sPicTable_NewGameBirch')),
                  ('palette_binding', struct.pack('<IHH', cart.symbols['sNewGameBirch_Pal'][0], 0x1006, 0),
                   cart.data('sSpritePalette_NewGameBirch'))]
        template = cart.data('sSpriteTemplate_NewGameBirch')
        if len(template) != 24:
            raise ValueError('Native intro sprite template changed size.')
        checks.append(('template_binding', struct.pack('<HHI', 0xffff, 0x1006,
                       cart.symbols['sPicTable_NewGameBirch'][0]), template[:4] + template[12:16]))
        for label, expected, actual in checks:
            receipt['checks'].append({'label': label, 'matches': actual == expected,
                'expected_sha256': hashlib.sha256(expected).hexdigest(),
                'actual_sha256': hashlib.sha256(actual).hexdigest()})
        receipt['inputs'] = {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (rom, elf, directory / 'portrait.png', Path(__file__))}
        receipt['passed'] = all(row['matches'] for row in receipt['checks'])
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        receipt['errors'].append(str(error))
    receipt['counts'] = {'total': len(receipt['checks']),
                         'matched': sum(row['matches'] for row in receipt['checks'])}
    return receipt


if __name__ == '__main__':
    encode_portrait(Path(__file__).resolve().parents[2], ASSET)
