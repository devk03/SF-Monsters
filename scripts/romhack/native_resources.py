"""Guarded post-link replacement of declared read-only native resources."""
import hashlib
import re
import subprocess
import uuid
from interface_text import symbols_from_nm


def named_addresses(elf, wanted):
    output = subprocess.check_output(['arm-none-eabi-nm', '--defined-only', str(elf)], text=True)
    symbols = {}
    for line in output.splitlines():
        match = re.fullmatch(r'([0-9a-f]+) [RrAa] ([A-Za-z0-9_]+)', line)
        if match and match[2] in wanted:
            if match[2] in symbols:
                raise ValueError('Ambiguous native resource symbol: ' + match[2])
            symbols[match[2]] = int(match[1], 16)
    if set(symbols) != wanted:
        raise ValueError('Missing declared native resource symbols.')
    return symbols


def bounded_span(addresses, start, end):
    offset, capacity = addresses[start] - 0x08000000, addresses[end] - addresses[start]
    if offset < 0 or capacity < 1:
        raise ValueError('Native end symbol must follow its resource in cartridge space.')
    return offset, capacity


def replace_resource(rom, linked, offset, capacity, data, preserve_tail=False):
    if offset < 0 or capacity < 1 or offset + capacity > min(len(rom), len(linked)):
        raise ValueError('Resource allocation is outside the linked cartridge.')
    if len(data) > capacity:
        raise ValueError('Resource exceeds its original allocation.')
    original = linked[offset:offset + capacity]
    replacement = data + (original[len(data):] if preserve_tail else bytes(capacity - len(data)))
    if rom[offset:offset + capacity] not in (original, replacement):
        raise ValueError('Resource matches neither the linked ELF nor our exact replacement.')
    return rom[:offset] + replacement + rom[offset + capacity:]


def apply_resources(root, emerald, target, resources):
    names = [resource['symbol'] for resource in resources]
    if len(set(names)) != len(names):
        raise ValueError('Declare each native resource only once.')
    symbols = symbols_from_nm(subprocess.check_output(['arm-none-eabi-nm', '-S',
        '--defined-only', str(emerald / 'sf-engine-probe.elf')], text=True), set(names))
    bounded = [resource for resource in resources if resource.get('end_symbol')]
    if bounded:
        addresses = named_addresses(emerald / 'sf-engine-probe.elf',
            {name for resource in bounded for name in (resource['symbol'], resource['end_symbol'])})
        for resource in bounded:
            span = bounded_span(addresses, resource['symbol'], resource['end_symbol'])
            if resource['symbol'] in symbols and symbols[resource['symbol']] != span:
                raise ValueError('End symbol disagrees with the declared native resource size.')
            symbols[resource['symbol']] = span
    work = root / '.tools' / ('native-resources-' + uuid.uuid4().hex)
    work.mkdir()
    linked_path, codec = work / 'linked.bin', work / 'native-lz'
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary',
        str(emerald / 'sf-engine-probe.elf'), str(linked_path)], check=True)
    source = emerald / 'tools/gbagfx'
    subprocess.run(['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        '-I' + str(source), str(root / 'scripts/romhack/native_lz.c'),
        str(source / 'lz.c'), '-o', str(codec)], check=True)
    rom, linked, occupied, receipt = target.read_bytes(), linked_path.read_bytes(), [], []
    for index, resource in enumerate(resources):
        name, raw = resource['symbol'], resource['data']
        if name not in symbols:
            raise ValueError('Missing declared native resource: ' + name)
        offset, capacity = symbols[name]
        if any(offset < end and offset + capacity > start for start, end in occupied):
            raise ValueError('Native resource allocations overlap.')
        occupied.append((offset, offset + capacity))
        data = raw
        if resource.get('compressed'):
            original, packed, verified = [work / f'{index}.{suffix}' for suffix in ('raw', 'lz', 'verified')]
            original.write_bytes(raw)
            subprocess.run([str(codec), 'encode', str(original), str(packed)], check=True)
            subprocess.run([str(codec), 'decode', str(packed), str(verified)], check=True)
            if verified.read_bytes() != raw:
                raise ValueError('Native resource failed lossless codec verification.')
            data = packed.read_bytes()
        rom = replace_resource(rom, linked, offset, capacity, data, resource.get('preserve_tail', False))
        receipt.append({'symbol': name, 'offset': offset, 'capacity': capacity,
            'encoded_bytes': len(data), 'raw_bytes': len(raw),
            'raw_sha256': hashlib.sha256(raw).hexdigest(),
            'preserved_tail_bytes': capacity - len(data) if resource.get('preserve_tail') else 0})
    target.write_bytes(rom)
    return receipt
