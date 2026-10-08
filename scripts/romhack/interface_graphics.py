"""Insert our guide wordmark into declared native tiles; inherited sheets stay private."""
import hashlib
import json
from pathlib import Path
import subprocess
import uuid
from interface_text import symbols_from_nm

ASSET = 'assets/ui/field-guide'
SYMBOL = 'gPokedexMenu_Gfx'


def put_pixel(tiles, x, y, color):
    address = ((y // 8) * 16 + x // 8) * 32 + y % 8 * 4 + x % 8 // 2
    shift = (x % 2) * 4
    tiles[address] = (tiles[address] & ~(15 << shift)) | color << shift


def replace_header(raw, mask):
    if len(raw) != 8192 or len(mask) != 640 or any(pixel not in (0, 1) for pixel in mask):
        raise ValueError('Guide header needs 256 native tiles and an 80x8 binary ink mask.')
    output = bytearray(raw)
    # Thirteen central header tiles. The two outer cap tiles remain intact.
    for y in range(8, 16):
        for x in range(8, 112):
            put_pixel(output, x, y, 1)
    for y in range(8):
        for x in range(80):
            if mask[y * 80 + x]:
                put_pixel(output, x + 20, y + 8, 15)
    return bytes(output)


def encode_header(root):
    # Technical native-format conversion of the generated asset, not an art edit.
    from PIL import Image
    directory = root / ASSET
    image = Image.open(directory / 'header-native.png').convert('RGBA')
    if image.size != (80, 8):
        raise ValueError('Use the native 80x8 wordmark asset.')
    mask = bytes(1 if alpha >= 128 else 0 for *_, alpha in image.get_flattened_data())
    (directory / 'header-mask.bin').write_bytes(mask)
    metadata = json.loads((directory / 'conversion.json').read_text())
    metadata['native_png_sha256'] = hashlib.sha256((directory / 'header-native.png').read_bytes()).hexdigest()
    metadata['native_mask_sha256'] = hashlib.sha256(mask).hexdigest()
    (directory / 'conversion.json').write_text(json.dumps(metadata, indent=2) + '\n')


def apply_interface_graphics(root, emerald, target):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    mask = (directory / 'header-mask.bin').read_bytes()
    if hashlib.sha256(mask).hexdigest() != metadata['native_mask_sha256'] or \
       hashlib.sha256((directory / 'header-native.png').read_bytes()).hexdigest() != metadata['native_png_sha256']:
        raise ValueError('Regenerate the native wordmark mask after changing its source asset.')
    symbols = symbols_from_nm(subprocess.check_output(['arm-none-eabi-nm', '-S',
        '--defined-only', str(emerald / 'sf-engine-probe.elf')], text=True), {SYMBOL})
    if SYMBOL not in symbols:
        raise ValueError('Pinned guide graphics allocation is missing.')
    offset, capacity = symbols[SYMBOL]
    work = root / '.tools' / ('guide-graphics-' + uuid.uuid4().hex)
    work.mkdir()
    linked = work / 'linked.bin'
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary',
                    str(emerald / 'sf-engine-probe.elf'), str(linked)], check=True)
    rom, linked_bytes = target.read_bytes(), linked.read_bytes()
    if offset < 0 or capacity < 4 or offset + capacity > min(len(rom), len(linked_bytes)):
        raise ValueError('Guide graphics allocation is outside the cartridge.')
    original = linked_bytes[offset:offset + capacity]
    codec = work / 'native-lz'
    tool_source = emerald / 'tools/gbagfx'
    subprocess.run(['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        '-I' + str(tool_source), str(root / 'scripts/romhack/native_lz.c'),
        str(tool_source / 'lz.c'), '-o', str(codec)], check=True)
    packed, raw, changed, compressed, verified = [work / name for name in
        ('original.lz', 'original.4bpp', 'changed.4bpp', 'changed.lz', 'verified.4bpp')]
    packed.write_bytes(original)
    subprocess.run([str(codec), 'decode', str(packed), str(raw)], check=True)
    changed.write_bytes(replace_header(raw.read_bytes(), mask))
    subprocess.run([str(codec), 'encode', str(changed), str(compressed)], check=True)
    subprocess.run([str(codec), 'decode', str(compressed), str(verified)], check=True)
    if changed.read_bytes() != verified.read_bytes():
        raise ValueError('Guide graphics failed lossless codec verification.')
    replacement = compressed.read_bytes()
    if len(replacement) > capacity:
        raise ValueError('Guide graphics exceed their original compressed allocation.')
    padded = replacement + bytes(capacity - len(replacement))
    if rom[offset:offset + capacity] not in (original, padded):
        raise ValueError('Guide graphics do not match the linked ELF or our exact replacement.')
    target.write_bytes(rom[:offset] + padded + rom[offset + capacity:])
    return {'symbol': SYMBOL, 'offset': offset, 'capacity': capacity,
        'compressed_bytes': len(replacement), 'raw_bytes': 8192,
        'mask_sha256': hashlib.sha256(mask).hexdigest(),
        'raw_sha256': hashlib.sha256(changed.read_bytes()).hexdigest(), 'quality_approval': 'pending'}


if __name__ == '__main__':
    encode_header(Path(__file__).resolve().parents[2])
