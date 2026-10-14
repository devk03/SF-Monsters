"""Read-only compiled creature audit; source conversion alone cannot prove integration."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct

from PIL import Image


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decode_lz(source):
    """Bounded GBA LZ10 decoder adapted from the independent Cartridge audit."""
    if len(source) < 4 or source[0] != 0x10:
        raise ValueError('Require an LZ10 header')
    length = int.from_bytes(source[1:4], 'little')
    if not 0 < length <= 32768:
        raise ValueError('Creature resource exceeds the decoded bound')
    out, pos = bytearray(), 4
    try:
        while len(out) < length:
            flags = source[pos]; pos += 1
            for bit in range(7, -1, -1):
                if len(out) == length:
                    break
                if flags & (1 << bit):
                    first, second = source[pos], source[pos + 1]; pos += 2
                    distance = ((first & 15) << 8 | second) + 1
                    count = (first >> 4) + 3
                    if distance > len(out) or len(out) + count > length:
                        raise ValueError('Invalid LZ10 backreference')
                    for _ in range(count):
                        out.append(out[-distance])
                else:
                    out.append(source[pos]); pos += 1
    except IndexError as error:
        raise ValueError('Truncated LZ10 resource') from error
    return bytes(out)


class Cartridge:
    """Explicit ROM/ELF variant of the existing independent Cartridge reader."""
    def __init__(self, rom, elf):
        self.rom, self.elf = rom.read_bytes(), elf.read_bytes()
        if not 0 < len(self.rom) <= 32 * 1024 * 1024 or len(self.elf) < 52 or (
                self.elf[:7] != b'\x7fELF\x01\x01\x01' or
                struct.unpack_from('<H', self.elf, 18)[0] != 40):
            raise ValueError('Require a bounded cartridge and little-endian ARM ELF32')
        start = struct.unpack_from('<I', self.elf, 32)[0]
        size, count = struct.unpack_from('<HH', self.elf, 46)
        if size != 40 or not count or start + size * count > len(self.elf):
            raise ValueError('Invalid ELF section table')
        self.sections = [struct.unpack_from('<10I', self.elf, start + i * size) for i in range(count)]
        self.symbols = {}
        for section in self.sections:
            _, kind, _, _, offset, capacity, link, _, _, entry_size = section
            if kind != 2:  # SHT_SYMTAB; no external binutils dependency.
                continue
            if entry_size != 16 or capacity % 16 or offset + capacity > len(self.elf) or link >= count:
                raise ValueError('Invalid ELF symbol table')
            strings = self.sections[link]
            if strings[1] != 3 or strings[4] + strings[5] > len(self.elf):
                raise ValueError('Invalid ELF symbol string table')
            names = self.elf[strings[4]:strings[4] + strings[5]]
            for index in range(offset, offset + capacity, 16):
                name_index, address, length, _, _, section_index = struct.unpack_from('<IIIBBH', self.elf, index)
                if section_index == 0:  # Undefined symbols are not resource definitions.
                    continue
                end = names.find(b'\x00', name_index)
                if name_index >= len(names) or end < 0:
                    raise ValueError('Invalid ELF symbol name')
                name = names[name_index:end].decode('ascii')
                if not name.startswith(('gMon', 'Cry_')) and name != 'gEnemyMonElevation':
                    continue
                if section_index >= count and section_index != 0xfff1:
                    raise ValueError('Invalid ELF resource section index')
                if name in self.symbols:
                    raise ValueError('Ambiguous resource symbol: ' + name)
                self.symbols[name] = (address, length or None)
        if not self.symbols:
            raise ValueError('ELF contains no defined creature resource symbols')

    def data(self, name, length=None):
        if name not in self.symbols:
            raise ValueError('Missing resource symbol: ' + name)
        address, size = self.symbols[name]
        length = size if length is None else length
        offset = address - 0x08000000
        if length is None or length < 1 or offset < 0 or offset + length > len(self.rom) or (
                size is not None and length > size):
            raise ValueError('Resource outside cartridge/symbol bounds: ' + name)
        actual = self.rom[offset:offset + length]
        for section in self.sections:
            _, kind, flags, base, file_offset, capacity, *_ = section
            if kind == 1 and flags & 2 and base <= address and address + length <= base + capacity:
                index = file_offset + address - base
                if index + length <= len(self.elf) and actual == self.elf[index:index + length]:
                    return actual
                raise ValueError('ROM/ELF resource bytes differ: ' + name)
        raise ValueError('Resource has no file-backed ELF section: ' + name)


def pack_image(image):
    width, height = image.size
    if image.mode != 'P' or width % 8 or height % 8 or not 0 < width <= 64 or not 0 < height <= 128:
        raise ValueError('Require native indexed tile dimensions')
    pixels = image.tobytes()
    if any(value > 15 for value in pixels):
        raise ValueError('Creature indices exceed four bits')
    out = bytearray()
    for ty in range(0, height, 8):
        for tx in range(0, width, 8):
            for y in range(8):
                for x in range(0, 8, 2):
                    index = (ty + y) * width + tx + x
                    out.append(pixels[index] | pixels[index + 1] << 4)
    return bytes(out)


def palette_bytes(path):
    lines = path.read_text().splitlines()
    if lines[:3] != ['JASC-PAL', '0100', '16'] or len(lines) != 19:
        raise ValueError('Require sixteen JASC palette colors')
    out = bytearray()
    for line in lines[3:]:
        colors = list(map(int, line.split()))
        if len(colors) != 3 or any(not 0 <= value <= 255 for value in colors):
            raise ValueError('Invalid palette channels')
        r, g, b = colors
        out.extend(struct.pack('<H', (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10))
    return bytes(out)


def audit(rom, elf, root, species_header):
    receipt = {'schema': 1, 'passed': False, 'checks': [], 'inputs': {}, 'errors': [],
               'scope': 'Compiled resource identity and bindings; no art approval or gameplay claim'}

    def source(path):
        data = path.read_bytes(); receipt['inputs'][str(path.resolve())] = digest(data)
        return data

    try:
        source(rom); source(elf); source(Path(__file__))
        cart = Cartridge(rom, elf)
        catalog = json.loads(source(root / 'romhack/content/monsters.json'))
        if not catalog['monsters'] or any(len({mon[key] for mon in catalog['monsters']}) !=
                len(catalog['monsters']) for key in ('species', 'symbol', 'name')):
            raise ValueError('Require a nonempty roster with unique species, symbols and names')
        constants = {name: int(value) for name, value in re.findall(
            r'^#define (SPECIES_\w+) (\d+)\s*$', source(species_header).decode(), re.M)}

        def check(category, label, expected, read):
            record = {'category': category, 'label': label, 'expected_sha256': digest(expected),
                      'expected_bytes': len(expected), 'matches': False}
            try:
                actual = read()
                record.update(actual_sha256=digest(actual), actual_bytes=len(actual), matches=actual == expected)
            except (ValueError, KeyError, struct.error) as error:
                record['error'] = str(error)
            receipt['checks'].append(record)

        for mon in catalog['monsters']:
            species, symbol = constants[mon['species']], mon['symbol']
            art = (root / mon['art']).resolve(); art.relative_to(root.resolve() / 'assets/monsters')
            for kind, prefix, filename, compressed in [
                    ('front', 'gMonStillFrontPic_', 'front.png', True),
                    ('anim_front', 'gMonFrontPic_', 'anim_front.png', True),
                    ('back', 'gMonBackPic_', 'back.png', True),
                    ('icon', 'gMonIcon_', 'icon.png', False),
                    ('normal', 'gMonPalette_', 'normal.pal', True),
                    ('shiny', 'gMonShinyPalette_', 'shiny.pal', True)]:
                path = art / filename; source(path)
                if kind in ('normal', 'shiny'):
                    expected = palette_bytes(path)
                else:
                    with Image.open(path) as image:
                        expected_size = (32, 64) if kind == 'icon' else (64, 128) if kind == 'anim_front' else (64, 64)
                        if image.size != expected_size or image.info.get('transparency') not in (0, b'\x00'):
                            raise ValueError('Invalid native creature canvas/transparency: ' + str(path))
                        expected = pack_image(image)
                name = prefix + symbol
                check('visual', name, expected,
                      lambda: decode_lz(cart.data(name)) if compressed else cart.data(name))
            for table, prefix, stride in [
                    ('gMonFrontPicTable', 'gMonFrontPic_', 8), ('gMonBackPicTable', 'gMonBackPic_', 8),
                    ('gMonPaletteTable', 'gMonPalette_', 8), ('gMonShinyPaletteTable', 'gMonShinyPalette_', 8),
                    ('gMonIconTable', 'gMonIcon_', 4)]:
                check('binding', table + ':' + mon['species'], struct.pack('<I', cart.symbols[prefix + symbol][0]),
                      lambda: cart.data(table)[species * stride:species * stride + 4])
            check('icon_selector', mon['species'], bytes([mon['icon_palette']]),
                  lambda: cart.data('gMonIconPaletteIndices')[species:species + 1])
            check('enemy_elevation', mon['species'], bytes([mon['enemy_elevation']]),
                  lambda: cart.data('gEnemyMonElevation')[species:species + 1])
        for group, reference in catalog['icon_palettes'].items():
            path = root / reference; source(path)
            check('shared_palette', group, palette_bytes(path),
                  lambda: cart.data('gMonIconPalettes')[int(group) * 32:(int(group) + 1) * 32])
        source(root / 'scripts/romhack/creature_audio.py')
        synthesize = runpy.run_path(str(root / 'scripts/romhack/creature_audio.py'))['synthesize']
        recipes = json.loads(source(root / 'assets/audio/creature-cries.json'))
        if not recipes['cries']:
            raise ValueError('Require declared original cry controls')
        for cry in recipes['cries']:
            pcm = synthesize(cry, recipes['sample_rate'])
            expected = struct.pack('<HHIII', 0, 0, recipes['sample_rate'] * 1024, 0, len(pcm)) + pcm
            name = 'Cry_' + cry['engine_symbol']
            check('cry', name, expected, lambda: cart.data(name, len(expected)))
        receipt['passed'] = bool(receipt['checks']) and all(row['matches'] for row in receipt['checks'])
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        receipt['errors'].append(str(error))
    receipt['counts'] = {}
    for row in receipt['checks']:
        counts = receipt['counts'].setdefault(row['category'], {'total': 0, 'matched': 0})
        counts['total'] += 1; counts['matched'] += row['matches']
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('rom', 'elf', 'root', 'species-header', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        args.output.resolve().relative_to(args.root.resolve() / '.tools')
    except ValueError:
        parser.error('Receipt must be a new private path beneath root/.tools')
    if args.output.exists():
        parser.error('Refuse to overwrite existing evidence')
    result = audit(args.rom, args.elf, args.root, args.species_header)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({'passed': result['passed'], 'counts': result['counts'], 'errors': result['errors']}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
