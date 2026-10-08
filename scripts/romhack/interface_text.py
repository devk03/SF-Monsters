"""Replace declared native text allocations without moving code or save data."""
import hashlib
import json
import re
import subprocess
import uuid


def encoding_table(path):
    table = {}
    for line in path.read_text().splitlines():
        match = re.match(r"(?:'((?:\\.|[^'])+)'|([A-Z][A-Z0-9_]*))\s*=\s*([0-9A-F]{2}(?: [0-9A-F]{2})*)", line)
        if match:
            key = "'" if match[1] == "\\'" else match[1] or match[2]
            table[key] = bytes.fromhex(match[3])
    return table


def encode(text, table):
    result = bytearray()
    for token in re.findall(r'\{[^}]+\}|\\[npl]|.', text, re.S):
        if token.startswith('{'):
            name, *arguments = token[1:-1].split()
            if name not in table:
                raise ValueError('Unknown native text command: ' + name)
            result.extend(table[name])
            for argument in arguments:
                value = int(argument)
                if not 0 <= value <= 255:
                    raise ValueError('Text command argument exceeds one byte.')
                result.append(value)
        else:
            key = '\\n' if token == '\n' else token
            if key not in table:
                raise ValueError('Unsupported native glyph: ' + repr(token))
            result.extend(table[key])
    return bytes(result) + b'\xff'


def symbols_from_nm(text, wanted):
    result = {}
    for line in text.splitlines():
        match = re.fullmatch(r'([0-9a-f]+) ([0-9a-f]+) ([Rr]) ([A-Za-z0-9_]+)', line.strip())
        if match and match[4] in wanted:
            name = match[4]
            if name in result:
                raise ValueError('Ambiguous native text symbol: ' + name)
            result[name] = (int(match[1], 16) - 0x08000000, int(match[2], 16))
    return result


def replace_allocations(rom, records, symbols, table, linked_rom):
    output, occupied, changes = bytearray(rom), [], []
    for record in records:
        name = record['symbol']
        if not re.fullmatch(r'[gs]Text_[A-Za-z0-9_]+', name) or name not in symbols:
            raise ValueError('Missing declared native text allocation: ' + name)
        offset, capacity = symbols[name]
        end = offset + capacity
        if offset < 0 or capacity < 1 or end > len(rom) or end > len(linked_rom):
            raise ValueError('Native text allocation is outside the cartridge.')
        if any(offset < other_end and end > other_start for other_start, other_end in occupied):
            raise ValueError('Native text allocations overlap.')
        if linked_rom[end - 1] != 255:
            raise ValueError('Expected a native text terminator at the allocation boundary.')
        replacement = encode(record['text'], table)
        if len(replacement) > capacity:
            raise ValueError('New label exceeds its native allocation: ' + name)
        padded = replacement + bytes(capacity - len(replacement))
        if rom[offset:end] not in (linked_rom[offset:end], padded):
            raise ValueError('Text allocation does not match the linked ELF: ' + name)
        output[offset:end] = padded
        occupied.append((offset, end))
        changes.append({'symbol': name, 'offset': offset, 'capacity': capacity,
                        'text': record['text'], 'encoded_bytes': len(replacement)})
    return bytes(output), changes


def apply_interface_text(root, emerald, target):
    content = json.loads((root / 'romhack/content/interface-text.json').read_text())
    symbols = symbols_from_nm(subprocess.check_output(['arm-none-eabi-nm', '-S',
        '--defined-only', str(emerald / 'sf-engine-probe.elf')], text=True),
        {record['symbol'] for record in content['labels']})
    rom = target.read_bytes()
    linked = root / '.tools' / ('interface-linked-' + uuid.uuid4().hex + '.bin')
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary',
                    str(emerald / 'sf-engine-probe.elf'), str(linked)], check=True)
    translated, changes = replace_allocations(rom, content['labels'], symbols,
        encoding_table(emerald / 'charmap.txt'), linked.read_bytes())
    target.write_bytes(translated)
    return {'input_sha256': hashlib.sha256(rom).hexdigest(),
            'target_sha256': hashlib.sha256(translated).hexdigest(), 'labels': changes}
