"""Verify three original battle portraits and their actual native trainer bindings."""
import hashlib
import json
from pathlib import Path
import struct

# Independent acceptance contract: never derive these IDs from the producer registry.
EXPECTED = (
    ('ScottWu', 'scott-wu', 93, 265),
    ('WaldenYan', 'walden-yan', 94, 320),
    ('StevenHao', 'steven-hao', 95, 321),
)
# Pinned agbcc STRUCTURE_SIZE_BOUNDARY=32 pads the two-u8 MonCoords to four bytes.
TABLES = {'gTrainerFrontPicCoords': 4, 'gTrainerFrontPicTable': 8,
          'gTrainerFrontPicPaletteTable': 8, 'gTrainerFrontAnimsPtrTable': 4}


def audit_portraits(rom, elf, root):
    from check_creature_resources import Cartridge, decode_lz, pack_image
    from PIL import Image

    checks, errors, inputs = [], [], {}
    receipt = {'passed': False, 'checks': checks, 'errors': errors, 'inputs': inputs,
               'quality_approval': 'pending',
               'scope': 'Exact Scott93/Walden94/Steven95 pixels, palettes and native bindings; '
                        'all96 front-table entries structurally bounded. Stock0..92 resource identity, '
                        'battle mechanics, saves, likeness and runtime animation are outside this receipt.'}

    def source(path):
        data = path.read_bytes()
        inputs[str(path)] = hashlib.sha256(data).hexdigest()
        return data

    def compare(name, expected, read):
        row = {'name': name, 'passed': False, 'expected_bytes': len(expected),
               'expected_sha256': hashlib.sha256(expected).hexdigest()}
        try:
            actual = read()
            row.update(passed=actual == expected, actual_bytes=len(actual),
                       actual_sha256=hashlib.sha256(actual).hexdigest())
        except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
            row['error'] = str(error)
            errors.append(name + ': ' + str(error))
        checks.append(row)

    try:
        inputs['rom'] = hashlib.sha256(rom.read_bytes()).hexdigest()
        inputs['elf'] = hashlib.sha256(elf.read_bytes()).hexdigest()
        source(Path(__file__))
        source(Path(__file__).with_name('trainer_portraits.py'))
        source(Path(__file__).parents[1] / 'quality/check_creature_resources.py')
        cart = Cartridge(rom, elf)
        receipt['expected'] = [{'symbol': symbol, 'picture': pic, 'trainer': trainer}
                               for symbol, slug, pic, trainer in EXPECTED]

        def pointer(address, size=4):
            if address % 4 or not 0x08000000 <= address <= 0x08000000 + len(cart.rom) - size:
                raise ValueError('Trainer table pointer leaves aligned cartridge data.')

        def table_shape(name, stride):
            data = cart.data(name)
            if len(data) != 96 * stride:
                raise ValueError('Require exactly96 complete entries in ' + name)
            for i in range(96):
                if name == 'gTrainerFrontPicCoords':
                    size, offset, padding0, padding1 = data[i*4:i*4+4]
                    if size != 8 or offset > 64 or padding0 or padding1:
                        raise ValueError('Trainer coordinates leave the native64x64 canvas.')
                elif name == 'gTrainerFrontPicTable':
                    address, size, tag = struct.unpack_from('<IHH', data, i*8)
                    pointer(address)
                    if tag != i or size not in (2048, 4096):
                        raise ValueError('Trainer sheet tag or frame allocation differs.')
                elif name == 'gTrainerFrontPicPaletteTable':
                    address, tag = struct.unpack_from('<IH', data, i*8)
                    pointer(address)
                    if tag != i:
                        raise ValueError('Trainer palette tag differs from its picture index.')
                else:
                    pointer(struct.unpack_from('<I', data, i*4)[0])
            return struct.pack('<I', len(data))

        for name, stride in TABLES.items():
            compare(name + ':complete_table', struct.pack('<I', 96 * stride),
                    lambda name=name, stride=stride: table_shape(name, stride))
        compare('single_frame_animation', bytes.fromhex('00000000ffff0000'),
                lambda: cart.data('sAnim_GeneralFrame0'))

        for symbol, slug, pic, trainer in EXPECTED:
            try:
                directory = root / 'assets/characters/cognition-cast' / slug / 'battle-portrait-v1'
                metadata = json.loads(source(directory / 'conversion.json'))
                if set(metadata['files']) != {'portrait.png', 'portrait.4bpp', 'portrait.gbapal'} or \
                   metadata['native_size'] != [64, 64] or metadata['baseline'] != 62 or \
                   metadata['palette_colors'] != 16:
                    raise ValueError('Portrait source contract changed.')
                for filename, expected_hash in dict(metadata['files'], **{'source.png': metadata['source_sha256']}).items():
                    if hashlib.sha256(source(directory / filename)).hexdigest() != expected_hash:
                        raise ValueError('Portrait source receipt differs: ' + filename)
                for filename, key in (('palette-policy.json', 'palette_policy_sha256'),
                                      ('native-cleanup.json', 'native_cleanup_sha256')):
                    path = directory / filename
                    actual_hash = hashlib.sha256(source(path)).hexdigest() if path.exists() else None
                    if actual_hash != metadata.get(key):
                        raise ValueError('Portrait drawing policy or cleanup changed.')
                with Image.open(directory / 'portrait.png') as image:
                    if image.mode != 'P' or image.size != (64, 64) or image.info.get('transparency') != 0 or \
                       not any(image.tobytes()[62*64:63*64]) or any(image.tobytes()[63*64:]):
                        raise ValueError('Portrait PNG needs a visible native frame and transparent bottom gutter.')
                    pixels = pack_image(image)
                    colors = image.getpalette()[:48]
                    palette = b''.join(struct.pack('<H', sum(round(colors[i*3+c]*31/255) << (5*c)
                        for c in range(3))) for i in range(16))
                if pixels != (directory/'portrait.4bpp').read_bytes() or len(pixels) != 2048 or \
                   palette != (directory/'portrait.gbapal').read_bytes() or len(palette) != 32 or palette[:2] != b'\0\0':
                    raise ValueError('Portrait PNG and native serialized pixels/palette disagree.')
            except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
                errors.append(symbol + ': ' + str(error))
                checks.append({'name': symbol + ':source', 'passed': False, 'error': str(error)})
                continue
            compare(symbol + ':pixels', pixels,
                    lambda symbol=symbol: decode_lz(cart.data('gTrainerFrontPic_' + symbol)))
            compare(symbol + ':palette', palette,
                    lambda symbol=symbol: decode_lz(cart.data('gTrainerPalette_' + symbol)))
            compare(symbol + ':coords', bytes([8, 1]),
                    lambda pic=pic: cart.data('gTrainerFrontPicCoords')[pic*4:pic*4+2])

            def sheet(symbol=symbol, pic=pic):
                expected = struct.pack('<IHH', cart.symbols['gTrainerFrontPic_' + symbol][0], 2048, pic)
                actual = cart.data('gTrainerFrontPicTable')[pic*8:pic*8+8]
                if actual != expected:
                    raise ValueError('Trainer sheet pointer, size or tag differs.')
                return b'exact-sheet-binding'
            compare(symbol + ':sheet_binding', b'exact-sheet-binding', sheet)

            def palette_binding(symbol=symbol, pic=pic):
                expected = struct.pack('<IH', cart.symbols['gTrainerPalette_' + symbol][0], pic)
                if cart.data('gTrainerFrontPicPaletteTable')[pic*8:pic*8+6] != expected:
                    raise ValueError('Trainer palette pointer or tag differs.')
                return b'exact-palette-binding'
            compare(symbol + ':palette_binding', b'exact-palette-binding', palette_binding)

            def animation(symbol=symbol, pic=pic):
                address = cart.symbols['sAnims_' + symbol][0]
                if cart.data('gTrainerFrontAnimsPtrTable')[pic*4:pic*4+4] != struct.pack('<I', address) or \
                   cart.data('sAnims_' + symbol) != struct.pack('<I', cart.symbols['sAnim_GeneralFrame0'][0]):
                    raise ValueError('Trainer front animation pointer chain differs.')
                return b'frame0-then-end'
            compare(symbol + ':animation_binding', b'frame0-then-end', animation)

            def selector(trainer=trainer):
                data = cart.data('gTrainers')
                if len(data) % 40 or len(data) < (trainer + 1) * 40:
                    raise ValueError('Trainer records do not fit the native40-byte ABI.')
                return data[trainer*40+3:trainer*40+4]
            compare(symbol + ':trainer_selector', bytes([pic]), selector)
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        errors.append(str(error))
        checks.append({'name': 'audit_inputs', 'passed': False, 'error': str(error)})
    receipt['counts'] = {'total': len(checks), 'matched': sum(row['passed'] for row in checks)}
    receipt['passed'] = bool(checks) and all(row['passed'] for row in checks) and not errors
    return receipt
