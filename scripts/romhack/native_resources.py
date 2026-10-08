"""Guarded post-link replacement of declared read-only native resources."""
import hashlib
import subprocess
import uuid
from interface_text import symbols_from_nm


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
